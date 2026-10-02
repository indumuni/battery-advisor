import json
from pathlib import Path
from battery_advisor.models.requirements import Requirements
from battery_advisor.tools.registry import anthropic_schemas, call_tool

PROMPTS = Path(__file__).resolve().parents[3] / "configs" / "prompts"
MAX_TURNS = 10

def recommend(client, model: str, requirements: Requirements, assumptions: dict) -> str:
    system = (PROMPTS / "system.md").read_text() + "\n\n" + (PROMPTS / "recommend.md").read_text()
    messages = [{"role": "user", "content":
        "Finalized requirements:\n" + requirements.model_dump_json(exclude_none=True, indent=2)
        + "\n\nAssumptions:\n" + json.dumps(assumptions, indent=2)
        + "\n\nRecommend the best battery pack(s)."}]

    for _ in range(MAX_TURNS):
        resp = client.messages.create(model=model, max_tokens=2000, system=system,
                                      tools=anthropic_schemas(), messages=messages)
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        results = [{"type": "tool_result", "tool_use_id": b.id,
                    "content": json.dumps(call_tool(b.name, b.input, requirements))}
                   for b in resp.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})
    return "Stopped: too many tool calls without a final answer."