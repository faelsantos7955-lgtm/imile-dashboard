import streamlit as st
import pandas as pd

from auth_ui import render_auth
from ui_components import (
    render_page_header,
    render_section_header,
    render_kpi_cards,
    render_ranking_table
)

from charts import (
    waterfall_volume,
    backlog_distribution,
    pareto_backlog,
    heatmap_ds
)

# ─────────────────────────────
# PAGE CONFIG
# ─────────────────────────────

st.set_page_config(
    page_title="iMile Dashboard",
    layout="wide"
)

# ─────────────────────────────
# LOAD CSS
# ─────────────────────────────

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─────────────────────────────
# AUTH
# ─────────────────────────────

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    if render_auth():
        st.rerun()
    st.stop()

# ─────────────────────────────
# SIDEBAR
# ─────────────────────────────

st.sidebar.title("🚚 iMile")

page = st.sidebar.radio(
    "Navegação",
    [
        "Dashboard",
        "Performance DS",
        "Backlog",
        "Diagnóstico"
    ]
)

# ─────────────────────────────
# MOCK DATA (até integrar banco)
# ─────────────────────────────

df = pd.DataFrame({
    "ds":["SP01","RJ02","MG03","BA01"],
    "backlog":[20000,30000,10000,15000],
    "taxa":[0.92,0.85,0.96,0.88],
    "data":["Seg","Seg","Seg","Seg"]
})

recebido = 1200000
expedido = 1100000

# ─────────────────────────────
# DASHBOARD
# ─────────────────────────────

if page == "Dashboard":

    render_page_header(
        "Dashboard Operacional",
        "Visão geral da operação"
    )

    render_section_header("Indicadores")

    render_kpi_cards([
        {"label":"Recebido","value":f"{recebido:,}"},
        {"label":"Expedido","value":f"{expedido:,}"},
        {"label":"Backlog","value":f"{recebido-expedido:,}"},
        {"label":"Taxa Expedição","value":"92%"}
    ])

    render_section_header("Fluxo de Volume")

    fig = waterfall_volume(recebido, expedido)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────
# PERFORMANCE DS
# ─────────────────────────────

elif page == "Performance DS":

    render_page_header(
        "Performance DS",
        "Comparação entre bases"
    )

    render_section_header("Heatmap de Performance")

    fig = heatmap_ds(df)
    st.plotly_chart(fig, use_container_width=True)

    render_section_header("Ranking DS")

    ranking = [
        {"pos":1,"ds":"SP01","taxa_exp":0.92,"meta":0.9,"na_meta":True},
        {"pos":2,"ds":"RJ02","taxa_exp":0.85,"meta":0.9,"na_meta":False},
        {"pos":3,"ds":"MG03","taxa_exp":0.96,"meta":0.9,"na_meta":True}
    ]

    render_ranking_table(ranking)

# ─────────────────────────────
# BACKLOG
# ─────────────────────────────

elif page == "Backlog":

    render_page_header(
        "Backlog Operacional",
        "Distribuição por DS"
    )

    render_section_header("Distribuição de Backlog")

    fig = backlog_distribution(df)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────
# DIAGNÓSTICO
# ─────────────────────────────

elif page == "Diagnóstico":

    render_page_header(
        "Diagnóstico Operacional",
        "Análise de gargalos"
    )

    render_section_header("Pareto de Backlog")

    fig = pareto_backlog(df)
    st.plotly_chart(fig, use_container_width=True)

    render_section_header("Alertas")

    if recebido-expedido > 100000:
        st.warning("Backlog elevado na operação")

    if df["taxa"].mean() < 0.9:
        st.warning("Taxa média abaixo da meta")