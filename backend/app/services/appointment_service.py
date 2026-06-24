from datetime import date, time

from sqlalchemy.orm import Session

from app.models import Appointment, AppointmentStatus, Department, Doctor
from app.schemas import AppointmentResponse, DoctorSlots, SlotsResponse
from app.utils.slots import get_available_slots_for_department, get_available_slots_for_doctor


class AppointmentError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AppointmentNotFoundError(AppointmentError):
    def __init__(self, appointment_id: int):
        super().__init__(f"Appointment {appointment_id} not found", status_code=404)


def _to_response(db: Session, appointment: Appointment) -> AppointmentResponse:
    doctor = db.get(Doctor, appointment.doctor_id)
    department = db.get(Department, appointment.department_id)
    return AppointmentResponse(
        id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        department_id=appointment.department_id,
        doctor_name=doctor.name if doctor else "",
        department_name=department.name if department else "",
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        status=appointment.status,
        created_at=appointment.created_at,
        updated_at=appointment.updated_at,
    )


def _validate_doctor_department(db: Session, doctor_id: int, department_id: int) -> Doctor:
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise AppointmentError(f"Doctor {doctor_id} not found", status_code=404)
    if doctor.department_id != department_id:
        raise AppointmentError(
            f"Doctor {doctor.name} does not belong to department {department_id}"
        )
    department = db.get(Department, department_id)
    if not department:
        raise AppointmentError(f"Department {department_id} not found", status_code=404)
    return doctor


def _check_slot_conflict(
    db: Session,
    doctor_id: int,
    appointment_date: date,
    appointment_time: time,
    exclude_appointment_id: int | None = None,
) -> None:
    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status == AppointmentStatus.BOOKED,
    )
    if exclude_appointment_id is not None:
        query = query.filter(Appointment.id != exclude_appointment_id)
    if query.first():
        raise AppointmentError(
            "This time slot is already booked for the selected doctor",
            status_code=409,
        )


def _validate_slot_available(
    db: Session,
    doctor: Doctor,
    appointment_date: date,
    appointment_time: time,
    exclude_appointment_id: int | None = None,
) -> None:
    if appointment_date < date.today():
        raise AppointmentError("Cannot book appointments in the past")

    appointments = db.query(Appointment).all()
    available = get_available_slots_for_doctor(doctor, appointment_date, appointments)
    if appointment_time not in available:
        raise AppointmentError(
            "Requested time is not available for this doctor on the selected date"
        )
    _check_slot_conflict(db, doctor.id, appointment_date, appointment_time, exclude_appointment_id)


def get_available_slots(
    db: Session,
    target_date: date,
    doctor_id: int | None = None,
    department_id: int | None = None,
) -> SlotsResponse:
    if doctor_id is None and department_id is None:
        raise AppointmentError("Provide doctor_id or department_id")

    if target_date < date.today():
        raise AppointmentError("Cannot query slots for past dates")

    appointments = db.query(Appointment).all()
    doctors: list[DoctorSlots] = []

    if doctor_id is not None:
        doctor = db.get(Doctor, doctor_id)
        if not doctor:
            raise AppointmentError(f"Doctor {doctor_id} not found", status_code=404)
        slots = get_available_slots_for_doctor(doctor, target_date, appointments)
        doctors.append(DoctorSlots(doctor_id=doctor.id, doctor_name=doctor.name, slots=slots))
        return SlotsResponse(
            date=target_date,
            doctor_id=doctor_id,
            department_id=doctor.department_id,
            doctors=doctors,
        )

    department = db.get(Department, department_id)
    if not department:
        raise AppointmentError(f"Department {department_id} not found", status_code=404)

    all_doctors = db.query(Doctor).filter(Doctor.department_id == department_id).all()
    slot_map = get_available_slots_for_department(
        all_doctors, department_id, target_date, appointments
    )
    doctor_by_id = {d.id: d for d in all_doctors}
    for doc_id, slots in slot_map.items():
        doctors.append(
            DoctorSlots(
                doctor_id=doc_id,
                doctor_name=doctor_by_id[doc_id].name,
                slots=slots,
            )
        )

    return SlotsResponse(
        date=target_date,
        department_id=department_id,
        doctors=doctors,
    )


def book_appointment(
    db: Session,
    patient_id: int,
    doctor_id: int,
    department_id: int,
    appointment_date: date,
    appointment_time: time,
) -> AppointmentResponse:
    doctor = _validate_doctor_department(db, doctor_id, department_id)
    _validate_slot_available(db, doctor, appointment_date, appointment_time)

    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        department_id=department_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        status=AppointmentStatus.BOOKED,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return _to_response(db, appointment)


def cancel_appointment(db: Session, appointment_id: int) -> AppointmentResponse:
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise AppointmentNotFoundError(appointment_id)
    if appointment.status == AppointmentStatus.CANCELLED:
        raise AppointmentError("Appointment is already cancelled")

    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    db.refresh(appointment)
    return _to_response(db, appointment)


def reschedule_appointment(
    db: Session,
    appointment_id: int,
    doctor_id: int | None = None,
    department_id: int | None = None,
    appointment_date: date | None = None,
    appointment_time: time | None = None,
) -> AppointmentResponse:
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise AppointmentNotFoundError(appointment_id)
    if appointment.status == AppointmentStatus.CANCELLED:
        raise AppointmentError("Cannot reschedule a cancelled appointment")

    new_doctor_id = doctor_id or appointment.doctor_id
    new_department_id = department_id or appointment.department_id
    new_date = appointment_date or appointment.appointment_date
    new_time = appointment_time or appointment.appointment_time

    doctor = _validate_doctor_department(db, new_doctor_id, new_department_id)
    _validate_slot_available(
        db, doctor, new_date, new_time, exclude_appointment_id=appointment.id
    )

    appointment.doctor_id = new_doctor_id
    appointment.department_id = new_department_id
    appointment.appointment_date = new_date
    appointment.appointment_time = new_time
    appointment.status = AppointmentStatus.RESCHEDULED
    db.commit()
    db.refresh(appointment)
    return _to_response(db, appointment)


def get_appointment(db: Session, appointment_id: int) -> AppointmentResponse:
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise AppointmentNotFoundError(appointment_id)
    return _to_response(db, appointment)
