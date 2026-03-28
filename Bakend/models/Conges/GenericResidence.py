"""
Bakend/models/Conges/GenericResidence.py
─────────────────────────────────────────
Generic backend functions that work for ANY residence.
IMPORTANT: Arabic strings must match EXACTLY what's in the DB.
           DB uses 'الاقامة' (no hamza) NOT 'الإقامة' (with hamza)
           DB uses 'اولاد' (no hamza) NOT 'أولاد' (with hamza)
           DB order: number BEFORE city  e.g. '1500 سرير الحسنية'
"""

import os
import sqlite3
from datetime import datetime


# ─── helpers ──────────────────────────────────────────────────────────────────

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


# ─── residence registry ───────────────────────────────────────────────────────
# ⚠️  Copied EXACTLY from debug_residences() repr() output.
#     DO NOT add hamza (إ / أ) — the DB does not use them.

RESIDENCE_AR = {
    "dou":       "مديرية الخدمات الجامعية",
    "mai1956":   "الاقامة الجامعية 19 ماي 1956",
    "nov1954":   "الاقامة الجامعية 1 نوفمبر 1954",
    "heni":      "الاقامة الجامعية هني صالح",
    "Touil":     "الاقامة الجامعية طويل عبد القادر",
    "ouled_fares_03":   "الاقامة الجامعية اولاد فارس 03",
    "ouled_fares_04":   "الاقامة الجامعية اولاد فارس 04",
    "hassania_1500": "الاقامة الجامعية 1500 سرير الحسنية",
    "hassania_2000": "الاقامة الجامعية 2000 سرير الحسنية",
    "tens_500":  "الاقامة الجامعية 500 سرير تنس",
}

RESIDENCE_FR = {
    "dou":       "Les Œuvres Universitaires",
    "mai1956":   "Résidence 19 Mai 1956",
    "nov1954":   "Résidence 1er Novembre 1954",
    "heni":      "Résidence Heni Saleh",
    "Touil":     "Résidence Tawil Abdelkader",
    "ouled_fares_03":   "Résidence Oulad Fares 03",
    "ouled_fares_04":   "Résidence Oulad Fares 04",
    "hassania_1500": "Résidence Hassania 1500 lits",
    "hassania_2000": "Résidence Hassania 2000 lits",
    "tens_500":  "Résidence Ténès 500 lits",
}


def resolve_residence_ar(key_or_value: str) -> str:
    return RESIDENCE_AR.get(key_or_value, key_or_value)


def resolve_residence_fr(key_or_value: str) -> str:
    return RESIDENCE_FR.get(key_or_value, key_or_value)


# ─── debug ────────────────────────────────────────────────────────────────────

def debug_residences():
    """Call once at startup to verify DB strings match RESIDENCE_AR."""
    conn = _connect()
    cursor = conn.cursor()

    print("\n=== TABLE employes ===")
    cursor.execute("SELECT DISTINCT residence FROM employes")
    for row in cursor.fetchall():
        print(f"  repr: {repr(row[0])}")

    print("\n=== VUE vue_conges_reste ===")
    cursor.execute("SELECT DISTINCT residence FROM vue_conges_reste")
    for row in cursor.fetchall():
        print(f"  repr: {repr(row[0])}")

    print("\n=== RESIDENCE_AR dict ===")
    for key, val in RESIDENCE_AR.items():
        print(f"  {key!r:12} → {repr(val)}")

    conn.close()


# ─── get_employes_data ────────────────────────────────────────────────────────

def get_employes_data(residence_key: str = "dou"):
    residence = resolve_residence_ar(residence_key)
    print(f"🔍 get_employes_data: key={residence_key!r} → {residence!r}")

    try:
        conn   = _connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id_employe,
                departement,
                nom || ' ' || prenom AS nom_prenom,
                grade,
                ancien_conges,
                premiere_date_debut,
                derniere_date_fin,
                jours_pris,
                nouveau_reste
            FROM vue_conges_reste
            WHERE TRIM(residence) = TRIM(?)
            ORDER BY departement, nom_prenom ASC
        """, (residence,))

        rows = cursor.fetchall()
        conn.close()

        print(f"✅ {len(rows)} employés trouvés pour {residence!r}")

        reordered = []
        for row in rows:
            (id_employe, departement, nom_prenom, grade,
             ancien_conges, date_debut, date_fin,
             jours_pris, nouveau_reste) = row

            reordered.append((
                nouveau_reste,
                jours_pris,
                date_fin,
                date_debut,
                ancien_conges,
                grade,
                nom_prenom,
                departement,
                id_employe,
            ))

        return reordered

    except Exception as e:
        print(f"❌ get_employes_data({residence_key}): {e}")
        return []


# ─── get_employe_by_id ────────────────────────────────────────────────────────

def get_employe_by_id(employe_id: int, residence_key: str = None):
    try:
        conn   = _connect()
        cursor = conn.cursor()

        if residence_key:
            residence = resolve_residence_ar(residence_key)
            cursor.execute("""
                SELECT id_employe, nom, prenom, grade
                FROM employes
                WHERE id_employe = ?
                  AND TRIM(residence) = TRIM(?)
            """, (employe_id, residence))
        else:
            cursor.execute("""
                SELECT id_employe, nom, prenom, grade
                FROM employes
                WHERE id_employe = ?
            """, (employe_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "id_employe": row[0],
            "nom":        row[1],
            "prenom":     row[2],
            "grade":      row[3],
        }

    except Exception as e:
        print(f"❌ get_employe_by_id({employe_id}): {e}")
        return None


# ─── get_conge_by_employe_id ──────────────────────────────────────────────────

def get_conge_by_employe_id(employe_id: int):
    try:
        conn   = _connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_conge, type_conge, date_debut, date_fin, nb_jours, lieu, statut
            FROM conges
            WHERE id_employe = ?
            ORDER BY date_debut DESC
            LIMIT 1
        """, (employe_id,))

        result = cursor.fetchone()
        if not result:
            conn.close()
            return None

        id_conge = result[0]

        cursor.execute("""
            SELECT date_debut, date_fin, nb_jours
            FROM conge_periodes
            WHERE id_conge = ?
            ORDER BY date_debut
        """, (id_conge,))

        periodes = cursor.fetchall()
        conn.close()

        return {
            "id_conge":   result[0],
            "type_conge": result[1],
            "date_debut": result[2],
            "date_fin":   result[3],
            "nb_jours":   result[4],
            "lieu":       result[5],
            "statut":     result[6],
            "periodes":   periodes,
        }

    except Exception as e:
        print(f"❌ get_conge_by_employe_id({employe_id}): {e}")
        return None


# ─── _base_pdf_data ───────────────────────────────────────────────────────────

def _base_pdf_data(employe_id: int, residence_key: str):
    employe_id   = int(employe_id)
    residence_ar = resolve_residence_ar(residence_key)

    try:
        conn   = _connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                e.id_employe,
                e.nom,   e.prenom,   e.grade,
                e.nomF,  e.prenomF,  e.gradeF,
                e.residence,   e.residenceF,
                e.departement,
                COALESCE(e.ancien_conges, 0) AS ancien_conges,
                e.poste_superieur,   e.poste_superieurF,
                v.premiere_date_debut,
                v.derniere_date_fin,
                v.jours_pris,
                v.nouveau_reste
            FROM employes e
            LEFT JOIN vue_conges_reste v ON e.id_employe = v.id_employe
            WHERE e.id_employe = ?
              AND TRIM(e.residence) = TRIM(?)
        """, (employe_id, residence_ar))

        result = cursor.fetchone()

        if not result:
            cursor.execute("SELECT residence FROM employes WHERE id_employe = ?",
                           (employe_id,))
            check = cursor.fetchone()
            if check:
                print(f"⚠️  Employé {employe_id}: résidence='{check[0]}' "
                      f"(attendu '{residence_ar}')")
            else:
                print(f"⚠️  Employé {employe_id} introuvable")
            conn.close()
            return None

        if not result[13]:
            print(f"⚠️  Employé {employe_id} sans congé enregistré cette année")
            conn.close()
            return None

        cursor.execute("""
            SELECT lieu, type_conge
            FROM conges
            WHERE id_employe = ?
            ORDER BY date_debut DESC
            LIMIT 1
        """, (employe_id,))

        lieu_row = cursor.fetchone()
        conn.close()

        return result, lieu_row

    except Exception as e:
        print(f"❌ _base_pdf_data({employe_id}, {residence_key}): {e}")
        import traceback; traceback.print_exc()
        return None


# ─── get_employee_pdf_Ar_data ─────────────────────────────────────────────────

def get_employee_pdf_Ar_data(employe_id: int, residence_key: str = "dou"):
    raw = _base_pdf_data(employe_id, residence_key)
    if raw is None:
        return None

    result, lieu_row = raw
    employe_id = int(employe_id)

    lieu       = lieu_row[0] if lieu_row else "الشلف"
    type_conge = lieu_row[1] if lieu_row else "عطلة سنوية"

    return {
        "nom":             result[1]  or "",
        "prenom":          result[2]  or "",
        "grade":           result[3]  or "",
        "residence":       result[7]  or resolve_residence_ar(residence_key),
        "departement":     result[9]  or "",
        "ancien_conges":   result[10] or 0,
        "poste_superieur": result[11] or "",
        "type_conge":      type_conge,
        "date_debut":      result[13] or "",
        "date_fin":        result[14] or "",
        "jours_pris":      str(result[15] or 0),
        "nouveau_reste":   str(result[16]),
        "lieu":            lieu,
        "annee":           str(datetime.now().year),
        "date_actuelle":   datetime.now().strftime("%d-%m-%Y"),
        "numero_document": f"{employe_id:03d}/ق.م.ب/{datetime.now().year}",
    }


def get_multiple_employees_pdf_Ar_data(employe_ids, residence_key: str = "dou"):
    results = []
    for eid in employe_ids:
        data = get_employee_pdf_Ar_data(eid, residence_key)
        if data:
            results.append(data)
        else:
            print(f"⚠️  Aucune donnée AR pour l'employé {eid}")
    print(f"📊 {len(results)}/{len(employe_ids)} employés AR OK")
    return results


# ─── get_employee_pdf_fr_data ─────────────────────────────────────────────────

def get_employee_pdf_fr_data(employe_id: int, residence_key: str = "dou"):
    raw = _base_pdf_data(employe_id, residence_key)
    if raw is None:
        return None

    result, lieu_row = raw
    employe_id = int(employe_id)

    lieu       = lieu_row[0] if lieu_row else "Chlef"
    type_conge = lieu_row[1] if lieu_row else "Congé annuel"

    return {
        "nom":             result[4]  or "",
        "prenom":          result[5]  or "",
        "grade":           result[6]  or "",
        "residence":       result[8]  or resolve_residence_fr(residence_key),
        "departement":     result[9]  or "",
        "ancien_conges":   result[10] or 0,
        "poste_superieur": result[12] or "",
        "type_conge":      type_conge,
        "date_debut":      result[13] or "",
        "date_fin":        result[14] or "",
        "jours_pris":      str(result[15] or 0),
        "nouveau_reste":   str(result[16]),
        "lieu":            lieu,
        "annee":           str(datetime.now().year),
        "date_actuelle":   datetime.now().strftime("%d/%m/%Y"),
        "numero_document": f"{employe_id:03d}/D.O.U.C/{datetime.now().year}",
    }


def get_multiple_employees_pdf_fr_data(employe_ids, residence_key: str = "dou"):
    results = []
    for eid in employe_ids:
        data = get_employee_pdf_fr_data(eid, residence_key)
        if data:
            results.append(data)
        else:
            print(f"⚠️  Aucune donnée FR pour l'employé {eid}")
    print(f"📊 {len(results)}/{len(employe_ids)} employés FR OK")
    return results