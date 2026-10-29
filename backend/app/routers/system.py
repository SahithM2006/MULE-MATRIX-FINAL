from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import Account, Transaction, SyntheticInstitution, Alert, IncidentCase
from app.algorithms.isolation_forest import IsolationForestEngine
from app.algorithms.graphsage_engine import GraphSAGEEngine
from app.algorithms.louvain_engine import LouvainCommunityEngine
from app.services.scenario_generator import ScenarioGenerator

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/health")
def get_system_health(db: Session = Depends(get_db)):
    iso_engine = IsolationForestEngine()
    gs_engine = GraphSAGEEngine()
    louvain_engine = LouvainCommunityEngine()
    
    return {
        "status": "HEALTHY",
        "backend": "ONLINE",
        "database": {
            "type": "SQLite",
            "accounts_count": db.query(Account).count(),
            "transactions_count": db.query(Transaction).count(),
            "institutions_count": db.query(SyntheticInstitution).count(),
            "alerts_count": db.query(Alert).count(),
            "cases_count": db.query(IncidentCase).count()
        },
        "engines": {
            "velocity_engine": "READY",
            "lineage_verifier": "READY",
            "bfs_tracer": "READY",
            "feature_extractor": "READY",
            "rule_engine": "READY",
            "isolation_forest": iso_engine.status,
            "louvain_community": louvain_engine.status,
            "graphsage_engine": gs_engine.status
        }
    }

@router.post("/seed")
def seed_dataset(db: Session = Depends(get_db)):
    result = ScenarioGenerator.generate_full_seeded_dataset(db, total_accounts=1500, total_transactions=30000, seed=42)
    return result

