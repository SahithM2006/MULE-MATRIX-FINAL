from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EngineSignal(BaseModel):
    engine_id: str
    engine_name: str
    status: str  # ACTIVE, NOT_TRAINED, UNAVAILABLE, BENIGN, SUSPICIOUS
    score: float = 0.0  # Normalized 0.0 - 100.0
    weight: float = 0.0
    weighted_contribution: float = 0.0
    summary: str
    details: Dict[str, Any] = {}

class AccountRiskProfile(BaseModel):
    account_id: str
    account_number: str
    holder_name: str
    bank_name: str
    bank_swift: str
    account_type: str
    balance: float
    composite_risk_score: float  # 0 to 100
    risk_tier: str               # LOW, MEDIUM, HIGH, CRITICAL
    active_signals_count: int
    narrative_explanation: str
    signals: List[EngineSignal]
    feature_metrics: Dict[str, Any]
    rule_evidences: List[Dict[str, Any]] = []

class BenchmarkReport(BaseModel):
    evaluation_run_id: str
    evaluated_at: datetime
    test_seed: int
    test_accounts_count: int
    rule_baseline: Dict[str, Any]
    candidate_detector: Dict[str, Any]
    isolation_forest_status: str
    graphsage_status: str
    comparison_summary: str

