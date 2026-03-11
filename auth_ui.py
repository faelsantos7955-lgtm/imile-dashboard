import streamlit as st
import base64, os

def _logo_b64():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    if os.path.exists(p):
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def _inject_css():
    b64 = _logo_b64()
    logo_src = f"data:image/png;base64,{b64}" if b64 else ""

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

#MainMenu, footer, header {{ visibility:hidden!important }}
[data-testid="stToolbar"] {{ display:none!important }}
section[data-testid="stSidebar"] {{ display:none!important }}

.stApp {{
    background: #f1f5f9 !important;
    min-height: 100vh;
    font-family: 'Inter', sans-serif !important;
}}

/* Faixa lateral esquerda decorativa */
.stApp::before {{
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 420px; height: 100vh;
    background: linear-gradient(160deg, #0f172a 0%, #1e3a8a 60%, #1d4ed8 100%);
    z-index: 0;
    pointer-events: none;
}}

/* Padrão geométrico na faixa */
.stApp::after {{
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 420px; height: 100vh;
    background-image:
        radial-gradient(circle at 80px 120px, rgba(255,255,255,0.06) 1px, transparent 1px),
        radial-gradient(circle at 240px 280px, rgba(255,255,255,0.04) 1px, transparent 1px),
        radial-gradient(circle at 160px 440px, rgba(255,255,255,0.06) 1px, transparent 1px),
        radial-gradient(circle at 320px 560px, rgba(255,255,255,0.04) 1px, transparent 1px),
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: auto, auto, auto, auto, 40px 40px, 40px 40px;
    z-index: 0;
    pointer-events: none;
}}

.block-container {{
    padding: 0 !important;
    max-width: 100vw !important;
    min-height: 100vh;
    position: relative;
    z-index: 1;
}}

.main > div {{
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    min-height: 100vh !important;
}}

/* ── Card de login (coluna do meio) ── */
[data-testid="column"]:nth-child(2) > div,
[data-testid="column"]:nth-child(2) > div > div {{
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 40px 44px !important;
    box-shadow:
        0 4px 6px -1px rgba(0,0,0,0.07),
        0 20px 60px -8px rgba(0,0,0,0.12),
        0 0 0 1px rgba(255,255,255,0.8) inset !important;
    position: relative !important;
    z-index: 2 !important;
}}

/* ── Título ── */
.login-title {{
    font-family: 'Inter', sans-serif !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    letter-spacing: -0.4px !important;
    margin-bottom: 2px !important;
    line-height: 1.2 !important;
}}
.login-sub {{
    font-size: 13px !important;
    color: #64748b !important;
    margin-bottom: 24px !important;
    line-height: 1.5 !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── Inputs ── */
div[data-testid="stTextInput"] input {{
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 8px !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    padding: 11px 14px !important;
    transition: border-color .2s, box-shadow .2s, background .2s !important;
}}
div[data-testid="stTextInput"] input:focus {{
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,.1) !important;
    background: #ffffff !important;
    outline: none !important;
}}
div[data-testid="stTextInput"] input::placeholder {{ color: #94a3b8 !important }}
div[data-testid="stTextInput"] label {{
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #475569 !important;
    font-family: 'DM Mono', monospace !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
}}
div[data-testid="stTextInput"] button {{
    color: #94a3b8 !important;
    background: transparent !important;
    border: none !important;
}}
div[data-testid="stTextArea"] textarea {{
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 8px !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}}
div[data-testid="stTextArea"] textarea:focus {{
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,.1) !important;
    background: #ffffff !important;
}}
div[data-testid="stTextArea"] label {{
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #475569 !important;
    font-family: 'DM Mono', monospace !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
}}

/* ── Botão primário ── */
div[data-testid="stButton"] > button {{
    width: 100% !important;
    background: #1d4ed8 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 20px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0.1px !important;
    box-shadow: 0 2px 8px rgba(29,78,216,.3), 0 1px 2px rgba(29,78,216,.2) !important;
    transition: all .2s ease !important;
    cursor: pointer !important;
}}
div[data-testid="stButton"] > button:hover {{
    background: #1e40af !important;
    box-shadow: 0 4px 16px rgba(29,78,216,.4) !important;
    transform: translateY(-1px) !important;
}}

/* Botão secundário */
.btn-sec div[data-testid="stButton"] > button {{
    background: #ffffff !important;
    color: #475569 !important;
    border: 1.5px solid #e2e8f0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}}
.btn-sec div[data-testid="stButton"] > button:hover {{
    background: #f8fafc !important;
    border-color: #cbd5e1 !important;
    color: #334155 !important;
    transform: none !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
}}

/* Botão ghost (Esqueci senha) */
.btn-ghost div[data-testid="stButton"] > button {{
    background: transparent !important;
    color: #2563eb !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 12px !important;
    padding: 4px 8px !important;
    width: auto !important;
    font-weight: 500 !important;
    text-decoration: underline !important;
}}
.btn-ghost div[data-testid="stButton"] > button:hover {{
    color: #1d4ed8 !important;
    transform: none !important;
    box-shadow: none !important;
    background: transparent !important;
}}

/* ── Divisor ── */
.adiv {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 14px 0;
    color: #cbd5e1;
    font-size: 10px;
    font-family: 'DM Mono', monospace;
    letter-spacing: 1px;
}}
.adiv::before, .adiv::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: #e2e8f0;
}}

/* ── Badges / banners ── */
.badge-pend {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #fefce8;
    border: 1px solid #fde68a;
    color: #92400e;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    margin-bottom: 16px;
}}
.banner-i {{
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1e40af;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    line-height: 1.55;
    margin-bottom: 16px;
    font-family: 'Inter', sans-serif;
}}
.msg-ok {{
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    margin-bottom: 14px;
    font-family: 'Inter', sans-serif;
}}
.msg-err {{
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #991b1b;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    margin-bottom: 14px;
    font-family: 'Inter', sans-serif;
}}

/* ── Footer ── */
.login-footer {{
    text-align: center;
    font-size: 11px;
    color: #94a3b8;
    font-family: 'DM Mono', monospace;
    margin-top: 20px;
    letter-spacing: 0.5px;
}}

/* ── Alertas Streamlit ── */
[data-testid="stAlert"] {{
    border-radius: 8px !important;
    font-size: 13px !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── Logo no card ── */
.login-logo {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 28px;
    padding-bottom: 24px;
    border-bottom: 1px solid #f1f5f9;
}}
.login-logo-text {{
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.3px;
}}
.login-logo-badge {{
    font-size: 9px;
    font-weight: 600;
    color: #64748b;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}
</style>
""", unsafe_allow_html=True)


def _card_col():
    """Retorna a coluna do meio que funciona como card."""
    _, mid, _ = st.columns([1, 1.4, 1])
    return mid


# ── Supabase helpers ──────────────────────────────────────────
def _sb():
    from database import get_supabase
    return get_supabase()

def login_supabase(email, password):
    try:
        res = _sb().auth.sign_in_with_password({"email": email, "password": password})
        return res.user, None
    except Exception as e:
        msg = str(e)
        if "Invalid login" in msg or "invalid_grant" in msg.lower():
            return None, "Email ou senha incorretos."
        if "Email not confirmed" in msg:
            return None, "Confirme seu email antes de entrar."
        return None, f"Erro: {msg}"

def solicitar_acesso(nome, email, empresa, motivo):
    try:
        _sb().table("solicitacoes_acesso").insert({
            "nome":nome,"email":email,"empresa":empresa,
            "motivo":motivo,"status":"pendente"
        }).execute()
        return True, None
    except Exception as e:
        return False, str(e)

def solicitar_reset(email):
    try:
        _sb().auth.reset_password_email(email)
        return True, None
    except Exception as e:
        return False, str(e)

def get_user_meta(user_id):
    try:
        res = _sb().table("usuarios").select("*").eq("id", user_id).execute()
        return res.data[0] if res.data else {}
    except Exception:
        return {}

def _bases_from_meta(meta):
    bases = meta.get("bases") or []
    if isinstance(bases, str):
        import json
        try: bases = json.loads(bases)
        except: bases = []
    return bases if bases else None


# ── Páginas ───────────────────────────────────────────────────

def pagina_login():
    _inject_css()
    mid = _card_col()
    with mid:
        # Logo
        b64 = _logo_b64()
        if b64:
            st.markdown(
                f'<div style="text-align:center;margin-bottom:6px">'
                f'<img src="data:image/png;base64,{b64}" '
                f'style="height:44px;filter:brightness(0) invert(1)"></div>',
                unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;font-family:Syne,sans-serif;'
                        'font-size:22px;font-weight:800;color:#fff;margin-bottom:6px">'
                        '🚚 iMile Delivery</div>', unsafe_allow_html=True)

        st.markdown('<div style="text-align:center;font-family:DM Mono,monospace;'
                    'font-size:10px;color:#3b82f6;letter-spacing:2px;'
                    'text-transform:uppercase;margin-bottom:24px">'
                    'Portal Operacional · iMile Brasil</div>', unsafe_allow_html=True)

        st.markdown('<div class="login-title">Bem-vindo de volta</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Acesso restrito à equipe iMile Brasil</div>', unsafe_allow_html=True)

        # Mensagem de retorno
        if st.session_state.get("auth_msg"):
            cls = "msg-ok" if st.session_state.get("auth_msg_type") == "ok" else "msg-err"
            ico = "✅" if st.session_state.get("auth_msg_type") == "ok" else "⚠️"
            st.markdown(f'<div class="{cls}">{ico} {st.session_state.pop("auth_msg")}</div>',
                        unsafe_allow_html=True)
            st.session_state.pop("auth_msg_type", None)

        email = st.text_input("Email", placeholder="seu@email.com", key="l_email")
        senha = st.text_input("Senha", placeholder="••••••••", type="password", key="l_senha")

        _, cf = st.columns([1, 1])
        with cf:
            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
            if st.button("Esqueci a senha", key="btn_forgot"):
                st.session_state["auth_page"] = "forgot"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Entrar no portal →", key="btn_login", use_container_width=True):
            if not email or not senha:
                st.error("Preencha email e senha.")
            else:
                user, err = login_supabase(email.strip(), senha)
                if err:
                    st.error(err)
                else:
                    meta = get_user_meta(user.id)
                    st.session_state.update({
                        "autenticado": True, "user_id": user.id,
                        "user_email": user.email,
                        "user_nome": meta.get("nome", user.email),
                        "user_role": meta.get("role", "viewer"),
                        "user_bases": _bases_from_meta(meta),
                    })
                    st.rerun()

        st.markdown('<div class="adiv">ou</div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-sec">', unsafe_allow_html=True)
        if st.button("Solicitar acesso", key="btn_reg", use_container_width=True):
            st.session_state["auth_page"] = "register"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="login-footer">© 2025 iMile Delivery · Acesso restrito</div>',
                    unsafe_allow_html=True)


def pagina_cadastro():
    _inject_css()
    mid = _card_col()
    with mid:
        b64 = _logo_b64()
        if b64:
            st.markdown(
                f'<div style="text-align:center;margin-bottom:6px">'
                f'<img src="data:image/png;base64,{b64}" '
                f'style="height:40px;filter:brightness(0) invert(1)"></div>',
                unsafe_allow_html=True)

        st.markdown('<div style="text-align:center;margin-bottom:20px">'
                    '<span class="badge-pend">⏳ Sujeito à aprovação do administrador</span>'
                    '</div>', unsafe_allow_html=True)

        st.markdown('<div class="login-title">Solicitar acesso</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            nome  = st.text_input("Nome completo", placeholder="João Silva", key="r_nome")
        with c2:
            email = st.text_input("Email", placeholder="joao@imile.com", key="r_email")

        empresa = st.text_input("Empresa / Departamento", placeholder="iMile · Operações", key="r_emp")
        motivo  = st.text_area("Motivo do acesso",
                               placeholder="Descreva brevemente para que você precisa acessar...",
                               key="r_mot", height=80)

        st.markdown('<div class="banner-i">🔒 O administrador definirá quais bases você poderá '
                    'visualizar após a aprovação.</div>', unsafe_allow_html=True)

        if st.button("Enviar solicitação →", key="btn_sol", use_container_width=True):
            if not all([nome, email, empresa, motivo]):
                st.error("Preencha todos os campos.")
            else:
                ok, err = solicitar_acesso(nome, email.strip(), empresa, motivo)
                if ok:
                    st.session_state.update({
                        "auth_msg": "Solicitação enviada! O admin analisará em breve.",
                        "auth_msg_type": "ok", "auth_page": "login"
                    })
                    st.rerun()
                else:
                    st.error(f"Erro: {err}")

        st.markdown('<div class="btn-sec">', unsafe_allow_html=True)
        if st.button("← Voltar ao login", key="btn_bk", use_container_width=True):
            st.session_state["auth_page"] = "login"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="login-footer">© 2025 iMile Delivery · Acesso restrito</div>',
                    unsafe_allow_html=True)


def pagina_esqueci_senha():
    _inject_css()
    mid = _card_col()
    with mid:
        b64 = _logo_b64()
        if b64:
            st.markdown(
                f'<div style="text-align:center;margin-bottom:6px">'
                f'<img src="data:image/png;base64,{b64}" '
                f'style="height:40px;filter:brightness(0) invert(1)"></div>',
                unsafe_allow_html=True)

        st.markdown('<div class="login-title">Redefinir senha</div>', unsafe_allow_html=True)
        st.markdown('<div class="banner-i">🔐 Enviaremos um link seguro para o seu email. '
                    'Válido por 15 minutos.</div>', unsafe_allow_html=True)

        email = st.text_input("Email cadastrado", placeholder="seu@email.com", key="f_email")

        if st.button("Enviar link de redefinição →", key="btn_reset", use_container_width=True):
            if not email:
                st.error("Digite seu email.")
            else:
                ok, err = solicitar_reset(email.strip())
                if ok:
                    st.session_state.update({
                        "auth_msg": "Link enviado! Verifique sua caixa de entrada.",
                        "auth_msg_type": "ok", "auth_page": "login"
                    })
                    st.rerun()
                else:
                    st.error(f"Erro: {err}")

        st.markdown('<div class="btn-sec">', unsafe_allow_html=True)
        if st.button("← Voltar ao login", key="btn_bkf", use_container_width=True):
            st.session_state["auth_page"] = "login"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="login-footer">© 2025 iMile Delivery · Acesso restrito</div>',
                    unsafe_allow_html=True)


def _definir_senha(token: str, tipo: str):
    """Pagina para definir/redefinir senha via token da URL."""
    _inject_css()
    mid = _card_col()
    with mid:
        b64 = _logo_b64()
        if b64:
            st.markdown(
                f'<div style="text-align:center;margin-bottom:6px">'
                f'<img src="data:image/png;base64,{b64}" '
                f'style="height:40px;filter:brightness(0) invert(1)"></div>',
                unsafe_allow_html=True)

        titulo = "Criar sua senha" if tipo == "invite" else "Redefinir senha"
        st.markdown(f'<div class="login-title">{titulo}</div>', unsafe_allow_html=True)
        st.markdown('<div class="banner-i">🔐 Escolha uma senha segura para acessar o portal.</div>',
                    unsafe_allow_html=True)

        nova_senha = st.text_input("Nova senha", type="password", placeholder="Mínimo 6 caracteres", key="ns1")
        conf_senha = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha", key="ns2")

        if st.button("Salvar senha →", key="btn_set_pwd", use_container_width=True):
            if not nova_senha or not conf_senha:
                st.error("Preencha os dois campos.")
            elif nova_senha != conf_senha:
                st.error("As senhas não coincidem.")
            elif len(nova_senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            else:
                try:
                    sb = _sb()
                    # Autentica com o token OTP do link
                    res = sb.auth.verify_otp({"token_hash": token, "type": tipo})
                    if not res or not res.session:
                        # Fallback: tenta exchange_code_for_session
                        res = sb.auth.exchange_code_for_session({"auth_code": token})
                    if res and res.session:
                        sb.auth.update_user({"password": nova_senha})
                        st.success("✅ Senha definida com sucesso!")
                        st.session_state["auth_page"] = "login"
                        st.session_state["auth_msg"] = "Senha criada! Faça login para continuar."
                        st.session_state["auth_msg_type"] = "ok"
                        st.query_params.clear()
                        st.rerun()
                    else:
                        st.error("Link inválido ou expirado. Solicite um novo.")
                except Exception as e:
                    err_str = str(e)
                    if "expired" in err_str.lower() or "invalid" in err_str.lower():
                        st.error("❌ Link expirado. Solicite um novo link de redefinição.")
                    else:
                        st.error(f"Erro: {err_str}")

        if st.button("← Voltar ao login", key="btn_bk_pwd", use_container_width=True):
            st.query_params.clear()
            st.session_state["auth_page"] = "login"
            st.rerun()

        st.markdown('<div class="login-footer">© 2025 iMile Delivery · Acesso restrito</div>',
                    unsafe_allow_html=True)


# ── Entrada principal ─────────────────────────────────────────
def render_auth() -> bool:
    if st.session_state.get("autenticado"):
        return True

    # Injeta JS que lê o hash (#access_token=...&type=recovery)
    # e redireciona para ?token=...&type=... que o Streamlit consegue ler
    st.markdown("""
    <script>
    (function() {
        var hash = window.location.hash;
        if (hash && hash.includes('access_token')) {
            var params = {};
            hash.replace('#','').split('&').forEach(function(p) {
                var kv = p.split('=');
                params[kv[0]] = decodeURIComponent(kv[1] || '');
            });
            if (params['type'] === 'recovery' || params['type'] === 'invite' || params['type'] === 'signup') {
                var newUrl = window.location.pathname +
                    '?token=' + encodeURIComponent(params['access_token']) +
                    '&type=' + encodeURIComponent(params['type']);
                window.location.replace(newUrl);
            }
        }
    })();
    </script>
    """, unsafe_allow_html=True)

    # Detecta token nos query params (após redirecionamento do JS acima)
    params = st.query_params
    token = params.get("token", "")
    tipo  = params.get("type", "")

    if token and tipo in ("invite", "recovery", "signup"):
        _definir_senha(token, tipo)
        return False

    page = st.session_state.get("auth_page", "login")
    if page == "register":   pagina_cadastro()
    elif page == "forgot":   pagina_esqueci_senha()
    else:                    pagina_login()
    return False

def logout():
    for k in ["autenticado","user_id","user_email","user_nome","user_role","user_bases","auth_page"]:
        st.session_state.pop(k, None)
    st.rerun()
