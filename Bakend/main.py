import os
from Connection.db_connection import get_connection
from Excel.import_excel import import_employes_from_excel
from Controle.Init_db import init_database
def main():
    print("🚀 Lancement de l'application de gestion des congés")

    db_path = os.path.join( "database", "gestion_conges.db")

    # 🔥 Supprimer l'ancienne base si elle existe
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️ Ancienne base supprimée.")

    # ✅ Recréer la base avec le schéma
    init_database()

    # ✅ Importer employés depuis Excel
    import_employes_from_excel()

    # ✅ Vérification de la connexion et comptage employés
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM employes")
    nb = cursor.fetchone()[0]
    conn.close()

    print(f"📊 Nombre total d'employés en base : {nb}")

if __name__ == "__main__":
    main()
