"""Composite country geopolitical-risk engine.

composite = w_s·Structural + w_g·Governance + w_l·Live + w_e·Escalation

  Structural  analyst baseline (data/countries.py)            0–100
  Governance  World Bank WGI political stability, inverted     0–100
  Live        real-time news heat from wires + GDELT           0–100
  Escalation  exposure to active theatres (data/theatres.py)   0–100

Missing components are dropped and the remaining weights re-normalised, so a
country is never penalised (or flattered) just because a data source is down.
"""
from __future__ import annotations

import pandas as pd

from core.theme import band

DEFAULT_WEIGHTS = {"structural": 0.45, "governance": 0.15, "live": 0.25, "escalation": 0.15}
LIVE_FLOOR_GAP = 15.0  # how far below structural a news-silent country's live component can sit


def wgi_to_risk(pv_est: float) -> float:
    """WGI PV.EST (≈ −2.5 … +2.5, higher = more stable) → 0–100 risk."""
    return float(min(100.0, max(0.0, (2.5 - pv_est) / 5.0 * 100.0)))


def theatre_exposure(theatres: list[dict]) -> dict[str, dict]:
    """Max over theatres of intensity × participation, plus which theatres."""
    out: dict[str, dict] = {}
    for t in theatres:
        for iso, w in t["participants"].items():
            val = t["intensity"] * w
            cur = out.setdefault(iso, {"score": 0.0, "theatres": []})
            cur["theatres"].append((t["id"], round(val, 1)))
            # soft-max: dominant theatre plus a damped contribution from others
            cur["score"] = max(cur["score"], val)
    for iso, cur in out.items():
        vals = sorted([v for _, v in cur["theatres"]], reverse=True)
        cur["score"] = min(100.0, vals[0] + 0.15 * sum(vals[1:]))
        cur["theatres"] = [tid for tid, _ in sorted(cur["theatres"], key=lambda x: x[1], reverse=True)]
    return out


def compute_risk(universe: list[dict], heat: dict[str, dict], wgi: dict[str, float],
                 exposure: dict[str, dict], weights: dict[str, float] | None = None,
                 default_base: float = 24.0) -> pd.DataFrame:
    """universe: list of {iso3, name, region, base?, mkt?} covering every country to map."""
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    rows = []
    for c in universe:
        iso = c["iso3"]
        seeded = c.get("base") is not None
        structural = float(c["base"]) if seeded else None
        governance = wgi_to_risk(wgi[iso]) if iso in wgi else None
        if structural is None:
            # Unseeded country: derive structural from governance when available
            structural = 0.8 * governance + 4 if governance is not None else default_base
        live_d = heat.get(iso)
        live = live_d["heat"] if live_d else 0.0
        # Silence is not safety: under-reported wars (Sudan, Myanmar, Sahel) must
        # not be scored down for lack of English-language coverage. News can lift
        # the live component above baseline; absence can only trim it a little.
        live_component = max(live, structural - LIVE_FLOOR_GAP)
        esc_d = exposure.get(iso)
        escalation = esc_d["score"] if esc_d else None   # not in a theatre → component dropped

        comps = {"structural": structural, "governance": governance, "live": live_component, "escalation": escalation}
        num = sum(w[k] * v for k, v in comps.items() if v is not None)
        den = sum(w[k] for k, v in comps.items() if v is not None)
        composite = num / den if den else structural

        # Live news can only move a country so far from its fundamentals:
        # cap the deviation so a viral story doesn't paint Switzerland red.
        composite = max(structural - 10, min(structural + 25, composite))

        rows.append({
            "iso3": iso, "name": c["name"], "region": c.get("region", "Other"),
            "structural": round(structural, 1),
            "governance": None if governance is None else round(governance, 1),
            "live": round(live, 1), "escalation": round(escalation or 0.0, 1),
            "composite": round(composite, 1),
            "delta": round(composite - structural, 1),
            "band": band(composite),
            "mentions": live_d["mentions"] if live_d else 0,
            "tone": live_d["tone"] if live_d else 0.0,
            "live_themes": ", ".join(live_d["themes"]) if live_d else "",
            "theatres": ", ".join(esc_d["theatres"]) if esc_d else "",
            "mkt": c.get("mkt", 1),
            "seeded": seeded,
        })
    df = pd.DataFrame(rows).sort_values("composite", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df


def global_index(df: pd.DataFrame) -> float:
    """Market-weighted global geo-risk index: mean composite weighted by each
    country's market importance (1–5), over the seeded register."""
    sub = df[df["seeded"]]
    if sub.empty:
        return float(df["composite"].mean())
    wts = sub["mkt"].astype(float) ** 1.5
    return float((sub["composite"] * wts).sum() / wts.sum())
