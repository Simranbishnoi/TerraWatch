"""TerraWatch — ml package."""
from .feature_builder import build_features, features_to_vector, calculate_observation_gap
from .risk_model import predict_risk
from .anomaly_detector import AnomalyDetector
from .model_registry import ModelRegistry, ModelRecord

__all__ = [
    "build_features", "features_to_vector", "calculate_observation_gap",
    "predict_risk", "AnomalyDetector", "ModelRegistry", "ModelRecord",
]
