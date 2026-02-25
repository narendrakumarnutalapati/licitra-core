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

    # Head/tail hashes
    if events:
        first = events[0]
        last = events[-1]
        line("Chain summary:")
        line(f"first.event_id: {first.get('event_id')} prev={first.get('prev_hash')} cur={first.get('current_hash')}")
        line(f"last.event_id: {last.get('event_id')} prev={last.get('prev_hash')} cur={last.get('current_hash')}")
        line("")

        # Last N events table-ish
        line(f"Last {min(max_events, len(events))} events (event_id, current_hash prefix):", 18)
        for ev in events[-max_events:]:
            ch = (ev.get("current_hash") or "")[:16]
            line(f"- {ev.get('event_id')}  {ch}…")
        line("")

    # Decision
    line("Decision (rollback v0):", 18)
    line(json.dumps(decision, ensure_ascii=False) if decision else "null", 14)

    c.showPage()
    c.save()
    return buf.getvalue()