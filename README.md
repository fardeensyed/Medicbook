# MediBook

An intelligent medical appointment booking chatbot. Patients chat in natural language to book, check, cancel, or reschedule appointments — no forms or dropdowns for the core booking flow easy and simple

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python 3.11+) |
| LLM orchestration | LangChain (prompt templates, chains, `ConversationBufferMemory`) |
| LLM inference | Groq API (`llama-3.1-70b-versatile` / `mixtral-8x7b-32768`) via `langchain-groq` |
| Frontend | React (Vite) — *planned* |
| Database | SQLite via SQLAlchemy |
| Auth | Lightweight identity capture (name + email/phone, no passwords/JWT) |

## Architecture

```
Patient (React Chat UI)          [Stage 5 — not yet built]
        │
        ▼
FastAPI Backend (/chat)          [Stage 4 — not yet built]
        │
        ▼
LangChain Pipeline               [Stage 3 — not yet built]
  (intent + slot extraction + ConversationBufferMemory)
        │
        ▼
Groq LLM (LLaMA 3 / Mixtral)
        │
        ▼
Appointment Service Layer        [Stage 2 — done]
        │
        ▼
SQLite Database                  [Stage 1 — done]
        │
        ▼
Structured response → React UI
```

## Progress

| Stage | Description | Status |
|-------|-------------|--------|
| **1** | Database layer (SQLAlchemy models, seed data, slot generation) | Done |
| **2** | FastAPI skeleton (health, auth, appointment CRUD, slots API) | Done |
| **3** | LangChain + Groq pipeline (intent, slot extraction, memory) | Pending |
| **4** | Wire pipeline into `/chat` endpoint | Pending |
| **5** | React frontend (chat UI, login gate, booking card) | Pending |
| **6** | Polish (README, tests, error handling) | Pending |

### Stage 1 — Database Layer

- SQLAlchemy models: `Patient`, `Department`, `Doctor`, `Appointment`
- Seeded 6 departments and 6 doctors with realistic weekly availability
- Programmatic 30-minute slot generation (`app/utils/slots.py`)
- Sample patient and appointments for testing

### Stage 2 — FastAPI Skeleton

- `GET /health` — health check
- `POST /auth/identify` — create or find patient by name + email/phone
- `GET /appointments/slots` — available slots by doctor or department + date
- `POST /appointments` — book appointment
- `GET /appointments/{id}` — get appointment details
- `PATCH /appointments/{id}` — reschedule appointment
- `DELETE /appointments/{id}` — cancel appointment
- Business logic in `appointment_service.py` (double-booking prevention, past-date validation)

## Project Structure

```
medic/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── services/        # Business logic (auth, appointments)
│   │   ├── routers/         # FastAPI route handlers
│   │   ├── utils/           # Slot generation utilities
│   │   ├── config.py
│   │   └── database.py
│   ├── main.py              # FastAPI entry point
│   ├── seed_data.py         # Database seeder
│   ├── verify_db.py         # DB verification script
│   ├── test_stage2.py       # API smoke tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── package.json         # React/Vite scaffold (Stage 5)
│   └── .env.example
└── .gitignore
```

## Setup

### Prerequisites

- Python 3.11+
- Git

### Backend

```powershell
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment file and add your Groq API key (needed from Stage 3 onward)
copy .env.example .env

# Seed the database
python seed_data.py

# Verify seeded data
python verify_db.py

# Start the API server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Run smoke tests

With the server running in another terminal:

```powershell
python test_stage2.py
```

## API Endpoints (Stage 2)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/auth/identify` | Identify patient `{ name, email_or_phone }` |
| `GET` | `/appointments/slots?doctor_id=&date=` | Available slots for a doctor |
| `GET` | `/appointments/slots?department_id=&date=` | Available slots for a department |
| `POST` | `/appointments` | Book appointment |
| `GET` | `/appointments/{id}` | Get appointment |
| `PATCH` | `/appointments/{id}` | Reschedule appointment |
| `DELETE` | `/appointments/{id}` | Cancel appointment |

### Example requests (PowerShell)

```powershell
# Health check
Invoke-RestMethod http://127.0.0.1:8000/health

# Identify patient
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/auth/identify `
  -ContentType "application/json" `
  -Body '{"name":"Jane Doe","email_or_phone":"jane@example.com"}'

# Check available slots
Invoke-RestMethod "http://127.0.0.1:8000/appointments/slots?doctor_id=1&date=2026-06-25"

# Book appointment
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/appointments `
  -ContentType "application/json" `
  -Body '{"patient_id":1,"doctor_id":1,"department_id":1,"appointment_date":"2026-06-25","appointment_time":"11:00:00"}'
```

## Seeded Data

**Departments:** Cardiology, Dermatology, General Medicine, Orthopedics, Pediatrics, ENT

**Doctors:**

| Doctor | Department | Available Days |
|--------|------------|----------------|
| Dr. Ananya Sharma | Cardiology | Mon–Fri, 9:00–17:00 |
| Dr. Rajesh Mehta | Dermatology | Mon/Wed/Fri, 10:00–16:00 |
| Dr. Priya Nair | General Medicine | Mon–Fri, 8:30–16:30 |
| Dr. Vikram Singh | Orthopedics | Tue/Thu/Sat, 9:30–15:30 |
| Dr. Meera Kapoor | Pediatrics | Mon–Fri, 9:00–14:00 |
| Dr. Arjun Desai | ENT | Mon/Wed/Thu/Fri, 10:00–18:00 |

## Environment Variables

**Backend** (`backend/.env`):

```
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///./medibook.db
```

**Frontend** (`frontend/.env`) — for Stage 5:

```
VITE_API_BASE_URL=http://localhost:8000
```

## License

Academic project — not for production use.
