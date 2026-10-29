from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AuditEventItem(BaseModel):
    id: str
    event_type: str
    actor: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    action_details: str
    previous_hash: str
    current_hash: str
    timestamp: datetime
    success: bool
    is_hash_valid: Optional[bool] = None

class AuditIntegrityReport(BaseModel):
    is_ledger_intact: bool
    total_events: int
    first_tampered_index: Optional[int] = None
    verification_details: str
    verified_at: str

