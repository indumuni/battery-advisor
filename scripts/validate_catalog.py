#!/usr/bin/env python3
"""Validate sample battery catalog entries."""

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

# Ensure src is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from battery_advisor.models.battery import BatteryPack


def validate_catalog(catalog_path: Path) -> bool:
    """Load and validate all battery entries in the catalog."""
    if not catalog_path.exists():
        print(f"Error: Catalog file not found at {catalog_path}", file=sys.stderr)
        return False

    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error: Failed to read/parse JSON from {catalog_path}: {e}", file=sys.stderr)
        return False

    if not isinstance(data, list):
        print("Error: Catalog JSON root must be a list of battery entries.", file=sys.stderr)
        return False

    print(f"Validating {len(data)} battery packs from {catalog_path.name}...\n")

    seen_ids = set()
    errors = []
    warnings = []
    validated_packs: list[BatteryPack] = []

    for idx, item in enumerate(data, start=1):
        pack_id = item.get("id", f"Entry #{idx}")

        # 1. Check duplicate IDs
        if pack_id in seen_ids:
            errors.append(f"[{pack_id}] Duplicate pack ID detected.")
        else:
            seen_ids.add(pack_id)

        # 2. Pydantic schema validation
        try:
            pack = BatteryPack.model_validate(item)
            validated_packs.append(pack)
        except ValidationError as ve:
            errors.append(f"[{pack_id}] Schema validation failed: {ve}")
            continue

        # 3. Domain & physical logic validation
        if pack.nominal_voltage_v <= 0:
            errors.append(
                f"[{pack.id}] Nominal voltage must be positive ({pack.nominal_voltage_v}V)."
            )
        if pack.capacity_ah <= 0:
            errors.append(f"[{pack.id}] Capacity must be positive ({pack.capacity_ah}Ah).")
        if pack.energy_wh <= 0:
            errors.append(f"[{pack.id}] Energy must be positive ({pack.energy_wh}Wh).")
        if pack.max_continuous_discharge_a <= 0:
            errors.append(
                f"[{pack.id}] Continuous discharge current must be positive "
                f"({pack.max_continuous_discharge_a}A)."
            )
        if pack.peak_discharge_a < pack.max_continuous_discharge_a:
            errors.append(
                f"[{pack.id}] Peak discharge ({pack.peak_discharge_a}A) cannot be lower than "
                f"continuous discharge ({pack.max_continuous_discharge_a}A)."
            )
        if pack.weight_kg <= 0:
            errors.append(f"[{pack.id}] Weight must be positive ({pack.weight_kg}kg).")
        if any(dim <= 0 for dim in pack.dimensions_mm):
            errors.append(f"[{pack.id}] All dimensions must be positive {pack.dimensions_mm}.")
        if pack.temp_range_c[0] >= pack.temp_range_c[1]:
            errors.append(f"[{pack.id}] Invalid temperature range: min >= max {pack.temp_range_c}.")
        if pack.cycle_life <= 0:
            errors.append(f"[{pack.id}] Cycle life must be positive ({pack.cycle_life}).")
        if pack.price_aud <= 0:
            errors.append(f"[{pack.id}] Price must be positive (${pack.price_aud:.2f} AUD).")

        # Energy Wh consistency check: V * Ah approx Wh
        calc_wh = pack.nominal_voltage_v * pack.capacity_ah
        if abs(calc_wh - pack.energy_wh) / pack.energy_wh > 0.05:
            warnings.append(
                f"[{pack.id}] Energy discrepancy: nominal Wh ({pack.energy_wh}) differs from "
                f"V*Ah ({calc_wh:.1f}Wh) by > 5%."
            )

    # Print summary
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")
        print()

    if errors:
        print(f"FAILED: {len(errors)} error(s) found during validation:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    # Summary breakdown
    chemistry_counts: dict[str, int] = {}
    for pack in validated_packs:
        chemistry_counts[pack.chemistry] = chemistry_counts.get(pack.chemistry, 0) + 1

    print(f"SUCCESS: All {len(validated_packs)} battery packs successfully validated.")
    print("Catalog breakdown by chemistry:")
    for chem, count in sorted(chemistry_counts.items()):
        print(f"  - {chem:12s}: {count} packs")
    print(f"Total catalog energy capacity: {sum(p.energy_wh for p in validated_packs):.1f} Wh")
    print(
        f"Price range: ${min(p.price_aud for p in validated_packs):.2f} - "
        f"${max(p.price_aud for p in validated_packs):.2f} AUD"
    )

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate battery catalog JSON file.")
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "catalog" / "catalog.json",
        help="Path to catalog.json (default: data/catalog/catalog.json)",
    )
    args = parser.parse_args()

    success = validate_catalog(args.path)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
