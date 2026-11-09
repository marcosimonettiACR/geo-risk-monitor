"""Shared Streamlit plumbing: cached data loaders, the intelligence pipeline,
house-style header/footer and the satellite risk map."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import feeds, geo, markets, nlp, risk
from core.theme import (BAND_COLOR, BANDS, GOLD_LIGHT, IVORY, MIDNIGHT, NAVY, RISK_SCALE,
                        plotly_layout)
from data.countries import COUNTRIES, COUNTRY_BY_ISO, DEFAULT_BASE
from data.theatres import THEATRES

APP_TITLE = "Geopolitical Intelligence & Risk Monitor"
APP_KICKER = "Strategic Intelligence · Finance Desk"

TTL_NEWS = 900        # 15 min
TTL_MARKETS = 900
TTL_SLOW = 86_400     # 24 h


# ── helpers ──────────────────────────────────────────────────────────────────
def show_fig(fig, key: str | None = None):
    """plotly_chart across Streamlit versions (width= vs use_container_width=)."""
    try:
        st.plotly_chart(fig, width="stretch", key=key, config={"displaylogo": False})
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, key=key, config={"displaylogo": False})


def show_df(df, **kw):
    try:
        st.dataframe(df, width="stretch", **kw)
    except TypeError:
        st.dataframe(df, use_container_width=True, **kw)


def chip(label: str, color: str | None = None, cls: str = "") -> str:
    style = f' style="background:{color}"' if color else ""
    return f'<span class="chip {cls}"{style}>{label}</span>'


def level_chip(level: str) -> str:
    return chip(level, BAND_COLOR.get(level.upper(), "#555"))


def settings() -> dict:
    """Sidebar-controlled settings live in session_state (set in app.py)."""
    ss = st.session_state
    return {
        "weights": ss.get("weights", risk.DEFAULT_WEIGHTS),
        "gdelt_on": ss.get("gdelt_on", True),
        "timespan": ss.get("timespan", "48h"),
    }


# ── cached loaders ───────────────────────────────────────────────────────────
@st.cache_data(ttl=TTL_NEWS, show_spinner="Collecting newswires…")
def load_rss():
    items, status = feeds.fetch_all_feeds()
    return items, status, datetime.now(timezone.utc)


@st.cache_data(ttl=TTL_NEWS, show_spinner="Querying GDELT global event stream…")
def load_gdelt(timespan: str):
    try:
        return feeds.gdelt_articles(timespan=timespan, maxrecords=250), None
    except Exception as exc:  # noqa: BLE001
        return [], str(exc)


@st.cache_data(ttl=TTL_NEWS, show_spinner="Querying GDELT…")
def load_gdelt_country(query: str, timespan: str = "30d"):
    out = {"articles": [], "vol": [], "tone": [], "error": None}
    try:
        out["vol"] = feeds.gdelt_timeline(query, "timelinevolraw", timespan)
        out["tone"] = feeds.gdelt_timeline(query, "timelinetone", timespan)
        out["articles"] = feeds.gdelt_articles(query, timespan="72h", maxrecords=40, sort="datedesc")
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)
    return out


@st.cache_data(ttl=TTL_SLOW, show_spinner="Loading world boundaries…")
def load_geojson():
    return geo.load_world_geojson()


@st.cache_data(ttl=TTL_SLOW * 7, show_spinner="Loading World Bank governance data…")
def load_wgi():
    return feeds.fetch_wgi_stability()


@st.cache_data(ttl=TTL_MARKETS, show_spinner="Pulling market data…")
def load_markets():
    prices, src = markets.fetch_prices("6mo")
    return prices, markets.snapshot(prices) if not prices.empty else pd.DataFrame(), src


@st.cache_resource
def country_index():
    return nlp.build_country_index(COUNTRIES)


# ── the pipeline ─────────────────────────────────────────────────────────────
def get_intel() -> dict:
    """Collect → tag → score → rank. Cached pieces underneath; this glue is cheap."""
    cfg = settings()
    rss_items, rss_status, fetched_at = load_rss()
    gdelt_items, gdelt_err = (load_gdelt(cfg["timespan"]) if cfg["gdelt_on"] else ([], "disabled"))
    items = feeds.dedupe_by_url(rss_items + gdelt_items)
    analysed = nlp.analyse(items, country_index())
    heat = nlp.country_heat(analysed)

    gj = load_geojson()
    wgi = load_wgi()
    exposure = risk.theatre_exposure(THEATRES)

    universe = [dict(c) for c in COUNTRIES]
    seen = {c["iso3"] for c in universe}
    for iso, name in geo.universe_from_geojson(gj):
        if iso not in seen:
            universe.append({"iso3": iso, "name": name, "region": "Other", "base": None, "mkt": 1})
            seen.add(iso)
    df = risk.compute_risk(universe, heat, wgi, exposure, cfg["weights"], DEFAULT_BASE)
    lookup = dict(zip(df["iso3"], df["composite"]))
    top12 = nlp.rank_headlines(analysed, lookup, limit=12)
    exposures = {c["iso3"]: c["exposures"] for c in COUNTRIES}
    for h in top12:
        h["so_what"] = nlp.so_what(h, exposures)
    return {
        "items": analysed, "top12": top12, "heat": heat, "risk": df, "geojson": gj,
        "wgi_ok": bool(wgi), "rss_status": rss_status, "gdelt_err": gdelt_err,
        "fetched_at": fetched_at, "n_items": len(analysed), "exposure": exposure,
    }


# ── header / footer ──────────────────────────────────────────────────────────
def header(title: str, subtitle: str = ""):
    now = datetime.now(timezone.utc)
    sgt = now + timedelta(hours=8)
    ldn = now  # UK is on GMT in November
    nyc = now - timedelta(hours=5)
    st.markdown(
        f"""<div class="ksg-banner">
        <div><div class="ksg-kicker">{APP_KICKER}</div>
        <div class="ksg-title">{title}</div>
        <div class="ksg-sub">{subtitle}</div></div>
        <div class="ksg-clock"><b>UTC</b> {now:%d %b %Y · %H:%M}<br>
        <b>London</b> {ldn:%H:%M} · <b>New York</b> {nyc:%H:%M} · <b>Singapore</b> {sgt:%H:%M}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        """<div class="ksg-footer">Independent prototype styled after Knightsbridge Strategic Group's
        visual identity — not an official KSG product. Open-source intelligence only (newswires, GDELT,
        World Bank, Yahoo Finance). Scores and probabilities are analytical judgements for discussion,
        not investment advice.</div>""",
        unsafe_allow_html=True,
    )


# ── maps ─────────────────────────────────────────────────────────────────────
def risk_map(df: pd.DataFrame, gj: dict | None, metric: str = "composite", height: int = 560,
             style: str = "Satellite", center=None, zoom: float = 0.9, key: str = "map"):
    hover = {"composite": ":.0f", "structural": ":.0f", "live": ":.0f", "escalation": ":.0f",
             "band": True, "iso3": False}
    rng = (-25, 25) if metric == "delta" else (0, 100)
    scale = "RdYlGn_r" if metric == "delta" else RISK_SCALE
    title_map = {"composite": "Composite risk", "structural": "Structural", "live": "Live heat",
                 "escalation": "Escalation exposure", "delta": "Live Δ vs baseline"}

    if style == "Satellite" and gj is not None and hasattr(px, "choropleth_map"):
        fig = px.choropleth_map(
            df, geojson=gj, locations="iso3", featureidkey="id", color=metric,
            color_continuous_scale=scale, range_color=rng, hover_name="name", hover_data=hover,
            map_style="white-bg", zoom=zoom, center=center or {"lat": 22, "lon": 25}, opacity=0.62,
        )
        fig.update_layout(map_layers=[
            {"below": "traces", "sourcetype": "raster", "sourceattribution": "Esri, Maxar, Earthstar Geographics",
             "source": [geo.ESRI_IMAGERY]},
        ])
        fig.update_traces(marker_line_width=0.4, marker_line_color="rgba(255,255,255,0.35)")
    elif style == "Satellite" and gj is not None and hasattr(px, "choropleth_mapbox"):
        fig = px.choropleth_mapbox(
            df, geojson=gj, locations="iso3", featureidkey="id", color=metric,
            color_continuous_scale=scale, range_color=rng, hover_name="name", hover_data=hover,
            mapbox_style="white-bg", zoom=zoom, center=center or {"lat": 22, "lon": 25}, opacity=0.62,
        )
        fig.update_layout(mapbox_layers=[{"below": "traces", "sourcetype": "raster", "source": [geo.ESRI_IMAGERY]}])
    else:
        proj = "orthographic" if style == "Globe" else "natural earth"
        fig = px.choropleth(df, locations="iso3", color=metric, color_continuous_scale=scale,
                            range_color=rng, hover_name="name", hover_data=hover, projection=proj)
        fig.update_geos(bgcolor="rgba(0,0,0,0)", showocean=True, oceancolor=MIDNIGHT, showland=True,
                        landcolor="#1a2550", showcountries=True, countrycolor="rgba(255,255,255,0.25)",
                        showcoastlines=False, showframe=False, lataxis_range=[-58, 85] if proj != "orthographic" else None)
        if proj == "orthographic":
            fig.update_geos(projection_rotation=dict(lon=45, lat=22))
    fig.update_layout(**plotly_layout(height=height, margin=dict(l=0, r=0, t=0, b=0)),
                      coloraxis_colorbar=dict(title=title_map.get(metric, metric), thickness=12, len=0.6,
                                              tickfont=dict(color=IVORY), title_font=dict(color=GOLD_LIGHT),
                                              bgcolor="rgba(2,4,54,0.55)"))
    show_fig(fig, key=key)


def band_legend():
    parts = [chip(f"{label} ≥{lo}" if lo else f"{label} <30", color) for lo, label, color in BANDS]
    st.markdown(" ".join(parts), unsafe_allow_html=True)


def gauge(value: float, title: str = "Composite"):
    from core.theme import band_color
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value, number={"font": {"family": "EB Garamond", "size": 46, "color": IVORY}},
        title={"text": title, "font": {"color": GOLD_LIGHT, "size": 13}},
        gauge={"axis": {"range": [0, 100], "tickcolor": IVORY},
               "bar": {"color": band_color(value), "thickness": 0.3},
               "bgcolor": NAVY,
               "steps": [{"range": [lo, hi], "color": c + "55"} for (lo, _, c), hi in
                         zip(sorted(BANDS), [30, 45, 60, 75, 100])],
               "threshold": {"line": {"color": GOLD_LIGHT, "width": 3}, "value": value}},
    ))
    fig.update_layout(**plotly_layout(height=230, margin=dict(l=20, r=20, t=40, b=0)))
    return fig


def country_name(iso: str) -> str:
    c = COUNTRY_BY_ISO.get(iso)
    return c["name"] if c else iso
