from typing import Dict, Any

def rollback_v0(org_id: str, reason: str, last_verified_hash: str) -> Dict[str, Any]:
    """
    Rollback v0 (MVP):
    - In production, this would restore agent state/memory to the last verified anchor.
    - For MVP, we emit a verifiable rollback decision record.
    """
    return {
        "org_id": org_id,
        "action": "ROLLBACK_V0",
        "reason": reason,
        "restore_to_hash": last_verified_hash,
    }
