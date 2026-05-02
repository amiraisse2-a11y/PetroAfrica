# gsheets_connector.py — PETRO AFRICA v2.3
# Connexion Google Sheets comme source de données réelles
# Compatible avec partage opérateur (ENI, PETROCI, TotalEnergies)

import streamlit as st
import pandas as pd
from datetime import date, datetime

# ─────────────────────────────────────────
# FORMAT ATTENDU DU GOOGLE SHEET
# ─────────────────────────────────────────
# Feuille "Production" — colonnes obligatoires :
#   date | puits | champ | production_huile_bbl | production_gaz_mmscf
#   production_eau_bbl | water_cut | gor | pression_tete_psi | heures_production
#
# Feuille "Puits" — colonnes obligatoires :
#   nom_puits | champ | operateur | type_puits | statut | latitude | longitude
#
# Feuille "Alertes" (optionnelle) :
#   date_alerte | puits | champ | type_alerte | niveau | message

# ─────────────────────────────────────────
# CONNEXION GOOGLE SHEETS
# ─────────────────────────────────────────
def _get_gsheet_client():
    """
    Authentification via compte de service Google.
    Configurer dans Streamlit secrets :

    [gcp_service_account]
    type = "service_account"
    project_id = "votre-projet"
    private_key_id = "..."
    private_key = "-----BEGIN RSA PRIVATE KEY-----\n..."
    client_email = "petro-africa@votre-projet.iam.gserviceaccount.com"
    client_id = "..."
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://oauth2.googleapis.com/token"
    """
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes,
    )
    return gspread.authorize(creds)

def gsheets_disponible() -> bool:
    """Vérifie si la config Google Sheets est présente."""
    try:
        _ = st.secrets["gcp_service_account"]["client_email"]
        _ = st.secrets["gsheets"]["spreadsheet_id"]
        return True
    except Exception:
        return False

def _get_spreadsheet():
    """Ouvre le Google Sheet principal."""
    client = _get_gsheet_client()
    sheet_id = st.secrets["gsheets"]["spreadsheet_id"]
    return client.open_by_key(sheet_id)

# ─────────────────────────────────────────
# LECTURE PRODUCTION DEPUIS GOOGLE SHEETS
# ─────────────────────────────────────────
@st.cache_data(ttl=300)  # Cache 5 minutes — données fraîches toutes les 5 min
def lire_production_gsheets(
    date_debut=None,
    date_fin=None,
    champ=None,
    puits=None,
) -> pd.DataFrame:
    """
    Lit la feuille 'Production' du Google Sheet.
    Cache de 5 minutes pour éviter les appels API répétitifs.
    """
    try:
        wb      = _get_spreadsheet()
        ws      = wb.worksheet("Production")
        records = ws.get_all_records()
        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        # Normalisation colonnes
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # Conversion types
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

        cols_num = [
            "production_huile_bbl", "production_gaz_mmscf",
            "production_eau_bbl", "water_cut", "gor",
            "pression_tete_psi", "heures_production",
        ]
        for col in cols_num:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Filtres
        if date_debut and "date" in df.columns:
            df = df[df["date"] >= date_debut]
        if date_fin and "date" in df.columns:
            df = df[df["date"] <= date_fin]
        if champ and "champ" in df.columns:
            df = df[df["champ"] == champ]
        if puits and "puits" in df.columns:
            df = df[df["puits"] == puits]

        return df.sort_values("date", ascending=False) if "date" in df.columns else df

    except Exception as e:
        st.warning(f"Google Sheets indisponible : {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────
# LECTURE PUITS DEPUIS GOOGLE SHEETS
# ─────────────────────────────────────────
@st.cache_data(ttl=600)  # Cache 10 minutes
def lire_puits_gsheets(champ=None) -> pd.DataFrame:
    """Lit la feuille 'Puits' du Google Sheet."""
    try:
        wb      = _get_spreadsheet()
        ws      = wb.worksheet("Puits")
        records = ws.get_all_records()
        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        if champ and "champ" in df.columns:
            df = df[df["champ"] == champ]

        return df

    except Exception as e:
        st.warning(f"Erreur lecture puits GSheets : {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────
# ÉCRITURE — SAUVEGARDER SAISIE OPÉRATEUR
# ─────────────────────────────────────────
def sauvegarder_production_gsheets(
    date_s, puits, champ,
    prod_huile, prod_gaz, prod_eau,
    wc, gor, pression, temperature,
    heures, statut, saisie_par="Operateur"
) -> bool:
    """
    Ajoute une ligne de production dans la feuille 'Production'.
    Utilisé par la page Saisie des Données.
    """
    try:
        wb  = _get_spreadsheet()
        ws  = wb.worksheet("Production")
        row = [
            str(date_s), puits, champ,
            round(prod_huile, 0), round(prod_gaz, 3),
            round(prod_eau, 0), round(wc, 4),
            round(gor, 0), round(pression, 1),
            round(temperature, 1), heures, statut,
            saisie_par,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ]
        ws.append_row(row, value_input_option="USER_ENTERED")
        # Invalider le cache pour que les nouvelles données apparaissent
        lire_production_gsheets.clear()
        return True
    except Exception as e:
        st.error(f"Erreur écriture GSheets : {e}")
        return False

# ─────────────────────────────────────────
# RÉSUMÉ STATUT CONNEXION
# ─────────────────────────────────────────
def statut_gsheets() -> dict:
    """Retourne le statut de la connexion pour affichage dans le dashboard."""
    if not gsheets_disponible():
        return {"connecte": False, "message": "Config manquante dans secrets"}
    try:
        wb    = _get_spreadsheet()
        feuilles = [ws.title for ws in wb.worksheets()]
        return {
            "connecte":  True,
            "feuilles":  feuilles,
            "message":   f"Connecté — {len(feuilles)} feuilles",
            "sheet_id":  st.secrets["gsheets"]["spreadsheet_id"],
        }
    except Exception as e:
        return {"connecte": False, "message": str(e)}

# ─────────────────────────────────────────
# PAGE CONFIGURATION — STREAMLIT
# ─────────────────────────────────────────
def render_gsheets_config():
    """
    Page de configuration Google Sheets affichée dans les Settings.
    Permet de tester la connexion et voir l'état.
    """
    st.markdown("### Connexion Google Sheets — Données Réelles")

    statut = statut_gsheets()

    if statut["connecte"]:
        st.success(f"✅ {statut['message']}")
        st.markdown(f"**Feuilles disponibles :** {', '.join(statut['feuilles'])}")
        st.markdown(f"**Sheet ID :** `{statut['sheet_id']}`")

        if st.button("🔄 Vider le cache (forcer rechargement)"):
            lire_production_gsheets.clear()
            lire_puits_gsheets.clear()
            st.success("Cache vidé — données rechargées au prochain accès")
    else:
        st.error(f"❌ Non connecté : {statut['message']}")
        st.markdown("#### Configuration requise dans Streamlit Secrets :")
        st.code("""
[gsheets]
spreadsheet_id = "1AbCdEfGhIjKlMnOpQrStUvWxYz..."

[gcp_service_account]
type = "service_account"
project_id = "petro-africa"
private_key_id = "xxx"
private_key = \"\"\"-----BEGIN RSA PRIVATE KEY-----
...votre clé privée...
-----END RSA PRIVATE KEY-----\"\"\"
client_email = "petro-africa@petro-africa.iam.gserviceaccount.com"
client_id = "xxx"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
        """, language="toml")

        st.markdown("""
**Étapes pour connecter votre Google Sheet :**

1. Allez sur [console.cloud.google.com](https://console.cloud.google.com)
2. Créez un projet → Activez **Google Sheets API** + **Google Drive API**
3. Créez un **compte de service** → téléchargez le JSON de clé
4. Partagez votre Google Sheet avec l'email du compte de service
5. Copiez le contenu JSON dans les Secrets Streamlit

**Format du Google Sheet Production (colonnes obligatoires) :**
`date | puits | champ | production_huile_bbl | production_gaz_mmscf | production_eau_bbl | water_cut | gor | pression_tete_psi | heures_production | statut`
        """)
