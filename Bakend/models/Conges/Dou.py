import sqlite3
import os

def get_employes_data():
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
    db_path = os.path.abspath(db_path)

    if not os.path.exists(db_path):
        print("❌ Base de données introuvable :", db_path)
        return []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
            SELECT 
                id_employe,
                departement,
                nom || ' ' || prenom AS nom_prenom,
                grade,
                ancien_conges,
                premiere_date_debut,
                derniere_date_fin,
                jours_pris,
                nouveau_reste
            FROM vue_conges_reste
            WHERE residence = 'مديرية الخدمات الجامعية'
            ORDER BY departement, nom_prenom ASC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        reordered = []
        for row in rows:
            (
                id_emp,
                departement,
                nom_prenom,
                grade,
                ancien_conges,
                date_debut,
                date_fin,
                jours_pris,
                nouveau_reste
            ) = row  # <-- 9 valeurs

            reordered.append((
                # même ordre que tes colonnes du DataTable
                nouveau_reste,
                jours_pris,
                date_fin,
                date_debut,
                ancien_conges,
                grade,
                nom_prenom,
                departement,
                id_emp   # tu peux le stocker ici si tu veux
            ))

        return reordered

    except Exception as e:
        print(f"❌ Erreur lors du chargement des données : {e}")
        return []
