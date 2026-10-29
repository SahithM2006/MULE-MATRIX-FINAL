from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import ScenarioDefinition, Transaction, Account
from app.schemas.simulator import ScenarioGenerateRequest, ScenarioInfo
from app.services.scenario_generator import ScenarioGenerator
from app.services.audit_service import AuditService

router = APIRouter(prefix="/simulator", tags=["Simulator"])

@router.get("/scenarios", response_model=List[ScenarioInfo])
def list_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(ScenarioDefinition).order_by(ScenarioDefinition.created_at.desc()).all()
    results = []
    for s in scenarios:
        tx_count = db.query(Transaction).filter_by(scenario_id=s.id).count()
        results.append(ScenarioInfo(
            id=s.id,
            name=s.name,
            scenario_type=s.scenario_type,
            description=s.description or "",
            seed=s.seed,
            created_at=s.created_at,
            transactions_count=tx_count,
            accounts_count=20
        ))
    return results

@router.post("/generate", response_model=ScenarioInfo, status_code=status.HTTP_201_CREATED)
def generate_scenario(req: ScenarioGenerateRequest, db: Session = Depends(get_db)):
    scen = ScenarioGenerator.generate_custom_scenario(
        db=db,
        scenario_type=req.scenario_type,
        seed=req.seed,
        name_prefix=req.name_prefix
    )
    
    AuditService.record_event(
        db=db,
        event_type="SCENARIO_GENERATED",
        action_details=f"Injected synthetic scenario '{scen.name}' (Type: {scen.scenario_type}, Seed: {scen.seed})",
        actor="Scenario Simulator",
        target_type="SCENARIO",
        target_id=scen.id
    )
    
    tx_count = db.query(Transaction).filter_by(scenario_id=scen.id).count()
    return ScenarioInfo(
        id=scen.id,
        name=scen.name,
        scenario_type=scen.scenario_type,
        description=scen.description or "",
        seed=scen.seed,
        created_at=scen.created_at,
        transactions_count=tx_count,
        accounts_count=req.accounts_count
    )

