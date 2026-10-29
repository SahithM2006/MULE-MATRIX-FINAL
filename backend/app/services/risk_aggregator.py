from typing import Dict, Any, List, Optional
from app.schemas.detect import EngineSignal

class RiskAggregator:
    """
    Explainable Risk Aggregation Service
    Combines outputs from active detection engines with documented, versioned weights.
    Dynamically renormalizes over available active signals.
    Does NOT blindly count BFS traversal or intact cryptographic lineage as fraud signals.
    Generates plain-English factual narratives.
    """
    
    VERSION = "v1.2.0"
    
    # Base canonical weights for active anomaly/detection engines
    BASE_WEIGHTS = {
        "rules": 0.35,           # Rule-based pattern engine
        "velocity": 0.20,        # Sliding-window burst & turnover
        "graphsage": 0.20,       # Inductive GraphSAGE mule classifier
        "isolation_forest": 0.15,# Topological outlier detection
        "louvain": 0.10          # Community structure & mule ring clustering
    }

    @classmethod
    def aggregate(
        cls,
        account_id: str,
        account_number: str,
        holder_name: str,
        bank_name: str,
        rule_result: Dict[str, Any],
        velocity_result: Dict[str, Any],
        iso_result: Dict[str, Any],
        louvain_result: Dict[str, Any],
        graphsage_result: Dict[str, Any],
        lineage_result: Optional[Dict[str, Any]] = None,
        feature_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        signals: List[EngineSignal] = []
        active_weights = {}
        
        # 1. Rule Engine Signal
        rule_score = float(rule_result.get("rule_risk_score", 0.0))
        rules_triggered = int(rule_result.get("rules_triggered", 0))
        signals.append(EngineSignal(
            engine_id="rules",
            engine_name="Rule-Based Pattern Engine",
            status="SUSPICIOUS" if rules_triggered > 0 else "BENIGN",
            score=round(rule_score, 1),
            weight=cls.BASE_WEIGHTS["rules"],
            weighted_contribution=0.0,
            summary=f"{rules_triggered} rule predicates triggered out of {rule_result.get('rules_evaluated', 6)} evaluated.",
            details={"triggered_count": rules_triggered, "evidences": rule_result.get("evidences", [])}
        ))
        active_weights["rules"] = cls.BASE_WEIGHTS["rules"]
        
        # 2. Velocity Engine Signal
        vel_score = float(velocity_result.get("velocity_risk_score", 0.0))
        signals.append(EngineSignal(
            engine_id="velocity",
            engine_name="Sliding-Window Temporal Velocity",
            status=velocity_result.get("status", "BENIGN"),
            score=round(vel_score, 1),
            weight=cls.BASE_WEIGHTS["velocity"],
            weighted_contribution=0.0,
            summary="; ".join(velocity_result.get("reasons", ["Normal transaction velocity over 10m/1h/24h."])) or "Normal velocity.",
            details=velocity_result.get("windows", {})
        ))
        active_weights["velocity"] = cls.BASE_WEIGHTS["velocity"]
        
        # 3. Isolation Forest Signal
        iso_status = iso_result.get("status", "NOT_TRAINED")
        if iso_status == "READY":
            iso_score = float(iso_result.get("anomaly_score", 0.0))
            is_outlier = bool(iso_result.get("is_outlier", False))
            signals.append(EngineSignal(
                engine_id="isolation_forest",
                engine_name="Isolation Forest Anomaly Engine",
                status="SUSPICIOUS" if is_outlier else "BENIGN",
                score=round(iso_score, 1),
                weight=cls.BASE_WEIGHTS["isolation_forest"],
                weighted_contribution=0.0,
                summary=f"Topological anomaly score {iso_score:.1f}/100. Outlier flag: {is_outlier}.",
                details={"top_anomalous_features": iso_result.get("top_anomalous_features", []), "raw_decision": iso_result.get("raw_decision_score")}
            ))
            active_weights["isolation_forest"] = cls.BASE_WEIGHTS["isolation_forest"]
        else:
            signals.append(EngineSignal(
                engine_id="isolation_forest",
                engine_name="Isolation Forest Anomaly Engine",
                status="NOT_TRAINED",
                score=0.0,
                weight=0.0,
                weighted_contribution=0.0,
                summary="Isolation Forest model has not been trained yet.",
                details={}
            ))
            
        # 4. GraphSAGE Signal
        gs_status = graphsage_result.get("status", "NOT_TRAINED")
        if gs_status == "READY":
            gs_score = float(graphsage_result.get("graphsage_risk_score", 0.0))
            gs_prob = float(graphsage_result.get("mule_probability", 0.0))
            signals.append(EngineSignal(
                engine_id="graphsage",
                engine_name="GraphSAGE Inductive Classifier",
                status="SUSPICIOUS" if gs_prob >= 0.50 else "BENIGN",
                score=round(gs_score, 1),
                weight=cls.BASE_WEIGHTS["graphsage"],
                weighted_contribution=0.0,
                summary=f"Inductive neighborhood aggregation predicted mule probability: {gs_prob*100:.1f}%.",
                details={"mule_probability": gs_prob}
            ))
            active_weights["graphsage"] = cls.BASE_WEIGHTS["graphsage"]
        else:
            signals.append(EngineSignal(
                engine_id="graphsage",
                engine_name="GraphSAGE Inductive Classifier",
                status="NOT_TRAINED",
                score=0.0,
                weight=0.0,
                weighted_contribution=0.0,
                summary="GraphSAGE weights unavailable or not trained.",
                details={}
            ))
            
        # 5. Louvain Community Signal
        comm_score = float(louvain_result.get("community_risk_score", 0.0))
        is_cluster = bool(louvain_result.get("is_mule_cluster_candidate", False))
        signals.append(EngineSignal(
            engine_id="louvain",
            engine_name="Louvain Community Detection",
            status="SUSPICIOUS" if is_cluster else "BENIGN",
            score=round(comm_score, 1),
            weight=cls.BASE_WEIGHTS["louvain"],
            weighted_contribution=0.0,
            summary=f"Community #{louvain_result.get('community_id')} (size: {louvain_result.get('community_size')}, internal density: {louvain_result.get('internal_density', 0)*100:.1f}%).",
            details=louvain_result
        ))
        active_weights["louvain"] = cls.BASE_WEIGHTS["louvain"]
        
        # 6. Cryptographic Lineage Status (Integrity Check - not fraud score unless tampered!)
        if lineage_result and lineage_result.get("verification_status") == "INTEGRITY_COMPROMISED":
            # Cryptographic tampering is a severe integrity event
            signals.append(EngineSignal(
                engine_id="lineage",
                engine_name="Token Lineage SHA-256 Verifier",
                status="SUSPICIOUS",
                score=90.0,
                weight=0.10,
                weighted_contribution=0.0,
                summary=f"Cryptographic tampering detected in token lineage at seq #{lineage_result.get('first_broken_seq')}.",
                details=lineage_result
            ))
            active_weights["lineage"] = 0.10
        elif lineage_result and lineage_result.get("verification_status") == "VERIFIED_INTACT":
            signals.append(EngineSignal(
                engine_id="lineage",
                engine_name="Token Lineage SHA-256 Verifier",
                status="BENIGN",
                score=0.0,
                weight=0.0,
                weighted_contribution=0.0,
                summary=f"Verified intact cryptographic lineage chain ({lineage_result.get('total_events')} hops, SHA-256).",
                details=lineage_result
            ))

        # Dynamic renormalization across active weights
        total_weight = sum(active_weights.values())
        composite_score = 0.0
        
        if total_weight > 0.0:
            for s in signals:
                if s.engine_id in active_weights:
                    norm_weight = active_weights[s.engine_id] / total_weight
                    s.weight = round(norm_weight, 3)
                    s.weighted_contribution = round(s.score * norm_weight, 2)
                    composite_score += s.weighted_contribution
                    
        composite_score = min(100.0, max(0.0, composite_score))
        
        # Risk Tier categorization
        if composite_score >= 75.0:
            risk_tier = "CRITICAL"
        elif composite_score >= 50.0:
            risk_tier = "HIGH"
        elif composite_score >= 25.0:
            risk_tier = "MEDIUM"
        else:
            risk_tier = "LOW"
            
        # Plain-English Narrative Construction
        narrative_parts = []
        narrative_parts.append(
            f"Account {account_number} ({holder_name}) at {bank_name} has been evaluated by the multi-engine detection matrix, yielding a composite risk score of {composite_score:.1f}/100 ({risk_tier} RISK)."
        )
        
        triggered_evidences = [e for e in rule_result.get("evidences", []) if e.get("predicate_met")]
        if triggered_evidences:
            rules_str = ", ".join(f"{e['rule_code']} ({e['rule_name']})" for e in triggered_evidences)
            narrative_parts.append(f"Primary behavioral risk arises from triggered deterministic rules: {rules_str}.")
            
        if velocity_result.get("reasons"):
            narrative_parts.append(f"Temporal velocity signals: {'; '.join(velocity_result['reasons'])}.")
            
        if gs_status == "READY" and graphsage_result.get("mule_probability", 0.0) >= 0.5:
            narrative_parts.append(
                f"GraphSAGE neighborhood aggregation confirms high mule probability of {graphsage_result['mule_probability']*100:.1f}% based on 2-hop topology."
            )
            
        if louvain_result.get("is_mule_cluster_candidate"):
            narrative_parts.append(
                f"Louvain modularity analysis isolates the account within a high-density candidate mule ring of {louvain_result.get('community_size')} accounts."
            )
            
        if not triggered_evidences and composite_score < 30.0:
            narrative_parts.append(
                "Transaction patterns remain consistent with baseline financial behaviors; no high-velocity pass-through or structured layering patterns observed."
            )

        return {
            "account_id": account_id,
            "account_number": account_number,
            "holder_name": holder_name,
            "bank_name": bank_name,
            "composite_risk_score": round(composite_score, 1),
            "risk_tier": risk_tier,
            "active_signals_count": len(active_weights),
            "signals": signals,
            "narrative_explanation": " ".join(narrative_parts),
            "aggregation_version": cls.VERSION
        }

