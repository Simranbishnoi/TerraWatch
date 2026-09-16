"""
TerraWatch — evidence builder.

Converts raw satellite analysis numbers into human-readable
evidence statements.  Language is intentionally cautious —
satellite data identifies potential change; human verification
confirms legal conclusions.
"""

from typing import Any, Dict, List, Optional


def build_evidence(
    ndvi_change: Optional[float],
    ndmi_change: Optional[float],
    forest_loss_ha: Optional[float],
    quality_level: str,
    boundary_assessment: str,
    excluded_loss_ha: Optional[float],
    inside_loss_ha: Optional[float],
    decline_pct: Optional[float],
    observation_date: Optional[str],
    previous_date: Optional[str],
) -> List[str]:
    """
    Generate a list of human-readable evidence statements.

    Parameters
    ----------
    (All parameters match the outputs of the pipeline stages.)

    Returns
    -------
    List[str] — evidence sentences, ordered by significance.
    """
    summary: List[str] = []

    # ── Observation context ───────────────────────────────────────────────
    if observation_date and previous_date:
        summary.append(
            f"Satellite analysis compared observations from {previous_date} (before) "
            f"and {observation_date} (after)."
        )
    elif observation_date:
        summary.append(
            f"Satellite observation from {observation_date} was analysed."
        )

    # ── Data quality ──────────────────────────────────────────────────────
    quality_msgs = {
        "HIGH":     "Observation quality was high — sufficient for reliable analysis.",
        "MEDIUM":   "Observation quality was medium — analysis results are indicative.",
        "LOW":      "Observation quality was low — results should be treated with caution.",
        "REJECTED": "Observation quality was insufficient for analysis.",
    }
    if quality_level in quality_msgs:
        summary.append(quality_msgs[quality_level])

    # ── NDVI change ───────────────────────────────────────────────────────
    if ndvi_change is not None:
        if ndvi_change < -0.30:
            summary.append(
                f"Strong potential vegetation decline detected (NDVI change: {ndvi_change:.3f}). "
                "This may indicate forest clearing, harvesting, fire, or drought stress."
            )
        elif ndvi_change < -0.15:
            summary.append(
                f"Moderate potential vegetation change detected (NDVI change: {ndvi_change:.3f}). "
                "Further verification is recommended."
            )
        elif ndvi_change < -0.05:
            summary.append(
                f"Minor vegetation change detected (NDVI change: {ndvi_change:.3f}). "
                "This may reflect seasonal variation."
            )
        else:
            summary.append(
                f"No significant vegetation decline detected (NDVI change: {ndvi_change:.3f})."
            )

    # ── NDMI change (moisture) ────────────────────────────────────────────
    if ndmi_change is not None and ndmi_change < -0.15:
        summary.append(
            f"Canopy moisture content also declined (NDMI change: {ndmi_change:.3f}), "
            "which is consistent with vegetation loss or drought."
        )

    # ── Forest loss area ──────────────────────────────────────────────────
    if forest_loss_ha is not None and forest_loss_ha > 0:
        summary.append(
            f"Approximately {forest_loss_ha:.2f} hectares of potential forest/vegetation "
            "loss were detected between the two observations."
        )
        if decline_pct and decline_pct > 20:
            summary.append(
                f"The decline affects approximately {decline_pct:.1f}% of valid pixels "
                "in the analysis area."
            )
    elif forest_loss_ha == 0.0:
        summary.append("No significant forest/vegetation loss area was detected.")

    # ── Boundary evidence ─────────────────────────────────────────────────
    if boundary_assessment == "CONSISTENT_WITH_BOUNDARY":
        summary.append(
            "The detected change is spatially consistent with the submitted farm boundary."
        )
    elif boundary_assessment in ("MINOR_BOUNDARY_DISCREPANCY",):
        if excluded_loss_ha:
            summary.append(
                f"A minor portion of detected change ({excluded_loss_ha:.2f} ha) "
                "falls outside the submitted farm boundary."
            )
    elif boundary_assessment in ("NOTABLE_BOUNDARY_DISCREPANCY", "REQUIRES_BOUNDARY_VERIFICATION"):
        if excluded_loss_ha and inside_loss_ha:
            summary.append(
                f"A notable portion of detected change ({excluded_loss_ha:.2f} ha) "
                f"falls outside the submitted farm boundary, while {inside_loss_ha:.2f} ha "
                "is inside. Boundary verification is recommended."
            )

    # ── Disclaimer ────────────────────────────────────────────────────────
    summary.append(
        "Note: Satellite evidence identifies potential changes. "
        "Field verification is required before drawing legal conclusions."
    )

    return summary
