"""Fuzzy department and doctor name resolution."""

from difflib import get_close_matches

from sqlalchemy.orm import Session

from app.models import Department, Doctor

DEPARTMENT_ALIASES: dict[str, str] = {
    "cardiology": "Cardiology",
    "cardiologist": "Cardiology",
    "heart": "Cardiology",
    "dermatology": "Dermatology",
    "dermatologist": "Dermatology",
    "skin": "Dermatology",
    "general medicine": "General Medicine",
    "general physician": "General Medicine",
    "gp": "General Medicine",
    "orthopedics": "Orthopedics",
    "orthopaedic": "Orthopedics",
    "orthopedist": "Orthopedics",
    "bone": "Orthopedics",
    "pediatrics": "Pediatrics",
    "pediatrician": "Pediatrics",
    "children": "Pediatrics",
    "ent": "ENT",
    "ear nose throat": "ENT",
    "otolaryngology": "ENT",
}


def resolve_department(db: Session, text: str | None) -> Department | None:
    if not text or not text.strip():
        return None

    lower = text.lower().strip()
    departments = db.query(Department).all()
    by_name = {d.name.lower(): d for d in departments}

    for alias, canonical in DEPARTMENT_ALIASES.items():
        if alias in lower:
            return by_name.get(canonical.lower())

    for dept in departments:
        if dept.name.lower() in lower or lower in dept.name.lower():
            return dept

    close = get_close_matches(lower, list(by_name.keys()), n=1, cutoff=0.6)
    if close:
        return by_name[close[0]]
    return None


def resolve_doctor(
    db: Session,
    doctor_name: str | None,
    department_id: int | None = None,
) -> tuple[Doctor | None, list[str]]:
    """
    Find a doctor by partial name. Returns (doctor, suggestions).
    Suggestions are populated when no unique match is found.
    """
    query = db.query(Doctor)
    if department_id is not None:
        query = query.filter(Doctor.department_id == department_id)
    doctors = query.all()

    if not doctor_name or not doctor_name.strip():
        return None, [d.name for d in doctors]

    normalized = (
        doctor_name.lower()
        .replace("dr.", "")
        .replace("dr", "")
        .strip()
    )
    matches: list[Doctor] = []

    for doctor in doctors:
        doc_lower = doctor.name.lower()
        parts = [p for p in normalized.split() if len(p) > 2]
        if normalized in doc_lower or any(part in doc_lower for part in parts):
            matches.append(doctor)

    if len(matches) == 1:
        return matches[0], []

    if len(matches) > 1:
        return None, [m.name for m in matches]

    all_names = [d.name for d in doctors]
    close = get_close_matches(normalized, [n.lower() for n in all_names], n=3, cutoff=0.4)
    suggestions = [doctors[[n.lower() for n in all_names].index(c)].name for c in close]
    return None, suggestions or all_names[:3]
