"""Load the local battery catalog and find affordable packs that meet requirements."""

import json
from functools import lru_cache
from pathlib import Path
from battery_advisor.models.battery import BatteryPack
from battery_advisor.models.requirements import Requirements

CATALOG = Path(__file__).resolve().parents[3] / "data" / "catalog" / "catalog.json"

@lru_cache
def load_catalog() -> tuple[BatteryPack, ...]:
    """Parse the catalog JSON into battery models and cache the resulting tuple."""
    return tuple(BatteryPack(**row) for row in json.loads(CATALOG.read_text()))

def get_pack(pack_id: str) -> BatteryPack | None:
    """Return the catalog pack with the exact ID, or None when no pack matches."""
    return next((p for p in load_catalog() if p.id == pack_id), None)

def catalog_search(requirements: Requirements, limit: int = 5) -> dict:
    """Check every catalog pack and return compatible matches ordered by AUD price.

    Return up to limit full compatibility reports, up to three price-ordered
    near misses that fail exactly one check, and the total number of packs
    searched. Near misses include the pack ID, name, failed check, and price.
    """
    from battery_advisor.tools.compatibility import check_pack
    reports = [check_pack(p, requirements) for p in load_catalog()]
    matches = sorted((r for r in reports if r["compatible"]), key=lambda r: r["price_aud"])
    near = sorted((r for r in reports if len(r["failed"]) == 1), key=lambda r: r["price_aud"])
    return {
        "matches": matches[:limit],
        "near_misses": [{"pack_id": r["pack_id"], "name": r["name"], "failed": r["failed"],
                         "price_aud": r["price_aud"]} for r in near[:3]],
        "searched": len(reports),
    }
