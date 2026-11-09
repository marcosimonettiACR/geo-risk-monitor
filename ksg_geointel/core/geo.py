"""World country polygons for the satellite map (ISO-3 keyed)."""
from __future__ import annotations

import requests

GEOJSON_SOURCES = [
    # (url, property holding ISO3 or None → feature['id'])
    ("https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json", None),
    ("https://cdn.jsdelivr.net/gh/johan/world.geo.json@master/countries.geo.json", None),
    ("https://raw.githubusercontent.com/datasets/geo-countries/main/data/countries.geojson", "ISO3166-1-Alpha-3"),
]

# Satellite imagery tiles (no token required)
ESRI_IMAGERY = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
ESRI_LABELS = "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"


def load_world_geojson() -> dict | None:
    for url, prop in GEOJSON_SOURCES:
        try:
            r = requests.get(url, timeout=25, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            gj = r.json()
            feats = []
            for f in gj.get("features", []):
                iso = f.get("id") if prop is None else f.get("properties", {}).get(prop)
                if isinstance(iso, str) and len(iso) == 3 and iso.isalpha():
                    f["id"] = iso.upper()
                    f.setdefault("properties", {})
                    f["properties"]["name"] = f["properties"].get("name") or f["properties"].get("ADMIN") or iso
                    feats.append(f)
            if len(feats) > 150:
                return {"type": "FeatureCollection", "features": feats}
        except Exception:  # noqa: BLE001
            continue
    return None


def universe_from_geojson(gj: dict | None) -> list[tuple[str, str]]:
    if not gj:
        return []
    return [(f["id"], f["properties"].get("name", f["id"])) for f in gj["features"]]
