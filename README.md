# MediBook

An intelligent medical appointment booking chatbot. Patients chat in natural language to book, check, cancel, or reschedule appointments — no forms or dropdowns for the core booking flow easy and simple

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python 3.11+) |
| LLM orchestration | LangChain (prompt templates, chains, `ConversationBufferMemory`) |
| LLM inference | Groq API (`llama-3.1-70b-versatile` / `mixtral-8x7b-32768`) via `langchain-groq` |
| Frontend | React (Vite) |
| Database | SQLite via SQLAlchemy |
| Auth | Lightweight identity capture (name + email/phone, no passwords/JWT) |

## Architecture

```
Patient (React Chat UI)          [Stage 5 — done]
        │
        ▼
FastAPI Backend (/chat)          [Stage 4 — done]
        │
        ▼
LangChain Pipeline               [Stage 3 — done]
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
| **3** | LangChain + Groq pipeline (intent, slot extraction, memory) | Done |
| **4** | Wire pipeline into `/chat` endpoint | Done |
| **5** | React frontend (chat UI, login gate, booking card) | Done |
| **6** | Polish (README, tests, error handling) | Done |
| **7** | Dashboard Layout, Landing Page, Auth Separator & Directory APIs | Done |


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

### Stage 3 — LangChain + Groq Pipeline

- `langchain_pipeline/llm.py` — Groq client via `langchain-groq` (`llama-3.1-70b-versatile`)
- `langchain_pipeline/prompts.py` — intent, slot extraction, and response generation templates
- `langchain_pipeline/memory.py` — `ConversationBufferMemory` per `session_id` (in-memory dict)
- `langchain_pipeline/intent_chain.py` — intent classification chain
- `langchain_pipeline/slot_extraction.py` — slot extraction chain
- `langchain_pipeline/response_chain.py` — natural language response generation
- `langchain_pipeline/test_pipeline.py` — standalone test script with sample utterances

### Stage 4 — `/chat` Endpoint

- `POST /chat` — accepts `{ patient_id, session_id, message }`
- Flow: memory → intent → slots → appointment service → NL reply
- `app/services/chat_service.py` — orchestrates pipeline + business logic
- `app/utils/date_resolver.py` — resolves "Friday", "tomorrow" to real dates
- `app/utils/doctor_lookup.py` — fuzzy doctor/department matching + suggestions
- Returns `{ reply, structured_data, intent }` for frontend booking cards

### Stage 5 — React Frontend

- `LoginGate.jsx` — name + email/phone form, stores `patient_id` in localStorage
- `ChatWindow.jsx` — message list, input, calls `/chat`, UUID `session_id` per visit
- `MessageBubble.jsx` — patient and bot message bubbles
- `BookingSummaryCard.jsx` — renders booking/slots/cancel/reschedule cards from `structured_data`

### Stage 6 & 7 — Dashboard, Landing Page, and Auth Separator

- **Auth Separator**: Separated authentication into distinct login (validates credentials exist) and registration (prevents account conflicts) screens.
- **Landing Page (`LandingPage.jsx`)**: Added homepage highlighting key features, public doctors directory with department filtering, inquiry feedback form, and authentication tab selections.
- **Dashboard (`Dashboard.jsx`)**: Designed main medical control panel displaying stats, active upcoming appointments table with dynamic cancel capabilities, doctor directory, and an interactive slot availability checker.
- **Floating AI Chatbot Widget (`ChatWindow.jsx` + Floating CSS)**: Renders the chatbot as a collapsible popover balloon in the bottom-right corner of the dashboard. Seamlessly triggers dynamic background updates on the dashboard table whenever appointments are scheduled, rescheduled, or cancelled via conversational commands.


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
│   ├── langchain_pipeline/  # LangChain + Groq pipeline (Stage 3)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # LandingPage, Dashboard, ChatWindow, MessageBubble, BookingSummaryCard, LoginGate
│   │   ├── api/client.js    # API calls to backend
│   │   ├── App.jsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── .env.example
└── .gitignore
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
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

### Frontend

```powershell
cd frontend

# Install dependencies (first time only)
npm install

# Copy environment file
copy .env.example .env

# Start dev server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) — the backend must be running on port 8000.

### Run smoke tests

With the server running in another terminal:

```powershell
python test_stage2.py
```

### Test LangChain pipeline (Stage 3)

```powershell
# Add your Groq API key first
copy .env.example .env
# Edit .env and set GROQ_API_KEY=...

python -m langchain_pipeline.test_pipeline
```

### Test /chat endpoint (Stage 4)

```powershell
# Server must be running
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# In another terminal
python test_stage4.py
```

Or via PowerShell:

```powershell
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/chat `
  -ContentType "application/json" `
  -Body '{"patient_id":1,"session_id":"demo-1","message":"I want to see a cardiologist this Friday afternoon"}'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/auth/identify` | Legacy identify patient `{ name, email_or_phone }` |
| `POST` | `/auth/login` | Log in patient `{ email_or_phone }` |
| `POST` | `/auth/register` | Register new patient `{ name, email_or_phone }` |
| `GET` | `/appointments/doctors` | Get all doctors list with department names and available schedules |
| `GET` | `/appointments/departments` | Get all departments list |
| `GET` | `/appointments/patient/{patient_id}` | Get active booked appointments list for a patient |
| `GET` | `/appointments/slots?doctor_id=&date=` | Available slots for a doctor |
| `GET` | `/appointments/slots?department_id=&date=` | Available slots for a department |
| `POST` | `/appointments` | Book appointment |
| `GET` | `/appointments/{id}` | Get appointment |
| `PATCH` | `/appointments/{id}` | Reschedule appointment |
| `DELETE` | `/appointments/{id}` | Cancel appointment |
| `POST` | `/chat` | Conversational booking (Stage 4) |


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
