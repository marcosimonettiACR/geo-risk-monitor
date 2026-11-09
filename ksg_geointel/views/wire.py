"""Intelligence Wire — every collected item, tagged, scored and filterable."""
import html
from collections import Counter

import pandas as pd
import plotly.express as px
import streamlit as st

from core.theme import GOLD_LIGHT, plotly_layout
from views.common import chip, country_name, footer, get_intel, header, show_df, show_fig

header("Intelligence Wire", "All collected open-source reporting — tagged by country, theme and escalation weight.")

intel = get_intel()
items = intel["items"]

themes = sorted({t for i in items for t in i["themes"]})
countries = sorted({c for i in items for c in i["countries"]}, key=country_name)
sources = sorted({i["source"] for i in items})

f1, f2, f3, f4 = st.columns([1.2, 1.2, 1.2, 1.4])
sel_c = f1.multiselect("Country", countries, format_func=country_name)
sel_t = f2.multiselect("Theme", themes)
sel_s = f3.multiselect("Source", sources)
q = f4.text_input("Keyword", placeholder="e.g. Hormuz, tariff, drone")
min_esc = st.slider("Minimum escalation score", 0.0, 10.0, 0.0, 0.5)
sort = st.radio("Sort", ["Newest", "Most escalatory", "Most de-escalatory"], horizontal=True)

v = items
if sel_c:
    v = [i for i in v if set(i["countries"]) & set(sel_c)]
if sel_t:
    v = [i for i in v if set(i["themes"]) & set(sel_t)]
if sel_s:
    v = [i for i in v if i["source"] in sel_s]
if q:
    v = [i for i in v if q.lower() in (i["title"] + " " + i.get("summary", "")).lower()]
v = [i for i in v if i["esc"] >= min_esc]
_EPOCH = pd.Timestamp("1970-01-01", tz="UTC").to_pydatetime()
key = {"Newest": lambda i: i.get("published") or _EPOCH,
       "Most escalatory": lambda i: i["esc"], "Most de-escalatory": lambda i: i["deesc"]}[sort]
v = sorted(v, key=key, reverse=True)

st.caption(f"{len(v):,} of {len(items):,} items")
c1, c2 = st.columns([1.6, 1], gap="large")
with c1:
    for i in v[:150]:
        ts = i["published"].strftime("%d %b %H:%M UTC") if i.get("published") else "time n/a"
        ctry = " ".join(chip(html.escape(country_name(c)), cls="chip-gold") for c in i["countries"][:3])
        th = " ".join(chip(t, cls="chip-theme") for t in i["themes"][:2])
        esc = f"esc {i['esc']:.1f}" + (f" · de-esc {i['deesc']:.1f}" if i["deesc"] else "")
        st.markdown(
            f"""<div class="brief-item" style="grid-template-columns: 1fr"><div>
            <div class="brief-head"><a href="{html.escape(i.get('url') or '#')}" target="_blank">{html.escape(i['title'])}</a></div>
            <div class="brief-meta">{html.escape(i['source'])} · {ts} · {esc} &nbsp;{ctry} {th}</div>
            {f'<div class="ksg-muted" style="margin-top:4px">{html.escape(i["summary"][:260])}</div>' if i.get('summary') else ''}
            </div></div>""", unsafe_allow_html=True)
with c2:
    cnt = Counter(c for i in v for c in i["countries"]).most_common(15)
    if cnt:
        d = pd.DataFrame(cnt, columns=["iso3", "stories"])
        d["country"] = d["iso3"].map(country_name)
        fig = px.bar(d, x="stories", y="country", orientation="h", color_discrete_sequence=[GOLD_LIGHT])
        fig.update_layout(**plotly_layout(height=430, title="Most-reported countries", yaxis=dict(autorange="reversed")))
        show_fig(fig, key="cnt")
    tc = Counter(t for i in v for t in i["themes"]).most_common()
    if tc:
        fig = px.pie(pd.DataFrame(tc, columns=["theme", "n"]), names="theme", values="n", hole=0.55)
        fig.update_layout(**plotly_layout(height=330, title="Theme mix"))
        show_fig(fig, key="themes")
    with st.expander("Feed health"):
        show_df(pd.DataFrame(sorted(intel["rss_status"].items()), columns=["feed", "status"]), hide_index=True)
        st.caption(f"GDELT: {intel['gdelt_err'] or 'ok'}")
footer()
