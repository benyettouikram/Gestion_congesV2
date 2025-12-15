import sqlite3
import os

def search_employes(search_text=None):
    """Recherche les employés dans la base de données selon un texte donné."""
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
    db_path = os.path.abspath(db_path)

    if not os.path.exists(db_path):
        print("❌ Base de données introuvable :", db_path)
        return []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 🧩 Requête SQL de base
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
        """

        # 🔍 Si une recherche est fournie, on ajoute un WHERE
        params = ()
        if search_text:
            search_text = f"%{search_text.strip()}%"
            query += """
                WHERE 
                    e.nom LIKE ? OR 
                    e.prenom LIKE ? OR 
                    e.residence LIKE ? OR 
                    e.departement LIKE ? OR 
                    e.grade LIKE ? OR 
                    e.poste_superieur LIKE ?
            """
            params = (search_text, search_text, search_text, search_text, search_text, search_text)

        query += " ORDER BY e.id_employe ASC"
        cursor.execute(query, params)

        rows = cursor.fetchall()
        conn.close()

        # ✅ Réorganiser les colonnes pour l’ordre RTL du tableau
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

        return reordered

    except Exception as e:
        print(f"❌ Erreur lors de la recherche : {e}")
        return []
