# alerts.py — PETROCI PRO
# Alertes automatiques + Email via Gmail SMTP

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, timedelta
import streamlit as st
from database import lire_production, sauvegarder_alerte, lire_alertes
from config import SEUILS, BENCHMARKS, TAUX  # ← TAUX ajouté ici

# ─────────────────────────────────────────
# VÉRIFIER TOUTES LES ALERTES
# ─────────────────────────────────────────
def verifier_alertes():
    hier = str(date.today() - timedelta(days=1))
    df   = lire_production(date_debut=hier, date_fin=hier)
    if df.empty:
        return []

    alertes = []

    for _, row in df.iterrows():
        puits = str(row["puits"])
        champ = str(row["champ"])
        wc    = float(row.get("water_cut", 0))
        prod  = float(row.get("production_huile_bbl", 0))
        press = float(row.get("pression_tete_psi", 0))
        heure = float(row.get("heures_production", 24))

        # Water cut critique
        if wc > SEUILS["water_cut_critique"]:
            msg = (f"Water cut {wc:.1%} depasse le seuil critique "
                   f"{SEUILS['water_cut_critique']:.0%}")
            sauvegarder_alerte(puits, champ, "Water Cut Critique",
                               "CRITIQUE", wc,
                               SEUILS["water_cut_critique"], msg)
            alertes.append({"puits":puits,"niveau":"CRITIQUE","msg":msg})

        elif wc > SEUILS["water_cut_alerte"]:
            msg = (f"Water cut {wc:.1%} depasse le seuil alerte "
                   f"{SEUILS['water_cut_alerte']:.0%}")
            sauvegarder_alerte(puits, champ, "Water Cut Eleve",
                               "ALERTE", wc,
                               SEUILS["water_cut_alerte"], msg)
            alertes.append({"puits":puits,"niveau":"ALERTE","msg":msg})

        # Production faible
        if 0 < prod < SEUILS["production_min_bbl"]:
            msg = (f"Production {prod:,.0f} bbl/j sous le minimum "
                   f"economique {SEUILS['production_min_bbl']:,} bbl/j")
            sauvegarder_alerte(puits, champ, "Production Faible",
                               "ALERTE", prod,
                               SEUILS["production_min_bbl"], msg)
            alertes.append({"puits":puits,"niveau":"ALERTE","msg":msg})

        # Pression basse
        if press < SEUILS["pression_min_psi"] and press > 0:
            msg = (f"Pression tete {press:.0f} psi sous le minimum "
                   f"operationnel {SEUILS['pression_min_psi']} psi")
            sauvegarder_alerte(puits, champ, "Pression Basse",
                               "CRITIQUE", press,
                               SEUILS["pression_min_psi"], msg)
            alertes.append({"puits":puits,"niveau":"CRITIQUE","msg":msg})

        # Arrêt non planifié
        if heure == 0 and prod == 0:
            msg = f"Puits {puits} en arret - 0 heures de production"
            sauvegarder_alerte(puits, champ, "Arret Non Planifie",
                               "ALERTE", 0, 24, msg)
            alertes.append({"puits":puits,"niveau":"ALERTE","msg":msg})

    return alertes

def resume_alertes():
    df = lire_alertes(resolues=False)
    if df.empty:
        return {"total": 0, "critiques": 0, "alertes": 0}
    return {
        "total":    len(df),
        "critiques":int((df["niveau"]=="CRITIQUE").sum()),
        "alertes":  int((df["niveau"]=="ALERTE").sum()),
    }

# ─────────────────────────────────────────
# ENVOI EMAIL GMAIL SMTP
# ─────────────────────────────────────────
def envoyer_email_alerte(alertes_liste, destinataires=None):
    """
    Envoie un email d'alerte via Gmail SMTP
    Config dans Streamlit secrets :
    [email]
    gmail_user = "votre@gmail.com"
    gmail_pass = "app_password"
    destinataires = "ing1@petroci.ci,ing2@petroci.ci"
    """
    try:
        gmail_user = st.secrets["email"]["gmail_user"]
        gmail_pass = st.secrets["email"]["gmail_pass"]
        dest_str   = st.secrets["email"].get("destinataires", gmail_user)
        destinataires = [d.strip() for d in dest_str.split(",")]
    except Exception:
        return False, "Configuration email non trouvee dans secrets"

    if not alertes_liste:
        return False, "Aucune alerte a envoyer"

    critiques = [a for a in alertes_liste if a.get("niveau")=="CRITIQUE"]
    normales  = [a for a in alertes_liste if a.get("niveau")=="ALERTE"]

    sujet = (f"[PETROCI] {len(critiques)} CRITIQUE(S) + "
             f"{len(normales)} ALERTE(S) - {date.today()}")

    corps_html = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:600px;">
    <div style="background:#E07B00;padding:20px;border-radius:8px 8px 0 0;">
        <h2 style="color:white;margin:0;">🛢️ PETROCI PRO — Rapport d'Alertes</h2>
        <p style="color:rgba(255,255,255,0.8);margin:4px 0 0 0;">
            {date.today().strftime('%d/%m/%Y')}
        </p>
    </div>
    <div style="background:#f9f9f9;padding:20px;border:1px solid #ddd;">
        <p>
            <b>{len(alertes_liste)} alerte(s)</b> detectee(s) sur vos puits :
            <b style="color:#CC0000;">{len(critiques)} critique(s)</b>
            et <b style="color:#CC7700;">{len(normales)} alerte(s)</b>
        </p>
    """

    for a in critiques:
        corps_html += f"""
        <div style="background:#FFF0F0;border-left:4px solid #CC0000;
                    padding:10px 14px;margin:8px 0;border-radius:0 6px 6px 0;">
            <b style="color:#CC0000;">CRITIQUE</b> — {a['puits']}<br>
            <span style="color:#666;">{a['msg']}</span>
        </div>"""

    for a in normales:
        corps_html += f"""
        <div style="background:#FFFBF0;border-left:4px solid #CC7700;
                    padding:10px 14px;margin:8px 0;border-radius:0 6px 6px 0;">
            <b style="color:#CC7700;">ALERTE</b> — {a['puits']}<br>
            <span style="color:#666;">{a['msg']}</span>
        </div>"""

    corps_html += """
        <p style="margin-top:20px;color:#888;font-size:0.85rem;">
            Consultez le dashboard : <a href="https://petrol-system.streamlit.app">
            petrol-system.streamlit.app</a>
        </p>
    </div>
    <div style="background:#1A1A2E;padding:12px;border-radius:0 0 8px 8px;
                text-align:center;color:#666;font-size:0.75rem;">
        PETROCI PRO © 2026 — Systeme de Gestion de Production
    </div>
    </body></html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = sujet
        msg["From"]    = gmail_user
        msg["To"]      = ", ".join(destinataires)
        msg.attach(MIMEText(corps_html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, destinataires, msg.as_string())

        return True, f"Email envoye a {', '.join(destinataires)}"
    except Exception as e:
        return False, f"Erreur envoi email : {e}"

def envoyer_rapport_quotidien(df_kpis, rapport_champ):
    """Envoie un rapport PDF quotidien par email"""
    try:
        gmail_user = st.secrets["email"]["gmail_user"]
        gmail_pass = st.secrets["email"]["gmail_pass"]
        dest_str   = st.secrets["email"].get("destinataires", gmail_user)
        destinataires = [d.strip() for d in dest_str.split(",")]
    except Exception:
        return False, "Config email manquante"

    prod = df_kpis.get("production_totale_bbl", 0)
    rev  = df_kpis.get("revenu_journalier_usd", 0)

    corps_html = f"""
    <html><body style="font-family:Arial;max-width:600px;">
    <div style="background:#E07B00;padding:20px;border-radius:8px 8px 0 0;">
        <h2 style="color:white;margin:0;">PETROCI PRO — Rapport Journalier</h2>
        <p style="color:rgba(255,255,255,0.8);">
            {date.today().strftime('%d/%m/%Y')}
        </p>
    </div>
    <div style="background:#f9f9f9;padding:20px;border:1px solid #ddd;">
        <table style="width:100%;border-collapse:collapse;">
            <tr style="background:#E07B00;color:white;">
                <th style="padding:10px;text-align:left;">Indicateur</th>
                <th style="padding:10px;text-align:right;">Valeur</th>
            </tr>
            <tr><td style="padding:8px;">Production totale</td>
                <td style="padding:8px;text-align:right;">
                    <b>{prod:,.0f} bbl/jour</b></td></tr>
            <tr style="background:#f0f0f0;">
                <td style="padding:8px;">Revenu journalier</td>
                <td style="padding:8px;text-align:right;">
                    <b>${rev:,.0f} USD</b></td></tr>
            <tr><td style="padding:8px;">En FCFA</td>
                <td style="padding:8px;text-align:right;">
                    <b>{rev*TAUX/1e6:.1f}M FCFA</b></td></tr>
            <tr style="background:#f0f0f0;">
                <td style="padding:8px;">Puits actifs</td>
                <td style="padding:8px;text-align:right;">
                    <b>{df_kpis.get('nb_puits_actifs',0)}</b></td></tr>
            <tr><td style="padding:8px;">Alertes actives</td>
                <td style="padding:8px;text-align:right;color:#CC7700;">
                    <b>{df_kpis.get('nb_puits_alerte',0)}</b></td></tr>
        </table>
    </div>
    </body></html>
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[PETROCI] Rapport Journalier — {date.today()}"
        msg["From"]    = gmail_user
        msg["To"]      = ", ".join(destinataires)
        msg.attach(MIMEText(corps_html, "html", "utf-8"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, destinataires, msg.as_string())
        return True, "Rapport envoye"
    except Exception as e:
        return False, str(e)
