from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CaseCreate(BaseModel):
    title: str
    primary_account_id: str
    priority: str = "HIGH"  # LOW, MEDIUM, HIGH, URGENT
    assigned_to: str = "Lead Financial Investigator"
    findings_summary: Optional[str] = None

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None  # NEW, IN_REVIEW, ESCALATED, FROZEN, CLOSED
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    findings_summary: Optional[str] = None
    status_change_reason: Optional[str] = None

class CaseNoteCreate(BaseModel):
    author: str = "Investigator"
    note_text: str

class CaseNoteItem(BaseModel):
    id: str
    case_id: str
    author: str
    note_text: str
    created_at: datetime

class CaseStatusEventItem(BaseModel):
    id: str
    case_id: str
    old_status: str
    new_status: str
    changed_by: str
    reason: Optional[str]
    created_at: datetime

class CaseDetail(BaseModel):
    id: str
    case_number: str
    title: str
    status: str
    priority: str
    primary_account_id: str
    primary_account_number: Optional[str] = None
    primary_holder_name: Optional[str] = None
    primary_bank_name: Optional[str] = None
    assigned_to: str
    findings_summary: Optional[str]
    risk_score: float = 0.0
    risk_tier: str = "MEDIUM"
    created_at: datetime
    updated_at: datetime
    notes: List[CaseNoteItem] = []
    status_events: List[CaseStatusEventItem] = []
    artifacts: List[Dict[str, Any]] = []

class EvidenceExportResponse(BaseModel):
    case_id: str
    case_number: str
    artifact_id: str
    artifact_type: str
    file_path: str
    content_hash: str
    dossier_summary: Dict[str, Any]
    download_url: str

