import json
from pathlib import Path

from battery_advisor.models.battery import BatteryPack
from scripts.validate_catalog import validate_catalog

CATALOG_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "catalog" / "catalog.json"


def test_catalog_file_exists():
    assert CATALOG_PATH.exists()


def test_catalog_entries_count():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert 15 <= len(data) <= 20


def test_catalog_pydantic_validation():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        pack = BatteryPack.model_validate(item)
        assert pack.id
        assert pack.nominal_voltage_v > 0
        assert pack.capacity_ah > 0
        assert pack.energy_wh > 0
        assert pack.price_aud > 0
        assert pack.peak_discharge_a >= pack.max_continuous_discharge_a


def test_validate_catalog_script():
    assert validate_catalog(CATALOG_PATH) is True
