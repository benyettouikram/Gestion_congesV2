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
    _FONT_BOLD = r"C:\\Windows\\Fonts\\arialbd.ttf"
    pdfmetrics.registerFont(TTFont("Arial", _FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("Arial-Bold", _FONT_BOLD))
    FONT_ARABIC = "Arial"
    FONT_ARABIC_BOLD = "Arial-Bold"
except Exception:
    FONT_ARABIC = "Helvetica"
    FONT_ARABIC_BOLD = "Helvetica-Bold"

# ---------------------------------------------------------------------------
# Utilitaires de texte arabe
# ---------------------------------------------------------------------------

def reshape_arabic(text: str) -> str:
    """Reformate le texte arabe pour l'affichage RTL."""
    return get_display(arabic_reshaper.reshape(text or ""))

def _draw_rtl(c: canvas.Canvas, text: str, x: float, y: float, *, font: str = FONT_ARABIC, size: int = 12) -> None:
    """Dessine du texte de droite à gauche."""
    text = reshape_arabic(text)
    c.setFont(font, size)
    text_width = c.stringWidth(text, font, size)
    c.drawString(x - text_width, y, text)

def _draw_center(c: canvas.Canvas, text: str, x: float, y: float, *, font: str = FONT_ARABIC, size: int = 12) -> None:
    """Dessine du texte centré."""
    text = reshape_arabic(text)
    c.setFont(font, size)
    half = c.stringWidth(text, font, size) / 2
    c.drawString(x - half, y, text)

# ---------------------------------------------------------------------------
# Recherche de signature
# ---------------------------------------------------------------------------

def find_signature_file(custom_path: Optional[str] = None) -> Optional[str]:
    """Trouve le premier fichier de signature existant."""
    _SEARCH_DIRS = [
        ".",
        "images", 
        "signatures",
        os.path.join(os.getcwd(), "images"),
        os.path.join(os.path.dirname(__file__), "images"),
    ]
    
    _SIGNATURE_NAMES = ["signature", "Signature", "singature", "sign"]
    _SIGNATURE_EXTS = [".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]
    
    if custom_path and os.path.isfile(custom_path):
        return custom_path

    for directory in _SEARCH_DIRS:
        for name in _SIGNATURE_NAMES:
            for ext in _SIGNATURE_EXTS:
                candidate = os.path.normpath(os.path.join(directory, name + ext))
                if os.path.isfile(candidate):
                    return candidate
    return None

# ---------------------------------------------------------------------------
# Fonction pour dessiner une page de congé
# ---------------------------------------------------------------------------

def draw_conge_page(c: canvas.Canvas, data: Dict, signature_path: Optional[str] = None, signature_width: float = 6.0) -> None:
    """
    Dessine une page de congé complète sur le canvas.
    
    Args:
        c: Canvas ReportLab
        data: Dictionnaire contenant les données de l'employé
        signature_path: Chemin vers l'image de signature
        signature_width: Largeur de la signature en cm
    """
    PAGE_W, PAGE_H = A4
    
    # En-tête du document
    _draw_center(c, "الجمهورية الجزائرية الديمقراطية الشعبية", PAGE_W / 2, PAGE_H - 1.5 * cm, font=FONT_ARABIC, size=14)
    _draw_rtl(c, "وزارة التعليم العالي والبحث العلمي", PAGE_W - 2 * cm, PAGE_H - 2.5 * cm)
    _draw_rtl(c, "الديوان الوطني للخدمات الجامعية", PAGE_W - 2 * cm, PAGE_H - 3.5 * cm)
    _draw_rtl(c, "مديرية الخدمات الجامعية بالشلف", PAGE_W - 2 * cm, PAGE_H - 4.5 * cm)

    # Informations de date et numéro
    date_actuelle = data.get("date_actuelle", datetime.now().strftime("%d-%m-%Y"))
    year = data.get("annee", str(datetime.now().year))
    numero = data.get("numero_document", "...........")
    
    _draw_rtl(c, f"الرقم: {numero}/ ق.م.ب/{year}", PAGE_W - 2 * cm, PAGE_H - 5.5 * cm)

    # Titre
    _draw_center(c, "سـنــد عطــلــة", PAGE_W / 2, PAGE_H - 8 * cm, font=FONT_ARABIC_BOLD, size=18)

    # Références légales
    _draw_rtl(
        c,
        "– بمقتضى الأمر رقم 06–03 المؤرخ في 15 جويلية 2006 المتضمن القانون الأساسي العام للوظيفة العمومية",
        PAGE_W - 2 * cm,
        PAGE_H - 9.5 * cm,
    )
    _draw_rtl(
        c,
        "– بمقتضى القانون رقم 81–08 المؤرخ في 27 جوان 1981 المتعلق بالعطل السنوية",
        PAGE_W - 2 * cm,
        PAGE_H - 10.7 * cm,
    )

    # Données personnelles
    nom = data.get("nom", "")
    prenom = data.get("prenom", "")
    _draw_rtl(c, f"– بناء على طلب المعني(ة): {nom} {prenom}", PAGE_W - 2 * cm, PAGE_H - 11.9 * cm)
    
    y_cursor = PAGE_H - 13.1 * cm
    
    # Residence (lieu de travail)
    residence = data.get("residence", "")
    if residence:
        _draw_rtl(c, f"– مكان العمل : {residence}", PAGE_W - 2 * cm, y_cursor)
        y_cursor -= 1.2 * cm
    
    # Grade (رتبة)
    grade = data.get("grade", "")
    if grade:
        _draw_rtl(c, f"– الرتبة: {grade}", PAGE_W - 2 * cm, y_cursor)
        y_cursor -= 1.2 * cm

    # Poste supérieur (optionnel)
    poste_sup = data.get("poste_superieur", "")
    if poste_sup:
        _draw_rtl(c, f"– الوظيفة : {poste_sup}", PAGE_W - 2 * cm, y_cursor)
        y_cursor -= 1.2 * cm

    # Type de congé
    type_conge = data.get("type_conge", "عطلة سنوية")
    
    # Détails du congé
    date_debut = data.get("date_debut", "")
    date_fin = data.get("date_fin", "")
    jours_pris = data.get("jours_pris", "0")
    nouveau_reste = data.get("nouveau_reste", "0")
    lieu = data.get("lieu", "")
    
    _draw_rtl(
        c,
        f"يستفيد المعني(ة) من {type_conge} لسنة {year} ابتداءً من {date_debut} إلى غاية {date_fin}",
        PAGE_W - 2 * cm,
        y_cursor,
    )
    _draw_rtl(c, f"المدة: {jours_pris} يوم", PAGE_W - 2 * cm, y_cursor - 1.2 * cm)
    _draw_rtl(c, f"الباقي: {nouveau_reste} يوم", PAGE_W - 6 * cm, y_cursor - 1.2 * cm)
    _draw_rtl(c, f"مكان الإقامة خلال العطلة: {lieu}", PAGE_W - 2 * cm, y_cursor - 2.4 * cm)

    # Pied de page - signature
    _draw_rtl(c, f"حرر بـ الشلف في: {date_actuelle}", 2 * cm + 7 * cm, PAGE_H - 20.1 * cm)
    HR_X = 2 * cm + 5 * cm
    HR_Y = PAGE_H - 21.3 * cm
    _draw_center(c, "رئيس قسم الموارد البشرية", HR_X, HR_Y, font=FONT_ARABIC_BOLD, size=12)

    # Signature
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

    # Ligne de contact en bas
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    y_line = 2.5 * cm
    c.line(2 * cm, y_line, PAGE_W - 2 * cm, y_line)
    _draw_center(
        c,
        "مديرية الخدمات الجامعية شلف          رقم الهاتف 25 19 72 027         البريد الالكتروني dou02.drh@ONOUchlef.com",
        PAGE_W / 2,
        y_line - 0.5 * cm,
        font=FONT_ARABIC,
        size=10,
    )

# ---------------------------------------------------------------------------
# Fonction principale de génération par résidence
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
        employees_data: Liste de dictionnaires contenant les données des employés
        residence_name: Nom de la résidence
        output_dir: Répertoire de sortie (par défaut: Desktop)
        signature_path: Chemin vers l'image de signature
        auto_open: Ouvrir automatiquement le PDF après création
    
    Returns:
        Chemin absolu du PDF généré
    """
    
    # Recherche de la signature
    signature_path = find_signature_file(signature_path)
    if signature_path:
        print(f"✅ Signature trouvée: {signature_path}")
    else:
        print("⚠️ Aucune signature trouvée - continuation sans signature")

    # Définir le chemin de sortie
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Nom du fichier
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_residence = residence_name.replace(" ", "_").replace("/", "-")
    filename = f"سند_عطلة_{safe_residence}_{timestamp}.pdf"
    save_path = os.path.join(output_dir, filename)

    try:
        # Créer le canvas PDF
        c = canvas.Canvas(save_path, pagesize=A4)
        
        # Générer une page pour chaque employé
        for idx, employee in enumerate(employees_data, 1):
            print(f"📄 Génération page {idx}/{len(employees_data)} - {employee.get('nom', '')} {employee.get('prenom', '')}")
            
            # Dessiner la page de congé
            draw_conge_page(c, employee, signature_path)
            
            # Ajouter une nouvelle page si ce n'est pas le dernier employé
            if idx < len(employees_data):
                c.showPage()
        
        # Sauvegarder le PDF
        c.save()
        print(f"✅ PDF créé avec succès: {save_path}")
        print(f"📊 Total de pages: {len(employees_data)}")
        
        # Ouverture automatique si demandé
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
                    
                print(f"📂 PDF ouvert automatiquement")
            except Exception as e:
                print(f"⚠️ Impossible d'ouvrir automatiquement: {e}")
        
        return save_path
        
    except Exception as exc:
        print(f"❌ Erreur lors de la génération du PDF: {exc}")
        import traceback
        traceback.print_exc()
        return None

# ---------------------------------------------------------------------------
# Fonction pour grouper les employés par résidence
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

# ---------------------------------------------------------------------------
# Fonction principale pour l'impression sélective (similaire à votre exemple)
# ---------------------------------------------------------------------------

def print_selected_conge(
    selected_rows: List[tuple],
    database_connection,
    language: str = "ar",
    output_dir: Optional[str] = None,
    signature_path: Optional[str] = None,
    auto_open: bool = True
) -> None:
    """
    Imprime les PDFs de congé des employés sélectionnés, groupés par résidence.
    
    Args:
        selected_rows: Liste des lignes sélectionnées du tableau
        database_connection: Connexion à la base de données
        language: Langue d'impression ("ar" ou "fr")
        output_dir: Répertoire de sortie
        signature_path: Chemin vers l'image de signature
        auto_open: Ouvrir automatiquement les PDFs
    """
    
    if not selected_rows:
        messagebox.showwarning("تنبيه", "يرجى اختيار موظف واحد على الأقل")
        return
    
    count = len(selected_rows)
    lang_text = "العربية" if language == "ar" else "الفرنسية"
    
    confirm = messagebox.askyesno(
        "تأكيد الطباعة",
        f"سيتم طباعة {count} وثيقة باللغة {lang_text}\n\nهل تريد المتابعة؟"
    )
    
    if not confirm:
        return
    
    try:
        # Récupérer les données complètes depuis la base de données
        employees_data = []
        
        for row in selected_rows:
            # Adapter selon la structure de votre table
            # Exemple: supposons que row[9] contient l'ID de l'employé
            employee_id = row[9] if len(row) > 9 else row[0]
            
            # Récupérer les données depuis la base de données
            # IMPORTANT: Remplacez cette partie par votre requête SQL réelle
            cursor = database_connection.cursor()
            cursor.execute("""
                SELECT 
                    nom, prenom, grade, residence, 
                    poste_superieur, type_conge,
                    date_debut, date_fin, jours_pris, 
                    nouveau_reste, lieu, annee, 
                    date_actuelle, numero_document
                FROM employes_conge 
                WHERE id = ?
            """, (employee_id,))
            
            result = cursor.fetchone()
            
            if result:
                employee_data = {
                    "nom": result[0],
                    "prenom": result[1],
                    "grade": result[2],
                    "residence": result[3],
                    "poste_superieur": result[4],
                    "type_conge": result[5],
                    "date_debut": result[6],
                    "date_fin": result[7],
                    "jours_pris": result[8],
                    "nouveau_reste": result[9],
                    "lieu": result[10],
                    "annee": result[11],
                    "date_actuelle": result[12],
                    "numero_document": result[13],
                }
                employees_data.append(employee_data)
        
        # Grouper par résidence
        grouped = group_employees_by_residence(employees_data)
        
        print(f"📊 {len(grouped)} résidences trouvées")
        
        # Générer un PDF par résidence
        generated_pdfs = []
        
        for residence, employees in grouped.items():
            print(f"\n🏢 Traitement résidence: {residence} ({len(employees)} employés)")
            
            pdf_path = generate_conge_pdf_by_residence(
                employees_data=employees,
                residence_name=residence,
                output_dir=output_dir,
                signature_path=signature_path,
                auto_open=auto_open
            )
            
            if pdf_path:
                generated_pdfs.append(pdf_path)
        
        # Message de confirmation
        total_pages = len(employees_data)
        total_pdfs = len(generated_pdfs)
        
        messagebox.showinfo(
            "نجح",
            f"تم إنشاء {total_pdfs} وثيقة PDF بنجاح\n"
            f"إجمالي الصفحات: {total_pages}\n"
            f"المقر: {', '.join(grouped.keys())}"
        )
        
        print(f"\n✅ Génération terminée avec succès!")
        print(f"📄 {total_pdfs} PDF(s) créé(s)")
        print(f"📊 {total_pages} page(s) au total")
        
    except Exception as e:
        error_msg = f"فشل في إنشاء الوثائق:\n{str(e)}"
        messagebox.showerror("خطأ", error_msg)
        print(f"❌ Erreur: {e}")

# ---------------------------------------------------------------------------
# Exemple d'utilisation
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Exemple de données
    exemple_employees = [
        {
            "nom": "بن علي",
            "prenom": "محمد",
            "grade": "أستاذ محاضر قسم أ",
            "residence": "الإقامة الجامعية بن سهلة",
            "poste_superieur": "رئيس المصلحة",
            "type_conge": "عطلة سنوية",
            "date_debut": "01-03-2026",
            "date_fin": "15-03-2026",
            "jours_pris": "15",
            "nouveau_reste": "15",
            "lieu": "الشلف",
            "annee": "2026",
            "date_actuelle": "15-02-2026",
            "numero_document": "001/ق.م.ب/2026"
        },
        {
            "nom": "حمدي",
            "prenom": "فاطمة",
            "grade": "ملحق إداري",
            "residence": "الإقامة الجامعية بن سهلة",
            "poste_superieur": "",
            "type_conge": "عطلة سنوية",
            "date_debut": "01-04-2026",
            "date_fin": "20-04-2026",
            "jours_pris": "20",
            "nouveau_reste": "10",
            "lieu": "وهران",
            "annee": "2026",
            "date_actuelle": "15-02-2026",
            "numero_document": "002/ق.م.ب/2026"
        },
        {
            "nom": "العربي",
            "prenom": "أحمد",
            "grade": "تقني سامي",
            "residence": "الإقامة الجامعية الحضنة",
            "poste_superieur": "",
            "type_conge": "عطلة سنوية",
            "date_debut": "10-03-2026",
            "date_fin": "25-03-2026",
            "jours_pris": "16",
            "nouveau_reste": "14",
            "lieu": "الجزائر",
            "annee": "2026",
            "date_actuelle": "15-02-2026",
            "numero_document": "003/ق.م.ب/2026"
        }
    ]
    
    # Tester la génération groupée par résidence
    grouped = group_employees_by_residence(exemple_employees)
    
    for residence, employees in grouped.items():
        print(f"\n🏢 Génération pour: {residence}")
        generate_conge_pdf_by_residence(
            employees_data=employees,
            residence_name=residence,
            auto_open=False
        )