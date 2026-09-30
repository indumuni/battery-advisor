import json
from battery_advisor.models.requirements import Requirements
from battery_advisor.tools.registry import call_tool

r = Requirements(application="e-bike", nominal_voltage_v=48, continuous_load_w=400,
                 peak_load_w=750, target_runtime_h=1.5, budget_aud=800)
print(json.dumps(call_tool("search_catalog", {}, r), indent=2))
print(json.dumps(call_tool("estimate_runtime", {"pack_id": "LI-48-14", "load_w": 400}), indent=2))
print(json.dumps(call_tool("melbourne_sun_times", {}), indent=2))