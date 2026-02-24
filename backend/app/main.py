import os
from fastapi import FastAPI, HTTPException, Depends
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


load_dotenv()

from .schemas import EventIn, EventOut
from .rollback import rollback_v0
from .evidence import build_evidence_bundle

from .db import engine, SessionLocal
from .models import LedgerEventModel
from .db import Base
from .ledger_db import PostgresLedger

def require_dev_mode():
    if os.getenv("DEV_MODE") != "1":
        raise HTTPException(status_code=404, detail="not found")

app = FastAPI(title="LICITRA Core MVP (Postgres)", version="0.2.0")

# Create tables (MVP). Later switch to Alembic migrations.
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/events", response_model=EventOut)
def ingest_event(e: EventIn, db: Session = Depends(get_db)):
    ledger = PostgresLedger(db)
    try:
        out = ledger.append(e.org_id, e.event_id, e.payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="duplicate event_id for org")
    return EventOut(**out)

@app.get("/verify/{org_id}")
def verify_chain(org_id: str, db: Session = Depends(get_db)):
    ledger = PostgresLedger(db)
    return ledger.verify(org_id)

@app.post("/dev/reset/{org_id}")
def dev_reset(org_id: str, db: Session = Depends(get_db)):
    require_dev_mode()
    ledger = PostgresLedger(db)
    ledger.dev_reset(org_id)
    return {"ok": True, "org_id": org_id}

@app.post("/circuit-break/{org_id}")
def circuit_break(org_id: str, db: Session = Depends(get_db)):
    ledger = PostgresLedger(db)
    report = ledger.verify(org_id)
    if report.get("ok") is True:
        return {"org_id": org_id, "action": "NOOP", "reason": "chain_ok"}

    decision = rollback_v0(org_id=org_id, reason=report.get("reason", "unknown"), last_verified_hash="GENESIS")
    return {"org_id": org_id, "verify": report, "decision": decision}

@app.get("/evidence/{org_id}")
def evidence(org_id: str, db: Session = Depends(get_db)):
    ledger = PostgresLedger(db)
    report = ledger.verify(org_id)
    events = ledger.export_events(org_id)

    decision = None
    if not report.get("ok", False):
        decision = rollback_v0(
            org_id=org_id,
            reason=report.get("reason", "unknown"),
            last_verified_hash="GENESIS",
        )

    return build_evidence_bundle(org_id, report, events, decision)

@app.get("/export/{org_id}")
def export(org_id: str, db: Session = Depends(get_db)):
    ledger = PostgresLedger(db)
    report = ledger.verify(org_id)
    events = ledger.export_events(org_id)
    return {
        "org_id": org_id,
        "verify_report": report,
        "events": events,
        "format_version": "0.1"
    }

@app.post("/tamper/{org_id}/{event_id}")
def tamper(org_id: str, event_id: str, db: Session = Depends(get_db)):
    require_dev_mode()
    ledger = PostgresLedger(db)
    ok = ledger.dev_tamper_payload(org_id, event_id, {"tampered": True})
    if not ok:
        raise HTTPException(status_code=404, detail="event not found")
    return {"ok": True}

@app.post("/tamper-prev/{org_id}/{event_id}")
def tamper_prev(org_id: str, event_id: str, db: Session = Depends(get_db)):
    require_dev_mode()
    ledger = PostgresLedger(db)
    ok = ledger.dev_tamper_prev_hash(org_id, event_id, "BADPREV")
    if not ok:
        raise HTTPException(status_code=404, detail="event not found")
    return {"ok": True}

@app.post("/dev/delete/{org_id}/{event_id}")
def dev_delete(org_id: str, event_id: str, db: Session = Depends(get_db)):
    require_dev_mode()
    ledger = PostgresLedger(db)
    ok = ledger.dev_delete_event(org_id, event_id)
    if not ok:
        raise HTTPException(status_code=404, detail="event not found")
    return {"ok": True}