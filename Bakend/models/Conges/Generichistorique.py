"""
Bakend/models/Historique/GenericHistorique.py
"""

import os
import re
import sqlite3


def _db_path():
    base_dir = os.path.dirname(__file__)
    return os.path.abspath(
        os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
    )


def _connect():
    path = _db_path()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Base de données introuvable : {path}")
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL;")   # ← prevents lock issues
    conn.execute("PRAGMA foreign_keys=ON;")    # ← ensures triggers fire
    return conn


def _parse_nb_jours(commentaire):
    if not commentaire:
        return ""
    match = re.search(r'عدد الأيام[:\s]*(\d+)', commentaire)
    return int(match.group(1)) if match else ""


def _fetch(extra_where="", params=()):
    try:
        conn   = _connect()
        cursor = conn.cursor()

        query = f"""
            SELECT
                h.id_historique,
                h.id_employe,
                e.nom || ' ' || e.prenom   AS employe_complet,
                e.grade,
                e.date_naissance,
                COALESCE(c.nb_jours,
                    CAST(
                        (SELECT nb_jours FROM conges
                         WHERE id_conge = h.id_conge) 
                    AS INTEGER)
                )                          AS nb_jours,
                h.commentaire,
                h.annee,
                h.action,
                v.nouveau_reste
            FROM historique h
            INNER JOIN (
                SELECT id_employe, MAX(id_historique) AS max_id
                FROM historique
                GROUP BY id_employe
            ) latest ON h.id_historique = latest.max_id
            LEFT JOIN employes         e ON e.id_employe = h.id_employe
            LEFT JOIN conges           c ON c.id_conge   = h.id_conge
            LEFT JOIN vue_conges_reste v ON v.id_employe = h.id_employe
            WHERE 1=1
            {extra_where}
            ORDER BY h.date_action DESC
        """

        cursor.execute(query, params)
        raw = cursor.fetchall()
        conn.close()

        rows = []
        for (id_hist, id_emp, emp, grade, date_naissance,
             nb_jours, commentaire, annee, action, nouveau_reste) in raw:

            jours = nb_jours if nb_jours is not None else _parse_nb_jours(commentaire)

            rows.append((
                nouveau_reste  if nouveau_reste is not None else "",  # 0
                annee          or "",                                  # 1
                jours          or "",                                  # 2
                grade          or "",                                  # 3
                date_naissance or "",                                  # 4
                emp            or "",                                  # 5
                id_emp         or "",                                  # 6  hidden
                id_hist,                                               # 7  hidden
            ))
        return rows

    except Exception as e:
        print(f"❌ _fetch historique: {e}")
        return []


def ensure_triggers(conn):
    """
    Re-create the three triggers if they are missing.
    Call once at startup so the DB is always consistent.
    """
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TRIGGER IF NOT EXISTS trg_after_insert_conge
        AFTER INSERT ON conges
        BEGIN
            INSERT INTO historique (id_employe, id_conge, action, annee, commentaire)
            VALUES (
                NEW.id_employe,
                NEW.id_conge,
                'إضافة عطلة',
                CAST(strftime('%Y', NEW.date_debut) AS INTEGER),
                'تمت إضافة عطلة تلقائياً | ' ||
                'من: ' || NEW.date_debut || ' إلى: ' || NEW.date_fin ||
                ' | عدد الأيام: ' || NEW.nb_jours
            );
        END;

        CREATE TRIGGER IF NOT EXISTS trg_after_update_conge
        AFTER UPDATE ON conges
        BEGIN
            INSERT INTO historique (id_employe, id_conge, action, annee, commentaire)
            VALUES (
                NEW.id_employe,
                NEW.id_conge,
                'تحديث عطلة',
                CAST(strftime('%Y', NEW.date_debut) AS INTEGER),
                'تم تحديث العطلة | ' ||
                'من: ' || NEW.date_debut || ' إلى: ' || NEW.date_fin ||
                ' | عدد الأيام: ' || NEW.nb_jours
            );
        END;

        CREATE TRIGGER IF NOT EXISTS trg_after_delete_conge
        AFTER DELETE ON conges
        BEGIN
            INSERT INTO historique (id_employe, id_conge, action, annee, commentaire)
            VALUES (
                OLD.id_employe,
                OLD.id_conge,
                'حذف عطلة',
                CAST(strftime('%Y', OLD.date_debut) AS INTEGER),
                'تم حذف العطلة | ' ||
                'من: ' || OLD.date_debut || ' إلى: ' || OLD.date_fin ||
                ' | عدد الأيام: ' || OLD.nb_jours
            );
        END;
    """)
    conn.commit()


def init_db():
    """Call this once when the app starts."""
    try:
        conn = _connect()
        ensure_triggers(conn)
        conn.close()
        print("✅ DB triggers verified.")
    except Exception as e:
        print(f"❌ init_db: {e}")


def delete_historique(id_historique):
    try:
        conn   = _connect()
        cursor = conn.cursor()

        id_historique = int(id_historique)
        cursor.execute(
            "DELETE FROM historique WHERE id_historique = ?",
            (id_historique,)
        )
        affected = cursor.rowcount
        conn.commit()
        conn.close()

        if affected:
            print(f"✅ historique row {id_historique} deleted")
        else:
            print(f"⚠️  no row found with id_historique={id_historique}")

    except Exception as e:
        print(f"❌ delete_historique: {e}")


def get_historique_data():
    return _fetch()


def search_historique(search_text):
    if not search_text or not search_text.strip():
        return get_historique_data()

    term = f"%{search_text.strip()}%"
    extra = """
        AND (
            (e.nom || ' ' || e.prenom) LIKE ? OR
            e.grade                    LIKE ? OR
            h.action                   LIKE ? OR
            CAST(h.annee AS TEXT)      LIKE ?
        )
    """
    return _fetch(extra_where=extra, params=(term, term, term, term))