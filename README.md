# LICITRA (Core)

Cryptographically Verifiable Runtime Integrity for Agentic AI Systems.

LICITRA provides tamper-evident runtime audit trails for autonomous AI agents using
hash-chained semantic events, PostgreSQL persistence, and forensic evidence exports.

This repository contains the core FastAPI backend and SDK primitives.

Evidence bundles and reproducible experiments live in the companion repository:

👉 https://github.com/narendrakumarnutalapati/licitra-evidence

---

## Architecture

![Architecture](architecture/overview.png)

---

## Key Capabilities

- Deterministic canonical JSON hashing
- Per-organization hash-chained event ledger (SHA-256)
- PostgreSQL persistence
- Verification endpoint (`/verify/{org_id}`)
- Evidence bundle export (`/evidence/{org_id}`)
- PDF governance reports (`/evidence/{org_id}/pdf`)
- Multi-organization isolation
- Dev-only tamper/reset endpoints gated by `DEV_MODE`
- Rollback v0 decision primitive

---

## Repo Layout

- `backend/` — FastAPI service + database models
- `sdk/` — minimal client SDK
- `test-vectors/` — deterministic hashing test vectors
- `architecture/` — diagrams and design notes
- `.env.example` — environment template

---

## Quickstart (Local)

### Requirements

- Python 3.12+
- PostgreSQL 16
- Windows PowerShell (or Bash)
- Git

---

### Setup

```powershell
git clone https://github.com/narendrakumarnutalapati/licitra-core.git
cd licitra-core

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r backend/requirements.txt
```

Set environment variables:

```powershell
$env:DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/licitra"
$env:DEV_MODE="1"
```

Run server:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Server runs at:

http://127.0.0.1:8000

---

## Core Endpoints

### Runtime

- `POST /events`
- `GET /verify/{org_id}`
- `GET /evidence/{org_id}`
- `GET /evidence/{org_id}/pdf`

### DEV ONLY (requires `DEV_MODE=1`)

- `POST /dev/reset/{org_id}`
- `POST /tamper/{org_id}/{event_id}`
- `POST /tamper-prev/{org_id}/{event_id}`
- `POST /dev/delete/{org_id}/{event_id}`

---

## What This MVP Is

LICITRA focuses strictly on cryptographic runtime integrity primitives:

- Immutable semantic event capture
- Deterministic verification
- Tamper detection
- Evidence export

It intentionally does NOT include:

- UI dashboards
- Authentication
- Policy enforcement
- Compliance workflows

LICITRA is a technical primitive, not a governance platform.

---

## Evidence & Experiments

Reproducible experiments, tampering scenarios, and exported JSON/PDF evidence bundles:

👉 https://github.com/narendrakumarnutalapati/licitra-evidence

---

## License

MIT
