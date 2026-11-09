"""Country Dossier — score decomposition, drivers, strike-back exposure, live GDELT pulse."""
import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from core.theme import GOLD_LIGHT, TERRACOTTA, band, band_color, plotly_layout
from data.countries import COUNTRIES, COUNTRY_BY_ISO
from data.theatres import THEATRES
from views.common import (chip, footer, gauge, get_intel, header, level_chip, load_gdelt_country,
                          show_df, show_fig)

header("Country Dossier", "Score decomposition, drivers, retaliation exposure and the live media pulse.")

intel = get_intel()
df = intel["risk"].set_index("iso3")

opts = sorted(COUNTRIES, key=lambda c: -df.loc[c["iso3"], "composite"] if c["iso3"] in df.index else 0)
labels = {c["iso3"]: f"{c['name']}  ·  {df.loc[c['iso3'], 'composite']:.0f}" for c in opts if c["iso3"] in df.index}
iso = st.selectbox("Country", list(labels), format_func=labels.get, index=0)
c = COUNTRY_BY_ISO[iso]
row = df.loc[iso]

a, b, d = st.columns([1, 1.25, 1.35], gap="large")
with a:
    show_fig(gauge(row["composite"], f"{c['name']} — composite"), key="g")
    st.markdown(f"{level_chip(row['band'])} {chip(c['region'], cls='chip-theme')} rank #{int(row['rank'])} of {len(df)}",
                unsafe_allow_html=True)
with b:
    comps = pd.DataFrame({
        "component": ["Structural", "WB stability", "Live heat", "Escalation"],
        "score": [row["structural"], row["governance"] if pd.notna(row["governance"]) else None, row["live"], row["escalation"]],
    })
    fig = go.Figure(go.Bar(x=comps["score"], y=comps["component"], orientation="h",
                           marker_color=[band_color(v) if v is not None and pd.notna(v) else "#555" for v in comps["score"]],
                           text=[f"{v:.0f}" if v is not None and pd.notna(v) else "n/a" for v in comps["score"]],
                           textposition="outside"))
    fig.update_layout(**plotly_layout(height=240, title="Score decomposition", xaxis=dict(range=[0, 110], gridcolor="#1E2F66")))
    show_fig(fig, key="decomp")
    st.caption(f"Live Δ vs baseline: **{row['delta']:+.1f}** · {int(row['mentions'])} stories in window · "
               f"media tone {row['tone']:+.2f} (−1 escalatory … +1 de-escalatory)")
with d:
    st.markdown(f"""<div class="ksg-card"><h4>Key drivers</h4><div>{html.escape(c['drivers'])}</div></div>
    <div class="ksg-card"><h4>Market exposures</h4><div class="ksg-muted">{html.escape(c['exposures'])}</div></div>""",
                unsafe_allow_html=True)

# ── Theatres & strike-back chains involving this country ────────────────────
st.markdown("### Escalation theatres & strike-back exposure")
inv = [t for t in THEATRES if iso in t["participants"]]
if not inv:
    st.caption("No active escalation theatre involves this country in the current register.")
rows = []
for t in sorted(inv, key=lambda t: -t["intensity"] * t["participants"][iso]):
    st.markdown(f"""<div class="ksg-card"><h4>{chip(band(t['intensity']), band_color(t['intensity']))}{t['name']}
    <span class="ksg-muted"> · exposure {t['participants'][iso]:.0%}</span></h4>
    <div class="ksg-muted">{t['status']}</div></div>""", unsafe_allow_html=True)
    for r in t["retaliation"]:
        if iso in (r["actor_iso"], r["target_iso"]):
            rows.append({"theatre": t["name"].split("·")[0].strip(),
                         "role": "Actor" if r["actor_iso"] == iso else "Target",
                         "actor": r["actor"], "action": r["action"], "target": r["target"],
                         "probability": r["prob"] * 100, "severity": r["severity"], "horizon": r["horizon"],
                         "market channels": ", ".join(r["channels"]), "tripwire": r["tripwire"]})
if rows:
    try:
        from streamlit import column_config as cc
        cfg = {"probability": cc.ProgressColumn("Prob. %", min_value=0, max_value=100, format="%.0f%%"),
               "severity": cc.NumberColumn("Sev. (1–5)")}
    except Exception:  # noqa: BLE001
        cfg = None
    show_df(pd.DataFrame(rows), hide_index=True, column_config=cfg)

# ── Live GDELT pulse ─────────────────────────────────────────────────────────
st.markdown("### Live media pulse (GDELT, 30 days)")
query = f'"{c["name"]}"' if " " in c["name"] else c["name"]
if st.toggle("Load GDELT pulse for this country", value=True, help="One volume + one tone + one article query (cached 15 min)."):
    g = load_gdelt_country(query + " sourcelang:english")
    if g["error"]:
        st.warning(f"GDELT unavailable right now: {g['error']}")
    if g["vol"]:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        vd = pd.DataFrame(g["vol"], columns=["date", "articles"])
        fig.add_trace(go.Bar(x=vd["date"], y=vd["articles"], name="Article volume", marker_color=GOLD_LIGHT, opacity=0.55), secondary_y=False)
        if g["tone"]:
            td = pd.DataFrame(g["tone"], columns=["date", "tone"])
            fig.add_trace(go.Scatter(x=td["date"], y=td["tone"], name="Avg tone", line=dict(color=TERRACOTTA, width=2)), secondary_y=True)
        fig.update_layout(**plotly_layout(height=320, legend=dict(orientation="h", y=1.1)))
        fig.update_yaxes(title_text="articles", secondary_y=False, gridcolor="#1E2F66")
        fig.update_yaxes(title_text="tone (− negative)", secondary_y=True, showgrid=False)
        show_fig(fig, key="pulse")
    arts = g["articles"][:15]
    if arts:
        st.markdown("**Latest coverage (72h)**")
        for x in arts:
            ts = x["published"].strftime("%d %b %H:%M") if x.get("published") else ""
            st.markdown(f"- [{x['title']}]({x['url']}) <span class='ksg-muted'>· {x['source']} · {ts}</span>", unsafe_allow_html=True)

wire = [h for h in intel["items"] if iso in h["countries"]]
_EPOCH = pd.Timestamp("1970-01-01", tz="UTC").to_pydatetime()
wire.sort(key=lambda h: h.get("published") or _EPOCH, reverse=True)
if wire:
    st.markdown("**From the newswires**")
    for x in wire[:12]:
        ts = x["published"].strftime("%d %b %H:%M") if x.get("published") else ""
        st.markdown(f"- [{x['title']}]({x['url']}) <span class='ksg-muted'>· {x['source']} · {ts}</span>", unsafe_allow_html=True)
footer()
