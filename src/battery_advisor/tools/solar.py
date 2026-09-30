"""Plan Melbourne solar charging using local sun times and monthly yield estimates."""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from astral import LocationInfo
from astral.sun import sun

TZ = ZoneInfo("Australia/Melbourne")
MELBOURNE = LocationInfo("Melbourne", "Australia", "Australia/Melbourne", -37.8136, 144.9631)

# Approximate mean daily solar exposure for Melbourne, kWh/m2/day (Jan..Dec).
# Placeholder figures for planning; replace with Bureau of Meteorology data.
PEAK_SUN_HOURS = [6.4, 5.6, 4.4, 3.0, 2.1, 1.7, 1.8, 2.5, 3.6, 4.9, 5.7, 6.3]

def melbourne_sun_times(on_date: str | None = None) -> dict:
    """Return Melbourne sunrise, sunset, daylight hours, and a charging window.

    Accept a date in YYYY-MM-DD format; default to today's Melbourne date.
    Times use Australia/Melbourne, including daylight saving. The estimated
    charging window excludes the first and last hour of daylight.
    """
    d = date.fromisoformat(on_date) if on_date else datetime.now(TZ).date()
    s = sun(MELBOURNE.observer, date=d, tzinfo=TZ)
    daylight = s["sunset"] - s["sunrise"]
    return {
        "date": d.isoformat(),
        "sunrise": s["sunrise"].strftime("%H:%M"),
        "sunset": s["sunset"].strftime("%H:%M"),
        "daylight_h": round(daylight.total_seconds() / 3600, 1),
        # Low-angle sun yields little; assume useful charging starts 1 h after sunrise, ends 1 h before sunset
        "charge_window": f'{(s["sunrise"] + timedelta(hours=1)).strftime("%H:%M")}-'
                         f'{(s["sunset"] - timedelta(hours=1)).strftime("%H:%M")}',
        "timezone": "Australia/Melbourne",
    }

def solar_charge_plan(pack_id: str, panel_w: float, month: int | None = None) -> dict:
    """Estimate daily solar Wh and days to charge a catalog pack from empty.

    Supply a positive panel rating in watts and a month from 1 to 12; the month
    defaults to the current Melbourne month. Use approximate monthly peak sun
    hours and 75% system efficiency, assuming no concurrent battery load.
    Return yield, charging days, and assumptions, or an error for an unknown ID.
    """
    from battery_advisor.tools.catalog_search import get_pack
    p = get_pack(pack_id)
    if p is None:
        return {"error": f"unknown pack {pack_id}"}
    m = month or datetime.now(TZ).month
    daily_wh = panel_w * PEAK_SUN_HOURS[m - 1] * 0.75      # 0.75 = wiring/controller/heat losses
    return {
        "pack_id": pack_id, "month": m, "panel_w": panel_w,
        "daily_yield_wh": round(daily_wh),
        "days_to_full_from_empty": round(p.energy_wh / daily_wh, 1),
        "assumptions": f"{PEAK_SUN_HOURS[m-1]} peak sun hours, 75% system efficiency",
    }
