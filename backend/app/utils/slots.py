"""Programmatic time-slot generation for doctor availability."""

from datetime import date, datetime, time, timedelta
from typing import Iterable

from app.models import Appointment, AppointmentStatus, Doctor

SLOT_INTERVAL_MINUTES = 30

WEEKDAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def doctor_works_on_day(doctor: Doctor, target_date: date) -> bool:
    weekday = WEEKDAY_NAMES[target_date.weekday()]
    available_days = [d.strip() for d in doctor.available_days.split(",")]
    return weekday in available_days


def generate_time_slots(
    start_time: time,
    end_time: time,
    interval_minutes: int = SLOT_INTERVAL_MINUTES,
) -> list[time]:
    """Generate fixed-interval slots within a doctor's working hours."""
    slots: list[time] = []
    current = datetime.combine(date.today(), start_time)
    end = datetime.combine(date.today(), end_time)

    while current + timedelta(minutes=interval_minutes) <= end:
        slots.append(current.time())
        current += timedelta(minutes=interval_minutes)

    return slots


def get_booked_times(
    appointments: Iterable[Appointment],
    doctor_id: int,
    target_date: date,
) -> set[time]:
    """Return times already booked for a doctor on a given date."""
    booked: set[time] = set()
    for appt in appointments:
        if (
            appt.doctor_id == doctor_id
            and appt.appointment_date == target_date
            and appt.status == AppointmentStatus.BOOKED
        ):
            booked.add(appt.appointment_time)
    return booked


def get_available_slots_for_doctor(
    doctor: Doctor,
    target_date: date,
    appointments: Iterable[Appointment],
    interval_minutes: int = SLOT_INTERVAL_MINUTES,
) -> list[time]:
    """
    Return available 30-minute slots for a doctor on a date,
    excluding already-booked appointments.
    """
    if not doctor_works_on_day(doctor, target_date):
        return []

    all_slots = generate_time_slots(
        doctor.available_start_time,
        doctor.available_end_time,
        interval_minutes,
    )
    booked = get_booked_times(appointments, doctor.id, target_date)
    return [slot for slot in all_slots if slot not in booked]


def get_available_slots_for_department(
    doctors: Iterable[Doctor],
    department_id: int,
    target_date: date,
    appointments: Iterable[Appointment],
    interval_minutes: int = SLOT_INTERVAL_MINUTES,
) -> dict[int, list[time]]:
    """Return available slots keyed by doctor_id for all doctors in a department."""
    result: dict[int, list[time]] = {}
    for doctor in doctors:
        if doctor.department_id != department_id:
            continue
        slots = get_available_slots_for_doctor(doctor, target_date, appointments, interval_minutes)
        if slots:
            result[doctor.id] = slots
    return result
