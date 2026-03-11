"""Build a treatment calendar from cycle templates + appointments."""

from datetime import date, datetime, timedelta
from typing import List
import calendar

from treatment.cycles import CYCLE_TEMPLATES
from schemas import CalendarDay


def build_calendar(medications, appointments, year: int, month: int) -> List[CalendarDay]:
    """Build calendar days for a given month."""
    num_days = calendar.monthrange(year, month)[1]
    first_day = date(year, month, 1)
    last_day = date(year, month, num_days)

    # Build a dict of date -> CalendarDay
    days = {}

    # Mark treatment days from medications
    for med in medications:
        if not med.cycle_type or not med.cycle_start_date:
            continue

        template = CYCLE_TEMPLATES.get(med.cycle_type)
        if not template:
            continue

        try:
            cycle_start = datetime.strptime(med.cycle_start_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        cycle_length = template["length"]

        # Iterate through every day in the month
        for day_num in range(1, num_days + 1):
            current_date = date(year, month, day_num)
            delta = (current_date - cycle_start).days

            if delta < 0:
                continue

            cycle_day = (delta % cycle_length) + 1
            day_type = template["days"].get(cycle_day, "rest")

            date_str = current_date.isoformat()
            label = f"Day {cycle_day}"
            if day_type == "drug":
                label = f"{template['drug_name']} — Day {cycle_day}"
            elif day_type == "bloodwork":
                label = f"Bloodwork — Day {cycle_day}"

            days[date_str] = CalendarDay(
                date=date_str,
                day_type=day_type,
                label=label,
                drug_name=med.drug_name,
            )

    # Mark appointments (override or add)
    for apt in appointments:
        try:
            apt_date = datetime.strptime(apt.appointment_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        if apt_date.year == year and apt_date.month == month:
            date_str = apt_date.isoformat()
            existing = days.get(date_str)
            if existing:
                # Upgrade day type to appointment so it's visually highlighted
                apt_label = apt.appointment_type or "Appointment"
                if apt.doctor_name:
                    apt_label += f" — {apt.doctor_name}"
                if existing.day_type in ("rest", "none"):
                    existing.day_type = "appointment"
                    existing.label = apt_label
                else:
                    # Drug or bloodwork day — keep original type but append appointment
                    existing.label = f"{existing.label} | {apt_label}"
            else:
                apt_label = apt.appointment_type or "Appointment"
                if apt.doctor_name:
                    apt_label += f" — {apt.doctor_name}"
                days[date_str] = CalendarDay(
                    date=date_str,
                    day_type="appointment",
                    label=apt_label,
                )

    # Fill in remaining days as empty
    for day_num in range(1, num_days + 1):
        date_str = date(year, month, day_num).isoformat()
        if date_str not in days:
            days[date_str] = CalendarDay(date=date_str, day_type="none", label="")

    return sorted(days.values(), key=lambda d: d.date)
