import inspect
from app.algorithms.velocity_engine import VelocityEngine
from app.algorithms.lineage_verifier import LineageVerifier
from app.algorithms.bfs_tracer import BFSTracer
from app.algorithms.feature_extractor import FeatureExtractor
from app.algorithms.rule_engine import RuleEngine
from app.algorithms.isolation_forest import IsolationForestEngine
from app.algorithms.louvain_engine import LouvainCommunityEngine
from app.algorithms.graphsage_engine import GraphSAGEEngine
from app.services.risk_aggregator import RiskAggregator
from app.routers import detect

def test_detection_engines_do_not_access_ground_truth():
    """
    Automated test verifying that runtime detection engines, risk aggregator,
    and detect router NEVER access ground-truth labels ('is_mule', 'mule_role').
    """
    engines = [
        VelocityEngine,
        LineageVerifier,
        BFSTracer,
        FeatureExtractor,
        RuleEngine,
        IsolationForestEngine,
        LouvainCommunityEngine,
        GraphSAGEEngine,
        RiskAggregator
    ]
    
    for engine_cls in engines:
        source = inspect.getsource(engine_cls)
        # Verify no direct lookup of ground-truth columns
        assert "acc.is_mule" not in source, f"{engine_cls.__name__} references 'acc.is_mule'!"
        assert "account.is_mule" not in source, f"{engine_cls.__name__} references 'account.is_mule'!"
        assert "acc.mule_role" not in source, f"{engine_cls.__name__} references 'acc.mule_role'!"
        assert "account.mule_role" not in source, f"{engine_cls.__name__} references 'account.mule_role'!"

def test_detect_router_source_does_not_read_ground_truth():
    """
    Verify the detection router does not read ground truth.
    """
    source = inspect.getsource(detect)
    assert "is_mule" not in source, "detect router references 'is_mule'!"
    assert "mule_role" not in source, "detect router references 'mule_role'!"

