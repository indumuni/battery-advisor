from pydantic import BaseModel, Field
from battery_advisor.models.requirements import Requirements

class AgentState(BaseModel):
    requirements: Requirements = Field(default_factory=Requirements)
    assumptions: dict[str, str] = {}      # field -> "assumed 'any' chemistry"
    messages: list[dict] = []             # Anthropic-format history
    finalized: bool = False

    def merge(self, updates: dict) -> list[str]:
        """Apply non-null updates; return the list of fields that changed."""
        changed = []
        for k, v in updates.items():
            if v is None or not hasattr(self.requirements, k):
                continue
            if getattr(self.requirements, k) != v:
                setattr(self.requirements, k, v)
                changed.append(k)
        return changed