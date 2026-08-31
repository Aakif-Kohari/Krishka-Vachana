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
(`Farmer -> Smart Slot -> ...`), built to be deployable as-is rather than a
throwaway prototype:

- Project scaffold (FastAPI app, settings, error handling)
- Auth dependency that verifies Firebase ID tokens (an explicitly enabled
  dev-only fallback keeps local work unblocked before Firebase is available)
- Repository abstraction (`app/repositories/`) with an in-memory
  implementation for local dev/tests and a Firestore implementation ready
  to wire in once the Infra teammate confirms collection names/schema
- **Farmer ID / Aadhaar-linked identification**: registration + profile
  endpoints. Full Aadhaar numbers are validated on input but never stored
  or returned in plaintext - only a keyed fingerprint and the last 4 digits.
- **Crop and quantity registration**: endpoints to register a crop +
  quantity against a farmer and list a farmer's registered crops.
- **Production/deployment readiness**:
  - Liveness (`/api/v1/health`) and readiness (`/api/v1/health/ready`)
    endpoints, matching the standard container-platform health-check split
  - Custom-branded interactive docs at `/docs`, ReDoc at `/redoc`, and a
    human-friendly `/status` page - all can be fully disabled in
    production via `ENABLE_DOCS=false` (verified: returns 404 while
    `/api/v1/health` keeps working)
  - `Dockerfile` (non-root user, `HEALTHCHECK`, gunicorn + uvicorn
    workers) and a `Procfile` for platforms that use one instead
  - Config fully via environment variables (`.env.example`), no
    hardcoded secrets
- Test suite (35 tests) covering all of the above.

### Roadmap (remaining phases, future PRs)

| Phase | Scope |
|---|---|
| 2 | Procurement-centre listing, Smart Slot booking, congestion-prediction integration point (consumes AI/ML's endpoint) |
| 3 | Dynamic Queue system (position, printable token generation), SMS/OTP integration |
| 4 | Payment tracking, Historical farm record, Village Cluster Booking, polish |

## API surface (Phase 1)

All endpoints are versioned under `/api/v1` and (except health) require
`Authorization: Bearer <firebase-id-token>`.

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | Liveness check (always 200 while the process is up) |
| GET | `/api/v1/health/ready` | Readiness check (verifies Firestore connectivity when configured; 503 if degraded) |
| POST | `/api/v1/farmers/register` | Register the authenticated farmer's profile |
| GET | `/api/v1/farmers/me` | Get the authenticated farmer's profile |
| PATCH | `/api/v1/farmers/me` | Update the authenticated farmer's profile |
| POST | `/api/v1/crops` | Register a crop + quantity for the authenticated farmer |
| GET | `/api/v1/crops/me` | List the authenticated farmer's registered crops |

Human-facing pages (disable in prod with `ENABLE_DOCS=false` if you don't
want them public):

| Path | What it is |
|---|---|
| `/docs` | Custom-branded Swagger UI |
| `/redoc` | ReDoc API reference |
| `/status` | Plain-English status page (version, environment, Firebase connectivity, links) |

## Local setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

For local development without Firebase credentials, explicitly set
`ALLOW_DEV_AUTH_FALLBACK=true` to use the in-memory store and dev-only auth
mode (any non-empty Bearer token is accepted as the farmer's uid). Set
`FIREBASE_SERVICE_ACCOUNT_PATH` (or `FIREBASE_EMULATOR_HOST`) once real
credentials or an emulator are available. Farmer registration also requires
a stable, 32-byte-or-longer key in Google Secret Manager; configure its full
version resource as `AADHAAR_HMAC_SECRET_NAME`.

## Running tests

```bash
pip install -r requirements.txt
pytest -q
```

35/35 tests currently pass, covering registration validation (including
Aadhaar/phone format checks and duplicate-registration handling), profile
updates, crop registration, the auth dependency's fallback behavior, and
the health/docs/status pages.

## Deploying

### Docker (any container host: Cloud Run, Fly.io, Render, ECS, etc.)

```bash
docker build -t kisansetu-backend .
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e ENABLE_DOCS=false \
  -e FIREBASE_SERVICE_ACCOUNT_PATH=/secrets/firebase.json \
  -v /path/to/firebase-service-account.json:/secrets/firebase.json:ro \
  kisansetu-backend
```

The image runs as a non-root user, serves via gunicorn with uvicorn
workers (`Dockerfile` `CMD`), and has a built-in `HEALTHCHECK` against
`/api/v1/health`.

### Platforms that use a Procfile instead (Railway, Heroku-style)

The included `Procfile` runs the same gunicorn command; just set the same
environment variables in the platform's dashboard.

### Vercel

The repo's `technology_stack.md` lists Vercel + Firebase for deployment.
Vercel's Python support targets serverless functions rather than a long-
running ASGI process - wiring that up (e.g. via an ASGI adapter and
`vercel.json`) is an infra/deployment decision I've left for the Database
& Infrastructure teammate to confirm, since they own the deployment
pipeline per `team_work_division.md`. The Docker/Procfile paths above work
on any container-based host in the meantime.

## Design notes for teammates

- **Frontend**: request/response shapes are the `FarmerCreate`/`FarmerOut`
  and `CropRegistrationCreate`/`CropOut` models in `app/schemas/`. Errors
  come back as `{"error": {"code": "...", "message": "..."}}` with an
  appropriate HTTP status, matching the error-state pattern in
  `UI_rules.md` section 22.
- **Database & Infrastructure**: `app/repositories/firestore.py` is a
  placeholder using `farmers`/`crops` as collection names and flat
  documents matching the schemas above - please review against whatever
  schema/security rules you set up and flag any mismatch. Also see the
  Vercel note above re: final deployment target.
- **AI/ML**: congestion prediction and alternative-centre recommendation
  will be called from a Phase 2 backend endpoint that wraps your model's
  API - not called directly by the frontend, per `team_work_division.md`.
