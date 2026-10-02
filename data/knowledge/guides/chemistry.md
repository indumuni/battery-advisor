# Chemistry guide

## LiFePO4 (lithium iron phosphate)
- Nominal 3.2 V per cell; a 12.8 V pack is 4 cells in series.
- Typical cycle life 2,000-6,000 cycles. Very stable thermally, so it is the safest common lithium chemistry.
- Lower energy density than Li-ion (heavier for the same Wh).
- Usable depth of discharge is about 90-100%.
- Do not charge below 0°C unless the pack has heating; charging cold causes lithium plating and permanent damage. Discharging down to about -20°C is usually fine.
- Best for solar storage, caravans, boats and backup power.

## Li-ion (NMC / NCA)
- Nominal 3.6-3.7 V per cell. Highest energy density, so best where weight matters: e-bikes, drones, robots, power tools.
- Typical cycle life 500-1,500 cycles.
- Usual charge window is 0-45°C. Needs a BMS; higher thermal runaway risk than LiFePO4.

## NiMH
- 1.2 V per cell, 60-120 Wh/kg, 300-500 cycles, high self-discharge.
- Tolerant of abuse. Mostly used in legacy or simple devices.

## Lead-acid (AGM and flooded)
- 2 V per cell, 30-50 Wh/kg, very heavy.
- Only discharge to about 50% to get 300-500 cycles. Voltage sags under heavy load.
- Cheapest upfront, but usually the most expensive per delivered kWh over its life.

## Choosing a chemistry
- Weight-critical and portable: Li-ion.
- Long life, daily cycling, stationary or fixed: LiFePO4.
- Lowest purchase price and weight does not matter: lead-acid, accepting the short life.
- Frequent charging below 0°C: choose a pack with a heater, or keep the pack warm.