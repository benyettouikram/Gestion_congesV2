import sqlite3
import os

def get_employe_by_id(employe_id):
    """
    Récupère les données d’un employé par son ID.
    """
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, "..", "..", "..", "database", "gestion_conges.db")
    db_path = os.path.abspath(db_path)

    if not os.path.exists(db_path):
        print("❌ Base de données introuvable :", db_path)
        return None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
        SELECT 
            id_employe, residence, residenceF, departement,
            nom, prenom, NomF, prenomF,
            date_naissance, grade, gradeF,
            poste_superieur, poste_superieurF, ancien_conges
        FROM employes
        WHERE id_employe = ?
        """

        cursor.execute(query, (employe_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "residence": row[1] or "",
                "residenceF": row[2] or "",
                "departement": row[3] or "",
                "nom": row[4] or "",
                "prenom": row[5] or "",
                "NomF": row[6] or "",
                "prenomF": row[7] or "",
                "date_naissance": row[8] or "",
                "grade": row[9] or "",
                "gradeF": row[10] or "",
                "poste_superieur": row[11] or "",
                "poste_superieurF": row[12] or "",
                "ancien_conges": row[13] or 0
            }
        else:
            print(f"❌ Aucun employé trouvé avec l’ID {employe_id}")
            return None

    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l’employé {employe_id} : {e}")
        return None
