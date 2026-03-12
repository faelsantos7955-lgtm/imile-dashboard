import streamlit as st


def kpi_card(title, value):
    st.markdown(
        f"""
        <div class="kpi-card">
            <span class="kpi-title">{title}</span>
            <span class="kpi-value">{value}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def chart_container(title):
    st.markdown(
        f"""
        <div class="chart-card">
        <h4>{title}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_kpi_cards(cards, delta_row=None):
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