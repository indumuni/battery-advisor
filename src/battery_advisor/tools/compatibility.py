"""Check battery packs against the supplied electrical, physical, and budget requirements."""

from battery_advisor.models.battery import BatteryPack
from battery_advisor.models.requirements import Requirements
from battery_advisor.tools.runtime_calc import needed_energy_wh, usable_energy_wh

VOLTAGE_TOLERANCE = 0.15   # +/-15% of the requested nominal voltage

def check_pack(p: BatteryPack, r: Requirements) -> dict:
    """Return a pack summary, compatibility flag, and individual constraint checks.

    Evaluate supplied constraints for voltage, usable energy, current, weight,
    dimensions, temperature, chemistry, cycle life, budget, and certifications.
    Voltage allows a 15% deviation; dimensions allow rotation. Energy uses
    discharge limits and the lowest requested operating temperature. A pack is
    compatible when no evaluated check fails, including when none are supplied.
    """
    checks: list[dict] = []
    def add(name: str, ok: bool, detail: str):
        """Record a named pass/fail result with a human-readable explanation."""
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    if r.nominal_voltage_v:
        off = abs(p.nominal_voltage_v - r.nominal_voltage_v) / r.nominal_voltage_v
        add("voltage", off <= VOLTAGE_TOLERANCE,
            f"pack {p.nominal_voltage_v} V vs required {r.nominal_voltage_v} V")

    need = needed_energy_wh(r)
    if need is not None:
        lo_temp = r.operating_temp_c[0] if r.operating_temp_c else None
        usable = usable_energy_wh(p.energy_wh, p.chemistry, lo_temp)
        add("energy", usable >= need, f"usable {usable:.0f} Wh vs needed {need:.0f} Wh")

    if r.continuous_load_w:
        amps = r.continuous_load_w / p.nominal_voltage_v
        add("continuous current", amps <= p.max_continuous_discharge_a,
            f"draw {amps:.1f} A vs limit {p.max_continuous_discharge_a} A")
    if r.peak_load_w:
        amps = r.peak_load_w / p.nominal_voltage_v
        add("peak current", amps <= p.peak_discharge_a,
            f"draw {amps:.1f} A vs limit {p.peak_discharge_a} A")

    if r.max_weight_kg:
        add("weight", p.weight_kg <= r.max_weight_kg, f"{p.weight_kg} kg vs max {r.max_weight_kg} kg")
    if r.max_dimensions_mm:
        fits = all(a <= b for a, b in zip(sorted(p.dimensions_mm), sorted(r.max_dimensions_mm)))
        add("dimensions", fits, f"{p.dimensions_mm} mm vs max {r.max_dimensions_mm} mm")
    if r.operating_temp_c:
        ok = p.temp_range_c[0] <= r.operating_temp_c[0] and p.temp_range_c[1] >= r.operating_temp_c[1]
        add("temperature", ok, f"pack {p.temp_range_c} °C vs required {r.operating_temp_c} °C")
    if r.chemistry and r.chemistry != "any":
        add("chemistry", p.chemistry == r.chemistry, f"{p.chemistry} vs wanted {r.chemistry}")
    if r.min_cycle_life:
        add("cycle life", p.cycle_life >= r.min_cycle_life, f"{p.cycle_life} vs min {r.min_cycle_life}")
    if r.budget_aud:
        add("budget", p.price_aud <= r.budget_aud, f"${p.price_aud:,.0f} AUD vs budget ${r.budget_aud:,.0f} AUD")
    if r.certifications:
        missing = sorted(set(r.certifications) - set(p.certifications))
        add("certifications", not missing, f"missing: {missing}" if missing else "all present")

    failed = [c["check"] for c in checks if not c["ok"]]
    return {
        "pack_id": p.id, "name": p.name, "price_aud": p.price_aud,
        "energy_wh": p.energy_wh, "chemistry": p.chemistry,
        "compatible": not failed, "failed": failed, "checks": checks,
    }

def check_compatibility(requirements: Requirements, pack_id: str) -> dict:
    """Look up a catalog pack and report how it meets the supplied requirements.

    Return the detailed check_pack report, or an error for an unknown pack ID.
    """
    from battery_advisor.tools.catalog_search import get_pack
    p = get_pack(pack_id)
    return check_pack(p, requirements) if p else {"error": f"unknown pack {pack_id}"}
