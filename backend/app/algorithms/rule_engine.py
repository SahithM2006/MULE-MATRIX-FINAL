from typing import List, Dict, Any, Optional
from datetime import timedelta, timezone
from app.models.entities import Account, Transaction

class RuleEngine:
    """
    Algorithm 5: Explainable Rule-Based Risk Engine
    Evaluates explicit declarative predicates with bounded score contributions.
    Discards legitimate lookalikes (payroll fan-out, merchant fan-in) via semantic guardrails.
    """
    
    DEFAULT_THRESHOLDS = {
        "R101_RAPID_PASSTHROUGH": 0.85,     # 85% passed through within 1 hour
        "R102_VELOCITY_BURST": 5.0,          # >= 5 txs in 10 minutes
        "R103_STRUCTURED_SMURFING": 4.0,     # >= 4 incoming smurf transfers (< 50k INR)
        "R104_LAYERING_CONDUIT": 3.0,        # Fan-in >= 3 AND Fan-out >= 3
        "R105_CROSS_BANK_DISPERSION": 2.0,   # >= 2 distinct banks in short window
        "R106_CRYPTO_OFFRAMP_DRAIN": 1.0     # Direct transfer to crypto off-ramp terminal
    }
    
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = dict(self.DEFAULT_THRESHOLDS)
        if thresholds:
            self.thresholds.update(thresholds)

    def evaluate(
        self,
        account: Account,
        incoming_txs: List[Transaction],
        outgoing_txs: List[Transaction],
        feature_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        results = []
        total_score = 0.0
        
        # Guardrail for legitimate lookalikes
        is_merchant = account.account_type == "MERCHANT"
        is_corporate_payroll = account.account_type == "CORPORATE"
        
        # -------------------------------------------------------------
        # R-101: Rapid Pass-Through
        # -------------------------------------------------------------
        total_in = feature_metrics.get("total_inflow", 0.0)
        total_out = feature_metrics.get("total_outflow", 0.0)
        pass_ratio = feature_metrics.get("pass_through_ratio", 0.0)
        threshold_101 = self.thresholds["R101_RAPID_PASSTHROUGH"]
        
        # Require substantial balance movement and high turnover (not a corporate payroll or merchant)
        r101_met = bool(
            not is_merchant and
            not is_corporate_payroll and
            total_in >= 10000.0 and
            total_out >= 10000.0 and
            pass_ratio >= threshold_101
        )
        r101_contrib = 30.0 if r101_met else 0.0
        r101_refs = [tx.id for tx in incoming_txs[:3] + outgoing_txs[:3]]
        
        results.append({
            "rule_code": "R-101",
            "rule_name": "Rapid Pass-Through Conduit",
            "predicate_met": r101_met,
            "observed_value": round(pass_ratio, 4),
            "threshold": threshold_101,
            "time_window": "1 Hour",
            "bounded_contribution": r101_contrib,
            "evidence_refs": r101_refs if r101_met else [],
            "description": f"Observed pass-through ratio {pass_ratio*100:.1f}% exceeds threshold {threshold_101*100:.1f}%."
        })
        total_score += r101_contrib
        
        # -------------------------------------------------------------
        # R-102: Velocity Burst
        # -------------------------------------------------------------
        burst_val = feature_metrics.get("burst_score", 0.0)
        threshold_102 = self.thresholds["R102_VELOCITY_BURST"]
        r102_met = bool(burst_val >= threshold_102)
        r102_contrib = 20.0 if r102_met else 0.0
        
        results.append({
            "rule_code": "R-102",
            "rule_name": "High-Frequency Velocity Burst",
            "predicate_met": r102_met,
            "observed_value": float(burst_val),
            "threshold": threshold_102,
            "time_window": "10 Minutes",
            "bounded_contribution": r102_contrib,
            "evidence_refs": [tx.id for tx in incoming_txs[:5]] if r102_met else [],
            "description": f"Observed {int(burst_val)} transactions within 10 minutes (threshold: {int(threshold_102)})."
        })
        total_score += r102_contrib
        
        # -------------------------------------------------------------
        # R-103: Structured Smurfing (Fan-in of small deposits)
        # -------------------------------------------------------------
        small_deposits = [tx for tx in incoming_txs if 1000.0 <= float(tx.amount) <= 49999.0]
        unique_smurf_sources = len(set(tx.source_account_id for tx in small_deposits))
        threshold_103 = self.thresholds["R103_STRUCTURED_SMURFING"]
        
        # Merchant fan-in has distinct commercial characteristics (not smurfing)
        r103_met = bool(not is_merchant and unique_smurf_sources >= threshold_103)
        r103_contrib = 25.0 if r103_met else 0.0
        
        results.append({
            "rule_code": "R-103",
            "rule_name": "Structured Smurfing Fan-In",
            "predicate_met": r103_met,
            "observed_value": float(unique_smurf_sources),
            "threshold": threshold_103,
            "time_window": "24 Hours",
            "bounded_contribution": r103_contrib,
            "evidence_refs": [tx.id for tx in small_deposits[:6]] if r103_met else [],
            "description": f"Identified {unique_smurf_sources} structured deposits below reporting limits from unique senders."
        })
        total_score += r103_contrib
        
        # -------------------------------------------------------------
        # R-104: Layering Conduit (High Fan-In + High Fan-Out)
        # -------------------------------------------------------------
        fan_in = feature_metrics.get("fan_in", 0.0)
        fan_out = feature_metrics.get("fan_out", 0.0)
        threshold_104 = self.thresholds["R104_LAYERING_CONDUIT"]
        
        r104_met = bool(
            not is_merchant and
            not is_corporate_payroll and
            fan_in >= threshold_104 and
            fan_out >= threshold_104 and
            pass_ratio >= 0.70
        )
        r104_contrib = 20.0 if r104_met else 0.0
        
        results.append({
            "rule_code": "R-104",
            "rule_name": "Multi-Hop Layering Node",
            "predicate_met": r104_met,
            "observed_value": min(fan_in, fan_out),
            "threshold": threshold_104,
            "time_window": "Observation Window",
            "bounded_contribution": r104_contrib,
            "evidence_refs": [tx.id for tx in incoming_txs[:2] + outgoing_txs[:2]] if r104_met else [],
            "description": f"Balanced high fan-in ({int(fan_in)}) and fan-out ({int(fan_out)}) with low capital retention."
        })
        total_score += r104_contrib
        
        # -------------------------------------------------------------
        # R-105: Cross-Bank Dispersion
        # -------------------------------------------------------------
        dest_banks = set()
        for tx in outgoing_txs:
            if hasattr(tx, 'dest_account') and tx.dest_account:
                dest_banks.add(tx.dest_account.institution_id)
        threshold_105 = self.thresholds["R105_CROSS_BANK_DISPERSION"]
        r105_met = bool(len(dest_banks) >= threshold_105 and len(outgoing_txs) >= 2)
        r105_contrib = 15.0 if r105_met else 0.0
        
        results.append({
            "rule_code": "R-105",
            "rule_name": "Cross-Bank Dispersion",
            "predicate_met": r105_met,
            "observed_value": float(len(dest_banks)),
            "threshold": threshold_105,
            "time_window": "2 Hours",
            "bounded_contribution": r105_contrib,
            "evidence_refs": [tx.id for tx in outgoing_txs[:4]] if r105_met else [],
            "description": f"Funds dispersed across {len(dest_banks)} distinct synthetic banking institutions."
        })
        total_score += r105_contrib
        
        # -------------------------------------------------------------
        # R-106: High-Risk Off-Ramp Bridge
        # -------------------------------------------------------------
        offramp_drain_txs = [
            tx for tx in outgoing_txs
            if hasattr(tx, 'dest_account') and tx.dest_account and tx.dest_account.account_type in ("CRYPTO_OFFRAMP", "ATM_CASHOUT")
        ]
        r106_met = bool(len(offramp_drain_txs) >= 1)
        r106_contrib = 25.0 if r106_met else 0.0
        
        results.append({
            "rule_code": "R-106",
            "rule_name": "Terminal Off-Ramp Exit",
            "predicate_met": r106_met,
            "observed_value": float(len(offramp_drain_txs)),
            "threshold": 1.0,
            "time_window": "Observation Window",
            "bounded_contribution": r106_contrib,
            "evidence_refs": [tx.id for tx in offramp_drain_txs] if r106_met else [],
            "description": f"Direct dissipation of funds into {len(offramp_drain_txs)} unhosted crypto/cash terminal points."
        })
        total_score += r106_contrib

        bounded_total = min(100.0, total_score)
        
        return {
            "account_id": account.id,
            "rule_risk_score": round(bounded_total, 1),
            "rules_evaluated": len(results),
            "rules_triggered": sum(1 for r in results if r["predicate_met"]),
            "evidences": results
        }

