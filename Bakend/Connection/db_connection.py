import sqlite3
import os

def get_connection():
    """Crée et retourne une connexion SQLite, en s'assurant que le dossier existe."""
    db_dir = "database"
    os.makedirs(db_dir, exist_ok=True)

    db_path = os.path.join(db_dir, "gestion_conges.db")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # accès type dictionnaire (row["nom"])
    return conn
