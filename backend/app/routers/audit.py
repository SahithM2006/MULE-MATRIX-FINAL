from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import AuditEvent
from app.schemas.audit import AuditEventItem, AuditIntegrityReport
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/events", response_model=List[AuditEventItem])
def get_audit_events(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc(), AuditEvent.id.desc()).offset(offset).limit(limit).all()
    results = []
    for ev in events:
        results.append(AuditEventItem(
            id=ev.id,
            event_type=ev.event_type,
            actor=ev.actor,
            target_type=ev.target_type,
            target_id=ev.target_id,
            action_details=ev.action_details,
            previous_hash=ev.previous_hash,
            current_hash=ev.current_hash,
            timestamp=ev.timestamp,
            success=ev.success
        ))
    return results

@router.get("/verify", response_model=AuditIntegrityReport)
def verify_audit_chain(db: Session = Depends(get_db)):
    res = AuditService.verify_ledger(db=db)
    return AuditIntegrityReport(**res)

