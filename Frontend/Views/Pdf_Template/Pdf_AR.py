import os
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict
from tkinter import messagebox
import sys

# ============================================================================
# ✅ PATCH REPORTLAB - Correction bug openssl_md5 avec Python 3.9+
# ============================================================================
import hashlib
if sys.version_info >= (3, 9) and not hasattr(hashlib, '_reportlab_patched'):
    _original_hashlib_new = hashlib.new
    def _patched_hashlib_new(name, *args, **kwargs):
        kwargs.pop('usedforsecurity', None)
        return _original_hashlib_new(name, *args, **kwargs)
    hashlib.new = _patched_hashlib_new
    hashlib._reportlab_patched = True
    print("✅ Patch ReportLab appliqué")
# ============================================================================

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from bidi.algorithm import get_display
import arabic_reshaper

# ---------------------------------------------------------------------------
# Configuration des polices
# ---------------------------------------------------------------------------

try:
    _FONT_REGULAR = r"C:\\Windows\\Fonts\\arial.ttf"
    _FONT_BOLD    = r"C:\\Windows\\Fonts\\arialbd.ttf"
    pdfmetrics.registerFont(TTFont("Arial", _FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("Arial-Bold", _FONT_BOLD))
    FONT_ARABIC      = "Arial"
    FONT_ARABIC_BOLD = "Arial-Bold"
except Exception:
    FONT_ARABIC      = "Helvetica"
    FONT_ARABIC_BOLD = "Helvetica-Bold"

# ---------------------------------------------------------------------------
# Utilitaires de texte arabe
# ---------------------------------------------------------------------------

def reshape_arabic(text: str) -> str:
    """Reformate le texte arabe pour l'affichage RTL."""
    return get_display(arabic_reshaper.reshape(text or ""))


def _draw_rtl(c: canvas.Canvas, text: str, x: float, y: float,
              *, font: str = FONT_ARABIC, size: int = 12) -> None:
    """Dessine du texte de droite à gauche."""
    text = reshape_arabic(text)
    c.setFont(font, size)
    text_width = c.stringWidth(text, font, size)
    c.drawString(x - text_width, y, text)


def _draw_center(c: canvas.Canvas, text: str, x: float, y: float,
                 *, font: str = FONT_ARABIC, size: int = 12) -> None:
    """Dessine du texte centré."""
    text = reshape_arabic(text)
    c.setFont(font, size)
    half = c.stringWidth(text, font, size) / 2
    c.drawString(x - half, y, text)

# ---------------------------------------------------------------------------
# Recherche de signature
# ---------------------------------------------------------------------------

def find_signature_file(custom_path: Optional[str] = None) -> Optional[str]:
    """Trouve le fichier signature_enhanced.png dans Frontend/Assets."""

    if custom_path and os.path.isfile(custom_path):
        return custom_path

    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    search_paths = [
        os.path.join(project_root, "Frontend", "Assets", "signature_enhanced.png"),
        os.path.join(os.getcwd(), "Frontend", "Assets", "signature_enhanced.png"),
    ]

    for path in search_paths:
        print("Checking:", path)
        if os.path.isfile(path):
            return path

    return None

# ---------------------------------------------------------------------------
# ✅ HELPER – Extraire (date_debut, date_fin) depuis un tuple ou dict de période
# ---------------------------------------------------------------------------

def _extract_periode_dates(periode) -> tuple:
    """
    Extrait (date_debut, date_fin) depuis une période qui peut être :
    - un tuple/liste : (date_debut, date_fin) ou (date_debut, date_fin, nb_jours)
    - un dict        : {"date_debut": ..., "date_fin": ...}
    Retourne ("", "") si impossible.
    """
    if isinstance(periode, dict):
        return str(periode.get("date_debut", "")).strip(), str(periode.get("date_fin", "")).strip()
    elif isinstance(periode, (list, tuple)) and len(periode) >= 2:
        return str(periode[0]).strip(), str(periode[1]).strip()
    return "", ""

# ---------------------------------------------------------------------------
# Fonction pour dessiner une page de congé
# ---------------------------------------------------------------------------

def draw_conge_page(c: canvas.Canvas, data: Dict,
                    signature_path: Optional[str] = None,
                    signature_width: float = 6.0) -> None:
    """
    Dessine une page de congé complète sur le canvas.

    Args:
        c               : Canvas ReportLab
        data            : Dictionnaire contenant les données de l'employé
        signature_path  : Chemin vers l'image de signature
        signature_width : Largeur de la signature en cm
    """
    PAGE_W, PAGE_H = A4

    # ── En-tête ──────────────────────────────────────────────────────────────
    _draw_center(c, "الجمهورية الجزائرية الديمقراطية الشعبية",
                 PAGE_W / 2, PAGE_H - 1.5 * cm, font=FONT_ARABIC, size=14)
    _draw_rtl(c, "وزارة التعليم العالي والبحث العلمي",
              PAGE_W - 2 * cm, PAGE_H - 2.5 * cm)
    _draw_rtl(c, "الديوان الوطني للخدمات الجامعية",
              PAGE_W - 2 * cm, PAGE_H - 3.5 * cm)
    _draw_rtl(c, "مديرية الخدمات الجامعية بالشلف",
              PAGE_W - 2 * cm, PAGE_H - 4.5 * cm)

    # ── Numéro & date ─────────────────────────────────────────────────────────
    year           = data.get("annee", str(datetime.now().year))
    date_actuelle  = data.get("date_actuelle", datetime.now().strftime("%d-%m-%Y"))

    _draw_rtl(c,
              f"الرقم: ........./ ق.م.ب/م.خ.ج.الشلف/{year}",
              PAGE_W - 2 * cm, PAGE_H - 5.5 * cm)

    # ── Titre ─────────────────────────────────────────────────────────────────
    _draw_center(c, "سـنــد عطــلــة",
                 PAGE_W / 2, PAGE_H - 8 * cm,
                 font=FONT_ARABIC_BOLD, size=18)
    title_width = c.stringWidth(
        reshape_arabic("سـنــد عطــلــة"), FONT_ARABIC_BOLD, 18
    )
    c.setLineWidth(1.5)
    lx = PAGE_W / 2 - title_width / 2
    c.line(lx, PAGE_H - 8.1 * cm, lx + title_width, PAGE_H - 8.1 * cm)
    c.setLineWidth(1)

    # ── Références légales ────────────────────────────────────────────────────
    _draw_rtl(
        c,
        "– بمقتضى الأمر رقم 06–03 المؤرخ في 15 جويلية 2006 المتضمن القانون الأساسي العام للوظيفة العمومية",
        PAGE_W - 2 * cm, PAGE_H - 9.5 * cm,
    )
    _draw_rtl(
        c,
        "– بمقتضى القانون رقم 81–08 المؤرخ في 27 جوان 1981 المتعلق بالعطل السنوية",
        PAGE_W - 2 * cm, PAGE_H - 10.7 * cm,
    )

    # ── Données personnelles ──────────────────────────────────────────────────
    nom    = data.get("nom", "")
    prenom = data.get("prenom", "")
    _draw_rtl(c, f"– بناء على طلب المعني(ة): {nom} {prenom}",
              PAGE_W - 2 * cm, PAGE_H - 11.9 * cm)

    y_cursor = PAGE_H - 13.1 * cm

    residence = data.get("residence", "")
    if residence:
        _draw_rtl(c, f"– مكان العمل : {residence}", PAGE_W - 2 * cm, y_cursor)
        y_cursor -= 1.2 * cm

    grade = data.get("grade", "")
    if grade:
        _draw_rtl(c, f"– الرتبة: {grade}", PAGE_W - 2 * cm, y_cursor)
        y_cursor -= 1.2 * cm

    poste_sup = data.get("poste_superieur", "").strip()
    if poste_sup and poste_sup.lower() not in ["aucun", "none", "null", "-"]:
        _draw_rtl(c, f"– الوظيفة : {poste_sup}", PAGE_W - 2 * cm, y_cursor)
        y_cursor -= 1.2 * cm
    else:
        y_cursor -= 0.5 * cm

    # ── Congé ─────────────────────────────────────────────────────────────────
    type_conge   = data.get("type_conge", "عطلة سنوية")
    date_debut   = data.get("date_debut", "")
    date_fin     = data.get("date_fin", "")
    jours_pris   = data.get("jours_pris", "0")
    nouveau_reste = data.get("nouveau_reste", "0")
    lieu         = data.get("lieu", "")
    periodes     = data.get("periodes") or []

    # ✅ CORRECTION: Construire les lignes de périodes correctement en arabe
    periode_lines = []
    for idx, periode in enumerate(periodes, 1):
        p_debut, p_fin = _extract_periode_dates(periode)
        if p_debut and p_fin:
            # Texte arabe pur – sera traité par reshape_arabic dans _draw_rtl
            periode_lines.append(f"الفترة {idx}: من {p_debut} إلى {p_fin}")

    if len(periodes) <= 1:
        # ── Cas 1 période : ligne classique debut → fin ──────────────────────
        _draw_rtl(
            c,
            f"يستفيد المعني(ة) من عطلة {type_conge} لسنة {year} ابتداءً من {date_debut} إلى غاية {date_fin}",
            PAGE_W - 2 * cm,
            y_cursor,
        )
        y_cursor -= 1.2 * cm
    else:
        # ── Cas plusieurs périodes : une ligne par période ────────────────────
        _draw_rtl(
            c,
            f"يستفيد المعني(ة) من عطلة {type_conge} لسنة {year}",
            PAGE_W - 2 * cm,
            y_cursor,
        )
        y_cursor -= 1.0 * cm
        for idx, line in enumerate(periode_lines):
            _draw_rtl(c, f"- {line}", PAGE_W - 2 * cm, y_cursor - idx * 1.0 * cm)
        y_cursor -= len(periode_lines) * 1.0 * cm

    # Durée et reste sur la même ligne
    _draw_rtl(c, f"المدة: {jours_pris} يوم",    PAGE_W - 2 * cm,      y_cursor)
    _draw_rtl(c, f"الباقي: {nouveau_reste} يوم", PAGE_W - 6 * cm,      y_cursor)
    y_cursor -= 1.2 * cm

    # Lieu de résidence pendant le congé
    _draw_rtl(c, f"مكان الإقامة خلال العطلة: {lieu}", PAGE_W - 2 * cm, y_cursor)
    y_cursor -= 1.2 * cm

    # ── Signature ─────────────────────────────────────────────────────────────
    _draw_rtl(c, f"حرر بـ الشلف في: {date_actuelle}",
              2 * cm + 7 * cm, PAGE_H - 20.1 * cm)

    HR_X = 2 * cm + 5 * cm
    HR_Y = PAGE_H - 21.3 * cm
    _draw_center(c, "رئيس قسم الموارد البشرية",
                 HR_X, HR_Y, font=FONT_ARABIC_BOLD, size=12)

    if signature_path and os.path.isfile(signature_path):
        try:
            signature_width_cm = signature_width * cm
            sig_x = HR_X - signature_width_cm / 2
            sig_y = HR_Y - 8 * cm
            c.drawImage(
                signature_path,
                x=sig_x,
                y=sig_y,
                width=signature_width_cm,
                height=None,
                preserveAspectRatio=True,
            )
        except Exception as exc:
            print(f"❌ Erreur signature: {exc}")

    # ── Pied de page ──────────────────────────────────────────────────────────
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    y_line = 2.5 * cm
    c.line(2 * cm, y_line, PAGE_W - 2 * cm, y_line)
    _draw_center(
        c,
        "مديرية الخدمات الجامعية شلف          رقم الهاتف 07 83 59 028         البريد الالكتروني dou02.drh@gmail.com",
        PAGE_W / 2,
        y_line - 0.5 * cm,
        font=FONT_ARABIC,
        size=10,
    )

# ---------------------------------------------------------------------------
# Génération PDF par résidence
# ---------------------------------------------------------------------------

def generate_conge_pdf_by_residence(
    employees_data: List[Dict],
    residence_name: str,
    output_dir: Optional[str] = None,
    signature_path: Optional[str] = None,
    auto_open: bool = False
) -> Optional[str]:
    """
    Génère un PDF avec plusieurs pages, une page par employé de la même résidence.

    Args:
        employees_data : Liste de dictionnaires contenant les données des employés
        residence_name : Nom de la résidence
        output_dir     : Répertoire de sortie (par défaut: Desktop)
        signature_path : Chemin vers l'image de signature
        auto_open      : Ouvrir automatiquement le PDF après création

    Returns:
        Chemin absolu du PDF généré, ou None en cas d'erreur.
    """

    # Recherche de la signature
    signature_path = find_signature_file(signature_path)
    if signature_path:
        print(f"✅ Signature trouvée: {signature_path}")
    else:
        print("⚠️ Aucune signature trouvée – continuation sans signature")

    # Répertoire de sortie
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Desktop")

    os.makedirs(output_dir, exist_ok=True)

    # Nom du fichier
    timestamp      = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_residence = residence_name.replace(" ", "_").replace("/", "-")
    filename       = f"سند_عطلة_{safe_residence}_{timestamp}.pdf"
    save_path      = os.path.join(output_dir, filename)

    try:
        c = canvas.Canvas(save_path, pagesize=A4)

        for idx, employee in enumerate(employees_data, 1):
            print(
                f"📄 Génération page {idx}/{len(employees_data)} – "
                f"{employee.get('nom', '')} {employee.get('prenom', '')} – "
                f"{len(employee.get('periodes') or [])} période(s)"
            )
            draw_conge_page(c, employee, signature_path)

            if idx < len(employees_data):
                c.showPage()

        c.save()
        print(f"✅ PDF créé avec succès: {save_path}")
        print(f"📊 Total de pages: {len(employees_data)}")

        if auto_open:
            try:
                import platform
                import subprocess
                system = platform.system()

                if system == "Windows":
                    os.startfile(save_path)
                elif system == "Darwin":
                    subprocess.run(["open", save_path], check=True)
                elif system == "Linux":
                    subprocess.run(["xdg-open", save_path], check=True)

                print("📂 PDF ouvert automatiquement")
            except Exception as e:
                print(f"⚠️ Impossible d'ouvrir automatiquement: {e}")

        return save_path

    except Exception as exc:
        print(f"❌ Erreur lors de la génération du PDF: {exc}")
        import traceback
        traceback.print_exc()
        return None

# ---------------------------------------------------------------------------
# Groupement des employés par résidence
# ---------------------------------------------------------------------------

def group_employees_by_residence(employees_data: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Groupe les employés par résidence.

    Args:
        employees_data: Liste de dictionnaires contenant les données des employés

    Returns:
        Dictionnaire avec résidence comme clé et liste d'employés comme valeur
    """
    grouped = defaultdict(list)

    for employee in employees_data:
        residence = employee.get("residence", "Non spécifié")
        grouped[residence].append(employee)

    return dict(grouped)