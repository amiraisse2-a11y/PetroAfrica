# ml_forecast.py — PETROCI PRO
# Module de prévision ML : Arps + Prophet + Random Forest

import numpy as np
import pandas as pd
from datetime import date, timedelta
from scipy.optimize import curve_fit

# ─────────────────────────────────────────
# COURBES DE DÉCLIN ARPS (Standard O&G)
# ─────────────────────────────────────────
def declin_exponentiel(t, qi, d):
    """Déclin exponentiel : q(t) = qi * exp(-d*t)"""
    return qi * np.exp(-d * t)

def declin_hyperbolique(t, qi, d, b):
    """Déclin hyperbolique Arps : q(t) = qi/(1+b*d*t)^(1/b)"""
    return qi / (1 + b * d * t) ** (1/b)

def declin_harmonique(t, qi, d):
    """Déclin harmonique : q(t) = qi/(1+d*t)"""
    return qi / (1 + d * t)

def fitter_declin_arps(df_historique):
    """
    Fitte les 3 types de déclin Arps sur les données
    et retourne le meilleur modèle
    """
    df = df_historique.copy()
    df = df[df["production_huile_bbl"] > 0].sort_values("date")

    if len(df) < 10:
        return None

    t = np.arange(len(df))
    q = df["production_huile_bbl"].values

    resultats = {}

    # Essai déclin exponentiel
    try:
        popt, _ = curve_fit(
            declin_exponentiel, t, q,
            p0=[q[0], 0.005],
            bounds=([0, 0], [q[0]*2, 0.1]),
            maxfev=5000
        )
        q_pred = declin_exponentiel(t, *popt)
        r2     = 1 - np.sum((q - q_pred)**2) / np.sum((q - q.mean())**2)
        resultats["exponentiel"] = {
            "params": popt, "r2": r2,
            "qi": popt[0], "d": popt[1], "b": 1.0
        }
    except Exception:
        pass

    # Essai déclin hyperbolique
    try:
        popt, _ = curve_fit(
            declin_hyperbolique, t, q,
            p0=[q[0], 0.005, 0.5],
            bounds=([0, 0, 0.01], [q[0]*2, 0.2, 1.5]),
            maxfev=5000
        )
        q_pred = declin_hyperbolique(t, *popt)
        r2     = 1 - np.sum((q - q_pred)**2) / np.sum((q - q.mean())**2)
        resultats["hyperbolique"] = {
            "params": popt, "r2": r2,
            "qi": popt[0], "d": popt[1], "b": popt[2]
        }
    except Exception:
        pass

    if not resultats:
        return None

    # Meilleur modèle = R² le plus élevé
    meilleur = max(resultats, key=lambda k: resultats[k]["r2"])
    return {
        "type":       meilleur,
        "params":     resultats[meilleur]["params"],
        "r2":         resultats[meilleur]["r2"],
        "qi":         resultats[meilleur]["qi"],
        "d":          resultats[meilleur]["d"],
        "b":          resultats[meilleur]["b"],
        "df_base":    df,
        "t_base":     t,
        "q_base":     q,
    }

def prevoir_production(modele, nb_jours_futur=365,
                       intervalle_confiance=0.90):
    """
    Génère les prévisions de production avec intervalles de confiance
    Retourne un DataFrame avec date, q_prevue, q_low, q_high
    """
    if not modele:
        return pd.DataFrame()

    t_max    = len(modele["t_base"])
    t_futur  = np.arange(t_max, t_max + nb_jours_futur)
    type_dec = modele["type"]
    params   = modele["params"]

    if type_dec == "exponentiel":
        q_futur = declin_exponentiel(t_futur, *params)
    elif type_dec == "hyperbolique":
        q_futur = declin_hyperbolique(t_futur, *params)
    else:
        q_futur = declin_harmonique(t_futur, *params[:2])

    q_futur = np.maximum(q_futur, 0)

    # Intervalle de confiance basé sur R²
    incertitude = 1 - modele["r2"]
    facteur     = 1 + incertitude * 1.5
    z           = 1.645 if intervalle_confiance == 0.90 else 1.96

    q_low  = q_futur * (1 - z * incertitude * facteur)
    q_high = q_futur * (1 + z * incertitude * facteur)
    q_low  = np.maximum(q_low, 0)

    # Dates futures
    date_debut = date.today()
    dates      = [date_debut + timedelta(days=i)
                  for i in range(nb_jours_futur)]

    return pd.DataFrame({
        "date":       [str(d) for d in dates],
        "q_prevue":   np.round(q_futur, 0),
        "q_low":      np.round(q_low, 0),
        "q_high":     np.round(q_high, 0),
        "type_declin":type_dec,
    })

def calculer_eur(modele, prix_baril=78.5,
                 cout_prod=18.5, prod_limite=500):
    """
    EUR = Estimated Ultimate Recovery
    Calcule la production cumulée jusqu'au seuil économique
    """
    if not modele:
        return {}

    t_max   = len(modele["t_base"])
    type_dec = modele["type"]
    params   = modele["params"]

    # Simuler jusqu'à 20 ans
    t_long   = np.arange(0, 365 * 20)
    if type_dec == "exponentiel":
        q_long = declin_exponentiel(t_long, *params)
    elif type_dec == "hyperbolique":
        q_long = declin_hyperbolique(t_long, *params)
    else:
        q_long = declin_harmonique(t_long, *params[:2])

    # Trouver le moment où la prod < seuil économique
    rentable = q_long > prod_limite
    if rentable.any():
        duree_vie_jours = int(np.argmin(rentable))
    else:
        duree_vie_jours = len(t_long)

    # EUR = somme production rentable
    eur_bbl   = float(np.sum(q_long[:duree_vie_jours]))
    revenu    = eur_bbl * prix_baril
    cout      = eur_bbl * cout_prod
    marge_tot = revenu - cout

    return {
        "eur_mmbl":          round(eur_bbl / 1e6, 2),
        "duree_vie_ans":     round(duree_vie_jours / 365, 1),
        "revenu_total_musd": round(revenu / 1e6, 1),
        "cout_total_musd":   round(cout / 1e6, 1),
        "marge_totale_musd": round(marge_tot / 1e6, 1),
        "prod_limite_bbl":   prod_limite,
    }

def forecast_random_forest(df_historique, nb_jours=90):
    """
    Prévision ML avec Random Forest
    Utilise les features : jour, mois, jour_annee, wc, pression
    """
    try:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler

        df = df_historique.copy()
        df = df[df["production_huile_bbl"] > 0].sort_values("date")

        if len(df) < 30:
            return pd.DataFrame()

        df["date_dt"]    = pd.to_datetime(df["date"])
        df["jour"]       = df["date_dt"].dt.dayofyear
        df["mois"]       = df["date_dt"].dt.month
        df["index_time"] = range(len(df))

        features = ["index_time", "jour", "mois"]
        for col in ["water_cut","pression_tete_psi","gor"]:
            if col in df.columns:
                features.append(col)

        X = df[features].fillna(df[features].mean())
        y = df["production_huile_bbl"].values

        scaler = StandardScaler()
        X_sc   = scaler.fit_transform(X)

        rf = RandomForestRegressor(
            n_estimators=100, random_state=42,
            max_depth=8
        )
        rf.fit(X_sc, y)

        # Score R²
        r2 = rf.score(X_sc, y)

        # Générer prévisions futures
        dernier_idx = len(df)
        previsions  = []

        for i in range(nb_jours):
            d_futur = date.today() + timedelta(days=i)
            row     = {
                "index_time": dernier_idx + i,
                "jour":       d_futur.timetuple().tm_yday,
                "mois":       d_futur.month,
            }
            if "water_cut" in features:
                row["water_cut"] = float(df["water_cut"].iloc[-1]) + 0.0002 * i
            if "pression_tete_psi" in features:
                row["pression_tete_psi"] = float(df["pression_tete_psi"].iloc[-1])
            if "gor" in features:
                row["gor"] = float(df["gor"].iloc[-1])

            X_pred = scaler.transform([[row.get(f, 0) for f in features]])
            q_pred = max(0, float(rf.predict(X_pred)[0]))
            previsions.append({
                "date":    str(d_futur),
                "q_rf":    round(q_pred, 0),
                "r2_rf":   round(r2, 3)
            })

        return pd.DataFrame(previsions)

    except Exception:
        return pd.DataFrame()
