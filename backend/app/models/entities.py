from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class SyntheticInstitution(Base):
    __tablename__ = "synthetic_institutions"
    
    id = Column(String(64), primary_key=True)
    routing_code = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    swift_bic = Column(String(32), nullable=False)
    risk_tier = Column(String(16), default="STANDARD")  # STANDARD, ELEVATED, HIGH_RISK
    country = Column(String(8), default="IN")
    created_at = Column(DateTime, default=utc_now)
    
    accounts = relationship("Account", back_populates="institution")

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(String(64), primary_key=True)
    institution_id = Column(String(64), ForeignKey("synthetic_institutions.id"), nullable=False, index=True)
    account_number = Column(String(64), unique=True, nullable=False, index=True)
    account_type = Column(String(32), default="CHECKING")  # CHECKING, SAVINGS, DIGITAL_WALLET, MERCHANT, CORPORATE, CRYPTO_OFFRAMP
    holder_name = Column(String(128), nullable=False)
    balance = Column(Float, default=0.0)
    status = Column(String(16), default="ACTIVE")  # ACTIVE, SUSPENDED, FROZEN, CLOSED
    created_at = Column(DateTime, default=utc_now)
    
    # Ground truth for held-out evaluation only (MUST NOT be accessed by runtime detection models)
    is_mule = Column(Boolean, default=False)
    mule_role = Column(String(32), default="LEGITIMATE")  # LEGITIMATE, ORIGIN, SMURF, LAYER, BRIDGE, CASHOUT
    
    institution = relationship("SyntheticInstitution", back_populates="accounts")
    outgoing_transactions = relationship("Transaction", foreign_keys="Transaction.source_account_id", back_populates="source_account")
    incoming_transactions = relationship("Transaction", foreign_keys="Transaction.dest_account_id", back_populates="dest_account")
    feature_snapshots = relationship("FeatureSnapshot", back_populates="account")
    detection_results = relationship("DetectionResult", back_populates="account")
    alerts = relationship("Alert", back_populates="account")
    cases = relationship("IncidentCase", back_populates="primary_account")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String(64), primary_key=True)
    tx_hash = Column(String(128), unique=True, nullable=False, index=True)
    scenario_id = Column(String(64), ForeignKey("scenario_definitions.id"), nullable=True, index=True)
    source_account_id = Column(String(64), ForeignKey("accounts.id"), nullable=False, index=True)
    dest_account_id = Column(String(64), ForeignKey("accounts.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), default="INR")
    timestamp = Column(DateTime, nullable=False, index=True)
    status = Column(String(16), default="SETTLED")  # SETTLED, PENDING, FAILED
    channel = Column(String(32), default="UPI")     # UPI, IMPS, NEFT, RTGS, WIRE, ATM, INTERNAL
    description = Column(String(256), nullable=True)
    has_token_lineage = Column(Boolean, default=False)
    
    source_account = relationship("Account", foreign_keys=[source_account_id], back_populates="outgoing_transactions")
    dest_account = relationship("Account", foreign_keys=[dest_account_id], back_populates="incoming_transactions")
    scenario = relationship("ScenarioDefinition", back_populates="transactions")
    token_lineages = relationship("TokenLineage", back_populates="transaction")
    alerts = relationship("Alert", back_populates="transaction")

Index("idx_tx_src_time", Transaction.source_account_id, Transaction.timestamp)
Index("idx_tx_dst_time", Transaction.dest_account_id, Transaction.timestamp)

class ScenarioDefinition(Base):
    __tablename__ = "scenario_definitions"
    
    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    scenario_type = Column(String(64), nullable=False)  # RAPID_PASSTHROUGH, SMURFING_FANIN, LAYERING_CHAIN, MULE_RING, CROSS_BANK_SPLIT_MERGE, MERCHANT_LOOKALIKE, PAYROLL_LOOKALIKE
    description = Column(Text, nullable=True)
    seed = Column(Integer, default=42)
    config_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    
    transactions = relationship("Transaction", back_populates="scenario")
    runs = relationship("ScenarioRun", back_populates="scenario")

class ScenarioRun(Base):
    __tablename__ = "scenario_runs"
    
    id = Column(String(64), primary_key=True)
    scenario_id = Column(String(64), ForeignKey("scenario_definitions.id"), nullable=False, index=True)
    status = Column(String(16), default="COMPLETED")  # RUNNING, COMPLETED, FAILED
    accounts_count = Column(Integer, default=0)
    transactions_count = Column(Integer, default=0)
    duration_ms = Column(Float, default=0.0)
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)
    
    scenario = relationship("ScenarioDefinition", back_populates="runs")

class TokenLineage(Base):
    __tablename__ = "token_lineages"
    
    id = Column(String(64), primary_key=True)
    token_id = Column(String(64), nullable=False, index=True)  # e.g., e-Rupee token mint/serial
    event_seq = Column(Integer, nullable=False)
    tx_id = Column(String(64), ForeignKey("transactions.id"), nullable=False, index=True)
    from_account_id = Column(String(64), nullable=False)
    to_account_id = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    previous_hash = Column(String(128), nullable=False)
    current_hash = Column(String(128), nullable=False)
    payload_json = Column(Text, nullable=False)
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    
    transaction = relationship("Transaction", back_populates="token_lineages")

Index("idx_token_seq", TokenLineage.token_id, TokenLineage.event_seq)

class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"
    
    id = Column(String(64), primary_key=True)
    account_id = Column(String(64), ForeignKey("accounts.id"), nullable=False, index=True)
    feature_version = Column(String(16), default="v1.0")
    in_degree = Column(Integer, default=0)
    out_degree = Column(Integer, default=0)
    total_inflow = Column(Float, default=0.0)
    total_outflow = Column(Float, default=0.0)
    fan_in = Column(Integer, default=0)
    fan_out = Column(Integer, default=0)
    degree_ratio = Column(Float, default=0.0)
    clustering_coeff = Column(Float, default=0.0)
    component_size = Column(Integer, default=1)
    velocity_10m = Column(Integer, default=0)
    velocity_1h = Column(Integer, default=0)
    velocity_24h = Column(Integer, default=0)
    pass_through_ratio = Column(Float, default=0.0)
    burst_score = Column(Float, default=0.0)
    computed_at = Column(DateTime, default=utc_now)
    
    account = relationship("Account", back_populates="feature_snapshots")

class DetectionResult(Base):
    __tablename__ = "detection_results"
    
    id = Column(String(64), primary_key=True)
    account_id = Column(String(64), ForeignKey("accounts.id"), nullable=False, index=True)
    scenario_id = Column(String(64), nullable=True, index=True)
    composite_risk_score = Column(Float, nullable=False)  # 0.0 to 100.0
    risk_tier = Column(String(16), nullable=False)        # LOW, MEDIUM, HIGH, CRITICAL
    active_signals_count = Column(Integer, default=0)
    contribution_json = Column(Text, nullable=False)      # JSON breakdown of active engine scores
    explanation_text = Column(Text, nullable=False)       # Plain English narrative
    created_at = Column(DateTime, default=utc_now)
    
    account = relationship("Account", back_populates="detection_results")
    evidences = relationship("RuleEvidence", back_populates="detection")

class RuleEvidence(Base):
    __tablename__ = "rule_evidences"
    
    id = Column(String(64), primary_key=True)
    detection_id = Column(String(64), ForeignKey("detection_results.id"), nullable=False, index=True)
    rule_code = Column(String(32), nullable=False)
    rule_name = Column(String(128), nullable=False)
    predicate_met = Column(Boolean, default=False)
    observed_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    time_window = Column(String(32), nullable=True)
    bounded_contribution = Column(Float, default=0.0)
    evidence_refs_json = Column(Text, nullable=True)  # List of matching transaction IDs or account IDs
    
    detection = relationship("DetectionResult", back_populates="evidences")

class TraceExecution(Base):
    __tablename__ = "trace_executions"
    
    id = Column(String(64), primary_key=True)
    start_account_id = Column(String(64), nullable=False, index=True)
    direction = Column(String(16), default="FORWARD")  # FORWARD, BACKWARD, BIDIRECTIONAL
    max_hops = Column(Integer, default=4)
    lookback_hours = Column(Float, default=72.0)
    lookahead_hours = Column(Float, default=72.0)
    stop_reason = Column(String(64), nullable=False)   # OFF_RAMP_REACHED, NO_ELIGIBLE_INCOMING_OR_OUTGOING_TRANSACTIONS, LOOKBACK_OR_LOOKAHEAD_WINDOW_EXCEEDED, MAX_HOPS_REACHED, SEARCH_BUDGET_EXHAUSTED
    nodes_visited = Column(Integer, default=0)
    edges_traversed = Column(Integer, default=0)
    paths_json = Column(Text, nullable=False)          # Reconstructed paths
    created_at = Column(DateTime, default=utc_now)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String(64), primary_key=True)
    account_id = Column(String(64), ForeignKey("accounts.id"), nullable=False, index=True)
    transaction_id = Column(String(64), ForeignKey("transactions.id"), nullable=True, index=True)
    severity = Column(String(16), default="MEDIUM")    # INFO, WARNING, HIGH, CRITICAL
    alert_type = Column(String(64), nullable=False)    # RAPID_PASSTHROUGH, BURST_VELOCITY, SMURFING_FANIN, CRYPTO_RAMP_DRAIN, LINEAGE_INTEGRITY_FAIL, ANOMALY_CLUSTER
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(16), default="OPEN")        # OPEN, INVESTIGATING, DISMISSED, RESOLVED
    created_at = Column(DateTime, default=utc_now)
    
    account = relationship("Account", back_populates="alerts")
    transaction = relationship("Transaction", back_populates="alerts")

class IncidentCase(Base):
    __tablename__ = "incident_cases"
    
    id = Column(String(64), primary_key=True)
    case_number = Column(String(32), unique=True, nullable=False, index=True)
    title = Column(String(128), nullable=False)
    status = Column(String(16), default="NEW")         # NEW, IN_REVIEW, ESCALATED, FROZEN, CLOSED
    priority = Column(String(16), default="HIGH")      # LOW, MEDIUM, HIGH, URGENT
    primary_account_id = Column(String(64), ForeignKey("accounts.id"), nullable=False, index=True)
    assigned_to = Column(String(64), default="Lead Investigator")
    findings_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    primary_account = relationship("Account", back_populates="cases")
    notes = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan")
    status_events = relationship("CaseStatusEvent", back_populates="case", cascade="all, delete-orphan")
    artifacts = relationship("EvidenceArtifact", back_populates="case", cascade="all, delete-orphan")

class CaseNote(Base):
    __tablename__ = "case_notes"
    
    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("incident_cases.id"), nullable=False, index=True)
    author = Column(String(64), nullable=False)
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)
    
    case = relationship("IncidentCase", back_populates="notes")

class CaseStatusEvent(Base):
    __tablename__ = "case_status_events"
    
    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("incident_cases.id"), nullable=False, index=True)
    old_status = Column(String(16), nullable=False)
    new_status = Column(String(16), nullable=False)
    changed_by = Column(String(64), nullable=False)
    reason = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    
    case = relationship("IncidentCase", back_populates="status_events")

class EvidenceArtifact(Base):
    __tablename__ = "evidence_artifacts"
    
    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("incident_cases.id"), nullable=False, index=True)
    artifact_type = Column(String(32), nullable=False)  # HTML_DOSSIER, JSON_EXPORT, GRAPH_SNAPSHOT
    title = Column(String(128), nullable=False)
    file_path = Column(String(256), nullable=True)
    content_hash = Column(String(128), nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    
    case = relationship("IncidentCase", back_populates="artifacts")

class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(String(64), primary_key=True)
    event_type = Column(String(64), nullable=False, index=True)  # CASE_CREATED, STATUS_UPDATED, SCENARIO_GENERATED, TRACE_EXECUTED, EVIDENCE_EXPORTED, ALGORITHM_EVALUATED
    actor = Column(String(64), default="system")
    target_type = Column(String(32), nullable=True)              # ACCOUNT, CASE, SCENARIO, TRACE
    target_id = Column(String(64), nullable=True, index=True)
    action_details = Column(Text, nullable=False)
    previous_hash = Column(String(128), nullable=False)
    current_hash = Column(String(128), nullable=False)
    timestamp = Column(DateTime, default=utc_now)
    success = Column(Boolean, default=True)

class ModelMetadata(Base):
    __tablename__ = "model_metadata"
    
    id = Column(String(64), primary_key=True)
    model_name = Column(String(64), unique=True, nullable=False)  # ISOLATION_FOREST, GRAPHSAGE, LOUVAIN_COMMUNITY
    model_type = Column(String(64), nullable=False)
    version = Column(String(16), default="v1.0")
    training_status = Column(String(16), default="NOT_TRAINED")   # NOT_TRAINED, TRAINING, READY, FAILED
    contamination_or_hyperparams_json = Column(Text, nullable=True)
    metrics_json = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=utc_now)

class BenchmarkResult(Base):
    __tablename__ = "benchmark_results"
    
    id = Column(String(64), primary_key=True)
    evaluation_run_id = Column(String(64), nullable=False, index=True)
    model_name = Column(String(64), nullable=False)  # RULE_BASELINE, ISOLATION_FOREST, GRAPHSAGE, COMPOSITE_DETECTOR
    dataset_seed = Column(Integer, default=42)
    total_accounts = Column(Integer, default=0)
    precision = Column(Float, default=0.0)
    recall = Column(Float, default=0.0)
    f1_score = Column(Float, default=0.0)
    false_positive_rate = Column(Float, default=0.0)
    confusion_matrix_json = Column(Text, nullable=True)  # {"tp": ..., "fp": ..., "tn": ..., "fn": ...}
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)

