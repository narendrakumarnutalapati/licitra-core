from fastapi import FastAPI, HTTPException
from .schemas import EventIn, EventOut
from .ledger import InMemoryLedger
from .rollback import rollback_v0

app = FastAPI(title="LICITRA Core MVP", version="0.1.0")

ledger = InMemoryLedger()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/events", response_model=EventOut)
def ingest_event(e: EventIn):
    ev = ledger.append(e.org_id, e.event_id, e.payload)
    return EventOut(org_id=ev.org_id, event_id=ev.event_id, prev_hash=ev.prev_hash, current_hash=ev.current_hash)

@app.get("/verify/{org_id}")
def verify_chain(org_id: str):
    return ledger.verify(org_id)

@app.post("/tamper/{org_id}/{event_id}")
def tamper(org_id: str, event_id: str):
    ok = ledger.tamper_payload(org_id, event_id, {"tampered": True})
    if not ok:
        raise HTTPException(status_code=404, detail="event not found")
    return {"ok": True}

@app.post("/circuit-break/{org_id}")
def circuit_break(org_id: str):
    report = ledger.verify(org_id)
    if report.get("ok") is True:
        return {"org_id": org_id, "action": "NOOP", "reason": "chain_ok"}

    # MVP policy: if chain is not ok, emit rollback decision to last known good anchor.
    # For MVP we approximate last_verified_hash as GENESIS when verification fails.
    decision = rollback_v0(org_id=org_id, reason=report.get("reason", "unknown"), last_verified_hash="GENESIS")
    return {"org_id": org_id, "verify": report, "decision": decision}

@app.post("/dev/reset/{org_id}")
def dev_reset(org_id: str):
    ledger._by_org[org_id] = []
    return {"ok": True, "org_id": org_id}


from .evidence import build_evidence_bundle

@app.get("/evidence/{org_id}")
def evidence(org_id: str):
    report = ledger.verify(org_id)
    decision = None
    if not report.get("ok", False):
        decision = rollback_v0(org_id=org_id, reason=report.get("reason", "unknown"), last_verified_hash="GENESIS")
    return build_evidence_bundle(org_id, report, decision)

