"""Knightsbridge-style palette, CSS and Plotly template.

Colours were read from the computed styles of knightsbridgesg.com:
royal navy #102763, midnight #020436, slate #324158, grey #858585, white,
and the site theme's bronze/gold family (#9C7741 · #BDA786 · #DECCB3).
Typography on the site: EB Garamond / Playfair Display (serif headings) and
Avenir (sans body) — Nunito Sans is used as the free Avenir stand-in.
"""

NAVY = "#102763"
MIDNIGHT = "#020436"
DEEP = "#07113F"
PANEL = "#0C1D52"
SLATE = "#324158"
GREY = "#858585"
MIST = "#AEB6C8"
IVORY = "#F4F1EA"
WHITE = "#FFFFFF"
GOLD = "#9C7741"
GOLD_LIGHT = "#BDA786"
SAND = "#DECCB3"
TERRACOTTA = "#A65B4C"

# Risk bands — red (heavy geo-risk exposure) → green (low)
BANDS = [
    # (lower bound, label, colour)
    (75, "SEVERE", "#C62828"),
    (60, "HIGH", "#EF6C00"),
    (45, "ELEVATED", "#F9A825"),
    (30, "MODERATE", "#9CCC65"),
    (0, "LOW", "#2E7D32"),
]
BAND_COLOR = {b[1]: b[2] for b in BANDS}

RISK_SCALE = [
    [0.00, "#1B5E20"],
    [0.20, "#43A047"],
    [0.32, "#9CCC65"],
    [0.45, "#FDD835"],
    [0.58, "#FB8C00"],
    [0.72, "#E53935"],
    [0.86, "#B71C1C"],
    [1.00, "#5E0A0A"],
]


def band(score: float) -> str:
    for lo, label, _ in BANDS:
        if score >= lo:
            return label
    return "LOW"


def band_color(score: float) -> str:
    return BAND_COLOR[band(score)]


FONT_IMPORT = (
    "https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400"
    "&family=Playfair+Display:wght@500;700&family=Nunito+Sans:wght@300;400;600;700&display=swap"
)

CSS = f"""
<style>
@import url('{FONT_IMPORT}');
:root {{
  --navy:{NAVY}; --midnight:{MIDNIGHT}; --panel:{PANEL}; --slate:{SLATE};
  --gold:{GOLD}; --gold-l:{GOLD_LIGHT}; --sand:{SAND}; --ivory:{IVORY}; --mist:{MIST};
}}
html, body, [class*="css"], .stMarkdown, .stText, p, li, label, input, textarea {{
  font-family: 'Nunito Sans', 'Avenir', 'Helvetica Neue', Arial, sans-serif;
}}
.stApp {{ background: radial-gradient(1200px 600px at 10% -10%, #14307a33, transparent 60%), {MIDNIGHT}; }}
h1, h2, h3, h4 {{ font-family: 'EB Garamond', 'Playfair Display', Georgia, serif !important; color: {IVORY}; letter-spacing: .2px; }}
h1 {{ font-weight: 600; }}
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {NAVY} 0%, {MIDNIGHT} 100%); border-right: 1px solid {GOLD}55; }}
section[data-testid="stSidebar"] * {{ color: {IVORY}; }}
div[data-testid="stMetric"] {{ background: {PANEL}; border: 1px solid {GOLD}40; border-radius: 6px; padding: 10px 14px; }}
div[data-testid="stMetricLabel"] p {{ color: {GOLD_LIGHT} !important; text-transform: uppercase; font-size: .72rem; letter-spacing: 1.2px; }}
div[data-testid="stMetricValue"] {{ font-family: 'EB Garamond', serif; color: {IVORY}; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {GOLD}55; }}
.stTabs [data-baseweb="tab"] {{ background: {PANEL}; border-radius: 4px 4px 0 0; padding: 6px 14px; }}
.stTabs [aria-selected="true"] {{ background: {NAVY}; border-bottom: 2px solid {GOLD_LIGHT}; }}
a {{ color: {SAND} !important; }}
hr {{ border-color: {GOLD}55; }}

.ksg-banner {{ border-bottom: 1px solid {GOLD}80; padding: 4px 0 14px 0; margin-bottom: 18px; display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:10px; }}
.ksg-kicker {{ color:{GOLD_LIGHT}; font-size:.72rem; letter-spacing:3px; text-transform:uppercase; font-weight:600; }}
.ksg-title {{ font-family:'EB Garamond',serif; font-size:2.25rem; color:{IVORY}; line-height:1.1; margin:2px 0 0 0; }}
.ksg-sub {{ color:{MIST}; font-size:.9rem; margin-top:4px; }}
.ksg-clock {{ text-align:right; color:{MIST}; font-size:.78rem; line-height:1.45; font-variant-numeric: tabular-nums; }}
.ksg-clock b {{ color:{SAND}; font-weight:600; }}

.ksg-card {{ background:{PANEL}; border:1px solid {GOLD}33; border-radius:6px; padding:14px 16px; margin-bottom:10px; }}
.ksg-card h4 {{ margin:0 0 6px 0; font-size:1.15rem; }}
.ksg-muted {{ color:{MIST}; font-size:.85rem; }}

.brief-item {{ display:grid; grid-template-columns: 38px 1fr; gap:12px; padding:12px 4px; border-bottom:1px solid {SLATE}; }}
.brief-num {{ font-family:'EB Garamond',serif; font-size:1.5rem; color:{GOLD_LIGHT}; text-align:center; line-height:1.1; }}
.brief-head {{ color:{IVORY}; font-weight:600; font-size:.98rem; line-height:1.35; }}
.brief-head a {{ color:{IVORY} !important; text-decoration:none; border-bottom:1px dotted {GOLD_LIGHT}; }}
.brief-meta {{ color:{MIST}; font-size:.76rem; margin-top:3px; }}
.brief-sowhat {{ color:{SAND}; font-size:.86rem; margin-top:5px; }}
.brief-next {{ color:{MIST}; font-size:.82rem; margin-top:3px; font-style:italic; }}

.chip {{ display:inline-block; padding:1px 8px; border-radius:10px; font-size:.68rem; font-weight:700; letter-spacing:.8px; margin-right:6px; color:#fff; vertical-align:middle; }}
.chip-theme {{ background:{SLATE}; color:{IVORY}; font-weight:600; }}
.chip-gold {{ background:{GOLD}; }}

.ladder {{ display:flex; gap:4px; margin:6px 0 12px 0; flex-wrap:wrap; }}
.rung {{ flex:1 1 110px; padding:8px 6px; font-size:.72rem; text-align:center; border-radius:4px; background:{PANEL}; color:{MIST}; border:1px solid {SLATE}; min-height:52px; display:flex; align-items:center; justify-content:center; }}
.rung.past {{ background:{SLATE}; color:{IVORY}; }}
.rung.now {{ background:{TERRACOTTA}; color:#fff; border:1px solid {SAND}; font-weight:700; box-shadow:0 0 0 2px {GOLD}55; }}

.ksg-footer {{ margin-top:28px; padding-top:10px; border-top:1px solid {GOLD}55; color:{GREY}; font-size:.74rem; }}
</style>
"""


def plotly_layout(**overrides):
    """Base Plotly layout in house style."""
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Nunito Sans, Avenir, Arial", color=IVORY, size=12),
        title_font=dict(family="EB Garamond, Georgia, serif", size=18, color=IVORY),
        margin=dict(l=10, r=10, t=40, b=10),
        colorway=[GOLD_LIGHT, "#6C8EBF", TERRACOTTA, SAND, "#8FB3A2", "#C7A4D8", MIST],
        xaxis=dict(gridcolor="#1E2F66", zerolinecolor="#2A3D7A", linecolor="#2A3D7A"),
        yaxis=dict(gridcolor="#1E2F66", zerolinecolor="#2A3D7A", linecolor="#2A3D7A"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=NAVY, bordercolor=GOLD_LIGHT, font=dict(color=IVORY)),
    )
    if isinstance(overrides.get("title"), str):
        # keep house title font (a bare string title would replace the whole title object)
        overrides["title"] = dict(text=overrides["title"], font=base.pop("title_font"))
    base.update(overrides)
    return base
