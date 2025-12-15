import sqlite3
import os

def init_database():
    """Initialise la base de données SQLite à partir du fichier schema.sql"""
    db_path = os.path.join("database", "gestion_conges.db")
    schema_path = os.path.join("database", "schema.sql")  # ✅ Corrigé: "schema" au lieu de "shema"

    # Créer le dossier database s'il n'existe pas
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    if not os.path.exists(schema_path):
        print(f"❌ Fichier de schéma introuvable : {schema_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)

    conn.commit()
    conn.close()
    print("✅ Base de données initialisée avec succès.")