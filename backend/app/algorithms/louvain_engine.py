from typing import Dict, Any, List, Set, Tuple, Optional
import networkx as nx
import networkx.algorithms.community as nx_comm

class LouvainCommunityEngine:
    """
    Algorithm 7: Seeded Louvain Community Detection Engine
    Projects directed multi-bank flows onto an undirected weighted graph to isolate
    topological clusters, circular mule rings, and modularity partitions.
    """
    
    def __init__(self, seed: int = 42, resolution: float = 1.0):
        self.seed = seed
        self.resolution = resolution
        self.cached_communities: List[Set[str]] = []
        self.node_to_comm: Dict[str, int] = {}
        self.modularity_score: float = 0.0
        self.status: str = "READY"
        
    def project_to_undirected(self, G: nx.MultiDiGraph) -> nx.Graph:
        """
        Projects directed multi-bank transaction graph into a weighted simple undirected graph.
        Edge weight = sum of transaction amounts between pair (min 1.0 to reflect relationship).
        """
        H = nx.Graph()
        for n, data in G.nodes(data=True):
            H.add_node(n, **data)
            
        for u, v, _, data in G.edges(keys=True, data=True):
            amt = float(data.get("amount", 1.0))
            if amt <= 0.0:
                amt = 1.0
            if H.has_edge(u, v):
                H[u][v]["weight"] += amt
                H[u][v]["tx_count"] += 1
            else:
                H.add_edge(u, v, weight=amt, tx_count=1)
                
        return H

    def compute_communities(self, G: nx.MultiDiGraph) -> Dict[str, Any]:
        """
        Computes Louvain modularity communities with deterministic seed.
        """
        if len(G) < 2:
            self.status = "EMPTY_GRAPH"
            return {
                "status": self.status,
                "modularity": 0.0,
                "total_communities": 0,
                "community_sizes": []
            }
            
        H = self.project_to_undirected(G)
        
        try:
            communities = nx_comm.louvain_communities(
                H,
                weight="weight",
                resolution=self.resolution,
                seed=self.seed
            )
            self.cached_communities = communities
            self.node_to_comm = {}
            for comm_id, c_set in enumerate(communities):
                for node_id in c_set:
                    self.node_to_comm[node_id] = comm_id
                    
            # Compute modularity
            try:
                self.modularity_score = float(nx_comm.modularity(H, communities, weight="weight"))
            except Exception:
                self.modularity_score = 0.0
                
            self.status = "READY"
        except Exception as e:
            self.status = "FAILED"
            self.cached_communities = []
            self.node_to_comm = {}
            self.modularity_score = 0.0
            
        return {
            "status": self.status,
            "modularity": round(self.modularity_score, 4),
            "total_communities": len(self.cached_communities),
            "community_sizes": [len(c) for c in self.cached_communities[:10]]
        }

    def analyze_account(self, G: nx.MultiDiGraph, account_id: str) -> Dict[str, Any]:
        """
        Analyzes community context for a specific account.
        """
        if not self.node_to_comm or account_id not in self.node_to_comm:
            self.compute_communities(G)
            
        if account_id not in self.node_to_comm:
            return {
                "community_id": -1,
                "community_size": 1,
                "modularity": 0.0,
                "internal_density": 0.0,
                "is_mule_cluster_candidate": False,
                "community_risk_score": 0.0,
                "disclaimer": "Account not found in active community partition."
            }
            
        comm_id = self.node_to_comm[account_id]
        comm_members = self.cached_communities[comm_id]
        comm_size = len(comm_members)
        
        # Calculate internal vs external edge density
        internal_edges = 0
        total_edges = 0
        for u in comm_members:
            if u in G:
                for _, v in G.out_edges(u):
                    total_edges += 1
                    if v in comm_members:
                        internal_edges += 1
                        
        internal_density = (float(internal_edges) / float(total_edges)) if total_edges > 0 else 0.0
        
        # Mule Ring indicator: tightly closed small-to-medium cluster (3-12 accounts) with very high internal cycling
        is_mule_cluster = bool(3 <= comm_size <= 15 and internal_density >= 0.75)
        
        comm_risk_score = 0.0
        if is_mule_cluster:
            comm_risk_score = 65.0
        elif 3 <= comm_size <= 25 and internal_density >= 0.5:
            comm_risk_score = 30.0
            
        return {
            "community_id": comm_id,
            "community_size": comm_size,
            "modularity": round(self.modularity_score, 4),
            "internal_density": round(internal_density, 3),
            "is_mule_cluster_candidate": is_mule_cluster,
            "community_risk_score": comm_risk_score,
            "disclaimer": "Community membership reflects graph partition structure, not conclusive proof of fraud."
        }

