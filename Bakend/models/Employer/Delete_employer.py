import sqlite3
import os

def delete_employe_by_id(employe_id):
    """
    Supprime un employé de la base de données par son ID.
    """
    try:
        # ✅ Construct database path
        base_dir = os.path.dirname(__file__)
        db_path = os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
        db_path = os.path.abspath(db_path)

        # ✅ Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # ✅ Execute deletion query
        cursor.execute("DELETE FROM employes WHERE id_employe = ?", (employe_id,))

        # ✅ Commit changes and close connection
        conn.commit()
        conn.close()

        print(f"✅ Employé {employe_id} supprimé avec succès.")

    except Exception as e:
        print(f"⚠️ Erreur lors de la suppression de l'employé {employe_id}: {e}")
