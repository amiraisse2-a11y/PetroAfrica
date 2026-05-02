# deepseek_ai.py — PETRO AFRICA v2.1
# Assistant IA — DeepSeek V4 + Upload PDF / CSV / Excel

import streamlit as st
from openai import OpenAI
import pandas as pd
import io

# ════════════════════════════════════════════
# CLIENT DEEPSEEK
# ════════════════════════════════════════════
def get_client():
    return OpenAI(
        api_key=st.secrets["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com"
    )

# ════════════════════════════════════════════
# SYSTEM PROMPT
# ════════════════════════════════════════════
SYSTEM_PROMPT = """Tu es PETRO-AI, assistant expert en ingénierie pétrolière
spécialisé dans les opérations offshore de Côte d'Ivoire et d'Afrique de l'Ouest.

Expertise :
- Production pétrolière (champs Baleine, Sankofa, Foxtrot, Baobab, Lion, Panthère)
- Courbes de déclin Arps, EUR, IRR, NPV
- Contrats PSC — droit pétrolier ivoirien
- ESP, gestion puits, sismique, logs
- ESG, flaring, émissions CO2 offshore
- Réglementation : Code Pétrolier CI, ENI, PETROCI, TotalEnergies

Règles absolues :
- Réponds TOUJOURS en FRANÇAIS
- Sois précis, chiffré, pratique
- Quand on te donne un fichier, analyse-le en détail avec des chiffres
- Adapte au contexte ivoirien et ouest-africain
"""

# ════════════════════════════════════════════
# EXTRACTION CONTENU FICHIER
# ════════════════════════════════════════════
def extraire_pdf(fichier) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(fichier)
        texte = ""
        for i, page in enumerate(reader.pages[:20]):
            texte += f"\n--- PAGE {i+1} ---\n"
            texte += page.extract_text() or ""
        return texte[:15000]
    except Exception as e:
        return f"Erreur lecture PDF : {e}"


def extraire_csv(fichier) -> str:
    try:
        df = pd.read_csv(fichier)
        resume  = f"Fichier CSV — {len(df)} lignes x {len(df.columns)} colonnes\n"
        resume += f"Colonnes : {list(df.columns)}\n\n"
        resume += "Statistiques :\n"
        resume += df.describe().to_string()
        resume += "\n\nApercu (10 premieres lignes) :\n"
        resume += df.head(10).to_string()
        return resume[:12000]
    except Exception as e:
        return f"Erreur lecture CSV : {e}"


def extraire_excel(fichier) -> str:
    try:
        xl = pd.ExcelFile(fichier)
        resume = f"Fichier Excel — Feuilles : {xl.sheet_names}\n\n"
        for sheet in xl.sheet_names[:3]:
            df = xl.parse(sheet)
            resume += f"=== Feuille : {sheet} ===\n"
            resume += f"{len(df)} lignes x {len(df.columns)} colonnes\n"
            resume += f"Colonnes : {list(df.columns)}\n"
            resume += df.head(8).to_string()
            resume += "\n\n"
        return resume[:12000]
    except Exception as e:
        return f"Erreur lecture Excel : {e}"


def traiter_fichier(fichier_upload) -> tuple:
    nom = fichier_upload.name
    ext = nom.split(".")[-1].lower()

    if ext == "pdf":
        contenu = extraire_pdf(fichier_upload)
        type_f  = "PDF"
    elif ext == "csv":
        contenu = extraire_csv(fichier_upload)
        type_f  = "CSV"
    elif ext in ["xlsx", "xls"]:
        contenu = extraire_excel(fichier_upload)
        type_f  = "Excel"
    elif ext in ["txt", "log"]:
        contenu = fichier_upload.read().decode("utf-8", errors="ignore")[:10000]
        type_f  = "Texte"
    else:
        contenu = None
        type_f  = "non supporte"

    return nom, contenu, type_f


# ════════════════════════════════════════════
# APPEL API DEEPSEEK
# ════════════════════════════════════════════
def ask_deepseek(messages_history, modele="deepseek-v4-flash"):
    try:
        client   = get_client()
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += messages_history

        response = client.chat.completions.create(
            model=modele,
            messages=messages,
            max_tokens=4000,
            temperature=0.3,
        )
        return response.choices[0].message.content, None

    except Exception as e:
        return None, str(e)


# ════════════════════════════════════════════
# ANALYSE FORECAST ML
# ════════════════════════════════════════════
def analyser_forecast_ml(modele_arps, df_prevision, champ, puits):
    if not modele_arps or df_prevision.empty:
        return "Donnees insuffisantes."

    q_actuelle  = round(modele_arps.get("qi", 0), 0)
    type_declin = modele_arps.get("type", "inconnu")
    r2          = round(modele_arps.get("r2", 0), 3)
    taux_declin = round(modele_arps.get("d", 0) * 365 * 100, 1)
    q_30j  = round(df_prevision["q_prevue"].iloc[29], 0)  if len(df_prevision) > 29  else "N/A"
    q_90j  = round(df_prevision["q_prevue"].iloc[89], 0)  if len(df_prevision) > 89  else "N/A"
    q_365j = round(df_prevision["q_prevue"].iloc[364], 0) if len(df_prevision) > 364 else "N/A"

    prompt = f"""Analyse ces resultats ML — Puits : {puits} / Champ : {champ}

MODELE ARPS : {type_declin} | Qi : {q_actuelle:,.0f} bbl/j
Taux declin annuel : {taux_declin}% | R2 : {r2}
PREVISIONS : J+30 = {q_30j} | J+90 = {q_90j} | J+365 = {q_365j} bbl/j

Fournis :
1. Interpretation du declin et etat du reservoir
2. Qualite du modele R2
3. Alertes et tendances critiques
4. Recommandations operationnelles concretes
5. Impact financier a 78$/bbl"""

    try:
        client   = get_client()
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur analyse IA : {e}"


# ════════════════════════════════════════════
# PAGE PRINCIPALE — INTERFACE STREAMLIT
# ════════════════════════════════════════════
def render_assistant_ia():

    # Header
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1A1A2E,#16213E,#0F3460);
                border-radius:14px;padding:22px 28px;margin-bottom:20px;
                box-shadow:0 6px 24px rgba(0,0,0,0.4);">
        <div style="color:#00D4FF;font-size:1.5rem;font-weight:900;">
            🤖 PETRO-AI — Assistant Intelligent
        </div>
        <div style="color:rgba(255,255,255,0.7);font-size:0.8rem;margin-top:4px;">
            DeepSeek V4 · Expert petrolier offshore CI · Upload PDF / CSV / Excel
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Modele
    col_m, col_i = st.columns([1, 2])
    with col_m:
        modele = st.selectbox(
            "Modele IA",
            ["deepseek-v4-flash", "deepseek-v4-pro"],
            help="Flash = rapide et economique | Pro = analyse profonde"
        )
    with col_i:
        if modele == "deepseek-v4-flash":
            st.info("🚀 **V4-Flash** — Usage quotidien & questions rapides : monitoring production, alertes puits, water cut, statut ESP, calculs simples")
        else:
            st.info("⚡ **V4-Pro** — Analyses complexes : PSC, sismique, EUR/IRR, déclin réservoir, interprétation logs, rapports techniques, modélisation économique")

    # Session state
    if "chat_history"    not in st.session_state:
        st.session_state.chat_history    = []
    if "fichier_contenu" not in st.session_state:
        st.session_state.fichier_contenu = None
    if "fichier_nom"     not in st.session_state:
        st.session_state.fichier_nom     = None

    # Upload fichier
    st.markdown("#### Analyser un fichier")
    fichier = st.file_uploader(
        "PDF · CSV · Excel (.xlsx) · Texte (.txt)",
        type=["pdf", "csv", "xlsx", "xls", "txt", "log"],
        help="Le fichier sera lu et analyse par DeepSeek V4"
    )

    if fichier:
        with st.spinner(f"Lecture de {fichier.name}..."):
            nom, contenu, type_f = traiter_fichier(fichier)

        if contenu and type_f != "non supporte":
            st.session_state.fichier_contenu = contenu
            st.session_state.fichier_nom     = nom
            st.success(f"✅ **{nom}** charge ({type_f}) — posez votre question ci-dessous")
            with st.expander("Apercu du contenu extrait"):
                st.text(contenu[:1500] + "..." if len(contenu) > 1500 else contenu)
        else:
            st.error(f"Format non supporte : .{nom.split('.')[-1]}")

    # Fichier actif
    if st.session_state.fichier_nom:
        col_f, col_sup = st.columns([4, 1])
        with col_f:
            st.markdown(
                f'<div style="background:#E8F8F0;border-left:4px solid #27AE60;'
                f'border-radius:6px;padding:8px 12px;font-size:0.8rem;">'
                f'Fichier actif : <b>{st.session_state.fichier_nom}</b></div>',
                unsafe_allow_html=True
            )
        with col_sup:
            if st.button("Retirer", use_container_width=True):
                st.session_state.fichier_contenu = None
                st.session_state.fichier_nom     = None
                st.rerun()

    st.divider()

    # Questions rapides
    st.markdown("**Questions rapides :**")
    c1, c2, c3 = st.columns(3)
    questions = {
        "Declin Baleine":
            "Explique le declin de production du champ Baleine et les actions si le taux depasse 15% annuel.",
        "Calcul EUR/IRR":
            "Calcule l'EUR et l'IRR pour un puits a 1200 bbl/j, declin 12%/an, OPEX 18$/bbl, prix 78$/bbl.",
        "Conformite ESG":
            "Quels sont les seuils de flaring selon le Code Petrolier CI et comment optimiser la conformite ESG ?"
    }
    for i, (label, question) in enumerate(questions.items()):
        with [c1, c2, c3][i]:
            if st.button(label, use_container_width=True):
                st.session_state.chat_history.append(
                    {"role": "user", "content": question}
                )

    # Historique
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            texte = msg["content"]
            if "[FICHIER:" in texte:
                idx = texte.find("\n\nCONTENU DU FICHIER")
                if idx > 0:
                    texte = texte[:idx] + "\n*(fichier joint)*"
            st.markdown(f"""
            <div style="background:#EBF5FB;border-radius:10px;padding:12px 16px;
                        margin:6px 0;border-left:4px solid #2E86C1;">
                <b style="color:#1A5276;">Vous</b><br>
                <span style="color:#333;">{texte}</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#F0FFF4;border-radius:10px;padding:12px 16px;
                        margin:6px 0;border-left:4px solid #27AE60;">
                <b style="color:#1A7A4A;">PETRO-AI</b><br>
                <span style="color:#333;">{msg['content']}</span>
            </div>""", unsafe_allow_html=True)

    # Saisie
    with st.form("chat_form", clear_on_submit=True):
        placeholder = (
            f"Posez votre question sur '{st.session_state.fichier_nom}'..."
            if st.session_state.fichier_nom
            else "Ex: Analyse ce water cut de 45% sur le puits B-07..."
        )
        user_input = st.text_area("Votre question :", placeholder=placeholder, height=90)
        col_s, col_c = st.columns([3, 1])
        with col_s:
            submitted = st.form_submit_button("Envoyer", use_container_width=True)
        with col_c:
            cleared = st.form_submit_button("Effacer", use_container_width=True)

    if cleared:
        st.session_state.chat_history    = []
        st.session_state.fichier_contenu = None
        st.session_state.fichier_nom     = None
        st.rerun()

    if submitted and user_input.strip():
        if st.session_state.fichier_contenu:
            message_complet = (
                f"{user_input.strip()}\n\n"
                f"[FICHIER: {st.session_state.fichier_nom}]\n\n"
                f"CONTENU DU FICHIER :\n{st.session_state.fichier_contenu}"
            )
        else:
            message_complet = user_input.strip()

        st.session_state.chat_history.append(
            {"role": "user", "content": message_complet}
        )

        with st.spinner("PETRO-AI analyse..."):
            reponse, erreur = ask_deepseek(
                st.session_state.chat_history, modele=modele
            )

        if erreur:
            st.error(f"Erreur : {erreur}")
            st.session_state.chat_history.pop()
        else:
            st.session_state.chat_history.append(
                {"role": "assistant", "content": reponse}
            )
        st.rerun()


