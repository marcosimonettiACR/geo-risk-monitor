"""Market Transmission — geo-sensitive assets, abnormal moves and theatre→asset mapping."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.markets import geo_stress
from core.theme import GOLD_LIGHT, IVORY, plotly_layout
from data.theatres import THEATRES
from views.common import footer, header, load_markets, show_df, show_fig

header("Market Transmission", "How geopolitics is (or isn't) being priced — energy, havens, freight, FX and equities.")

prices, snap, src = load_markets()
if prices.empty:
    st.warning("Market data unavailable right now (Yahoo Finance/Stooq unreachable). The rest of the dashboard still works.")
    footer()
    st.stop()

stress = geo_stress(snap)
c1, c2, c3 = st.columns([1, 1, 2])
c1.metric("Market geo-stress", f"{stress:.0f}/100" if stress is not None else "—")
c2.metric("Assets tracked", len(snap))
c3.caption(f"Source: {src}. Geo-stress = logistic of a weighted average of 5-day z-scores "
           "(Brent, gold, VIX, TTF, tankers, defence up; S&P 500 & USD/JPY down). 50 = normal.")

try:
    from streamlit import column_config as cc
    cfg = {"last": cc.NumberColumn("Last", format="%.2f"),
           "1d %": cc.NumberColumn(format="%+.2f"), "1w %": cc.NumberColumn(format="%+.2f"),
           "1m %": cc.NumberColumn(format="%+.2f"), "vol 20d %": cc.NumberColumn(format="%.1f"),
           "5d z": cc.NumberColumn("5d move z-score", format="%+.2f")}
except Exception:  # noqa: BLE001
    cfg = None
show_df(snap.sort_values(["group", "asset"]), hide_index=True, column_config=cfg, height=520)

st.markdown("### Rebased performance (6 months = 100)")
default = [a for a in ["Brent crude", "Gold", "TTF gas (EU)", "Tankers (FRO)", "US Defence (ITA)", "S&P 500"] if a in prices.columns]
pick = st.multiselect("Assets", list(prices.columns), default=default)
if pick:
    rb = prices[pick].ffill().dropna(how="all")
    rb = rb / rb.bfill().iloc[0] * 100
    fig = go.Figure()
    for col in pick:
        fig.add_trace(go.Scatter(x=rb.index, y=rb[col], name=col, mode="lines", line=dict(width=2)))
    fig.add_hline(y=100, line_dash="dot", line_color="#556")
    fig.update_layout(**plotly_layout(height=430, legend=dict(orientation="h", y=1.1)))
    show_fig(fig, key="rb")

st.markdown("### Abnormal moves (5-day z-score)")
z = snap.dropna(subset=["5d z"]).sort_values("5d z")
fig = go.Figure(go.Bar(x=z["5d z"], y=z["asset"], orientation="h",
                       marker_color=["#C62828" if v > 1.5 else "#2E7D32" if v < -1.5 else "#4A5A8A" for v in z["5d z"]]))
fig.add_vline(x=1.5, line_dash="dot", line_color=GOLD_LIGHT)
fig.add_vline(x=-1.5, line_dash="dot", line_color=GOLD_LIGHT)
fig.update_layout(**plotly_layout(height=560, xaxis_title="z-score of latest 5-day move vs 6-month history"))
show_fig(fig, key="z")

st.markdown("### Theatre → asset transmission map")
rows = []
for t in sorted(THEATRES, key=lambda x: -x["intensity"]):
    chans = sorted({c for r in t["retaliation"] for c in r["channels"]})
    ev_b = sum(s["prob"] * s["brent"] for s in t["scenarios"])
    ev_s = sum(s["prob"] * s["spx"] for s in t["scenarios"])
    rows.append({"theatre": t["name"], "intensity": t["intensity"], "channels": ", ".join(chans),
                 "EV Brent $": round(ev_b, 1), "EV S&P %": round(ev_s, 1)})
show_df(pd.DataFrame(rows), hide_index=True)
st.caption("EV columns use the analyst scenario trees on the Escalation page (default probabilities).")
footer()
