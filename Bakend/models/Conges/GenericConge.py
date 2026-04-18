"""
Bakend/models/Conges/GenericConge.py
─────────────────────────────────────
Generic CRUD backend that works for ANY residence.
Used by ResidenceBase (frontend) for add / update / delete congé.

All functions accept `residence_required` as an Arabic string
resolved from the short key via GenericResidence.resolve_residence_ar().

NOTE: historique is now written automatically by SQL triggers
      (trg_after_insert_conge / trg_after_update_conge / trg_after_delete_conge).
      No manual INSERT into historique is needed here.

Import map
──────────
    from Bakend.models.Conges.GenericConge import (
        insert_conge,
        update_conge,
        clear_conge_data,
        get_conge_periodes,
    )
"""

import os
import sqlite3
from datetime import datetime


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


# ─── insert_conge ──────────────────────────────────────────────────────────────

def insert_conge(
    id_employe,
    type_conge,
    periodes,               # list of (date_debut, date_fin) datetime.date tuples
    lieu,
    residence_required,     # Arabic string from resolve_residence_ar(key)
):
    """
    Insert a new congé for any residence.
    historique is recorded automatically by trg_after_insert_conge.

    Returns (True, success_message) or (False, error_message).
    """
    if not periodes:
        return False, "يجب تحديد تاريخ البداية والنهاية"

    try:
        conn   = _connect()
        cursor = conn.cursor()

        # ── 1. Verify employee belongs to this residence ───────────────────
        cursor.execute("""
            SELECT id_employe FROM employes
            WHERE id_employe = ?
              AND TRIM(residence) = TRIM(?)
        """, (id_employe, residence_required))

        if not cursor.fetchone():
            conn.close()
            return False, "الموظف غير تابع لهذه الإقامة"

        # ── 2. Aggregate date range & total days ───────────────────────────
        total_jours       = sum((fin - debut).days + 1 for debut, fin in periodes)
        date_debut_global = min(debut for debut, fin in periodes)
        date_fin_global   = max(fin   for debut, fin in periodes)

        # ── 3. Insert main congé record ────────────────────────────────────
        #       trg_after_insert_conge fires here automatically
        cursor.execute("""
            INSERT INTO conges
                (id_employe, type_conge, date_debut, date_fin, nb_jours, lieu, statut)
            VALUES (?, ?, ?, ?, ?, ?, 'en_attente')
        """, (
            id_employe,
            type_conge,
            date_debut_global.strftime("%Y-%m-%d"),
            date_fin_global.strftime("%Y-%m-%d"),
            total_jours,
            lieu,
        ))
        id_conge = cursor.lastrowid

        # ── 4. Insert periods ──────────────────────────────────────────────
        for debut, fin in periodes:
            cursor.execute("""
                INSERT INTO conge_periodes (id_conge, date_debut, date_fin, nb_jours)
                VALUES (?, ?, ?, ?)
            """, (
                id_conge,
                debut.strftime("%Y-%m-%d"),
                fin.strftime("%Y-%m-%d"),
                (fin - debut).days + 1,
            ))

        conn.commit()
        conn.close()

        print(f"✅ insert_conge: employe={id_employe}, résidence='{residence_required}', {total_jours}j")
        return True, "تمت إضافة العطلة بنجاح"

    except Exception as e:
        if "conn" in locals():
            conn.rollback()
            conn.close()
        print(f"❌ insert_conge: {e}")
        return False, f"خطأ في قاعدة البيانات: {e}"


# ─── update_conge ──────────────────────────────────────────────────────────────

def update_conge(id_conge, id_employe, type_conge, periodes, lieu):
    """
    Replace all periods of an existing congé.
    historique is recorded automatically by trg_after_update_conge.

    Returns (True, success_message) or (False, error_message).
    """
    if not periodes:
        return False, "يجب تحديد تاريخ البداية والنهاية"

    try:
        conn   = _connect()
        cursor = conn.cursor()

        # ── 1. Verify the congé belongs to this employee ───────────────────
        cursor.execute("""
            SELECT id_conge FROM conges
            WHERE id_conge = ? AND id_employe = ?
        """, (id_conge, id_employe))

        if not cursor.fetchone():
            conn.close()
            return False, "العطلة غير موجودة"

        # ── 2. Aggregate ───────────────────────────────────────────────────
        total_jours       = sum((fin - debut).days + 1 for debut, fin in periodes)
        date_debut_global = min(debut for debut, fin in periodes)
        date_fin_global   = max(fin   for debut, fin in periodes)

        # ── 3. Update main row ─────────────────────────────────────────────
        #       trg_after_update_conge fires here automatically
        cursor.execute("""
            UPDATE conges
            SET type_conge = ?,
                date_debut = ?,
                date_fin   = ?,
                nb_jours   = ?,
                lieu       = ?
            WHERE id_conge = ? AND id_employe = ?
        """, (
            type_conge,
            date_debut_global.strftime("%Y-%m-%d"),
            date_fin_global.strftime("%Y-%m-%d"),
            total_jours,
            lieu,
            id_conge,
            id_employe,
        ))

        # ── 4. Replace periods ─────────────────────────────────────────────
        cursor.execute("DELETE FROM conge_periodes WHERE id_conge = ?", (id_conge,))

        for debut, fin in periodes:
            cursor.execute("""
                INSERT INTO conge_periodes (id_conge, date_debut, date_fin, nb_jours)
                VALUES (?, ?, ?, ?)
            """, (
                id_conge,
                debut.strftime("%Y-%m-%d"),
                fin.strftime("%Y-%m-%d"),
                (fin - debut).days + 1,
            ))

        conn.commit()
        conn.close()

        print(f"✅ update_conge: id_conge={id_conge}, {total_jours}j")
        return True, "تم تحديث العطلة بنجاح"

    except Exception as e:
        if "conn" in locals():
            conn.rollback()
            conn.close()
        print(f"❌ update_conge: {e}")
        return False, f"خطأ في التحديث: {e}"


# ─── clear_conge_data ─────────────────────────────────────────────────────────

def clear_conge_data(id_employe, residence_required):
    """
    Delete all congé records for an employee (employee row stays intact).
    historique is recorded automatically by trg_after_delete_conge for each row.

    Parameters
    ----------
    id_employe          : int
    residence_required  : str   Arabic name from resolve_residence_ar(key)
                                e.g. "الاقامة الجامعية 19 ماي 1956"

    Returns True on success, False on failure.
    """
    try:
        # ── Ensure id_employe is a real int, not a dash or empty string ───
        employe_id = int(id_employe)
    except (ValueError, TypeError):
        print(f"❌ clear_conge_data: id_employe invalide → '{id_employe}'")
        return False

    try:
        conn   = _connect()
        cursor = conn.cursor()

        # ── Debug: show what is actually in the DB for this employee ──────
        cursor.execute(
            "SELECT id_employe, residence FROM employes WHERE id_employe = ?",
            (employe_id,)
        )
        db_row = cursor.fetchone()
        if db_row:
            print(f"🔍 DB  résidence = {repr(db_row[1])}")
        print(f"🔍 ARG résidence = {repr(residence_required)}")

        # ── Residence guard ────────────────────────────────────────────────
        cursor.execute("""
            SELECT 1 FROM employes
            WHERE id_employe = ?
              AND TRIM(residence) = TRIM(?)
        """, (employe_id, residence_required))

        if not cursor.fetchone():
            conn.close()
            print(
                f"❌ clear_conge_data refusé : employe={employe_id} "
                f"ne correspond pas à résidence='{residence_required}'"
            )
            return False

        # ── Delete child periods first (FK) ────────────────────────────────
        #    Must delete conge_periodes BEFORE conges so the DELETE trigger
        #    on conges still finds its periods if needed.
        cursor.execute("""
            DELETE FROM conge_periodes
            WHERE id_conge IN (
                SELECT id_conge FROM conges WHERE id_employe = ?
            )
        """, (employe_id,))

        # ── Delete congés ──────────────────────────────────────────────────
        #    trg_after_delete_conge fires once per row deleted
        cursor.execute("DELETE FROM conges WHERE id_employe = ?", (employe_id,))
        rows_affected = cursor.rowcount

        conn.commit()
        conn.close()
        print(f"✅ clear_conge_data: employe={employe_id}, {rows_affected} congé(s) supprimé(s)")
        return True

    except Exception as e:
        if "conn" in locals():
            conn.rollback()
            conn.close()
        print(f"❌ clear_conge_data: {e}")
        return False


# ─── get_conge_periodes ───────────────────────────────────────────────────────

def get_conge_periodes(id_conge):
    """
    Return all periods for a congé as list of (date_debut, date_fin, nb_jours).
    """
    try:
        conn   = _connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date_debut, date_fin, nb_jours
            FROM conge_periodes
            WHERE id_conge = ?
            ORDER BY date_debut
        """, (id_conge,))
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print(f"❌ get_conge_periodes({id_conge}): {e}")
        return []