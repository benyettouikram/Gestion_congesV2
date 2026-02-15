from datetime import datetime
import sqlite3
import os


# ================================
# GET EMPLOYES (Residence = DOU)
# ================================
def get_employes_data():
    base_dir = os.path.dirname(__file__)
    db_path = os.path.abspath(
        os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
    )

    if not os.path.exists(db_path):
        print("❌ Base de données introuvable :", db_path)
        return []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
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
            WHERE residence = 'مديرية الخدمات الجامعية'
            ORDER BY departement, nom_prenom ASC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        reordered = []
        for row in rows:
            (
                id_employe,
                departement,
                nom_prenom,
                grade,
                ancien_conges,
                date_debut,
                date_fin,
                jours_pris,
                nouveau_reste
            ) = row

            # ترتيب الأعمدة مع وضع ID آخر للمعالجة الداخلية فقط
            reordered.append((
                nouveau_reste,
                jours_pris,
                date_fin,
                date_debut,
                ancien_conges,
                grade,
                nom_prenom,
                departement,
                id_employe  # 👈 hidden ID
            ))

        return reordered

    except Exception as e:
        print(f"❌ Erreur lors du chargement des données : {e}")
        return []
# ================================
# GET SINGLE EMPLOYE BY ID (SAFE)
# ================================
def get_employe_by_id(employe_id):
    """
    Get employee ONLY if residence = 'مديرية الخدمات الجامعية'
    """

    base_dir = os.path.dirname(__file__)
    db_path = os.path.abspath(
        os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
    )

    if not os.path.exists(db_path):
        print("❌ Base de données introuvable :", db_path)
        return None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_employe, nom, prenom, grade
            FROM employes
            WHERE id_employe = ?
              AND residence = 'مديرية الخدمات الجامعية'
        """, (employe_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "id_employe": row[0],  # ✅ Added this!
            "nom": row[1],
            "prenom": row[2],
            "grade": row[3]
        }

    except Exception as e:
        print("❌ DB ERROR:", e)
        return None
    

def get_conge_by_employe_id(employe_id):
    """
    ✅ Récupérer les données de congé d'un employé avec TOUTES les informations nécessaires
    """
    try:
        base_dir = os.path.dirname(__file__)
        db_path = os.path.abspath(
            os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
        )
        
        if not os.path.exists(db_path):
            print("❌ Base de données introuvable")
            return None
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ✅ Récupérer le congé le plus récent
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
        
        # ✅ Récupérer les périodes associées
        cursor.execute("""
            SELECT date_debut, date_fin, nb_jours
            FROM conge_periodes
            WHERE id_conge = ?
            ORDER BY date_debut
        """, (id_conge,))
        
        periodes = cursor.fetchall()
        conn.close()
        
        # ✅ Retourner un dictionnaire complet
        conge_data = {
            "id_conge": result[0],        # ✅ TRÈS IMPORTANT!
            "type_conge": result[1],
            "date_debut": result[2],
            "date_fin": result[3],
            "nb_jours": result[4],
            "lieu": result[5],
            "statut": result[6],
            "periodes": periodes          # ✅ Liste des périodes
        }
        
        print(f"✅ Congé chargé: id_conge={conge_data['id_conge']}, nb_periodes={len(periodes)}")
        return conge_data
        
    except Exception as e:
        print(f"❌ Erreur get_conge_by_employe_id: {e}")
        return None


def get_employe_by_id(employe_id):
    """
    ✅ Récupérer les informations d'un employé
    """
    try:
        base_dir = os.path.dirname(__file__)
        db_path = os.path.abspath(
            os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
        )
        
        if not os.path.exists(db_path):
            print("❌ Base de données introuvable")
            return None
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id_employe, nom, prenom, grade
            FROM employes
            WHERE id_employe = ?
        """, (employe_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id_employe": result[0],
                "nom": result[1],
                "prenom": result[2],
                "grade": result[3]
            }
        
        return None
        
    except Exception as e:
        print(f"❌ Erreur get_employe_by_id: {e}")
        return None

def get_employee_pdf_data(employe_id):
    """
    ✅ Récupère TOUTES les données nécessaires pour générer un PDF de congé
    Compatible avec votre structure de base de données
    
    Args:
        employe_id: ID de l'employé (int ou str)
    
    Returns:
        Dictionnaire complet avec toutes les données pour le PDF
    """
    try:
        # ✅ CORRECTION: Convertir employe_id en integer
        employe_id = int(employe_id)
        
        base_dir = os.path.dirname(__file__)
        db_path = os.path.abspath(
            os.path.join(base_dir, "..", "..", "database", "gestion_conges.db")
        )
        
        if not os.path.exists(db_path):
            print("❌ Base de données introuvable")
            return None
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ✅ Récupérer les données de l'employé ET de son congé en une seule requête
        cursor.execute("""
            SELECT 
                e.id_employe,
                e.nom,
                e.prenom,
                e.grade,
                e.residence,
                e.departement,
                COALESCE(e.ancien_conges, 0) AS ancien_conges,
                e.poste_superieur,
                v.premiere_date_debut,
                v.derniere_date_fin,
                v.jours_pris,
                v.nouveau_reste
            FROM employes e
            LEFT JOIN vue_conges_reste v ON e.id_employe = v.id_employe
            WHERE e.id_employe = ?
                AND e.residence = 'مديرية الخدمات الجامعية'
        """, (employe_id,))
        
        result = cursor.fetchone()
        
        if not result:
            # ✅ Debug: vérifier si l'employé existe mais avec mauvaise résidence
            cursor.execute("SELECT residence FROM employes WHERE id_employe = ?", (employe_id,))
            check = cursor.fetchone()
            if check:
                print(f"⚠️ Employé {employe_id} trouvé mais résidence = '{check[0]}' (attendu: 'مديرية الخدمات الجامعية')")
            else:
                print(f"⚠️ Employé {employe_id} n'existe pas dans la base")
            conn.close()
            return None
        
        # ✅ Vérifier si l'employé a des congés
        if not result[8]:  # premiere_date_debut est NULL
            print(f"⚠️ Employé {employe_id} ({result[1]} {result[2]}) n'a pas de congé enregistré cette année")
            # ✅ Optionnel: retourner quand même avec des valeurs par défaut
            # ou retourner None pour ignorer cet employé
            # Pour l'instant, on retourne None
            conn.close()
            return None
        
        # ✅ Récupérer le lieu du congé
        cursor.execute("""
            SELECT lieu
            FROM conges
            WHERE id_employe = ?
            ORDER BY date_debut DESC
            LIMIT 1
        """, (employe_id,))
        
        lieu_result = cursor.fetchone()
        lieu = lieu_result[0] if lieu_result else "الشلف"
        
        conn.close()
        
        # ✅ Construire le dictionnaire pour le PDF
        pdf_data = {
            "nom": result[1] or "",
            "prenom": result[2] or "",
            "grade": result[3] or "",
            "residence": result[4] or "مديرية الخدمات الجامعية",
            "departement": result[5] or "",
            "ancien_conges": result[6] or 0,
            "poste_superieur": result[7] or "",
            "type_conge": "عطلة سنوية",  # Type par défaut
            "date_debut": result[8] or "",
            "date_fin": result[9] or "",
            "jours_pris": str(result[10] or 0),
            "nouveau_reste": str(result[11] or 30),
            "lieu": lieu,
            "annee": str(datetime.now().year),
            "date_actuelle": datetime.now().strftime("%d-%m-%Y"),
            "numero_document": f"{employe_id:03d}/ق.م.ب/{datetime.now().year}",
        }
        
        print(f"✅ Données PDF récupérées pour {pdf_data['nom']} {pdf_data['prenom']}")
        return pdf_data
        
    except ValueError as ve:
        print(f"❌ Erreur: employe_id invalide '{employe_id}' - {ve}")
        return None
    except Exception as e:
        print(f"❌ Erreur get_employee_pdf_data: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_multiple_employees_pdf_data(employe_ids):
    """
    ✅ Récupère les données PDF pour plusieurs employés en une seule fois
    
    Args:
        employe_ids: Liste des IDs d'employés [1, 5, 8, 12]
    
    Returns:
        Liste de dictionnaires contenant les données pour chaque employé
    """
    employees_data = []
    
    for employe_id in employe_ids:
        pdf_data = get_employee_pdf_data(employe_id)
        if pdf_data:
            employees_data.append(pdf_data)
        else:
            print(f"⚠️ Aucune donnée trouvée pour l'employé {employe_id}")
    
    print(f"📊 {len(employees_data)}/{len(employe_ids)} employés avec données complètes")
    return employees_data


