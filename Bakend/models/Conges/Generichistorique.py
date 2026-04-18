"""
Bakend/models/Historique/GenericHistorique.py
─────────────────────────────────────────────
Returns only the LATEST historique row per employee.

Column order matches the DataTable display (RTL layout):
    The DataTable renders columns left→right on screen as:
        المعرف | الاسم و اللقب | الرتبة | تاريخ الميلاد | عدد الأيام | السنة | الإجراء

    So the tuple must be:
        index 0 → id_employe       (المعرف)
        index 1 → employe_complet  (الاسم و اللقب)
        index 2 → grade            (الرتبة)
        index 3 → date_naissance   (تاريخ الميلاد)
        index 4 → nb_jours         (عدد الأيام)
        index 5 → annee            (السنة)
        index 6 → action           (الإجراء)
"""

import os
import re
import sqlite3


# ─── DB helper ────────────────────────────────────────────────────────────────

def _db_path():
    base_dir = os.path.dirname(__file__)
    return os.path.abspath(
        os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
    )


def _connect():
    path = _db_path()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Base de données introuvable : {path}")
    return sqlite3.connect(path)


def _parse_nb_jours(commentaire):
    """Extract nb_jours from trigger commentaire string."""
    if not commentaire:
        return ""
    match = re.search(r'عدد الأيام[:\s]+(\d+)', commentaire)
    return int(match.group(1)) if match else ""


# ─── _fetch ───────────────────────────────────────────────────────────────────

def _fetch(extra_where="", params=()):
    """
    One row per employee (most recent action only).

    Tuple order matches screen column order left→right:
        0 → id_employe       (المعرف)
        1 → employe_complet  (الاسم و اللقب)
        2 → grade            (الرتبة)
        3 → date_naissance   (تاريخ الميلاد)
        4 → nb_jours         (عدد الأيام)   ← parsed from commentaire
        5 → annee            (السنة)
        6 → action           (الإجراء)
    """
    try:
        conn   = _connect()
        cursor = conn.cursor()

        query = f"""
            SELECT
                h.id_employe,
                e.nom || ' ' || e.prenom  AS employe_complet,
                e.grade,
                e.date_naissance,
                h.commentaire,
                h.annee,
                h.action
            FROM historique h
            LEFT JOIN employes e ON e.id_employe = h.id_employe
            WHERE h.id_historique IN (
                SELECT MAX(id_historique)
                FROM historique
                GROUP BY id_employe
            )
            {extra_where}
            ORDER BY h.date_action DESC
        """

        cursor.execute(query, params)
        raw = cursor.fetchall()
        conn.close()

        rows = []
        for id_emp, emp, grade, date_naissance, commentaire, annee, action in raw:
            rows.append((
                id_emp         or "",   # 0 → المعرف
                emp            or "",   # 1 → الاسم و اللقب
                grade          or "",   # 2 → الرتبة
                date_naissance or "",   # 3 → تاريخ الميلاد
                _parse_nb_jours(commentaire),  # 4 → عدد الأيام
                annee          or "",   # 5 → السنة
                action         or "",   # 6 → الإجراء
            ))
        return rows

    except Exception as e:
        print(f"❌ _fetch historique: {e}")
        return []


# ─── public API ───────────────────────────────────────────────────────────────

def get_historique_data():
    """Return the latest operation for every employee."""
    return _fetch()


def search_historique(search_text):
    """Filter latest-per-employee rows by name, grade, action, or year."""
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