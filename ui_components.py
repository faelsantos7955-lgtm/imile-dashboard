"""
ui_components.py
Componentes visuais HTML puro — renderizados via st.components.v1.html()
Recebem dados Python, devolvem HTML string + altura sugerida.
"""

import streamlit.components.v1 as _components

# ── Fonte compartilhada ────────────────────────────────────────────────────────
_FONT = "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');"

_BASE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', sans-serif; background: transparent; color: #0f172a; }
"""


# ══════════════════════════════════════════════════════════════════════════════
#  KPI CARDS
#  Uso: render_kpi_cards(cards, delta_row=None)
#
#  cards = lista de dicts:
#    { "label": str, "value": str, "sub": str, "icon": str, "color": "blue|green|orange|violet|red" }
#
#  delta_row = lista de dicts (opcional):
#    { "text": str, "value": str, "positive": bool }
# ══════════════════════════════════════════════════════════════════════════════

_COLOR_MAP = {
    "blue":   {"accent": "#2563eb", "bg": "#eff6ff",  "icon_color": "#1d4ed8"},
    "green":  {"accent": "#059669", "bg": "#f0fdf4",  "icon_color": "#047857"},
    "orange": {"accent": "#ea580c", "bg": "#fff7ed",  "icon_color": "#c2410c"},
    "violet": {"accent": "#7c3aed", "bg": "#f5f3ff",  "icon_color": "#6d28d9"},
    "red":    {"accent": "#dc2626", "bg": "#fef2f2",  "icon_color": "#b91c1c"},
    "slate":  {"accent": "#475569", "bg": "#f8fafc",  "icon_color": "#334155"},
}


def _kpi_card_html(card: dict, idx: int) -> str:
    color   = card.get("color", "blue")
    c       = _COLOR_MAP.get(color, _COLOR_MAP["blue"])
    label   = card.get("label", "")
    value   = card.get("value", "—")
    sub     = card.get("sub", "")
    icon    = card.get("icon", "📦")
    delay   = idx * 60

    return f"""
    <div class="kpi-card" style="
        border-top: 3px solid {c['accent']};
        animation-delay: {delay}ms;
    ">
        <div class="kpi-icon" style="background:{c['bg']}">{icon}</div>
        <div class="kpi-lbl">{label}</div>
        <div class="kpi-val">{value}</div>
        {f'<div class="kpi-sub">{sub}</div>' if sub else ''}
    </div>"""


def render_kpi_cards(cards: list, delta_row: list = None, cols: int = None):
    """
    Renderiza KPI cards via iframe.
    cards: lista de dicts com label, value, sub, icon, color
    delta_row: lista de dicts com text, value, positive
    cols: número de colunas (default = len(cards))
    """
    n = cols or len(cards)
    cards_html = "".join(_kpi_card_html(c, i) for i, c in enumerate(cards))

    delta_html = ""
    if delta_row:
        items = ""
        for d in delta_row:
            pos   = d.get("positive", True)
            color = "#16a34a" if pos else "#dc2626"
            arrow = "▲" if pos else "▼"
            items += f"""
            <div class="delta-item">
                {d.get('text', '')}
                <span style="color:{color};font-weight:700;margin-left:4px">{arrow} {d.get('value','')}</span>
                <span style="color:#94a3b8;margin-left:2px">vs ontem</span>
            </div>"""
        delta_html = f'<div class="delta-row">{items}</div>'

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{_FONT}
{_BASE_CSS}
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat({n}, 1fr);
    gap: 12px;
    padding: 4px 2px 8px;
}}
.kpi-card {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px 20px 16px;
    position: relative;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
    animation: slideUp .4s ease both;
    transition: transform .2s, box-shadow .2s;
}}
.kpi-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 6px 18px rgba(0,0,0,.09);
}}
.kpi-icon {{
    position: absolute;
    top: 16px; right: 16px;
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
}}
.kpi-lbl {{
    font-size: 10px; font-weight: 700;
    letter-spacing: 1.2px; text-transform: uppercase;
    color: #64748b; margin-bottom: 8px;
    font-family: 'DM Mono', monospace;
}}
.kpi-val {{
    font-size: 30px; font-weight: 800;
    color: #0f172a; line-height: 1;
    margin-bottom: 5px; letter-spacing: -.5px;
}}
.kpi-sub {{
    font-size: 11px; color: #94a3b8;
    font-family: 'DM Mono', monospace;
}}
.delta-row {{
    display: flex; gap: 20px; flex-wrap: wrap;
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 10px 16px;
    margin-top: 4px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}}
.delta-item {{
    font-size: 12px; color: #64748b;
    font-family: 'DM Mono', monospace;
}}
@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
</style></head>
<body>
<div class="kpi-grid">{cards_html}</div>
{delta_html}
</body></html>"""

    height = 140 + (48 if delta_row else 0)
    _components.html(html, height=height, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
#  RANKING TABLE
#  Uso: render_ranking_table(rows)
#
#  rows = lista de dicts:
#    { "pos": int, "ds": str, "regiao": str, "recebido": int, "expedido": int,
#      "taxa_exp": float (0-1), "taxa_ent": float (0-1),
#      "meta": float (0-100), "na_meta": bool }
# ══════════════════════════════════════════════════════════════════════════════

def render_ranking_table(rows: list):
    """
    Renderiza tabela de ranking via iframe com barra de progresso e badges.
    rows: lista de dicts com pos, ds, regiao, recebido, expedido, taxa_exp, meta, na_meta
    """
    rows_html = ""
    for r in rows:
        ok      = bool(r.get("na_meta", False))
        tx      = float(r.get("taxa_exp", 0))
        tx_pct  = tx * 100 if tx <= 1 else tx
        meta    = float(r.get("meta", 50))
        if meta <= 1.0: meta *= 100
        bar_w   = min(int(tx_pct), 100)
        bar_c   = "#16a34a" if ok else "#ef4444"
        txt_c   = "#15803d" if ok else "#b91c1c"
        bg_c    = "#dcfce7" if ok else "#fee2e2"
        badge   = f"<span class='badge' style='background:{bg_c};color:{txt_c}'>{'✓ Meta' if ok else '✗ Abaixo'}</span>"
        rec     = int(r.get("recebido", 0))
        exp_v   = int(r.get("expedido", 0))
        pos     = r.get("pos", "")
        ds      = r.get("ds", "")
        regiao  = r.get("regiao", "")

        rows_html += f"""
        <tr class="{'row-ok' if ok else 'row-bad'}">
            <td class="td-num">{pos}</td>
            <td class="td-ds">{ds}</td>
            <td class="td-reg">{regiao}</td>
            <td class="td-n">{rec:,}</td>
            <td class="td-n">{exp_v:,}</td>
            <td class="td-bar">
                <div class="bar-wrap">
                    <div class="bar-track">
                        <div class="bar-fill" style="width:{bar_w}%;background:{bar_c}"></div>
                    </div>
                    <span class="bar-label" style="color:{bar_c}">{tx_pct:.1f}%</span>
                </div>
            </td>
            <td class="td-n td-meta">{meta:.0f}%</td>
            <td>{badge}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{_FONT}
{_BASE_CSS}
.wrapper {{
    border-radius: 12px; overflow: hidden;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
}}
table {{
    width: 100%; border-collapse: collapse;
    font-size: 13px; font-family: 'Inter', sans-serif;
}}
thead tr {{ background: #0f172a; }}
th {{
    padding: 11px 14px; text-align: left;
    font-size: 10px; font-weight: 700;
    letter-spacing: 1.2px; text-transform: uppercase;
    color: #64748b; border: none;
    font-family: 'DM Mono', monospace;
}}
tr {{ border-bottom: 1px solid #f1f5f9; transition: background .12s; }}
tr:last-child {{ border-bottom: none; }}
tr:hover {{ background: #f8fafc !important; }}
td {{
    padding: 10px 14px; color: #334155;
    background: #ffffff; vertical-align: middle;
}}
.td-num {{ color: #94a3b8; font-weight: 700; font-size: 12px; width: 32px; }}
.td-ds  {{ font-weight: 700; color: #0f172a; }}
.td-reg {{ color: #64748b; font-size: 12px; }}
.td-n   {{ font-family: 'DM Mono', monospace; font-size: 12px; }}
.td-meta {{ color: #64748b; }}
.td-bar {{ min-width: 150px; }}
.bar-wrap  {{ display: flex; align-items: center; gap: 10px; }}
.bar-track {{ flex: 1; background: #f1f5f9; border-radius: 4px; height: 8px; overflow: hidden; }}
.bar-fill  {{ height: 100%; border-radius: 4px; transition: width .4s ease; }}
.bar-label {{ font-weight: 700; font-size: 12px; white-space: nowrap; min-width: 42px; text-align: right; font-family: 'DM Mono', monospace; }}
.badge {{
    display: inline-block; padding: 3px 10px;
    border-radius: 99px; font-size: 11px; font-weight: 700;
    font-family: 'DM Mono', monospace;
}}
</style></head>
<body>
<div class="wrapper">
<table>
<thead>
  <tr>
    <th>#</th><th>DS</th><th>Região</th>
    <th>Recebido</th><th>Expedido</th>
    <th>Taxa Exp.</th><th>Meta</th><th>Status</th>
  </tr>
</thead>
<tbody>{rows_html}</tbody>
</table>
</div>
</body></html>"""

    height = max(120, len(rows) * 46 + 56)
    _components.html(html, height=height, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION HEADER  (substitui .section-label)
#  Uso: render_section_header("Título", "subtítulo opcional")
# ══════════════════════════════════════════════════════════════════════════════

def render_section_header(title: str, subtitle: str = ""):
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{_FONT}
{_BASE_CSS}
body {{ padding: 4px 0; }}
.wrap {{
    display: flex; align-items: center; gap: 12px;
}}
.title {{
    font-size: 10px; font-weight: 700; letter-spacing: 1.8px;
    text-transform: uppercase; color: #94a3b8;
    font-family: 'DM Mono', monospace; white-space: nowrap;
}}
.sub {{
    font-size: 11px; color: #94a3b8;
    font-family: 'DM Mono', monospace;
}}
.line {{ flex: 1; height: 1px; background: #e2e8f0; }}
</style></head>
<body>
<div class="wrap">
  <span class="title">{title}</span>
  {f'<span class="sub">— {subtitle}</span>' if subtitle else ''}
  <div class="line"></div>
</div>
</body></html>"""
    _components.html(html, height=32, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE HEADER  (substitui .app-header)
#  Uso: render_page_header("Dashboard Operacional", "Visão geral do dia", "📊")
# ══════════════════════════════════════════════════════════════════════════════

def render_page_header(title: str, subtitle: str = "", icon: str = "📊"):
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{_FONT}
{_BASE_CSS}
body {{ padding: 0; }}
.header {{
    background: #ffffff;
    padding: 22px 28px 18px;
    border-bottom: 1px solid #e2e8f0;
    display: flex; align-items: center; gap: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
}}
.icon {{ font-size: 26px; }}
.title {{
    font-size: 22px; font-weight: 800;
    color: #0f172a; letter-spacing: -.4px;
    line-height: 1.1;
}}
.sub {{
    font-size: 12px; color: #64748b;
    font-family: 'DM Mono', monospace;
    margin-top: 2px;
}}
</style></head>
<body>
<div class="header">
  <div class="icon">{icon}</div>
  <div>
    <div class="title">{title}</div>
    {f'<div class="sub">{subtitle}</div>' if subtitle else ''}
  </div>
</div>
</body></html>"""
    _components.html(html, height=78, scrolling=False)
