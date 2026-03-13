import streamlit as st


def render_auth():

    # ─────────────────────────────────────────────
    # HEADER / BRAND
    # ─────────────────────────────────────────────
    st.markdown("""
    <style>

    .login-header{
        text-align:center;
        margin-top:40px;
        margin-bottom:30px;
    }

    .login-brand{
        font-size:32px;
        font-weight:700;
        color:#1E40AF;
    }

    .login-divider{
        width:140px;
        height:3px;
        background:#1E40AF;
        margin:10px auto;
        border-radius:3px;
    }

    .login-subtitle{
        font-size:12px;
        letter-spacing:2px;
        color:#64748B;
        text-transform:uppercase;
    }

    .login-card{
        background:white;
        padding:40px;
        border-radius:14px;
        box-shadow:0 10px 25px rgba(0,0,0,0.08);
        max-width:420px;
        margin:auto;
    }

    .login-title{
        font-size:24px;
        font-weight:600;
        margin-bottom:4px;
    }

    .login-desc{
        color:#6B7280;
        font-size:14px;
        margin-bottom:25px;
    }

    .login-button button{
        width:100%;
        border-radius:10px;
        height:45px;
        font-size:16px;
        font-weight:500;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-header">
        <div class="login-brand">🚚 iMile Delivery</div>
        <div class="login-divider"></div>
        <div class="login-subtitle">Portal Operacional · Brasil</div>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # LOGIN CARD
    # ─────────────────────────────────────────────

    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    st.markdown('<div class="login-title">Bem-vindo de volta</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-desc">Acesso restrito à equipe iMile Brasil</div>', unsafe_allow_html=True)

    email = st.text_input("EMAIL", placeholder="seu@email.com")
    senha = st.text_input("SENHA", type="password")

    st.markdown('<div class="login-button">', unsafe_allow_html=True)

    login = st.button("Entrar no portal →")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Solicitar acesso"):
        st.info("Solicitação de acesso enviada.")

    st.markdown('</div>', unsafe_allow_html=True)

    if login:
        if email and senha:
            st.session_state["auth"] = True
            return True
        else:
            st.error("Preencha email e senha")

    return False