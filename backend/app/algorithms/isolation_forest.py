import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

from app.config import settings
from app.algorithms.feature_extractor import FeatureExtractor

class IsolationForestEngine:
    """
    Algorithm 6: Unsupervised Isolation Forest Anomaly Engine
    Identifies multi-dimensional topological and velocity outliers.
    Provides local explainability via feature perturbation without claiming raw scores are calibrated probabilities.
    """
    
    def __init__(self, model_path: Optional[Path] = None, contamination: float = 0.05, random_state: int = 42):
        self.model_path = model_path or settings.ISOLATION_FOREST_PATH
        self.contamination = contamination
        self.random_state = random_state
        self.model: Optional[IsolationForest] = None
        self._load_model_if_exists()
        
    def _load_model_if_exists(self):
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
            except Exception:
                self.model = None

    @property
    def status(self) -> str:
        return "READY" if self.model is not None else "NOT_TRAINED"

    def train(self, feature_vectors: np.ndarray) -> Dict[str, Any]:
        """
        Trains Isolation Forest on background population feature vectors.
        """
        if len(feature_vectors) < 10:
            return {"status": "FAILED", "reason": "Insufficient training samples (minimum 10 required)."}
            
        clf = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1
        )
        clf.fit(feature_vectors)
        self.model = clf
        
        # Save model artifact
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        
        return {
            "status": "READY",
            "samples_trained": len(feature_vectors),
            "features_dimension": feature_vectors.shape[1],
            "contamination": self.contamination,
            "model_path": str(self.model_path)
        }

    def predict(self, feature_dict: Dict[str, float]) -> Dict[str, Any]:
        if self.model is None:
            return {
                "status": "NOT_TRAINED",
                "anomaly_score": 0.0,
                "is_outlier": False,
                "top_anomalous_features": [],
                "disclaimer": "Isolation Forest model has not been trained yet."
            }
            
        vec = FeatureExtractor.to_normalized_vector(feature_dict).reshape(1, -1)
        raw_score = float(self.model.decision_function(vec)[0])  # negative is anomalous
        prediction = int(self.model.predict(vec)[0])             # -1 is outlier, 1 is inlier
        
        # Normalize score into [0.0, 100.0]
        # In sklearn, decision_function ~ [-0.25 to 0.25]. Lower = more anomalous.
        # Mapping: score <= -0.15 => 100, score >= 0.15 => 0
        normalized_score = float(np.clip((0.15 - raw_score) / 0.30 * 100.0, 0.0, 100.0))
        
        # Feature perturbation explainability:
        # Check sensitivity of decision function to each feature
        base_score = raw_score
        feature_impacts = []
        
        for idx, feat_name in enumerate(FeatureExtractor.FEATURE_NAMES):
            perturbed_vec = vec.copy()
            # Perturb downwards towards median/baseline
            perturbed_vec[0, idx] *= 0.5
            delta = float(self.model.decision_function(perturbed_vec)[0]) - base_score
            # If moving towards zero reduces anomaly (increases decision function), this feature drove isolation
            if delta > 0:
                feature_impacts.append({
                    "feature": feat_name,
                    "impact": round(delta * 100.0, 2),
                    "value": feature_dict.get(feat_name, 0.0)
                })
                
        feature_impacts.sort(key=lambda x: x["impact"], reverse=True)
        
        return {
            "status": "READY",
            "raw_decision_score": round(raw_score, 4),
            "anomaly_score": round(normalized_score, 1),
            "is_outlier": bool(prediction == -1),
            "top_anomalous_features": feature_impacts[:3],
            "disclaimer": "Unsupervised topological outlier measure; does not represent calibrated fraud probability."
        }

