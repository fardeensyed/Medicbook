from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AppointmentStatus, Department, Doctor
from app.schemas import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
    DepartmentResponse,
    DoctorResponse,
    SlotsResponse,
)
from app.services.appointment_service import (
    AppointmentError,
    book_appointment,
    cancel_appointment,
    get_appointment,
    get_available_slots,
    list_patient_active_appointments,
    reschedule_appointment,
)
from app.services.auth_service import PatientNotFoundError, get_patient

router = APIRouter(prefix="/appointments", tags=["appointments"])



def _handle_service_error(exc: AppointmentError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("/slots", response_model=SlotsResponse)
def list_available_slots(
    date: date = Query(..., description="Date in YYYY-MM-DD format"),
    doctor_id: int | None = Query(None),
    department_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    try:
        return get_available_slots(db, date, doctor_id=doctor_id, department_id=department_id)
    except AppointmentError as exc:
        raise _handle_service_error(exc) from exc


@router.post("", response_model=AppointmentResponse, status_code=201)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        get_patient(db, payload.patient_id)
        return book_appointment(
            db,
            patient_id=payload.patient_id,
            doctor_id=payload.doctor_id,
            department_id=payload.department_id,
            appointment_date=payload.appointment_date,
            appointment_time=payload.appointment_time,
        )
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AppointmentError as exc:
        raise _handle_service_error(exc) from exc


@router.get("/doctors", response_model=list[DoctorResponse])
def list_doctors(db: Session = Depends(get_db)):
    doctors = db.query(Doctor).all()
    res = []
    for doc in doctors:
        dept = db.get(Department, doc.department_id)
        res.append(
            DoctorResponse(
                id=doc.id,
                name=doc.name,
                department_id=doc.department_id,
                department_name=dept.name if dept else "",
                available_days=doc.available_days,
                available_start_time=doc.available_start_time,
                available_end_time=doc.available_end_time,
            )
        )
    return res


@router.get("/departments", response_model=list[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()


@router.get("/patient/{patient_id}", response_model=list[AppointmentResponse])
def list_patient_appts(patient_id: int, db: Session = Depends(get_db)):
    try:
        get_patient(db, patient_id)
        return list_patient_active_appointments(db, patient_id)
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def read_appointment(appointment_id: int, db: Session = Depends(get_db)):
    try:
        return get_appointment(db, appointment_id)
    except AppointmentError as exc:
        raise _handle_service_error(exc) from exc


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    try:
        if payload.status == AppointmentStatus.CANCELLED:
            return cancel_appointment(db, appointment_id)
        return reschedule_appointment(
            db,
            appointment_id,
            doctor_id=payload.doctor_id,
            department_id=payload.department_id,
            appointment_date=payload.appointment_date,
            appointment_time=payload.appointment_time,
        )
    except AppointmentError as exc:
        raise _handle_service_error(exc) from exc


@router.delete("/{appointment_id}", response_model=AppointmentResponse)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    try:
        return cancel_appointment(db, appointment_id)
    except AppointmentError as exc:
        raise _handle_service_error(exc) from exc


