"""
PETRO AFRICA — Configuration Centrale
Mise à jour : ajout PRIX_GAZ_MMSCFD + constantes gaz Afrique de l'Ouest
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Supabase ────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# ─── Application ─────────────────────────────────────────────────────────────
APP_NAME    = "PETRO AFRICA"
APP_VERSION = "2.1.0"
APP_LOGO    = "🛢️"

# ─── Unités par défaut ───────────────────────────────────────────────────────
UNITE_DEBIT    = "BOPD"    # Barils par jour
UNITE_GPI      = "MMscfd"  # Millions de pieds cubes par jour
UNITE_PRESSION = "psi"
UNITE_TEMP     = "°C"

# ─── PRIX & RÉFÉRENCES MARCHÉ ────────────────────────────────────────────────

# Huile — référence Brent/Dated
PRIX_BARIL = 75.0          # USD/bbl  (Brent spot, mise à jour manuelle recommandée)

# Gaz — référence Afrique de l'Ouest
# Sources : NLNG (Nigeria), GTA (Sénégal/Mauritanie), Foxtrot/Sankofa (CI)
# Fourchette typique : 3.5–6.0 USD/MMBtu selon contrat et destination
PRIX_GAZ_MMBTU    = 4.5    # USD/MMBtu  ← NOUVEAU — tarif moyen contrats AOG
PRIX_GAZ_MMSCFD   = 4.5    # Alias explicite pour la facturation par MMscfd/j
                             # (1 MMscfd ≈ 1 000 MMBtu/j en conditions standard)

# Conversion énergétique gaz → BOE
# 1 BOE ≈ 5.8 MMBtu  (API/SPE standard)
GAZ_MMBTU_PAR_BOE = 5.8

# Condensat (si champ gaz à condensat)
PRIX_CONDENSAT = 72.0       # USD/bbl  (rabais ~3–5 $/bbl vs Brent)

# ─── PARAMÈTRES FISCAUX CÔTE D'IVOIRE (Code Pétrolier 1996, amendé 2012) ───
ROYALTIES_HUILE_PCT = 12.5  # % sur revenus bruts huile
ROYALTIES_GAZ_PCT   = 8.0   # % sur revenus bruts gaz
IMPOT_SOCIETES_PCT  = 30.0  # % (taux standard Côte d'Ivoire)
PROFIT_OIL_SPLIT    = 0.60  # Part état sur profit oil (contrat de partage type)

# ─── PARAMÈTRES PRODUCTION ───────────────────────────────────────────────────
DECLINE_RATE_DEFAULT = 10.0   # % annuel (déclin exponentiel)
WATER_CUT_DEFAULT    = 0.20   # fraction (20%)
GOR_DEFAULT          = 500.0  # scf/bbl (Gas-Oil Ratio)

# ─── ESG / FLARING ───────────────────────────────────────────────────────────
# Facteurs d'émission IPCC/GIE
CO2_PAR_TONNE_GAZ_TORCHE  = 2.75   # tCO2/t gaz brûlé
GAZ_DENSITÉ_KG_M3          = 0.75   # kg/m³ (gaz naturel moyen)
METHANE_GWP100             = 28.0   # Global Warming Potential CH4 (GIEC AR6)
FLARING_FRACTION_DEFAULT   = 0.05   # 5% de la production gaz torchée (benchmark CI)

# Réglementation PETROCI : objectif zéro torchage systématique d'ici 2030
PETROCI_FLARING_TARGET_PCT = 2.0   # % cible max flaring 2030

# ─── TAUX DE CHANGE ─────────────────────────────────────────────────────────
# Utilisé dans analytics.py : rev_xof = rev_usd * TAUX
TAUX = 610.0    # 1 USD = 610 XOF/FCFA (taux BCEAO moyen 2024)

# ─── BENCHMARKS INDUSTRIE — CÔTE D'IVOIRE OFFSHORE ──────────────────────────
# Utilisé dans analytics.py : kpis_journaliers, calculer_declin, analyse_benchmark
BENCHMARKS = {
    "cout_prod_offshore_ci":   12.0,   # USD/bbl — coût opex offshore CI
    "declin_annuel_normal":     0.10,   # 10 %/an — déclin normal
    "declin_annuel_rapide":     0.20,   # 20 %/an — seuil déclin accéléré
    "water_cut_moyen_ci":       0.35,   # 35 % — water cut moyen parc CI
    "uptime_cible":             0.95,   # 95 % — objectif disponibilité puits
    "production_min_viable":  500.0,   # BOPD — seuil rentabilité minimal
}

# ─── WACC / FINANCE ──────────────────────────────────────────────────────────
WACC_DEFAULT    = 12.0   # % (risque pays CI inclus)
WACC_LOW_RISK   = 10.0   # % (opérateur majeur, financement BEI/IFC)
WACC_HIGH_RISK  = 18.0   # % (exploration early-stage)

# ─── PROFILS PUITS ───────────────────────────────────────────────────────────
# Utilisé par database.py → peupler_puits()
# Clés requises : champ, prod_base, wc_base, lat, lon
# Clés optionnelles : type, profondeur_m, gor_base, pression_tete
PROFILS_PUITS = {
    # ── Baleine (ENI / PETROCI — huile, depuis 2023) ──────────────────────
    "Baleine-A": {
        "champ": "Baleine", "type": "Producteur",
        "prod_base": 15000, "wc_base": 0.05,
        "gor_base": 420, "pression_tete": 1800,
        "lat": 4.42, "lon": -4.55, "profondeur_m": 1900,
    },
    "Baleine-B": {
        "champ": "Baleine", "type": "Producteur",
        "prod_base": 12000, "wc_base": 0.08,
        "gor_base": 450, "pression_tete": 1750,
        "lat": 4.40, "lon": -4.57, "profondeur_m": 2050,
    },
    "Baleine-C": {
        "champ": "Baleine", "type": "Producteur",
        "prod_base": 9500, "wc_base": 0.12,
        "gor_base": 480, "pression_tete": 1700,
        "lat": 4.38, "lon": -4.53, "profondeur_m": 2100,
    },
    # ── Sankofa (TotalEnergies / PETROCI — gaz + condensat) ───────────────
    "Sankofa-1": {
        "champ": "Sankofa", "type": "Gazier",
        "prod_base": 3200, "wc_base": 0.02,
        "gor_base": 8500, "pression_tete": 2200,
        "lat": 4.85, "lon": -4.20, "profondeur_m": 3100,
    },
    "Sankofa-2": {
        "champ": "Sankofa", "type": "Gazier",
        "prod_base": 2800, "wc_base": 0.03,
        "gor_base": 8200, "pression_tete": 2150,
        "lat": 4.87, "lon": -4.22, "profondeur_m": 3050,
    },
    "Sankofa-3": {
        "champ": "Sankofa", "type": "Gazier",
        "prod_base": 2500, "wc_base": 0.04,
        "gor_base": 7900, "pression_tete": 2100,
        "lat": 4.83, "lon": -4.18, "profondeur_m": 3200,
    },
    "Sankofa-GAS": {
        "champ": "Sankofa", "type": "Gazier",
        "prod_base": 1800, "wc_base": 0.01,
        "gor_base": 12000, "pression_tete": 2300,
        "lat": 4.89, "lon": -4.25, "profondeur_m": 3400,
    },
    # ── Foxtrot (TotalEnergies / PETROCI — gaz, depuis 1999) ──────────────
    "Foxtrot-1": {
        "champ": "Foxtrot", "type": "Gazier",
        "prod_base": 1500, "wc_base": 0.15,
        "gor_base": 15000, "pression_tete": 1200,
        "lat": 4.10, "lon": -4.80, "profondeur_m": 2800,
    },
    "Foxtrot-2": {
        "champ": "Foxtrot", "type": "Gazier",
        "prod_base": 1200, "wc_base": 0.18,
        "gor_base": 14500, "pression_tete": 1150,
        "lat": 4.12, "lon": -4.82, "profondeur_m": 2750,
    },
    # ── Baobab (CNR International / PETROCI — huile) ──────────────────────
    "Baobab-1": {
        "champ": "Baobab", "type": "Producteur",
        "prod_base": 4200, "wc_base": 0.45,
        "gor_base": 620, "pression_tete": 950,
        "lat": 4.65, "lon": -4.35, "profondeur_m": 1650,
    },
    "Baobab-2": {
        "champ": "Baobab", "type": "Producteur",
        "prod_base": 3800, "wc_base": 0.52,
        "gor_base": 590, "pression_tete": 900,
        "lat": 4.63, "lon": -4.37, "profondeur_m": 1700,
    },
    "Baobab-3W": {
        "champ": "Baobab", "type": "Injecteur",
        "prod_base": 0, "wc_base": 1.0,
        "gor_base": 0, "pression_tete": 2800,
        "lat": 4.67, "lon": -4.33, "profondeur_m": 1600,
    },
    # ── Lion (TotalEnergies / PETROCI — huile légère) ─────────────────────
    "Lion-1": {
        "champ": "Lion", "type": "Producteur",
        "prod_base": 2100, "wc_base": 0.62,
        "gor_base": 750, "pression_tete": 700,
        "lat": 4.30, "lon": -4.10, "profondeur_m": 1450,
    },
    # ── Panthère (TotalEnergies / PETROCI — huile) ────────────────────────
    "Panthere-1": {
        "champ": "Panthere", "type": "Producteur",
        "prod_base": 1800, "wc_base": 0.71,
        "gor_base": 820, "pression_tete": 620,
        "lat": 4.25, "lon": -4.05, "profondeur_m": 1380,
    },
}

# ─── CHAMPS RÉFÉRENCE CÔTE D'IVOIRE ─────────────────────────────────────────
CHAMPS = {
    "Baleine":  {"type": "huile",    "operateur": "ENI/PETROCI", "debut": 2023},
    "Sankofa":  {"type": "gaz",      "operateur": "ENI/PETROCI", "debut": 2017},
    "Foxtrot":  {"type": "gaz",      "operateur": "FOXTROT Int.","debut": 1999},
    "Espoir":   {"type": "huile/gaz","operateur": "CNR Int.",    "debut": 2002},
    "Baobab":   {"type": "huile",    "operateur": "CNR Int.",    "debut": 2005},
}

# ─── ALERTES & SEUILS ────────────────────────────────────────────────────────
SEUIL_ALERTE_WATERCUT   = 0.80   # 80% — seuil critique
SEUIL_ALERTE_GOR        = 2000   # scf/bbl — gas coning potentiel
SEUIL_ALERTE_DECLINE    = 20.0   # %/an — déclin accéléré anormal
SEUIL_FLARING_ALERTE    = 0.10   # 10% — alerte réglementaire

# ─── RAPPORT ─────────────────────────────────────────────────────────────────
RAPPORT_LOGO_PATH   = "assets/logo_petro_africa.png"
RAPPORT_FOOTER      = "PETRO AFRICA Dashboard — Confidentiel"
RAPPORT_AUTEUR      = "PETRO AFRICA Analytics Platform"
EXCEL_COULEUR_HEADER = "1B4F72"   # Bleu pétrole (hex sans #)
EXCEL_COULEUR_ACCENT = "F39C12"   # Or/orange
