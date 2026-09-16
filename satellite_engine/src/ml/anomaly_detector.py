"""
TerraWatch — anomaly detector.

Uses scikit-learn's IsolationForest for unsupervised anomaly detection
when labelled training data is insufficient.

An anomaly score indicates unusual spectral/temporal change patterns
relative to a reference distribution.  It is a supplementary signal —
NOT a standalone deforestation verdict.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


class AnomalyDetector:
    """
    Isolation Forest-based anomaly detector for satellite feature vectors.

    Training
    --------
    >>> detector = AnomalyDetector()
    >>> detector.fit(training_features_list)
    >>> detector.save(Path("ml_models/development/anomaly_v1.pkl"))

    Inference
    ---------
    >>> detector = AnomalyDetector.load(Path("ml_models/production/anomaly_v1.pkl"))
    >>> result = detector.predict(feature_dict)
    """

    def __init__(self, contamination: float = 0.05, n_estimators: int = 100) -> None:
        """
        Parameters
        ----------
        contamination : float — expected proportion of anomalous samples.
        n_estimators  : int   — number of trees in the forest.
        """
        self.contamination = contamination
        self.n_estimators  = n_estimators
        self._model        = None
        self._version      = None

    def fit(
        self,
        feature_dicts: List[Dict[str, Optional[float]]],
        version: str = "v1.0",
    ) -> None:
        """
        Fit the Isolation Forest on a list of feature dicts.

        Parameters
        ----------
        feature_dicts : list of dicts — from feature_builder.build_features().
        version       : str — version tag.
        """
        from sklearn.ensemble import IsolationForest
        from .feature_builder import features_to_vector

        X = np.array([features_to_vector(f) for f in feature_dicts])

        self._model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=42,
        )
        self._model.fit(X)
        self._version = version

    def predict(
        self,
        features: Dict[str, Optional[float]],
    ) -> Dict[str, Any]:
        """
        Compute an anomaly score for a single observation.

        Parameters
        ----------
        features : dict — from feature_builder.build_features().

        Returns
        -------
        dict with:
            is_anomaly        : bool
            anomaly_score     : float  [-1, 0] (lower = more anomalous)
            anomaly_level     : str    (NORMAL / SUSPICIOUS / ANOMALOUS)
            model_version     : str | None
        """
        if self._model is None:
            return {
                "is_anomaly":    None,
                "anomaly_score": None,
                "anomaly_level": "MODEL_NOT_FITTED",
                "model_version": None,
            }

        from .feature_builder import features_to_vector

        vec   = np.array([features_to_vector(features)])
        score = float(self._model.score_samples(vec)[0])  # more negative = more anomalous
        pred  = int(self._model.predict(vec)[0])          # -1 = anomaly, 1 = normal

        is_anomaly = (pred == -1)

        if score > -0.1:
            level = "NORMAL"
        elif score > -0.3:
            level = "SUSPICIOUS"
        else:
            level = "ANOMALOUS"

        return {
            "is_anomaly":    is_anomaly,
            "anomaly_score": round(score, 6),
            "anomaly_level": level,
            "model_version": self._version,
        }

    def save(self, path: Path) -> None:
        """Pickle the fitted model to disk."""
        import pickle
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"model": self._model, "version": self._version}, f)

    @classmethod
    def load(cls, path: Path) -> "AnomalyDetector":
        """Load a previously saved detector."""
        import pickle
        detector = cls()
        with open(path, "rb") as f:
            bundle = pickle.load(f)
        detector._model   = bundle["model"]
        detector._version = bundle.get("version")
        return detector
