import json
from pathlib import Path
import anthropic
from battery_advisor.models.requirements import Requirements
from battery_advisor.agent.state import AgentState
from battery_advisor.agent.clarifier import status_report

MODEL = "claude-sonnet-5-5"   # move to configs/settings.yaml
PROMPTS = Path(__file__).resolve().parents[3] / "configs" / "prompts"

TOOLS = [
    {
        "name": "update_requirements",
        "description": "Record any requirement values the user has stated or confirmed. "
                       "Only include fields the user actually provided. Use metric units and AUD.",
        "input_schema": Requirements.model_json_schema(),
    },
    {
        "name": "record_assumption",
        "description": "Log a default you are assuming for a nice-to-have field the user skipped.",
        "input_schema": {
            "type": "object",
            "properties": {"field": {"type": "string"}, "assumption": {"type": "string"}},
            "required": ["field", "assumption"],
        },
    },
    {
        "name": "finalize_requirements",
        "description": "Call ONLY after the user has confirmed your summary. "
                       "Fails if must-have fields are missing.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

class ClarifyingAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.state = AgentState()
        self.system = (PROMPTS / "system.md").read_text() + "\n\n" + (PROMPTS / "clarify.md").read_text()

    def _run_tool(self, name: str, args: dict) -> dict:
        s = self.state
        if name == "update_requirements":
            changed = s.merge(args)
            return {"updated": changed, **status_report(s.requirements)}
        if name == "record_assumption":
            s.assumptions[args["field"]] = args["assumption"]
            return {"ok": True}
        if name == "finalize_requirements":
            report = status_report(s.requirements)
            if not report["ready"]:
                return {"error": "Not ready to finalize", **report}
            s.finalized = True
            return {"ok": True, "requirements": s.requirements.model_dump(),
                    "assumptions": s.assumptions}
        return {"error": f"unknown tool {name}"}

    def chat(self, user_text: str) -> str:
        s = self.state
        s.messages.append({"role": "user", "content": user_text})
        while True:
            resp = self.client.messages.create(
                model=MODEL, max_tokens=1000, system=self.system,
                tools=TOOLS, messages=s.messages,
            )
            s.messages.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason != "tool_use":
                return "".join(b.text for b in resp.content if b.type == "text")
            results = []
            for b in resp.content:
                if b.type == "tool_use":
                    out = self._run_tool(b.name, b.input)
                    results.append({"type": "tool_result", "tool_use_id": b.id,
                                    "content": json.dumps(out)})
            s.messages.append({"role": "user", "content": results})

if __name__ == "__main__":
    agent = ClarifyingAgent()
    print("Battery advisor: what are you looking to power?")
    while not agent.state.finalized:
        print("\n" + agent.chat(input("> ")))
    print("\nFinal requirements:\n", agent.state.requirements.model_dump_json(indent=2))