from typing import Any, Dict
from datetime import datetime, timezone

def build_evidence_bundle(org_id: str, verify_report: Dict[str, Any], decision: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "org_id": org_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verify_report": verify_report,
        "decision": decision,
        "format_version": "0.1"
    }
