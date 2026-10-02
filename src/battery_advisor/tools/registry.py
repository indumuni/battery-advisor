from dataclasses import dataclass
from typing import Callable
from pydantic import BaseModel
from battery_advisor.models.requirements import Requirements
from battery_advisor.tools.catalog_search import catalog_search
from battery_advisor.tools.compatibility import check_compatibility
from battery_advisor.tools.runtime_calc import estimate_runtime
from battery_advisor.tools.solar import melbourne_sun_times, solar_charge_plan



from typing import Literal
from battery_advisor.rag.retriever import search_knowledge

class KnowledgeIn(BaseModel):
    query: str
    k: int = 4
    category: Literal["datasheets", "guides", "standards"] | None = None

class SearchIn(BaseModel):
    limit: int = 5
class CompatIn(BaseModel):
    pack_id: str
class RuntimeIn(BaseModel):
    pack_id: str
    load_w: float
    ambient_c: float | None = None
class SunIn(BaseModel):
    on_date: str | None = None          # YYYY-MM-DD, defaults to today in Melbourne
class SolarPlanIn(BaseModel):
    pack_id: str
    panel_w: float
    month: int | None = None

@dataclass
class Tool:
    name: str
    description: str
    input_model: type[BaseModel]
    fn: Callable
    needs_requirements: bool = False    # agent injects the finalized requirements

REGISTRY: dict[str, Tool] = {t.name: t for t in [
    Tool("search_catalog", "Find battery packs that satisfy the user's finalized requirements. "
         "Returns ranked matches plus near-misses that fail only one check.",
         SearchIn, catalog_search, needs_requirements=True),
    Tool("check_compatibility", "Check one pack against the user's requirements, check by check.",
         CompatIn, check_compatibility, needs_requirements=True),
    Tool("estimate_runtime", "Estimate runtime (h), current and C-rate for a pack at a given load in W.",
         RuntimeIn, estimate_runtime),
    Tool("melbourne_sun_times", "Sunrise, sunset and useful solar charging window in Melbourne.",
         SunIn, melbourne_sun_times),
    Tool("solar_charge_plan", "Days to fully charge a pack from a solar panel in Melbourne.",
         SolarPlanIn, solar_charge_plan),
    Tool("search_knowledge",
         "Search the battery knowledge base (chemistry, sizing, safety, certifications, "
         "transport rules, pack datasheets). Use it for any explanation, safety, standards or "
         "regulatory claim, and cite the returned 'source'. Use category to narrow the search.",
         KnowledgeIn, search_knowledge),
]}

def anthropic_schemas() -> list[dict]:
    return [{"name": t.name, "description": t.description,
             "input_schema": t.input_model.model_json_schema()} for t in REGISTRY.values()]

def call_tool(name: str, args: dict, requirements: Requirements | None = None) -> dict:
    tool = REGISTRY.get(name)
    if tool is None:
        return {"error": f"unknown tool {name}"}
    try:
        kwargs = tool.input_model(**args).model_dump()
        if tool.needs_requirements:
            kwargs["requirements"] = requirements
        return tool.fn(**kwargs)
    except Exception as e:                       # return errors to the model instead of crashing
        return {"error": str(e)}