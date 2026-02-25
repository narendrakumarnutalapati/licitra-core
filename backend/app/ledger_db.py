from typing import Any, Dict, Optional
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from .ledger import GENESIS_HASH, compute_event_hash
from .canonical_json import canonicalize
from .models import LedgerEventModel

class PostgresLedger:
    def __init__(self, db: Session) -> None:
        self.db = db

    def last_hash(self, org_id: str) -> str:
        q = (
            select(LedgerEventModel.current_hash)
            .where(LedgerEventModel.org_id == org_id)
            .order_by(LedgerEventModel.id.desc())
            .limit(1)
        )
        row = self.db.execute(q).scalar_one_or_none()
        return row if row else GENESIS_HASH

    def append(self, org_id: str, event_id: str, payload: Dict[str, Any]) -> Dict[str, str]:
        prev = self.last_hash(org_id)

        payload_cjson = canonicalize(payload)

        record = {
            "org_id": org_id,
            "event_id": event_id,
            "prev_hash": prev,
            "payload": payload,
        }
        cur = compute_event_hash(record)

        ev = LedgerEventModel(
            org_id=org_id,
            event_id=event_id,
            prev_hash=prev,
            current_hash=cur,
            payload_cjson=payload_cjson,
        )
        self.db.add(ev)
        self.db.commit()

        return {"org_id": org_id, "event_id": event_id, "prev_hash": prev, "current_hash": cur}

    def verify(self, org_id: str) -> Dict[str, Any]:
        q = (
            select(LedgerEventModel)
            .where(LedgerEventModel.org_id == org_id)
            .order_by(LedgerEventModel.id.asc())
        )
        events = list(self.db.execute(q).scalars().all())
        if not events:
            return {"org_id": org_id, "ok": True, "count": 0, "message": "no events"}

        prev = GENESIS_HASH
        for idx, ev in enumerate(events):
            if ev.prev_hash != prev:
                return {"org_id": org_id, "ok": False, "count": len(events), "bad_index": idx, "reason": "prev_hash_mismatch"}

            # rebuild expected hash using original payload (parsed from canonical JSON)
            # NOTE: canonical JSON ensures stable encoding. We store canonical string; for hashing we need dict.
            # For MVP we parse back via json. (If you want, we can store both canonical string + original dict.)
            import json
            payload = json.loads(ev.payload_cjson)

            record = {
                "org_id": ev.org_id,
                "event_id": ev.event_id,
                "prev_hash": ev.prev_hash,
                "payload": payload,
            }
            expected = compute_event_hash(record)
            if ev.current_hash != expected:
                return {"org_id": org_id, "ok": False, "count": len(events), "bad_index": idx, "reason": "hash_mismatch"}

            prev = ev.current_hash

        return {"org_id": org_id, "ok": True, "count": len(events)}

    def dev_reset(self, org_id: str) -> None:
        self.db.execute(delete(LedgerEventModel).where(LedgerEventModel.org_id == org_id))
        self.db.commit()
    
    def dev_tamper_payload(self, org_id: str, event_id: str, new_payload: Dict[str, Any]) -> bool:
        from sqlalchemy import update
        payload_cjson = canonicalize(new_payload)
        q = (
            update(LedgerEventModel)
            .where(LedgerEventModel.org_id == org_id, LedgerEventModel.event_id == event_id)
            .values(payload_cjson=payload_cjson)
        )
        res = self.db.execute(q)
        self.db.commit()
        return res.rowcount > 0
    
    def export_events(self, org_id: str) -> list[dict]:
        from sqlalchemy import select
        q = (
            select(LedgerEventModel)
            .where(LedgerEventModel.org_id == org_id)
            .order_by(LedgerEventModel.id.asc())
        )
        rows = list(self.db.execute(q).scalars().all())
        out = []
        for ev in rows:
            out.append({
                "org_id": ev.org_id,
                "event_id": ev.event_id,
                "prev_hash": ev.prev_hash,
                "current_hash": ev.current_hash,
                "payload_cjson": ev.payload_cjson,
                "created_at": str(ev.created_at),
            })
        return out
    
    def dev_tamper_prev_hash(self, org_id: str, event_id: str, new_prev_hash: str) -> bool:
        from sqlalchemy import update
        q = (
            update(LedgerEventModel)
            .where(LedgerEventModel.org_id == org_id, LedgerEventModel.event_id == event_id)
            .values(prev_hash=new_prev_hash)
        )
        res = self.db.execute(q)
        self.db.commit()
        return res.rowcount > 0

    def dev_delete_event(self, org_id: str, event_id: str) -> bool:
        from sqlalchemy import delete
        q = delete(LedgerEventModel).where(
            LedgerEventModel.org_id == org_id,
            LedgerEventModel.event_id == event_id,
        )
        res = self.db.execute(q)
        self.db.commit()
        return res.rowcount > 0