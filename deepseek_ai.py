# deepseek_ai.py — PETRO AFRICA v2.0
# Module Assistant IA — DeepSeek V4-Pro
# Intégration complète : chat, analyse production, interprétation ML

import streamlit as st
from openai import OpenAI
import pandas as pd
from datetime import date

# ════════════════════════════════════════════
# CLIENT DEEPSEEK
# ════════════════════════════════════════════
def get_client():
    """Initialise le client DeepSeek via les secrets Streamlit"""
    return OpenAI(
        api_key=st.secrets["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com"
    )

# ════════════════════════════════════════════
# SYSTEM PROMPT — EXPERT PÉTROLIER
# ════════════════════════════════════════════
SYSTEM_PROMPT = """Tu es PETRO-AI, un assistant expert en ingénierie pétrolière 
spécialisé dans les opérations offshore de Côte d'Ivoire et d'Afrique de l'Ouest.

Tes domaines d'expertise :
- Production pétrolière et gazière (champs Baleine, Sankofa, Foxtrot, Baobab, Lion, Panthère)
- Analyse des courbes de déclin Arps (exponentiel, hyperbolique, harmonique)
- Calculs EUR (Estimated Ultimate Recovery), IRR, NPV
- Contrats de partage de production (PSC) — droit pétrolier ivoirien
- Gestion des puits ESP (pompes électrosubmersibles)
- Interprétation des données sismiques et logs
- Conformité ESG, flaring, émissions CO2 offshore
- Réglementation : Code Pétrolier CI, ENI, PETROCI, TotalEnergies

Règles :
- Réponds toujours en FRANÇAIS
- Sois précis, chiffré, et pratique
- Si on te donne des données de production, analyse-les en détail
- Adapte tes réponses au contexte ivoirien et ouest-africain
- Tu peux faire des calculs et interpréter des résultats ML
"""

# ════════════════════════════════════════════
# FONCTION PRINCIPALE — CHAT
# ════════════════════════════════════════════
def ask_deepseek(messages_history, modele="deepseek-v4-pro"):
    """
    Appel API DeepSeek avec historique de conversation
    modele : "deepseek-v4-pro" (puissant) ou "deepseek-v4-flash" (rapide)
    """
    try:
        client = get_client()
        
        # Construction des messages avec system prompt
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += messages_history
        
        response = client.chat.completions.create(
            model=modele,
            messages=messages,
            max_tokens=2000,
            temperature=0.3,  # Précision maximale pour données techniques
        )
        
        return response.choices[0].message.content, None
    
    except Exception as e:
        return None, str(e)


# ════════════════════════════════════════════
# ANALYSE AUTOMATIQUE ML
# ════════════════════════════════════════════
def analyser_forecast_ml(modele_arps: dict, df_prevision: pd.DataFrame,
                          champ: str, puits: str) -> str:
    """
    Envoie les résultats ML à DeepSeek V4-Pro pour interprétation
    Utilisé directement dans la page ML du dashboard
    """
    if not modele_arps or df_prevision.empty:
        return "Données insuffisantes pour l'analyse IA."

    # Résumé des données pour le prompt
    q_actuelle  = round(modele_arps.get("qi", 0), 0)
    type_declin = modele_arps.get("type", "inconnu")
    r2          = round(modele_arps.get("r2", 0), 3)
    taux_declin = round(modele_arps.get("d", 0) * 365 * 100, 1)  # % annuel

    q_30j  = round(df_prevision["q_prevue"].iloc[29], 0)  if len(df_prevision) > 29  else "N/A"
    q_90j  = round(df_prevision["q_prevue"].iloc[89], 0)  if len(df_prevision) > 89  else "N/A"
    q_180j = round(df_prevision["q_prevue"].iloc[179], 0) if len(df_prevision) > 179 else "N/A"
    q_365j = round(df_prevision["q_prevue"].iloc[364], 0) if len(df_prevision) > 364 else "N/A"

    prompt = f"""Analyse ces résultats ML de production pétrolière :

PUITS : {puits} — CHAMP : {champ}
Date analyse : {date.today()}

MODÈLE ARPS SÉLECTIONNÉ :
- Type de déclin : {type_declin}
- Débit initial (Qi) : {q_actuelle:,.0f} bbl/jour
- Taux de déclin annuel : {taux_declin}%
- R² (qualité du fit) : {r2}

PRÉVISIONS DE PRODUCTION :
- Dans 30 jours  : {q_30j} bbl/jour
- Dans 90 jours  : {q_90j} bbl/jour
- Dans 180 jours : {q_180j} bbl/jour
- Dans 365 jours : {q_365j} bbl/jour

Fournis une analyse technique complète comprenant :
1. Interprétation du type de déclin et ce qu'il indique sur le réservoir
2. Évaluation de la qualité du modèle (R²)
3. Tendance de production et alertes éventuelles
4. Recommandations opérationnelles concrètes (stimulation, workover, etc.)
5. Impact financier estimé (base : 78$/bbl)
"""

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.2,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Erreur analyse IA : {str(e)}"


# ════════════════════════════════════════════
# ANALYSE ALERTES AUTOMATIQUE
# ════════════════════════════════════════════
def analyser_alertes_ia(alertes: list) -> str:
    """
    Analyse les alertes actives et génère des recommandations IA
    """
    if not alertes:
        return "Aucune alerte active à analyser."

    resume = "\n".join([
        f"- {a.get('type_alerte','?')} | Puits: {a.get('puits','?')} "
        f"| Valeur: {a.get('valeur','?')} | Seuil: {a.get('seuil','?')}"
        for a in alertes[:10]  # Max 10 alertes
    ])

    prompt = f"""Analyse ces alertes de production actives sur PETRO AFRICA :

{resume}

Pour chaque alerte, fournis :
1. Cause probable
2. Urgence (CRITIQUE / MODÉRÉ / FAIBLE)
3. Action immédiate recommandée
4. Délai d'intervention suggéré

Conclude avec une priorisation globale des interventions.
"""

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.2,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Erreur analyse alertes IA : {str(e)}"


# ════════════════════════════════════════════
# PAGE ASSISTANT IA — STREAMLIT
# ════════════════════════════════════════════
def render_assistant_ia():
    """
    Page complète Assistant IA à appeler dans dashboard.py
    Ajouter dans le menu : "🤖 Assistant IA"
    """

    # ── Header ──────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1A1A2E,#16213E,#0F3460);
                border-radius:14px;padding:22px 28px;margin-bottom:24px;
                box-shadow:0 6px 24px rgba(0,0,0,0.4);">
        <div style="color:#00D4FF;font-size:1.55rem;font-weight:900;
                    letter-spacing:0.5px;">🤖 PETRO-AI — Assistant Intelligent</div>
        <div style="color:rgba(255,255,255,0.75);font-size:0.82rem;margin-top:5px;">
            Propulsé par DeepSeek V4-Pro · Expert en ingénierie pétrolière offshore CI
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sélection modèle ────────────────────
    col_m, col_info = st.columns([1, 2])
    with col_m:
        modele_choisi = st.selectbox(
            "Modèle IA",
            ["deepseek-v4-pro", "deepseek-v4-flash"],
            help="Pro = analyse profonde | Flash = réponse rapide"
        )
    with col_info:
        if modele_choisi == "deepseek-v4-pro":
            st.info("⚡ **V4-Pro** — Raisonnement avancé STEM, idéal pour PSC, calculs réservoirs, EUR")
        else:
            st.info("🚀 **V4-Flash** — Réponse instantanée, idéal pour questions rapides et monitoring")

    # ── Initialisation historique ────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ── Suggestions rapides ─────────────────
    st.markdown("**Questions rapides :**")
    c1, c2, c3 = st.columns(3)
    questions_rapides = {
        "📊 Analyse déclin Baleine": "Explique-moi le déclin de production du champ Baleine et les actions recommandées si le taux de déclin dépasse 15% annuel.",
        "💰 Calcul EUR & IRR": "Comment calculer l'EUR et l'IRR pour un puits offshore à 1200 bbl/jour avec un déclin de 12% annuel et un coût OPEX de 18$/bbl ?",
        "🌱 Conformité ESG": "Quels sont les seuils de flaring acceptables selon le Code Pétrolier ivoirien et comment optimiser la conformité ESG offshore ?"
    }

    for i, (label, question) in enumerate(questions_rapides.items()):
        col = [c1, c2, c3][i]
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.chat_history.append(
                    {"role": "user", "content": question}
                )

    st.divider()

    # ── Affichage historique ─────────────────
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="background:#EBF5FB;border-radius:10px;padding:12px 16px;
                        margin:8px 0;border-left:4px solid #2E86C1;">
                <b style="color:#1A5276;">👤 Vous</b><br>
                <span style="color:#333;">{msg['content']}</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#F0FFF4;border-radius:10px;padding:12px 16px;
                        margin:8px 0;border-left:4px solid #27AE60;">
                <b style="color:#1A7A4A;">🤖 PETRO-AI</b><br>
                <span style="color:#333;">{msg['content']}</span>
            </div>""", unsafe_allow_html=True)

    # ── Zone de saisie ───────────────────────
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Votre question :",
            placeholder="Ex: Analyse ce taux de water cut de 45% sur le puits B-07...",
            height=100
        )
        col_send, col_clear = st.columns([3, 1])
        with col_send:
            submitted = st.form_submit_button(
                "🚀 Envoyer", use_container_width=True
            )
        with col_clear:
            if st.form_submit_button("🗑️ Effacer", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

    # ── Traitement réponse ───────────────────
    if submitted and user_input.strip():
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input.strip()}
        )

        with st.spinner("PETRO-AI analyse votre question..."):
            reponse, erreur = ask_deepseek(
                st.session_state.chat_history,
                modele=modele_choisi
            )

        if erreur:
            st.error(f"Erreur : {erreur}")
        else:
            st.session_state.chat_history.append(
                {"role": "assistant", "content": reponse}
            )
            st.rerun()

    # ── Info crédits ─────────────────────────
    st.markdown("""
    <div style="background:#FFF8F0;border:1px solid rgba(224,123,0,0.2);
                border-radius:8px;padding:10px 14px;margin-top:16px;
                font-size:0.75rem;color:#888;">
        💡 <b>Coût estimé :</b> V4-Flash ~$0.001/question · V4-Pro ~$0.01/analyse complexe
        · 5M tokens offerts à l'inscription platform.deepseek.com
    </div>
    """, unsafe_allow_html=True)
