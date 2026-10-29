import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Account, Transaction, TokenLineage, BenchmarkResult, ModelMetadata
from app.schemas.detect import AccountRiskProfile, BenchmarkReport, EngineSignal
from app.algorithms.feature_extractor import FeatureExtractor
from app.algorithms.rule_engine import RuleEngine
from app.algorithms.velocity_engine import VelocityEngine
from app.algorithms.isolation_forest import IsolationForestEngine
from app.algorithms.louvain_engine import LouvainCommunityEngine
from app.algorithms.graphsage_engine import GraphSAGEEngine
from app.algorithms.lineage_verifier import LineageVerifier
from app.services.graph_service import GraphService
from app.services.risk_aggregator import RiskAggregator
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/detect", tags=["Detect"])

@router.get("/account/{account_id}", response_model=AccountRiskProfile)
def get_account_risk_profile(account_id: str, db: Session = Depends(get_db)):
    acc = db.query(Account).filter_by(id=account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail=f"Account '{account_id}' not found.")
        
    G = GraphService.get_graph(db)
    in_txs = list(acc.incoming_transactions)
    out_txs = list(acc.outgoing_transactions)
    
    # 1. Feature Extraction (Consistent feature source)
    features = FeatureExtractor.extract_features(G, acc.id)
    
    # 2. Rule Engine
    rule_engine = RuleEngine()
    rule_res = rule_engine.evaluate(acc, in_txs, out_txs, features)
    
    # 3. Sliding-window Temporal Velocity
    vel_engine = VelocityEngine()
    vel_res = vel_engine.analyze_account(acc.id, in_txs, out_txs)
    
    # 4. Isolation Forest
    iso_engine = IsolationForestEngine()
    iso_res = iso_engine.predict(features)
    
    # 5. Louvain Community Detection
    louvain_engine = LouvainCommunityEngine()
    louvain_res = louvain_engine.analyze_account(G, acc.id)
    
    # 6. GraphSAGE Inductive Classifier
    gs_engine = GraphSAGEEngine()
    gs_res = gs_engine.predict(G, acc.id)
    
    # 7. Token Lineage (if available for account's transactions)
    lineage_records = db.query(TokenLineage).filter(
        (TokenLineage.from_account_id == acc.id) | (TokenLineage.to_account_id == acc.id)
    ).all()
    lineage_res = None
    if lineage_records:
        token_id = lineage_records[0].token_id
        all_token_events = db.query(TokenLineage).filter_by(token_id=token_id).order_by(TokenLineage.event_seq.asc()).all()
        events_payload = [{
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
        } for r in all_token_events]
        lineage_res = LineageVerifier.verify_chain(events_payload)
        
    # Aggregate Composite Risk
    composite = RiskAggregator.aggregate(
        account_id=acc.id,
        account_number=acc.account_number,
        holder_name=acc.holder_name,
        bank_name=acc.institution.name if acc.institution else "Synthetic Bank",
        rule_result=rule_res,
        velocity_result=vel_res,
        iso_result=iso_res,
        louvain_result=louvain_res,
        graphsage_result=gs_res,
        lineage_result=lineage_res,
        feature_metrics=features
    )
    
    return AccountRiskProfile(
        account_id=acc.id,
        account_number=acc.account_number,
        holder_name=acc.holder_name,
        bank_name=acc.institution.name if acc.institution else "Synthetic Bank",
        bank_swift=acc.institution.swift_bic if acc.institution else "MULEINBB",
        account_type=acc.account_type,
        balance=float(acc.balance),
        composite_risk_score=composite["composite_risk_score"],
        risk_tier=composite["risk_tier"],
        active_signals_count=composite["active_signals_count"],
        narrative_explanation=composite["narrative_explanation"],
        signals=composite["signals"],
        feature_metrics=features,
        rule_evidences=rule_res.get("evidences", [])
    )

@router.get("/benchmark", response_model=BenchmarkReport)
def get_latest_benchmark(db: Session = Depends(get_db)):
    latest_run = db.query(BenchmarkResult).order_by(BenchmarkResult.created_at.desc()).first()
    if not latest_run:
        # Run initial benchmark if none exists
        eval_data = EvaluationService.run_benchmark_evaluation(db, test_seed=42)
        return BenchmarkReport(**eval_data)
        
    run_id = latest_run.evaluation_run_id
    baseline = db.query(BenchmarkResult).filter_by(evaluation_run_id=run_id, model_name="RULE_BASELINE").first()
    cand = db.query(BenchmarkResult).filter_by(evaluation_run_id=run_id, model_name="CANDIDATE_DETECTOR").first()
    
    iso_engine = IsolationForestEngine()
    gs_engine = GraphSAGEEngine()
    
    base_data = {
        "precision": baseline.precision if baseline else 0.0,
        "recall": baseline.recall if baseline else 0.0,
        "f1_score": baseline.f1_score if baseline else 0.0,
        "false_positive_rate": baseline.false_positive_rate if baseline else 0.0,
        "confusion_matrix": json.loads(baseline.confusion_matrix_json) if baseline and baseline.confusion_matrix_json else {}
    }
    cand_data = {
        "precision": cand.precision if cand else 0.0,
        "recall": cand.recall if cand else 0.0,
        "f1_score": cand.f1_score if cand else 0.0,
        "false_positive_rate": cand.false_positive_rate if cand else 0.0,
        "confusion_matrix": json.loads(cand.confusion_matrix_json) if cand and cand.confusion_matrix_json else {}
    }
    
    return BenchmarkReport(
        evaluation_run_id=run_id,
        evaluated_at=latest_run.created_at,
        test_seed=latest_run.dataset_seed,
        test_accounts_count=latest_run.total_accounts,
        rule_baseline=base_data,
        candidate_detector=cand_data,
        isolation_forest_status=iso_engine.status,
        graphsage_status=gs_engine.status,
        comparison_summary=f"Held-out evaluation comparing Rule Baseline (F1: {base_data['f1_score']}) with Multi-Engine Candidate Matrix (F1: {cand_data['f1_score']})."
    )

@router.post("/benchmark/run", response_model=BenchmarkReport)
def run_benchmark(seed: int = Query(default=105), db: Session = Depends(get_db)):
    eval_data = EvaluationService.run_benchmark_evaluation(db, test_seed=seed)
    return BenchmarkReport(**eval_data)

