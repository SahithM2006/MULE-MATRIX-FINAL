import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.entities import (
    IncidentCase, CaseNote, CaseStatusEvent, EvidenceArtifact,
    Account, Transaction, DetectionResult, AuditEvent, utc_now
)
from app.config import settings
from app.services.audit_service import AuditService

EXPORT_DIR = settings.DATA_DIR / "evidence_vault"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

class CaseService:
    """
    Incident Response and Evidence Vault Service
    Manages investigative cases, notes, state transitions, and generates
    verifiable standalone HTML and JSON forensic dossiers with cryptographic hashes.
    """

    @classmethod
    def create_case(
        cls,
        db: Session,
        title: str,
        primary_account_id: str,
        priority: str = "HIGH",
        assigned_to: str = "Financial Crime Unit",
        findings_summary: Optional[str] = None
    ) -> IncidentCase:
        count = db.query(IncidentCase).count()
        case_num = f"CASE-2026-{count+1:04d}"
        
        case_id = f"case_{int(utc_now().timestamp())}_{count+1}"
        new_case = IncidentCase(
            id=case_id,
            case_number=case_num,
            title=title,
            status="NEW",
            priority=priority,
            primary_account_id=primary_account_id,
            assigned_to=assigned_to,
            findings_summary=findings_summary or "Preliminary investigation opened based on algorithmic risk detection."
        )
        db.add(new_case)
        db.commit()
        db.refresh(new_case)
        
        # Log status event
        st_event = CaseStatusEvent(
            id=f"cse_{new_case.id}_init",
            case_id=new_case.id,
            old_status="NONE",
            new_status="NEW",
            changed_by=assigned_to,
            reason="Case initialization"
        )
        db.add(st_event)
        db.commit()
        
        # Record tamper-evident audit
        AuditService.record_event(
            db=db,
            event_type="CASE_CREATED",
            action_details=f"Opened incident case {case_num} for account {primary_account_id}",
            actor=assigned_to,
            target_type="CASE",
            target_id=new_case.id
        )
        return new_case

    @classmethod
    def add_note(cls, db: Session, case_id: str, author: str, note_text: str) -> CaseNote:
        note = CaseNote(
            id=f"note_{int(utc_now().timestamp()*1000)}",
            case_id=case_id,
            author=author,
            note_text=note_text
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        
        AuditService.record_event(
            db=db,
            event_type="NOTE_ADDED",
            action_details=f"Added investigative note to case {case_id}",
            actor=author,
            target_type="CASE",
            target_id=case_id
        )
        return note

    @classmethod
    def update_status(
        cls,
        db: Session,
        case_id: str,
        new_status: str,
        changed_by: str,
        reason: Optional[str] = None
    ) -> IncidentCase:
        case = db.query(IncidentCase).filter_by(id=case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found.")
            
        old_status = case.status
        case.status = new_status
        case.updated_at = utc_now()
        
        st_event = CaseStatusEvent(
            id=f"cse_{int(utc_now().timestamp()*1000)}",
            case_id=case.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            reason=reason or f"Status transition from {old_status} to {new_status}"
        )
        db.add(st_event)
        db.commit()
        db.refresh(case)
        
        AuditService.record_event(
            db=db,
            event_type="CASE_STATUS_UPDATED",
            action_details=f"Transitioned case {case.case_number} status: {old_status} -> {new_status} (Reason: {reason})",
            actor=changed_by,
            target_type="CASE",
            target_id=case.id
        )
        return case

    @classmethod
    def generate_dossier(cls, db: Session, case_id: str, dossier_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds standalone HTML and JSON forensic evidence packages.
        Computes SHA-256 digest and records into evidence_artifacts and audit ledger.
        """
        case = db.query(IncidentCase).filter_by(id=case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found.")
            
        primary_acc = db.query(Account).filter_by(id=case.primary_account_id).first()
        
        # 1. Create JSON Dossier
        json_filename = f"dossier_{case.case_number}.json"
        json_path = EXPORT_DIR / json_filename
        
        package_payload = {
            "case_number": case.case_number,
            "title": case.title,
            "status": case.status,
            "priority": case.priority,
            "primary_account": {
                "id": primary_acc.id if primary_acc else None,
                "account_number": primary_acc.account_number if primary_acc else None,
                "holder_name": primary_acc.holder_name if primary_acc else None,
                "bank": primary_acc.institution.name if primary_acc and primary_acc.institution else None
            },
            "findings_summary": case.findings_summary,
            "generated_at": utc_now().isoformat(),
            "analysis": dossier_data,
            "legal_disclaimer": "This forensic evidence package was compiled by MULE MATRIX. Analytical risk scores, GraphSAGE predictions, and BFS flow reconstructions are derived from deterministic multi-bank algorithmic engines."
        }
        
        json_content = json.dumps(package_payload, indent=2)
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_content)
            
        json_hash = hashlib.sha256(json_content.encode('utf-8')).hexdigest()
        
        # 2. Create Swiss Editorial HTML Dossier
        html_filename = f"dossier_{case.case_number}.html"
        html_path = EXPORT_DIR / html_filename
        
        html_content = cls._render_editorial_html_dossier(case, primary_acc, dossier_data, json_hash)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        html_hash = hashlib.sha256(html_content.encode('utf-8')).hexdigest()
        
        # Save artifact record
        artifact = EvidenceArtifact(
            id=f"art_{int(utc_now().timestamp()*1000)}",
            case_id=case.id,
            artifact_type="HTML_DOSSIER",
            title=f"Forensic Evidence Dossier - {case.case_number}",
            file_path=str(html_path),
            content_hash=html_hash,
            metadata_json=json.dumps({"json_hash": json_hash, "file_name": html_filename})
        )
        db.add(artifact)
        db.commit()
        
        AuditService.record_event(
            db=db,
            event_type="EVIDENCE_EXPORTED",
            action_details=f"Exported evidence dossier for {case.case_number} (SHA256: {html_hash[:16]}...)",
            actor="Evidence Vault",
            target_type="CASE",
            target_id=case.id
        )
        
        return {
            "case_id": case.id,
            "case_number": case.case_number,
            "artifact_id": artifact.id,
            "artifact_type": "HTML_DOSSIER",
            "file_path": str(html_path),
            "content_hash": html_hash,
            "dossier_summary": {
                "json_path": str(json_path),
                "json_hash": json_hash,
                "html_path": str(html_path),
                "html_hash": html_hash
            },
            "download_url": f"/api/v1/respond/evidence/{artifact.id}/download"
        }

    @classmethod
    def _render_editorial_html_dossier(
        cls,
        case: IncidentCase,
        primary_acc: Optional[Account],
        data: Dict[str, Any],
        json_hash: str
    ) -> str:
        signals = data.get("signals", [])
        risk_score = data.get("composite_risk_score", 0.0)
        risk_tier = data.get("risk_tier", "MEDIUM")
        narrative = data.get("narrative_explanation", case.findings_summary or "")
        nodes_count = data.get("nodes_count", 0)
        edges_count = data.get("edges_count", 0)
        stop_reason = data.get("stop_reason", "OFF_RAMP_REACHED")
        
        signals_rows = ""
        for s in signals:
            status_color = "#C83232" if s.get("status") == "SUSPICIOUS" else "#7596C8"
            signals_rows += f"""
            <tr style="border-bottom: 1px solid #E5E0D5;">
                <td style="padding: 10px 12px; font-family: 'SF Pro Text', -apple-system, sans-serif; font-weight: 600;">{s.get('engine_name')}</td>
                <td style="padding: 10px 12px; font-family: monospace; color: {status_color}; font-weight: bold;">{s.get('status')}</td>
                <td style="padding: 10px 12px; font-family: monospace;">{s.get('score', 0):.1f}/100</td>
                <td style="padding: 10px 12px; font-family: monospace;">{s.get('weight', 0)*100:.1f}%</td>
                <td style="padding: 10px 12px; color: #444; font-size: 13px;">{s.get('summary')}</td>
            </tr>
            """
            
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>MULE MATRIX Forensic Evidence Dossier · {case.case_number}</title>
<style>
    body {{
        background-color: #F4F1E9;
        color: #111111;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        margin: 0;
        padding: 40px;
    }}
    .dossier-card {{
        max-width: 900px;
        margin: 0 auto;
        background: #FFFFFF;
        border: 1px solid #D8D2C4;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        padding: 48px;
    }}
    .header-rule {{
        border-top: 3px solid #111111;
        margin-bottom: 24px;
    }}
    h1 {{
        font-family: "Georgia", serif;
        font-size: 28px;
        font-weight: 700;
        margin: 0 0 8px 0;
        letter-spacing: -0.5px;
    }}
    .case-subhead {{
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #858585;
        margin-bottom: 24px;
    }}
    .meta-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        padding: 16px 0;
        border-top: 1px solid #E5E0D5;
        border-bottom: 1px solid #E5E0D5;
        margin-bottom: 28px;
    }}
    .meta-item label {{
        font-size: 11px;
        text-transform: uppercase;
        color: #858585;
        letter-spacing: 1px;
        display: block;
        margin-bottom: 4px;
    }}
    .meta-item span {{
        font-weight: 600;
        font-size: 15px;
    }}
    .score-badge {{
        display: inline-block;
        padding: 6px 14px;
        background: {'#C83232' if risk_score >= 50 else '#C6A45A'};
        color: white;
        font-weight: 700;
        font-size: 16px;
        border-radius: 2px;
    }}
    .editorial-section {{
        margin-bottom: 32px;
    }}
    h2 {{
        font-family: "Georgia", serif;
        font-size: 18px;
        margin: 0 0 12px 0;
        border-bottom: 1px solid #111111;
        padding-bottom: 6px;
    }}
    p {{
        line-height: 1.6;
        font-size: 14px;
        color: #222222;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        margin-top: 8px;
    }}
    th {{
        text-align: left;
        padding: 8px 12px;
        background: #F4F1E9;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        border-bottom: 1px solid #D8D2C4;
    }}
    .hash-footer {{
        margin-top: 40px;
        padding-top: 16px;
        border-top: 1px dashed #A09A8E;
        font-family: monospace;
        font-size: 11px;
        color: #666666;
    }}
</style>
</head>
<body>
<div class="dossier-card">
    <div class="header-rule"></div>
    <div class="case-subhead">MULE MATRIX · Forensic Financial Investigation Dossier</div>
    <h1>{case.title}</h1>
    
    <div class="meta-grid">
        <div class="meta-item">
            <label>Case Number</label>
            <span>{case.case_number}</span>
        </div>
        <div class="meta-item">
            <label>Current Status</label>
            <span>{case.status}</span>
        </div>
        <div class="meta-item">
            <label>Risk Assessment</label>
            <span class="score-badge">{risk_score:.1f} / 100 ({risk_tier})</span>
        </div>
        <div class="meta-item">
            <label>Investigator</label>
            <span>{case.assigned_to}</span>
        </div>
    </div>

    <div class="editorial-section">
        <h2>Target Entity Profile</h2>
        <p><strong>Account Number:</strong> {primary_acc.account_number if primary_acc else 'N/A'}<br>
           <strong>Account Holder:</strong> {primary_acc.holder_name if primary_acc else 'N/A'}<br>
           <strong>Institution:</strong> {primary_acc.institution.name if primary_acc and primary_acc.institution else 'N/A'} ({primary_acc.institution.swift_bic if primary_acc and primary_acc.institution else 'N/A'})<br>
           <strong>Account Type:</strong> {primary_acc.account_type if primary_acc else 'N/A'} · <strong>Status:</strong> {primary_acc.status if primary_acc else 'ACTIVE'}</p>
    </div>

    <div class="editorial-section">
        <h2>Investigative Narrative & Analytical Synthesis</h2>
        <p>{narrative}</p>
    </div>

    <div class="editorial-section">
        <h2>Multi-Engine Algorithmic Evidence Matrix</h2>
        <table>
            <thead>
                <tr>
                    <th>Algorithmic Engine</th>
                    <th>Signal Status</th>
                    <th>Raw Score</th>
                    <th>Normalized Weight</th>
                    <th>Observed Findings</th>
                </tr>
            </thead>
            <tbody>
                {signals_rows}
            </tbody>
        </table>
    </div>

    <div class="editorial-section">
        <h2>Graph Traversal & Lineage Boundaries</h2>
        <p><strong>Traversal Scope:</strong> {nodes_count} nodes analyzed, {edges_count} edges tracked.<br>
           <strong>Terminal Stop Reason:</strong> <code>{stop_reason}</code><br>
           <em>Methodology Note: Money flows represent chronological graph traversals through banking rails; transactions are validated against temporal ordering.</em></p>
    </div>

    <div class="hash-footer">
        <strong>CRYPTOGRAPHIC EVIDENCE AUTHENTICATION</strong><br>
        Companion JSON Digest: <code>{json_hash}</code><br>
        Export Timestamp: {utc_now().isoformat()} · Generated by MULE MATRIX Core v1.0
    </div>
</div>
</body>
</html>"""

