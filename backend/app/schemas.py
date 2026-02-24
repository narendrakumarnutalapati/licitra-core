from typing import Any, Dict
from pydantic import BaseModel, Field

class EventIn(BaseModel):
    org_id: str = Field(..., description="Organization identifier")
    event_id: str = Field(..., description="Client-supplied unique event id")
    payload: Dict[str, Any] = Field(default_factory=dict)

class EventOut(BaseModel):
    org_id: str
    event_id: str
    prev_hash: str
    current_hash: str
