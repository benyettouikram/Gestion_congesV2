"""
Bakend/models/Historique/GenericHistorique.py
─────────────────────────────────────────────
Reads historique directly — does NOT depend on the conges JOIN.

Why: historique_conges VIEW joins LEFT JOIN conges. After a DELETE the
conges row is gone and nb_jours / dates come back NULL. After an INSERT
the screen may not have refreshed yet. Both cases cause empty rows.

Fix: parse nb_jours out of h.commentaire, which the SQL triggers always
write in the form:
    'من: YYYY-MM-DD إلى: YYYY-MM-DD | عدد الأيام: N'
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


# ─── helpers ──────────────────────────────────────────────────────────────────

def _parse_nb_jours(commentaire):
    """
    Extract nb_jours from a trigger commentaire string.
    Example:
        'تمت إضافة عطلة تلقائياً | من: 2025-01-01 إلى: 2025-01-10 | عدد الأيام: 10'
    Returns int or empty string if not found.
    """
    if not commentaire:
        return ""
    match = re.search(r'عدد الأيام[:\s]+(\d+)', commentaire)
    return int(match.group(1)) if match else ""


# ─── get_historique_data ──────────────────────────────────────────────────────

def get_historique_data():
    """
    Return all historique rows ordered by most recent action.

    Reads historique + employes ONLY — no dependency on conges table.
    nb_jours is parsed from h.commentaire so deleted congés still show
    their day count correctly.

    Tuple order (matches Historique.py DataTable column order):
        index 0 → action           (الإجراء)
        index 1 → annee            (السنة)
        index 2 → nb_jours         (عدد الأيام)
        index 3 → date_naissance   (تاريخ الميلاد)
        index 4 → grade            (الرتبة)
        index 5 → employe_complet  (الاسم و اللقب)
        index 6 → id_employe       (المعرف)
    """
    try:
        conn   = _connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                h.action,
                h.annee,
                h.commentaire,
                e.date_naissance,
                e.grade,
                e.nom || ' ' || e.prenom  AS employe_complet,
                h.id_employe
            FROM historique h
            LEFT JOIN employes e ON e.id_employe = h.id_employe
            ORDER BY h.date_action DESC
        """)
        raw = cursor.fetchall()
        conn.close()

        rows = []
        for action, annee, commentaire, date_naissance, grade, emp, id_emp in raw:
            rows.append((
                action         or "",
                annee          or "",
                _parse_nb_jours(commentaire),
                date_naissance or "",
                grade          or "",
                emp            or "",
                id_emp         or "",
            ))
        return rows

    except Exception as e:
        print(f"❌ get_historique_data: {e}")
        return []


# ─── search_historique ────────────────────────────────────────────────────────

def search_historique(search_text):
    """
    Filter by employee name, grade, action, or year.
    Returns same tuple shape as get_historique_data().
    """
    if not search_text or not search_text.strip():
        return get_historique_data()

    term = f"%{search_text.strip()}%"

    try:
        conn   = _connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                h.action,
                h.annee,
                h.commentaire,
                e.date_naissance,
                e.grade,
                e.nom || ' ' || e.prenom  AS employe_complet,
                h.id_employe
            FROM historique h
            LEFT JOIN employes e ON e.id_employe = h.id_employe
            WHERE
                (e.nom || ' ' || e.prenom) LIKE ? OR
                e.grade                    LIKE ? OR
                h.action                   LIKE ? OR
                CAST(h.annee AS TEXT)      LIKE ?
            ORDER BY h.date_action DESC
        """, (term, term, term, term))
        raw = cursor.fetchall()
        conn.close()

        rows = []
        for action, annee, commentaire, date_naissance, grade, emp, id_emp in raw:
            rows.append((
                action         or "",
                annee          or "",
                _parse_nb_jours(commentaire),
                date_naissance or "",
                grade          or "",
                emp            or "",
                id_emp         or "",
            ))
        return rows

    except Exception as e:
        print(f"❌ search_historique: {e}")
        return []