"""
TerraWatch — boundary exclusion analysis.

Assesses whether the detected forest/vegetation loss is spatially
consistent with the submitted farm boundary.

A high boundary_manipulation_score indicates that a notable portion
of detected loss falls *outside* the declared farm polygon — which
may warrant further verification.

IMPORTANT: A high score does NOT prove fraud.
           It is an indicator that requires human review.
"""

from typing import Any, Dict, Optional


def analyze_boundary_exclusion(
    overlap_result: Dict[str, Optional[float]],
) -> Dict[str, Optional[float]]:
    """
    Derive a boundary-exclusion score from overlap metrics.

    Parameters
    ----------
    overlap_result : dict
        Output of ``calculate_overlap``.
        Must contain:
            total_detected_loss_ha
            inside_loss_ha
            outside_loss_ha
            overlap_percentage
            outside_percentage

    Returns
    -------
    dict with keys:
        boundary_manipulation_score    [0.0 – 1.0]
            0.0 = all loss inside boundary (consistent)
            1.0 = all loss outside boundary (requires verification)
        excluded_loss_ha               hectares outside boundary
        inside_loss_ha                 hectares inside boundary
        total_detected_loss_ha
        assessment                     human-readable label
    """
    total_ha: float = overlap_result.get("total_detected_loss_ha") or 0.0
    inside_ha: float = overlap_result.get("inside_loss_ha") or 0.0
    outside_ha: float = overlap_result.get("outside_loss_ha") or 0.0
    outside_pct: float = overlap_result.get("outside_percentage") or 0.0

    if total_ha == 0.0:
        # No loss detected — no exclusion concern
        return {
            "boundary_manipulation_score": 0.0,
            "excluded_loss_ha": 0.0,
            "inside_loss_ha": 0.0,
            "total_detected_loss_ha": 0.0,
            "assessment": "NO_LOSS_DETECTED",
        }

    # Score = fraction of loss outside boundary
    score = round(outside_ha / total_ha, 4) if total_ha > 0 else 0.0

    # Qualitative assessment
    if score < 0.10:
        assessment = "CONSISTENT_WITH_BOUNDARY"
    elif score < 0.30:
        assessment = "MINOR_BOUNDARY_DISCREPANCY"
    elif score < 0.60:
        assessment = "NOTABLE_BOUNDARY_DISCREPANCY"
    else:
        assessment = "REQUIRES_BOUNDARY_VERIFICATION"

    return {
        "boundary_manipulation_score": score,
        "excluded_loss_ha": round(outside_ha, 4),
        "inside_loss_ha": round(inside_ha, 4),
        "total_detected_loss_ha": round(total_ha, 4),
        "assessment": assessment,
    }
