# analytics.py — PETROCI PRO

import pandas as pd
import numpy as np
from datetime import date, timedelta
from database import lire_production, lire_puits
from config import PRIX_BARIL, TAUX, BENCHMARKS

def kpis_journaliers(date_cible=None):
    if not date_cible:
        date_cible = str(date.today() - timedelta(days=1))
    df = lire_production(date_debut=date_cible, date_fin=date_cible)
    if df.empty:
        date_cible = str(date.today() - timedelta(days=2))
        df = lire_production(date_debut=date_cible, date_fin=date_cible)
    if df.empty:
        return {}
    prod        = df["production_huile_bbl"].sum()
    rev_usd     = prod * PRIX_BARIL
    rev_xof     = rev_usd * TAUX
    df_puits    = lire_puits()
    return {
        "date":                  date_cible,
        "production_totale_bbl": round(prod, 0),
        "production_gaz_mmscf":  round(df["production_gaz_mmscf"].sum(), 2),
        "water_cut_moyen":       round(df["water_cut"].mean(), 4),
        "pression_moyenne_psi":  round(df["pression_tete_psi"].mean(), 1),
        "nb_puits_actifs":       int((df_puits["statut"]=="Actif").sum()) if not df_puits.empty else 0,
        "nb_puits_alerte":       int((df_puits["statut"]=="Alerte").sum()) if not df_puits.empty else 0,
        "nb_puits_critiques":    int((df_puits["statut"]=="Critique").sum()) if not df_puits.empty else 0,
        "revenu_journalier_usd": round(rev_usd, 0),
        "revenu_journalier_xof": round(rev_xof, 0),
        "uptime_moyen":          round(df["heures_production"].mean() / 24 * 100, 1),
        "cout_prod_total_usd":   round(prod * BENCHMARKS["cout_prod_offshore_ci"], 0),
        "marge_usd":             round(rev_usd - prod * BENCHMARKS["cout_prod_offshore_ci"], 0),
    }

def production_par_champ(periode_jours=30):
    df = lire_production(
        date_debut=str(date.today() - timedelta(days=periode_jours)),
        date_fin=str(date.today())
    )
    if df.empty:
        return pd.DataFrame()
    rapport = df.groupby("champ").agg(
        Production_Totale  =("production_huile_bbl","sum"),
        Production_Moyenne =("production_huile_bbl","mean"),
        WaterCut_Moyen     =("water_cut","mean"),
        GOR_Moyen          =("gor","mean"),
        Pression_Moyenne   =("pression_tete_psi","mean"),
        Gaz_Total          =("production_gaz_mmscf","sum"),
        Uptime_Moyen       =("heures_production","mean"),
        Nb_Jours           =("date","nunique")
    ).reset_index()
    rapport["Revenu_USD"]   = rapport["Production_Totale"] * PRIX_BARIL
    rapport["Revenu_FCFA"]  = rapport["Revenu_USD"] * TAUX
    rapport["Cout_USD"]     = rapport["Production_Totale"] * BENCHMARKS["cout_prod_offshore_ci"]
    rapport["Marge_USD"]    = rapport["Revenu_USD"] - rapport["Cout_USD"]
    rapport["Uptime_Moyen"] = rapport["Uptime_Moyen"] / 24 * 100
    return rapport.sort_values("Production_Totale", ascending=False)

def calculer_declin(puits_nom, periode_jours=90):
    df = lire_production(
        date_debut=str(date.today() - timedelta(days=periode_jours)),
        date_fin=str(date.today()),
        puits=puits_nom
    )
    if df.empty or len(df) < 7:
        return None
    df = df.sort_values("date")
    # Filtrer les zéros (arrêts)
    df = df[df["production_huile_bbl"] > 0]
    if len(df) < 5:
        return None
    prod_debut = float(df.iloc[0]["production_huile_bbl"])
    prod_fin   = float(df.iloc[-1]["production_huile_bbl"])
    if prod_debut == 0:
        return None
    declin_total   = (prod_debut - prod_fin) / prod_debut
    declin_mensuel = declin_total / max(periode_jours / 30, 1)
    declin_annuel  = declin_mensuel * 12
    # Comparaison benchmark
    bench = BENCHMARKS["declin_annuel_normal"]
    if declin_annuel < bench:
        perf = "Meilleure que le benchmark"
    elif declin_annuel < BENCHMARKS["declin_annuel_rapide"]:
        perf = "Dans la normale"
    else:
        perf = "Déclin rapide - Attention"
    return {
        "puits":               puits_nom,
        "production_debut":    round(prod_debut, 0),
        "production_actuelle": round(prod_fin, 0),
        "declin_total_pct":    round(declin_total * 100, 2),
        "declin_mensuel_pct":  round(declin_mensuel * 100, 2),
        "declin_annuel_pct":   round(declin_annuel * 100, 2),
        "benchmark_annuel_pct":round(bench * 100, 1),
        "performance":         perf,
        "periode_jours":       periode_jours,
    }

def historique_champs(periode_jours=90):
    df = lire_production(
        date_debut=str(date.today() - timedelta(days=periode_jours)),
        date_fin=str(date.today())
    )
    if df.empty:
        return pd.DataFrame()
    return (df.groupby(["date","champ"])
              .agg(
                  production_huile_bbl=("production_huile_bbl","sum"),
                  production_gaz_mmscf=("production_gaz_mmscf","sum"),
                  production_eau_bbl  =("production_eau_bbl","sum"),
                  water_cut           =("water_cut","mean"),
              )
              .reset_index()
              .sort_values("date"))

def analyse_benchmark(df_prod):
    """Compare les performances aux benchmarks industrie CI"""
    if df_prod.empty:
        return {}
    wc_moyen = df_prod["water_cut"].mean()
    return {
        "wc_moyen":          round(wc_moyen, 4),
        "wc_benchmark":      BENCHMARKS["water_cut_moyen_ci"],
        "wc_statut":         ("Meilleur" if wc_moyen < BENCHMARKS["water_cut_moyen_ci"]
                              else "Au-dessus benchmark"),
        "uptime_moyen":      round(df_prod["heures_production"].mean()/24*100, 1),
        "uptime_cible":      BENCHMARKS["uptime_cible"] * 100,
        "nb_puits_rentables":int((df_prod.groupby("puits")["production_huile_bbl"]
                               .mean() > BENCHMARKS["production_min_viable"]).sum()),
    }
