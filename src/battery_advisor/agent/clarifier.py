from battery_advisor.models.requirements import Requirements

# Sensible defaults the agent may assume (and must disclose) for nice-to-haves
DEFAULTS = {
    "chemistry": "any",
    "certifications": [],
}

def missing_must_haves(r: Requirements) -> list[str]:
    missing = []
    if not r.application:
        missing.append("application")
    if r.nominal_voltage_v is None:
        missing.append("nominal_voltage_v")
    if r.peak_load_w is None:
        missing.append("peak_load_w")
    # Energy can be given directly OR derived from load x runtime
    has_energy = r.required_energy_wh is not None
    has_load_and_time = r.continuous_load_w is not None and r.target_runtime_h is not None
    if not (has_energy or has_load_and_time):
        missing.append("energy (required_energy_wh, or continuous_load_w + target_runtime_h)")
    return missing

def is_ready(r: Requirements) -> bool:
    return not missing_must_haves(r)

def consistency_warnings(r: Requirements) -> list[str]:
    """Cheap deterministic checks that trigger a follow-up question."""
    w = []
    if r.peak_load_w and r.continuous_load_w and r.peak_load_w < r.continuous_load_w:
        w.append("peak_load_w is lower than continuous_load_w")
    if r.required_energy_wh and r.continuous_load_w and r.target_runtime_h:
        derived = r.continuous_load_w * r.target_runtime_h
        if abs(derived - r.required_energy_wh) / r.required_energy_wh > 0.2:
            w.append(f"energy ({r.required_energy_wh} Wh) doesn't match load x runtime ({derived:.0f} Wh)")
    if r.operating_temp_c and r.operating_temp_c[0] < 0 and r.chemistry == "Li-ion":
        w.append("charging standard Li-ion below 0°C is unsafe; confirm cold-charging needs")
    return w

def status_report(r: Requirements) -> dict:
    return {
        "missing_must_haves": missing_must_haves(r),
        "warnings": consistency_warnings(r),
        "ready": is_ready(r) and not consistency_warnings(r),
    }