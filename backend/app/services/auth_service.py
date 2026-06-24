from sqlalchemy.orm import Session

from app.models import Patient
from app.schemas import IdentifyResponse


class PatientNotFoundError(Exception):
    pass


def identify_patient(db: Session, name: str, email_or_phone: str) -> IdentifyResponse:
    """Find existing patient by contact info or create a new one."""
    normalized_contact = email_or_phone.strip().lower()
    patient = (
        db.query(Patient)
        .filter(Patient.email_or_phone == normalized_contact)
        .first()
    )

    if patient:
        if patient.name != name.strip():
            patient.name = name.strip()
            db.commit()
            db.refresh(patient)
        return IdentifyResponse(
            patient_id=patient.id,
            name=patient.name,
            email_or_phone=patient.email_or_phone,
            is_new=False,
        )

    patient = Patient(name=name.strip(), email_or_phone=normalized_contact)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return IdentifyResponse(
        patient_id=patient.id,
        name=patient.name,
        email_or_phone=patient.email_or_phone,
        is_new=True,
    )


def get_patient(db: Session, patient_id: int) -> Patient:
    patient = db.get(Patient, patient_id)
    if not patient:
        raise PatientNotFoundError(f"Patient {patient_id} not found")
    return patient
