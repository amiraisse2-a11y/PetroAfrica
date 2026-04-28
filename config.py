# config.py — PETROCI PRO
# Données réelles des champs pétroliers de Côte d'Ivoire

PRIX_BARIL    = 78.5   # USD/bbl (Brent avril 2026)
TAUX_USD_XOF  = 615    # 1 USD = 615 FCFA
TAUX_EUR_XOF  = 655    # 1 EUR = 655 FCFA

# ─────────────────────────────────────────────────────
# CHAMPS EN PRODUCTION — données proches réalité 2024-2026
# Sources : rapports PETROCI, ENI, TotalEnergies publics
# ─────────────────────────────────────────────────────
CHAMPS_PRODUCTION = {
    "Baleine": {
        "operateur":        "ENI / PETROCI",
        "type":             "Offshore deepwater",
        "statut":           "Production",
        "profondeur_eau_m": 1200,
        "date_debut":       "2023-01-01",
        "bloc":             "CI-101",
        "lat_centre":       4.852,
        "lon_centre":       -3.987,
        "production_peak_bbl": 17000,
        "reserves_MMbbl":   2500,
        "description":      "Plus grande découverte CI - 2021. ENI opérateur."
    },
    "Sankofa": {
        "operateur":        "TotalEnergies / ENI / PETROCI",
        "type":             "Offshore",
        "statut":           "Production",
        "profondeur_eau_m": 1500,
        "date_debut":       "2017-05-01",
        "bloc":             "CI-202",
        "lat_centre":       4.120,
        "lon_centre":       -3.456,
        "production_peak_bbl": 35000,
        "reserves_MMbbl":   246,
        "description":      "Sankofa-Gohene. Gaz et condensats + huile."
    },
    "Foxtrot": {
        "operateur":        "TotalEnergies / PETROCI",
        "type":             "Offshore",
        "statut":           "Declin avance",
        "profondeur_eau_m": 600,
        "date_debut":       "1999-01-01",
        "bloc":             "CI-27",
        "lat_centre":       3.890,
        "lon_centre":       -3.234,
        "production_peak_bbl": 12000,
        "reserves_MMbbl":   39,
        "description":      "Champ mature. Production en declin accelere."
    },
    "Baobab": {
        "operateur":        "CNR International / PETROCI",
        "type":             "Offshore",
        "statut":           "Declin",
        "profondeur_eau_m": 1000,
        "date_debut":       "2005-06-01",
        "bloc":             "CI-40",
        "lat_centre":       4.350,
        "lon_centre":       -3.678,
        "production_peak_bbl": 45000,
        "reserves_MMbbl":   200,
        "description":      "Champ mature. Récupération assistée en cours."
    },
    "Lion": {
        "operateur":        "TotalEnergies / PETROCI",
        "type":             "Offshore",
        "statut":           "Declin avance",
        "profondeur_eau_m": 450,
        "date_debut":       "1994-01-01",
        "bloc":             "CI-11",
        "lat_centre":       4.050,
        "lon_centre":       -3.350,
        "production_peak_bbl": 8000,
        "reserves_MMbbl":   20,
        "description":      "Champ historique. En fin de vie economique."
    },
    "Panthere": {
        "operateur":        "TotalEnergies / PETROCI",
        "type":             "Offshore",
        "statut":           "Declin avance",
        "profondeur_eau_m": 500,
        "date_debut":       "1995-01-01",
        "bloc":             "CI-11",
        "lat_centre":       4.070,
        "lon_centre":       -3.370,
        "production_peak_bbl": 5000,
        "reserves_MMbbl":   15,
        "description":      "Satellite du champ Lion."
    },
}

# ─────────────────────────────────────────────────────
# BLOCS EN EXPLORATION / APPRAISAL
# ─────────────────────────────────────────────────────
BLOCS_EXPLORATION = {
    "CI-101 Deep": {
        "operateur":    "ENI / PETROCI",
        "statut":       "Appraisal",
        "phase":        "Evaluation",
        "lat":          4.900,
        "lon":          -4.100,
        "potentiel":    "1.5+ Milliards bbl",
        "description":  "Extension profonde du Baleine. Très prometteur."
    },
    "CI-205": {
        "operateur":    "ENI / PETROCI",
        "statut":       "Exploration",
        "phase":        "Sismique 3D",
        "lat":          4.650,
        "lon":          -4.350,
        "potentiel":    "TBD",
        "description":  "Bloc adjacent au Baleine. Sismique en cours."
    },
    "CI-401": {
        "operateur":    "TotalEnergies / PETROCI",
        "statut":       "Exploration",
        "phase":        "Forage exploratoire",
        "lat":          3.800,
        "lon":          -4.200,
        "potentiel":    "500+ MMbbl",
        "description":  "Forages exploratoires planifiés 2025-2026."
    },
    "CI-602": {
        "operateur":    "PETROCI",
        "statut":       "Exploration",
        "phase":        "Sismique 2D",
        "lat":          3.500,
        "lon":          -3.800,
        "potentiel":    "TBD",
        "description":  "Bloc opéré par PETROCI. Données sismiques en cours."
    },
    "CI-706": {
        "operateur":    "Vittol / PETROCI",
        "statut":       "Exploration",
        "phase":        "Etude technique",
        "lat":          5.100,
        "lon":          -3.500,
        "potentiel":    "TBD",
        "description":  "Nouveau bloc attribué. Etudes préliminaires."
    },
    "CI-803": {
        "operateur":    "PETROCI / Partenaires TBD",
        "statut":       "Exploration",
        "phase":        "Licencement",
        "lat":          5.300,
        "lon":          -3.200,
        "potentiel":    "TBD",
        "description":  "Nouveau bloc frontier. Appel d'offres en cours."
    },
}

# ─────────────────────────────────────────────────────
# PROFILS PUITS — Productions proches réalité
# ─────────────────────────────────────────────────────
PROFILS_PUITS = {
    # BALEINE — Production depuis 2023
    "Baleine-A": {
        "prod_base": 6500, "declin": 0.003,
        "wc_base": 0.18,  "pression_base": 580,
        "champ": "Baleine", "lat": 4.848, "lon": -3.983,
        "type": "Producteur", "profondeur_m": 3800
    },
    "Baleine-B": {
        "prod_base": 5800, "declin": 0.003,
        "wc_base": 0.22,  "pression_base": 560,
        "champ": "Baleine", "lat": 4.852, "lon": -3.987,
        "type": "Producteur", "profondeur_m": 3750
    },
    "Baleine-C": {
        "prod_base": 4700, "declin": 0.004,
        "wc_base": 0.25,  "pression_base": 545,
        "champ": "Baleine", "lat": 4.855, "lon": -3.991,
        "type": "Producteur", "profondeur_m": 3820
    },
    # SANKOFA — En production depuis 2017
    "Sankofa-1": {
        "prod_base": 8500, "declin": 0.006,
        "wc_base": 0.32,  "pression_base": 420,
        "champ": "Sankofa", "lat": 4.115, "lon": -3.451,
        "type": "Producteur", "profondeur_m": 2900
    },
    "Sankofa-2": {
        "prod_base": 7800, "declin": 0.006,
        "wc_base": 0.35,  "pression_base": 410,
        "champ": "Sankofa", "lat": 4.120, "lon": -3.456,
        "type": "Producteur", "profondeur_m": 2850
    },
    "Sankofa-3": {
        "prod_base": 6200, "declin": 0.007,
        "wc_base": 0.38,  "pression_base": 395,
        "champ": "Sankofa", "lat": 4.125, "lon": -3.461,
        "type": "Producteur", "profondeur_m": 2920
    },
    "Sankofa-GAS": {
        "prod_base": 0, "declin": 0.002,
        "wc_base": 0.05,  "pression_base": 380,
        "champ": "Sankofa", "lat": 4.118, "lon": -3.448,
        "type": "Producteur gaz", "profondeur_m": 2800
    },
    # FOXTROT — En déclin depuis 2010
    "Foxtrot-1": {
        "prod_base": 1800, "declin": 0.015,
        "wc_base": 0.62,  "pression_base": 185,
        "champ": "Foxtrot", "lat": 3.888, "lon": -3.232,
        "type": "Producteur", "profondeur_m": 2100
    },
    "Foxtrot-2": {
        "prod_base": 1200, "declin": 0.018,
        "wc_base": 0.72,  "pression_base": 165,
        "champ": "Foxtrot", "lat": 3.893, "lon": -3.237,
        "type": "Producteur", "profondeur_m": 2050
    },
    # BAOBAB — En déclin depuis 2012
    "Baobab-1": {
        "prod_base": 3200, "declin": 0.009,
        "wc_base": 0.48,  "pression_base": 265,
        "champ": "Baobab", "lat": 4.348, "lon": -3.675,
        "type": "Producteur", "profondeur_m": 2600
    },
    "Baobab-2": {
        "prod_base": 2800, "declin": 0.010,
        "wc_base": 0.52,  "pression_base": 255,
        "champ": "Baobab", "lat": 4.352, "lon": -3.680,
        "type": "Producteur", "profondeur_m": 2650
    },
    "Baobab-3W": {
        "prod_base": 1500, "declin": 0.012,
        "wc_base": 0.58,  "pression_base": 240,
        "champ": "Baobab", "lat": 4.355, "lon": -3.683,
        "type": "Producteur", "profondeur_m": 2580
    },
    # LION — En fin de vie
    "Lion-1": {
        "prod_base": 800, "declin": 0.020,
        "wc_base": 0.78,  "pression_base": 145,
        "champ": "Lion", "lat": 4.048, "lon": -3.348,
        "type": "Producteur", "profondeur_m": 1800
    },
    # PANTHERE — En fin de vie
    "Panthere-1": {
        "prod_base": 500, "declin": 0.022,
        "wc_base": 0.82,  "pression_base": 130,
        "champ": "Panthere", "lat": 4.068, "lon": -3.368,
        "type": "Producteur", "profondeur_m": 1750
    },
}

# ─────────────────────────────────────────────────────
# BENCHMARKS INDUSTRIE O&G — Côte d'Ivoire
# Sources : SPE, IHS Markit, rapports PETROCI publics
# ─────────────────────────────────────────────────────
BENCHMARKS = {
    "water_cut_moyen_ci":     0.42,   # 42% moyen CI
    "water_cut_alerte":       0.55,   # Seuil alerte
    "water_cut_critique":     0.70,   # Seuil critique
    "declin_annuel_normal":   0.18,   # 18%/an normal offshore CI
    "declin_annuel_rapide":   0.30,   # 30%/an = déclin rapide
    "uptime_cible":           0.95,   # 95% temps fonctionnement
    "gor_normal_min":         400,    # scf/stb
    "gor_normal_max":         1500,   # scf/stb
    "pression_min_ops":       150,    # psi min opérationnel
    "production_min_viable":  500,    # bbl/j min économique
    "cout_prod_offshore_ci":  18.5,   # USD/bbl coût de production
}

# ─────────────────────────────────────────────────────
# SEUILS D'ALERTE
# ─────────────────────────────────────────────────────
SEUILS = {
    "water_cut_alerte":   BENCHMARKS["water_cut_alerte"],
    "water_cut_critique": BENCHMARKS["water_cut_critique"],
    "production_min_bbl": BENCHMARKS["production_min_viable"],
    "pression_min_psi":   BENCHMARKS["pression_min_ops"],
    "declin_mensuel_max": BENCHMARKS["declin_annuel_rapide"] / 12,
}

CHAMPS    = CHAMPS_PRODUCTION
PRIX_BARIL = PRIX_BARIL
TAUX      = TAUX_USD_XOF
