import sqlite3
import os
from datetime import datetime


def update_conge(id_conge, id_employe, type_conge, periodes, lieu):
    """
    ✅ Mettre à jour un congé existant (comme insert_conge)
    """
    try:
        base_dir = os.path.dirname(__file__)
        db_path = os.path.abspath(
            os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
        )
        
        if not os.path.exists(db_path):
            return False, "قاعدة البيانات غير موجودة"
        
        if not periodes or len(periodes) == 0:
            return False, "يجب تحديد تاريخ البداية والنهاية"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ✅ 1. Vérifier que le congé existe
        cursor.execute("""
            SELECT id_conge FROM conges
            WHERE id_conge = ? AND id_employe = ?
        """, (id_conge, id_employe))
        
        if not cursor.fetchone():
            conn.close()
            return False, "العطلة غير موجودة"
        
        # ✅ 2. Calculer le total de jours et la plage globale
        total_jours = sum((fin - debut).days + 1 for debut, fin in periodes)
        date_debut_global = min(debut for debut, fin in periodes)
        date_fin_global = max(fin for debut, fin in periodes)
        
        # ✅ 3. Mettre à jour la table conges (comme insert_conge)
        cursor.execute("""
            UPDATE conges
            SET type_conge = ?, 
                date_debut = ?,
                date_fin = ?,
                nb_jours = ?,
                lieu = ?
            WHERE id_conge = ? AND id_employe = ?
        """, (
            type_conge, 
            date_debut_global.strftime("%Y-%m-%d"),
            date_fin_global.strftime("%Y-%m-%d"),
            total_jours,
            lieu, 
            id_conge, 
            id_employe
        ))
        
        # ✅ 4. Supprimer les anciennes périodes
        cursor.execute("""
            DELETE FROM conge_periodes
            WHERE id_conge = ?
        """, (id_conge,))
        
        # ✅ 5. Insérer les nouvelles périodes (comme insert_conge)
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
        
        # ✅ 6. Ajouter à l'historique (comme insert_conge)
        nb_periodes = len(periodes)
        commentaire = f"تم تحديث العطلة مع {nb_periodes} فترة/فترات" if nb_periodes > 1 else "تم تحديث العطلة"
        
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
            "تحديث عطلة",
            datetime.now().year,
            commentaire
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Congé {id_conge} mis à jour avec succès")
        return True, "تم تحديث العطلة بنجاح"
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        print(f"❌ Erreur update_conge: {e}")
        return False, f"خطأ في التحديث: {str(e)}"