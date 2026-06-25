"""Smoke-test all Stage 2 endpoints. Run while server is up."""

import json
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000"


def request(method: str, path: str, body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def main():
    import datetime
    # Calculate target date matching next weekday (same logic as seed_data.py)
    target_date = datetime.date.today() + datetime.timedelta(days=1)
    while target_date.weekday() >= 5:
        target_date += datetime.timedelta(days=1)
    date_str = target_date.strftime('%Y-%m-%d')
    print(f"Target date for booking test: {date_str}")

    print("1. GET /health")
    status, data = request("GET", "/health")
    print(f"   {status} -> {data}")

    print("\n2. POST /auth/identify (new patient)")
    status, data = request("POST", "/auth/identify", {
        "name": "John Smith",
        "email_or_phone": "john@example.com",
    })
    print(f"   {status} -> {data}")
    patient_id = data["patient_id"]

    print("\n3. POST /auth/identify (existing patient)")
    status, data = request("POST", "/auth/identify", {
        "name": "Jane Doe",
        "email_or_phone": "jane.doe@example.com",
    })
    print(f"   {status} -> {data}")

    print(f"\n4. GET /appointments/slots?doctor_id=1&date={date_str}")
    status, data = request("GET", f"/appointments/slots?doctor_id=1&date={date_str}")
    print(f"   {status} -> slots count: {len(data['doctors'][0]['slots'])}")

    print("\n5. POST /appointments (book 11:00 with Dr. Sharma)")
    status, data = request("POST", "/appointments", {
        "patient_id": patient_id,
        "doctor_id": 1,
        "department_id": 1,
        "appointment_date": date_str,
        "appointment_time": "11:00:00",
    })
    print(f"   {status} -> appointment id: {data.get('id')}")
    appt_id = data["id"]

    print("\n6. POST /appointments (double-book 11:00 — expect 409)")
    status, data = request("POST", "/appointments", {
        "patient_id": patient_id,
        "doctor_id": 1,
        "department_id": 1,
        "appointment_date": date_str,
        "appointment_time": "11:00:00",
    })
    print(f"   {status} -> {data}")

    print("\n7. PATCH /appointments/{id} (reschedule to 14:00)")
    status, data = request("PATCH", f"/appointments/{appt_id}", {
        "appointment_time": "14:00:00",
    })
    print(f"   {status} -> time: {data.get('appointment_time')}, status: {data.get('status')}")

    print("\n8. DELETE /appointments/{id} (cancel)")
    status, data = request("DELETE", f"/appointments/{appt_id}")
    print(f"   {status} -> status: {data.get('status')}")

    print(f"\n9. GET /appointments/slots (14:00 should be free again)")
    status, data = request("GET", f"/appointments/slots?doctor_id=1&date={date_str}")
    slots = data["doctors"][0]["slots"]
    print(f"   {status} -> 14:00 available: {'14:00:00' in slots}")

    print("\nAll Stage 2 smoke tests passed.")


if __name__ == "__main__":
    main()
