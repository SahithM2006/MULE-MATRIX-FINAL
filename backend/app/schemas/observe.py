from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SentinelSummary(BaseModel):
    total_accounts: int
    total_transactions: int
    total_institutions: int
    active_alerts_count: int
    critical_alerts_count: int
    high_risk_accounts_count: int
    total_volume_inr: float
    recent_alerts: List[Dict[str, Any]]
    active_scenarios: List[Dict[str, Any]]

class TransactionFilter(BaseModel):
    account_id: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    channel: Optional[str] = None
    status: Optional[str] = None
    has_lineage: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    scenario_id: Optional[str] = None
    limit: int = 100
    offset: int = 0

class TransactionItem(BaseModel):
    id: str
    tx_hash: str
    scenario_id: Optional[str]
    source_account_id: str
    source_account_number: Optional[str] = None
    source_holder: Optional[str] = None
    source_bank: Optional[str] = None
    dest_account_id: str
    dest_account_number: Optional[str] = None
    dest_holder: Optional[str] = None
    dest_bank: Optional[str] = None
    amount: float
    currency: str
    timestamp: datetime
    status: str
    channel: str
    description: Optional[str]
    has_token_lineage: bool
    risk_flag: Optional[str] = None

class AlertItem(BaseModel):
    id: str
    account_id: str
    account_number: str
    holder_name: str
    bank_name: str
    transaction_id: Optional[str]
    severity: str
    alert_type: str
    title: str
    description: str
    status: str
    created_at: datetime

