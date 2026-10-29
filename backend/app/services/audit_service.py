import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.entities import AuditEvent, utc_now

class AuditService:
    """
    Tamper-Evident SHA-256 Audit Ledger Service
    Ensures every critical application event (case changes, trace executions,
    scenario runs, evidence exports) is linked in an immutable cryptographic chain.
    """
    
    GENESIS_HASH = "0" * 64
    
    @classmethod
    def format_timestamp(cls, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def record_event(
        cls,
        db: Session,
        event_type: str,
        action_details: str,
        actor: str = "Financial Investigator",
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        success: bool = True
    ) -> AuditEvent:
        # Fetch last recorded audit event to link previous_hash
        last_event = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc(), AuditEvent.id.desc()).first()
        prev_hash = last_event.current_hash if last_event else cls.GENESIS_HASH
        
        now = utc_now()
        ts_str = cls.format_timestamp(now)
        event_id = f"aud_{int(now.timestamp()*1000)}_{hashlib.md5(f'{event_type}{now}'.encode()).hexdigest()[:8]}"
        
        # Build payload for hash preimage
        preimage_str = f"{prev_hash}|{ts_str}|{event_type}|{actor}|{target_type or ''}|{target_id or ''}|{action_details}|{success}"
        curr_hash = hashlib.sha256(preimage_str.encode('utf-8')).hexdigest()
        
        audit_rec = AuditEvent(
            id=event_id,
            event_type=event_type,
            actor=actor,
            target_type=target_type,
            target_id=target_id,
            action_details=action_details,
            previous_hash=prev_hash,
            current_hash=curr_hash,
            timestamp=now,
            success=success
        )
        db.add(audit_rec)
        db.commit()
        db.refresh(audit_rec)
        return audit_rec

    @classmethod
    def verify_ledger(cls, db: Session) -> Dict[str, Any]:
        """
        Cryptographically verifies the complete audit trail from genesis to latest record.
        """
        events = db.query(AuditEvent).order_by(AuditEvent.timestamp.asc(), AuditEvent.id.asc()).all()
        
        if not events:
            return {
                "is_ledger_intact": True,
                "total_events": 0,
                "first_tampered_index": None,
                "verification_details": "Audit ledger is empty; genesis state intact.",
                "verified_at": utc_now().isoformat()
            }
            
        expected_prev_hash = cls.GENESIS_HASH
        is_intact = True
        first_tampered_idx = None
        detail_msg = "All cryptographic hash links verified successfully."
        
        for idx, ev in enumerate(events):
            # Check previous hash link
            if ev.previous_hash != expected_prev_hash:
                is_intact = False
                first_tampered_idx = idx
                detail_msg = f"Audit link broken at record #{idx} (ID: {ev.id}). Expected prev_hash {expected_prev_hash[:12]}..., got {ev.previous_hash[:12]}..."
                break
                
            # Recompute current hash
            ts_str = cls.format_timestamp(ev.timestamp)
            preimage_str = f"{ev.previous_hash}|{ts_str}|{ev.event_type}|{ev.actor}|{ev.target_type or ''}|{ev.target_id or ''}|{ev.action_details}|{ev.success}"
            recomputed = hashlib.sha256(preimage_str.encode('utf-8')).hexdigest()
            
            if recomputed != ev.current_hash:
                is_intact = False
                first_tampered_idx = idx
                detail_msg = f"Audit content tampering detected at record #{idx} (ID: {ev.id}). Recorded hash {ev.current_hash[:12]}... does not match computed {recomputed[:12]}..."
                break
                
            expected_prev_hash = ev.current_hash
            
        return {
            "is_ledger_intact": is_intact,
            "total_events": len(events),
            "first_tampered_index": first_tampered_idx,
            "verification_details": detail_msg,
            "verified_at": utc_now().isoformat()
        }
