"""
charts.py — Gráficos do iMile Dashboard
Tema corporativo claro (branco/cinza + azul iMile)
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Paleta corporativa ────────────────────────────────────────
_BG_PAPER = "#ffffff"
_BG_PLOT  = "#f8fafc"
_FONT     = dict(family="Inter, sans-serif", color="#1e293b", size=12)
_GRID     = "#e2e8f0"
_MARGIN   = dict(t=40, b=40, l=50, r=30)

_AZUL     = "#2563eb"
_AZUL_CL  = "#60a5fa"
_LARANJA  = "#f97316"
_VERDE    = "#10b981"
_VERMELHO = "#ef4444"
_ROXO     = "#8b5cf6"
_CINZA    = "#94a3b8"


def _layout_base(fig, height=380, **kw):
    """Aplica layout corporativo padrão."""
    # Merge defaults com overrides para evitar conflito de kwargs
    xaxis = {**dict(gridcolor=_GRID), **(kw.pop("xaxis", {}))}
    yaxis = {**dict(gridcolor=_GRID), **(kw.pop("yaxis", {}))}
    legend = {**dict(bgcolor=_BG_PAPER, bordercolor=_GRID), **(kw.pop("legend", {}))}

    fig.update_layout(
        paper_bgcolor=_BG_PAPER,
        plot_bgcolor=_BG_PLOT,
        font=_FONT,
        height=height,
        margin=_MARGIN,
        xaxis=xaxis,
        yaxis=yaxis,
        legend=legend,
        **kw,
    )
    return fig


# ══════════════════════════════════════════════════════════════
#  1. VOLUME POR DS — barras agrupadas (Recebido × Expedido)
# ══════════════════════════════════════════════════════════════
def chart_volume_ds(df_dia: pd.DataFrame) -> go.Figure:
    """Barras agrupadas de Recebido e Expedido por DS."""
    df = df_dia.sort_values("recebido", ascending=False).copy()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Recebido",
        x=df["scan_station"], y=df["recebido"],
        marker_color=_AZUL,
        hovertemplate="<b>%{x}</b><br>Recebido: %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Expedido",
        x=df["scan_station"], y=df["expedido"],
        marker_color=_LARANJA,
        hovertemplate="<b>%{x}</b><br>Expedido: %{y:,}<extra></extra>",
    ))

    if "entregas" in df.columns and df["entregas"].sum() > 0:
        fig.add_trace(go.Bar(
            name="Entregas",
            x=df["scan_station"], y=df["entregas"],
            marker_color=_VERDE,
            hovertemplate="<b>%{x}</b><br>Entregas: %{y:,}<extra></extra>",
        ))

    _layout_base(fig, barmode="group",
                 title=dict(text="Volume por DS", font=dict(size=14)),
                 xaxis=dict(tickangle=-35, gridcolor=_GRID))
    return fig


# ══════════════════════════════════════════════════════════════
#  2. TAXA DE EXPEDIÇÃO POR DS — barras coloridas por meta
# ══════════════════════════════════════════════════════════════
def chart_taxa_ds(df_dia: pd.DataFrame) -> go.Figure:
    """Barras horizontais de taxa de expedição, coloridas por atingimento de meta."""
    df = df_dia.sort_values("taxa_exp", ascending=True).copy()

    cores = [
        _VERDE if row["atingiu_meta"] else _VERMELHO
        for _, row in df.iterrows()
    ]

    fig = go.Figure(go.Bar(
        y=df["scan_station"],
        x=df["taxa_exp"],
        orientation="h",
        marker_color=cores,
        text=[f"{v:.1%}" for v in df["taxa_exp"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Taxa: %{x:.1%}<br>Meta: %{customdata:.0%}<extra></extra>",
        customdata=df["meta"],
    ))

    meta_media = df["meta"].mean() if "meta" in df.columns else 0.5
    fig.add_vline(
        x=meta_media, line_dash="dash", line_color="#0f172a", line_width=2,
        annotation_text=f"Meta {meta_media:.0%}",
        annotation_position="top right",
        annotation_font_size=11,
    )

    _layout_base(fig, height=max(300, len(df) * 36 + 80),
                 title=dict(text="Taxa de Expedição por DS", font=dict(size=14)),
                 xaxis=dict(tickformat=".0%", range=[0, 1.15], gridcolor=_GRID),
                 yaxis=dict(gridcolor=_GRID),
                 showlegend=False)
    return fig


# ══════════════════════════════════════════════════════════════
#  3. DONUT — Recebido × Expedido
# ══════════════════════════════════════════════════════════════
def chart_donut(recebido: int, expedido: int, taxa: float) -> go.Figure:
    """Gráfico donut mostrando proporção Expedido/Backlog."""
    backlog = max(recebido - expedido, 0)

    fig = go.Figure(go.Pie(
        labels=["Expedido", "Backlog"],
        values=[expedido, backlog],
        hole=0.65,
        marker=dict(colors=[_AZUL, "#e2e8f0"]),
        textinfo="percent",
        textfont=dict(size=13, color="#1e293b"),
        hovertemplate="<b>%{label}</b><br>%{value:,} waybills<br>%{percent}<extra></extra>",
    ))

    fig.add_annotation(
        text=f"<b>{taxa:.1%}</b><br><span style='font-size:11px;color:#64748b'>expedido</span>",
        showarrow=False,
        font=dict(size=22, color="#1e293b"),
    )

    _layout_base(fig, height=340,
                 title=dict(text="Proporção de Expedição", font=dict(size=14)),
                 showlegend=True,
                 legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"))
    return fig


# ══════════════════════════════════════════════════════════════
#  4. HEATMAP DE CIDADES
# ══════════════════════════════════════════════════════════════
def chart_heatmap_cidades(df_cid: pd.DataFrame, col_valor: str = "taxa_exp") -> go.Figure:
    """Heatmap DS × Cidade com taxa de expedição ou entrega."""
    label_map = {
        "taxa_exp": "Taxa Expedição",
        "taxa_ent": "Taxa Entrega",
    }
    titulo = label_map.get(col_valor, col_valor)

    # Pega top 20 cidades por volume
    top_cidades = (df_cid.groupby("destination_city")["recebido"]
                   .sum().nlargest(20).index.tolist())
    df = df_cid[df_cid["destination_city"].isin(top_cidades)].copy()

    if len(df) == 0:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados de cidades", showarrow=False, font=dict(size=14))
        _layout_base(fig, height=200)
        return fig

    pivot = df.pivot_table(
        index="scan_station",
        columns="destination_city",
        values=col_valor,
        aggfunc="mean",
    ).fillna(0)

    colorscale = "RdYlGn" if "exp" in col_valor else "Blues"

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=colorscale,
        zmin=0, zmax=1,
        labels=dict(x="Cidade", y="DS", color=titulo),
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b> → %{x}<br>" + titulo + ": %{z:.1%}<extra></extra>",
    )

    _layout_base(fig, height=max(350, len(pivot) * 28 + 100),
                 title=dict(text=f"Heatmap — {titulo}", font=dict(size=14)),
                 xaxis=dict(tickangle=-40))
    return fig


# ══════════════════════════════════════════════════════════════
#  5. EVOLUÇÃO DIÁRIA — linhas de Recebido, Expedido e Taxa
# ══════════════════════════════════════════════════════════════
def chart_evolucao_diaria(df_hist: pd.DataFrame) -> go.Figure:
    """Gráfico de linhas com evolução diária de volumes e taxa."""
    agg = (df_hist.groupby("data_ref", as_index=False)
           .agg(recebido=("recebido", "sum"),
                expedido=("expedido", "sum"),
                entregas=("entregas", "sum")))
    agg["taxa_exp"] = np.where(agg["recebido"] > 0, agg["expedido"] / agg["recebido"], 0)
    agg["data_ref"] = pd.to_datetime(agg["data_ref"])
    agg = agg.sort_values("data_ref")

    fig = go.Figure()

    # Barras de volume
    fig.add_trace(go.Bar(
        name="Recebido",
        x=agg["data_ref"], y=agg["recebido"],
        marker_color=_AZUL_CL, opacity=0.5,
        hovertemplate="<b>%{x|%d/%m}</b><br>Recebido: %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Expedido",
        x=agg["data_ref"], y=agg["expedido"],
        marker_color=_LARANJA, opacity=0.5,
        hovertemplate="<b>%{x|%d/%m}</b><br>Expedido: %{y:,}<extra></extra>",
    ))

    # Linha de taxa no eixo secundário
    fig.add_trace(go.Scatter(
        name="Taxa Exp.",
        x=agg["data_ref"], y=agg["taxa_exp"],
        mode="lines+markers+text",
        yaxis="y2",
        line=dict(color=_AZUL, width=3),
        marker=dict(size=7),
        text=[f"{v:.0%}" for v in agg["taxa_exp"]],
        textposition="top center",
        textfont=dict(size=10, color=_AZUL),
        hovertemplate="<b>%{x|%d/%m}</b><br>Taxa: %{y:.1%}<extra></extra>",
    ))

    _layout_base(fig, height=420, barmode="group",
                 title=dict(text="Evolução Diária", font=dict(size=14)),
                 yaxis2=dict(
                     overlaying="y", side="right",
                     tickformat=".0%", range=[0, 1.15],
                     gridcolor="rgba(0,0,0,0)",
                     showgrid=False,
                 ),
                 xaxis=dict(dtick="D1", tickformat="%d/%m", gridcolor=_GRID),
                 legend=dict(orientation="h", y=1.08, x=0))
    return fig


# ══════════════════════════════════════════════════════════════
#  6. COMPARATIVO — agregado por dia, semana ou mês
# ══════════════════════════════════════════════════════════════
def chart_comparativo(df_hist: pd.DataFrame, periodo: str = "dia") -> go.Figure:
    """Gráfico comparativo agregado por dia, semana ou mês."""
    df = df_hist.copy()
    df["data_ref"] = pd.to_datetime(df["data_ref"])

    if periodo == "semana":
        df["periodo"] = df["data_ref"].dt.isocalendar().week.astype(str).str.zfill(2)
        df["periodo"] = "S" + df["periodo"]
        label_x = "Semana"
    elif periodo == "mes":
        df["periodo"] = df["data_ref"].dt.strftime("%Y-%m")
        label_x = "Mês"
    else:
        df["periodo"] = df["data_ref"].dt.strftime("%d/%m")
        label_x = "Dia"

    agg = (df.groupby("periodo", as_index=False)
           .agg(recebido=("recebido", "sum"),
                expedido=("expedido", "sum"),
                entregas=("entregas", "sum")))
    agg["taxa_exp"] = np.where(agg["recebido"] > 0, agg["expedido"] / agg["recebido"], 0)
    agg = agg.sort_values("periodo")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Recebido", x=agg["periodo"], y=agg["recebido"],
        marker_color=_AZUL,
        hovertemplate="<b>%{x}</b><br>Recebido: %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Expedido", x=agg["periodo"], y=agg["expedido"],
        marker_color=_LARANJA,
        hovertemplate="<b>%{x}</b><br>Expedido: %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        name="Taxa",
        x=agg["periodo"], y=agg["taxa_exp"],
        mode="lines+markers+text",
        yaxis="y2",
        line=dict(color=_VERDE, width=3),
        marker=dict(size=8, color=_VERDE),
        text=[f"{v:.0%}" for v in agg["taxa_exp"]],
        textposition="top center",
        textfont=dict(size=10, color=_VERDE),
        hovertemplate="<b>%{x}</b><br>Taxa: %{y:.1%}<extra></extra>",
    ))

    _layout_base(fig, height=420, barmode="group",
                 title=dict(text=f"Comparativo — {label_x}", font=dict(size=14)),
                 xaxis=dict(title=label_x, gridcolor=_GRID, tickangle=-30),
                 yaxis=dict(title="Volume", gridcolor=_GRID),
                 yaxis2=dict(
                     title="Taxa", overlaying="y", side="right",
                     tickformat=".0%", range=[0, 1.15],
                     showgrid=False,
                 ),
                 legend=dict(orientation="h", y=1.08, x=0))
    return fig
