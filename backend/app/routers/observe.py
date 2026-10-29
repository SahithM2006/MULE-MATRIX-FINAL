from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from app.database import get_db
from app.models.entities import SyntheticInstitution, Account, Transaction, Alert, ScenarioDefinition
from app.schemas.observe import SentinelSummary, TransactionItem, AlertItem

router = APIRouter(prefix="/observe", tags=["Observe"])

@router.get("/sentinel", response_model=SentinelSummary)
def get_sentinel_summary(db: Session = Depends(get_db)):
    total_accs = db.query(Account).count()
    total_txs = db.query(Transaction).count()
    total_insts = db.query(SyntheticInstitution).count()
    
    active_alerts = db.query(Alert).filter(Alert.status.in_(["OPEN", "INVESTIGATING"])).count()
    critical_alerts = db.query(Alert).filter(Alert.severity == "CRITICAL", Alert.status.in_(["OPEN", "INVESTIGATING"])).count()
    high_risk_accs = db.query(Account).filter(Account.is_mule == True).count()
    
    vol_res = db.query(func.sum(Transaction.amount)).scalar() or 0.0
    
    recent_alerts_objs = db.query(Alert).order_by(Alert.created_at.desc()).limit(8).all()
    recent_alerts = []
    for a in recent_alerts_objs:
        recent_alerts.append({
            "id": a.id,
            "account_id": a.account_id,
            "account_number": a.account.account_number if a.account else "N/A",
            "holder_name": a.account.holder_name if a.account else "N/A",
            "severity": a.severity,
            "alert_type": a.alert_type,
            "title": a.title,
            "description": a.description,
            "status": a.status,
            "created_at": a.created_at.isoformat()
        })
        
    scenarios_objs = db.query(ScenarioDefinition).order_by(ScenarioDefinition.created_at.desc()).limit(5).all()
    active_scenarios = [{
        "id": s.id,
        "name": s.name,
        "scenario_type": s.scenario_type,
        "seed": s.seed,
        "created_at": s.created_at.isoformat()
    } for s in scenarios_objs]
    
    return SentinelSummary(
        total_accounts=total_accs,
        total_transactions=total_txs,
        total_institutions=total_insts,
        active_alerts_count=active_alerts,
        critical_alerts_count=critical_alerts,
        high_risk_accounts_count=high_risk_accs,
        total_volume_inr=round(float(vol_res), 2),
        recent_alerts=recent_alerts,
        active_scenarios=active_scenarios
    )

@router.get("/transactions", response_model=List[TransactionItem])
def get_transactions(
    account_id: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    channel: Optional[str] = None,
    status: Optional[str] = None,
    has_lineage: Optional[bool] = None,
    scenario_id: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction)
    
    if account_id:
        query = query.filter(or_(
            Transaction.source_account_id == account_id,
            Transaction.dest_account_id == account_id
        ))
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    if channel:
        query = query.filter(Transaction.channel == channel)
    if status:
        query = query.filter(Transaction.status == status)
    if has_lineage is not None:
        query = query.filter(Transaction.has_token_lineage == has_lineage)
    if scenario_id:
        query = query.filter(Transaction.scenario_id == scenario_id)
        
    txs = query.order_by(Transaction.timestamp.desc()).offset(offset).limit(limit).all()
    
    results = []
    for tx in txs:
        src = tx.source_account
        dst = tx.dest_account
        
        # Risk flag if involves known mule or off-ramp
        risk_flag = None
        if src and src.is_mule:
            risk_flag = f"SOURCE_MULE ({src.mule_role})"
        elif dst and dst.is_mule:
            risk_flag = f"DEST_MULE ({dst.mule_role})"
        elif dst and dst.account_type == "CRYPTO_OFFRAMP":
            risk_flag = "OFFRAMP_EXIT"
            
        results.append(TransactionItem(
            id=tx.id,
            tx_hash=tx.tx_hash,
            scenario_id=tx.scenario_id,
            source_account_id=tx.source_account_id,
            source_account_number=src.account_number if src else None,
            source_holder=src.holder_name if src else None,
            source_bank=src.institution.name if src and src.institution else None,
            dest_account_id=tx.dest_account_id,
            dest_account_number=dst.account_number if dst else None,
            dest_holder=dst.holder_name if dst else None,
            dest_bank=dst.institution.name if dst and dst.institution else None,
            amount=float(tx.amount),
            currency=tx.currency,
            timestamp=tx.timestamp,
            status=tx.status,
            channel=tx.channel,
            description=tx.description,
            has_token_lineage=tx.has_token_lineage,
            risk_flag=risk_flag
        ))
    return results

@router.get("/alerts", response_model=List[AlertItem])
def get_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
        
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    results = []
    for a in alerts:
        results.append(AlertItem(
            id=a.id,
            account_id=a.account_id,
            account_number=a.account.account_number if a.account else "N/A",
            holder_name=a.account.holder_name if a.account else "Unknown",
            bank_name=a.account.institution.name if a.account and a.account.institution else "Synthetic Bank",
            transaction_id=a.transaction_id,
            severity=a.severity,
            alert_type=a.alert_type,
            title=a.title,
            description=a.description,
            status=a.status,
            created_at=a.created_at
        ))
    return results

@router.get("/accounts")
def get_accounts(
    query: Optional[str] = None,
    account_type: Optional[str] = None,
    is_mule: Optional[bool] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    q = db.query(Account)
    if query:
        q = q.filter(or_(
            Account.account_number.contains(query),
            Account.holder_name.contains(query)
        ))
    if account_type:
        q = q.filter(Account.account_type == account_type)
    if is_mule is not None:
        q = q.filter(Account.is_mule == is_mule)
        
    accs = q.order_by(Account.id.asc()).offset(offset).limit(limit).all()
    return [{
        "id": a.id,
        "account_number": a.account_number,
        "holder_name": a.holder_name,
        "account_type": a.account_type,
        "bank_name": a.institution.name if a.institution else "Bank",
        "balance": a.balance,
        "status": a.status,
        "is_mule": a.is_mule,
        "mule_role": a.mule_role
    } for a in accs]

