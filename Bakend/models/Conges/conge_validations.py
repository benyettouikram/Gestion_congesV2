import sqlite3
import os


def check_employe_has_conge_en_cours(id_employe):
    """
    ✅ Vérifier si l'employé a déjà un congé en attente ou validé
    Returns: (has_conge: bool, conge_data: dict or None)
    """
    try:
        base_dir = os.path.dirname(__file__)
        db_path = os.path.abspath(
            os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
        )
        
        if not os.path.exists(db_path):
            return False, None
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier les congés en attente ou validés
        cursor.execute("""
            SELECT id_conge, type_conge, date_debut, date_fin, nb_jours, statut
            FROM conges
            WHERE id_employe = ? 
            AND statut IN ('en_attente', 'validé')
            ORDER BY date_debut DESC
            LIMIT 1
        """, (id_employe,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            conge_data = {
                "id_conge": result[0],
                "type_conge": result[1],
                "date_debut": result[2],
                "date_fin": result[3],
                "nb_jours": result[4],
                "statut": result[5]
            }
            return True, conge_data
        
        return False, None
        
    except Exception as e:
        print(f"❌ Erreur check_employe_has_conge_en_cours: {e}")
        return False, None


def get_solde_conge(id_employe):
    """
    ✅ Récupérer le solde de congé disponible
    Returns: (conge_ancien, conge_annuel, total_disponible)
    """
    try:
        base_dir = os.path.dirname(__file__)
        db_path = os.path.abspath(
            os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
        )
        
        if not os.path.exists(db_path):
            return 0, 0, 0
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ✅ D'abord, vérifier quelles colonnes existent
        cursor.execute("PRAGMA table_info(employes)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"🔍 Colonnes disponibles dans employes: {columns}")
        
        # ✅ Adapter la requête selon les colonnes disponibles
        # Support the schema which uses `ancien_conges` + default annual 30 days
        if 'ancien_conges' in columns:
            cursor.execute("""
                SELECT ancien_conges
                FROM employes
                WHERE id_employe = ?
            """, (id_employe,))
            result = cursor.fetchone()
            if result:
                conge_ancien = result[0] or 0
                conge_annuel = 30
                total_disponible = conge_ancien + conge_annuel
                conn.close()
                return conge_ancien, conge_annuel, total_disponible

        if 'conge_ancien' in columns and 'conge_annuel' in columns:
            # Cas 1: colonnes conge_ancien et conge_annuel existent
            cursor.execute("""
                SELECT conge_ancien, conge_annuel
                FROM employes
                WHERE id_employe = ?
            """, (id_employe,))
            result = cursor.fetchone()
            if result:
                conge_ancien = result[0] or 0
                conge_annuel = result[1] or 0
                total_disponible = conge_ancien + conge_annuel
                conn.close()
                return conge_ancien, conge_annuel, total_disponible
        
        elif 'solde_conge' in columns:
            # Cas 2: colonne solde_conge existe
            cursor.execute("""
                SELECT solde_conge
                FROM employes
                WHERE id_employe = ?
            """, (id_employe,))
            result = cursor.fetchone()
            if result:
                solde_conge = result[0] or 0
                conn.close()
                return 0, solde_conge, solde_conge
        
        elif 'nb_jours_conge' in columns:
            # Cas 3: colonne nb_jours_conge existe
            cursor.execute("""
                SELECT nb_jours_conge
                FROM employes
                WHERE id_employe = ?
            """, (id_employe,))
            result = cursor.fetchone()
            if result:
                nb_jours_conge = result[0] or 0
                conn.close()
                return 0, nb_jours_conge, nb_jours_conge
        
        else:
            # Cas 4: aucune colonne de congé trouvée, utiliser une valeur par défaut
            print("⚠️ Aucune colonne de congé trouvée, utilisation de 30 jours par défaut")
            conn.close()
            return 0, 30, 30
        
        conn.close()
        return 0, 0, 0
        
    except Exception as e:
        print(f"❌ Erreur get_solde_conge: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0, 0


def get_jours_conge_pris(id_employe, annee=None):
    """
    ✅ Calculer le nombre de jours de congé déjà pris par l'employé
    """
    try:
        base_dir = os.path.dirname(__file__)
        db_path = os.path.abspath(
            os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
        )
        
        if not os.path.exists(db_path):
            return 0
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if annee:
            cursor.execute("""
                SELECT COALESCE(SUM(nb_jours), 0)
                FROM conges
                WHERE id_employe = ? 
                AND statut IN ('validé', 'en_attente')
                AND strftime('%Y', date_debut) = ?
            """, (id_employe, str(annee)))
        else:
            cursor.execute("""
                SELECT COALESCE(SUM(nb_jours), 0)
                FROM conges
                WHERE id_employe = ? 
                AND statut IN ('validé', 'en_attente')
            """, (id_employe,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0
        
    except Exception as e:
        print(f"❌ Erreur get_jours_conge_pris: {e}")
        return 0


def validate_conge_solde(id_employe, nb_jours_demande, id_conge_to_exclude=None):
    """
    ✅ Valider que le nombre de jours demandé ne dépasse pas le solde disponible
    
    🧠 LOGIQUE:
    - Pour INSERT: Vérifie si nb_jours_demande <= solde_restant
    - Pour UPDATE: REMPLACE l'ancien congé par le nouveau (pas d'addition!)
    
    Exemple:
    - Total: 30 jours
    - Congé actuel: 20 jours
    - UPDATE à 30 jours → 30 jours total (pas 50!)
    """
    try:
        # Récupérer le solde disponible
        conge_ancien, conge_annuel, total_disponible = get_solde_conge(id_employe)
        
        if total_disponible == 0:
            print("⚠️ Attention: solde_conge = 0, vérifiez la structure de la table employes")
        
        # Calculer les jours déjà pris
        base_dir = os.path.dirname(__file__)
        db_path = os.path.abspath(
            os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
        )
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer les jours de l'ancien congé si UPDATE
        jours_ancien_conge = 0
        if id_conge_to_exclude:
            cursor.execute("""
                SELECT nb_jours
                FROM conges
                WHERE id_conge = ?
            """, (id_conge_to_exclude,))
            result = cursor.fetchone()
            if result:
                jours_ancien_conge = result[0]
                print(f"🔄 UPDATE: {jours_ancien_conge} jours ➜ {nb_jours_demande} jours")
        
        # ✅ Calculer les jours pris SANS le congé qu'on modifie
        if id_conge_to_exclude:
            cursor.execute("""
                SELECT COALESCE(SUM(nb_jours), 0)
                FROM conges
                WHERE id_employe = ? 
                AND statut IN ('validé', 'en_attente')
                AND id_conge != ?
            """, (id_employe, id_conge_to_exclude))
        else:
            cursor.execute("""
                SELECT COALESCE(SUM(nb_jours), 0)
                FROM conges
                WHERE id_employe = ? 
                AND statut IN ('validé', 'en_attente')
            """, (id_employe,))
        
        jours_deja_pris_autres = cursor.fetchone()[0]
        conn.close()
        
        # Solde restant
        solde_restant = total_disponible - jours_deja_pris_autres
        total_jours_pris = jours_deja_pris_autres + (jours_ancien_conge if id_conge_to_exclude else 0)
        
        print(f"""
🧮 CALCUL:
   Total disponible: {total_disponible} jours
   Autres congés: {jours_deja_pris_autres} jours
   {"Ancien congé (sera remplacé): " + str(jours_ancien_conge) + " jours" if id_conge_to_exclude else ""}
   Solde restant: {solde_restant} jours
   Nouveau congé demandé: {nb_jours_demande} jours
   ➜ {nb_jours_demande} <= {solde_restant}? {'✅ OUI' if nb_jours_demande <= solde_restant else '❌ NON'}
        """)
        
        solde_info = {
            "conge_ancien": conge_ancien,
            "conge_annuel": conge_annuel,
            "total_disponible": total_disponible,
            "jours_deja_pris": jours_deja_pris_autres,
            "jours_ancien_conge": jours_ancien_conge,
            "total_jours_pris": total_jours_pris,
            "solde_restant": solde_restant,
            "nb_jours_demande": nb_jours_demande
        }
        
        # Vérifier si le solde est suffisant
        if nb_jours_demande > solde_restant:
            if id_conge_to_exclude:
                message = f"""
❌ الرصيد غير كافٍ!

الرصيد المتاح: {total_disponible} يوم
  • عطلة قديمة: {conge_ancien} يوم
  • عطلة سنوية: {conge_annuel} يوم

العطل الأخرى المأخوذة: {jours_deja_pris_autres} يوم
العطلة الحالية (سيتم استبدالها): {jours_ancien_conge} يوم
الرصيد المتبقي (بدون العطلة الحالية): {solde_restant} يوم

الأيام المطلوبة للعطلة الجديدة: {nb_jours_demande} يوم
النقص: {nb_jours_demande - solde_restant} يوم
                """
            else:
                message = f"""
❌ الرصيد غير كافٍ!

الرصيد المتاح: {total_disponible} يوم
  • عطلة قديمة: {conge_ancien} يوم
  • عطلة سنوية: {conge_annuel} يوم

الأيام المأخوذة: {jours_deja_pris_autres} يوم
الرصيد المتبقي: {solde_restant} يوم

الأيام المطلوبة: {nb_jours_demande} يوم
النقص: {nb_jours_demande - solde_restant} يوم
                """
            return False, message.strip(), solde_info
        
        # ✅ Solde suffisant
        if id_conge_to_exclude:
            difference = nb_jours_demande - jours_ancien_conge
            message = f"""
✅ الرصيد كافٍ

الرصيد المتبقي (بدون العطلة الحالية): {solde_restant} يوم
العطلة القديمة: {jours_ancien_conge} يوم ➜ العطلة الجديدة: {nb_jours_demande} يوم
الفرق: {difference:+d} يوم

الرصيد بعد التعديل: {solde_restant - nb_jours_demande} يوم
            """
        else:
            message = f"""
✅ الرصيد كافٍ

الرصيد المتبقي: {solde_restant} يوم
الأيام المطلوبة: {nb_jours_demande} يوم
الرصيد بعد العطلة: {solde_restant - nb_jours_demande} يوم
            """
        return True, message.strip(), solde_info
        
    except Exception as e:
        print(f"❌ Erreur validate_conge_solde: {e}")
        import traceback
        traceback.print_exc()
        return False, f"خطأ في التحقق من الرصيد: {str(e)}", {}