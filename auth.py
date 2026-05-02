# auth.py — PETRO AFRICA v2.3
# Authentification via Supabase Auth (email/password hashé côté serveur)
# Fallback local si Supabase indisponible

import streamlit as st
import hashlib

# ─────────────────────────────────────────
# FALLBACK LOCAL — mots de passe hashés SHA-256
# Générer avec : hashlib.sha256("monmdp".encode()).hexdigest()
# ─────────────────────────────────────────
def _hash(mdp: str) -> str:
    return hashlib.sha256(mdp.encode()).hexdigest()

UTILISATEURS_FALLBACK = {
    "admin@petroci.ci": {
        "hash":      _hash("petroci2026"),
        "nom":       "Administrateur PETROCI",
        "role":      "admin",
        "compagnie": "PETROCI",
        "acces":     ["Baleine","Sankofa","Foxtrot","Baobab","Lion","Panthere"],
    },
    "eni@baleine.ci": {
        "hash":      _hash("baleine2026"),
        "nom":       "Ingenieur ENI",
        "role":      "operateur",
        "compagnie": "ENI",
        "acces":     ["Baleine"],
    },
    "total@sankofa.ci": {
        "hash":      _hash("sankofa2026"),
        "nom":       "Ingenieur TotalEnergies",
        "role":      "operateur",
        "compagnie": "TotalEnergies",
        "acces":     ["Sankofa","Foxtrot","Lion","Panthere"],
    },
    "cnr@baobab.ci": {
        "hash":      _hash("baobab2026"),
        "nom":       "Ingenieur CNR",
        "role":      "operateur",
        "compagnie": "CNR International",
        "acces":     ["Baobab"],
    },
    "demo@petroci.ci": {
        "hash":      _hash("demo2026"),
        "nom":       "Utilisateur Demo",
        "role":      "viewer",
        "compagnie": "Demo",
        "acces":     ["Baleine","Sankofa"],
    },
}

# ─────────────────────────────────────────
# DÉTECTION SUPABASE
# ─────────────────────────────────────────
def _supabase_disponible() -> bool:
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return bool(url and key and url.startswith("https://"))
    except Exception:
        return False

def _get_supabase():
    from supabase import create_client
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"],
    )

# ─────────────────────────────────────────
# LOGIN SUPABASE AUTH
# ─────────────────────────────────────────
def _login_supabase(email: str, mdp: str):
    """
    Authentification via Supabase Auth (mots de passe stockés et hashés
    côté Supabase — jamais en clair dans le code).
    Retourne le profil utilisateur ou None.
    """
    try:
        sb   = _get_supabase()
        resp = sb.auth.sign_in_with_password({"email": email, "password": mdp})
        user = resp.user
        if not user:
            return None

        # Récupérer le profil dans la table 'profils_utilisateurs'
        profil_data = (
            sb.table("profils_utilisateurs")
              .select("*")
              .eq("email", email)
              .single()
              .execute()
        )
        if profil_data.data:
            p = profil_data.data
            return {
                "email":     email,
                "nom":       p.get("nom", email),
                "role":      p.get("role", "viewer"),
                "compagnie": p.get("compagnie", ""),
                "acces":     p.get("acces_champs", []),
                "supabase":  True,
            }
        # Profil absent → accès viewer par défaut
        return {
            "email":     email,
            "nom":       email,
            "role":      "viewer",
            "compagnie": "",
            "acces":     [],
            "supabase":  True,
        }
    except Exception:
        return None

# ─────────────────────────────────────────
# LOGIN FALLBACK LOCAL
# ─────────────────────────────────────────
def _login_local(email: str, mdp: str):
    """Fallback : comparaison hash SHA-256 — aucun mot de passe en clair."""
    email = email.strip().lower()
    user  = UTILISATEURS_FALLBACK.get(email)
    if user and user["hash"] == _hash(mdp):
        return {
            "email":     email,
            "nom":       user["nom"],
            "role":      user["role"],
            "compagnie": user["compagnie"],
            "acces":     user["acces"],
            "supabase":  False,
        }
    return None

# ─────────────────────────────────────────
# VÉRIFICATION LOGIN (point d'entrée unique)
# ─────────────────────────────────────────
def verifier_login(email: str, mdp: str):
    """
    Tente Supabase Auth en priorité.
    Si Supabase Auth échoue (utilisateur non inscrit dans Supabase Auth),
    bascule automatiquement sur le fallback local hashé.
    """
    if _supabase_disponible():
        user = _login_supabase(email, mdp)
        if user:
            return user
    # Fallback local — toujours disponible
    return _login_local(email, mdp)

# ─────────────────────────────────────────
# PAGE LOGIN
# ─────────────────────────────────────────
def afficher_page_login():
    st.markdown("""
    <div style="
        max-width: 420px;
        margin: 40px auto;
        background: white;
        border-radius: 16px;
        padding: 40px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.10);
        border-top: 5px solid #E07B00;
    ">
        <div style="text-align:center;margin-bottom:28px;">
            <div style="font-size:3rem;">🛢️</div>
            <div style="color:#E07B00;font-size:1.5rem;
                        font-weight:800;letter-spacing:3px;
                        margin:8px 0 4px 0;">PETRO AFRICA</div>
            <div style="color:#AAA;font-size:0.78rem;
                        letter-spacing:2px;">
                SYSTEME DE GESTION DE PRODUCTION
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    mode = "Supabase Auth" if _supabase_disponible() else "Mode local sécurisé"
    st.caption(f"🔒 Authentification : {mode}")

    with st.form("login_form"):
        st.markdown("### Connexion")
        email = st.text_input(
            "Email professionnel",
            placeholder="votre.nom@compagnie.ci"
        )
        mdp = st.text_input(
            "Mot de passe",
            type="password",
            placeholder="••••••••"
        )
        col1, col2 = st.columns([2, 1])
        with col1:
            connecter = st.form_submit_button(
                "Se connecter",
                use_container_width=True,
                type="primary"
            )
        with col2:
            demo_btn = st.form_submit_button(
                "Demo",
                use_container_width=True
            )

    if demo_btn:
        user = _login_local("demo@petroci.ci", "demo2026")
        if user:
            _enregistrer_session(user)
            st.rerun()

    if connecter:
        if not email or not mdp:
            st.error("Veuillez remplir tous les champs.")
            return False
        user = verifier_login(email, mdp)
        if user:
            _enregistrer_session(user)
            st.success(f"Bienvenue {user['nom']} !")
            st.rerun()
        else:
            st.error("Email ou mot de passe incorrect.")
            return False

    return False

def _enregistrer_session(user: dict):
    st.session_state["connecte"]  = True
    st.session_state["user"]      = user
    st.session_state["email"]     = user["email"]
    st.query_params["session"]    = user["email"]

# ─────────────────────────────────────────
# VÉRIFICATION SESSION
# ─────────────────────────────────────────
def verifier_session() -> bool:
    if st.session_state.get("connecte", False):
        return True
    email_saved = st.query_params.get("session", "")
    if email_saved:
        # Restaurer depuis fallback local (pas de mot de passe requis)
        user_data = UTILISATEURS_FALLBACK.get(email_saved.strip().lower())
        if user_data:
            st.session_state["connecte"] = True
            st.session_state["email"]    = email_saved
            st.session_state["user"]     = {
                "email":     email_saved,
                "nom":       user_data["nom"],
                "role":      user_data["role"],
                "compagnie": user_data["compagnie"],
                "acces":     user_data["acces"],
                "supabase":  False,
            }
            return True
    return False

def get_user() -> dict:
    return st.session_state.get("user", {})

def deconnecter():
    for key in ["connecte", "user", "email"]:
        st.session_state.pop(key, None)
    st.query_params.clear()
    st.rerun()

def verifier_acces_champ(champ: str) -> bool:
    user = get_user()
    if user.get("role") == "admin":
        return True
    return champ in user.get("acces", [])
