from typing import Optional, Dict, Any
import networkx as nx
from sqlalchemy.orm import Session
from app.models.entities import Account, Transaction, SyntheticInstitution

class GraphService:
    """
    Manages in-memory NetworkX directed multigraph representation of multi-bank transactions.
    Provides fast graph querying and cached views with deterministic invalidation.
    """
    
    _cached_graph: Optional[nx.MultiDiGraph] = None
    _last_tx_count: int = 0
    
    @classmethod
    def get_graph(cls, db: Session, force_reload: bool = False) -> nx.MultiDiGraph:
        tx_count = db.query(Transaction).count()
        if cls._cached_graph is not None and not force_reload and tx_count == cls._last_tx_count:
            return cls._cached_graph
            
        G = nx.MultiDiGraph()
        
        # Load all synthetic institutions
        institutions = {inst.id: inst for inst in db.query(SyntheticInstitution).all()}
        
        # Load all accounts
        accounts = db.query(Account).all()
        for acc in accounts:
            inst = institutions.get(acc.institution_id)
            G.add_node(
                acc.id,
                account_number=acc.account_number,
                holder_name=acc.holder_name,
                bank_name=inst.name if inst else "Unknown Bank",
                bank_swift=inst.swift_bic if inst else "MULEINBB",
                account_type=acc.account_type,
                balance=acc.balance,
                status=acc.status,
                is_mule=acc.is_mule,
                risk_score=0.0,
                risk_tier="LOW"
            )
            
        # Load all transactions
        transactions = db.query(Transaction).filter(Transaction.status == "SETTLED").all()
        for tx in transactions:
            G.add_edge(
                tx.source_account_id,
                tx.dest_account_id,
                key=tx.id,
                tx_id=tx.id,
                tx_hash=tx.tx_hash,
                amount=float(tx.amount),
                timestamp=tx.timestamp,
                channel=tx.channel,
                has_lineage=tx.has_token_lineage,
                scenario_id=tx.scenario_id
            )
            
        cls._cached_graph = G
        cls._last_tx_count = tx_count
        return G

    @classmethod
    def invalidate_cache(cls):
        cls._cached_graph = None
        cls._last_tx_count = 0

