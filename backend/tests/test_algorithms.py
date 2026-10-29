import pytest
import networkx as nx
import numpy as np
from datetime import datetime, timedelta, timezone

from app.models.entities import Account, Transaction
from app.algorithms.velocity_engine import VelocityEngine
from app.algorithms.lineage_verifier import LineageVerifier
from app.algorithms.bfs_tracer import BFSTracer
from app.algorithms.feature_extractor import FeatureExtractor
from app.algorithms.rule_engine import RuleEngine
from app.algorithms.isolation_forest import IsolationForestEngine
from app.algorithms.louvain_engine import LouvainCommunityEngine
from app.algorithms.graphsage_engine import GraphSAGEEngine

def test_algorithm_1_velocity_engine():
    vel = VelocityEngine()
    now = datetime(2026, 10, 29, 12, 0, 0, tzinfo=timezone.utc)
    
    # Empty window test (zero-denominator safe)
    res_empty = vel.analyze_account("acc_test_1", [], [], reference_time=now)
    assert res_empty["velocity_risk_score"] == 0.0
    assert res_empty["status"] == "BENIGN"
    assert res_empty["windows"]["10m"]["pass_through_ratio"] == 0.0

    # Rapid pass-through test: 100,000 in, 95,000 out within 20 minutes
    in_tx = Transaction(id="tx_in", amount=100000.0, timestamp=now - timedelta(minutes=25))
    out_tx = Transaction(id="tx_out", amount=95000.0, timestamp=now - timedelta(minutes=5))
    
    res_rpt = vel.analyze_account("acc_test_2", [in_tx], [out_tx], reference_time=now)
    assert res_rpt["windows"]["1h"]["rapid_passthrough"] is True
    assert res_rpt["windows"]["1h"]["pass_through_ratio"] == 0.95
    assert res_rpt["velocity_risk_score"] >= 35.0

    # Burst test: 6 transactions in 5 minutes
    burst_txs = [
        Transaction(id=f"tx_b_{i}", amount=5000.0, timestamp=now - timedelta(minutes=i))
        for i in range(6)
    ]
    res_burst = vel.analyze_account("acc_test_3", burst_txs, [], reference_time=now)
    assert res_burst["windows"]["10m"]["is_burst"] is True
    assert res_burst["windows"]["10m"]["total_txs"] == 6

def test_algorithm_2_lineage_verifier():
    # 1. Build an authentic chain
    token_id = "eINR_TEST_001"
    events = []
    prev_hash = LineageVerifier.GENESIS_PREV_HASH
    
    for seq in range(4):
        payload = {"token_id": token_id, "event_seq": seq, "amount": 10000.0 + seq*100, "from": f"acc_{seq}", "to": f"acc_{seq+1}"}
        curr_hash = LineageVerifier.compute_event_hash(prev_hash, payload)
        events.append({
            "token_id": token_id,
            "event_seq": seq,
            "tx_id": f"tx_{seq}",
            "previous_hash": prev_hash,
            "current_hash": curr_hash,
            "payload": payload
        })
        prev_hash = curr_hash
        
    # Verify intact chain
    v_res = LineageVerifier.verify_chain(events)
    assert v_res["is_intact"] is True
    assert v_res["verification_status"] == "VERIFIED_INTACT"
    assert v_res["total_events"] == 4
    assert v_res["first_broken_seq"] is None

    # 2. Tampered chain test (mutate payload at seq 2)
    tampered_events = [dict(e) for e in events]
    tampered_payload = dict(tampered_events[2]["payload"])
    tampered_payload["amount"] = 999999.0  # altered amount
    tampered_events[2]["payload"] = tampered_payload
    
    t_res = LineageVerifier.verify_chain(tampered_events)
    assert t_res["is_intact"] is False
    assert t_res["verification_status"] == "INTEGRITY_COMPROMISED"
    assert t_res["first_broken_seq"] == 2
    assert "Hash integrity failure" in t_res["error_reason"]

    # 3. Broken link test (corrupt previous_hash at seq 1)
    broken_link_events = [dict(e) for e in events]
    broken_link_events[1]["previous_hash"] = "f" * 64
    b_res = LineageVerifier.verify_chain(broken_link_events)
    assert b_res["is_intact"] is False
    assert b_res["first_broken_seq"] == 1
    assert "Broken previous-hash link" in b_res["error_reason"]

def test_algorithm_3_bfs_tracer():
    G = nx.MultiDiGraph()
    now = datetime(2026, 10, 29, 12, 0, 0, tzinfo=timezone.utc)
    
    # Setup graph: A -> B -> C -> OFFRAMP
    G.add_node("A", account_type="CHECKING", account_number="1001", holder_name="Sender")
    G.add_node("B", account_type="CHECKING", account_number="1002", holder_name="Intermediate")
    G.add_node("C", account_type="CHECKING", account_number="1003", holder_name="Layer")
    G.add_node("OFFRAMP", account_type="CRYPTO_OFFRAMP", account_number="9999", holder_name="Crypto Bridge")
    
    G.add_edge("A", "B", key="tx1", tx_id="tx1", amount=50000.0, timestamp=now + timedelta(minutes=10))
    G.add_edge("B", "C", key="tx2", tx_id="tx2", amount=48000.0, timestamp=now + timedelta(minutes=20))
    G.add_edge("C", "OFFRAMP", key="tx3", tx_id="tx3", amount=46000.0, timestamp=now + timedelta(minutes=30))
    
    tracer = BFSTracer(default_max_hops=5)
    
    # Forward trace should reach off-ramp and stop with OFF_RAMP_REACHED
    res = tracer.trace(G, start_account_id="A", direction="FORWARD", reference_time=now)
    assert res["stop_reason"] == "OFF_RAMP_REACHED"
    assert res["nodes_count"] == 4
    assert res["edges_count"] == 3
    assert res["total_volume_traced"] == 144000.0
    
    # Backward trace from OFFRAMP
    res_back = tracer.trace(G, start_account_id="OFFRAMP", direction="BACKWARD", reference_time=now + timedelta(minutes=35))
    assert res_back["nodes_count"] == 4

    # Max hops limit test
    tracer_small = BFSTracer(default_max_hops=1)
    res_hop1 = tracer_small.trace(G, start_account_id="A", direction="FORWARD", reference_time=now, max_hops=1)
    assert res_hop1["stop_reason"] in ("MAX_HOPS_REACHED", "NO_ELIGIBLE_INCOMING_OR_OUTGOING_TRANSACTIONS")
    assert res_hop1["nodes_count"] == 2

    # Non-existent node
    res_none = tracer.trace(G, start_account_id="NON_EXISTENT")
    assert res_none["stop_reason"] == "START_ACCOUNT_NOT_FOUND"

def test_algorithm_4_feature_extractor():
    G = nx.MultiDiGraph()
    G.add_node("acc_hub")
    for i in range(5):
        G.add_node(f"src_{i}")
        G.add_edge(f"src_{i}", "acc_hub", key=f"e_in_{i}", amount=10000.0, timestamp=datetime(2026, 10, 29, 10, i, 0, tzinfo=timezone.utc))
    for j in range(3):
        G.add_node(f"dst_{j}")
        G.add_edge("acc_hub", f"dst_{j}", key=f"e_out_{j}", amount=15000.0, timestamp=datetime(2026, 10, 29, 11, j, 0, tzinfo=timezone.utc))
        
    features = FeatureExtractor.extract_features(G, "acc_hub")
    assert features["in_degree"] == 5.0
    assert features["out_degree"] == 3.0
    assert features["total_inflow"] == 50000.0
    assert features["total_outflow"] == 45000.0
    assert features["fan_in"] == 5.0
    assert features["fan_out"] == 3.0
    assert features["pass_through_ratio"] == 0.90
    assert features["burst_score"] == 5.0
    
    vec = FeatureExtractor.to_normalized_vector(features)
    assert vec.shape == (12,)
    assert not np.isnan(vec).any()
    assert not np.isinf(vec).any()

def test_algorithm_5_rule_engine():
    rule_engine = RuleEngine()
    
    # Suspicious Mule Account
    acc_mule = Account(id="mule_1", account_type="CHECKING", account_number="55001", holder_name="Mule Node")
    in_tx = [Transaction(id="tx_1", source_account_id="src_1", dest_account_id="mule_1", amount=100000.0)]
    out_tx = [Transaction(id="tx_2", source_account_id="mule_1", dest_account_id="dst_1", amount=95000.0)]
    features = {
        "total_inflow": 100000.0,
        "total_outflow": 95000.0,
        "pass_through_ratio": 0.95,
        "burst_score": 6.0,
        "fan_in": 1.0,
        "fan_out": 1.0
    }
    
    res = rule_engine.evaluate(acc_mule, in_tx, out_tx, features)
    assert res["rule_risk_score"] >= 50.0
    assert res["rules_triggered"] >= 2  # R-101 (pass-through) and R-102 (burst)
    
    # Legitimate Corporate Payroll lookalike must NOT trigger pass-through rule
    acc_corp = Account(id="corp_1", account_type="CORPORATE", account_number="99001", holder_name="Big Corp")
    res_corp = rule_engine.evaluate(acc_corp, in_tx, out_tx, features)
    r101 = [e for e in res_corp["evidences"] if e["rule_code"] == "R-101"][0]
    assert r101["predicate_met"] is False

def test_algorithm_6_isolation_forest():
    iso = IsolationForestEngine()
    # Synthetic normal population
    np.random.seed(42)
    normal_data = np.random.normal(loc=2.0, scale=0.5, size=(50, 12)).astype(np.float32)
    train_res = iso.train(normal_data)
    assert train_res["status"] == "READY"
    assert iso.status == "READY"
    
    # Normal sample prediction
    norm_features = {name: 2.0 for name in FeatureExtractor.FEATURE_NAMES}
    pred_norm = iso.predict(norm_features)
    assert pred_norm["status"] == "READY"
    
    # Extreme outlier sample prediction (huge values)
    outlier_features = {name: 1000.0 for name in FeatureExtractor.FEATURE_NAMES}
    pred_outlier = iso.predict(outlier_features)
    assert pred_outlier["anomaly_score"] > pred_norm["anomaly_score"]
    assert len(pred_outlier["top_anomalous_features"]) > 0

def test_algorithm_7_louvain_community():
    G = nx.MultiDiGraph()
    # Create two distinct clusters
    for i in range(4):
        G.add_node(f"c1_{i}", account_number=f"c1_{i}")
        for j in range(4):
            if i != j:
                G.add_edge(f"c1_{i}", f"c1_{j}", key=f"e_{i}_{j}", amount=10000.0)
                
    for i in range(4):
        G.add_node(f"c2_{i}", account_number=f"c2_{i}")
        for j in range(4):
            if i != j:
                G.add_edge(f"c2_{i}", f"c2_{j}", key=f"e2_{i}_{j}", amount=5000.0)
                
    # Single bridge between clusters
    G.add_edge("c1_0", "c2_0", key="bridge", amount=500.0)
    
    engine = LouvainCommunityEngine(seed=42)
    comm_res = engine.compute_communities(G)
    assert comm_res["status"] == "READY"
    assert comm_res["total_communities"] >= 2
    assert comm_res["modularity"] > 0.3
    
    acc_res = engine.analyze_account(G, "c1_1")
    assert acc_res["community_size"] == 4
    assert acc_res["internal_density"] > 0.8
    assert acc_res["is_mule_cluster_candidate"] is True

def test_algorithm_8_graphsage():
    gs = GraphSAGEEngine()
    G = nx.MultiDiGraph()
    # Ring of 8 nodes
    labels = {}
    nodes = [f"node_{i}" for i in range(8)]
    for i, n in enumerate(nodes):
        G.add_node(n)
        nxt = nodes[(i + 1) % 8]
        G.add_edge(n, nxt, key=f"e_{i}", amount=10000.0)
        labels[n] = 1 if i < 4 else 0
        
    train_res = gs.train_on_graph(G, labels, train_nodes=nodes, epochs=15)
    assert train_res["status"] == "READY"
    assert gs.status == "READY"
    
    # Inference on node_0
    pred = gs.predict(G, "node_0")
    assert pred["status"] == "READY"
    assert 0.0 <= pred["mule_probability"] <= 1.0
    assert 0.0 <= pred["graphsage_risk_score"] <= 100.0

