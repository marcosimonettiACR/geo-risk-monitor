"""Offline tests for the pure (Streamlit-free) core. Run: python -m pytest -q  (or python tests/test_core.py)"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import feeds, nlp, risk  # noqa: E402
from core.theme import band  # noqa: E402
from data.brief import ANALYST_BRIEF, CALENDAR  # noqa: E402
from data.countries import COUNTRIES, COUNTRY_BY_ISO  # noqa: E402
from data.theatres import THEATRES  # noqa: E402

NOW = datetime(2026, 11, 10, 2, 0, tzinfo=timezone.utc)

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>
<item><title>Iran says two tankers hit naval mines in Strait of Hormuz</title><link>https://x/a</link>
<description>&lt;p&gt;IRGC claims blockade...&lt;/p&gt;</description><pubDate>Mon, 09 Nov 2026 22:00:00 GMT</pubDate></item>
<item><title>Russia and Ukraine open talks in Abu Dhabi on energy ceasefire</title><link>https://x/b</link>
<pubDate>Mon, 09 Nov 2026 20:00:00 +0000</pubDate></item>
<item><title>US Fed hike odds rise after payrolls beat</title><link>https://x/c</link><pubDate>Sun, 08 Nov 2026 10:00:00 GMT</pubDate></item>
<item><title>China's PLA navy surges ships near Taiwan as Lai warns of interference</title><link>https://x/d</link><pubDate>Mon, 09 Nov 2026 23:30:00 GMT</pubDate></item>
<item><title>Tankers hit by naval mines in Hormuz, Iran claims</title><link>https://y/a</link><pubDate>Mon, 09 Nov 2026 23:00:00 GMT</pubDate></item>
<item><title>Swiss chocolate exports rise</title><link>https://x/e</link><pubDate>Mon, 09 Nov 2026 23:00:00 GMT</pubDate></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>Houthis strike Aramco office in Riyadh</title><link href="https://z/1"/><updated>2026-11-08T12:00:00Z</updated>
<summary>Saudi coalition vows response</summary></entry></feed>"""

RDF = b"""<?xml version="1.0"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<item><title>Sudan RSF drones hit Port Sudan</title><link>https://dw/1</link><dc:date>2026-11-09T10:00:00Z</dc:date></item></rdf:RDF>"""


def _items():
    a = feeds.parse_feed(RSS, "Test RSS", "Global", 1.0)
    b = feeds.parse_feed(ATOM, "Test Atom", "Global", 1.0)
    c = feeds.parse_feed(RDF, "Test RDF", "Global", 1.0)
    return a + b + c


def test_parsers():
    items = _items()
    assert len(items) == 8
    assert all(i["published"] is not None for i in items), [i["title"] for i in items if not i["published"]]
    assert items[0]["summary"].startswith("IRGC claims")
    assert any(i["url"] == "https://z/1" for i in items)


def test_tagging_and_scoring():
    idx = nlp.build_country_index(COUNTRIES)
    out = {i["title"]: i for i in nlp.analyse(_items(), idx)}
    hz = out["Iran says two tankers hit naval mines in Strait of Hormuz"]
    assert "IRN" in hz["countries"] and hz["esc"] >= 5 and "Shipping" in hz["themes"]
    ab = out["Russia and Ukraine open talks in Abu Dhabi on energy ceasefire"]
    assert {"RUS", "UKR"} <= set(ab["countries"]) and ab["deesc"] > 0
    tw = out["China's PLA navy surges ships near Taiwan as Lai warns of interference"]
    assert {"CHN", "TWN"} <= set(tw["countries"])
    fed = out["US Fed hike odds rise after payrolls beat"]
    assert "USA" in fed["countries"]
    assert out["Swiss chocolate exports rise"]["esc"] == 0
    # lowercase "us" must not tag USA
    assert "USA" not in nlp.tag_countries("tell us about chocolate", idx)
    # Niger must not match Nigeria
    assert nlp.tag_countries("Nigeria election", idx) == ["NGA"]
    assert "SDN" in nlp.tag_countries("Sudan RSF drones hit Port Sudan", idx)
    assert "SDN" not in nlp.tag_countries("South Sudan oil pipeline", idx)


def test_heat_ranking_and_risk():
    idx = nlp.build_country_index(COUNTRIES)
    an = nlp.analyse(_items(), idx)
    heat = nlp.country_heat(an, now=NOW)
    assert heat["IRN"]["heat"] > heat.get("CHE", {"heat": 0})["heat"]
    assert 0 < heat["IRN"]["heat"] <= 100

    exp = risk.theatre_exposure(THEATRES)
    assert exp["IRN"]["score"] >= 90 and exp["IRN"]["theatres"][0] == "hormuz"
    universe = [dict(c) for c in COUNTRIES] + [{"iso3": "ISL", "name": "Iceland", "base": None}]
    df = risk.compute_risk(universe, heat, {"ISL": 1.3, "IRN": -1.6}, exp)
    r = df.set_index("iso3")
    assert r.loc["IRN", "band"] == "SEVERE"
    assert r.loc["CHE", "band"] == "LOW"
    assert r.loc["ISL", "composite"] < 30 and not r.loc["ISL", "seeded"]
    assert df["composite"].between(0, 100).all()
    assert 20 < risk.global_index(df) < 80

    top = nlp.rank_headlines(an, dict(zip(df["iso3"], df["composite"])), now=NOW)
    titles = [t["title"] for t in top]
    assert "Swiss chocolate exports rise" not in titles
    # the two Hormuz mine stories must be clustered into one, corroborated by 1 source here (same source name)
    assert sum("mines" in t.lower() for t in titles) == 1
    assert top[0]["countries"] and top[0]["countries"][0] in {"IRN", "TWN", "SDN", "YEM", "SAU", "CHN"}
    so = nlp.so_what(top[0], {c["iso3"]: c["exposures"] for c in COUNTRIES})
    assert so


def test_seed_integrity():
    isos = [c["iso3"] for c in COUNTRIES]
    assert len(isos) == len(set(isos)), "duplicate ISO codes"
    for c in COUNTRIES:
        assert 0 <= c["base"] <= 100 and -90 <= c["lat"] <= 90 and -180 <= c["lon"] <= 180, c["iso3"]
    for t in THEATRES:
        assert abs(sum(s["prob"] for s in t["scenarios"]) - 1.0) < 1e-6, t["id"]
        assert 0 <= t["current_rung"] < len(t["ladder"])
        for r in t["retaliation"]:
            assert 0 < r["prob"] < 1 and 1 <= r["severity"] <= 5
            assert r["actor_iso"] in COUNTRY_BY_ISO and r["target_iso"] in COUNTRY_BY_ISO, (t["id"], r["actor_iso"], r["target_iso"])
    assert len(ANALYST_BRIEF) == 12
    assert all(set(b) == {"tag", "theatre", "level", "what", "so_what", "next"} for b in ANALYST_BRIEF)
    assert all(band(0) == "LOW" and band(80) == "SEVERE" for _ in [0])
    assert CALENDAR


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("✓", name)
    print("all passed")
