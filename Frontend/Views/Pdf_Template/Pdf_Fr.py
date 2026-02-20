import os
import sys
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict
from tkinter import messagebox

# ============================================================================
# ✅ PATCH REPORTLAB - Fix openssl_md5 bug with Python 3.9+
# ============================================================================
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

# ---------------------------------------------------------------------------
# Font configuration
# ---------------------------------------------------------------------------

try:
    _FONT_REGULAR = r"C:\\Windows\\Fonts\\arial.ttf"
    _FONT_BOLD    = r"C:\\Windows\\Fonts\\arialbd.ttf"
    pdfmetrics.registerFont(TTFont("Arial", _FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("Arial-Bold", _FONT_BOLD))
    FONT_FR       = "Arial"
    FONT_FR_BOLD  = "Arial-Bold"
except Exception:
    FONT_FR       = "Helvetica"
    FONT_FR_BOLD  = "Helvetica-Bold"

# ---------------------------------------------------------------------------
# LTR drawing helpers
# ---------------------------------------------------------------------------

def _draw_ltr(c: canvas.Canvas, text: str, x: float, y: float,
              *, font: str = FONT_FR, size: int = 12) -> None:
    """Draw left-to-right text starting at x."""
    c.setFont(font, size)
    c.drawString(x, y, text)

def _draw_center_fr(c: canvas.Canvas, text: str, x: float, y: float,
                    *, font: str = FONT_FR, size: int = 12) -> None:
    """Draw centered text around x."""
    c.setFont(font, size)
    half = c.stringWidth(text, font, size) / 2
    c.drawString(x - half, y, text)

# ---------------------------------------------------------------------------
# Signature search (reused from Arabic module)
# ---------------------------------------------------------------------------

def find_signature_file(custom_path: Optional[str] = None) -> Optional[str]:
    _SEARCH_DIRS = [
        ".",
        "images",
        "signatures",
        os.path.join(os.getcwd(), "images"),
        os.path.join(os.path.dirname(__file__), "images"),
    ]
    _NAMES = ["signature", "Signature", "singature", "sign"]
    _EXTS  = [".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]

    if custom_path and os.path.isfile(custom_path):
        return custom_path

    for directory in _SEARCH_DIRS:
        for name in _NAMES:
            for ext in _EXTS:
                candidate = os.path.normpath(os.path.join(directory, name + ext))
                if os.path.isfile(candidate):
                    return candidate
    return None

# ---------------------------------------------------------------------------
# Core French page drawing
# ---------------------------------------------------------------------------

def draw_conge_page_fr(c: canvas.Canvas, data: Dict,
                       signature_path: Optional[str] = None,
                       signature_width: float = 6.0) -> None:
    """
    Draws a single French-language leave (congé) page on the canvas.

    Args:
        c               : ReportLab canvas
        data            : Employee + leave data dictionary
        signature_path  : Path to signature image file
        signature_width : Width of the signature image in cm
    """
    PAGE_W, PAGE_H = A4
    LEFT  = 2 * cm       # left margin
    RIGHT = PAGE_W - 2 * cm  # right margin

    # ── Header ──────────────────────────────────────────────────────────────
    _draw_center_fr(c, "REPUBLIQUE ALGERIENNE DEMOCRATIQUE ET POPULAIRE",
                    PAGE_W / 2, PAGE_H - 1.5 * cm, font=FONT_FR_BOLD, size=11)

    _draw_ltr(c, "Ministère de l'Enseignement Supérieur et de la Recherche Scientifique",
              LEFT, PAGE_H - 2.5 * cm, size=10)
    _draw_ltr(c, "Office National des Œuvres Universitaires",
              LEFT, PAGE_H - 3.3 * cm, size=10)
    _draw_ltr(c, "Direction des Œuvres Universitaires de Chlef",
              LEFT, PAGE_H - 4.1 * cm, size=10)

    # ── Reference number & date ─────────────────────────────────────────────
    date_actuelle = data.get("date_actuelle", datetime.now().strftime("%d/%m/%Y"))
    year          = data.get("annee", str(datetime.now().year))
    numero        = data.get("numero_document", "...........")

    _draw_ltr(c, f"N° : {numero} / D.O.U.C / {year}",
              LEFT, PAGE_H - 5.1 * cm, size=10)
    _draw_ltr(c, f"Chlef, le : {date_actuelle}",
              RIGHT - 7 * cm, PAGE_H - 5.1 * cm, size=10)

    # ── Title ────────────────────────────────────────────────────────────────
    _draw_center_fr(c, "BON DE CONGE", PAGE_W / 2, PAGE_H - 7.5 * cm,
                    font=FONT_FR_BOLD, size=18)

    # Decorative underline
    title_width = c.stringWidth("BON DE CONGE", FONT_FR_BOLD, 18)
    lx = PAGE_W / 2 - title_width / 2
    c.setLineWidth(1.5)
    c.line(lx, PAGE_H - 7.9 * cm, lx + title_width, PAGE_H - 7.9 * cm)
    c.setLineWidth(1)

    # ── Legal references ─────────────────────────────────────────────────────
    _draw_ltr(c,
              "– Vu l'Ordonnance n° 06-03 du 15 juillet 2006 portant statut général de la Fonction Publique ;",
              LEFT, PAGE_H - 9.3 * cm, size=10)
    _draw_ltr(c,
              "– Vu la Loi n° 81-08 du 27 juin 1981 relative aux congés annuels ;",
              LEFT, PAGE_H - 10.3 * cm, size=10)

    # ── Employee details ─────────────────────────────────────────────────────
    nom    = data.get("nom", "")
    prenom = data.get("prenom", "")
    _draw_ltr(c, f"– Sur demande de l'intéressé(e) : {nom}  {prenom}",
              LEFT, PAGE_H - 11.5 * cm, size=11)

    y_cursor = PAGE_H - 12.7 * cm

    lieu_travail = data.get("residence", "")
    if lieu_travail:
        _draw_ltr(c, f"– Lieu de travail : {lieu_travail}", LEFT, y_cursor, size=11)
        y_cursor -= 1.2 * cm

    grade = data.get("grade", "")
    if grade:
        _draw_ltr(c, f"– Grade : {grade}", LEFT, y_cursor, size=11)
        y_cursor -= 1.2 * cm

    poste_sup = data.get("poste_superieur", "")
    if poste_sup:
        _draw_ltr(c, f"– Fonction : {poste_sup}", LEFT, y_cursor, size=11)
        y_cursor -= 1.2 * cm

    # ── Leave details ────────────────────────────────────────────────────────
    type_conge  = data.get("type_conge", "Congé annuel")
    date_debut  = data.get("date_debut", "")
    date_fin    = data.get("date_fin", "")
    jours_pris  = data.get("jours_pris", "0")
    nouveau_reste = data.get("nouveau_reste", "0")
    lieu        = data.get("lieu", "")

    _draw_ltr(c,
              f"L'intéressé(e) bénéficie d'un {type_conge} pour l'année {year}",
              LEFT, y_cursor, size=11)
    y_cursor -= 1.2 * cm

    _draw_ltr(c, f"du {date_debut}  au  {date_fin}", LEFT, y_cursor, size=11)
    y_cursor -= 1.2 * cm

    _draw_ltr(c, f"Durée : {jours_pris} jour(s)", LEFT, y_cursor, size=11)
    _draw_ltr(c, f"Solde restant : {nouveau_reste} jour(s)",
              LEFT + 8 * cm, y_cursor, size=11)
    y_cursor -= 1.2 * cm

    _draw_ltr(c, f"Lieu de résidence pendant le congé : {lieu}", LEFT, y_cursor, size=11)

    # ── Signature block ──────────────────────────────────────────────────────
    SIG_X = PAGE_W / 2      # centred on page
    SIG_LABEL_Y = PAGE_H - 20.5 * cm

    _draw_center_fr(c, "Le Chef de la Division des Ressources Humaines",
                    SIG_X, SIG_LABEL_Y, font=FONT_FR_BOLD, size=11)

    if signature_path and os.path.isfile(signature_path):
        try:
            sig_w = signature_width * cm
            sig_x = SIG_X - sig_w / 2
            sig_y = SIG_LABEL_Y - 7.5 * cm
            c.drawImage(
                signature_path,
                x=sig_x, y=sig_y,
                width=sig_w, height=None,
                preserveAspectRatio=True,
            )
        except Exception as exc:
            print(f"❌ Erreur signature: {exc}")

    # ── Footer line ──────────────────────────────────────────────────────────
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    y_line = 2.5 * cm
    c.line(LEFT, y_line, RIGHT, y_line)
    _draw_center_fr(
        c,
        "Direction des Œuvres Universitaires de Chlef  –  Tél : 027 72 19 25  –  Email : dou02.drh@ONOUchlef.com",
        PAGE_W / 2, y_line - 0.5 * cm,
        font=FONT_FR, size=9,
    )

# ---------------------------------------------------------------------------
# PDF generation (one file per residence, one page per employee)
# ---------------------------------------------------------------------------

def generate_conge_pdf_fr_by_residence(
    employees_data: List[Dict],
    residence_name: str,
    output_dir: Optional[str] = None,
    signature_path: Optional[str] = None,
    auto_open: bool = False,
) -> Optional[str]:
    """
    Generates a French-language PDF with one page per employee for a given residence.

    Args:
        employees_data : List of employee data dictionaries
        residence_name : Name of the residence (used in the filename)
        output_dir     : Output directory (defaults to Desktop)
        signature_path : Path to signature image
        auto_open      : Open the PDF after creation

    Returns:
        Absolute path of the generated PDF, or None on error.
    """
    signature_path = find_signature_file(signature_path)
    if signature_path:
        print(f"✅ Signature trouvée: {signature_path}")
    else:
        print("⚠️ Aucune signature trouvée – continuation sans signature")

    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Desktop")

    os.makedirs(output_dir, exist_ok=True)

    timestamp      = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_residence = residence_name.replace(" ", "_").replace("/", "-")
    filename       = f"Bon_Conge_{safe_residence}_{timestamp}.pdf"
    save_path      = os.path.join(output_dir, filename)

    try:
        c = canvas.Canvas(save_path, pagesize=A4)

        for idx, employee in enumerate(employees_data, 1):
            print(f"📄 Page {idx}/{len(employees_data)} – "
                  f"{employee.get('nom', '')} {employee.get('prenom', '')}")
            draw_conge_page_fr(c, employee, signature_path)
            if idx < len(employees_data):
                c.showPage()

        c.save()
        print(f"✅ PDF créé : {save_path}  ({len(employees_data)} page(s))")

        if auto_open:
            try:
                import platform, subprocess
                system = platform.system()
                if system == "Windows":
                    os.startfile(save_path)
                elif system == "Darwin":
                    subprocess.run(["open", save_path], check=True)
                else:
                    subprocess.run(["xdg-open", save_path], check=True)
                print("📂 PDF ouvert automatiquement")
            except Exception as e:
                print(f"⚠️ Impossible d'ouvrir automatiquement : {e}")

        return save_path

    except Exception as exc:
        print(f"❌ Erreur génération PDF : {exc}")
        import traceback
        traceback.print_exc()
        return None