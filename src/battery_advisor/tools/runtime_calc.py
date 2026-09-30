"""Estimate usable battery energy and runtime with depth-of-discharge and cold derating."""

from battery_advisor.models.requirements import Requirements

# Fraction of rated energy you can safely use (depth of discharge)
DEPTH_OF_DISCHARGE = {"LiFePO4": 0.90, "Li-ion": 0.90, "NiMH": 0.80, "Lead-acid": 0.50}

def temp_derate(ambient_c: float | None) -> float:
    """Rough capacity loss in the cold. A planning approximation, not a datasheet value."""
    if ambient_c is None or ambient_c >= 10:
        return 1.0
    return 0.9 if ambient_c >= 0 else 0.8

def usable_energy_wh(energy_wh: float, chemistry: str, ambient_c: float | None = None) -> float:
    """Return usable Wh after chemistry-specific discharge limits and cold derating.

    Unknown chemistries use an 80% discharge limit. An omitted temperature
    applies no cold derating.
    """
    return energy_wh * DEPTH_OF_DISCHARGE.get(chemistry, 0.8) * temp_derate(ambient_c)

def needed_energy_wh(r: Requirements) -> float | None:
    """Return explicit required Wh, or load watts times target runtime hours.

    Return None when neither an energy target nor both load and runtime are set.
    """
    if r.required_energy_wh is not None:
        return r.required_energy_wh
    if r.continuous_load_w is not None and r.target_runtime_h is not None:
        return r.continuous_load_w * r.target_runtime_h
    return None

def estimate_runtime(pack_id: str, load_w: float, ambient_c: float | None = None) -> dict:
    """Estimate a catalog pack's runtime for a constant positive load in watts.

    Return usable Wh, runtime hours, current in amps, C-rate, and assumptions.
    The estimate accounts for discharge limits and cold, but excludes inverter
    losses. Return an error dictionary when the pack ID is unknown.
    """
    from battery_advisor.tools.catalog_search import get_pack
    p = get_pack(pack_id)
    if p is None:
        return {"error": f"unknown pack {pack_id}"}
    usable = usable_energy_wh(p.energy_wh, p.chemistry, ambient_c)
    return {
        "pack_id": p.id,
        "usable_wh": round(usable, 1),
        "runtime_h": round(usable / load_w, 2),
        "current_a": round(load_w / p.nominal_voltage_v, 1),
        "c_rate": round((load_w / p.nominal_voltage_v) / p.capacity_ah, 2),
        "assumptions": f"DoD {DEPTH_OF_DISCHARGE.get(p.chemistry, 0.8):.0%}, "
                       f"cold derate x{temp_derate(ambient_c)}, no inverter losses",
    }
