import math
from typing import Dict, Any, List, Optional
import networkx as nx
import numpy as np

class FeatureExtractor:
    """
    Algorithm 4: Graph-Feature Extraction Engine
    Extracts structural topological and flow-based metrics for accounts.
    Guarantees strict zero-division safety, NaN prevention, and numeric consistency
    across Detection Lab, Isolation Forest, and GraphSAGE models.
    """
    
    FEATURE_NAMES = [
        "in_degree",
        "out_degree",
        "total_inflow",
        "total_outflow",
        "fan_in",
        "fan_out",
        "degree_ratio",
        "clustering_coeff",
        "component_size",
        "velocity_24h",
        "pass_through_ratio",
        "burst_score"
    ]
    
    @classmethod
    def extract_features(cls, G: nx.MultiDiGraph, account_id: str) -> Dict[str, float]:
        if account_id not in G:
            return {name: 0.0 for name in cls.FEATURE_NAMES}
            
        # Feature caching for high-speed graph operations
        if not hasattr(G, "graph") or G.graph is None:
            G.graph = {}
        if "_features_cache" not in G.graph:
            G.graph["_features_cache"] = {}
        if account_id in G.graph["_features_cache"]:
            return dict(G.graph["_features_cache"][account_id])

        in_edges = list(G.in_edges(account_id, data=True))
        out_edges = list(G.out_edges(account_id, data=True))
        
        in_degree = len(in_edges)
        out_degree = len(out_edges)
        
        total_inflow = sum(float(d.get("amount", 0.0)) for _, _, d in in_edges)
        total_outflow = sum(float(d.get("amount", 0.0)) for _, _, d in out_edges)
        
        # Unique counterparties
        in_nbrs = set(u for u, _, _ in in_edges)
        out_nbrs = set(v for _, v, _ in out_edges)
        fan_in = len(in_nbrs)
        fan_out = len(out_nbrs)
        
        # Safe degree ratio
        degree_ratio = float(out_degree) / float(in_degree + 1.0)
        
        # Pass-through ratio: min/max flow
        max_flow = max(total_inflow, total_outflow)
        min_flow = min(total_inflow, total_outflow)
        pass_through_ratio = (min_flow / max_flow) if max_flow > 0.0 else 0.0
        
        # Velocity and burst score from edges
        all_times = []
        for _, _, d in in_edges + out_edges:
            t = d.get("timestamp")
            if t:
                all_times.append(t)
                
        all_times.sort()
        total_txs = in_degree + out_degree
        velocity_24h = float(total_txs)
        
        burst_score = 0.0
        if len(all_times) > 0:
            window_max = 1
            for i in range(len(all_times)):
                cnt = 1
                for j in range(i + 1, len(all_times)):
                    tdiff = (all_times[j] - all_times[i]).total_seconds()
                    if tdiff <= 600.0:
                        cnt += 1
                    else:
                        break
                if cnt > window_max:
                    window_max = cnt
            burst_score = float(window_max)
            
        # Connected component size (cached weakly connected component map)
        if "_wcc_map" not in G.graph:
            try:
                wcc_map = {}
                for comp in nx.weakly_connected_components(G):
                    c_size = float(len(comp))
                    for n in comp:
                        wcc_map[n] = c_size
                G.graph["_wcc_map"] = wcc_map
            except Exception:
                G.graph["_wcc_map"] = {}
        component_size = G.graph["_wcc_map"].get(account_id, 1.0)
            
        # Local clustering coefficient on 1-hop undirected neighborhood
        nbrs = in_nbrs.union(out_nbrs)
        k_nbr = len(nbrs)
        if k_nbr < 2:
            clustering_coeff = 0.0
        else:
            nbrs_sub = list(nbrs)[:25]  # bound check for efficiency
            k_sub = len(nbrs_sub)
            if k_sub < 2:
                clustering_coeff = 0.0
            else:
                links = 0
                for i in range(k_sub):
                    u = nbrs_sub[i]
                    for j in range(i + 1, k_sub):
                        v = nbrs_sub[j]
                        if G.has_edge(u, v) or G.has_edge(v, u):
                            links += 1
                clustering_coeff = float(2.0 * links) / float(k_sub * (k_sub - 1))
            
        def sanitize(val: float) -> float:
            if math.isnan(val) or math.isinf(val):
                return 0.0
            return float(val)
            
        result = {
            "in_degree": float(in_degree),
            "out_degree": float(out_degree),
            "total_inflow": round(sanitize(total_inflow), 2),
            "total_outflow": round(sanitize(total_outflow), 2),
            "fan_in": float(fan_in),
            "fan_out": float(fan_out),
            "degree_ratio": round(sanitize(degree_ratio), 4),
            "clustering_coeff": round(sanitize(clustering_coeff), 4),
            "component_size": float(component_size),
            "velocity_24h": float(velocity_24h),
            "pass_through_ratio": round(sanitize(pass_through_ratio), 4),
            "burst_score": float(burst_score)
        }
        G.graph["_features_cache"][account_id] = result
        return result

    @classmethod
    def to_normalized_vector(cls, features: Dict[str, float]) -> np.ndarray:
        """
        Transforms raw feature dict into a standardized vector for Isolation Forest & GraphSAGE.
        Uses logarithmic scaling for heavy-tailed counts and bounded scaling for ratios.
        """
        vec = [
            math.log1p(max(0.0, features.get("in_degree", 0.0))),
            math.log1p(max(0.0, features.get("out_degree", 0.0))),
            math.log1p(max(0.0, features.get("total_inflow", 0.0))),
            math.log1p(max(0.0, features.get("total_outflow", 0.0))),
            math.log1p(max(0.0, features.get("fan_in", 0.0))),
            math.log1p(max(0.0, features.get("fan_out", 0.0))),
            min(10.0, max(0.0, features.get("degree_ratio", 0.0))),
            min(1.0, max(0.0, features.get("clustering_coeff", 0.0))),
            math.log1p(max(1.0, features.get("component_size", 1.0))),
            math.log1p(max(0.0, features.get("velocity_24h", 0.0))),
            min(1.0, max(0.0, features.get("pass_through_ratio", 0.0))),
            math.log1p(max(0.0, features.get("burst_score", 0.0)))
        ]
        return np.array(vec, dtype=np.float32)
