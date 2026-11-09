"""Lightweight intelligence NLP: entity (country) tagging, escalation scoring,
theme classification, headline ranking/de-duplication and country 'heat'.

Deliberately dependency-free (regex + heuristics) so it runs on Streamlit
Community Cloud without heavy models.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict
from datetime import datetime, timezone

# ── Escalation lexicon: (pattern, weight, theme) ─────────────────────────────
# Positive weight = escalatory; negative = de-escalatory.
LEXICON = [
    (r"\bnuclear (?:test|strike|weapon|threat)s?\b|\bwarhead", 4.0, "Military"),
    (r"\binvasion\b|\binvade[sd]?\b|\bground offensive\b", 4.0, "Military"),
    (r"\bcoup\b|\bjunta\b|\bassassinat", 3.5, "Political"),
    (r"\bballistic missiles?\b|\bmissile (?:strike|attack|barrage)s?\b|\bhypersonic\b", 3.5, "Military"),
    (r"\bair ?strikes?\b|\bbombard|\bshelling\b|\bbombing\b", 3.0, "Military"),
    (r"\bkill(?:ed|s|ing)\b|\bdead\b|\bdeaths?\b|\bcasualt", 2.5, "Military"),
    (r"\bblockade\b|\bnaval mines?\b|\bmine strikes?\b|\bmined\b|\btankers? (?:hit|struck|attacked|seized)\b", 3.5, "Shipping"),
    (r"\bstrait of hormuz\b|\bhormuz\b|\bbab el-?mandeb\b|\bred sea\b|\bsuez\b|\bmalacca\b|\btaiwan strait\b", 2.0, "Shipping"),
    (r"\bdrones?\b|\buav\b|\bloitering munition", 2.0, "Military"),
    (r"\bwarships?\b|\bcarrier (?:group|strike)\b|\bdestroyer\b|\bfrigate\b|\bpla(?:n)?\b", 1.8, "Military"),
    (r"\bmobili[sz]ation\b|\btroops? (?:massing|deploy)|\bbuild-?up\b", 2.5, "Military"),
    (r"\bdrills?\b|\bexercises?\b|\blive-?fire\b|\bencircle", 1.8, "Military"),
    (r"\bstrikes? on\b|\battack(?:s|ed)? on\b|\bretaliat|\bescalat", 2.2, "Military"),
    (r"\bsanction(?:s|ed)?\b|\bembargo\b|\bentity list\b|\basset freeze", 2.0, "Sanctions & Trade"),
    (r"\btariffs?\b|\btrade war\b|\bexport controls?\b|\brare earths?\b|\bchip (?:ban|curbs)", 1.6, "Sanctions & Trade"),
    (r"\boil\b|\bcrude\b|\bbrent\b|\blng\b|\bgas (?:supply|prices?)\b|\bopec\+?\b|\brefiner(?:y|ies)\b|\bpipeline\b", 1.2, "Energy"),
    (r"\bcyber|\bhack(?:ed|ers|ing)\b|\bransomware\b|\bsabotage\b|\bsubsea cable", 2.2, "Cyber & Hybrid"),
    (r"\battack(?:s|ed)?\b", 1.2, "Military"),
    (r"\bprotests?\b|\bunrest\b|\briots?\b|\bcrackdown\b|\bstate of emergency\b", 1.6, "Political"),
    (r"\belection\b|\bimpeach|\bno-confidence\b|\bresign(?:s|ed|ation)\b|\bsnap poll\b", 1.0, "Political"),
    (r"\bebola\b|\boutbreak\b|\bpandemic\b|\bpheic\b|\bcholera\b", 2.2, "Health"),
    (r"\bdefault\b|\bdevaluation\b|\bcapital controls\b|\bbank run\b|\bimf bailout\b", 2.0, "Macro"),
    (r"\bfed\b|\brate hike\b|\binflation\b|\bcpi\b|\bpayrolls\b|\byields?\b", 0.6, "Macro"),
    (r"\bhostages?\b|\bterror(?:ist|ism)?\b|\bsuicide bomb", 3.0, "Military"),
    (r"\brefugees?\b|\bfamine\b|\bhumanitarian\b|\bdisplaced\b", 1.2, "Humanitarian"),
    # de-escalation
    (r"\bceasefire\b|\btruce\b|\barmistice\b", -2.0, "Diplomacy"),
    (r"\bpeace (?:talks|deal|plan|agreement)\b|\bnegotiat|\bmediat|\bdialogue\b|\btalks\b", -1.2, "Diplomacy"),
    (r"\bde-?escalat|\breopen(?:s|ed|ing)?\b|\bwithdraw(?:s|al|n)?\b|\bdeal\b|\bagreement\b|\bmou\b", -1.0, "Diplomacy"),
    (r"\bsanctions? (?:relief|lifted|eased)\b|\btariffs? (?:cut|paused|suspended)\b|\bextend(?:s|ed)? truce\b", -1.5, "Diplomacy"),
]
_LEX = [(re.compile(p, re.I), w, t) for p, w, t in LEXICON]

# Market transmission channels per theme (the "so what")
THEME_CHANNELS = {
    "Shipping": "Freight & tanker rates, war-risk premia, Brent",
    "Energy": "Brent/WTI, TTF gas, refining margins",
    "Military": "Gold, defence equities, regional FX/CDS",
    "Sanctions & Trade": "Tariff-exposed equities, CNH, commodities flows",
    "Cyber & Hybrid": "Critical-infrastructure & cyber insurance, utilities",
    "Political": "Local FX, sovereign spreads, equity risk premium",
    "Health": "Airlines, travel, EM FX, supply chains",
    "Macro": "Rates, USD, equity multiples",
    "Humanitarian": "Aid flows, regional stability, migration politics",
    "Diplomacy": "Risk-premium compression — fade hedges",
}


def build_country_index(countries: list[dict]) -> list[tuple[str, re.Pattern, re.Pattern | None]]:
    """Compile per-country regexes from names + aliases.

    Upper-case short aliases (US, UK, UAE, DRC, IRGC, PLA…) are matched
    case-sensitively to avoid false hits on ordinary words ("us").
    """
    index = []
    for c in countries:
        names = [c["name"]] + list(c.get("aliases", []))
        ci, cs = [], []
        for n in names:
            if not n:
                continue
            if n.isupper() or (len(n) <= 4 and n.upper() == n):
                cs.append(re.escape(n))
            else:
                ci.append(re.escape(n))
        pat_ci = re.compile(r"(?<![\w-])(?:" + "|".join(sorted(ci, key=len, reverse=True)) + r")(?![\w-])", re.I) if ci else None
        pat_cs = re.compile(r"(?<![\w.])(?:" + "|".join(sorted(cs, key=len, reverse=True)) + r")(?![\w])") if cs else None
        index.append((c["iso3"], pat_ci, pat_cs))
    return index


def tag_countries(text: str, index) -> list[str]:
    found = []
    for iso, pci, pcs in index:
        if (pci is not None and pci.search(text)) or (pcs is not None and pcs.search(text)):
            found.append(iso)
    # "South Korea"/"North Korea" both contain "Korea" — handled by aliases; ensure
    # South Sudan doesn't double-count as Sudan only when "South Sudan" present.
    if "SSD" in found and "SDN" in found and not re.search(r"(?<!South )\bSudan", text):
        found.remove("SDN")
    if "PRK" in found and "KOR" in found and not re.search(r"South Korea|Seoul", text, re.I):
        found.remove("KOR")
    return found


def score_text(text: str) -> tuple[float, list[str], float]:
    """Return (escalation score ≥0, themes, de-escalation magnitude ≥0)."""
    esc, deesc, themes = 0.0, 0.0, defaultdict(float)
    for rx, w, theme in _LEX:
        hits = len(rx.findall(text))
        if not hits:
            continue
        contribution = w * min(hits, 2)
        if w > 0:
            esc += contribution
        else:
            deesc += -contribution
        themes[theme] += abs(contribution)
    ordered = [t for t, _ in sorted(themes.items(), key=lambda kv: kv[1], reverse=True)]
    return esc, ordered[:3], deesc


def analyse(items: list[dict], index) -> list[dict]:
    out = []
    for it in items:
        text = f"{it['title']}. {it.get('summary', '')}"
        esc, themes, deesc = score_text(text)
        # Country tagging weighted toward the headline
        countries = tag_countries(it["title"], index) or tag_countries(text, index)
        out.append({**it, "countries": countries, "esc": esc, "deesc": deesc,
                    "net": esc - 0.6 * deesc, "themes": themes})
    return out


def _hours_ago(d: datetime | None, now: datetime) -> float:
    if d is None:
        return 18.0
    return max(0.0, (now - d).total_seconds() / 3600.0)


_TOKEN = re.compile(r"[a-z]{3,}")
_STOP = set("the and for with from that this after over into amid says said will has have are was were its their they new more than about what why how who".split())


def _tokens(s: str) -> set[str]:
    """Lower-cased, de-hyphenated, crudely singularised content words."""
    s = s.lower().replace("-", "").replace("'s", "")
    return {t[:-1] if t.endswith("s") and len(t) > 4 else t for t in _TOKEN.findall(s) if t not in _STOP}


def same_story(a: dict, b: dict) -> bool:
    """Heuristic: are two headlines the same underlying event?

    1. Near-identical wording (Jaccard ≥ 0.35 on content words), or
    2. Same set of ≥2 countries plus a shared theme or content word (Iran+France+cyber), or
    3. Same lead country, a shared theme and ≥2 shared content words.
    """
    ta, tb = a["_tok"], b["_tok"]
    jac = len(ta & tb) / max(1, len(ta | tb)) if ta and tb else 0.0
    if jac >= 0.35:
        return True
    ca, cb = set(a["countries"]), set(b["countries"])
    shared_theme = bool(set(a["themes"][:2]) & set(b["themes"][:2]))
    if len(ca) >= 2 and ca == cb and (shared_theme or ta & tb):
        return True
    if a["countries"] and b["countries"] and a["countries"][0] == b["countries"][0] and shared_theme \
            and len(ta & tb) >= 2:
        return True
    return False


def rank_headlines(items: list[dict], risk_lookup: dict[str, float], now: datetime | None = None,
                   half_life_h: float = 14.0, limit: int = 12, max_age_h: float = 72.0,
                   per_country_cap: int = 2) -> list[dict]:
    """Score = escalation relevance × country risk × recency × source weight,
    then cluster near-duplicates (corroboration boosts the cluster) and
    enforce diversity across countries/theatres."""
    now = now or datetime.now(timezone.utc)
    scored = []
    for it in items:
        age = _hours_ago(it.get("published"), now)
        if age > max_age_h:
            continue
        if it["esc"] + it["deesc"] == 0:      # no geopolitical signal at all
            continue
        if not it["countries"] and it["esc"] < 2.5:
            continue
        crisk = max([risk_lookup.get(c, 25.0) for c in it["countries"]] or [30.0])
        relevance = 1.0 + it["esc"] + 0.5 * it["deesc"]  # de-escalation news is still news
        s = relevance * (0.6 + crisk / 60.0) * (0.5 ** (age / half_life_h)) * it.get("weight", 1.0)
        scored.append({**it, "score": s, "age_h": age, "_tok": _tokens(it["title"])})
    scored.sort(key=lambda x: x["score"], reverse=True)

    clusters: list[dict] = []
    for it in scored:
        for cl in clusters:
            if same_story(it, cl):
                cl["sources"].add(it["source"])
                cl["score"] += 0.25 * it["score"]
                break
        else:
            clusters.append({**it, "sources": {it["source"]}})
    clusters.sort(key=lambda x: x["score"], reverse=True)

    picked, per_country = [], defaultdict(int)
    for cl in clusters:
        # diversity: no country may appear in more than `per_country_cap` items
        if any(per_country[c] >= per_country_cap for c in cl["countries"][:2]):
            continue
        for c in cl["countries"][:2] or ["_"]:
            per_country[c] += 1
        cl = {k: v for k, v in cl.items() if k != "_tok"}
        cl["n_sources"] = len(cl["sources"])
        cl["sources"] = sorted(cl["sources"])
        picked.append(cl)
        if len(picked) >= limit:
            break
    return picked


def country_heat(items: list[dict], now: datetime | None = None, half_life_h: float = 36.0,
                 k: float = 14.0) -> dict[str, dict]:
    """Live 'heat' 0–100 per country from recency-weighted escalation mentions.

    heat = 100·(1 − e^(−raw/k)) — saturating, so a flood of coverage cannot
    push a country past 100 and a single story cannot dominate.
    """
    now = now or datetime.now(timezone.utc)
    acc = defaultdict(lambda: {"mentions": 0, "raw": 0.0, "esc": 0.0, "deesc": 0.0, "themes": defaultdict(float)})
    for it in items:
        if not it["countries"]:
            continue
        decay = 0.5 ** (_hours_ago(it.get("published"), now) / half_life_h)
        share = 1.0 / math.sqrt(len(it["countries"]))  # multi-country stories split weight
        for c in it["countries"]:
            a = acc[c]
            a["mentions"] += 1
            contrib = (0.4 + max(it["net"], 0.0)) * decay * share * it.get("weight", 1.0)
            a["raw"] += contrib
            a["esc"] += it["esc"] * decay
            a["deesc"] += it["deesc"] * decay
            for t in it["themes"]:
                a["themes"][t] += decay
    out = {}
    for c, a in acc.items():
        heat = 100.0 * (1.0 - math.exp(-a["raw"] / k))
        top_themes = [t for t, _ in sorted(a["themes"].items(), key=lambda kv: kv[1], reverse=True)[:3]]
        tone = (a["deesc"] - a["esc"]) / max(1e-6, a["deesc"] + a["esc"])  # −1 escalatory … +1 de-escalatory
        out[c] = {"heat": round(heat, 1), "mentions": a["mentions"], "themes": top_themes, "tone": round(tone, 2)}
    return out


def so_what(item: dict, country_exposures: dict[str, str]) -> str:
    parts = []
    for c in item.get("countries", [])[:2]:
        if country_exposures.get(c):
            parts.append(country_exposures[c].split(",")[0].split(";")[0].strip())
    for t in item.get("themes", [])[:2]:
        ch = THEME_CHANNELS.get(t)
        if ch:
            parts.append(ch.split(",")[0])
    seen, uniq = set(), []
    for p in parts:
        if p.lower() not in seen:
            seen.add(p.lower())
            uniq.append(p)
    return " · ".join(uniq[:4])
