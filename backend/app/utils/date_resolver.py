"""Resolve natural-language dates to concrete date objects."""

import re
from datetime import date, timedelta

WEEKDAY_NAMES = {
    "monday": 0,
    "mon": 0,
    "tuesday": 1,
    "tue": 1,
    "tues": 1,
    "wednesday": 2,
    "wed": 2,
    "thursday": 3,
    "thu": 3,
    "thur": 3,
    "thurs": 3,
    "friday": 4,
    "fri": 4,
    "saturday": 5,
    "sat": 5,
    "sunday": 6,
    "sun": 6,
}


def resolve_date(text: str | None, reference: date | None = None) -> date | None:
    """Convert strings like 'Friday', 'tomorrow', or '2026-06-25' to a date."""
    if not text or not text.strip():
        return None

    ref = reference or date.today()
    lower = text.lower().strip()

    if lower == "today":
        return ref
    if lower == "tomorrow":
        return ref + timedelta(days=1)
    if lower == "day after tomorrow":
        return ref + timedelta(days=2)

    iso_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if iso_match:
        try:
            return date.fromisoformat(iso_match.group(1))
        except ValueError:
            pass

    slash_match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", text)
    if slash_match:
        day, month, year = slash_match.groups()
        year = int(year)
        if year < 100:
            year += 2000
        try:
            return date(year, int(month), int(day))
        except ValueError:
            pass

    use_next = "next" in lower
    for name, weekday in WEEKDAY_NAMES.items():
        if re.search(rf"\b{re.escape(name)}\b", lower):
            days_ahead = (weekday - ref.weekday()) % 7
            if days_ahead == 0 and use_next:
                days_ahead = 7
            elif days_ahead == 0 and not use_next:
                # Same weekday mentioned — treat as today if it matches, else next week
                if ref.weekday() != weekday:
                    days_ahead = 7
            return ref + timedelta(days=days_ahead)

    return None
