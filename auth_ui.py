import streamlit as st


def render_auth():

    st.markdown("""
    <div class="login-header">
        <div class="login-brand">🚚 iMile Delivery</div>
        <div class="login-divider"></div>
        <div class="login-subtitle">Portal Operacional · Brasil</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    st.subheader("Bem-vindo de volta")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    login = st.button("Entrar no portal")

    if login:
        if email and senha:
            st.session_state["auth"] = True
            return True
        else:
            st.error("Preencha email e senha")

    st.markdown('</div>', unsafe_allow_html=True)

    return False