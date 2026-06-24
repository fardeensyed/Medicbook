"""
Seed MediBook database with departments, doctors, and sample data.

Run from the backend directory:
    python seed_data.py
"""

from datetime import date, time, timedelta

from app.database import SessionLocal, init_db
from app.models import Appointment, AppointmentStatus, Department, Doctor, Patient
from app.utils.slots import get_available_slots_for_doctor

DEPARTMENTS = [
    "Cardiology",
    "Dermatology",
    "General Medicine",
    "Orthopedics",
    "Pediatrics",
    "ENT",
]

DOCTORS = [
    {
        "name": "Dr. Ananya Sharma",
        "department": "Cardiology",
        "available_days": "Monday,Tuesday,Wednesday,Thursday,Friday",
        "start": time(9, 0),
        "end": time(17, 0),
    },
    {
        "name": "Dr. Rajesh Mehta",
        "department": "Dermatology",
        "available_days": "Monday,Wednesday,Friday",
        "start": time(10, 0),
        "end": time(16, 0),
    },
    {
        "name": "Dr. Priya Nair",
        "department": "General Medicine",
        "available_days": "Monday,Tuesday,Wednesday,Thursday,Friday",
        "start": time(8, 30),
        "end": time(16, 30),
    },
    {
        "name": "Dr. Vikram Singh",
        "department": "Orthopedics",
        "available_days": "Tuesday,Thursday,Saturday",
        "start": time(9, 30),
        "end": time(15, 30),
    },
    {
        "name": "Dr. Meera Kapoor",
        "department": "Pediatrics",
        "available_days": "Monday,Tuesday,Wednesday,Thursday,Friday",
        "start": time(9, 0),
        "end": time(14, 0),
    },
    {
        "name": "Dr. Arjun Desai",
        "department": "ENT",
        "available_days": "Monday,Wednesday,Thursday,Friday",
        "start": time(10, 0),
        "end": time(18, 0),
    },
]


def seed():
    init_db()
    db = SessionLocal()

    try:
        if db.query(Department).count() > 0:
            print("Database already seeded. Skipping.")
            return

        # Departments
        dept_map: dict[str, Department] = {}
        for name in DEPARTMENTS:
            dept = Department(name=name)
            db.add(dept)
            dept_map[name] = dept
        db.flush()

        # Doctors
        doctor_records: list[Doctor] = []
        for doc_data in DOCTORS:
            doctor = Doctor(
                name=doc_data["name"],
                department_id=dept_map[doc_data["department"]].id,
                available_days=doc_data["available_days"],
                available_start_time=doc_data["start"],
                available_end_time=doc_data["end"],
            )
            db.add(doctor)
            doctor_records.append(doctor)
        db.flush()

        # Sample patient
        patient = Patient(name="Jane Doe", email_or_phone="jane.doe@example.com")
        db.add(patient)
        db.flush()

        # Book a couple of appointments on the next available weekday
        today = date.today()
        target_date = today + timedelta(days=1)
        while target_date.weekday() >= 5:  # skip weekend
            target_date += timedelta(days=1)

        cardiologist = next(d for d in doctor_records if "Sharma" in d.name)
        general_doc = next(d for d in doctor_records if "Nair" in d.name)

        appt1 = Appointment(
            patient_id=patient.id,
            doctor_id=cardiologist.id,
            department_id=cardiologist.department_id,
            appointment_date=target_date,
            appointment_time=time(10, 0),
            status=AppointmentStatus.BOOKED,
        )
        appt2 = Appointment(
            patient_id=patient.id,
            doctor_id=general_doc.id,
            department_id=general_doc.department_id,
            appointment_date=target_date,
            appointment_time=time(9, 0),
            status=AppointmentStatus.BOOKED,
        )
        db.add_all([appt1, appt2])
        db.commit()

        # Print verification summary
        print("=" * 60)
        print("MediBook seed complete")
        print("=" * 60)

        print(f"\nDepartments ({db.query(Department).count()}):")
        for dept in db.query(Department).order_by(Department.name):
            doc_count = db.query(Doctor).filter(Doctor.department_id == dept.id).count()
            print(f"  [{dept.id}] {dept.name} ({doc_count} doctor(s))")

        print(f"\nDoctors ({db.query(Doctor).count()}):")
        for doc in db.query(Doctor).order_by(Doctor.id):
            dept_name = db.get(Department, doc.department_id).name
            print(
                f"  [{doc.id}] {doc.name} — {dept_name} | "
                f"{doc.available_days} | {doc.available_start_time}-{doc.available_end_time}"
            )

        print(f"\nPatients ({db.query(Patient).count()}):")
        for p in db.query(Patient):
            print(f"  [{p.id}] {p.name} ({p.email_or_phone})")

        print(f"\nAppointments ({db.query(Appointment).count()}):")
        for appt in db.query(Appointment):
            doc = db.get(Doctor, appt.doctor_id)
            print(
                f"  [{appt.id}] {appt.appointment_date} {appt.appointment_time} "
                f"with {doc.name} — {appt.status.value}"
            )

        # Demonstrate programmatic slot generation
        all_appointments = db.query(Appointment).all()
        print(f"\nAvailable slots for Dr. Sharma on {target_date} (10:00 should be taken):")
        slots = get_available_slots_for_doctor(cardiologist, target_date, all_appointments)
        print(f"  {len(slots)} slots: {', '.join(s.strftime('%H:%M') for s in slots[:6])}...")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
