"""Optional: Claude-written 12-point analyst brief from the live wire.

Activated only when an Anthropic API key is present (st.secrets
["ANTHROPIC_API_KEY"] or typed into the sidebar). Uses plain HTTPS, so no SDK
dependency. Without a key the app uses the deterministic ranking in core/nlp.
"""
from __future__ import annotations

import json
import re

import requests

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-5-5"

SYSTEM = (
    "You are a senior geopolitical intelligence analyst briefing portfolio managers at a "
    "finance client. You think like a NATO strategic planner and a UN political officer: "
    "precise, sourced, probabilistic, and focused on what developments MEAN for markets and "
    "what is likely to happen NEXT. Never invent facts beyond the headlines provided; if "
    "uncertain, say so and lower confidence."
)

PROMPT = """Below are the latest open-source headlines (UTC timestamps, source in brackets), followed by the current top country risk scores.

Write EXACTLY 12 intelligence bullets, ordered by importance to a finance client.
Return ONLY a JSON array of 12 objects with keys:
  "headline"  – one sentence: what happened (≤30 words)
  "so_what"   – market transmission: assets, direction, magnitude where reasonable (≤35 words)
  "next"      – what to watch / likely next move with a rough probability (≤25 words)
  "theatre"   – short label (e.g. "Hormuz", "Russia–Ukraine", "Taiwan Strait", "Macro")
  "level"     – one of SEVERE, HIGH, ELEVATED, MODERATE, LOW
  "confidence"– one of High, Medium, Low (source corroboration)

HEADLINES:
{headlines}

TOP COUNTRY RISK (composite 0–100):
{risks}
"""


def claude_brief(api_key: str, headlines: list[dict], risk_rows: list[tuple[str, float]],
                 model: str = DEFAULT_MODEL, timeout: float = 90.0) -> list[dict]:
    lines = []
    for h in headlines[:60]:
        ts = h["published"].strftime("%d %b %H:%M") if h.get("published") else "n/a"
        lines.append(f"- {ts} [{h['source']}] {h['title']}")
    risks = "\n".join(f"- {n}: {s:.0f}" for n, s in risk_rows[:20])
    body = {
        "model": model,
        "max_tokens": 3000,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": PROMPT.format(headlines="\n".join(lines), risks=risks)}],
    }
    r = requests.post(API_URL, json=body, timeout=timeout, headers={
        "x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    r.raise_for_status()
    text = "".join(b.get("text", "") for b in r.json().get("content", []) if b.get("type") == "text")
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        raise ValueError("Model did not return a JSON array")
    items = json.loads(m.group(0))
    return [i for i in items if isinstance(i, dict) and i.get("headline")][:12]
