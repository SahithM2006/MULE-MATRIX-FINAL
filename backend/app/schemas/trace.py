from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TraceRequest(BaseModel):
    account_id: str
    direction: str = Field(default="FORWARD", description="FORWARD, BACKWARD, or BIDIRECTIONAL")
    max_hops: int = Field(default=4, ge=1, le=8)
    lookback_hours: float = Field(default=72.0, ge=0.5, le=720.0)
    lookahead_hours: float = Field(default=72.0, ge=0.5, le=720.0)
    search_budget: int = Field(default=250, ge=10, le=1000)

class GraphNode(BaseModel):
    id: str
    account_number: str
    holder_name: str
    bank_name: str
    bank_swift: str
    account_type: str
    risk_score: float = 0.0
    risk_tier: str = "LOW"
    is_start: bool = False
    is_offramp: bool = False

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    amount: float
    timestamp: datetime
    channel: str
    tx_hash: str
    has_lineage: bool = False

class TraceResult(BaseModel):
    start_account_id: str
    direction: str
    max_hops: int
    stop_reason: str
    stop_reason_description: str
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    paths: List[List[str]] = []
    total_volume_traced: float = 0.0
    nodes_count: int
    edges_count: int

class LineageEventItem(BaseModel):
    id: str
    token_id: str
    event_seq: int
    tx_id: str
    from_account_id: str
    from_account_number: Optional[str] = None
    to_account_id: str
    to_account_number: Optional[str] = None
    amount: float
    previous_hash: str
    current_hash: str
    computed_hash: Optional[str] = None
    is_valid: bool
    created_at: datetime
    payload_json: str

class LineageVerificationResult(BaseModel):
    token_id: str
    is_intact: bool
    total_events: int
    first_broken_seq: Optional[int] = None
    verification_status: str  # VERIFIED_INTACT, INTEGRITY_COMPROMISED, NO_LINEAGE_FOUND
    error_reason: Optional[str] = None
    chain: List[LineageEventItem]

