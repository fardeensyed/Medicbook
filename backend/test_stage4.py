"""Smoke tests for Stage 4 /chat endpoint. Requires GROQ_API_KEY and running server."""

import json
import sys
import urllib.error
import urllib.request
import uuid

BASE = "http://127.0.0.1:8000"
SESSION_ID = f"stage4-{uuid.uuid4().hex[:8]}"


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read())


def check_server() -> bool:
    """Verify the API is up and includes the Stage 4 /chat route."""
    try:
        _get_json(f"{BASE}/health")
        openapi = _get_json(f"{BASE}/openapi.json")
        paths = openapi.get("paths", {})
        if "/chat" not in paths:
            print("ERROR: Server on port 8000 is running but /chat is missing.")
            print("       An old Stage 2 server is likely still bound to port 8000.")
            print("\nFix:")
            print("  1. Find the process:  netstat -ano | findstr :8000")
            print("  2. Kill it:           taskkill /PID <pid> /F")
            print("  3. Restart:           uvicorn main:app --reload --host 127.0.0.1 --port 8000")
            print("  4. Re-run this test in a second terminal while the server stays running.")
            return False
        return True
    except urllib.error.URLError:
        print("ERROR: No server responding at http://127.0.0.1:8000")
        print("Start it first: uvicorn main:app --reload --host 127.0.0.1 --port 8000")
        return False


def post_chat(patient_id: int, message: str) -> tuple[int, dict]:
    body = {
        "patient_id": patient_id,
        "session_id": SESSION_ID,
        "message": message,
    }
    req = urllib.request.Request(
        f"{BASE}/chat",
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def main():
    print("Stage 4 — /chat endpoint smoke test")
    print(f"Session: {SESSION_ID}\n")

    if not check_server():
        sys.exit(1)

    samples = [
        "I want to see a cardiologist this Friday afternoon",
        "Do you have anything with Dr. Sharma tomorrow morning?",
        "Cancel my appointment",
    ]

    patient_id = 1  # Jane Doe from seed data

    for msg in samples:
        print("=" * 60)
        print(f"Patient: {msg}")
        status, data = post_chat(patient_id, msg)
        print(f"Status: {status}")
        if status == 404 and "detail" in data:
            print(f"Error:  {data['detail']}")
        print(f"Intent: {data.get('intent')}")
        print(f"Reply:  {(data.get('reply') or '')[:200]}")
        sd = data.get("structured_data") or {}
        print(f"Type:   {sd.get('type')}")
        print()

    print("Stage 4 smoke test complete.")


if __name__ == "__main__":
    main()
