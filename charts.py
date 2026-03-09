"""
charts.py — Gráficos Plotly · Tema Corporativo Dark iMile
"""
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Paleta ────────────────────────────────────────────────────
AZ   = "#3b82f6"   # azul (recebido)
AZ2  = "#1d4ed8"   # azul escuro (borda)
VD   = "#10b981"   # verde (expedido / taxa boa)
VD2  = "#059669"
AM   = "#f59e0b"   # amarelo (alerta)
VM   = "#ef4444"   # vermelho (ruim)
CN   = "#06b6d4"   # ciano (entregas)
BG   = "#0f172a"   # fundo escuro
BG2  = "#1e293b"   # fundo plot
GD   = "#334155"   # grade
TX   = "#f1f5f9"   # texto principal
TX2  = "#94a3b8"   # texto secundário
BRANCO = "#ffffff"


def _layout(fig, h=420, title=""):
    fig.update_layout(
        paper_bgcolor=BG,
        plot_bgcolor=BG2,
        font=dict(color=TX, family="DM Sans, Segoe UI, Arial", size=12),
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=14, color=TX),
            x=0.01, xanchor="left", pad=dict(b=8)
        ),
        legend=dict(
            bgcolor="rgba(15,23,42,0.8)", bordercolor=GD, borderwidth=1,
            font=dict(color=TX2, size=11),
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0
        ),
        margin=dict(t=60, b=50, l=60, r=36),
        height=h,
        hoverlabel=dict(bgcolor="#1e293b", bordercolor=AZ,
                        font=dict(color=TX, size=12)),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=GD,
        tickfont=dict(color=TX2, size=11),
        tickcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.05)",
        gridwidth=1,
        zeroline=False,
        linecolor="rgba(0,0,0,0)",
        tickfont=dict(color=TX2, size=11),
    )
    return fig


def _cor_taxa(taxa, meta=0.5):
    if taxa >= meta:         return VD
    elif taxa >= meta * 0.8: return AM
    else:                    return VM


# ══════════════════════════════════════════════════════════════
#  1. VOLUME POR DS
# ══════════════════════════════════════════════════════════════
def chart_volume_ds(df: pd.DataFrame, top_n=20) -> go.Figure:
    df = df.copy().sort_values("expedido", ascending=False).head(top_n)
    fig = go.Figure()

    # Recebido — azul
    fig.add_trace(go.Bar(
        name="Recebido", x=df["scan_station"], y=df["recebido"],
        marker=dict(color=AZ, line=dict(color=AZ2, width=0.8)),
        text=df["recebido"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(color=TX2, size=9, family="DM Mono, monospace"),
        hovertemplate="<b>%{x}</b><br>Recebido: %{y:,}<extra></extra>",
    ))

    # Expedido — verde
    fig.add_trace(go.Bar(
        name="Expedido", x=df["scan_station"], y=df["expedido"],
        marker=dict(color=VD, line=dict(color=VD2, width=0.8)),
        text=df["expedido"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(color=TX2, size=9, family="DM Mono, monospace"),
        hovertemplate="<b>%{x}</b><br>Expedido: %{y:,}<extra></extra>",
    ))

    # Entregas — ciano (linha)
    if "entregas" in df.columns and df["entregas"].sum() > 0:
        fig.add_trace(go.Scatter(
            name="Entregas", x=df["scan_station"], y=df["entregas"],
            mode="markers",
            marker=dict(color=CN, size=9, symbol="diamond",
                        line=dict(color=BG, width=1.5)),
            hovertemplate="<b>%{x}</b><br>Entregas: %{y:,}<extra></extra>",
        ))

    fig.update_layout(
        barmode="group", bargap=0.22, bargroupgap=0.05,
        xaxis=dict(tickangle=-35),
    )
    return _layout(fig, h=450, title=f"Volume por DS — Top {top_n}")


# ══════════════════════════════════════════════════════════════
#  2. TAXA DE EXPEDIÇÃO POR DS (horizontal)
# ══════════════════════════════════════════════════════════════
def chart_taxa_ds(df: pd.DataFrame, meta_col="meta") -> go.Figure:
    df = df.copy().sort_values("taxa_exp", ascending=True)
    metas = df[meta_col].values if meta_col in df.columns else [0.5] * len(df)
    cores = [_cor_taxa(r["taxa_exp"], r.get(meta_col, 0.5)) for _, r in df.iterrows()]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Taxa de Expedição",
        orientation="h",
        x=df["taxa_exp"] * 100,
        y=df["scan_station"],
        marker=dict(
            color=cores,
            line=dict(color="rgba(0,0,0,0)", width=0),
        ),
        text=[f"{t:.1%}" for t in df["taxa_exp"]],
        textposition="outside",
        textfont=dict(size=11, color=TX, family="DM Mono, monospace"),
        customdata=np.column_stack([
            df.get("recebido", pd.Series([0]*len(df))).values,
            df.get("expedido", pd.Series([0]*len(df))).values,
            metas * 100,
        ]),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Taxa: %{x:.1f}%<br>"
            "Recebido: %{customdata[0]:,}<br>"
            "Expedido: %{customdata[1]:,}<br>"
            "Meta: %{customdata[2]:.1f}%<extra></extra>"
        ),
    ))

    meta_val = float(metas[0]) * 100 if len(metas) > 0 else 50
    fig.add_vline(
        x=meta_val, line_dash="dash", line_color=AM, line_width=1.5,
        annotation_text=f"Meta {meta_val:.0f}%",
        annotation_font=dict(color=AM, size=11),
        annotation_position="top",
    )

    fig.update_layout(
        xaxis=dict(ticksuffix="%", range=[0, 115], showgrid=False),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        height=max(420, len(df) * 30),
    )
    return _layout(fig, title="Taxa de Expedição por DS")


# ══════════════════════════════════════════════════════════════
#  3. EVOLUÇÃO DIÁRIA
# ══════════════════════════════════════════════════════════════
def chart_evolucao_diaria(df_hist: pd.DataFrame) -> go.Figure:
    df = (df_hist.groupby("data_ref", as_index=False)
                 .agg(recebido=("recebido", "sum"),
                      expedido=("expedido", "sum"),
                      entregas=("entregas", "sum"))
                 .sort_values("data_ref"))
    df["taxa_exp"] = df["expedido"] / df["recebido"].replace(0, np.nan)
    df["taxa_ent"] = df["entregas"] / df["recebido"].replace(0, np.nan)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Recebido", x=df["data_ref"], y=df["recebido"],
        marker=dict(color=AZ, line=dict(color=AZ2, width=0.8)),
        text=df["recebido"].apply(lambda v: f"{v:,}"),
        textposition="inside",
        textfont=dict(color=BRANCO, size=10, family="DM Mono, monospace"),
        hovertemplate="<b>%{x}</b><br>Recebido: %{y:,}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        name="Expedido", x=df["data_ref"], y=df["expedido"],
        marker=dict(color=VD, line=dict(color=VD2, width=0.8)),
        text=df["expedido"].apply(lambda v: f"{v:,}"),
        textposition="inside",
        textfont=dict(color=BRANCO, size=10, family="DM Mono, monospace"),
        hovertemplate="<b>%{x}</b><br>Expedido: %{y:,}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        name="Taxa Exp. %", x=df["data_ref"], y=df["taxa_exp"] * 100,
        mode="lines+markers+text", yaxis="y2",
        line=dict(color=AM, width=2.5),
        marker=dict(color=AM, size=8, line=dict(color=BG, width=2)),
        text=[f"{t:.0%}" for t in df["taxa_exp"].fillna(0)],
        textposition="top center",
        textfont=dict(color=AM, size=11, family="DM Mono, monospace"),
        hovertemplate="Taxa Exp: %{y:.1f}%<extra></extra>",
    ))

    if df["entregas"].sum() > 0:
        fig.add_trace(go.Scatter(
            name="Taxa Ent. %", x=df["data_ref"], y=df["taxa_ent"] * 100,
            mode="lines+markers", yaxis="y2",
            line=dict(color=CN, width=2, dash="dot"),
            marker=dict(color=CN, size=7, line=dict(color=BG, width=1.5)),
            hovertemplate="Taxa Ent: %{y:.1f}%<extra></extra>",
        ))

    fig.update_layout(
        barmode="group", bargap=0.25,
        yaxis=dict(title=dict(text="Quantidade", font=dict(color=TX2, size=11))),
        yaxis2=dict(
            overlaying="y", side="right",
            ticksuffix="%", range=[0, 120],
            showgrid=False,
            tickfont=dict(color=TX2),
        ),
    )
    return _layout(fig, h=440, title="Evolução Diária — Volume e Taxa")


# ══════════════════════════════════════════════════════════════
#  4. MAPA DE CALOR — escala clara e legível
# ══════════════════════════════════════════════════════════════
def chart_heatmap_cidades(df_cidades: pd.DataFrame, metrica="taxa_exp") -> go.Figure:
    if len(df_cidades) == 0:
        return go.Figure()

    df_com_dado = df_cidades[df_cidades["recebido"] > 0].copy()
    if len(df_com_dado) == 0:
        return go.Figure()

    top_ds   = (df_com_dado.groupby("scan_station")["recebido"].sum()
                .nlargest(15).index.tolist())
    top_city = (df_com_dado.groupby("destination_city")["recebido"].sum()
                .nlargest(20).index.tolist())
    df_filt  = df_com_dado[
        df_com_dado["scan_station"].isin(top_ds) &
        df_com_dado["destination_city"].isin(top_city)
    ]

    pivot = df_filt.pivot_table(
        index="destination_city", columns="scan_station",
        values=metrica, aggfunc="mean"
    ).reindex(
        index=[c for c in top_city if c in df_filt["destination_city"].values],
        columns=[c for c in top_ds  if c in df_filt["scan_station"].values]
    )

    z_vals    = pivot.values * 100
    text_vals = [
        [f"{v*100:.0f}%" if not np.isnan(v) else "—" for v in row]
        for row in pivot.values
    ]

    titulo = ("Taxa de Expedição · DS × Cidade"
              if metrica == "taxa_exp" else "Taxa de Entrega · DS × Cidade")

    # Escala: cinza (sem dado) → vermelho → amarelo → verde
    colorscale = [
        [0.00, "#1a1a2e"],  # 0%  — quase preto (sem dado / zero)
        [0.01, "#7f1d1d"],  # 1%  — vermelho escuro
        [0.40, "#dc2626"],  # 40% — vermelho vivo
        [0.55, "#d97706"],  # 55% — âmbar
        [0.70, "#16a34a"],  # 70% — verde
        [1.00, "#bbf7d0"],  # 100%— verde claro
    ]

    fig = go.Figure(go.Heatmap(
        z=z_vals,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=colorscale,
        zmin=0, zmax=100, zmid=50,
        text=text_vals,
        texttemplate="%{text}",
        textfont=dict(size=10, color=BRANCO, family="DM Mono, monospace"),
        hovertemplate="<b>%{x}</b> · %{y}<br>Taxa: %{z:.1f}%<extra></extra>",
        colorbar=dict(
            ticksuffix="%",
            title=dict(text="Taxa", side="right", font=dict(color=TX2, size=11)),
            tickvals=[0, 25, 50, 75, 100],
            tickfont=dict(color=TX2, size=10),
            bgcolor=BG, bordercolor=GD,
            thickness=12, len=0.85,
        ),
        xgap=2, ygap=2,   # espaço entre células — deixa mais limpo
    ))

    fig.update_layout(xaxis=dict(tickangle=-35, side="bottom"))
    return _layout(fig, h=max(460, len(pivot) * 28 + 120), title=titulo)


# ══════════════════════════════════════════════════════════════
#  5. COMPARATIVO
# ══════════════════════════════════════════════════════════════
def chart_comparativo(df_hist: pd.DataFrame, periodo="semana") -> go.Figure:
    df = df_hist.copy()
    df["data_ref"] = pd.to_datetime(df["data_ref"])

    if periodo == "dia":
        df["grupo"] = df["data_ref"].dt.strftime("%d/%m")
    elif periodo == "semana":
        df["grupo"] = df["data_ref"].dt.to_period("W").apply(
            lambda p: f"Sem {p.start_time.strftime('%d/%m')}")
    else:
        df["grupo"] = df["data_ref"].dt.strftime("%b/%Y")

    agg = (df.groupby("grupo", as_index=False)
             .agg(recebido=("recebido", "sum"),
                  expedido=("expedido", "sum"),
                  entregas=("entregas", "sum")))
    agg["taxa_exp"] = agg["expedido"] / agg["recebido"].replace(0, np.nan).fillna(1)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Recebido", x=agg["grupo"], y=agg["recebido"],
        marker=dict(color=AZ, line=dict(color=AZ2, width=0.8)),
        text=agg["recebido"].apply(lambda v: f"{v:,}"),
        textposition="inside",
        textfont=dict(color=BRANCO, size=11, family="DM Mono, monospace"),
        hovertemplate="<b>%{x}</b><br>Recebido: %{y:,}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        name="Expedido", x=agg["grupo"], y=agg["expedido"],
        marker=dict(color=VD, line=dict(color=VD2, width=0.8)),
        text=agg["expedido"].apply(lambda v: f"{v:,}"),
        textposition="inside",
        textfont=dict(color=BRANCO, size=11, family="DM Mono, monospace"),
        hovertemplate="<b>%{x}</b><br>Expedido: %{y:,}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        name="Taxa Exp. %", x=agg["grupo"], y=agg["taxa_exp"] * 100,
        mode="lines+markers+text", yaxis="y2",
        line=dict(color=AM, width=2.5),
        marker=dict(color=AM, size=9, line=dict(color=BG, width=2)),
        text=[f"{t:.0%}" for t in agg["taxa_exp"]],
        textposition="top center",
        textfont=dict(color=AM, size=12, family="DM Mono, monospace"),
        hovertemplate="Taxa Exp: %{y:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        barmode="group", bargap=0.3,
        yaxis=dict(title=dict(text="Quantidade", font=dict(color=TX2, size=11))),
        yaxis2=dict(
            overlaying="y", side="right",
            ticksuffix="%", range=[0, 120],
            showgrid=False, tickfont=dict(color=TX2),
        ),
    )
    labels = {"dia": "Diário", "semana": "Semanal", "mes": "Mensal"}
    return _layout(fig, h=420, title=f"Comparativo {labels.get(periodo, '')}")


# ══════════════════════════════════════════════════════════════
#  6. DONUT
# ══════════════════════════════════════════════════════════════
def chart_donut(total_rec, total_exp, taxa) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=["Recebido", "Expedido"],
        values=[total_rec, total_exp],
        hole=0.68,
        marker=dict(colors=[AZ, VD], line=dict(color=BG, width=4)),
        textinfo="label+percent",
        textfont=dict(size=12, color=TX),
        hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
        pull=[0, 0.04],
        direction="clockwise",
        sort=False,
    ))
    fig.update_layout(
        annotations=[dict(
            text=(f"<b style='font-size:20px;color:{TX}'>{taxa:.1%}</b>"
                  f"<br><span style='font-size:11px;color:{TX2}'>Em Rota</span>"),
            x=0.5, y=0.5, showarrow=False,
            font=dict(family="Syne, DM Sans"),
        )],
        legend=dict(
            bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
            font=dict(color=TX2, size=12),
            orientation="h", x=0.5, xanchor="center", y=-0.06,
        ),
    )
    return _layout(fig, h=360, title="Distribuição Geral")
