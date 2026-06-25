from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import IdentifyRequest, IdentifyResponse, LoginRequest, RegisterRequest
from app.services.auth_service import (
    PatientNotFoundError,
    identify_patient,
    login_patient,
    register_patient,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/identify", response_model=IdentifyResponse)
def identify(payload: IdentifyRequest, db: Session = Depends(get_db)):
    return identify_patient(db, payload.name, payload.email_or_phone)


@router.post("/login", response_model=IdentifyResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        patient = login_patient(db, payload.email_or_phone)
        return IdentifyResponse(
            patient_id=patient.id,
            name=patient.name,
            email_or_phone=patient.email_or_phone,
            is_new=False,
        )
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/register", response_model=IdentifyResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        patient = register_patient(db, payload.name, payload.email_or_phone)
        return IdentifyResponse(
            patient_id=patient.id,
            name=patient.name,
            email_or_phone=patient.email_or_phone,
            is_new=True,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

