"""
auth_ui.py — Autenticação via Supabase Auth
Login real + Solicitação de acesso + Design corporativo claro
"""
import streamlit as st


def _get_sb():
    """Retorna cliente Supabase (reusa o cache do database.py se disponível)."""
    try:
        from database import get_supabase
        return get_supabase()
    except Exception:
        import os
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
        return create_client(url, key)


def _carregar_perfil_usuario(sb, user_id: str, email: str) -> dict:
    """Busca perfil do usuário na tabela 'usuarios'."""
    try:
        res = sb.table("usuarios").select("*").eq("id", user_id).execute()
        if res.data:
            return res.data[0]
        # Fallback: busca por email (caso id ainda não esteja sincronizado)
        res2 = sb.table("usuarios").select("*").eq("email", email.lower()).execute()
        if res2.data:
            return res2.data[0]
    except Exception:
        pass
    return {}


def render_auth() -> bool:
    """
    Renderiza tela de login/registro.
    Retorna True se o usuário está autenticado, False caso contrário.

    Session state preenchidos após login:
        - user_id, user_email, user_nome, user_role, user_bases, user_paginas
    """

    # ── Já autenticado? ───────────────────────────────────────
    if st.session_state.get("auth"):
        return True

    # ── Layout da página de login ─────────────────────────────
    st.markdown("""
    <style>
    /* Esconde sidebar e header do Streamlit na tela de login */
    [data-testid="stSidebar"] { display: none; }
    header[data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 40px !important; max-width: 480px !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Header corporativo ────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; margin-bottom:32px;">
        <div style="font-size:36px; margin-bottom:8px;">🚚</div>
        <div style="font-size:22px; font-weight:700; color:#0f172a; letter-spacing:-0.5px;">
            iMile Delivery
        </div>
        <div style="font-size:13px; color:#64748b; margin-top:4px;">
            Portal Operacional · Brasil
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs Login / Solicitar Acesso ─────────────────────────
    tab_login, tab_registro = st.tabs(["🔑 Entrar", "📝 Solicitar Acesso"])

    # ══════════════════════════════════════════════════════════
    #  TAB: LOGIN
    # ══════════════════════════════════════════════════════════
    with tab_login:
        st.markdown(
            "<p style='color:#475569;font-size:14px;margin-bottom:16px'>"
            "Entre com seu email e senha cadastrados.</p>",
            unsafe_allow_html=True,
        )

        email = st.text_input("Email", key="login_email", placeholder="seu.email@imile.com")
        senha = st.text_input("Senha", type="password", key="login_senha", placeholder="••••••••")

        if st.button("Entrar no portal", use_container_width=True, type="primary", key="btn_login"):
            if not email or not senha:
                st.error("Preencha email e senha.")
            else:
                with st.spinner("Autenticando..."):
                    try:
                        sb = _get_sb()
                        res = sb.auth.sign_in_with_password({
                            "email": email.strip(),
                            "password": senha,
                        })

                        user = res.user
                        if not user:
                            st.error("Credenciais inválidas.")
                            return False

                        # Busca perfil na tabela usuarios
                        perfil = _carregar_perfil_usuario(sb, user.id, user.email)

                        if not perfil:
                            st.warning(
                                "Seu email foi autenticado mas ainda não tem perfil no portal. "
                                "Solicite acesso na aba **📝 Solicitar Acesso** ou "
                                "peça ao administrador para aprovar seu cadastro."
                            )
                            return False

                        if not perfil.get("ativo", True):
                            st.error("Sua conta está desativada. Entre em contato com o administrador.")
                            return False

                        # ── Preenche session state ────────────
                        st.session_state["auth"]          = True
                        st.session_state["user_id"]       = str(user.id)
                        st.session_state["user_email"]    = user.email
                        st.session_state["user_nome"]     = perfil.get("nome", "")
                        st.session_state["user_role"]     = perfil.get("role", "viewer")
                        st.session_state["user_bases"]    = perfil.get("bases") or []
                        st.session_state["user_paginas"]  = perfil.get("paginas") or []
                        st.session_state["access_token"]  = res.session.access_token

                        st.rerun()

                    except Exception as e:
                        msg = str(e).lower()
                        if "invalid" in msg or "credentials" in msg:
                            st.error("Email ou senha incorretos.")
                        elif "email not confirmed" in msg:
                            st.warning(
                                "Seu email ainda não foi confirmado. "
                                "Verifique sua caixa de entrada (e spam)."
                            )
                        else:
                            st.error(f"Erro na autenticação: {e}")

    # ══════════════════════════════════════════════════════════
    #  TAB: SOLICITAR ACESSO
    # ══════════════════════════════════════════════════════════
    with tab_registro:
        st.markdown(
            "<p style='color:#475569;font-size:14px;margin-bottom:16px'>"
            "Preencha o formulário abaixo. O administrador será notificado e aprovará seu acesso.</p>",
            unsafe_allow_html=True,
        )

        reg_nome   = st.text_input("Nome completo", key="reg_nome", placeholder="João Silva")
        reg_email  = st.text_input("Email corporativo", key="reg_email", placeholder="joao.silva@imile.com")
        reg_motivo = st.text_area(
            "Motivo / Área de atuação",
            key="reg_motivo",
            placeholder="Ex: Supervisor da região Capital, preciso acompanhar indicadores diários.",
            height=100,
        )

        if st.button("Enviar solicitação", use_container_width=True, type="primary", key="btn_registro"):
            if not reg_nome or not reg_email:
                st.error("Nome e email são obrigatórios.")
            elif "@" not in reg_email:
                st.error("Informe um email válido.")
            else:
                with st.spinner("Enviando..."):
                    try:
                        sb = _get_sb()
                        sb.table("solicitacoes_acesso").insert({
                            "nome":   reg_nome.strip(),
                            "email":  reg_email.strip().lower(),
                            "motivo": reg_motivo.strip() if reg_motivo else "",
                            "status": "pendente",
                        }).execute()

                        st.success(
                            "✅ Solicitação enviada com sucesso! "
                            "Você receberá um email quando o administrador aprovar seu acesso."
                        )
                    except Exception as e:
                        st.error(f"Erro ao enviar solicitação: {e}")

    return False


def logout():
    """Desloga o usuário e limpa session state."""
    # Tenta sign_out no Supabase (silencia erros)
    try:
        sb = _get_sb()
        sb.auth.sign_out()
    except Exception:
        pass

    # Limpa todos os dados de sessão
    for key in [
        "auth", "user_id", "user_email", "user_nome",
        "user_role", "user_bases", "user_paginas", "access_token",
        "pagina_atual",
    ]:
        st.session_state.pop(key, None)

    st.rerun()
