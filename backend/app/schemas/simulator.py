from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AuditEventItem(BaseModel):
    id: str
    event_type: str
    actor: str
    target_type: Optional[str]
    target_id: Optional[str]
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
    verified_at: datetime

class ScenarioGenerateRequest(BaseModel):
    scenario_type: str = Field(
        default="RAPID_PASSTHROUGH",
        description="RAPID_PASSTHROUGH, SMURFING_FANIN, LAYERING_CHAIN, MULE_RING, CROSS_BANK_SPLIT_MERGE, MERCHANT_LOOKALIKE, PAYROLL_LOOKALIKE"
    )
    seed: int = Field(default=42)
    accounts_count: int = Field(default=20, ge=4, le=500)
    name_prefix: Optional[str] = None

class ScenarioInfo(BaseModel):
    id: str
    name: str
    scenario_type: str
    description: str
    seed: int
    created_at: datetime
    transactions_count: int
    accounts_count: int

