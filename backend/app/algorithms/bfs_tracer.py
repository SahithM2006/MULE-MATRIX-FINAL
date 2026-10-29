from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import deque
import networkx as nx

class BFSTracer:
    """
    Algorithm 3: Time-Constrained Breadth-First Search (BFS) Traversal Engine
    Reconstructs chronological multi-hop money flows with explicit temporal windows,
    search limits, cycle prevention, and precise stop reasons.
    """
    
    STOP_REASONS = {
        "OFF_RAMP_REACHED": "Traversal terminated upon reaching a designated off-ramp/cash-out terminal (crypto bridge, ATM, or cash desk).",
        "NO_ELIGIBLE_INCOMING_OR_OUTGOING_TRANSACTIONS": "No further transactions were found in the graph meeting direction and chronological continuity criteria.",
        "LOOKBACK_OR_LOOKAHEAD_WINDOW_EXCEEDED": "Further transactions exist, but their timestamps fall outside the configured temporal lookback/lookahead window.",
        "MAX_HOPS_REACHED": "Maximum configured hop traversal depth limit was reached.",
        "SEARCH_BUDGET_EXHAUSTED": "Search space exceeded the maximum allocated node/edge budget for this investigation.",
        "START_ACCOUNT_NOT_FOUND": "The specified starting account does not exist in the active graph."
    }
    
    def __init__(
        self,
        default_max_hops: int = 4,
        default_lookback_hours: float = 72.0,
        default_lookahead_hours: float = 72.0,
        search_budget: int = 250
    ):
        self.default_max_hops = default_max_hops
        self.default_lookback_hours = default_lookback_hours
        self.default_lookahead_hours = default_lookahead_hours
        self.search_budget = search_budget

    def trace(
        self,
        G: nx.MultiDiGraph,
        start_account_id: str,
        direction: str = "FORWARD",  # FORWARD, BACKWARD, or BIDIRECTIONAL
        max_hops: Optional[int] = None,
        lookback_hours: Optional[float] = None,
        lookahead_hours: Optional[float] = None,
        reference_time: Optional[datetime] = None,
        offramp_types: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        if start_account_id not in G:
            return {
                "start_account_id": start_account_id,
                "direction": direction,
                "max_hops": max_hops or self.default_max_hops,
                "stop_reason": "START_ACCOUNT_NOT_FOUND",
                "stop_reason_description": self.STOP_REASONS["START_ACCOUNT_NOT_FOUND"],
                "nodes": [],
                "edges": [],
                "paths": [],
                "total_volume_traced": 0.0,
                "nodes_count": 0,
                "edges_count": 0
            }
            
        max_hops = max_hops or self.default_max_hops
        lookback_hours = lookback_hours or self.default_lookback_hours
        lookahead_hours = lookahead_hours or self.default_lookahead_hours
        offramp_types = offramp_types or {"CRYPTO_OFFRAMP", "ATM_CASHOUT", "CASH_SETTLEMENT"}
        
        start_node_data = G.nodes[start_account_id]
        
        if reference_time is None:
            # Pick earliest or latest transaction of the start node as reference
            all_times = []
            for _, _, data in G.out_edges(start_account_id, data=True):
                all_times.append(data.get("timestamp"))
            for _, _, data in G.in_edges(start_account_id, data=True):
                all_times.append(data.get("timestamp"))
            all_times = [t for t in all_times if t is not None]
            reference_time = sorted(all_times)[0] if (direction == "FORWARD" and all_times) else (sorted(all_times)[-1] if all_times else datetime.now(timezone.utc))

        if reference_time.tzinfo is None:
            reference_time = reference_time.replace(tzinfo=timezone.utc)
            
        visited_nodes: Set[str] = {start_account_id}
        collected_edges: Dict[str, Dict[str, Any]] = {}
        paths: List[List[str]] = []
        total_volume = 0.0
        
        stop_reason = "MAX_HOPS_REACHED"
        exhausted_budget = False
        reached_offramp = False
        window_exceeded = False
        
        # Queue item: (current_node_id, current_hop, current_time, current_path)
        queue = deque([(start_account_id, 0, reference_time, [start_account_id])])
        
        while queue:
            if len(visited_nodes) >= self.search_budget or len(collected_edges) >= self.search_budget:
                exhausted_budget = True
                stop_reason = "SEARCH_BUDGET_EXHAUSTED"
                break
                
            curr_node, curr_hop, curr_time, curr_path = queue.popleft()
            
            # Check if current node is an offramp (and not the starting node)
            curr_type = G.nodes[curr_node].get("account_type", "")
            if curr_node != start_account_id and curr_type in offramp_types:
                reached_offramp = True
                stop_reason = "OFF_RAMP_REACHED"
                paths.append(curr_path)
                continue  # Do not expand beyond off-ramp terminal
                
            if curr_hop >= max_hops:
                paths.append(curr_path)
                continue
                
            # Determine eligible edge candidate list
            candidates = []
            
            if direction in ("FORWARD", "BIDIRECTIONAL"):
                for u, v, key, data in G.out_edges(curr_node, keys=True, data=True):
                    tx_time = data.get("timestamp")
                    if tx_time and tx_time.tzinfo is None:
                        tx_time = tx_time.replace(tzinfo=timezone.utc)
                    # Forward time constraint: tx_time must be >= current path time (or within window)
                    time_diff = (tx_time - reference_time).total_seconds() / 3600.0 if tx_time else 0.0
                    
                    if tx_time and time_diff > lookahead_hours:
                        window_exceeded = True
                        continue
                    if tx_time and tx_time < curr_time - timedelta(minutes=5):  # allow 5 min clock skew
                        continue
                        
                    candidates.append((u, v, key, data, tx_time, "FORWARD"))
                    
            if direction in ("BACKWARD", "BIDIRECTIONAL"):
                for u, v, key, data in G.in_edges(curr_node, keys=True, data=True):
                    tx_time = data.get("timestamp")
                    if tx_time and tx_time.tzinfo is None:
                        tx_time = tx_time.replace(tzinfo=timezone.utc)
                    time_diff = (reference_time - tx_time).total_seconds() / 3600.0 if tx_time else 0.0
                    
                    if tx_time and time_diff > lookback_hours:
                        window_exceeded = True
                        continue
                    if tx_time and tx_time > curr_time + timedelta(minutes=5):
                        continue
                        
                    candidates.append((u, v, key, data, tx_time, "BACKWARD"))
                    
            if not candidates and len(curr_path) > 1:
                paths.append(curr_path)
                
            # Sort candidates chronologically for deterministic forward progress
            candidates.sort(key=lambda x: x[4] if x[4] else datetime.min.replace(tzinfo=timezone.utc))
            
            for u, v, key, data, tx_time, d in candidates:
                next_node = v if d == "FORWARD" else u
                edge_id = data.get("tx_id", f"{u}->{v}:{key}")
                
                # Cycle prevention: don't loop back to any node already in current path
                if next_node in curr_path:
                    continue
                    
                collected_edges[edge_id] = {
                    "id": edge_id,
                    "source": u,
                    "target": v,
                    "amount": float(data.get("amount", 0.0)),
                    "timestamp": tx_time.isoformat() if tx_time else None,
                    "channel": data.get("channel", "UPI"),
                    "tx_hash": data.get("tx_hash", edge_id),
                    "has_lineage": bool(data.get("has_lineage", False))
                }
                total_volume += float(data.get("amount", 0.0))
                visited_nodes.add(next_node)
                
                new_path = curr_path + [next_node]
                queue.append((next_node, curr_hop + 1, tx_time or curr_time, new_path))

        # Evaluate final stop reason if not explicitly set
        if reached_offramp:
            stop_reason = "OFF_RAMP_REACHED"
        elif exhausted_budget:
            stop_reason = "SEARCH_BUDGET_EXHAUSTED"
        elif not collected_edges:
            if window_exceeded:
                stop_reason = "LOOKBACK_OR_LOOKAHEAD_WINDOW_EXCEEDED"
            else:
                stop_reason = "NO_ELIGIBLE_INCOMING_OR_OUTGOING_TRANSACTIONS"
        elif any(len(p) - 1 >= max_hops for p in paths):
            stop_reason = "MAX_HOPS_REACHED"
        elif window_exceeded:
            stop_reason = "LOOKBACK_OR_LOOKAHEAD_WINDOW_EXCEEDED"
        else:
            stop_reason = "NO_ELIGIBLE_INCOMING_OR_OUTGOING_TRANSACTIONS"

        # Assemble graph nodes
        nodes_result = []
        for n_id in visited_nodes:
            nd = G.nodes.get(n_id, {})
            nodes_result.append({
                "id": n_id,
                "account_number": nd.get("account_number", n_id),
                "holder_name": nd.get("holder_name", "Unknown Holder"),
                "bank_name": nd.get("bank_name", "Synthetic Bank"),
                "bank_swift": nd.get("bank_swift", "MULEINBB"),
                "account_type": nd.get("account_type", "CHECKING"),
                "risk_score": float(nd.get("risk_score", 0.0)),
                "risk_tier": nd.get("risk_tier", "LOW"),
                "is_start": (n_id == start_account_id),
                "is_offramp": nd.get("account_type") in offramp_types
            })
            
        return {
            "start_account_id": start_account_id,
            "direction": direction,
            "max_hops": max_hops,
            "stop_reason": stop_reason,
            "stop_reason_description": self.STOP_REASONS.get(stop_reason, stop_reason),
            "nodes": nodes_result,
            "edges": list(collected_edges.values()),
            "paths": paths[:20],  # cap to top 20 representative paths
            "total_volume_traced": round(total_volume, 2),
            "nodes_count": len(nodes_result),
            "edges_count": len(collected_edges)
        }

