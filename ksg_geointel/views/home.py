"""Command Brief — home page: KPIs, the 12-point brief and the satellite risk map."""
import html

import streamlit as st

from core import llm
from core.markets import geo_stress
from core.risk import global_index
from core.theme import band, band_color
from data.brief import ANALYST_BRIEF, BRIEF_AS_OF
from data.theatres import THEATRES
from views.common import (band_legend, chip, footer, get_intel, header, level_chip, load_markets,
                          risk_map, show_df)

header("Command Brief", "Twelve things a finance client needs to know right now — and what happens next.")

intel = get_intel()
df = intel["risk"]
prices, snap, msrc = load_markets()

# ── KPI strip ────────────────────────────────────────────────────────────────
gidx = global_index(df)
n_severe = int((df["band"] == "SEVERE").sum())
n_high = int((df["band"] == "HIGH").sum())
hot = max(THEATRES, key=lambda t: t["intensity"])
stress = geo_stress(snap)

def _asset(name):
    if snap is None or snap.empty or name not in set(snap["asset"]):
        return None
    return snap.set_index("asset").loc[name]

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Global geo-risk index", f"{gidx:.0f}/100", band(gidx), delta_color="off")
k2.metric("Countries Severe / High", f"{n_severe} / {n_high}")
k3.metric("Hottest theatre", hot["name"].split("·")[0].strip(), f"intensity {hot['intensity']}", delta_color="off")
b = _asset("Brent crude")
k4.metric("Brent", f"${b['last']:.2f}" if b is not None else "—", f"{b['1w %']:+.1f}% 1w" if b is not None else None)
g = _asset("Gold")
k5.metric("Gold", f"${g['last']:,.0f}" if g is not None else "—", f"{g['1w %']:+.1f}% 1w" if g is not None else None)
k6.metric("Market geo-stress", f"{stress:.0f}/100" if stress is not None else "—",
          "heuristic · 5d z-scores", delta_color="off")

src_ok = sum(1 for v in intel["rss_status"].values() if v.startswith("ok"))
gdelt_note = " + GDELT" if not intel["gdelt_err"] else f" (GDELT: {intel['gdelt_err']})"
wgi_note = "✓" if intel["wgi_ok"] else "✗ (baseline used)"
st.caption(
    f"Live collection: **{intel['n_items']:,}** items from **{src_ok}/{len(intel['rss_status'])}** newswires"
    f"{gdelt_note} · World Bank stability data {wgi_note} · markets: {msrc}"
    f" · collected {intel['fetched_at']:%H:%M} UTC"
)

left, right = st.columns([1.05, 1], gap="large")

# ── The 12-point brief ───────────────────────────────────────────────────────
with left:
    st.markdown("### The 12-Point Brief")
    tab_live, tab_ai, tab_base = st.tabs(["📡 Live wire (auto)", "🧠 AI analyst", f"🗂 Analyst baseline · {BRIEF_AS_OF}"])

    with tab_live:
        top = intel["top12"]
        if len(top) < 6:
            st.warning("Live feeds returned too little to rank — showing the analyst baseline instead.")
            top = []
        for i, h in enumerate(top, 1):
            ctry = ", ".join(df.set_index("iso3").loc[c, "name"] for c in h["countries"][:3] if c in set(df["iso3"])) or "Global"
            lvl = band(max([df.set_index("iso3").loc[c, "composite"] for c in h["countries"] if c in set(df["iso3"])] or [30]))
            themes = "".join(chip(t, cls="chip-theme") for t in h["themes"][:2])
            age = f"{h['age_h']:.0f}h ago" if h["age_h"] >= 1 else "<1h ago"
            corro = f" · corroborated by {h['n_sources']} sources" if h["n_sources"] > 1 else ""
            st.markdown(
                f"""<div class="brief-item"><div class="brief-num">{i:02d}</div><div>
                <div class="brief-head">{level_chip(lvl)}<a href="{html.escape(h.get('url') or '#')}" target="_blank">{html.escape(h['title'])}</a></div>
                <div class="brief-meta">{html.escape(ctry)} · {html.escape(h['source'])} · {age}{corro} {themes}</div>
                <div class="brief-sowhat">▸ So what: {html.escape(h.get('so_what') or 'Monitor for market transmission')}</div>
                </div></div>""",
                unsafe_allow_html=True,
            )
        if not top:
            for i, b_ in enumerate(ANALYST_BRIEF, 1):
                st.markdown(f"**{i:02d}. {b_['tag']}** — {b_['what']}")
        st.caption("Ranking = escalation relevance × country risk × recency (14h half-life) × source weight, "
                   "near-duplicates clustered (corroboration boosts), max 3 items per country.")

    with tab_ai:
        key = ""
        try:
            key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:  # noqa: BLE001
            pass
        key = key or st.session_state.get("anthropic_key", "")
        if not key:
            st.info("Add an Anthropic API key in the sidebar (or `ANTHROPIC_API_KEY` in Streamlit secrets) and "
                    "Claude will turn the live wire into a 12-point analyst brief with 'so what' and 'what next'.")
        elif st.button("Generate analyst brief from live wire"):
            ranked = sorted(intel["items"], key=lambda x: (x.get("published") is not None, x["esc"]), reverse=True)
            ranked = [h for h in ranked if h["countries"] or h["esc"] >= 2.5][:60]
            risks = list(zip(df["name"], df["composite"]))
            try:
                with st.spinner("Claude is drafting the brief…"):
                    st.session_state["ai_brief"] = llm.claude_brief(key, ranked, risks)
            except Exception as exc:  # noqa: BLE001
                st.error(f"AI brief failed: {exc}")
        for i, b_ in enumerate(st.session_state.get("ai_brief", []), 1):
            st.markdown(
                f"""<div class="brief-item"><div class="brief-num">{i:02d}</div><div>
                <div class="brief-head">{level_chip(str(b_.get('level','ELEVATED')))}{chip(html.escape(str(b_.get('theatre',''))), cls='chip-theme')}{html.escape(str(b_['headline']))}</div>
                <div class="brief-sowhat">▸ So what: {html.escape(str(b_.get('so_what','')))}</div>
                <div class="brief-next">Next: {html.escape(str(b_.get('next','')))} · confidence {html.escape(str(b_.get('confidence','—')))}</div>
                </div></div>""", unsafe_allow_html=True)

    with tab_base:
        for i, b_ in enumerate(ANALYST_BRIEF, 1):
            st.markdown(
                f"""<div class="brief-item"><div class="brief-num">{i:02d}</div><div>
                <div class="brief-head">{level_chip(b_['level'])}{chip(b_['tag'], cls='chip-theme')}{html.escape(b_['what'])}</div>
                <div class="brief-sowhat">▸ So what: {html.escape(b_['so_what'])}</div>
                <div class="brief-next">Next: {html.escape(b_['next'])}</div>
                </div></div>""", unsafe_allow_html=True)

# ── Map + movers ─────────────────────────────────────────────────────────────
with right:
    st.markdown("### Global Risk Exposure")
    style = st.radio("View", ["Satellite", "Globe", "Flat"], horizontal=True, label_visibility="collapsed", key="home_style")
    risk_map(df, intel["geojson"], "composite", height=520, style=style, key="home_map")
    band_legend()

    st.markdown("#### Heating up vs. cooling (live Δ vs structural)")
    seeded = df[df["seeded"]]
    c1, c2 = st.columns(2)
    up = seeded.sort_values("delta", ascending=False).head(6)[["name", "composite", "delta", "mentions"]]
    dn = seeded.sort_values("delta").head(6)[["name", "composite", "delta", "mentions"]]
    with c1:
        st.caption("🔺 Heating up")
        show_df(up.rename(columns={"name": "Country", "composite": "Score", "delta": "Δ", "mentions": "Stories"}), hide_index=True)
    with c2:
        st.caption("🔻 Quieter than baseline")
        show_df(dn.rename(columns={"name": "Country", "composite": "Score", "delta": "Δ", "mentions": "Stories"}), hide_index=True)

    st.markdown("#### Active theatres")
    for t in sorted(THEATRES, key=lambda x: -x["intensity"])[:6]:
        st.markdown(
            f"""<div class="ksg-card"><h4>{chip(band(t['intensity']), band_color(t['intensity']))}{t['name']}</h4>
            <div class="ksg-muted">{t['status']}</div></div>""", unsafe_allow_html=True)

footer()
