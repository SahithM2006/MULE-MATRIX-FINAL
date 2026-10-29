import time
import json
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from app.models.entities import Account, Transaction, BenchmarkResult, ModelMetadata, utc_now
from app.algorithms.feature_extractor import FeatureExtractor
from app.algorithms.rule_engine import RuleEngine
from app.algorithms.velocity_engine import VelocityEngine
from app.algorithms.isolation_forest import IsolationForestEngine
from app.algorithms.louvain_engine import LouvainCommunityEngine
from app.algorithms.graphsage_engine import GraphSAGEEngine
from app.services.graph_service import GraphService
from app.services.risk_aggregator import RiskAggregator
from app.services.audit_service import AuditService

class EvaluationService:
    """
    Independent Held-Out Detection Evaluation Pipeline
    Compares:
      1. Deterministic Rule-Based Baseline
      2. Combined Candidate Detector (Rules + IsoForest + GraphSAGE + Louvain)
    Strictly isolates ground-truth labels from runtime detection features.
    Computes precision, recall, f1, fpr, confusion matrix, and measured latency.
    """

    @classmethod
    def train_models_if_needed(cls, db: Session) -> Dict[str, Any]:
        """
        Trains Isolation Forest and GraphSAGE on the training partition of accounts.
        """
        G = GraphService.get_graph(db)
        all_accounts = db.query(Account).all()
        
        # Partition accounts into Train scenarios (Alpha, Beta, Gamma) and Held-out Test scenarios (Delta, Epsilon)
        train_mules = [a for a in all_accounts if a.is_mule and any(f"acc_mule_{i:03d}" in a.id for i in range(1, 26))]
        train_legit = [a for a in all_accounts if not a.is_mule and a.account_type in ("CHECKING", "SAVINGS")][:50]
        train_accounts = train_mules + train_legit
        
        train_ids = [a.id for a in train_accounts]
        
        # 1. Train Isolation Forest
        feature_vectors = []
        for acc in train_accounts:
            f = FeatureExtractor.extract_features(G, acc.id)
            vec = FeatureExtractor.to_normalized_vector(f)
            feature_vectors.append(vec)
            
        iso_engine = IsolationForestEngine()
        iso_res = iso_engine.train(np.array(feature_vectors))
        
        # 2. Train GraphSAGE
        # Ground truth labels accessed ONLY here for training loss
        train_labels = {a.id: (1 if a.is_mule else 0) for a in train_accounts}
        gs_engine = GraphSAGEEngine()
        gs_res = gs_engine.train_on_graph(G, train_labels, train_ids, epochs=30)
        
        # Update ModelMetadata records
        cls._update_metadata(db, "ISOLATION_FOREST", "Unsupervised", "v1.0", iso_res.get("status", "READY"), iso_res)
        cls._update_metadata(db, "GRAPHSAGE", "Inductive GNN", "v1.0", gs_res.get("status", "READY"), gs_res)
        
        return {
            "isolation_forest": iso_res,
            "graphsage": gs_res,
            "train_accounts_count": len(train_accounts)
        }

    @classmethod
    def _update_metadata(cls, db: Session, model_name: str, model_type: str, version: str, status: str, meta: Dict[str, Any]):
        rec = db.query(ModelMetadata).filter_by(model_name=model_name).first()
        if not rec:
            rec = ModelMetadata(
                id=f"meta_{model_name.lower()}",
                model_name=model_name,
                model_type=model_type,
                version=version,
                training_status=status,
                contamination_or_hyperparams_json=json.dumps(meta),
                metrics_json=json.dumps(meta)
            )
            db.add(rec)
        else:
            rec.training_status = status
            rec.updated_at = utc_now()
            rec.metrics_json = json.dumps(meta)
        db.commit()

    @classmethod
    def run_benchmark_evaluation(cls, db: Session, test_seed: int = 999) -> Dict[str, Any]:
        """
        Executes benchmark evaluation on held-out test partition.
        Ground truth is strictly isolated and used ONLY for final scoring metric comparison.
        """
        # Ensure models are trained
        cls.train_models_if_needed(db)
        
        G = GraphService.get_graph(db)
        all_accounts = db.query(Account).all()
        
        # Held-out Test accounts: Mules from Scenarios Delta (30-34) and Epsilon (40-44), plus lookalikes
        test_mules = [a for a in all_accounts if a.is_mule and any(f"acc_mule_{i:03d}" in a.id for i in range(30, 45))]
        test_merchants = [a for a in all_accounts if a.account_type == "MERCHANT"][:5]
        test_corporates = [a for a in all_accounts if a.account_type == "CORPORATE"][:5]
        test_retail = [a for a in all_accounts if not a.is_mule and a.account_type in ("CHECKING", "SAVINGS")][60:85]
        test_accounts = test_mules + test_merchants + test_corporates + test_retail
            
        y_true = []
        baseline_preds = []
        candidate_preds = []
        
        rule_engine = RuleEngine()
        vel_engine = VelocityEngine()
        iso_engine = IsolationForestEngine()
        louvain_engine = LouvainCommunityEngine()
        gs_engine = GraphSAGEEngine()
        
        run_id = f"eval_{int(utc_now().timestamp())}_{test_seed}"
        start_time = time.time()
        
        for acc in test_accounts:
            # 1. Ground truth label (ISOLATED - NOT passed to any engine)
            label = 1 if acc.is_mule else 0
            y_true.append(label)
            
            # Fetch transactions
            in_txs = list(acc.incoming_transactions)
            out_txs = list(acc.outgoing_transactions)
            
            # Extract features (runtime inputs only)
            features = FeatureExtractor.extract_features(G, acc.id)
            
            # --- EVALUATE BASELINE (Rules Only) ---
            rule_res = rule_engine.evaluate(acc, in_txs, out_txs, features)
            baseline_flag = 1 if rule_res["rule_risk_score"] >= 50.0 else 0
            baseline_preds.append(baseline_flag)
            
            # --- EVALUATE CANDIDATE DETECTOR (Multi-Engine Matrix) ---
            vel_res = vel_engine.analyze_account(acc.id, in_txs, out_txs)
            iso_res = iso_engine.predict(features)
            louvain_res = louvain_engine.analyze_account(G, acc.id)
            gs_res = gs_engine.predict(G, acc.id)
            
            composite = RiskAggregator.aggregate(
                account_id=acc.id,
                account_number=acc.account_number,
                holder_name=acc.holder_name,
                bank_name="Test Bank",
                rule_result=rule_res,
                velocity_result=vel_res,
                iso_result=iso_res,
                louvain_result=louvain_res,
                graphsage_result=gs_res,
                feature_metrics=features
            )
            candidate_flag = 1 if composite["composite_risk_score"] >= 45.0 else 0
            candidate_preds.append(candidate_flag)

        total_latency_ms = (time.time() - start_time) * 1000.0
        avg_latency_ms = total_latency_ms / max(1, len(test_accounts))
        
        # Calculate Metrics
        def compute_metrics(y_actual, y_predicted):
            cm = confusion_matrix(y_actual, y_predicted, labels=[0, 1])
            tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])
            prec = float(precision_score(y_actual, y_predicted, zero_division=0))
            rec = float(recall_score(y_actual, y_predicted, zero_division=0))
            f1 = float(f1_score(y_actual, y_predicted, zero_division=0))
            fpr = float(fp / max(1, fp + tn))
            return {
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "false_positive_rate": round(fpr, 4),
                "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn}
            }

        base_metrics = compute_metrics(y_true, baseline_preds)
        cand_metrics = compute_metrics(y_true, candidate_preds)
        
        # Persist results to DB
        b_rec1 = BenchmarkResult(
            id=f"{run_id}_baseline",
            evaluation_run_id=run_id,
            model_name="RULE_BASELINE",
            dataset_seed=test_seed,
            total_accounts=len(test_accounts),
            precision=base_metrics["precision"],
            recall=base_metrics["recall"],
            f1_score=base_metrics["f1_score"],
            false_positive_rate=base_metrics["false_positive_rate"],
            confusion_matrix_json=json.dumps(base_metrics["confusion_matrix"]),
            latency_ms=round(avg_latency_ms, 2)
        )
        b_rec2 = BenchmarkResult(
            id=f"{run_id}_candidate",
            evaluation_run_id=run_id,
            model_name="CANDIDATE_DETECTOR",
            dataset_seed=test_seed,
            total_accounts=len(test_accounts),
            precision=cand_metrics["precision"],
            recall=cand_metrics["recall"],
            f1_score=cand_metrics["f1_score"],
            false_positive_rate=cand_metrics["false_positive_rate"],
            confusion_matrix_json=json.dumps(cand_metrics["confusion_matrix"]),
            latency_ms=round(avg_latency_ms, 2)
        )
        db.add(b_rec1)
        db.add(b_rec2)
        db.commit()
        
        AuditService.record_event(
            db=db,
            event_type="ALGORITHM_EVALUATED",
            action_details=f"Evaluated held-out test benchmark on {len(test_accounts)} accounts. Baseline F1: {base_metrics['f1_score']}, Candidate F1: {cand_metrics['f1_score']}",
            actor="Evaluation Harness",
            target_type="BENCHMARK",
            target_id=run_id
        )

        return {
            "evaluation_run_id": run_id,
            "evaluated_at": utc_now().isoformat(),
            "test_seed": test_seed,
            "test_accounts_count": len(test_accounts),
            "rule_baseline": base_metrics,
            "candidate_detector": cand_metrics,
            "avg_latency_per_account_ms": round(avg_latency_ms, 2),
            "isolation_forest_status": iso_engine.status,
            "graphsage_status": gs_engine.status,
            "comparison_summary": f"Candidate multi-engine detector achieved F1 of {cand_metrics['f1_score']} (Recall {cand_metrics['recall']}, Precision {cand_metrics['precision']}) vs Baseline Rule F1 of {base_metrics['f1_score']} on {len(test_accounts)} held-out accounts."
        }
