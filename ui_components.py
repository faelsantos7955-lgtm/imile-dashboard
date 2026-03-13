import streamlit as st


def render_page_header(title, subtitle="", icon=""):
    st.markdown(f"""
    <div class="app-header">
        <div>{icon}</div>
        <div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title, subtitle=""):
    st.markdown(f"""
    <div class="section-header">
        <h3>{title}</h3>
        <span>{subtitle}</span>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_cards(cards=None, delta_row=None):

    cards = cards or []

    if cards:
        cols = st.columns(len(cards))

        for col, card in zip(cols, cards):
            with col:
                st.metric(
                    label=card.get("label", ""),
                    value=card.get("value", ""),
                    delta=card.get("sub", None)
                )

    if delta_row:
        st.divider()

        cols = st.columns(len(delta_row))

        for col, d in zip(cols, delta_row):
            with col:
                st.metric(
                    label=d.get("text", ""),
                    value=d.get("value", "")
                )


def render_ranking_table(rows):

    st.markdown('<div class="ranking-table">', unsafe_allow_html=True)

    for r in rows:
        cor = "#16a34a" if r.get("na_meta") else "#dc2626"

        st.markdown(f"""
        <div style="
            display:flex;
            justify-content:space-between;
            padding:10px 14px;
            border-bottom:1px solid #e2e8f0;
            font-size:14px
        ">
            <span><b>{r.get("pos")}</b> · {r.get("ds")}</span>
            <span>{r.get("taxa_exp"):.1%}</span>
            <span style="color:{cor}">meta {r.get("meta"):.0%}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)