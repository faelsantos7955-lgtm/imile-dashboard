"""
app.py — Dashboard de Expedição Logística
Streamlit Cloud + Supabase + Login por região
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
from auth_ui import render_auth, logout as auth_logout
import time as _time
from datetime import datetime as _dt
import plotly.express as px
from modulos import reclamacoes as mod_reclamacoes

from processing import (
    normalizar_colunas, construir_mapa_sigla, padronizar_scan_station,
    filtrar_dados, fazer_merge, criar_pivot, criar_pivot_cidades,
    calcular_metricas, separar_por_regiao,
    detectar_coluna_data, ler_datas_recebimento, _ler_uploads, _wb_to_str
)
from database import (
    salvar_processamento, ler_dia, ler_periodo,
    ler_cidades_dia, ler_datas_disponiveis,
    salvar_supervisores, carregar_supervisores, tem_supervisores,
    salvar_metas, carregar_metas, tem_metas,
    carregar_metas_completo, upsert_meta_ds, upsert_metas_bulk,
    get_supabase, invalidar_cache,
    listar_solicitacoes, aprovar_solicitacao, rejeitar_solicitacao, listar_usuarios,
    listar_bases_disponiveis, atualizar_bases_usuario,
    PAGINAS_DISPONIVEIS, PAGINAS_POR_PERFIL,
    atualizar_permissoes_usuario, get_paginas_usuario,
    get_motoristas_status, upsert_motorista_status, listar_motoristas_inativos,
    invalidar_cache_config,
)
from excel_export import exportar_excel_bytes
from modulos import triagem as mod_triagem
from charts import (
    chart_volume_ds, chart_taxa_ds, chart_evolucao_diaria,
    chart_heatmap_cidades, chart_comparativo, chart_donut
)

# ══════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Expedição Logística",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────
import os
_css = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")
if os.path.exists(_css):
    with open(_css) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  LOGIN — Supabase Auth
# ══════════════════════════════════════════════════════════════
if not render_auth():
    st.stop()

# Dados do usuário logado (vindos do session_state)
nome         = st.session_state.get("user_nome", "")
usuario      = st.session_state.get("user_email", "")
is_admin     = st.session_state.get("user_role", "viewer") == "admin"
_bases_raw = st.session_state.get("user_bases") or None
if _bases_raw == [] or _bases_raw == ["all"] or not _bases_raw:
    bases_user = None  # None = vê tudo (admin)
else:
    bases_user = tuple(_bases_raw)  # tuple é hashável para cache

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='padding:16px 0 12px;text-align:center'>
      <div style='font-size:13px;font-weight:600;color:#94a3b8;margin-top:10px'>
        Olá, <span style='color:#fff'>{nome.split()[0] if nome else usuario}</span>
      </div>
      {'<div style="font-size:10px;background:#1d3a7a;color:#60a5fa;padding:3px 10px;border-radius:20px;display:inline-block;margin-top:6px;font-weight:700;letter-spacing:0.5px">● ADMIN</div>' if is_admin else '<div style="font-size:10px;color:#475569;margin-top:4px">Acesso regional</div>'}
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Páginas liberadas para o usuário
    if is_admin:
        _paginas = list(PAGINAS_DISPONIVEIS)
    else:
        _user_id = st.session_state.get("user_id", "")
        _role    = st.session_state.get("user_role", "viewer")
        _paginas = get_paginas_usuario(_user_id, _role)

    if is_admin:
        _paginas.append("👥 Solicitações de Acesso")
        _paginas.append("⚙️ Configurações")
    pagina = st.radio(
        "Navegação", _paginas,
        label_visibility="collapsed"
    )
    st.divider()
    if st.button("🚪 Sair", width='stretch'):
        auth_logout()

# ══════════════════════════════════════════════════════════════
#  PÁGINA: DASHBOARD
# ══════════════════════════════════════════════════════════════
if pagina == "📊 Dashboard":
    col_hdr, col_refresh = st.columns([4, 1])
    with col_hdr:
        st.markdown("""
        <div class="app-header">
          <div class="app-header-icon">📊</div>
          <div><h1>Dashboard</h1>
          <p>Visão consolidada por dia · atualização automática a cada 5 min</p></div>
        </div>""", unsafe_allow_html=True)
    with col_refresh:
        st.markdown("<div style='padding-top:18px'>", unsafe_allow_html=True)
        if st.button("🔄 Atualizar agora", width='stretch'):
            invalidar_cache()
            st.rerun()
        ultimo = st.session_state.get("ultimo_refresh", _dt.now().strftime("%H:%M:%S"))
        st.caption(f"Última atualização: {ultimo}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Auto-refresh a cada 5 minutos via session state
    _agora = _time.time()
    if "next_refresh" not in st.session_state:
        st.session_state["next_refresh"] = _agora + 300
        st.session_state["ultimo_refresh"] = _dt.now().strftime("%H:%M:%S")
    if _agora >= st.session_state["next_refresh"]:
        invalidar_cache()
        st.session_state["next_refresh"] = _agora + 300
        st.session_state["ultimo_refresh"] = _dt.now().strftime("%H:%M:%S")
        st.rerun()

    # ── Carrega datas disponíveis ─────────────────────────────
    datas = ler_datas_disponiveis(bases_user)
    if not datas:
        st.info("Nenhum dado no histórico ainda. Vá para **Upload / Processar** para gerar o primeiro.")
        st.stop()

    # ── Filtros interativos na sidebar ────────────────────────
    with st.sidebar:
        st.markdown('<div class="section-label" style="margin-top:0">Filtros</div>',
                    unsafe_allow_html=True)
        data_sel = st.selectbox(
            "📅 Data",
            options=datas,
            format_func=lambda d: pd.to_datetime(d).strftime("%d/%m/%Y"),
            index=0
        )

        if is_admin:
            reg_filtro = st.multiselect(
                "🌎 Região",
                ["capital","metropolitan","countryside"],
                default=["capital","metropolitan","countryside"])
        else:
            reg_filtro = bases_user

    # ── Carrega dados base ────────────────────────────────────
    df_dia_full = ler_dia(data_sel, bases_user)
    df_cid_full = ler_cidades_dia(data_sel, bases_user)

    if len(df_dia_full) == 0:
        st.warning(f"Sem dados para {pd.to_datetime(data_sel).strftime('%d/%m/%Y')}.")
        st.stop()

    # ── Filtros adicionais: DS ────────────────────────────────
    with st.sidebar:
        todos_ds = sorted(df_dia_full["scan_station"].unique().tolist())
        ds_sel = st.multiselect("🏭 DS", todos_ds, placeholder="Todos")

    df_dia = df_dia_full[df_dia_full["scan_station"].isin(ds_sel)].copy() if ds_sel else df_dia_full.copy()
    df_cid = df_cid_full[df_cid_full["scan_station"].isin(ds_sel)].copy() if ds_sel else df_cid_full.copy()

    # ── Alertas ───────────────────────────────────────────────
    df_alerta = df_dia[df_dia["taxa_exp"] < df_dia["meta"]].copy()
    if len(df_alerta):
        nomes_alerta = ", ".join(df_alerta.sort_values("taxa_exp")["scan_station"].head(5).tolist())
        st.warning(f"⚠️ **{len(df_alerta)} DS abaixo da meta:** {nomes_alerta}"
                   + (" e outros..." if len(df_alerta) > 5 else ""))

    # ── KPIs ──────────────────────────────────────────────────
    rec  = int(df_dia["recebido"].sum())
    exp  = int(df_dia["expedido"].sum())
    ent  = int(df_dia["entregas"].sum())
    tx   = exp / rec if rec else 0
    txe  = ent / rec if rec else 0
    nds  = len(df_dia)
    nok  = int(df_dia["atingiu_meta"].sum())

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card c1">
        <div class="kpi-lbl">Recebido</div>
        <div class="kpi-val">{rec:,}</div>
        <div class="kpi-sub">waybills no dia</div>
      </div>
      <div class="kpi-card c2">
        <div class="kpi-lbl">Em Rota</div>
        <div class="kpi-val">{exp:,}</div>
        <div class="kpi-sub">taxa {tx:.1%}</div>
      </div>
      <div class="kpi-card c3">
        <div class="kpi-lbl">Entregas</div>
        <div class="kpi-val">{ent:,}</div>
        <div class="kpi-sub">{'taxa ' + f'{txe:.1%}' if ent else 'sem dados'}</div>
      </div>
      <div class="kpi-card c4">
        <div class="kpi-lbl">DS na Meta</div>
        <div class="kpi-val">{nok}</div>
        <div class="kpi-sub">de {nds} bases</div>
      </div>
      <div class="kpi-card c5">
        <div class="kpi-lbl">DS Abaixo</div>
        <div class="kpi-val">{nds - nok}</div>
        <div class="kpi-sub">precisam atenção</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Comparativo ontem ─────────────────────────────────────
    ontem = pd.to_datetime(data_sel).date() - timedelta(days=1)
    df_ont = ler_dia(str(ontem), bases_user)
    if len(df_ont):
        if ds_sel:
            df_ont = df_ont[df_ont["scan_station"].isin(ds_sel)]
        rec_ont = int(df_ont["recebido"].sum())
        exp_ont = int(df_ont["expedido"].sum())
        tx_ont  = exp_ont / rec_ont if rec_ont else 0
        d_rec = rec - rec_ont
        d_exp = exp - exp_ont
        d_tx  = tx  - tx_ont
        def _delta(v, fmt=","):
            sinal = "+" if v >= 0 else ""
            cor   = "#16a34a" if v >= 0 else "#dc2626"
            txt   = f"{sinal}{v:{fmt}}" if fmt == "," else f"{sinal}{v:.1%}"
            return f"<span style='color:{cor};font-weight:700'>{txt}</span>"
        st.markdown(f"""
        <div class="delta-row">
          <div class="delta-item">Recebido {_delta(d_rec)} vs ontem</div>
          <div class="delta-item">Expedido {_delta(d_exp)} vs ontem</div>
          <div class="delta-item">Taxa {_delta(d_tx, fmt='%')} vs ontem</div>
        </div>""", unsafe_allow_html=True)

    # ── Gráficos ──────────────────────────────────────────────
    col_a, col_b = st.columns([1.3, 1])
    with col_a:
        st.plotly_chart(chart_volume_ds(df_dia), width='stretch')
    with col_b:
        st.plotly_chart(chart_donut(rec, exp, tx), width='stretch')

    st.plotly_chart(chart_taxa_ds(df_dia), width='stretch')

    if len(df_cid):
        tem_entregas = df_cid["entregas"].sum() > 0
        if tem_entregas:
            col_c, col_d = st.columns(2)
            with col_c:
                st.plotly_chart(chart_heatmap_cidades(df_cid, "taxa_exp"), width='stretch')
            with col_d:
                st.plotly_chart(chart_heatmap_cidades(df_cid, "taxa_ent"), width='stretch')
        else:
            st.plotly_chart(chart_heatmap_cidades(df_cid, "taxa_exp"), width='stretch')
            st.caption("ℹ️ Mapa de Taxa de Entrega não exibido — sem dados de entregas para este dia.")

    # ── Ranking DS ────────────────────────────────────────────
    st.markdown('<div class="section-label">Ranking por Taxa de Expedição</div>',
                unsafe_allow_html=True)
    df_rank = df_dia[["scan_station","region","recebido","expedido","entregas",
                       "taxa_exp","taxa_ent","meta","atingiu_meta"]].copy()
    df_rank = df_rank.sort_values("taxa_exp", ascending=True).reset_index(drop=True)
    df_rank.insert(0, "Pos.", range(1, len(df_rank)+1))
    df_rank.insert(1, "⚠️", df_rank["atingiu_meta"].apply(lambda v: "" if v else "⚠️"))
    df_rank.columns = ["Pos.","⚠️","DS","Região","Recebido","Expedido","Entregas",
                        "Taxa Exp.","Taxa Ent.","Meta","Na Meta"]
    df_rank["Taxa Exp."] = df_rank["Taxa Exp."].map("{:.1%}".format)
    df_rank["Taxa Ent."] = df_rank["Taxa Ent."].map("{:.1%}".format)
    df_rank["Meta"]      = df_rank["Meta"].apply(
        lambda v: f"{float(v):.0%}" if pd.notna(v) and float(v) <= 1.0 else f"{float(v):.0f}%")
    df_rank = df_rank.drop(columns=["Na Meta"])

    def _colorir_linha(row):
        cor = "#fff1f2" if row["⚠️"] == "⚠️" else ""
        return [f"background-color: {cor}" for _ in row]

    st.dataframe(
        df_rank.style.apply(_colorir_linha, axis=1),
        width='stretch', hide_index=True
    )

    # ── Meta dinâmica por DS (só admin) ───────────────────────
    if is_admin:
        with st.expander("🎯 Metas por DS", expanded=False):
            st.caption("Configure a meta individual de cada base. As mudanças valem para os próximos processamentos.")

            df_metas_db = carregar_metas_completo()
            # Monta tabela com todas as DS do dia + metas salvas
            ds_hoje = sorted(df_dia["scan_station"].unique().tolist())
            meta_map = {}
            if len(df_metas_db) > 0:
                meta_map = df_metas_db.set_index("DS")["Meta (%)"].to_dict()

            # ── Editor rápido — uma DS por vez ────────────────
            st.markdown("**Edição rápida**")
            ce1, ce2, ce3 = st.columns([2, 1, 1])
            with ce1:
                ds_edit = st.selectbox("Base (DS)", ds_hoje, key="ds_meta_sel")
            with ce2:
                meta_atual = meta_map.get(ds_edit, 50.0)
                nova_meta  = st.number_input("Meta (%)", min_value=1, max_value=100,
                                              value=int(meta_atual), step=1, key="meta_edit_v2")
            with ce3:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.button("💾 Salvar", key="btn_meta_rapido"):
                    ok, err = upsert_meta_ds(ds_edit, float(nova_meta), usuario)
                    if ok:
                        st.success(f"✅ Meta de **{ds_edit}** → **{nova_meta}%**")
                        st.rerun()
                    else:
                        st.error(f"Erro: {err}")

            st.divider()

            # ── Tabela completa editável ───────────────────────
            st.markdown("**Todas as metas salvas**")
            if len(df_metas_db) > 0:
                # Mostra tabela com st.data_editor para edição em massa
                df_edit = df_metas_db[["DS","Meta (%)"]].copy()
                df_edit["Meta (%)"] = df_edit["Meta (%)"].astype(float)
                edited = st.data_editor(
                    df_edit,
                    column_config={
                        "DS":       st.column_config.TextColumn("Base", disabled=True),
                        "Meta (%)": st.column_config.NumberColumn(
                            "Meta (%)", min_value=1, max_value=100,
                            step=1, format="%d%%"
                        ),
                    },
                    hide_index=True,
                    width='stretch',
                    key="editor_metas_bulk",
                )
                if st.button("💾 Salvar todas", key="btn_meta_bulk"):
                    rows = [{"ds": row["DS"], "meta_pct": row["Meta (%)"]}
                            for _, row in edited.iterrows()]
                    ok, err = upsert_metas_bulk(rows, usuario)
                    if ok:
                        st.success(f"✅ {len(rows)} metas atualizadas!")
                        st.rerun()
                    else:
                        st.error(f"Erro: {err}")

                # Resumo visual
                st.divider()
                c1, c2, c3 = st.columns(3)
                c1.metric("Total configuradas", len(df_metas_db))
                c2.metric("Meta mais alta", f"{df_metas_db['Meta (%)'].max():.0f}%")
                c3.metric("Meta mais baixa", f"{df_metas_db['Meta (%)'].min():.0f}%")

                st.caption("🕐 Última edição: " +
                    df_metas_db.sort_values("Atualizado em", ascending=False)
                    .iloc[0][["Editado por","Atualizado em"]]
                    .to_list().__str__().strip("[]").replace("'",""))
            else:
                st.info("Nenhuma meta configurada ainda. Use a edição rápida acima ou suba um arquivo Excel em Upload / Processar.")

# ══════════════════════════════════════════════════════════════
#  PÁGINA: UPLOAD / PROCESSAR
# ══════════════════════════════════════════════════════════════
elif pagina == "📤 Upload / Processar":
    if not is_admin:
        st.error("🔒 Acesso restrito ao administrador.")
        st.stop()
    st.markdown("""
    <div class="app-header">
      <div class="app-header-icon">📤</div>
      <div><h1>Upload e Processamento</h1>
      <p>Carregue os arquivos do dia · Processe · Salva automaticamente no histórico</p></div>
    </div>""", unsafe_allow_html=True)

    _tem_sup  = tem_supervisores()
    _tem_meta = tem_metas()

    st.markdown('<div class="section-label">Arquivos de entrada</div>', unsafe_allow_html=True)

    # Aviso se arquivos fixos já estão salvos
    if _tem_sup and _tem_meta:
        st.success("✅ Supervisores e Metas já salvos no banco — não precisa subir novamente. Gerencie em ⚙️ Configurações.")
    elif _tem_sup:
        st.info("✅ Supervisores já salvos. Metas ainda não configuradas — você pode subir abaixo ou em ⚙️ Configurações.")
    elif _tem_meta:
        st.info("✅ Metas já salvas. Supervisores ainda não configurados — suba o arquivo abaixo.")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="upload-label">Recebimento <span class="badge-r">OBRIGATÓRIO</span></div>'
                    '<div class="upload-hint">todos os arquivos da pasta — precisa ter coluna de data</div>',
                    unsafe_allow_html=True)
        f_rec = st.file_uploader("rec", type=["xlsx","xls"], key="rec",
                                  accept_multiple_files=True, label_visibility="collapsed")
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        st.markdown('<div class="upload-label">Out of Delivery <span class="badge-r">OBRIGATÓRIO</span></div>'
                    '<div class="upload-hint">todos os arquivos da pasta</div>',
                    unsafe_allow_html=True)
        f_out = st.file_uploader("out", type=["xlsx","xls"], key="out",
                                  accept_multiple_files=True, label_visibility="collapsed")

    with col2:
        st.markdown('<div class="upload-label">Entregas <span class="badge-o">OPCIONAL</span></div>'
                    '<div class="upload-hint">todos os arquivos da pasta</div>',
                    unsafe_allow_html=True)
        f_ent = st.file_uploader("ent", type=["xlsx","xls"], key="ent",
                                  accept_multiple_files=True, label_visibility="collapsed")
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        if not _tem_sup:
            st.markdown('<div class="upload-label">Supervisores <span class="badge-r">OBRIGATÓRIO (1ª vez)</span></div>'
                        '<div class="upload-hint">arquivo único — colunas: SIGLA, REGION</div>',
                        unsafe_allow_html=True)
            f_sup = st.file_uploader("sup", type=["xlsx","xls"], key="sup", label_visibility="collapsed")
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        else:
            f_sup = None

        if not _tem_meta:
            st.markdown('<div class="upload-label">Metas por Base <span class="badge-o">OPCIONAL (1ª vez)</span></div>'
                        '<div class="upload-hint">arquivo único — colunas: DS, Meta</div>',
                        unsafe_allow_html=True)
            f_meta = st.file_uploader("meta", type=["xlsx","xls"], key="meta", label_visibility="collapsed")
        else:
            f_meta = None

    # ── Detecção de data ──────────────────────────────────────
    data_selecionada = None
    col_data_nome    = None

    if f_rec:
        st.markdown('<div class="section-label">Selecione a data</div>', unsafe_allow_html=True)
        with st.spinner("Detectando datas..."):
            col_data_nome = detectar_coluna_data(f_rec[0])
            datas_disp    = ler_datas_recebimento(f_rec, col_data_nome) if col_data_nome else []

        if col_data_nome and datas_disp:
            st.success(f"Coluna de data: **{col_data_nome}** — {len(datas_disp)} dia(s) disponível(is)")
            data_selecionada = st.selectbox(
                "Dia para processar:",
                options=datas_disp,
                format_func=lambda d: d.strftime("%d/%m/%Y (%A)"),
                index=len(datas_disp)-1
            )
        else:
            st.warning("Coluna de data não encontrada. Todos os registros serão usados.")

    # ── Botão processar ───────────────────────────────────────
    st.markdown('<div class="section-label">Processar</div>', unsafe_allow_html=True)
    pronto    = bool(_tem_sup or f_sup) and bool(f_rec) and bool(f_out)
    data_lbl  = data_selecionada.strftime("%d/%m/%Y") if data_selecionada else "todos os dias"
    if not pronto:
        st.info("Faça o upload dos 3 arquivos obrigatórios.")

    if st.button(f"▶  PROCESSAR E SALVAR — {data_lbl}", disabled=not pronto, width='stretch'):
        prog = st.progress(0, text="Iniciando...")
        try:
            prog.progress(8,  "Carregando arquivos...")
            cols_rec = {"Scan Station":"Scan Station","Waybill Number":"Waybill Number",
                        "Destination City":"Destination City"}
            if col_data_nome:
                cols_rec[col_data_nome] = col_data_nome
            cols_out = {"Waybill No.":"Waybill No.","Scan time":"Scan time"}

            # Supervisores — usa arquivo novo ou carrega do banco
            if f_sup:
                df_sup = normalizar_colunas(pd.read_excel(f_sup), {"SIGLA":"SIGLA","REGION":"REGION"})
                salvar_supervisores(df_sup, usuario)
                st.toast("✅ Supervisores salvos no banco!", icon="💾")
            else:
                df_sup = carregar_supervisores()
            df_rec = _ler_uploads(f_rec, cols_rec)
            df_out = _ler_uploads(f_out, cols_out)

            # Filtro por data
            prog.progress(18, "Filtrando por data...")
            if data_selecionada and col_data_nome and col_data_nome in df_rec.columns:
                df_rec[col_data_nome] = pd.to_datetime(df_rec[col_data_nome], errors="coerce")
                df_rec = df_rec[df_rec[col_data_nome].dt.date == data_selecionada].copy()
                if len(df_rec) == 0:
                    st.error("Nenhum registro para a data selecionada.")
                    st.stop()

            if "Scan Station" not in df_out.columns:
                wb_to_ss = (df_rec[["Waybill Number","Scan Station"]]
                            .dropna(subset=["Waybill Number","Scan Station"])
                            .drop_duplicates("Waybill Number")
                            .rename(columns={"Waybill Number":"Waybill No."}))
                df_out = df_out.merge(wb_to_ss, on="Waybill No.", how="left")

            df_ent  = _ler_uploads(f_ent,  {"Scan Station":"Scan Station","Waybill No.":"Waybill No."}) if f_ent  else None
            df_meta = None
            if f_meta:
                df_meta = normalizar_colunas(pd.read_excel(f_meta), {"DS":"DS","Meta":"Meta"})
                df_meta["DS"] = df_meta["DS"].astype(str).str.strip()
                # Salva no banco para próximas vezes
                _meta_tmp = df_meta.copy()
                # Lê o valor bruto — Excel já guarda % como decimal (0.795 = 79,5%)
                # Se vier como string "79,5%" converte manualmente
                meta_raw = df_meta["Meta"]
                # Tenta ler direto (caso Excel já seja decimal 0.xx)
                meta_num = pd.to_numeric(meta_raw, errors="coerce")
                # Se algum valor veio como string com % ou vírgula, converte
                if meta_num.isna().any() or (meta_raw.astype(str).str.contains("%", na=False).any()):
                    meta_str = (meta_raw.astype(str)
                                .str.replace("%", "", regex=False)
                                .str.replace(",", ".", regex=False)
                                .str.strip())
                    meta_num = pd.to_numeric(meta_str, errors="coerce")
                    # Valores > 1 vieram como 79.5 → divide por 100
                    meta_num = meta_num.where(meta_num <= 1.0, meta_num / 100)
                else:
                    # Valores já decimais — se algum > 1 também divide
                    meta_num = meta_num.where(meta_num <= 1.0, meta_num / 100)
                df_meta["Meta"] = meta_num.fillna(0.5)
                _meta_tmp["Meta"] = df_meta["Meta"]
                salvar_metas(_meta_tmp, usuario)
                st.toast("✅ Metas atualizadas no banco!", icon="💾")
            elif tem_metas():
                df_meta = carregar_metas()

            prog.progress(32, "Padronizando Scan Stations...")
            mapa    = construir_mapa_sigla(df_sup)
            df_rec  = filtrar_dados(df_sup, df_rec, mapa)
            df_out  = padronizar_scan_station(df_out, mapa)
            if df_ent is not None:
                df_ent = padronizar_scan_station(df_ent, mapa)

            prog.progress(48, "Calculando volumes por Waybill...")
            df_merge      = fazer_merge(df_sup, df_rec)
            pivot         = criar_pivot(df_merge, df_out, df_ent)
            pivot_cidades = criar_pivot_cidades(df_merge, df_out, df_ent)

            prog.progress(65, "Calculando métricas...")
            pivot_m = calcular_metricas(pivot, df_meta)

            prog.progress(80, "Salvando no histórico (Supabase)...")
            salvar_processamento(
                pivot_metricas=pivot_m,
                pivot_cidades=pivot_cidades,
                data_ref=data_selecionada or date.today(),
                usuario=usuario
            )

            prog.progress(92, "Gerando Excel para download...")
            pivot_full2, df_cap2, df_met2, df_cou2 = separar_por_regiao(df_merge, pivot_m)
            exc_cols  = {"SIGLA", "_count"}
            base_cols = [c for c in df_merge.columns if c not in exc_cols]
            data_str  = data_selecionada.strftime("%d-%m-%Y") if data_selecionada else ""
            excel_bytes = exportar_excel_bytes(
                base=df_merge[base_cols].copy(),
                geral=pivot_full2, capital=df_cap2,
                metro=df_met2,    country=df_cou2,
                pivot_cidades=pivot_cidades,
                data_str=data_str
            )
            st.session_state["excel_bytes"]    = excel_bytes
            st.session_state["excel_filename"] = f"Dashboard_Expedicao_{data_str}.xlsx" if data_str else "Dashboard_Expedicao.xlsx"

            prog.progress(100, "Concluído!")

            # ── Resumo ────────────────────────────────────────
            rec_t = int(pivot_m["recebido no DS"].sum())
            exp_t = int(pivot_m["em rota de entrega"].sum())
            ent_t = int(pivot_m["Entregas"].sum())
            tx_t  = exp_t / rec_t if rec_t else 0
            n_ds  = len(pivot_m)
            n_ok  = int(pivot_m["Atingiu Meta"].sum())

            st.success(f"✅ Processamento salvo para **{data_lbl}**")
            st.markdown(f"""
            <div class="kpi-grid">
              <div class="kpi-card c1"><div class="kpi-lbl">Recebido</div>
                <div class="kpi-val">{rec_t:,}</div></div>
              <div class="kpi-card c2"><div class="kpi-lbl">Expedido</div>
                <div class="kpi-val">{exp_t:,}</div>
                <div class="kpi-sub">taxa {tx_t:.1%}</div></div>
              <div class="kpi-card c3"><div class="kpi-lbl">Entregas</div>
                <div class="kpi-val">{ent_t:,}</div></div>
              <div class="kpi-card c4"><div class="kpi-lbl">DS na Meta</div>
                <div class="kpi-val">{n_ok}/{n_ds}</div></div>
              <div class="kpi-card c5"><div class="kpi-lbl">DS Abaixo</div>
                <div class="kpi-val">{n_ds-n_ok}</div></div>
            </div>""", unsafe_allow_html=True)
            st.info("Vá para **📊 Dashboard** para ver os gráficos completos.")

        except Exception as e:
            import traceback
            prog.progress(0, "Erro")
            st.error(f"Erro: {e}")
            with st.expander("Detalhes"):
                st.code(traceback.format_exc())

    # ── Download Excel (persiste após processamento) ──────────
    if "excel_bytes" in st.session_state:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Download Excel</div>', unsafe_allow_html=True)
        st.download_button(
            label="⬇️  Baixar Dashboard Excel",
            data=st.session_state["excel_bytes"],
            file_name=st.session_state.get("excel_filename", "Dashboard_Expedicao.xlsx"),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch',
        )

# ══════════════════════════════════════════════════════════════
#  PÁGINA: HISTÓRICO
# ══════════════════════════════════════════════════════════════
elif pagina == "📅 Histórico":
    st.markdown("""
    <div class="app-header">
      <div class="app-header-icon">📅</div>
      <div><h1>Histórico</h1>
      <p>Todos os dias processados</p></div>
    </div>""", unsafe_allow_html=True)

    col_i, col_f, _ = st.columns([2, 2, 4])
    with col_i:
        d_ini = st.date_input("De", value=date.today() - timedelta(days=30))
    with col_f:
        d_fim = st.date_input("Até", value=date.today())

    df_hist = ler_periodo(d_ini, d_fim, bases_user if not is_admin else None)

    if len(df_hist) == 0:
        st.info("Nenhum dado no período selecionado.")
        st.stop()

    # ── Resumo do período ─────────────────────────────────────
    agg = (df_hist.groupby("data_ref", as_index=False)
                  .agg(recebido=("recebido","sum"),
                       expedido=("expedido","sum"),
                       entregas=("entregas","sum")))
    agg["taxa_exp"] = agg["expedido"] / agg["recebido"].replace(0, np.nan)

    rec_per = int(agg["recebido"].sum())
    exp_per = int(agg["expedido"].sum())
    tx_per  = exp_per / rec_per if rec_per else 0
    dias    = len(agg)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Recebido",  f"{rec_per:,}")
    c2.metric("Total Expedido",  f"{exp_per:,}")
    c3.metric("Taxa Média",      f"{tx_per:.1%}")
    c4.metric("Dias no período", dias)

    st.plotly_chart(chart_evolucao_diaria(df_hist), width='stretch')

    # ── Tabela por dia ────────────────────────────────────────
    st.markdown('<div class="section-label">Resumo por dia</div>', unsafe_allow_html=True)
    agg["Taxa"]     = agg["taxa_exp"].map("{:.1%}".format)
    agg["data_ref"] = pd.to_datetime(agg["data_ref"]).dt.strftime("%d/%m/%Y")
    agg.columns     = ["Data","Recebido","Expedido","Entregas","taxa_exp","Taxa Exp."]
    st.dataframe(agg[["Data","Recebido","Expedido","Entregas","Taxa Exp."]],
                 width='stretch', hide_index=True)

    # ── Download Excel do período ─────────────────────────────
    st.markdown('<div class="section-label">Download do período</div>', unsafe_allow_html=True)

    if st.button("📥  Gerar Excel do período", width='stretch', key="btn_excel_hist"):
        with st.spinner("Gerando Excel..."):
            try:
                # Monta pivot a partir do histórico agregado por DS
                pivot_hist = df_hist.rename(columns={
                    "scan_station":  "Scan Station",
                    "region":        "REGION",
                    "recebido":      "Recebido",
                    "expedido":      "Expedido",
                    "entregas":      "Entregas",
                    "taxa_exp":      "Taxa de Expedicao",
                    "taxa_ent":      "Taxa de Entrega",
                    "meta":          "Meta",
                    "atingiu_meta":  "Atingiu Meta",
                })
                # Agrega o período todo por DS
                agg_ds = (pivot_hist.groupby(["Scan Station","REGION"], as_index=False)
                          .agg(Recebido=("Recebido","sum"),
                               Expedido=("Expedido","sum"),
                               Entregas=("Entregas","sum"),
                               Meta=("Meta","mean")))
                agg_ds["recebido no DS"]     = agg_ds["Recebido"]
                agg_ds["em rota de entrega"] = agg_ds["Expedido"]
                agg_ds["Total Geral"]        = agg_ds["Recebido"]
                agg_ds["Taxa de Expedicao"]  = np.where(agg_ds["Recebido"]>0,
                    agg_ds["Expedido"]/agg_ds["Recebido"], 0.0)
                agg_ds["Taxa de Entrega"]    = np.where(agg_ds["Recebido"]>0,
                    (agg_ds["Entregas"]/agg_ds["Recebido"]).clip(upper=1.0), 0.0)
                agg_ds["Atingiu Meta"]       = agg_ds["Taxa de Expedicao"] >= agg_ds["Meta"]

                def _fr(r):
                    return agg_ds[agg_ds["REGION"].str.lower()==r].reset_index(drop=True)

                data_str_hist = f"{d_ini.strftime('%d-%m-%Y')}_a_{d_fim.strftime('%d-%m-%Y')}"
                excel_hist = exportar_excel_bytes(
                    base=agg_ds[["Scan Station","REGION","Recebido","Expedido","Entregas",
                                  "Taxa de Expedicao","Taxa de Entrega"]].copy(),
                    geral=agg_ds, capital=_fr("capital"),
                    metro=_fr("metropolitan"), country=_fr("countryside"),
                    pivot_cidades=None,
                    data_str=data_str_hist
                )
                st.session_state["excel_hist_bytes"]    = excel_hist
                st.session_state["excel_hist_filename"] = f"Historico_{data_str_hist}.xlsx"
                st.success("Excel gerado!")
            except Exception as e:
                st.error(f"Erro ao gerar Excel: {e}")

    if "excel_hist_bytes" in st.session_state:
        st.download_button(
            label="⬇️  Baixar Excel do período",
            data=st.session_state["excel_hist_bytes"],
            file_name=st.session_state.get("excel_hist_filename","Historico.xlsx"),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch',
            key="dl_excel_hist"
        )

# ══════════════════════════════════════════════════════════════
#  PÁGINA: COMPARATIVOS
# ══════════════════════════════════════════════════════════════
elif pagina == "📈 Comparativos":
    st.markdown("""
    <div class="app-header">
      <div class="app-header-icon">📈</div>
      <div><h1>Comparativos</h1>
      <p>Evolução por dia, semana e mês</p></div>
    </div>""", unsafe_allow_html=True)

    col_i, col_f, _ = st.columns([2, 2, 4])
    with col_i:
        d_ini = st.date_input("De", value=date.today() - timedelta(days=90), key="ci")
    with col_f:
        d_fim = st.date_input("Até", value=date.today(), key="cf")

    df_hist = ler_periodo(d_ini, d_fim, bases_user if not is_admin else None)
    if len(df_hist) == 0:
        st.info("Nenhum dado no período.")
        st.stop()

    # Filtro de DS (opcional)
    ds_lista = sorted(df_hist["scan_station"].unique().tolist())
    ds_sel   = st.multiselect("Filtrar por DS (deixe vazio = todos)", ds_lista)
    if ds_sel:
        df_hist = df_hist[df_hist["scan_station"].isin(ds_sel)]

    # Tabs por período
    tab_d, tab_s, tab_m = st.tabs(["📅 Diário", "📆 Semanal", "🗓️ Mensal"])
    with tab_d:
        st.plotly_chart(chart_comparativo(df_hist, "dia"),    width='stretch')
    with tab_s:
        st.plotly_chart(chart_comparativo(df_hist, "semana"), width='stretch')
    with tab_m:
        st.plotly_chart(chart_comparativo(df_hist, "mes"),    width='stretch')

    st.divider()

    # Taxa por DS ao longo do tempo
    st.markdown('<div class="section-label">Evolução por DS</div>', unsafe_allow_html=True)
    ds_top = (df_hist.groupby("scan_station")["recebido"].sum()
              .nlargest(10).index.tolist())
    df_top = df_hist[df_hist["scan_station"].isin(ds_top)].copy()
    df_top["data_ref"] = pd.to_datetime(df_top["data_ref"])

    fig = px.line(
        df_top.sort_values("data_ref"),
        x="data_ref", y="taxa_exp", color="scan_station",
        labels={"data_ref":"Data","taxa_exp":"Taxa Exp.","scan_station":"DS"},
        color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_layout(
        paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
        font=dict(color="#e2e8f0"), height=420,
        yaxis=dict(tickformat=".0%", gridcolor="#334155"),
        xaxis=dict(gridcolor="#334155"),
        legend=dict(bgcolor="#1e293b", bordercolor="#334155"))
    fig.add_hline(y=0.5, line_dash="dash", line_color="#64748b",
                  annotation_text="Meta 50%")
    st.plotly_chart(fig, width='stretch')

# ══════════════════════════════════════════════════════════════
#  PÁGINA: TRIAGEM DC×DS
# ══════════════════════════════════════════════════════════════
elif pagina == "🔀 Triagem DC×DS":
    mod_triagem.render(usuario, is_admin=is_admin)

# ══════════════════════════════════════════════════════════════
#  PÁGINA: SOLICITAÇÕES DE ACESSO (somente admin)
# ══════════════════════════════════════════════════════════════
elif pagina == "📋 Reclamações":
    mod_reclamacoes.render(is_admin=is_admin)

elif pagina == "👥 Solicitações de Acesso":
    if not is_admin:
        st.error("🔒 Acesso restrito ao administrador.")
        st.stop()

    st.markdown("""
    <div class="app-header">
      <div class="app-header-icon">👥</div>
      <div><h1>Solicitações de Acesso</h1>
      <p>Aprove ou rejeite pedidos de acesso ao portal</p></div>
    </div>""", unsafe_allow_html=True)

    tab_pend, tab_hist, tab_users = st.tabs(
        ["⏳ Pendentes", "📋 Histórico", "👤 Usuários ativos"])

    with tab_pend:
        sols = listar_solicitacoes("pendente")
        if not sols:
            st.success("✅ Nenhuma solicitação pendente!")
        else:
            st.info(f"**{len(sols)}** solicitação(ões) aguardando aprovação")
            for s in sols:
                with st.container():
                    st.markdown(f"""
                    <div style='background:#fff;border:1px solid #e2e8f0;border-radius:12px;
                    padding:20px 24px;margin-bottom:12px;box-shadow:0 1px 4px rgba(0,0,0,0.05)'>
                      <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                        <div>
                          <div style='font-size:16px;font-weight:700;color:#0f172a'>{s.get('nome','—')}</div>
                          <div style='font-size:13px;color:#64748b;margin-top:2px'>{s.get('email','—')} · {s.get('empresa','—')}</div>
                          <div style='font-size:12px;color:#94a3b8;margin-top:4px'>
                            Região: <b>{s.get('regiao','—')}</b> · 
                            Solicitado em: {str(s.get('criado_em',''))[:10]}
                          </div>
                          <div style='font-size:13px;color:#475569;margin-top:8px;
                          background:#f8fafc;padding:8px 12px;border-radius:8px'>
                            "{s.get('motivo','')}"
                          </div>
                        </div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                    col_role, col_apr, col_rej = st.columns([2, 1, 1])
                    with col_role:
                        role_sel = st.selectbox(
                            "Permissão", ["viewer","admin"],
                            key=f"role_{s['id']}",
                            format_func=lambda r: "Visualizador" if r=="viewer" else "Administrador"
                        )
                    with col_apr:
                        if st.button("✅ Aprovar", key=f"apr_{s['id']}",
                                      width='stretch'):
                            ok, err = aprovar_solicitacao(
                                s["id"], s["email"], s["nome"],
                                s.get("regiao",""), role_sel)
                            if ok:
                                listar_solicitacoes.clear()
                                listar_usuarios.clear()
                                st.success(f"✅ {s['nome']} aprovado! Email de convite enviado.")
                                st.rerun()
                            else:
                                st.error(f"Erro: {err}")
                    with col_rej:
                        if st.button("❌ Rejeitar", key=f"rej_{s['id']}",
                                      width='stretch'):
                            ok, err = rejeitar_solicitacao(s["id"])
                            if ok:
                                listar_solicitacoes.clear()
                                st.warning(f"Solicitação de {s['nome']} rejeitada.")
                                st.rerun()
                            else:
                                st.error(f"Erro: {err}")
                    st.markdown("<hr style='border-color:#f1f5f9;margin:4px 0 16px'>",
                                unsafe_allow_html=True)

    with tab_hist:
        for status, label in [("aprovado","✅ Aprovados"), ("rejeitado","❌ Rejeitados")]:
            hist = listar_solicitacoes(status)
            if hist:
                st.markdown(f'<div class="section-label">{label}</div>',
                            unsafe_allow_html=True)
                df_hist_s = pd.DataFrame(hist)[
                    ["nome","email","empresa","regiao","criado_em"]]
                df_hist_s.columns = ["Nome","Email","Empresa","Região","Solicitado em"]
                df_hist_s["Solicitado em"] = pd.to_datetime(
                    df_hist_s["Solicitado em"]).dt.strftime("%d/%m/%Y")
                st.dataframe(df_hist_s, width='stretch', hide_index=True)

    with tab_users:
        users = listar_usuarios()
        if not users:
            st.info("Nenhum usuário cadastrado ainda.")
        else:
            bases_disp = listar_bases_disponiveis()

            ROLES = ["viewer", "operador", "supervisor", "admin"]
            ROLE_LABELS = {
                "viewer":     "👁️ Viewer — só Dashboard e Histórico",
                "operador":   "🔧 Operador — Dashboard, Triagem, Upload",
                "supervisor": "📋 Supervisor — Dashboard, Histórico, Comparativos, Reclamações",
                "admin":      "🔑 Admin — acesso total",
            }

            for u in users:
                uid          = u.get("id","")
                nome         = u.get("nome","") or u.get("email","")
                email        = u.get("email","")
                role         = u.get("role","viewer")
                bases_atuais = u.get("bases") or []
                pags_atuais  = u.get("paginas") or []
                ativo        = u.get("ativo", True)

                badge = "🟢" if ativo else "🔴"
                with st.expander(f"{badge} **{nome}** · {email} · `{role}`"):

                    # ── Perfil base ───────────────────────────
                    st.markdown("**Perfil de acesso**")
                    novo_role = st.selectbox(
                        "Perfil",
                        ROLES,
                        index=ROLES.index(role) if role in ROLES else 0,
                        format_func=lambda r: ROLE_LABELS.get(r, r),
                        key=f"role_{uid}"
                    )

                    # Páginas padrão do perfil selecionado
                    pags_perfil = PAGINAS_POR_PERFIL.get(novo_role, PAGINAS_POR_PERFIL["viewer"])

                    st.divider()

                    # ── Páginas ───────────────────────────────
                    st.markdown("**Páginas liberadas**")
                    st.caption(f"Perfil `{novo_role}` libera por padrão: {', '.join(pags_perfil)}")
                    usar_custom_pags = st.checkbox(
                        "Personalizar páginas (sobrepõe o perfil)",
                        value=bool(pags_atuais),
                        key=f"custom_pag_{uid}"
                    )
                    if usar_custom_pags:
                        novas_pags = st.multiselect(
                            "Páginas visíveis",
                            options=PAGINAS_DISPONIVEIS,
                            default=[p for p in pags_atuais if p in PAGINAS_DISPONIVEIS] or pags_perfil,
                            key=f"pags_{uid}"
                        )
                    else:
                        novas_pags = []  # usa perfil base

                    st.divider()

                    # ── Bases ─────────────────────────────────
                    st.markdown("**Bases (DS) visíveis**")
                    acesso_total = st.checkbox(
                        "Acesso total (todas as bases)",
                        value=len(bases_atuais) == 0,
                        key=f"total_{uid}"
                    )
                    if not acesso_total:
                        novas_bases = st.multiselect(
                            "Bases liberadas",
                            options=bases_disp,
                            default=[b for b in bases_atuais if b in bases_disp],
                            placeholder="Selecione as bases...",
                            key=f"bases_{uid}"
                        )
                    else:
                        novas_bases = []

                    st.divider()

                    # ── Status ────────────────────────────────
                    novo_ativo = st.checkbox("Usuário ativo", value=ativo, key=f"ativo_{uid}")

                    if st.button("💾 Salvar permissões", key=f"salvar_{uid}", width='stretch'):
                        ok, err = atualizar_permissoes_usuario(
                            uid, novas_bases, novas_pags,
                            novo_role, usuario, novo_ativo
                        )
                        if ok:
                            st.success(f"✅ Permissões de **{nome}** atualizadas!")
                            st.rerun()
                        else:
                            st.error(f"Erro: {err}")

# ══════════════════════════════════════════════════════════════
#  PÁGINA: CONFIGURAÇÕES (somente admin)
# ══════════════════════════════════════════════════════════════
elif pagina == "⚙️ Configurações":
    if not is_admin:
        st.error("🔒 Acesso restrito ao administrador.")
        st.stop()
    st.markdown("""
    <div class="app-header">
      <div class="app-header-icon">⚙️</div>
      <div><h1>Configurações</h1>
      <p>Gerencie os arquivos fixos — Supervisores e Metas</p></div>
    </div>""", unsafe_allow_html=True)

    tab_sup, tab_meta = st.tabs(["👥 Supervisores", "🎯 Metas por DS"])

    # ── Aba Supervisores ──────────────────────────────────────
    with tab_sup:
        st.markdown('<div class="section-label">Supervisores cadastrados</div>',
                    unsafe_allow_html=True)
        df_sup_atual = carregar_supervisores()
        if len(df_sup_atual):
            st.success(f"✅ {len(df_sup_atual)} bases cadastradas no banco")
            col_t, col_b = st.columns([3, 1])
            with col_t:
                st.dataframe(df_sup_atual, width='stretch', hide_index=True)
            with col_b:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                # Botão para limpar
                if st.button("🗑️ Limpar supervisores", width='stretch', type="secondary"):
                    sb = get_supabase()
                    sb.table("config_supervisores").delete().neq("id", 0).execute()
                    st.success("Supervisores removidos. Suba um novo arquivo na próxima vez.")
                    st.rerun()
        else:
            st.warning("Nenhum supervisor salvo ainda. Suba o arquivo na página de Upload.")

        st.markdown('<div class="section-label">Atualizar supervisores</div>',
                    unsafe_allow_html=True)
        st.caption("Suba um novo arquivo para substituir os dados atuais.")
        f_sup_cfg = st.file_uploader(
            "Novo arquivo de supervisores", type=["xlsx","xls"],
            key="sup_cfg", label_visibility="visible")
        if f_sup_cfg and st.button("💾 Salvar supervisores", width='stretch'):
            with st.spinner("Salvando..."):
                try:
                    df_new = normalizar_colunas(
                        pd.read_excel(f_sup_cfg), {"SIGLA":"SIGLA","REGION":"REGION"})
                    salvar_supervisores(df_new, usuario)
                    st.success(f"✅ {len(df_new)} supervisores salvos com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Aba Metas ─────────────────────────────────────────────
    with tab_meta:
        st.markdown('<div class="section-label">Metas cadastradas</div>',
                    unsafe_allow_html=True)
        df_meta_atual = carregar_metas()
        if len(df_meta_atual):
            st.success(f"✅ {len(df_meta_atual)} bases com meta cadastrada")
            df_meta_show = df_meta_atual.copy()
            df_meta_show["Meta"] = df_meta_show["Meta"].map("{:.1%}".format)
            col_t2, col_b2 = st.columns([3, 1])
            with col_t2:
                st.dataframe(df_meta_show, width='stretch', hide_index=True)
            with col_b2:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Limpar metas", width='stretch', type="secondary"):
                    sb = get_supabase()
                    sb.table("config_metas").delete().neq("id", 0).execute()
                    st.success("Metas removidas.")
                    st.rerun()
        else:
            st.warning("Nenhuma meta salva ainda. Suba o arquivo abaixo ou na página de Upload.")

        st.markdown('<div class="section-label">Atualizar metas</div>',
                    unsafe_allow_html=True)
        st.caption("Suba um novo arquivo para substituir as metas atuais.")
        f_meta_cfg = st.file_uploader(
            "Novo arquivo de metas", type=["xlsx","xls"],
            key="meta_cfg", label_visibility="visible")
        if f_meta_cfg and st.button("💾 Salvar metas", width='stretch'):
            with st.spinner("Salvando..."):
                try:
                    df_new = normalizar_colunas(
                        pd.read_excel(f_meta_cfg), {"DS":"DS","Meta":"Meta"})
                    df_new["DS"] = df_new["DS"].astype(str).str.strip()
                    meta_raw = df_new["Meta"]
                    meta_num = pd.to_numeric(meta_raw, errors="coerce")
                    if meta_num.isna().any() or meta_raw.astype(str).str.contains("%", na=False).any():
                        meta_str = (meta_raw.astype(str)
                                    .str.replace("%","",regex=False)
                                    .str.replace(",",".",regex=False).str.strip())
                        meta_num = pd.to_numeric(meta_str, errors="coerce")
                        meta_num = meta_num.where(meta_num <= 1.0, meta_num / 100)
                    else:
                        meta_num = meta_num.where(meta_num <= 1.0, meta_num / 100)
                    df_new["Meta"] = meta_num.fillna(0.5)
                    salvar_metas(df_new, usuario)
                    st.success(f"✅ Metas de {len(df_new)} bases salvas com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
