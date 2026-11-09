"""Escalation & Strike-back — ladders, retaliation matrices, a strike-back map,
a conditional 'if X happens' simulator, scenario trees with market EV and
cross-theatre contagion."""
import html
import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.theme import GOLD_LIGHT, IVORY, MIDNIGHT, RISK_SCALE, band, band_color, plotly_layout
from data.countries import COUNTRY_BY_ISO
from data.theatres import THEATRES
from views.common import chip, footer, header, show_df, show_fig

header("Escalation & Strike-back Matrix",
       "Who can hit back, how, with what probability, and what it does to markets.")

theatres = sorted(THEATRES, key=lambda t: -t["intensity"])
names = {t["id"]: f"{t['name']}  ·  intensity {t['intensity']}" for t in theatres}
tid = st.selectbox("Theatre", list(names), format_func=names.get)
t = next(x for x in theatres if x["id"] == tid)

# ── Summary + ladder ─────────────────────────────────────────────────────────
st.markdown(f"""<div class="ksg-card"><h4>{chip(band(t['intensity']), band_color(t['intensity']))}{html.escape(t['name'])}</h4>
<div class="ksg-muted" style="margin-bottom:6px">{html.escape(t['status'])}</div>
<div>{html.escape(t['summary'])}</div></div>""", unsafe_allow_html=True)

st.markdown("**Escalation ladder** — current rung highlighted")
rungs = "".join(
    f'<div class="rung {"now" if i == t["current_rung"] else "past" if i < t["current_rung"] else ""}">{i + 1}. {html.escape(r)}</div>'
    for i, r in enumerate(t["ladder"]))
st.markdown(f'<div class="ladder">{rungs}</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚔️ Retaliation options", "🗺 Strike-back map", "🎯 If X happens…",
                                        "🌳 Scenarios & market EV", "🕸 Contagion"])

ret = pd.DataFrame(t["retaliation"])
ret["prob %"] = ret["prob"] * 100
ret["expected severity"] = ret["prob"] * ret["severity"]

# ── 1. Retaliation table + probability × severity matrix ─────────────────────
with tab1:
    c1, c2 = st.columns([1.25, 1], gap="large")
    with c1:
        tbl = ret[["actor", "action", "target", "prob %", "severity", "horizon", "channels", "tripwire"]].copy()
        tbl["channels"] = tbl["channels"].apply(", ".join)
        try:
            from streamlit import column_config as cc
            cfg = {"prob %": cc.ProgressColumn("Prob.", min_value=0, max_value=100, format="%.0f%%"),
                   "severity": cc.NumberColumn("Sev. 1–5")}
        except Exception:  # noqa: BLE001
            cfg = None
        show_df(tbl.sort_values("prob %", ascending=False), hide_index=True, column_config=cfg)
    with c2:
        fig = px.scatter(ret, x="prob %", y="severity", size=[18] * len(ret), color="expected severity",
                         color_continuous_scale=RISK_SCALE, range_color=(0, 4), hover_name="action",
                         hover_data={"actor": True, "target": True, "prob %": ":.0f", "expected severity": ":.2f"},
                         text=ret["actor"].str.split("/").str[0].str.strip())
        fig.add_shape(type="rect", x0=50, x1=100, y0=3.5, y1=5.5, fillcolor="rgba(198,40,40,0.12)", line_width=0)
        fig.add_annotation(x=75, y=5.35, text="Act-now quadrant", showarrow=False, font=dict(color=GOLD_LIGHT, size=11))
        fig.update_traces(textposition="top center", textfont=dict(size=10, color=IVORY))
        fig.update_layout(**plotly_layout(height=430, title="Probability × severity",
                                          xaxis=dict(range=[0, 100], title="probability (%)", gridcolor="#1E2F66"),
                                          yaxis=dict(range=[0.5, 5.5], title="severity", dtick=1, gridcolor="#1E2F66"),
                                          coloraxis_showscale=False))
        show_fig(fig, key="pxs")
    st.markdown("**Indicators & warnings to watch**")
    st.markdown(" ".join(chip(html.escape(i), cls="chip-theme") for i in t["indicators"]), unsafe_allow_html=True)

# ── 2. Strike-back map ───────────────────────────────────────────────────────
with tab2:
    scope = st.radio("Show", ["This theatre", "All theatres"], horizontal=True)
    src = [t] if scope == "This theatre" else theatres
    fig = go.Figure()
    nodes = {}
    for th in src:
        for r in th["retaliation"]:
            a, b = COUNTRY_BY_ISO.get(r["actor_iso"]), COUNTRY_BY_ISO.get(r["target_iso"])
            if not a or not b or a["iso3"] == b["iso3"]:
                continue
            col = band_color(min(100, r["prob"] * 100 * 0.5 + r["severity"] * 12))
            fig.add_trace(go.Scattergeo(
                lon=[a["lon"], b["lon"]], lat=[a["lat"], b["lat"]], mode="lines",
                line=dict(width=1 + 6 * r["prob"], color=col), opacity=0.85,
                hoverinfo="text", text=f"{r['actor']} → {r['target']}<br>{r['action']}<br>p={r['prob']:.0%} · sev {r['severity']}",
                showlegend=False))
            # arrow head (target marker)
            fig.add_trace(go.Scattergeo(lon=[b["lon"]], lat=[b["lat"]], mode="markers",
                                        marker=dict(size=6 + 10 * r["prob"], color=col, symbol="triangle-down"),
                                        hoverinfo="skip", showlegend=False))
            nodes[a["iso3"]] = a
            nodes[b["iso3"]] = b
    fig.add_trace(go.Scattergeo(lon=[n["lon"] for n in nodes.values()], lat=[n["lat"] for n in nodes.values()],
                                text=[n["name"] for n in nodes.values()], mode="markers+text", textposition="top center",
                                textfont=dict(color=IVORY, size=10), marker=dict(size=7, color=GOLD_LIGHT,
                                line=dict(color=MIDNIGHT, width=1)), hoverinfo="text", showlegend=False))
    fig.update_geos(projection_type="natural earth", showland=True, landcolor="#1a2550", showocean=True,
                    oceancolor=MIDNIGHT, showcountries=True, countrycolor="rgba(255,255,255,0.18)",
                    showcoastlines=False, showframe=False, bgcolor="rgba(0,0,0,0)",
                    fitbounds="locations" if scope == "This theatre" else False)
    fig.update_layout(**plotly_layout(height=560, margin=dict(l=0, r=0, t=10, b=0)))
    show_fig(fig, key="sbmap")
    st.caption("Line width = probability; colour = probability × severity (green→red); triangle = target.")

# ── 3. Conditional simulator ─────────────────────────────────────────────────
with tab3:
    st.markdown("Pick a **trigger** — assume it happens — and see how the other strike-back options re-price. "
                "Heuristic: an option whose actor is the *victim* of the trigger is a direct retaliation and gets the "
                "biggest uplift; options by the trigger's own side get a smaller momentum uplift.")
    trig_i = st.selectbox("Trigger event", range(len(t["retaliation"])),
                          format_func=lambda i: f"{t['retaliation'][i]['actor']} — {t['retaliation'][i]['action']}")
    trig = t["retaliation"][trig_i]
    sim = []
    for i, r in enumerate(t["retaliation"]):
        if i == trig_i:
            continue
        if r["actor_iso"] == trig["target_iso"] or r["target_iso"] == trig["actor_iso"]:
            k, why = 0.45 * trig["severity"], "Direct retaliation"
        elif r["actor_iso"] == trig["actor_iso"]:
            k, why = 0.20 * trig["severity"], "Follow-through / momentum"
        else:
            k, why = 0.10 * trig["severity"], "Spill-over"
        p_new = 1 - (1 - r["prob"]) ** (1 + k)
        sim.append({"option": f"{r['actor']} — {r['action']}", "link": why,
                    "before %": r["prob"] * 100, "after %": p_new * 100, "Δ pp": (p_new - r["prob"]) * 100,
                    "severity": r["severity"]})
    sim = pd.DataFrame(sim).sort_values("after %", ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(y=sim["option"], x=sim["before %"], orientation="h", name="Before", marker_color="#4A5A8A"))
    fig.add_trace(go.Bar(y=sim["option"], x=sim["after %"], orientation="h", name="After trigger", marker_color="#E53935"))
    fig.update_layout(**plotly_layout(height=110 + 48 * len(sim), barmode="overlay",
                                      xaxis=dict(range=[0, 100], title="probability %", gridcolor="#1E2F66"),
                                      yaxis=dict(autorange="reversed"), legend=dict(orientation="h", y=1.08)))
    fig.update_traces(opacity=0.85)
    show_fig(fig, key="sim")
    show_df(sim, hide_index=True)
    # escalation of the whole theatre
    rung_jump = 1 if trig["severity"] >= 4 else 0
    new_rung = min(len(t["ladder"]) - 1, t["current_rung"] + rung_jump)
    st.markdown(f"Implied ladder position after trigger: **{new_rung + 1}. {t['ladder'][new_rung]}**"
                + (" (one rung up)" if rung_jump else " (no change)"))

# ── 4. Scenarios & EV ────────────────────────────────────────────────────────
with tab4:
    sc = t["scenarios"]
    st.markdown("Adjust probabilities to your own view — they're re-normalised to 100%.")
    cols = st.columns(len(sc))
    raw = []
    for col, s in zip(cols, sc):
        with col:
            raw.append(st.slider(s["name"], 0, 100, int(round(s["prob"] * 100)), 5, key=f"sc_{tid}_{s['name']}"))
            st.caption(s["desc"])
    tot = sum(raw) or 1
    probs = [r / tot for r in raw]
    ev = {k: sum(p * s[k] for p, s in zip(probs, sc)) for k in ("brent", "gold", "spx")}
    m1, m2, m3 = st.columns(3)
    m1.metric("Expected Brent move", f"{ev['brent']:+.1f} $/bbl")
    m2.metric("Expected gold move", f"{ev['gold']:+.1f}%")
    m3.metric("Expected S&P 500 move", f"{ev['spx']:+.1f}%")
    fig = go.Figure()
    for k, lab, col in (("brent", "Brent ($/bbl)", "#C62828"), ("gold", "Gold (%)", GOLD_LIGHT), ("spx", "S&P 500 (%)", "#6C8EBF")):
        fig.add_trace(go.Bar(x=[s["name"] for s in sc], y=[s[k] for s in sc], name=lab, marker_color=col))
    fig.update_layout(**plotly_layout(height=360, barmode="group", title="Indicative first-order market impact by scenario",
                                      legend=dict(orientation="h", y=1.12)))
    show_fig(fig, key="scen")
    tail = max(sc, key=lambda s: abs(s["spx"]))
    st.caption(f"Tail scenario: **{tail['name']}**. Probability-weighted EV hides fat tails; size hedges to the tail, not the mean. "
               "Impacts are illustrative first-order moves, not forecasts or advice.")

# ── 5. Contagion matrix ──────────────────────────────────────────────────────
with tab5:
    ids = [x["id"] for x in theatres]
    labs = [x["name"].split("·")[0].strip()[:28] for x in theatres]
    M = np.zeros((len(ids), len(ids)))
    for i, a in enumerate(theatres):
        for j, b in enumerate(theatres):
            if i == j:
                continue
            shared = set(a["participants"]) & set(b["participants"])
            M[i, j] = sum(math.sqrt(a["participants"][c] * b["participants"][c]) for c in shared) * \
                math.sqrt(a["intensity"] * b["intensity"]) / 100
    fig = go.Figure(go.Heatmap(z=M, x=labs, y=labs, colorscale=[[0, MIDNIGHT], [0.5, "#7a5a2b"], [1, "#E53935"]],
                               hovertemplate="%{y} ↔ %{x}<br>linkage %{z:.2f}<extra></extra>"))
    fig.update_layout(**plotly_layout(height=560, title="Cross-theatre contagion (shared actors × intensity)",
                                      xaxis=dict(tickangle=-40), yaxis=dict(autorange="reversed")))
    show_fig(fig, key="contagion")
    i = ids.index(tid)
    order = np.argsort(-M[i])[:4]
    st.markdown("**Most likely contagion paths from this theatre:** " +
                ", ".join(f"{labs[j]} ({M[i, j]:.2f})" for j in order if M[i, j] > 0))
footer()
