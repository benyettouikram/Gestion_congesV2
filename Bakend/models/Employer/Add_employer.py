import sqlite3
import os

def add_employe(
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
    """Ajoute un employé dans la base de données"""
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
    db_path = os.path.abspath(db_path)

    if not os.path.exists(db_path):
        print("❌ Base de données introuvable :", db_path)
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
        INSERT INTO employes (
            residence, residenceF, departement,
            nom, prenom, NomF, prenomF,
            date_naissance, grade, gradeF,
            poste_superieur, poste_superieurF, ancien_conges
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(query, (
            residence, residenceF, departement,
            nom, prenom, NomF, prenomF,
            date_naissance, grade, gradeF,
            poste_superieur, poste_superieurF, ancien_conges
        ))

        conn.commit()
        conn.close()
        print("✅ Employé ajouté avec succès.")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de l’ajout de l’employé : {e}")
        return False
