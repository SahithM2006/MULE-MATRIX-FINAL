from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from app.models.entities import Transaction

class VelocityEngine:
    """
    Algorithm 1: Sliding-Window Temporal Velocity Engine
    Analyzes transaction counts, inflow, outflow, burst rates, and pass-through ratios
    over 10-minute, 1-hour, and 24-hour rolling windows.
    Zero-denominator safe and boundary validated.
    """
    
    def __init__(self, rapid_passthrough_threshold: float = 0.85, burst_threshold_txs: int = 5):
        self.rapid_passthrough_threshold = rapid_passthrough_threshold
        self.burst_threshold_txs = burst_threshold_txs
        
    def analyze_account(
        self,
        account_id: str,
        incoming_txs: List[Transaction],
        outgoing_txs: List[Transaction],
        reference_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        all_txs = []
        for tx in incoming_txs:
            all_txs.append({"tx": tx, "type": "IN", "time": tx.timestamp, "amount": float(tx.amount)})
        for tx in outgoing_txs:
            all_txs.append({"tx": tx, "type": "OUT", "time": tx.timestamp, "amount": float(tx.amount)})
            
        all_txs.sort(key=lambda x: x["time"])
        
        if not reference_time:
            reference_time = all_txs[-1]["time"] if all_txs else datetime.now(timezone.utc)
            
        # Ensure timezone-aware if needed
        if reference_time.tzinfo is None:
            reference_time = reference_time.replace(tzinfo=timezone.utc)
            
        # Window definitions
        windows = {
            "10m": timedelta(minutes=10),
            "1h": timedelta(hours=1),
            "24h": timedelta(hours=24)
        }
        
        window_stats = {}
        for win_name, delta in windows.items():
            win_start = reference_time - delta
            
            in_amount = 0.0
            out_amount = 0.0
            in_count = 0
            out_count = 0
            tx_ids = []
            
            for item in all_txs:
                t = item["time"]
                if t.tzinfo is None:
                    t = t.replace(tzinfo=timezone.utc)
                    
                if win_start <= t <= reference_time:
                    tx_ids.append(item["tx"].id)
                    if item["type"] == "IN":
                        in_amount += item["amount"]
                        in_count += 1
                    else:
                        out_amount += item["amount"]
                        out_count += 1
                        
            # Pass-through ratio safe calculation
            max_flow = max(in_amount, out_amount)
            min_flow = min(in_amount, out_amount)
            pass_through_ratio = (min_flow / max_flow) if max_flow > 0 else 0.0
            
            # Rapid pass-through flag: Significant funds entered and mostly exited within window
            rapid_passthrough = bool(
                in_amount > 5000.0 and
                out_amount > 5000.0 and
                pass_through_ratio >= self.rapid_passthrough_threshold
            )
            
            total_txs = in_count + out_count
            is_burst = (win_name == "10m" and total_txs >= self.burst_threshold_txs)
            
            window_stats[win_name] = {
                "window_start": win_start.isoformat(),
                "window_end": reference_time.isoformat(),
                "total_txs": total_txs,
                "inflow_amount": round(in_amount, 2),
                "outflow_amount": round(out_amount, 2),
                "inflow_count": in_count,
                "outflow_count": out_count,
                "pass_through_ratio": round(pass_through_ratio, 4),
                "rapid_passthrough": rapid_passthrough,
                "is_burst": is_burst,
                "tx_ids": tx_ids
            }
            
        # Compute normalized velocity risk score (0 - 100)
        score = 0.0
        reasons = []
        
        # 10m burst contribution
        if window_stats["10m"]["is_burst"]:
            burst_score = min(40.0, float(window_stats["10m"]["total_txs"]) * 6.0)
            score += burst_score
            reasons.append(f"High velocity burst detected: {window_stats['10m']['total_txs']} transactions in 10 minutes")
            
        # 1h rapid pass-through
        if window_stats["1h"]["rapid_passthrough"]:
            score += 35.0
            reasons.append(f"Rapid pass-through: {window_stats['1h']['pass_through_ratio']*100:.1f}% funds routed within 1 hour")
            
        # 24h high turnover
        if window_stats["24h"]["total_txs"] >= 20 and window_stats["24h"]["pass_through_ratio"] > 0.8:
            score += 25.0
            reasons.append(f"Sustained 24h pass-through velocity ({window_stats['24h']['total_txs']} transfers, {window_stats['24h']['pass_through_ratio']*100:.1f}% pass-through)")
            
        score = min(100.0, score)
        
        return {
            "account_id": account_id,
            "reference_time": reference_time.isoformat(),
            "windows": window_stats,
            "velocity_risk_score": round(score, 1),
            "reasons": reasons,
            "status": "SUSPICIOUS" if score >= 50.0 else "BENIGN"
        }

