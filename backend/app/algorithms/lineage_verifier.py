import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple

class LineageVerifier:
    """
    Algorithm 2: SHA-256 Cryptographic Token-Lineage Verification
    Verifies cryptographic hash chains for e₹ CBDC / asset token transfers.
    Uses canonical JSON serialization (RFC 8785 conforming) and strict previous-hash integrity checks.
    """
    
    GENESIS_PREV_HASH = "0" * 64
    
    @staticmethod
    def canonical_serialize(payload: Dict[str, Any]) -> str:
        """
        RFC 8785 canonical JSON serializer:
        - Sorted keys
        - No whitespace between tokens
        - UTF-8 encoding
        """
        return json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        
    @classmethod
    def compute_event_hash(cls, previous_hash: str, payload: Dict[str, Any]) -> str:
        canonical_str = cls.canonical_serialize(payload)
        preimage = (previous_hash + canonical_str).encode('utf-8')
        return hashlib.sha256(preimage).hexdigest()
        
    @classmethod
    def verify_chain(cls, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verifies a list of lineage events ordered by event_seq.
        Each event dictionary must contain:
        {
            "id": ...,
            "token_id": ...,
            "event_seq": int,
            "tx_id": ...,
            "previous_hash": str,
            "current_hash": str,
            "payload": dict or payload_json: str
        }
        """
        if not events:
            return {
                "token_id": None,
                "is_intact": False,
                "total_events": 0,
                "first_broken_seq": None,
                "verification_status": "NO_LINEAGE_FOUND",
                "error_reason": "No lineage events provided for verification.",
                "verified_chain": []
            }
            
        # Sort by sequence
        sorted_events = sorted(events, key=lambda x: x.get("event_seq", 0))
        token_id = sorted_events[0].get("token_id")
        
        verified_chain = []
        is_intact = True
        first_broken_seq = None
        error_reason = None
        
        expected_prev_hash = cls.GENESIS_PREV_HASH
        
        for idx, event in enumerate(sorted_events):
            seq = event.get("event_seq", idx)
            recorded_prev = event.get("previous_hash", "")
            recorded_curr = event.get("current_hash", "")
            
            raw_payload = event.get("payload")
            if raw_payload is None:
                payload_str = event.get("payload_json", "{}")
                try:
                    raw_payload = json.loads(payload_str)
                except Exception:
                    raw_payload = {}
                    
            # Compute hash based on recorded_prev
            recomputed_hash = cls.compute_event_hash(recorded_prev, raw_payload)
            
            chain_broken_here = False
            step_error = None
            
            # Check 1: Sequence continuity
            if seq != idx:
                chain_broken_here = True
                step_error = f"Sequence gap or ordering error: expected sequence {idx}, observed {seq}"
                
            # Check 2: Previous hash link
            elif recorded_prev != expected_prev_hash:
                chain_broken_here = True
                step_error = f"Broken previous-hash link: recorded '{recorded_prev[:12]}...', expected '{expected_prev_hash[:12]}...'"
                
            # Check 3: Current hash integrity (tampering in payload or hash)
            elif recomputed_hash != recorded_curr:
                chain_broken_here = True
                step_error = f"Hash integrity failure: recomputed '{recomputed_hash[:12]}...' does not match recorded '{recorded_curr[:12]}...'"
                
            verified_item = {
                "event_seq": seq,
                "tx_id": event.get("tx_id"),
                "from_account_id": event.get("from_account_id", raw_payload.get("from_account_id")),
                "to_account_id": event.get("to_account_id", raw_payload.get("to_account_id")),
                "amount": event.get("amount", raw_payload.get("amount", 0.0)),
                "recorded_previous_hash": recorded_prev,
                "recorded_current_hash": recorded_curr,
                "recomputed_hash": recomputed_hash,
                "is_step_valid": not chain_broken_here,
                "step_error": step_error
            }
            verified_chain.append(verified_item)
            
            if chain_broken_here and is_intact:
                is_intact = False
                first_broken_seq = seq
                error_reason = step_error
                
            # Update expected for next step
            expected_prev_hash = recorded_curr
            
        status_str = "VERIFIED_INTACT" if is_intact else "INTEGRITY_COMPROMISED"
        
        return {
            "token_id": token_id,
            "is_intact": is_intact,
            "total_events": len(sorted_events),
            "first_broken_seq": first_broken_seq,
            "verification_status": status_str,
            "error_reason": error_reason,
            "verified_chain": verified_chain,
            "cryptographic_algorithm": "SHA-256",
            "canonicalization_standard": "RFC 8785"
        }

