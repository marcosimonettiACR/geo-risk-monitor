"""Live open-source collection: RSS/Atom newswires + GDELT DOC 2.0 API.

No API keys required. Everything degrades gracefully: a feed that times out
or changes format is skipped and reported, never fatal.
"""
from __future__ import annotations

import html
import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET

import requests

UA = "Mozilla/5.0 (X11; Linux x86_64) GeoRiskMonitor/1.0 (+streamlit)"
HEADERS = {"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8"}

# name: (url, category, reliability weight 0.6–1.2)
FEEDS: dict[str, tuple[str, str, float]] = {
    "BBC World": ("https://feeds.bbci.co.uk/news/world/rss.xml", "Global", 1.1),
    "Al Jazeera": ("https://www.aljazeera.com/xml/rss/all.xml", "Global", 1.0),
    "The Guardian World": ("https://www.theguardian.com/world/rss", "Global", 1.0),
    "NYT World": ("https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "Global", 1.1),
    "NYT Business": ("https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "Markets", 1.0),
    "DW World": ("https://rss.dw.com/rdf/rss-en-world", "Global", 1.0),
    "France 24": ("https://www.france24.com/en/rss", "Global", 1.0),
    "CNBC World": ("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100727362", "Markets", 1.0),
    "CNBC Economy": ("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258", "Markets", 0.9),
    "UN News": ("https://news.un.org/feed/subscribe/en/news/all/rss.xml", "Multilateral", 1.0),
    "Politico Europe": ("https://www.politico.eu/feed/", "Europe", 0.9),
    "Kyiv Independent": ("https://kyivindependent.com/news-archive/rss/", "Russia–Ukraine", 0.9),
    "Times of Israel": ("https://www.timesofisrael.com/feed/", "Middle East", 0.9),
    "Al-Monitor": ("https://www.al-monitor.com/rss", "Middle East", 0.9),
    "SCMP China": ("https://www.scmp.com/rss/4/feed", "Asia-Pacific", 0.9),
    "Focus Taiwan": ("https://focustaiwan.tw/rss/aall.xml", "Asia-Pacific", 0.9),
    "The Diplomat": ("https://thediplomat.com/feed/", "Asia-Pacific", 0.9),
    "Defense News": ("https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml", "Defence", 0.9),
    "Breaking Defense": ("https://breakingdefense.com/feed/", "Defence", 0.9),
    "War on the Rocks": ("https://warontherocks.com/feed/", "Analysis", 0.8),
    "Foreign Policy": ("https://foreignpolicy.com/feed/", "Analysis", 0.9),
    "gCaptain (shipping)": ("https://gcaptain.com/feed/", "Shipping", 1.0),
    "OilPrice": ("https://oilprice.com/rss/main", "Energy", 0.8),
    "Africanews": ("https://www.africanews.com/feed/rss", "Africa", 0.8),
    "MercoPress": ("https://en.mercopress.com/rss", "Americas", 0.8),
}

GDELT_DOC = "https://api.gdeltproject.org/api/v2/doc/doc"

GDELT_GLOBAL_QUERY = (
    '(missile OR airstrike OR "air strike" OR sanctions OR blockade OR coup OR ceasefire OR invasion '
    'OR tariff OR "export controls" OR drone OR warship OR mobilization OR insurgents OR hostage '
    'OR "naval" OR "nuclear") sourcelang:english'
)

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def clean_text(text: str | None) -> str:
    if not text:
        return ""
    text = html.unescape(_TAG_RE.sub(" ", text))
    return _WS_RE.sub(" ", text).strip()


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower() if tag else ""


def _child_text(el, *names) -> str:
    for ch in el:
        if _local(ch.tag) in names:
            if _local(ch.tag) == "link" and ch.get("href"):
                return ch.get("href")
            return (ch.text or "").strip()
    return ""


def _parse_date(s: str) -> datetime | None:
    if not s:
        return None
    s = s.strip()
    try:
        d = parsedate_to_datetime(s)
        if d is not None:
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError, IndexError):
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%f%z", "%Y%m%dT%H%M%SZ", "%Y-%m-%d"):
        try:
            d = datetime.strptime(s.replace("Z", "+0000") if "%z" in fmt else s, fmt)
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def parse_feed(xml_bytes: bytes, source: str, category: str = "", weight: float = 1.0) -> list[dict]:
    """Parse RSS 2.0, RSS 1.0/RDF or Atom into normalised items."""
    root = ET.fromstring(xml_bytes)
    items = [el for el in root.iter() if _local(el.tag) in ("item", "entry")]
    out = []
    for it in items:
        title = clean_text(_child_text(it, "title"))
        if not title:
            continue
        link = _child_text(it, "link") or _child_text(it, "guid", "id")
        summary = clean_text(_child_text(it, "description", "summary", "content", "encoded"))[:400]
        pub = _parse_date(_child_text(it, "pubdate", "published", "updated", "date", "issued"))
        out.append({
            "title": title,
            "url": link,
            "summary": summary,
            "published": pub,
            "source": source,
            "category": category,
            "weight": weight,
            "origin": "RSS",
        })
    return out


def fetch_feed(name: str, url: str, category: str = "", weight: float = 1.0, timeout: float = 8.0) -> tuple[str, list[dict], str | None]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return name, parse_feed(r.content, name, category, weight), None
    except Exception as exc:  # noqa: BLE001 — any failure just skips the feed
        return name, [], f"{type(exc).__name__}: {str(exc)[:120]}"


def fetch_all_feeds(feeds: dict | None = None, max_workers: int = 10) -> tuple[list[dict], dict]:
    """Fetch every feed concurrently. Returns (items, status{name: ok|error})."""
    feeds = feeds or FEEDS
    items, status = [], {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(fetch_feed, n, u, c, w) for n, (u, c, w) in feeds.items()]
        for f in as_completed(futs):
            name, got, err = f.result()
            items.extend(got)
            status[name] = err or f"ok · {len(got)} items"
    return items, status


# ── GDELT ────────────────────────────────────────────────────────────────────
_gdelt_lock = threading.Lock()
_gdelt_last = [0.0]
GDELT_MIN_INTERVAL = 5.5  # GDELT asks for ≤1 request / 5 s


class GdeltError(RuntimeError):
    pass


def _gdelt_get(params: dict, timeout: float = 25.0) -> dict:
    with _gdelt_lock:
        wait = GDELT_MIN_INTERVAL - (time.time() - _gdelt_last[0])
        if wait > 0:
            time.sleep(wait)
        try:
            r = requests.get(GDELT_DOC, params=params, headers={"User-Agent": UA}, timeout=timeout)
        finally:
            _gdelt_last[0] = time.time()
    txt = r.text.strip()
    if r.status_code == 429 or txt.lower().startswith("please limit"):
        raise GdeltError("GDELT rate limit — try again shortly")
    if r.status_code != 200:
        raise GdeltError(f"GDELT HTTP {r.status_code}")
    if not txt or not txt.startswith("{"):
        raise GdeltError(f"GDELT returned non-JSON: {txt[:120]}")
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        # GDELT occasionally emits stray control characters
        return json.loads(re.sub(r"[\x00-\x1f]", " ", txt))


def gdelt_articles(query: str = GDELT_GLOBAL_QUERY, timespan: str = "24h", maxrecords: int = 200,
                   sort: str = "hybridrel") -> list[dict]:
    data = _gdelt_get({"query": query, "mode": "artlist", "format": "json",
                       "maxrecords": str(min(maxrecords, 250)), "timespan": timespan, "sort": sort})
    out = []
    for a in data.get("articles", []) or []:
        title = clean_text(a.get("title"))
        if not title:
            continue
        out.append({
            "title": title,
            "url": a.get("url", ""),
            "summary": "",
            "published": _parse_date(a.get("seendate", "")),
            "source": a.get("domain", "GDELT"),
            "category": f"GDELT · {a.get('sourcecountry', '')}".strip(" ·"),
            "weight": 0.85,
            "origin": "GDELT",
        })
    return out


def gdelt_timeline(query: str, mode: str = "timelinevolraw", timespan: str = "30d"):
    """Return list of (datetime, value) for a GDELT timeline mode."""
    data = _gdelt_get({"query": query, "mode": mode, "format": "json", "timespan": timespan})
    series = (data.get("timeline") or [{}])[0].get("data", []) or []
    out = []
    for p in series:
        d = _parse_date(p.get("date", ""))
        if d is not None:
            out.append((d, float(p.get("value", 0) or 0)))
    return out


def dedupe_by_url(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for it in items:
        key = (it.get("url") or it["title"]).split("?")[0].rstrip("/").lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


# ── World Bank: Political Stability & Absence of Violence (WGI PV.EST) ──────
WB_URLS = [
    "https://api.worldbank.org/v2/country/all/indicator/PV.EST?format=json&mrnev=1&per_page=500&source=3",
    "https://api.worldbank.org/v2/country/all/indicator/GOV_WGI_PV.EST?format=json&mrnev=1&per_page=500",
]


def fetch_wgi_stability() -> dict[str, float]:
    """ISO3 -> PV.EST (approx −2.5 unstable … +2.5 stable). Empty dict on failure."""
    for url in WB_URLS:
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
            payload = r.json()
            if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
                continue
            out = {}
            for row in payload[1]:
                iso = row.get("countryiso3code") or ""
                val = row.get("value")
                if len(iso) == 3 and val is not None:
                    out[iso] = float(val)
            if out:
                return out
        except Exception:  # noqa: BLE001
            continue
    return {}
