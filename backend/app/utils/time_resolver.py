"""Resolve natural-language times and filter slots by time-of-day."""

import re
from datetime import time


def get_time_period(text: str | None) -> str | None:
    if not text:
        return None
    lower = text.lower()
    for period in ("morning", "afternoon", "evening"):
        if period in lower:
            return period
    return None


def parse_time(text: str | None) -> time | None:
    """Parse explicit times like '10:00', '2pm', '14:30'. Returns None for vague periods."""
    if not text or not text.strip():
        return None

    if get_time_period(text):
        return None

    lower = text.lower().strip()

    match = re.search(r"(\d{1,2}):(\d{2})(?:\s*(am|pm))?", lower)
    if match:
        hour, minute, meridiem = match.groups()
        hour, minute = int(hour), int(minute)
        if meridiem == "pm" and hour < 12:
            hour += 12
        elif meridiem == "am" and hour == 12:
            hour = 0
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return time(hour, minute)

    match = re.search(r"(\d{1,2})\s*(am|pm)", lower)
    if match:
        hour, meridiem = int(match.group(1)), match.group(2)
        if meridiem == "pm" and hour < 12:
            hour += 12
        elif meridiem == "am" and hour == 12:
            hour = 0
        return time(hour, 0)

    return None


def filter_slots_by_period(slots: list[time], period: str) -> list[time]:
    if period == "morning":
        return [s for s in slots if s.hour < 12]
    if period == "afternoon":
        return [s for s in slots if 12 <= s.hour < 17]
    if period == "evening":
        return [s for s in slots if s.hour >= 17]
    return slots


def pick_slot(slots: list[time], preferred: time | None, period: str | None) -> time | None:
    """Pick the best matching slot from available slots."""
    if not slots:
        return None
    if preferred:
        if preferred in slots:
            return preferred
        # Allow nearest match within 30 min
        for slot in slots:
            if abs(slot.hour * 60 + slot.minute - preferred.hour * 60 - preferred.minute) <= 30:
                return slot
        return None
    if period:
        filtered = filter_slots_by_period(slots, period)
        return filtered[0] if filtered else None
    return None
