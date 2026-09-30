from pydantic import BaseModel, Field
from typing import Optional, Literal

class Requirements(BaseModel):
    # Core electrical
    application: Optional[str] = None            # e-bike, drone, solar storage, robot...
    nominal_voltage_v: Optional[float] = None
    required_energy_wh: Optional[float] = None   # or derive from load x runtime
    continuous_load_w: Optional[float] = None
    peak_load_w: Optional[float] = None
    target_runtime_h: Optional[float] = None

    # Physical / environmental
    max_weight_kg: Optional[float] = None
    max_dimensions_mm: Optional[tuple[float, float, float]] = None
    operating_temp_c: Optional[tuple[float, float]] = None

    # Preferences
    chemistry: Optional[Literal["Li-ion", "LiFePO4", "NiMH", "Lead-acid", "any"]] = None
    max_charge_time_h: Optional[float] = None
    min_cycle_life: Optional[int] = None
    budget_aud: Optional[float] = Field(None, description="Budget in Australian dollars")
    certifications: list[str] = []