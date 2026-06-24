from datetime import date, datetime, time

from pydantic import BaseModel, Field

from app.models import AppointmentStatus


class IdentifyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email_or_phone: str = Field(..., min_length=3, max_length=150)


class IdentifyResponse(BaseModel):
    patient_id: int
    name: str
    email_or_phone: str
    is_new: bool


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    department_id: int
    appointment_date: date
    appointment_time: time


class AppointmentUpdate(BaseModel):
    doctor_id: int | None = None
    department_id: int | None = None
    appointment_date: date | None = None
    appointment_time: time | None = None
    status: AppointmentStatus | None = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    department_id: int
    doctor_name: str
    department_name: str
    appointment_date: date
    appointment_time: time
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DoctorSlots(BaseModel):
    doctor_id: int
    doctor_name: str
    slots: list[time]


class SlotsResponse(BaseModel):
    date: date
    department_id: int | None = None
    doctor_id: int | None = None
    doctors: list[DoctorSlots]


class HealthResponse(BaseModel):
    status: str
