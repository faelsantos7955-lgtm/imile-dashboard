import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def waterfall_volume(recebido, expedido):

    backlog = recebido - expedido

    fig = go.Figure(go.Waterfall(
        measure=["absolute","relative","total"],
        x=["Recebido","Expedido","Backlog"],
        y=[recebido,-expedido,0]
    ))

    fig.update_layout(title="Fluxo de Volume")

    return fig


def backlog_distribution(df):

    fig = px.bar(
        df,
        x="ds",
        y="backlog",
        title="Distribuição de Backlog por DS"
    )

    return fig


def pareto_backlog(df):

    df = df.sort_values("backlog", ascending=False)

    fig = px.bar(
        df,
        x="ds",
        y="backlog",
        title="Pareto de Backlog"
    )

    return fig


def heatmap_ds(df):

    pivot = df.pivot(index="ds", columns="data", values="taxa")

    fig = px.imshow(
        pivot,
        aspect="auto",
        title="Heatmap de Performance DS"
    )

    return fig