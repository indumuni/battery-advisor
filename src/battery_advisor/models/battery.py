from pydantic import BaseModel


class BatteryPack(BaseModel):
    id: str
    name: str
    chemistry: str
    nominal_voltage_v: float
    capacity_ah: float
    energy_wh: float
    max_continuous_discharge_a: float
    peak_discharge_a: float
    weight_kg: float
    dimensions_mm: tuple[float, float, float]
    temp_range_c: tuple[float, float]
    cycle_life: int
    price_aud: float
    certifications: list[str]
    has_bms: bool
