"""Shared helpers for LangChain pipeline chains."""

import json
import re
from typing import Any

VALID_INTENTS = frozenset(
    {
        "book_appointment",
        "check_slots",
        "cancel_appointment",
        "reschedule_appointment",
        "clarify",
    }
)


def parse_json_response(text: str) -> dict[str, Any]:
    """Extract and parse a JSON object from an LLM response string."""
    cleaned = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if brace_match:
            cleaned = brace_match.group(0)

    return json.loads(cleaned)


def normalize_slots(raw: dict[str, Any]) -> dict[str, str | None]:
    """Normalize extracted slot dict to consistent string-or-None values."""
    fields = ("department", "doctor_name", "preferred_date", "preferred_time")
    result: dict[str, str | None] = {}
    for field in fields:
        value = raw.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            result[field] = None
        else:
            result[field] = str(value).strip()
    return result
