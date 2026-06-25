"""Chat orchestration: LangChain pipeline + appointment business logic."""

from datetime import date, time
from typing import Any

from sqlalchemy.orm import Session

from app.models import Doctor
from app.services.appointment_service import (
    AppointmentError,
    book_appointment,
    cancel_appointment,
    get_available_slots,
    list_patient_active_appointments,
    reschedule_appointment,
)
from app.services.auth_service import PatientNotFoundError, get_patient
from app.utils.date_resolver import resolve_date
from app.utils.doctor_lookup import resolve_department, resolve_doctor
from app.utils.time_resolver import get_time_period, parse_time, pick_slot
from langchain_pipeline.intent_chain import classify_intent
from langchain_pipeline.memory import get_history_text, save_turn
from langchain_pipeline.response_chain import generate_response
from langchain_pipeline.slot_extraction import extract_slots


class ChatServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _clarification_result(
    intent: str,
    slots: dict[str, str | None],
    missing_fields: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "type": "clarification",
        "intent": intent,
        "extracted_slots": slots,
        "missing_fields": missing_fields,
        "needs_clarification": True,
    }
    if extra:
        result.update(extra)
    return result


def _appointment_card(appt) -> dict[str, Any]:
    return {
        "type": "booking_confirmation",
        "appointment_id": appt.id,
        "doctor": appt.doctor_name,
        "department": appt.department_name,
        "date": str(appt.appointment_date),
        "time": appt.appointment_time.strftime("%H:%M"),
        "status": appt.status.value,
    }


def _resolve_entities(
    db: Session,
    slots: dict[str, str | None],
) -> dict[str, Any]:
    department = resolve_department(db, slots.get("department"))
    doctor, doctor_suggestions = resolve_doctor(
        db,
        slots.get("doctor_name"),
        department.id if department else None,
    )

    if doctor and not department:
        from app.models import Department

        department = db.get(Department, doctor.department_id)

    resolved_date = resolve_date(slots.get("preferred_date"))
    resolved_time = parse_time(slots.get("preferred_time"))
    time_period = get_time_period(slots.get("preferred_time"))

    return {
        "department": department,
        "doctor": doctor,
        "doctor_suggestions": doctor_suggestions,
        "date": resolved_date,
        "time": resolved_time,
        "time_period": time_period,
    }


def _handle_book(
    db: Session,
    patient_id: int,
    slots: dict[str, str | None],
    entities: dict[str, Any],
) -> dict[str, Any]:
    missing: list[str] = []

    if not entities["department"] and not entities["doctor"]:
        missing.append("department or doctor_name")
    if not entities["date"]:
        missing.append("preferred_date")
    if not entities["time"] and not entities["time_period"]:
        missing.append("preferred_time")

    if missing:
        extra = {}
        if entities["doctor_suggestions"]:
            extra["doctor_suggestions"] = entities["doctor_suggestions"]
        return _clarification_result("book_appointment", slots, missing, extra)

    doctor: Doctor | None = entities["doctor"]
    department = entities["department"]

    if not doctor and department:
        dept_doctors = db.query(Doctor).filter(Doctor.department_id == department.id).all()
        if len(dept_doctors) == 1:
            doctor = dept_doctors[0]

    if not doctor:
        doctor, suggestions = resolve_doctor(
            db, slots.get("doctor_name"), department.id if department else None
        )
        if not doctor:
            return _clarification_result(
                "book_appointment",
                slots,
                ["doctor_name"],
                {
                    "doctor_suggestions": suggestions,
                    "message": (
                        f"No doctor found matching '{slots.get('doctor_name')}'."
                        if slots.get("doctor_name")
                        else "Please specify which doctor you'd like to see."
                    ),
                },
            )

    if not department:
        from app.models import Department

        department = db.get(Department, doctor.department_id)

    target_date: date = entities["date"]
    slots_response = get_available_slots(
        db, target_date, doctor_id=doctor.id
    )
    available = slots_response.doctors[0].slots if slots_response.doctors else []

    chosen_time = pick_slot(available, entities["time"], entities["time_period"])
    if not chosen_time:
        return _clarification_result(
            "book_appointment",
            slots,
            ["preferred_time"],
            {
                "available_slots": [s.strftime("%H:%M") for s in available[:8]],
                "resolved_date": str(target_date),
                "doctor": doctor.name,
            },
        )

    try:
        appt = book_appointment(
            db,
            patient_id=patient_id,
            doctor_id=doctor.id,
            department_id=department.id,
            appointment_date=target_date,
            appointment_time=chosen_time,
        )
        return _appointment_card(appt)
    except AppointmentError as exc:
        return {
            "type": "error",
            "intent": "book_appointment",
            "error": exc.message,
            "extracted_slots": slots,
        }


def _handle_check_slots(
    db: Session,
    slots: dict[str, str | None],
    entities: dict[str, Any],
) -> dict[str, Any]:
    missing: list[str] = []
    if not entities["department"] and not entities["doctor"]:
        missing.append("department or doctor_name")
    if not entities["date"]:
        missing.append("preferred_date")

    if missing:
        extra = {}
        if entities["doctor_suggestions"]:
            extra["doctor_suggestions"] = entities["doctor_suggestions"]
        return _clarification_result("check_slots", slots, missing, extra)

    target_date: date = entities["date"]
    doctor = entities["doctor"]
    department = entities["department"]

    if doctor:
        slots_response = get_available_slots(db, target_date, doctor_id=doctor.id)
    else:
        if not doctor and entities["doctor_suggestions"] and slots.get("doctor_name"):
            return _clarification_result(
                "check_slots",
                slots,
                ["doctor_name"],
                {"doctor_suggestions": entities["doctor_suggestions"]},
            )
        slots_response = get_available_slots(
            db, target_date, department_id=department.id
        )

    doctors_data = []
    for doc_slots in slots_response.doctors:
        available = doc_slots.slots
        if entities["time_period"]:
            from app.utils.time_resolver import filter_slots_by_period

            available = filter_slots_by_period(available, entities["time_period"])
        doctors_data.append(
            {
                "doctor_id": doc_slots.doctor_id,
                "doctor_name": doc_slots.doctor_name,
                "slots": [s.strftime("%H:%M") for s in available],
            }
        )

    return {
        "type": "available_slots",
        "intent": "check_slots",
        "date": str(target_date),
        "department": department.name if department else None,
        "doctors": doctors_data,
    }


def _handle_cancel(db: Session, patient_id: int, slots: dict[str, str | None]) -> dict[str, Any]:
    active = list_patient_active_appointments(db, patient_id)

    if not active:
        return {
            "type": "error",
            "intent": "cancel_appointment",
            "error": "You have no active appointments to cancel.",
            "extracted_slots": slots,
        }

    if len(active) > 1:
        return _clarification_result(
            "cancel_appointment",
            slots,
            ["appointment_id"],
            {
                "active_appointments": [
                    {
                        "appointment_id": a.id,
                        "doctor": a.doctor_name,
                        "date": str(a.appointment_date),
                        "time": a.appointment_time.strftime("%H:%M"),
                    }
                    for a in active
                ],
            },
        )

    try:
        appt = cancel_appointment(db, active[0].id)
        result = _appointment_card(appt)
        result["type"] = "cancellation_confirmation"
        return result
    except AppointmentError as exc:
        return {
            "type": "error",
            "intent": "cancel_appointment",
            "error": exc.message,
        }


def _handle_reschedule(
    db: Session,
    patient_id: int,
    slots: dict[str, str | None],
    entities: dict[str, Any],
) -> dict[str, Any]:
    active = list_patient_active_appointments(db, patient_id)

    if not active:
        return {
            "type": "error",
            "intent": "reschedule_appointment",
            "error": "You have no active appointments to reschedule.",
            "extracted_slots": slots,
        }

    appointment = active[0]
    if len(active) > 1:
        appointment = active[0]
        # If multiple, use first unless date/time in slots implies urgency — keep simple

    missing: list[str] = []
    if not entities["date"]:
        missing.append("preferred_date")
    if not entities["time"] and not entities["time_period"]:
        missing.append("preferred_time")

    if missing:
        return _clarification_result(
            "reschedule_appointment",
            slots,
            missing,
            {
                "current_appointment": {
                    "appointment_id": appointment.id,
                    "doctor": appointment.doctor_name,
                    "date": str(appointment.appointment_date),
                    "time": appointment.appointment_time.strftime("%H:%M"),
                },
            },
        )

    target_date: date = entities["date"]
    doctor_id = appointment.doctor_id
    slots_response = get_available_slots(db, target_date, doctor_id=doctor_id)
    available = slots_response.doctors[0].slots if slots_response.doctors else []
    chosen_time = pick_slot(available, entities["time"], entities["time_period"])

    if not chosen_time:
        return _clarification_result(
            "reschedule_appointment",
            slots,
            ["preferred_time"],
            {
                "available_slots": [s.strftime("%H:%M") for s in available[:8]],
                "resolved_date": str(target_date),
            },
        )

    try:
        appt = reschedule_appointment(
            db,
            appointment.id,
            appointment_date=target_date,
            appointment_time=chosen_time,
        )
        result = _appointment_card(appt)
        result["type"] = "reschedule_confirmation"
        return result
    except AppointmentError as exc:
        return {
            "type": "error",
            "intent": "reschedule_appointment",
            "error": exc.message,
        }


def _handle_clarify(slots: dict[str, str | None]) -> dict[str, Any]:
    return {
        "type": "clarification",
        "intent": "clarify",
        "extracted_slots": slots,
        "needs_clarification": True,
        "message": "How can I help with your appointment today?",
    }


def handle_chat(
    db: Session,
    patient_id: int,
    session_id: str,
    message: str,
) -> dict[str, Any]:
    """
    Full /chat flow:
    memory → intent → slots → business logic → NL response → save memory
    """
    try:
        get_patient(db, patient_id)
    except PatientNotFoundError as exc:
        raise ChatServiceError(str(exc), status_code=404) from exc

    history = get_history_text(session_id)

    try:
        intent = classify_intent(message, history)
        slots = extract_slots(message, history, intent=intent)
    except Exception as exc:
        return {
            "reply": (
                "I'm having trouble processing your request right now. "
                "Please try again in a moment."
            ),
            "structured_data": {"type": "error", "error": "llm_unavailable"},
            "intent": None,
        }

    entities = _resolve_entities(db, slots)

    if intent == "book_appointment":
        structured = _handle_book(db, patient_id, slots, entities)
    elif intent == "check_slots":
        structured = _handle_check_slots(db, slots, entities)
    elif intent == "cancel_appointment":
        structured = _handle_cancel(db, patient_id, slots)
    elif intent == "reschedule_appointment":
        structured = _handle_reschedule(db, patient_id, slots, entities)
    else:
        structured = _handle_clarify(slots)

    try:
        reply = generate_response(structured)
    except Exception:
        reply = _fallback_reply(structured)

    save_turn(session_id, message, reply)

    return {
        "reply": reply,
        "structured_data": structured,
        "intent": intent,
    }


def _fallback_reply(structured: dict[str, Any]) -> str:
    """Simple reply when the LLM response generator fails."""
    type_ = structured.get("type")
    if type_ == "booking_confirmation":
        return (
            f"Your appointment with {structured['doctor']} is confirmed for "
            f"{structured['date']} at {structured['time']}."
        )
    if type_ == "available_slots":
        return "Here are the available appointment slots I found for you."
    if type_ == "cancellation_confirmation":
        return "Your appointment has been cancelled."
    if type_ == "reschedule_confirmation":
        return (
            f"Your appointment has been rescheduled to {structured['date']} "
            f"at {structured['time']}."
        )
    if type_ == "clarification":
        missing = structured.get("missing_fields", [])
        if missing:
            return f"I need a bit more information: {', '.join(missing)}."
        return structured.get("message", "How can I help you with your appointment?")
    if type_ == "error":
        return structured.get("error", "Something went wrong. Please try again.")
    return "How can I help you with your appointment today?"
