import json
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import IncidentCase, CaseNote, CaseStatusEvent, EvidenceArtifact, Account
from app.schemas.respond import (
    CaseCreate, CaseUpdate, CaseNoteCreate, CaseDetail,
    CaseNoteItem, CaseStatusEventItem, EvidenceExportResponse
)
from app.services.case_service import CaseService
from app.routers.detect import get_account_risk_profile
from app.routers.trace import run_bfs_trace
from app.schemas.trace import TraceRequest

router = APIRouter(prefix="/respond", tags=["Respond"])

@router.get("/cases", response_model=List[CaseDetail])
def list_cases(status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(IncidentCase)
    if status_filter:
        q = q.filter(IncidentCase.status == status_filter)
        
    cases = q.order_by(IncidentCase.created_at.desc()).all()
    results = []
    for c in cases:
        acc = c.primary_account
        results.append(CaseDetail(
            id=c.id,
            case_number=c.case_number,
            title=c.title,
            status=c.status,
            priority=c.priority,
            primary_account_id=c.primary_account_id,
            primary_account_number=acc.account_number if acc else None,
            primary_holder_name=acc.holder_name if acc else None,
            primary_bank_name=acc.institution.name if acc and acc.institution else None,
            assigned_to=c.assigned_to,
            findings_summary=c.findings_summary,
            created_at=c.created_at,
            updated_at=c.updated_at,
            notes=[CaseNoteItem(id=n.id, case_id=n.case_id, author=n.author, note_text=n.note_text, created_at=n.created_at) for n in c.notes],
            status_events=[CaseStatusEventItem(id=e.id, case_id=e.case_id, old_status=e.old_status, new_status=e.new_status, changed_by=e.changed_by, reason=e.reason, created_at=e.created_at) for e in c.status_events],
            artifacts=[{"id": a.id, "type": a.artifact_type, "title": a.title, "hash": a.content_hash} for a in c.artifacts]
        ))
    return results

@router.post("/cases", response_model=CaseDetail, status_code=status.HTTP_201_CREATED)
def create_case(req: CaseCreate, db: Session = Depends(get_db)):
    acc = db.query(Account).filter_by(id=req.primary_account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail=f"Primary account '{req.primary_account_id}' not found.")
        
    new_case = CaseService.create_case(
        db=db,
        title=req.title,
        primary_account_id=req.primary_account_id,
        priority=req.priority,
        assigned_to=req.assigned_to,
        findings_summary=req.findings_summary
    )
    return get_case_detail(case_id=new_case.id, db=db)

@router.get("/cases/{case_id}", response_model=CaseDetail)
def get_case_detail(case_id: str, db: Session = Depends(get_db)):
    c = db.query(IncidentCase).filter_by(id=case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")
        
    acc = c.primary_account
    return CaseDetail(
        id=c.id,
        case_number=c.case_number,
        title=c.title,
        status=c.status,
        priority=c.priority,
        primary_account_id=c.primary_account_id,
        primary_account_number=acc.account_number if acc else None,
        primary_holder_name=acc.holder_name if acc else None,
        primary_bank_name=acc.institution.name if acc and acc.institution else None,
        assigned_to=c.assigned_to,
        findings_summary=c.findings_summary,
        created_at=c.created_at,
        updated_at=c.updated_at,
        notes=[CaseNoteItem(id=n.id, case_id=n.case_id, author=n.author, note_text=n.note_text, created_at=n.created_at) for n in c.notes],
        status_events=[CaseStatusEventItem(id=e.id, case_id=e.case_id, old_status=e.old_status, new_status=e.new_status, changed_by=e.changed_by, reason=e.reason, created_at=e.created_at) for e in c.status_events],
        artifacts=[{"id": a.id, "type": a.artifact_type, "title": a.title, "hash": a.content_hash} for a in c.artifacts]
    )

@router.post("/cases/{case_id}/notes", response_model=CaseNoteItem)
def add_case_note(case_id: str, note_in: CaseNoteCreate, db: Session = Depends(get_db)):
    case = db.query(IncidentCase).filter_by(id=case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")
        
    note = CaseService.add_note(db=db, case_id=case_id, author=note_in.author, note_text=note_in.note_text)
    return CaseNoteItem(
        id=note.id,
        case_id=note.case_id,
        author=note.author,
        note_text=note.note_text,
        created_at=note.created_at
    )

@router.patch("/cases/{case_id}/status", response_model=CaseDetail)
def update_case_status(case_id: str, update: CaseUpdate, db: Session = Depends(get_db)):
    if not update.status:
        raise HTTPException(status_code=400, detail="New status must be provided.")
        
    case = CaseService.update_status(
        db=db,
        case_id=case_id,
        new_status=update.status,
        changed_by=update.assigned_to or "Lead Investigator",
        reason=update.status_change_reason
    )
    return get_case_detail(case_id=case.id, db=db)

@router.post("/cases/{case_id}/export", response_model=EvidenceExportResponse)
def export_evidence_dossier(case_id: str, db: Session = Depends(get_db)):
    case = db.query(IncidentCase).filter_by(id=case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")
        
    # Gather active detection and trace data for the case
    acc_risk = get_account_risk_profile(account_id=case.primary_account_id, db=db)
    trace_res = run_bfs_trace(TraceRequest(account_id=case.primary_account_id, direction="BIDIRECTIONAL", max_hops=4), db=db)
    
    dossier_data = {
        "composite_risk_score": acc_risk.composite_risk_score,
        "risk_tier": acc_risk.risk_tier,
        "narrative_explanation": acc_risk.narrative_explanation,
        "signals": [s.model_dump() for s in acc_risk.signals],
        "feature_metrics": acc_risk.feature_metrics,
        "nodes_count": trace_res.nodes_count,
        "edges_count": trace_res.edges_count,
        "stop_reason": trace_res.stop_reason,
        "stop_reason_description": trace_res.stop_reason_description,
        "paths": trace_res.paths
    }
    
    export_res = CaseService.generate_dossier(db=db, case_id=case.id, dossier_data=dossier_data)
    return EvidenceExportResponse(**export_res)

@router.get("/evidence/{artifact_id}/download")
def download_evidence_artifact(artifact_id: str, db: Session = Depends(get_db)):
    artifact = db.query(EvidenceArtifact).filter_by(id=artifact_id).first()
    if not artifact or not artifact.file_path:
        raise HTTPException(status_code=404, detail="Artifact file not found.")
        
    p = Path(artifact.file_path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="File on disk not found.")
        
    media_type = "text/html" if p.suffix == ".html" else "application/json"
    return FileResponse(path=str(p), filename=p.name, media_type=media_type)

