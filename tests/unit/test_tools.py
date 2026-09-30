from battery_advisor.models.requirements import Requirements
from battery_advisor.tools.catalog_search import catalog_search
from battery_advisor.tools.registry import call_tool
from battery_advisor.tools.solar import melbourne_sun_times

EBIKE = Requirements(application="e-bike", nominal_voltage_v=48, continuous_load_w=400,
                     peak_load_w=750, target_runtime_h=1.5)

def test_ebike_finds_48v_packs():
    ids = [m["pack_id"] for m in catalog_search(EBIKE)["matches"]]
    assert "NMC-48-15" in ids and "LFP-12-100" not in ids

def test_budget_creates_near_miss():
    r = EBIKE.model_copy(update={"budget_aud": 500, "chemistry": "Li-ion"})
    out = catalog_search(r)
    assert [m["pack_id"] for m in out["matches"]] == ["NMC-48-15"]
    assert all(m["price_aud"] <= 500 for m in out["matches"])
    assert any(n["pack_id"] == "NMC-52-20" and n["failed"] == ["budget"]
               for n in out["near_misses"])

def test_unknown_pack_returns_error_not_exception():
    assert "error" in call_tool("estimate_runtime", {"pack_id": "nope", "load_w": 100})

def test_winter_days_shorter_than_summer():
    assert melbourne_sun_times("2026-06-21")["daylight_h"] < melbourne_sun_times("2026-12-21")["daylight_h"]
