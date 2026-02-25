import io
import json
import hashlib
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def evidence_pdf_bytes(evidence: dict, max_events: int = 10) -> bytes:
    # Stable JSON for checksum
    j = json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode("utf-8")
    checksum = hashlib.sha256(j).hexdigest()

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    y = height - 50
    def line(txt, dy=14):
        nonlocal y
        c.drawString(50, y, txt)
        y -= dy
        if y < 60:
            c.showPage()
            y = height - 50

    org_id = evidence.get("org_id")
    ts = evidence.get("timestamp")
    vr = evidence.get("verify_report", {})
    events = evidence.get("events", [])
    decision = evidence.get("decision")

    line("LICITRA Evidence Report (format_version=%s)" % evidence.get("format_version", "unknown"), 18)
    line(f"org_id: {org_id}")
    line(f"timestamp: {ts}")
    line(f"verify.ok: {vr.get('ok')}")
    line(f"verify.count: {vr.get('count')}")
    if vr.get("ok") is False:
        line(f"verify.reason: {vr.get('reason')}")
        line(f"verify.bad_index: {vr.get('bad_index')}")
    line("")

    # Hash summary
    line("SHA256(JSON evidence bundle):")
    line(checksum, 18)
    line("")

        # Head/tail hashes + link proof
    if events:
        first = events[0]
        last = events[-1]

        line("Chain summary:", 18)
        line(f"events.count: {len(events)}")
        line(f"first.event_id: {first.get('event_id')}")
        line(f"  first.prev_hash: {first.get('prev_hash')}")
        line(f"  first.current_hash: {first.get('current_hash')}")
        line(f"last.event_id: {last.get('event_id')}")
        line(f"  last.prev_hash: {last.get('prev_hash')}")
        line(f"  last.current_hash: {last.get('current_hash')}")
        line("")

        # Link proof on the tail (strongest human-readable proof)
        n = min(max_events, len(events))
        tail = events[-n:]
        line(f"Chain link proof (tail {n} events):", 18)

        prev_cur = None
        for i, ev in enumerate(tail):
            eid = ev.get("event_id")
            prev_h = ev.get("prev_hash")
            cur_h = ev.get("current_hash")

            # expected linkage: prev_hash == previous event's current_hash
            ok_link = True
            if prev_cur is not None and prev_h != prev_cur:
                ok_link = False

            prev_short = (prev_h or "")[:16]
            cur_short = (cur_h or "")[:16]
            status = "OK" if ok_link else "BROKEN"

            line(f"- {eid}: prev={prev_short}… cur={cur_short}… link={status}")
            prev_cur = cur_h

        line("")

    # Decision
    line("Decision (rollback v0):", 18)
    line(json.dumps(decision, ensure_ascii=False) if decision else "null", 14)

    c.showPage()
    c.save()
    return buf.getvalue()