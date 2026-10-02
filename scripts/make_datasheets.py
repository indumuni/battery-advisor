from pathlib import Path
from battery_advisor.tools.catalog_search import load_catalog
from battery_advisor.tools.runtime_calc import usable_energy_wh

OUT = Path(__file__).resolve().parents[1] / "data" / "knowledge" / "datasheets"
OUT.mkdir(parents=True, exist_ok=True)

for p in load_catalog():
    usable_kwh = usable_energy_wh(p.energy_wh, p.chemistry) / 1000
    lifetime_cost = p.price_aud / (usable_kwh * p.cycle_life)
    (OUT / f"{p.id}.md").write_text(f"""# {p.name} ({p.id})

## Overview
{p.chemistry} battery pack, {p.nominal_voltage_v} V nominal, {p.capacity_ah} Ah, {p.energy_wh} Wh. \
Price ${p.price_aud:,.0f} AUD. Built-in BMS: {"yes" if p.has_bms else "no"}.

## Electrical
- Continuous discharge: {p.max_continuous_discharge_a} A ({p.max_continuous_discharge_a * p.nominal_voltage_v:.0f} W)
- Peak discharge: {p.peak_discharge_a} A ({p.peak_discharge_a * p.nominal_voltage_v:.0f} W)
- Cycle life: {p.cycle_life} cycles

## Physical and environmental
- Weight: {p.weight_kg} kg ({p.energy_wh / p.weight_kg:.0f} Wh/kg)
- Dimensions: {p.dimensions_mm[0]:.0f} x {p.dimensions_mm[1]:.0f} x {p.dimensions_mm[2]:.0f} mm
- Operating temperature: {p.temp_range_c[0]:.0f} to {p.temp_range_c[1]:.0f} °C

## Certifications
{", ".join(p.certifications) if p.certifications else "None listed"}

## Cost of ownership
Approximate lifetime cost ${lifetime_cost:.2f} AUD per kWh delivered \
(usable energy x rated cycle life).
""")
print(f"Wrote datasheets to {OUT}")