from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import IdentifyRequest, IdentifyResponse
from app.services.auth_service import identify_patient

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/identify", response_model=IdentifyResponse)
def identify(payload: IdentifyRequest, db: Session = Depends(get_db)):
    return identify_patient(db, payload.name, payload.email_or_phone)
