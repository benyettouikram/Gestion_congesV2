import sqlite3
import os
from datetime import datetime


def insert_conge(
    id_employe,
    type_conge,
    periodes,  # List of (date_debut, date_fin) tuples
    lieu,
    residence_required="مديرية الخدمات الجامعية"
):
    """
    Insert a congé with multiple periods OR single period
    """
    base_dir = os.path.dirname(__file__)
    db_path = os.path.abspath(
        os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
    )

    if not os.path.exists(db_path):
        return False, "قاعدة البيانات غير موجودة"

    if not periodes or len(periodes) == 0:
        return False, "يجب تحديد تاريخ البداية والنهاية"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1️⃣ Verify employee + residence
        cursor.execute("""
            SELECT id_employe
            FROM employes
            WHERE id_employe = ?
              AND residence = ?
        """, (id_employe, residence_required))

        if not cursor.fetchone():
            conn.close()
            return False, "الموظف غير تابع لهذه الإقامة"

        # 2️⃣ Calculate total days and overall date range
        total_jours = sum((fin - debut).days + 1 for debut, fin in periodes)
        date_debut_global = min(debut for debut, fin in periodes)
        date_fin_global = max(fin for debut, fin in periodes)

        # 3️⃣ Insert main congé record
        cursor.execute("""
            INSERT INTO conges (
                id_employe,
                type_conge,
                date_debut,
                date_fin,
                nb_jours,
                lieu,
                statut
            ) VALUES (?, ?, ?, ?, ?, ?, 'en_attente')
        """, (
            id_employe,
            type_conge,
            date_debut_global.strftime("%Y-%m-%d"),
            date_fin_global.strftime("%Y-%m-%d"),
            total_jours,
            lieu
        ))

        id_conge = cursor.lastrowid

        # 4️⃣ Insert all periods into conge_periodes table
        for date_debut, date_fin in periodes:
            nb_jours_periode = (date_fin - date_debut).days + 1
            
            cursor.execute("""
                INSERT INTO conge_periodes (
                    id_conge,
                    date_debut,
                    date_fin,
                    nb_jours
                ) VALUES (?, ?, ?, ?)
            """, (
                id_conge,
                date_debut.strftime("%Y-%m-%d"),
                date_fin.strftime("%Y-%m-%d"),
                nb_jours_periode
            ))

        # 5️⃣ Insert historique
        nb_periodes = len(periodes)
        commentaire = f"تمت إضافة عطلة مع {nb_periodes} فترة/فترات" if nb_periodes > 1 else "تمت إضافة عطلة"
        
        cursor.execute("""
            INSERT INTO historique (
                id_employe,
                id_conge,
                action,
                annee,
                commentaire
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            id_employe,
            id_conge,
            "إضافة عطلة",
            datetime.now().year,
            commentaire
        ))

        conn.commit()
        conn.close()

        return True, "تمت إضافة العطلة بنجاح"

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False, f"خطأ في قاعدة البيانات: {e}"


def get_conge_periodes(id_conge):
    """Get all periods for a specific congé"""
    base_dir = os.path.dirname(__file__)
    db_path = os.path.abspath(
        os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
    )
    
    if not os.path.exists(db_path):
        print("❌ Base de données introuvable")
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date_debut, date_fin, nb_jours
            FROM conge_periodes
            WHERE id_conge = ?
            ORDER BY date_debut
        """, (id_conge,))
        
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des périodes: {e}")
        return []





