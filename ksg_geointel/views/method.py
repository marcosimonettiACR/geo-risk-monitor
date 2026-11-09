"""Methodology & Sources."""
import pandas as pd
import streamlit as st

from core.feeds import FEEDS
from core.risk import DEFAULT_WEIGHTS
from data.brief import BRIEF_AS_OF, SOURCES
from views.common import footer, header, show_df

header("Methodology & Sources", "How the scores are built, what they can and cannot tell you.")

w = st.session_state.get("weights", DEFAULT_WEIGHTS)
st.markdown(f"""
#### 1 · Collection
- **{len(FEEDS)} newswire RSS/Atom feeds** (BBC, NYT, Guardian, Al Jazeera, DW, France 24, CNBC, UN News, regional specialists, defence & shipping trade press). Refreshed every 15 minutes.
- **GDELT DOC 2.0 API**: up to 250 English-language articles worldwide matching an escalation query (missiles, sanctions, blockade, coup…). On the Country Dossier page it also returns 30-day volume and tone timelines.
- **World Bank Worldwide Governance Indicators**: *Political Stability & Absence of Violence* (PV.EST), the most recent value per country.
- **Markets**: Yahoo Finance via `yfinance`, with Stooq as a fallback.

#### 2 · Tagging
Each item is tagged to countries using names, demonyms, capitals, leaders and institutions (for example IRGC → Iran, PLA → China). It is then scored against an escalation/de-escalation lexicon, so 'ballistic missile' and 'blockade' push the score up while 'ceasefire' and 'talks' pull it down. Each item gets up to three themes (Military, Shipping, Energy, Sanctions & Trade, Cyber & Hybrid, Political, Health, Macro, Diplomacy).

#### 3 · Composite country score (0–100)
`composite = {w['structural']:.2f}·Structural + {w['governance']:.2f}·WB stability + {w['live']:.2f}·Live heat + {w['escalation']:.2f}·Escalation`

| Component | What it captures | Source |
|---|---|---|
| Structural | Analyst baseline of war, regime fragility, sanctions and chokepoints (as of {BRIEF_AS_OF}) | `data/countries.py` |
| WB stability | Inverted PV.EST: (2.5 − est) / 5 × 100 | World Bank |
| Live heat | 100·(1 − e^(−raw/14)), where raw = Σ recency-decayed (36h half-life) escalation-weighted mentions. Floored at structural − 15, so news silence is (nearly) neutral | Wires + GDELT |
| Escalation | Max theatre intensity × participation, plus 15% of the other theatres (dropped if the country is in no theatre) | `data/theatres.py` |

Missing components are dropped and the remaining weights re-normalised. Live data can move a country at most +25 / −10 points from its structural baseline, so a single viral story cannot repaint the map, and under-reported wars are not scored down for being under-reported. Bands: **Severe ≥75 · High ≥60 · Elevated ≥45 · Moderate ≥30 · Low <30**.

#### 4 · The 12-point brief
Items from the last 72 hours are ranked by *escalation relevance × country risk × recency (14h half-life) × source reliability*. Near-duplicate headlines are clustered (Jaccard ≥0.42), and corroboration by several outlets boosts the cluster. At most three items per country keeps the brief diverse. An optional Claude pass rewrites the wire into analyst prose with 'so what' and 'what next'.

#### 5 · Escalation & strike-back
For each theatre there is a hand-built escalation ladder, retaliation options (actor → action → target, probability, severity, horizon, market channels, tripwire) and a scenario tree with indicative first-order market moves. The 'If X happens' simulator applies `p' = 1 − (1 − p)^(1 + k·severity)`, where k depends on whether an option is a direct retaliation, follow-through or spill-over.

#### 6 · Limitations
- Keyword NLP is fast and transparent but cruder than human reading. Treat live heat as a *where to look* signal, not a verdict.
- Media attention is biased toward English-language, Western-covered theatres. Sudan, the Sahel and Myanmar are under-reported relative to their severity, which is why the structural baseline carries the most weight.
- All probabilities are subjective analytical judgements. Nothing here is investment advice.
""")

st.markdown("#### Live feeds")
show_df(pd.DataFrame([(n, u, c) for n, (u, c, _) in FEEDS.items()], columns=["feed", "url", "category"]), hide_index=True)

st.markdown(f"#### Research sources for the analyst baseline ({BRIEF_AS_OF})")
for title, url in SOURCES:
    st.markdown(f"- [{title}]({url})")
footer()
