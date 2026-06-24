"""Quick verification script — run after seed_data.py."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "medibook.db"


def verify():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Run: python seed_data.py")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    tables = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    print("Tables:", [t[0] for t in tables])

    print("\nDepartments:")
    for row in cur.execute("SELECT id, name FROM departments ORDER BY name"):
        print(f"  {row}")

    print("\nDoctors:")
    for row in cur.execute(
        "SELECT d.id, d.name, dept.name, d.available_days "
        "FROM doctors d JOIN departments dept ON d.department_id = dept.id"
    ):
        print(f"  {row}")

    print("\nAppointments:")
    for row in cur.execute(
        "SELECT a.id, p.name, d.name, a.appointment_date, a.appointment_time, a.status "
        "FROM appointments a "
        "JOIN patients p ON a.patient_id = p.id "
        "JOIN doctors d ON a.doctor_id = d.id"
    ):
        print(f"  {row}")

    conn.close()
    print("\nVerification complete.")


if __name__ == "__main__":
    verify()
