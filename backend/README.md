# KisanSetu Backend (Krishka Vachana - SIH26032)

Backend API for the project, owned by the Backend role (see
`team_work_division.md` at the repo root). Built with **FastAPI + Python**,
per the repo's `technology_stack.md` (the tech stack in the initial project
PPT is out of date - this repo's own docs are the source of truth).

## Scope of this package

This directory contains **backend only**. It does not touch:
- `frontend/` (Next.js + React + TypeScript) - Frontend role
- Firebase project config, Firestore schema/security rules, CI/CD - Database
  & Infrastructure role
- ML models - AI/ML role (this backend exposes a placeholder integration
  point for their predictions once ready; see roadmap below)

## Current status: Phase 1 of 4 (~25%)

Implemented so far - the first stage of the product flow
(`Farmer -> Smart Slot -> ...`):

- Project scaffold (FastAPI app, settings, error handling)
- Auth dependency that verifies Firebase ID tokens (falls back to a
  dev-only mode when Firebase credentials aren't available yet, so backend
  work isn't blocked on Infra's Firebase setup)
- Repository abstraction (`app/repositories/`) with an in-memory
  implementation for local dev/tests and a Firestore implementation ready
  to wire in once the Infra teammate confirms collection names/schema
- **Farmer ID / Aadhaar-linked identification**: registration + profile
  endpoints. Full Aadhaar numbers are validated on input but never stored
  or returned in plaintext - only a hash and the last 4 digits.
- **Crop and quantity registration**: endpoints to register a crop +
  quantity against a farmer and list a farmer's registered crops.
- Test suite (18 tests) covering the above.

### Roadmap (remaining phases, future PRs)

| Phase | Scope |
|---|---|
| 2 | Procurement-centre listing, Smart Slot booking, congestion-prediction integration point (consumes AI/ML's endpoint) |
| 3 | Dynamic Queue system (position, printable token generation), SMS/OTP integration |
| 4 | Payment tracking, Historical farm record, Village Cluster Booking, polish |

## API surface (Phase 1)

All endpoints are versioned under `/api/v1` and (except `/health`) require
`Authorization: Bearer <firebase-id-token>`.

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | Liveness check |
| POST | `/api/v1/farmers/register` | Register the authenticated farmer's profile |
| GET | `/api/v1/farmers/me` | Get the authenticated farmer's profile |
| PATCH | `/api/v1/farmers/me` | Update the authenticated farmer's profile |
| POST | `/api/v1/crops` | Register a crop + quantity for the authenticated farmer |
| GET | `/api/v1/crops/me` | List the authenticated farmer's registered crops |

Interactive docs are available at `/docs` (Swagger UI) once the server is
running.

## Local setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Without Firebase credentials configured, the API automatically falls back
to an in-memory store and a dev-only auth mode (any non-empty Bearer token
is accepted as the farmer's uid) so you can develop and test without
waiting on the Firebase project. Set `FIREBASE_SERVICE_ACCOUNT_PATH` (or
`FIREBASE_EMULATOR_HOST`) in `.env` once real credentials/emulator are
available - no code changes needed, the switch is automatic
(`app/api/deps.py`).

## Running tests

```bash
pip install -r requirements.txt
pytest -q
```

18/18 tests currently pass, covering registration validation (including
Aadhaar/phone format checks and duplicate-registration handling), profile
updates, crop registration, and the auth dependency's fallback behavior.

## Design notes for teammates

- **Frontend**: request/response shapes are the `FarmerCreate`/`FarmerOut`
  and `CropRegistrationCreate`/`CropOut` models in `app/schemas/`. Errors
  come back as `{"error": {"code": "...", "message": "..."}}` with an
  appropriate HTTP status, matching the error-state pattern in
  `UI_rules.md` section 22.
- **Database & Infrastructure**: `app/repositories/firestore.py` is a
  placeholder using `farmers`/`crops` as collection names and flat
  documents matching the schemas above - please review against whatever
  schema/security rules you set up and flag any mismatch.
- **AI/ML**: congestion prediction and alternative-centre recommendation
  will be called from a Phase 2 backend endpoint that wraps your model's
  API - not called directly by the frontend, per `team_work_division.md`.
