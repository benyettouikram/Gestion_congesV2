import sqlite3
import os

def get_employes_data():
    """Retourne la liste des employés avec résidence, département et informations principales."""
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
    db_path = os.path.abspath(db_path)

    if not os.path.exists(db_path):
        print("❌ Base de données introuvable :", db_path)
        return []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # ✅ Récupération des colonnes dans l’ordre logique de la base
        query = """
            SELECT 
                e.id_employe,
                e.residence,
                e.departement,
                e.nom || ' ' || e.prenom AS nom_prenom,
                e.date_naissance,
                e.grade,
                e.poste_superieur,
                e.ancien_conges
            FROM employes e
            ORDER BY e.id_employe ASC;
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        # ✅ Réorganisation pour correspondre à l’ordre du tableau (UI RTL)
        reordered = []
        for row in rows:
            (
                id_employe,
                residence,
                departement,
                nom_prenom,
                date_naissance,
                grade,
                poste_superieur,
                ancien_conges
            ) = row

            reordered.append((
                ancien_conges,       # العطلة القديمة
                poste_superieur,     # المنصب الأعلى
                grade,               # الرتبة
                date_naissance,      # تاريخ الميلاد
                nom_prenom,          # الاسم و اللقب
                departement,         # القسم
                residence,           # مكان الإقامة
                id_employe           # المعرف
            ))

        return reordered  # ✅ retourne les données dans l’ordre d’affichage de la table

    except Exception as e:
        print(f"❌ Erreur lors du chargement des données : {e}")
        return []
