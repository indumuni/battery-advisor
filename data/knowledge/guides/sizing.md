# Sizing guide

## Energy
Energy needed (Wh) = load (W) x runtime (h).
Rated capacity needed = energy needed / (depth of discharge x temperature factor).
The tools in this project assume depth of discharge of 90% for lithium, 80% for NiMH and 50% for lead-acid, and a temperature factor of 0.9 between 0 and 10°C and 0.8 below 0°C.

## Voltage
Match the voltage the device or controller expects. Common nominal voltages: LiFePO4 12.8 / 25.6 / 51.2 V; e-bikes 36 / 48 / 52 V. A pack within about 15% of the target voltage is usually acceptable, but always confirm with the device manual.

## Current and C-rate
Current (A) = power (W) / voltage (V). C-rate = current / capacity (Ah).
Compare continuous current with the continuous discharge rating and peak current with the peak rating. Peak ratings apply for seconds only. Keep about 20% headroom on continuous current. A high C-rate causes heat, voltage sag and less usable capacity.

## System losses
Inverters typically lose 5-15%. Controllers and wiring lose a few percent more. Add these to the energy requirement when the load runs through an inverter.

## Ageing margin
Batteries are usually considered worn out at 80% of original capacity. If the pack must deliver the full runtime at end of life, add about 20% capacity.

## Series and parallel
Series adds voltage; parallel adds capacity. Only combine identical packs of the same age and state of charge, and stay within the manufacturer's maximum number of packs in parallel.