# data_real_ci.py — PETROCI PRO
# Génère des données proches de la réalité CI
# Basées sur rapports publics ENI, TotalEnergies, PETROCI

import numpy as np
import sqlite3
from datetime import date, timedelta
from config import PROFILS_PUITS

DB_PATH = "petroci_pro.db"

def generer_donnees_realistes(nb_jours=730):
    """
    Génère 2 ans de données de production
    calées sur les productions réelles connues des champs CI
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c    = conn.cursor()

    # Vérifier si déjà peuplé
    c.execute("SELECT COUNT(*) FROM production_journaliere")
    if c.fetchone()[0] > 500:
        conn.close()
        return

    date_fin   = date.today()
    date_debut = date_fin - timedelta(days=nb_jours)
    donnees    = []
    date_cur   = date_debut

    np.random.seed(42)  # Reproductibilité

    while date_cur <= date_fin:
        j = (date_cur - date_debut).days

        for nom, p in PROFILS_PUITS.items():
            champ = p["champ"]

            # Facteur saisonnier (léger effet météo offshore)
            mois     = date_cur.month
            saison   = 1.0 + 0.03 * np.sin(2 * np.pi * mois / 12)

            # Déclin exponentiel + bruit réaliste
            facteur  = np.exp(-p["declin"] * j)
            bruit    = np.random.normal(1.0, 0.04)  # ±4% variation
            prod     = max(0, p["prod_base"] * facteur * saison * bruit)

            # Événements aléatoires (arrêts maintenance)
            prob_arret = np.random.random()
            if prob_arret < 0.02:    # 2% chance arrêt complet
                heures = 0.0
                prod   = 0.0
            elif prob_arret < 0.05:  # 3% chance arrêt partiel
                heures = float(np.random.randint(12, 20))
                prod  *= heures / 24
            else:
                heures = 24.0

            # Water cut croissant + variations
            wc = min(
                p["wc_base"] + 0.00015 * j + np.random.normal(0, 0.01),
                0.97
            )
            wc = max(0, wc)

            # Production eau et gaz
            prod_eau = (prod * wc / max(1 - wc, 0.01)
                       if wc < 0.99 else prod * 30)

            # GOR varie avec pression réservoir
            gor_base  = 650 + np.random.normal(0, 50)
            gor_facteur = 1.0 + 0.2 * (1 - facteur)  # GOR augmente
            gor       = max(200, gor_base * gor_facteur)
            prod_gaz  = prod * gor / 1000

            # Pression décline
            # p["pression_tete"] = pression de tête initiale (clé config.py)
            pression_init = p.get("pression_tete", p.get("pression_base", 1000))
            pression  = max(
                pression_init * facteur * np.random.uniform(0.97, 1.03),
                100
            )

            # Température quasi constante
            temperature = np.random.normal(175, 5)

            # Statut
            if wc > 0.70 or (prod < 500 and heures > 0):
                statut = "Critique"
            elif wc > 0.55 or prod < 1500:
                statut = "Alerte"
            elif heures == 0:
                statut = "Arret"
            else:
                statut = "Actif"

            donnees.append((
                str(date_cur), nom, champ,
                round(prod, 0),
                round(prod_gaz, 3),
                round(prod_eau, 0),
                round(wc, 4),
                round(gor, 0),
                round(pression, 1),
                round(temperature, 1),
                heures, statut, "Systeme"
            ))

        date_cur += timedelta(days=1)

    c.executemany("""
        INSERT OR IGNORE INTO production_journaliere
        (date,puits,champ,
         production_huile_bbl,production_gaz_mmscf,
         production_eau_bbl,water_cut,gor,
         pression_tete_psi,temperature_f,
         heures_production,statut,saisie_par)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, donnees)

    conn.commit()
    conn.close()
    print(f"✓ {len(donnees)} enregistrements générés")


def generer_donnees_drilling():
    """
    Génère des données de forage réalistes
    pour les blocs en exploration CI
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c    = conn.cursor()

    c.execute("SELECT COUNT(*) FROM drilling_log")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    forages = [
        {
            "puits": "CI-101-EXP-1",
            "bloc":  "CI-101 Deep",
            "cible_m": 4200,
            "debut": date.today() - timedelta(days=45),
            "op":    "ENI / PETROCI"
        },
        {
            "puits": "CI-401-EXP-1",
            "bloc":  "CI-401",
            "cible_m": 3800,
            "debut": date.today() - timedelta(days=20),
            "op":    "TotalEnergies / PETROCI"
        },
    ]

    phases = [
        ("Conducteur 36\"",    0,    150,   "Phase surface"),
        ("Surface 26\"",     150,    800,   "Phase surface"),
        ("Intermediaire 17\"",800,  2500,   "Phase intermediaire"),
        ("Production 12\"", 2500,   4200,   "Phase production"),
    ]

    operations = [
        "Forage rotary", "Forage rotary", "Forage rotary",
        "Carottage", "Diagraphies", "Cimentation",
        "Forage rotary", "BHA change", "Test de pression"
    ]

    donnees = []
    for f in forages:
        profondeur = 0.0
        date_cur   = f["debut"]

        while profondeur < f["cible_m"] and date_cur <= date.today():
            # ROP varie selon la phase
            if profondeur < 150:
                rop = np.random.uniform(25, 45)
            elif profondeur < 800:
                rop = np.random.uniform(15, 30)
            elif profondeur < 2500:
                rop = np.random.uniform(8, 18)
            else:
                rop = np.random.uniform(3, 10)

            profondeur_jour = rop * 12  # 12h de forage/jour en moyenne
            profondeur      = min(profondeur + profondeur_jour, f["cible_m"])

            # Phase actuelle
            phase_nom = "Phase production"
            for ph in phases:
                if ph[1] <= profondeur <= ph[2]:
                    phase_nom = ph[3]
                    break

            operation = np.random.choice(operations)
            boue      = ("Eau douce" if profondeur < 800
                         else "Boue synthetique OBM")

            donnees.append((
                str(date_cur), f["puits"], f["bloc"],
                round(profondeur, 1), f["cible_m"],
                round(rop, 1), operation,
                phase_nom, boue,
                f"Forage nominal - {operation}",
                f["op"]
            ))
            date_cur += timedelta(days=1)

    c.executemany("""
        INSERT INTO drilling_log
        (date,puits,bloc,profondeur_actuelle_m,
         profondeur_cible_m,rop_m_heure,type_operation,
         phase,boue_type,commentaire,operateur)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, donnees)

    conn.commit()
    conn.close()
    print(f"✓ {len(donnees)} enregistrements forage générés")
