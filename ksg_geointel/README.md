# Geopolitical Intelligence & Risk Monitor

A live geopolitical-risk dashboard for finance clients, built in Python/Streamlit and styled after the
Knightsbridge Strategic Group palette (royal navy `#102763`, midnight `#020436`, bronze-gold `#9C7741`,
EB Garamond headings).

> Independent prototype — not an official KSG product. Open-source intelligence only. Not investment advice.

## What's inside

| Page | What it does |
|---|---|
| **Command Brief** (home) | KPI strip (global geo-risk index, Severe/High count, Brent, gold, market geo-stress), the **12-point brief** (live auto-ranked wire · optional Claude analyst rewrite · dated analyst baseline), **satellite map** red→green, countries heating up vs cooling, active theatres |
| **Global Risk Map** | Full-screen Esri satellite choropleth (or globe/flat), metric switcher (composite, structural, live heat, escalation, live Δ), regional zoom, sortable league table |
| **Country Dossier** | Gauge + score decomposition, drivers, market exposures, every strike-back option where the country is actor or target, 30-day GDELT volume & tone, latest coverage |
| **Escalation & Strike-back** | 15 theatres with escalation ladders, retaliation matrices (probability × severity), a strike-back flow map, an **"If X happens…" conditional simulator**, editable scenario trees with expected Brent / gold / S&P moves, cross-theatre contagion heatmap |
| **Intelligence Wire** | Every collected item tagged by country/theme/escalation score with filters; feed-health panel |
| **Market Transmission** | 23 geo-sensitive assets (energy, havens, freight, FX, defence, semis), abnormal-move z-scores, theatre→asset EV table |
| **Calendar & Watchlist** | Dated catalysts and per-theatre tripwires |
| **Methodology & Sources** | Model maths, limitations, feed list, research sources |

### Live data (no API keys needed)
- 25 RSS/Atom newswires (BBC, NYT, Guardian, Al Jazeera, DW, France 24, CNBC, UN News, Kyiv Independent, Times of Israel, SCMP, Focus Taiwan, The Diplomat, Defense News, gCaptain, OilPrice, Africanews…)
- GDELT DOC 2.0 global event stream (≈250 articles per refresh + per-country timelines)
- World Bank WGI Political Stability
- Yahoo Finance via `yfinance` (Stooq fallback)
- Optional: Claude (Anthropic API) for analyst-prose briefs

Everything is cached for 15 minutes and refreshes automatically; the sidebar has a manual **Refresh** button.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Share it — deploy free on Streamlit Community Cloud
1. Create a new GitHub repository (public or private) and upload the contents of this folder
   (keep the structure: `app.py`, `core/`, `data/`, `views/`, `.streamlit/config.toml`, `requirements.txt`).
2. Go to **share.streamlit.io** → *Create app* → pick the repo, branch `main`, main file `app.py` → *Deploy*.
3. (Optional) *App settings → Secrets* → paste `ANTHROPIC_API_KEY = "sk-ant-…"` to enable the AI analyst tab.
4. Share the `https://<your-app>.streamlit.app` link. Under *Settings → Sharing* you can make it public or
   invite specific emails.

## Updating the intelligence
- `data/countries.py` — structural baseline score, drivers and exposures per country (≈95 countries).
- `data/theatres.py` — theatres, escalation ladders, retaliation options (probabilities/severity/tripwires), scenario trees.
- `data/brief.py` — the dated 12-point analyst baseline, calendar and source list.
- `core/feeds.py` — add/remove newswires.

## Tests
```bash
python tests/test_core.py      # or: python -m pytest -q
```
