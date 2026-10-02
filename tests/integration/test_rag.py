import pytest
from battery_advisor.rag import store
from battery_advisor.rag.ingest import ingest
from battery_advisor.rag.retriever import search_knowledge

@pytest.fixture
def index(tmp_path, monkeypatch):
    monkeypatch.setenv("BATTERY_VECTORSTORE", str(tmp_path))
    store.get_client.cache_clear()
    ingest()
    yield
    store.get_client.cache_clear()

def test_cold_charging_finds_chemistry_guide(index):
    out = search_knowledge("can I charge LiFePO4 in freezing weather", k=3)
    assert any("chemistry" in r["source"] for r in out["results"])

def test_flying_with_battery_finds_certifications(index):
    out = search_knowledge("can I carry an e-bike battery on a plane", k=3)
    assert any("certifications" in r["source"] for r in out["results"])

def test_category_filter(index):
    out = search_knowledge("48V battery", k=5, category="datasheets")
    assert all(r["source"].startswith("datasheets/") for r in out["results"])