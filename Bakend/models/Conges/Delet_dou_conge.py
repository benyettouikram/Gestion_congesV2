import sqlite3
import os


def clear_conge_data(
    id_employe,
    residence_required="مديرية الخدمات الجامعية"
):
    """
    Vide les données de congé d'un employé (au lieu de supprimer l'employé)
    """
    try:
        # Database path
        base_dir = os.path.dirname(__file__)
        db_path = os.path.abspath(
            os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
        )

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Vérifier que l'employé appartient à la résidence DOU
        cursor.execute("""
            SELECT 1
            FROM employes
            WHERE id_employe = ?
              AND TRIM(residence) = TRIM(?)
        """, (id_employe, residence_required))

        if not cursor.fetchone():
            conn.close()
            print("❌ Opération refusée (résidence non DOU)")
            return False

        # Récupérer tous les id_conge de cet employé
        cursor.execute("""
            SELECT id_conge
            FROM conges
            WHERE id_employe = ?
        """, (id_employe,))
        
        conge_ids = [row[0] for row in cursor.fetchall()]

        # Supprimer d'abord les périodes associées
        if conge_ids:
            placeholders = ','.join('?' * len(conge_ids))
            cursor.execute(f"""
                DELETE FROM conge_periodes 
                WHERE id_conge IN ({placeholders})
            """, conge_ids)

        # Supprimer tous les congés de cet employé
        cursor.execute("""
            DELETE FROM conges
            WHERE id_employe = ?
        """, (id_employe,))

        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()

        print(f"✅ Données de congé supprimées pour l'employé {id_employe} ({rows_affected} congés)")
        return True

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        print(f"⚠️ Erreur lors de la suppression des congés: {e}")
        return False


