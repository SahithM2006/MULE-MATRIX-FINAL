import json
import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import TokenLineage, TraceExecution, Account
from app.schemas.trace import TraceRequest, TraceResult, LineageVerificationResult, LineageEventItem
from app.algorithms.bfs_tracer import BFSTracer
from app.algorithms.lineage_verifier import LineageVerifier
from app.services.graph_service import GraphService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/trace", tags=["Trace"])

@router.post("/bfs", response_model=TraceResult)
def run_bfs_trace(req: TraceRequest, db: Session = Depends(get_db)):
    acc = db.query(Account).filter_by(id=req.account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail=f"Account '{req.account_id}' not found.")
        
    G = GraphService.get_graph(db)
    tracer = BFSTracer(
        default_max_hops=req.max_hops,
        default_lookback_hours=req.lookback_hours,
        default_lookahead_hours=req.lookahead_hours,
        search_budget=req.search_budget
    )
    
    result = tracer.trace(
        G=G,
        start_account_id=req.account_id,
        direction=req.direction,
        max_hops=req.max_hops,
        lookback_hours=req.lookback_hours,
        lookahead_hours=req.lookahead_hours
    )
    
    # Persist execution trace with unique execution ID
    trace_rec = TraceExecution(
        id=f"trc_{int(time.time()*1000)}_{uuid.uuid4().hex[:8]}",
        start_account_id=req.account_id,
        direction=req.direction,
        max_hops=req.max_hops,
        lookback_hours=req.lookback_hours,
        lookahead_hours=req.lookahead_hours,
        stop_reason=result["stop_reason"],
        nodes_visited=result["nodes_count"],
        edges_traversed=result["edges_count"],
        paths_json=json.dumps(result["paths"])
    )
    db.add(trace_rec)
    db.commit()
    
    AuditService.record_event(
        db=db,
        event_type="TRACE_EXECUTED",
        action_details=f"BFS {req.direction} trace from {req.account_id} (Nodes: {result['nodes_count']}, Edges: {result['edges_count']}, Stop Reason: {result['stop_reason']})",
        actor="Investigator Workspace",
        target_type="TRACE",
        target_id=req.account_id
    )
    
    return TraceResult(**result)

@router.get("/tokens")
def list_available_tokens(db: Session = Depends(get_db)):
    """
    Returns all cryptographic token IDs present in the lineage database with summary metrics.
    """
    distinct_tokens = db.query(TokenLineage.token_id).distinct().all()
    token_ids = [r[0] for r in distinct_tokens]
    results = []
    for tid in token_ids:
        events = db.query(TokenLineage).filter_by(token_id=tid).order_by(TokenLineage.event_seq.asc()).all()
        if events:
            results.append({
                "token_id": tid,
                "total_events": len(events),
                "origin_account_id": events[0].from_account_id,
                "terminal_account_id": events[-1].to_account_id,
                "amount": float(events[0].amount),
                "created_at": events[0].created_at.isoformat() if events[0].created_at else None
            })
    return results

@router.post("/lineage/tamper-test")
def simulate_tamper_test(token_id: str = Query(...), tamper_seq: int = Query(default=1), db: Session = Depends(get_db)):
    """
    Demonstrates Algorithm 2 by deliberately mutating an event payload to prove
    that the SHA-256 verification engine detects the first broken link.
    """
    records = db.query(TokenLineage).filter_by(token_id=token_id).order_by(TokenLineage.event_seq.asc()).all()
    if not records:
        raise HTTPException(status_code=404, detail=f"Token '{token_id}' not found.")
        
    events = []
    for r in records:
        payload = json.loads(r.payload_json) if isinstance(r.payload_json, str) else dict(r.payload_json)
        # Inject deliberate tampering on specified seq
        if r.event_seq == tamper_seq:
            payload["amount"] = float(payload.get("amount", 0.0)) + 50000.0  # modified amount
            
        events.append({
            "id": r.id,
            "token_id": r.token_id,
            "event_seq": r.event_seq,
            "tx_id": r.tx_id,
            "from_account_id": r.from_account_id,
            "to_account_id": r.to_account_id,
            "amount": payload.get("amount", r.amount),
            "previous_hash": r.previous_hash,
            "current_hash": r.current_hash,  # unchanged recorded hash -> causes mismatch
            "payload": payload
        })
        
    verification = LineageVerifier.verify_chain(events)
    return {
        "tamper_simulation": "SUCCESS",
        "simulated_tamper_seq": tamper_seq,
        "verification_result": verification
    }

@router.get("/lineage/{token_id}", response_model=LineageVerificationResult)
def get_token_lineage(token_id: str, db: Session = Depends(get_db)):
    records = db.query(TokenLineage).filter_by(token_id=token_id).order_by(TokenLineage.event_seq.asc()).all()
    
    if not records:
        raise HTTPException(status_code=404, detail=f"Token lineage for ID '{token_id}' not found.")
        
    events = []
    for r in records:
        events.append({
            "id": r.id,
            "token_id": r.token_id,
            "event_seq": r.event_seq,
            "tx_id": r.tx_id,
            "from_account_id": r.from_account_id,
            "to_account_id": r.to_account_id,
            "amount": r.amount,
            "previous_hash": r.previous_hash,
            "current_hash": r.current_hash,
            "payload_json": r.payload_json
        })
        
    verification = LineageVerifier.verify_chain(events)
    
    chain_items = []
    for step in verification["verified_chain"]:
        chain_items.append(LineageEventItem(
            id=f"lin_{token_id}_{step['event_seq']}",
            token_id=token_id,
            event_seq=step["event_seq"],
            tx_id=step["tx_id"] or "",
            from_account_id=step["from_account_id"] or "",
            to_account_id=step["to_account_id"] or "",
            amount=step["amount"],
            previous_hash=step["recorded_previous_hash"],
            current_hash=step["recorded_current_hash"],
            computed_hash=step["recomputed_hash"],
            is_valid=step["is_step_valid"],
            created_at=records[min(step["event_seq"], len(records)-1)].created_at,
            payload_json=f'{{"amount": {step["amount"]}}}'
        ))
        
    return LineageVerificationResult(
        token_id=token_id,
        is_intact=verification["is_intact"],
        total_events=verification["total_events"],
        first_broken_seq=verification["first_broken_seq"],
        verification_status=verification["verification_status"],
        error_reason=verification["error_reason"],
        chain=chain_items
    )
