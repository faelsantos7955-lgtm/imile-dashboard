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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset geral ── */
#MainMenu, footer, header {{ visibility:hidden!important }}
[data-testid="stToolbar"] {{ display:none!important }}
section[data-testid="stSidebar"] {{ display:none!important }}

/* ── Fundo animado ── */
.stApp {{
    background:#060d1a!important;
    min-height:100vh;
}}
.block-container {{
    padding:0!important;
    max-width:100vw!important;
    min-height:100vh;
}}

/* ── Canvas partículas ── */
#login-canvas {{
    position:fixed;top:0;left:0;
    width:100vw;height:100vh;
    z-index:0;pointer-events:none;
}}

/* ── Centralização vertical ── */
.main > div {{
    display:flex!important;
    flex-direction:column!important;
    justify-content:center!important;
    min-height:100vh!important;
}}
.block-container {{
    padding-top:20px!important;
    padding-bottom:20px!important;
    max-width:100vw!important;
}}

/* ── Card: tenta múltiplos seletores ── */
[data-testid="column"]:nth-child(2) > div,
[data-testid="column"]:nth-child(2) > div > div {{
    background:#0c1a30!important;
    border:1.5px solid rgba(37,99,235,0.35)!important;
    border-radius:18px!important;
    padding:32px 36px!important;
    box-shadow:0 2px 40px rgba(0,0,0,0.8),
               0 0 0 1px rgba(37,99,235,0.1),
               inset 0 1px 0 rgba(255,255,255,0.04)!important;
    position:relative!important;
    z-index:2!important;
}}

/* ── Título ── */
.login-title {{
    font-family:'Syne',sans-serif!important;
    font-size:22px!important;font-weight:800!important;
    color:#f1f5f9!important;letter-spacing:-.3px!important;
    margin-bottom:2px!important;
}}
.login-sub {{
    font-size:12px!important;color:#475569!important;
    margin-bottom:20px!important;line-height:1.5!important;
    font-family:'DM Sans',sans-serif!important;
}}

/* ── Inputs ── */
div[data-testid="stTextInput"] input {{
    background:#0d1f3c!important;
    border:1.5px solid #1e3a5f!important;
    border-radius:10px!important;
    color:#e2e8f0!important;
    font-family:'DM Sans',sans-serif!important;
    font-size:14px!important;
    padding:11px 14px!important;
    transition:border-color .2s,box-shadow .2s!important;
}}
div[data-testid="stTextInput"] input:focus {{
    border-color:#3b82f6!important;
    box-shadow:0 0 0 3px rgba(59,130,246,.15)!important;
    outline:none!important;
}}
div[data-testid="stTextInput"] input::placeholder {{ color:#334155!important }}
div[data-testid="stTextInput"] label {{
    font-size:10px!important;font-weight:600!important;
    color:#64748b!important;font-family:'DM Mono',monospace!important;
    letter-spacing:1px!important;text-transform:uppercase!important;
    margin-bottom:4px!important;
}}
div[data-testid="stTextInput"] button {{
    color:#475569!important;background:transparent!important;border:none!important;
}}
div[data-testid="stTextArea"] textarea {{
    background:#0d1f3c!important;
    border:1.5px solid #1e3a5f!important;
    border-radius:10px!important;color:#e2e8f0!important;
    font-family:'DM Sans',sans-serif!important;font-size:14px!important;
}}
div[data-testid="stTextArea"] textarea:focus {{
    border-color:#3b82f6!important;
    box-shadow:0 0 0 3px rgba(59,130,246,.15)!important;
}}
div[data-testid="stTextArea"] label {{
    font-size:10px!important;font-weight:600!important;color:#64748b!important;
    font-family:'DM Mono',monospace!important;letter-spacing:1px!important;
    text-transform:uppercase!important;
}}

/* ── Botão primário ── */
div[data-testid="stButton"] > button {{
    width:100%!important;
    background:linear-gradient(135deg,#1d4ed8,#2563eb)!important;
    color:#fff!important;border:none!important;
    border-radius:10px!important;padding:12px 20px!important;
    font-family:'Syne',sans-serif!important;font-size:14px!important;
    font-weight:700!important;letter-spacing:.3px!important;
    box-shadow:0 4px 20px rgba(37,99,235,.4)!important;
    transition:transform .2s,box-shadow .2s!important;
    cursor:pointer!important;
}}
div[data-testid="stButton"] > button:hover {{
    transform:translateY(-2px)!important;
    box-shadow:0 8px 28px rgba(37,99,235,.55)!important;
}}

/* Botão secundário */
.btn-sec div[data-testid="stButton"] > button {{
    background:transparent!important;
    color:#64748b!important;
    border:1px solid #1e3a5f!important;
    box-shadow:none!important;
    font-size:13px!important;font-weight:500!important;
}}
.btn-sec div[data-testid="stButton"] > button:hover {{
    background:#0d1f3c!important;color:#94a3b8!important;
    transform:none!important;box-shadow:none!important;
}}

/* Botão ghost (Esqueci senha) */
.btn-ghost div[data-testid="stButton"] > button {{
    background:transparent!important;color:#475569!important;
    border:none!important;box-shadow:none!important;
    font-size:12px!important;padding:4px 8px!important;
    width:auto!important;font-weight:500!important;
}}
.btn-ghost div[data-testid="stButton"] > button:hover {{
    color:#94a3b8!important;transform:none!important;box-shadow:none!important;
}}

/* ── Divisor ── */
.adiv {{
    display:flex;align-items:center;gap:10px;
    margin:12px 0;color:#1e3a5f;
    font-size:10px;font-family:'DM Mono',monospace;
}}
.adiv::before,.adiv::after {{
    content:'';flex:1;height:1px;background:#1e3a5f;
}}

/* ── Badges / banners ── */
.badge-pend {{
    display:inline-flex;align-items:center;gap:6px;
    background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.2);
    color:#fbbf24;border-radius:20px;padding:5px 14px;
    font-size:10px;font-weight:600;font-family:'DM Mono',monospace;
    margin-bottom:16px;
}}
.banner-i {{
    background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.18);
    color:#93c5fd;border-radius:10px;padding:10px 14px;
    font-size:12px;line-height:1.55;margin-bottom:16px;
}}
.msg-ok {{
    background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.2);
    color:#86efac;border-radius:10px;padding:10px 14px;
    font-size:12px;margin-bottom:14px;
}}
.msg-err {{
    background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);
    color:#fca5a5;border-radius:10px;padding:10px 14px;
    font-size:12px;margin-bottom:14px;
}}

/* ── Footer ── */
.login-footer {{
    text-align:center;font-size:10px;color:#1e3a5f;
    font-family:'DM Mono',monospace;margin-top:16px;letter-spacing:.5px;
}}

/* Remove padding lateral das colunas */
[data-testid="column"] {{ padding:0 8px!important }}
</style>

<!-- Canvas animado -->
<canvas id="login-canvas"></canvas>

<script>
(function(){{
    function init(){{
        var canvas = document.getElementById('login-canvas');
        if(!canvas) {{ setTimeout(init,200); return; }}
        var ctx = canvas.getContext('2d');
        var W = canvas.width  = window.innerWidth;
        var H = canvas.height = window.innerHeight;
        window.addEventListener('resize', function(){{
            W = canvas.width  = window.innerWidth;
            H = canvas.height = window.innerHeight;
        }});
        var N=65, pts=[];
        for(var i=0;i<N;i++) pts.push({{
            x:Math.random()*W, y:Math.random()*H,
            vx:(Math.random()-.5)*.35,
            vy:(Math.random()-.5)*.35,
            r:Math.random()*1.6+.4
        }});
        function draw(){{
            ctx.clearRect(0,0,W,H);
            for(var i=0;i<N;i++){{
                for(var j=i+1;j<N;j++){{
                    var dx=pts[i].x-pts[j].x, dy=pts[i].y-pts[j].y;
                    var d=Math.sqrt(dx*dx+dy*dy);
                    if(d<130){{
                        ctx.beginPath();
                        ctx.moveTo(pts[i].x,pts[i].y);
                        ctx.lineTo(pts[j].x,pts[j].y);
                        ctx.strokeStyle='rgba(37,99,235,'+(1-d/130)*.15+')';
                        ctx.lineWidth=.5;
                        ctx.stroke();
                    }}
                }}
                ctx.beginPath();
                ctx.arc(pts[i].x,pts[i].y,pts[i].r,0,Math.PI*2);
                ctx.fillStyle='rgba(59,130,246,.45)';
                ctx.fill();
                pts[i].x+=pts[i].vx; pts[i].y+=pts[i].vy;
                if(pts[i].x<0||pts[i].x>W) pts[i].vx*=-1;
                if(pts[i].y<0||pts[i].y>H) pts[i].vy*=-1;
            }}
            requestAnimationFrame(draw);
        }}
        draw();
    }}
    init();

    // Aplica estilos do card e centralização
    function applyStyles() {{
        // Card na coluna do meio
        var cols = document.querySelectorAll('[data-testid="column"]');
        if (cols.length >= 2) {{
            var mid = cols[1];
            mid.style.cssText += [
                'background:#0c1a30!important',
                'border:1.5px solid rgba(37,99,235,0.4)!important',
                'border-radius:18px!important',
                'padding:32px 36px!important',
                'box-shadow:0 4px 48px rgba(0,0,0,0.85),0 0 0 1px rgba(37,99,235,0.15)!important',
                'position:relative!important',
                'z-index:2!important'
            ].join(';');
        }}
        // Centralização vertical
        var bc = document.querySelector('.block-container');
        if (bc) {{
            bc.style.cssText += [
                'display:flex!important',
                'flex-direction:column!important',
                'justify-content:center!important',
                'min-height:100vh!important',
                'padding-top:24px!important',
                'padding-bottom:24px!important'
            ].join(';');
        }}
    }}

    // Aplica imediatamente e via MutationObserver para persistir após re-renders
    applyStyles();
    setTimeout(applyStyles, 500);
    setTimeout(applyStyles, 1500);

    var observer = new MutationObserver(function(mutations) {{
        applyStyles();
    }});
    observer.observe(document.body, {{ childList:true, subtree:true }});
}})();
</script>
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