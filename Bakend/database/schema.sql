--------------------------------------------
-- TABLE employes
--------------------------------------------
CREATE TABLE IF NOT EXISTS employes (
    id_employe INTEGER PRIMARY KEY AUTOINCREMENT,
    residenceF TEXT,
    residence TEXT,
    departement TEXT,
    nomF TEXT,
    prenomF TEXT,
    nom TEXT,
    prenom TEXT,
    date_naissance TEXT,
    gradeF TEXT,
    grade TEXT,
    poste_superieur TEXT,
    poste_superieurF TEXT,
    ancien_conges INTEGER DEFAULT 0
);

--------------------------------------------
-- TABLE conges
--------------------------------------------
CREATE TABLE IF NOT EXISTS conges (
    id_conge INTEGER PRIMARY KEY AUTOINCREMENT,
    id_employe INTEGER NOT NULL,
    type_conge TEXT NOT NULL,
    date_debut TEXT NOT NULL,
    date_fin TEXT NOT NULL,
    nb_jours INTEGER NOT NULL,
    lieu TEXT,
    statut TEXT DEFAULT 'en_attente',
    date_demande TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (id_employe) REFERENCES employes(id_employe) ON DELETE CASCADE
);

---TABLE of période -----------------------------

CREATE TABLE IF NOT EXISTS conge_periodes (
    id_periode INTEGER PRIMARY KEY AUTOINCREMENT,
    id_conge INTEGER NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    nb_jours INTEGER NOT NULL,
    FOREIGN KEY (id_conge) REFERENCES conges(id_conge) ON DELETE CASCADE
);
--------------------------------------------
-- TABLE historique
--------------------------------------------
CREATE TABLE IF NOT EXISTS historique (
    id_historique INTEGER PRIMARY KEY AUTOINCREMENT,
    id_employe INTEGER,
    id_conge INTEGER,
    action TEXT NOT NULL,
    annee INTEGER,
    date_action TEXT DEFAULT (datetime('now')),
    commentaire TEXT,
    FOREIGN KEY (id_employe) REFERENCES employes(id_employe) ON DELETE SET NULL,
    FOREIGN KEY (id_conge) REFERENCES conges(id_conge) ON DELETE SET NULL
);

--------------------------------------------
-- DELETE OLD VIEWS
--------------------------------------------
DROP VIEW IF EXISTS vue_conges_reste;
DROP VIEW IF EXISTS historique_conges;

--------------------------------------------
-- VIEW vue_conges_reste
--------------------------------------------
CREATE VIEW vue_conges_reste AS
SELECT
    e.id_employe,
    e.nom,
    e.prenom,
    e.grade,
    e.residence,
    e.departement,
    COALESCE(e.ancien_conges, 0) AS ancien_conges,
    IFNULL(SUM(c.nb_jours), 0) AS jours_pris,
    COALESCE(e.ancien_conges, 0) + 30 - IFNULL(SUM(c.nb_jours), 0) AS nouveau_reste,
    MIN(c.date_debut) AS premiere_date_debut,
    MAX(c.date_fin) AS derniere_date_fin
FROM employes e
LEFT JOIN conges c 
    ON e.id_employe = c.id_employe
    AND strftime('%Y', c.date_debut) = strftime('%Y', 'now')
GROUP BY e.id_employe
ORDER BY e.id_employe ASC;

--------------------------------------------
-- VIEW historique_conges
--------------------------------------------
CREATE VIEW historique_conges AS
SELECT 
    h.id_historique,
    e.nom || ' ' || e.prenom AS employe,
    e.residence,
    e.departement,
    c.type_conge,
    c.date_debut,
    c.date_fin,
    c.nb_jours,
    c.lieu,
    h.action,
    h.annee,
    h.date_action,
    h.commentaire
FROM historique h
LEFT JOIN employes e ON e.id_employe = h.id_employe
LEFT JOIN conges c ON c.id_conge = h.id_conge
ORDER BY h.date_action DESC;