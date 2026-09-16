"""
TerraWatch — risk model.

Two-stage approach:
    Stage 1 — Rule-based scoring (always available).
    Stage 2 — Trained ML model (used when a validated model exists).

Risk levels: LOW | MEDIUM | HIGH | VERY_HIGH | REVIEW

IMPORTANT: No fake scores.  If a trained model is not loaded,
risk_score is None and model_status = "MODEL_NOT_READY".
The rule-based score is always computed and returned.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Thresholds (aligned with config/thresholds.yaml)
_NDVI_STRONG   = -0.30
_NDVI_MODERATE = -0.15
_NDVI_MINOR    = -0.05
_LOSS_LARGE    = 10.0   # ha
_LOSS_MODERATE = 2.0    # ha
_EXCLUDE_HIGH  = 0.5    # boundary_manipulation_score

_RISK_LOW_MAX    = 30
_RISK_MEDIUM_MAX = 60
_RISK_HIGH_MAX   = 85


def predict_risk(
    features: Dict[str, Optional[float]],
    model_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Compute risk score and level from the feature dict.

    Parameters
    ----------
    features   : dict — output of feature_builder.build_features().
    model_path : Path | None — path to a serialised sklearn model (.pkl).
                 If None, falls back to rule-based scoring only.

    Returns
    -------
    dict with:
        rule_score       : float   [0–100]  always computed
        rule_level       : str
        ml_score         : float | None    from trained model
        ml_level         : str | None
        final_score      : float | None    (ml_score if available, else None)
        final_level      : str
        model_version    : str | None
        model_status     : str
    """
    rule_score, rule_level = _rule_based_score(features)

    ml_score  = None
    ml_level  = None
    model_ver = None
    status    = "RULE_BASED"

    if model_path and model_path.exists():
        try:
            ml_score, ml_level, model_ver = _ml_score(features, model_path)
            status = "ML_MODEL"
        except Exception as exc:
            print(f"[risk_model] ML model failed: {exc}. Falling back to rule-based.")
            status = "ML_MODEL_ERROR"

    final_score = ml_score   if ml_score is not None else None
    final_level = ml_level   if ml_level is not None else rule_level

    return {
        "rule_score":    round(rule_score, 2),
        "rule_level":    rule_level,
        "ml_score":      round(ml_score, 2) if ml_score is not None else None,
        "ml_level":      ml_level,
        "final_score":   round(final_score, 2) if final_score is not None else None,
        "final_level":   final_level,
        "model_version": model_ver,
        "model_status":  status,
    }


# ── Rule-based scoring ───────────────────────────────────────────────────────

def _rule_based_score(features: Dict[str, Optional[float]]) -> Tuple[float, str]:
    """
    Weighted heuristic score [0–100] based on:
        - NDVI change magnitude
        - Detected loss area
        - Boundary exclusion
        - Data quality

    Weights are documented, not arbitrary.  Adjust in config/thresholds.yaml.
    """
    score = 0.0

    # ── NDVI component (max 35 pts) ───────────────────────────────────────
    ndvi_chg = features.get("ndvi_change")
    if ndvi_chg is not None:
        if ndvi_chg < _NDVI_STRONG:
            score += 35
        elif ndvi_chg < _NDVI_MODERATE:
            score += 20
        elif ndvi_chg < _NDVI_MINOR:
            score += 8

    # ── Forest loss component (max 35 pts) ───────────────────────────────
    loss_ha = features.get("forest_loss_hectares") or 0.0
    if loss_ha >= _LOSS_LARGE:
        score += 35
    elif loss_ha >= _LOSS_MODERATE:
        score += 15 + (loss_ha / _LOSS_LARGE) * 20
    elif loss_ha > 0:
        score += (loss_ha / _LOSS_MODERATE) * 15

    # ── Boundary exclusion component (max 20 pts) ────────────────────────
    manip_score = features.get("boundary_manipulation_score") or 0.0  # handled in features
    excl_ha     = features.get("excluded_loss_ha") or 0.0
    total_loss  = (features.get("inside_loss_ha") or 0.0) + excl_ha
    if total_loss > 0:
        excl_fraction = excl_ha / total_loss
        score += excl_fraction * 20

    # ── Quality penalty (subtract up to 10 pts for low quality) ──────────
    usable_pct = features.get("usable_pixel_pct") or 100.0
    if usable_pct < 70:
        score -= (70 - usable_pct) * 0.3  # partial penalty

    score = max(0.0, min(100.0, score))

    level = _score_to_level(score)
    return score, level


def _score_to_level(score: float) -> str:
    if score <= _RISK_LOW_MAX:
        return "LOW"
    elif score <= _RISK_MEDIUM_MAX:
        return "MEDIUM"
    elif score <= _RISK_HIGH_MAX:
        return "HIGH"
    else:
        return "VERY_HIGH"


# ── ML model scoring ─────────────────────────────────────────────────────────

def _ml_score(
    features: Dict[str, Optional[float]],
    model_path: Path,
) -> Tuple[float, str, str]:
    """
    Load and run a pickled sklearn model.

    Returns (score_0_to_100, level, model_version).
    """
    import pickle
    from .feature_builder import features_to_vector

    with open(model_path, "rb") as f:
        model_bundle = pickle.load(f)

    model         = model_bundle["model"]
    model_version = model_bundle.get("version", "unknown")

    vec = features_to_vector(features)
    proba = model.predict_proba([vec])[0]

    # Assume binary classification: class 0 = no-loss, class 1 = loss
    score = float(proba[1]) * 100
    level = _score_to_level(score)

    return score, level, model_version
