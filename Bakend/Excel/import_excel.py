import sqlite3
import openpyxl
import os
from datetime import datetime

def import_employes_from_excel():
    """Importe les employés depuis un fichier Excel vers la base SQLite"""
    db_path = os.path.join("database", "gestion_conges.db")
    excel_path = os.path.join("Excel", "Employes.xlsx")

    if not os.path.exists(excel_path):
        print("❌ Fichier Excel introuvable :", os.path.abspath(excel_path))
        return

    try:
        wb = openpyxl.load_workbook(excel_path)
        sheet = wb.active

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        inserted = 0
        skipped = 0

        for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            # Vérifie qu’il y a des données
            if not any(row):
                skipped += 1
                continue

            try:
                (residenceF, residence, departement, nomF, prenomF, nom, prenom,
                 date_naissance, gradeF, grade, poste_superieur, poste_superieurF,
                 ancien_conges) = row
            except ValueError:
                print(f"⚠️ Ligne {idx} contient un nombre de colonnes invalide ({len(row)} colonnes).")
                skipped += 1
                continue

            # Nettoyage des valeurs
            departement = departement or "—"
            poste_superieur = poste_superieur or "Aucun"
            poste_superieurF = poste_superieurF or "Aucun"
            ancien_conges = ancien_conges or 0

            # Format date
            if isinstance(date_naissance, datetime):
                date_naissance = date_naissance.strftime("%Y-%m-%d")

            try:
                cursor.execute("""
                    INSERT INTO employes (
                        residenceF, residence, departement, nomF, prenomF, nom, prenom,
                        date_naissance, gradeF, grade, poste_superieur, poste_superieurF, ancien_conges
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (residenceF, residence, departement, nomF, prenomF, nom, prenom,
                      date_naissance, gradeF, grade, poste_superieur, poste_superieurF, ancien_conges))
                inserted += 1

            except Exception as e:
                print(f"⚠️ Erreur ligne {idx}: {e}")
                skipped += 1

        conn.commit()
        conn.close()
        wb.close()

        print(f"✅ Import terminé : {inserted} employés ajoutés.")
        if skipped > 0:
            print(f"⚠️ {skipped} lignes ignorées (vides ou erreurs).")

    except Exception as e:
        print(f"❌ Erreur générale lors de l'import : {e}")
