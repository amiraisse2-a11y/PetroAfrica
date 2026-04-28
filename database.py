# database.py — PETROCI PRO
# Supabase PostgreSQL (cloud) + SQLite (fallback local)

import sqlite3
import pandas as pd
import streamlit as st
from datetime import date, timedelta
from config import PROFILS_PUITS

DB_PATH = "petroci_pro.db"

# ─────────────────────────────────────────
# DÉTECTION SUPABASE
# ─────────────────────────────────────────
def utiliser_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return bool(url and key and url.startswith("https://"))
    except Exception:
        return False

def get_supabase():
    from supabase import create_client
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"]
    )

# ─────────────────────────────────────────
# INITIALISATION SQLITE
# ─────────────────────────────────────────
def initialiser_sqlite():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c    = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS puits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_puits TEXT UNIQUE NOT NULL,
            champ TEXT, operateur TEXT,
            type_puits TEXT DEFAULT 'Producteur',
            latitude REAL, longitude REAL,
            profondeur_totale_m REAL,
            date_forage TEXT, statut TEXT DEFAULT 'Actif',
            date_creation TEXT DEFAULT (date('now'))
        )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS production_journaliere (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL, puits TEXT, champ TEXT,
            production_huile_bbl REAL DEFAULT 0,
            production_gaz_mmscf REAL DEFAULT 0,
            production_eau_bbl   REAL DEFAULT 0,
            water_cut REAL DEFAULT 0,
            gor REAL DEFAULT 0,
            pression_tete_psi REAL DEFAULT 0,
            temperature_f REAL DEFAULT 0,
            heures_production REAL DEFAULT 24,
            statut TEXT DEFAULT 'Actif',
            saisie_par TEXT DEFAULT 'Systeme'
        )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS alertes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_alerte TEXT DEFAULT (datetime('now')),
            puits TEXT, champ TEXT,
            type_alerte TEXT, niveau TEXT,
            valeur_actuelle REAL, seuil REAL,
            message TEXT, resolue INTEGER DEFAULT 0
        )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS drilling_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            puits TEXT, bloc TEXT,
            profondeur_actuelle_m REAL DEFAULT 0,
            profondeur_cible_m REAL DEFAULT 0,
            rop_m_heure REAL DEFAULT 0,
            type_operation TEXT,
            phase TEXT,
            boue_type TEXT,
            commentaire TEXT,
            operateur TEXT
        )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_action TEXT DEFAULT (datetime('now')),
            email TEXT, action TEXT, details TEXT
        )""")

    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# PEUPLER PUITS
# ─────────────────────────────────────────
def peupler_puits():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c    = conn.cursor()

    operateurs = {
        "Baleine": "ENI / PETROCI",
        "Sankofa": "TotalEnergies / PETROCI",
        "Foxtrot": "TotalEnergies / PETROCI",
        "Baobab":  "CNR International / PETROCI",
        "Lion":    "TotalEnergies / PETROCI",
        "Panthere":"TotalEnergies / PETROCI",
    }

    dates_forage = {
        "Baleine-A":   "2022-03-15",
        "Baleine-B":   "2022-07-20",
        "Baleine-C":   "2023-01-10",
        "Sankofa-1":   "2016-04-12",
        "Sankofa-2":   "2016-09-08",
        "Sankofa-3":   "2017-02-22",
        "Sankofa-GAS": "2017-06-15",
        "Foxtrot-1":   "1997-08-10",
        "Foxtrot-2":   "1998-03-25",
        "Baobab-1":    "2004-05-18",
        "Baobab-2":    "2004-11-30",
        "Baobab-3W":   "2006-07-14",
        "Lion-1":      "1993-02-08",
        "Panthere-1":  "1994-06-20",
    }

    for nom, p in PROFILS_PUITS.items():
        wc    = p["wc_base"]
        prod  = p["prod_base"]
        statut = ("Critique" if wc > 0.70 else
                  "Alerte"   if wc > 0.55 else
                  "Fin de vie" if prod < 800 else "Actif")
        c.execute("""
            INSERT OR IGNORE INTO puits
            (nom_puits, champ, operateur, type_puits,
             latitude, longitude, profondeur_totale_m,
             date_forage, statut)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            nom, p["champ"],
            operateurs.get(p["champ"], "PETROCI"),
            p.get("type", "Producteur"),
            p["lat"], p["lon"],
            p.get("profondeur_m", 0),
            dates_forage.get(nom, ""),
            statut
        ))

    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# LECTURE PUITS
# ─────────────────────────────────────────
def lire_puits(champ=None, statut=None):
    try:
        if utiliser_supabase():
            sb = get_supabase()
            q  = sb.table("puits").select("*")
            if champ:  q = q.eq("champ", champ)
            if statut: q = q.eq("statut", statut)
            data = q.execute().data
            return pd.DataFrame(data) if data else pd.DataFrame()
        else:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            sql  = "SELECT * FROM puits WHERE 1=1"
            if champ:  sql += f" AND champ='{champ}'"
            if statut: sql += f" AND statut='{statut}'"
            sql += " ORDER BY champ, nom_puits"
            df   = pd.read_sql_query(sql, conn)
            conn.close()
            return df
    except Exception as e:
        st.error(f"Erreur lecture puits : {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────
# LECTURE PRODUCTION
# ─────────────────────────────────────────
def lire_production(date_debut=None, date_fin=None,
                    champ=None, puits=None):
    try:
        if utiliser_supabase():
            sb = get_supabase()
            q  = sb.table("production_journaliere").select("*")
            if date_debut: q = q.gte("date", str(date_debut))
            if date_fin:   q = q.lte("date", str(date_fin))
            if champ:      q = q.eq("champ", champ)
            if puits:      q = q.eq("puits", puits)
            data = q.execute().data
            return pd.DataFrame(data) if data else pd.DataFrame()
        else:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            sql  = "SELECT * FROM production_journaliere WHERE 1=1"
            if date_debut: sql += f" AND date>='{date_debut}'"
            if date_fin:   sql += f" AND date<='{date_fin}'"
            if champ:      sql += f" AND champ='{champ}'"
            if puits:      sql += f" AND puits='{puits}'"
            sql += " ORDER BY date DESC"
            df   = pd.read_sql_query(sql, conn)
            conn.close()
            return df
    except Exception as e:
        st.error(f"Erreur lecture production : {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────
# LECTURE ALERTES
# ─────────────────────────────────────────
def lire_alertes(resolues=False):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        df   = pd.read_sql_query(
            f"SELECT * FROM alertes WHERE resolue={1 if resolues else 0} "
            "ORDER BY date_alerte DESC LIMIT 100", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# ─────────────────────────────────────────
# SAUVEGARDER ALERTE
# ─────────────────────────────────────────
def sauvegarder_alerte(puits, champ, type_alerte,
                        niveau, valeur, seuil, message):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.cursor().execute("""
            INSERT INTO alertes
            (puits,champ,type_alerte,niveau,
             valeur_actuelle,seuil,message)
            VALUES (?,?,?,?,?,?,?)
        """, (puits, champ, type_alerte, niveau,
              valeur, seuil, message))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Erreur sauvegarde alerte : {e}")

# ─────────────────────────────────────────
# LECTURE DRILLING
# ─────────────────────────────────────────
def lire_drilling(bloc=None, puits=None):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        sql  = "SELECT * FROM drilling_log WHERE 1=1"
        if bloc:  sql += f" AND bloc='{bloc}'"
        if puits: sql += f" AND puits='{puits}'"
        sql += " ORDER BY date DESC LIMIT 200"
        df   = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# ─────────────────────────────────────────
# SAUVEGARDER MESURE PRODUCTION
# ─────────────────────────────────────────
def sauvegarder_production(date_s, puits, champ,
                            prod_huile, prod_gaz, prod_eau,
                            wc, gor, pression, temperature,
                            heures, statut, saisie_par="Systeme"):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.cursor().execute("""
            INSERT OR REPLACE INTO production_journaliere
            (date,puits,champ,
             production_huile_bbl,production_gaz_mmscf,
             production_eau_bbl,water_cut,gor,
             pression_tete_psi,temperature_f,
             heures_production,statut,saisie_par)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (str(date_s), puits, champ,
              round(prod_huile,0), round(prod_gaz,3),
              round(prod_eau,0), round(wc,4),
              round(gor,0), round(pression,1),
              round(temperature,1), heures, statut, saisie_par))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde : {e}")
        return False
