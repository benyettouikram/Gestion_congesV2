import sqlite3, os

db_path = os.path.join("database", "gestion_conges.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Show structure of vue_conges_reste
cursor.execute("PRAGMA table_info(employes);")
for row in cursor.fetchall():
    print(row)

conn.close()
