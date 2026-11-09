"""Global Risk Map — full-width satellite choropleth with metric/region filters and league table."""
import plotly.express as px
import streamlit as st

from core.theme import BAND_COLOR, plotly_layout
from views.common import band_legend, footer, get_intel, header, risk_map, show_df, show_fig

header("Global Risk Map", "Every country scored red (heavy geopolitical exposure) → green (low). Satellite imagery: Esri World Imagery.")

intel = get_intel()
df = intel["risk"]

REGION_VIEW = {
    "World": ({"lat": 22, "lon": 25}, 0.9),
    "Middle East": ({"lat": 27, "lon": 46}, 3.0),
    "Europe/Eurasia": ({"lat": 52, "lon": 30}, 2.4),
    "Asia-Pacific": ({"lat": 20, "lon": 115}, 2.1),
    "Africa": ({"lat": 4, "lon": 20}, 2.1),
    "Americas": ({"lat": 8, "lon": -80}, 1.6),
}

c1, c2, c3 = st.columns([1.3, 1.2, 1])
metric = c1.selectbox("Metric", ["composite", "structural", "live", "escalation", "delta"],
                      format_func={"composite": "Composite risk", "structural": "Structural baseline",
                                   "live": "Live news heat", "escalation": "Escalation exposure",
                                   "delta": "Live Δ vs baseline"}.get)
region = c2.selectbox("Focus", list(REGION_VIEW))
style = c3.radio("Style", ["Satellite", "Globe", "Flat"], horizontal=True)

center, zoom = REGION_VIEW[region]
risk_map(df, intel["geojson"], metric, height=680, style=style, center=center, zoom=zoom, key="big_map")
band_legend()

st.markdown("### League table")
view = df if region == "World" else df[df["region"] == region]
f1, f2 = st.columns([1, 3])
only_seeded = f1.toggle("Analyst-covered countries only", value=True)
q = f2.text_input("Filter", placeholder="Search country…", label_visibility="collapsed")
if only_seeded:
    view = view[view["seeded"]]
if q:
    view = view[view["name"].str.contains(q, case=False)]

cols = ["rank", "name", "region", "band", "composite", "structural", "governance", "live", "escalation", "delta",
        "mentions", "live_themes", "theatres"]
try:
    from streamlit import column_config as cc
    colcfg = {
        "composite": cc.ProgressColumn("Composite", min_value=0, max_value=100, format="%.0f"),
        "structural": cc.NumberColumn("Structural", format="%.0f"),
        "governance": cc.NumberColumn("WB stability risk", format="%.0f"),
        "live": cc.NumberColumn("Live heat", format="%.0f"),
        "escalation": cc.NumberColumn("Escalation", format="%.0f"),
        "delta": cc.NumberColumn("Δ live", format="%+.1f"),
        "mentions": cc.NumberColumn("Stories"),
        "live_themes": "Live themes", "theatres": "Theatres", "name": "Country", "band": "Band",
    }
except Exception:  # noqa: BLE001
    colcfg = None
show_df(view[cols], hide_index=True, column_config=colcfg, height=520)

st.markdown("### Distribution by region")
reg = df[df["seeded"]].groupby(["region", "band"]).size().reset_index(name="countries")
fig = px.bar(reg, x="region", y="countries", color="band", color_discrete_map=BAND_COLOR,
             category_orders={"band": ["SEVERE", "HIGH", "ELEVATED", "MODERATE", "LOW"]})
fig.update_layout(**plotly_layout(height=340, legend_title_text=""))
show_fig(fig, key="regbar")
footer()
