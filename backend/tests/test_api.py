import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db

client = TestClient(app)

def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["project"] == "MULE MATRIX"

def test_system_health():
    resp = client.get("/api/v1/system/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "HEALTHY"
    assert "engines" in data
    assert data["engines"]["velocity_engine"] == "READY"
    assert data["engines"]["lineage_verifier"] == "READY"

def test_observe_sentinel():
    resp = client.get("/api/v1/observe/sentinel")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_accounts" in data
    assert "total_transactions" in data
    assert "recent_alerts" in data

def test_observe_transactions():
    resp = client.get("/api/v1/observe/transactions?limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "amount" in data[0]

def test_observe_alerts():
    resp = client.get("/api/v1/observe/alerts?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)

def test_trace_bfs():
    # Fetch first account
    accs_resp = client.get("/api/v1/observe/accounts?limit=1")
    accs = accs_resp.json()
    if len(accs) > 0:
        acc_id = accs[0]["id"]
        trace_req = {
            "account_id": acc_id,
            "direction": "FORWARD",
            "max_hops": 3,
            "lookback_hours": 72.0,
            "lookahead_hours": 72.0
        }
        resp = client.post("/api/v1/trace/bfs", json=trace_req)
        assert resp.status_code == 200
        data = resp.json()
        assert "stop_reason" in data
        assert "nodes" in data
        assert "edges" in data

def test_detect_account():
    accs_resp = client.get("/api/v1/observe/accounts?limit=1")
    accs = accs_resp.json()
    if len(accs) > 0:
        acc_id = accs[0]["id"]
        resp = client.get(f"/api/v1/detect/account/{acc_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert "composite_risk_score" in data
        assert "risk_tier" in data
        assert "signals" in data
        assert len(data["signals"]) >= 5

def test_case_lifecycle_and_export():
    accs_resp = client.get("/api/v1/observe/accounts?limit=1")
    accs = accs_resp.json()
    acc_id = accs[0]["id"] if accs else "acc_00001"
    
    # 1. Create Case
    case_payload = {
        "title": "Suspected Mule Syndicate Testing Case",
        "primary_account_id": acc_id,
        "priority": "HIGH",
        "assigned_to": "Senior Forensic Analyst",
        "findings_summary": "Automated alert triggered high risk pass-through."
    }
    create_resp = client.post("/api/v1/respond/cases", json=case_payload)
    assert create_resp.status_code == 201
    case_data = create_resp.json()
    case_id = case_data["id"]
    
    # 2. Add Note
    note_resp = client.post(f"/api/v1/respond/cases/{case_id}/notes", json={
        "author": "Forensic Analyst",
        "note_text": "Examined transactional velocity; matches rapid dispersion profile."
    })
    assert note_resp.status_code == 200
    
    # 3. Update Status
    status_resp = client.patch(f"/api/v1/respond/cases/{case_id}/status", json={
        "status": "IN_REVIEW",
        "assigned_to": "Compliance Lead",
        "status_change_reason": "Escalated for senior review."
    })
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "IN_REVIEW"
    
    # 4. Export Evidence Dossier
    export_resp = client.post(f"/api/v1/respond/cases/{case_id}/export")
    assert export_resp.status_code == 200
    export_data = export_resp.json()
    assert "artifact_id" in export_data
    assert "content_hash" in export_data
    assert export_data["artifact_type"] == "HTML_DOSSIER"

def test_audit_integrity():
    resp = client.get("/api/v1/audit/verify")
    assert resp.status_code == 200
    data = resp.json()
    assert "is_ledger_intact" in data
    assert data["is_ledger_intact"] is True

