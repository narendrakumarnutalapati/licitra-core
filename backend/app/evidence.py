from datetime import datetime, timezone

def build_evidence_bundle(org_id: str, verify_report: dict, events: list, decision: dict | None):
    return {
        "org_id": org_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verify_report": verify_report,
        "events": events,
        "decision": decision,
        "format_version": "0.2",
    }