"""Geo-sensitive market data (Yahoo Finance via yfinance, Stooq CSV fallback)."""
from __future__ import annotations

import io
import math

import numpy as np
import pandas as pd
import requests

# label: (yahoo ticker, stooq fallback, group, geo channel)
ASSETS = {
    "Brent crude": ("BZ=F", "cb.f", "Energy", "Hormuz · Red Sea · Russia"),
    "WTI crude": ("CL=F", "cl.f", "Energy", "Hormuz · US policy"),
    "TTF gas (EU)": ("TTF=F", None, "Energy", "Russia–Ukraine · Qatar LNG"),
    "Henry Hub gas": ("NG=F", "ng.f", "Energy", "US LNG exports"),
    "Gold": ("GC=F", "gc.f", "Havens", "Systemic geo-risk"),
    "Silver": ("SI=F", "si.f", "Havens", "Geo-risk / industrial"),
    "Copper": ("HG=F", "hg.f", "Metals", "China · DRC · Chile"),
    "Wheat": ("ZW=F", "zw.f", "Agri", "Black Sea · Red Sea"),
    "Soybeans": ("ZS=F", "zs.f", "Agri", "US–China trade"),
    "VIX": ("^VIX", None, "Risk", "Equity fear gauge"),
    "S&P 500": ("^GSPC", "^spx", "Equities", "Global risk appetite"),
    "Euro Stoxx 50": ("^STOXX50E", None, "Equities", "Europe / Ukraine"),
    "Nikkei 225": ("^N225", "^nkx", "Equities", "Japan / Taiwan"),
    "Taiwan TAIEX": ("^TWII", None, "Equities", "Taiwan Strait"),
    "Semis (SOXX)": ("SOXX", None, "Equities", "Taiwan · US–China tech"),
    "US Defence (ITA)": ("ITA", None, "Equities", "Conflict demand"),
    "Tankers (FRO)": ("FRO", None, "Shipping", "Hormuz · Red Sea"),
    "Dollar index": ("DX-Y.NYB", None, "FX", "Haven USD"),
    "USD/JPY": ("JPY=X", "usdjpy", "FX", "Haven / BoJ intervention"),
    "USD/CNH": ("CNH=X", None, "FX", "US–China"),
    "EUR/USD": ("EURUSD=X", "eurusd", "FX", "Europe energy"),
    "US 10Y yield": ("^TNX", None, "Rates", "Stagflation / Fed"),
    "Bitcoin": ("BTC-USD", None, "Alt", "Liquidity / sanctions"),
}


def _yf_history(tickers: list[str], period: str) -> pd.DataFrame:
    import yfinance as yf  # optional dependency

    data = yf.download(tickers, period=period, interval="1d", auto_adjust=False,
                       progress=False, group_by="column", threads=True)
    if data is None or data.empty:
        return pd.DataFrame()
    close = data["Close"] if isinstance(data.columns, pd.MultiIndex) else data[["Close"]].rename(columns={"Close": tickers[0]})
    return close.dropna(how="all")


def _stooq(symbol: str) -> pd.Series | None:
    try:
        r = requests.get(f"https://stooq.com/q/d/l/?s={symbol}&i=d", timeout=10,
                         headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200 or not r.text.startswith("Date"):
            return None
        df = pd.read_csv(io.StringIO(r.text), parse_dates=["Date"]).set_index("Date")
        return df["Close"].tail(260)
    except Exception:  # noqa: BLE001
        return None


def fetch_prices(period: str = "6mo") -> tuple[pd.DataFrame, str]:
    """Returns (DataFrame of closes with columns = asset labels, source note)."""
    labels = list(ASSETS)
    tickers = [ASSETS[l][0] for l in labels]
    try:
        raw = _yf_history(tickers, period)
        if not raw.empty:
            inv = {ASSETS[l][0]: l for l in labels}
            raw = raw.rename(columns=inv)
            return raw[[c for c in labels if c in raw.columns]], "Yahoo Finance (yfinance)"
    except Exception:  # noqa: BLE001
        pass
    cols = {}
    for l in labels:
        sym = ASSETS[l][1]
        if sym:
            s = _stooq(sym)
            if s is not None and not s.empty:
                cols[l] = s
    if cols:
        return pd.DataFrame(cols).sort_index(), "Stooq (fallback)"
    return pd.DataFrame(), "unavailable"


def snapshot(prices: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in prices.columns:
        s = prices[col].dropna()
        if len(s) < 3:
            continue
        last = s.iloc[-1]

        def chg(n):
            return (last / s.iloc[-1 - n] - 1) * 100 if len(s) > n else np.nan

        rets = np.log(s).diff().dropna()
        vol20 = rets.tail(20).std() * math.sqrt(252) * 100 if len(rets) >= 20 else np.nan
        # z-score of the latest 5-day move vs the 6-month distribution of 5-day moves
        r5 = np.log(s).diff(5).dropna()
        z5 = (r5.iloc[-1] - r5.mean()) / r5.std() if len(r5) > 20 and r5.std() > 0 else np.nan
        _, _, group, channel = ASSETS.get(col, ("", "", "", ""))
        rows.append({"asset": col, "group": group, "geo channel": channel, "last": last,
                     "1d %": chg(1), "1w %": chg(5), "1m %": chg(21), "vol 20d %": vol20, "5d z": z5})
    return pd.DataFrame(rows)


def geo_stress(snap: pd.DataFrame) -> float | None:
    """Heuristic 0–100 'geo-stress' from abnormal moves in geo-sensitive havens
    and energy. Positive weight = stress when the asset rises."""
    weights = {"Brent crude": 1.0, "Gold": 1.0, "VIX": 1.2, "TTF gas (EU)": 0.6, "Tankers (FRO)": 0.4,
               "US Defence (ITA)": 0.4, "S&P 500": -1.0, "USD/JPY": -0.4}
    if snap is None or snap.empty:
        return None
    z = snap.set_index("asset")["5d z"].dropna()
    num = sum(w * z[a] for a, w in weights.items() if a in z)
    den = sum(abs(w) for a, w in weights.items() if a in z)
    if den == 0:
        return None
    s = num / den  # ~N(0,1)
    return float(100 / (1 + math.exp(-1.6 * s)))
