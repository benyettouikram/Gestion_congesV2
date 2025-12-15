import sqlite3
import os

def update_employe(
    employe_id,
    residence,
    residenceF,
    departement,
    nom,
    prenom,
    NomF,
    prenomF,
    date_naissance,
    grade,
    gradeF,
    poste_superieur,
    poste_superieurF,
    ancien_conges
):
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, "..", "..", "..", "database", "gestion_conges.db")
    db_path = os.path.abspath(db_path)

    if not os.path.exists(db_path):
        print("❌ Base de données introuvable :", db_path)
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
        UPDATE employes
        SET 
            residence = ?, residenceF = ?, departement = ?,
            nom = ?, prenom = ?, NomF = ?, prenomF = ?,
            date_naissance = ?, grade = ?, gradeF = ?,
            poste_superieur = ?, poste_superieurF = ?, ancien_conges = ?
        WHERE id_employe = ?
        """

        cursor.execute(query, (
            residence, residenceF, departement,
            nom, prenom, NomF, prenomF,
            date_naissance, grade, gradeF,
            poste_superieur, poste_superieurF, ancien_conges,
            employe_id
        ))

        conn.commit()
        conn.close()
        print(f"✅ Employé {employe_id} mis à jour avec succès.")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour de l’employé {employe_id} : {e}")
        return False
