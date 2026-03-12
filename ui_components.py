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