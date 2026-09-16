"""
TerraWatch Satellite + ML Pipeline
====================================
Main entry point consumed by Simran's backend via:

    from satellite_engine.src.pipeline import run_satellite_analysis
    result = run_satellite_analysis(request_dict)

Pipeline steps
--------------
1.  Validate & parse request
2.  Validate farm boundary
3.  Convert boundary → ee.Geometry
4.  Retrieve before observation (or detect no previous)
5.  Find latest usable observation after previous date
6.  Return NO_NEW_OBSERVATION early if none found
7.  Assess quality of the new observation
8.  Run temporal change detection (NDVI + spectral)
9.  Build forest masks (before + after)
10. Detect loss area + generate loss GeoJSON
11. Compute boundary overlap / exclusion
12. Build ML feature vector
13. Run risk model (rule-based + optional ML)
14. Build evidence statements
15. Assemble + return standard JSON response

All GEE computations run server-side; only derived statistics
are transferred to the Python runtime.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .gee_client import require_gee
from .contracts.request import SatelliteAnalysisRequest
from .contracts.response import (
    SatelliteAnalysisResponse,
    ObservationInfo,
    QualityInfo,
    ForestInfo,
    RiskInfo,
    BoundaryInfo,
    EvidenceInfo,
    STATUS_NEW_OBSERVATION,
    STATUS_NO_NEW_OBSERVATION,
    STATUS_NO_USABLE_OBSERVATION,
    STATUS_INVALID_BOUNDARY,
    STATUS_INVALID_DATE_RANGE,
    STATUS_PROCESSING_ERROR,
    QUALITY_REJECTED,
    RISK_REVIEW,
)

from .boundary.geometry import validate_boundary, geojson_to_ee_geometry, calculate_area_hectares
from .boundary.overlap import calculate_overlap
from .boundary.exclusion import analyze_boundary_exclusion

from .satellite_client import SatelliteClient
from .observation_manager import STATUS_NEW_OBSERVATION as OBS_NEW

from .change_detection.temporal_change import run_temporal_change
from .forest.loss_area import run_loss_analysis
from .image_processor import get_true_color_thumb_url

from .ml.feature_builder import build_features, calculate_observation_gap
from .ml.risk_model import predict_risk
from .ml.model_registry import ModelRegistry

from .evidence.evidence_builder import build_evidence


# ── Configuration ─────────────────────────────────────────────────────────────
_CLOUD_THRESHOLD = int(os.getenv("GEE_CLOUD_THRESHOLD", "50"))
_FOREST_NDVI     = float(os.getenv("GEE_FOREST_NDVI", "0.50"))
_MIN_CLUSTER_HA  = float(os.getenv("GEE_MIN_CLUSTER_HA", "0.10"))
_GEE_PROJECT     = os.getenv("GEE_PROJECT_ID", "")

# Model registry (optional; no crash if not found)
_REGISTRY = ModelRegistry()


# ── Public entry point ────────────────────────────────────────────────────────

def run_satellite_analysis(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the complete TerraWatch satellite analysis pipeline.

    Parameters
    ----------
    request : dict
        {
            "farm_id":                  int,
            "boundary":                 GeoJSON Polygon dict,
            "start_date":               "YYYY-MM-DD",
            "end_date":                 "YYYY-MM-DD",
            "previous_observation_date": "YYYY-MM-DD" | None
        }

    Returns
    -------
    dict — standardised JSON response (see contracts/response.py).
    """
    now = datetime.now(timezone.utc).isoformat()

    # ── Step 1: Parse & validate request ─────────────────────────────────
    try:
        req = SatelliteAnalysisRequest.from_dict(request)
        req.validate()
    except (KeyError, ValueError) as exc:
        return SatelliteAnalysisResponse.error_response(
            farm_id=request.get("farm_id", -1),
            status=STATUS_INVALID_BOUNDARY,
            message=str(exc),
        ).to_dict()

    farm_id = req.farm_id

    # ── Step 2: Validate boundary geometry ───────────────────────────────
    try:
        validate_boundary(req.boundary)
    except ValueError as exc:
        return SatelliteAnalysisResponse.error_response(
            farm_id=farm_id,
            status=STATUS_INVALID_BOUNDARY,
            message=f"Invalid farm boundary: {exc}",
        ).to_dict()

    # ── Step 3: Initialise GEE and convert geometry ───────────────────────
    try:
        require_gee(_GEE_PROJECT or None)
        import ee
        geometry = geojson_to_ee_geometry(req.boundary)
        farm_area_ha = calculate_area_hectares(geometry)
        print(f"[pipeline] Farm {farm_id} | area: {farm_area_ha:.2f} ha")
    except Exception as exc:
        return SatelliteAnalysisResponse.error_response(
            farm_id=farm_id,
            status=STATUS_PROCESSING_ERROR,
            message=f"GEE initialisation/geometry error: {exc}",
        ).to_dict()

    # ── Step 4: Retrieve before observation ──────────────────────────────
    client = SatelliteClient(cloud_prob_threshold=_CLOUD_THRESHOLD)

    try:
        before_result = client.get_before_observation(
            geometry=geometry,
            start_date=req.start_date,
            end_date=req.end_date,
            previous_observation_date=req.previous_observation_date,
        )
    except Exception as exc:
        return SatelliteAnalysisResponse.error_response(
            farm_id=farm_id,
            status=STATUS_PROCESSING_ERROR,
            message=f"Error retrieving before observation: {exc}",
        ).to_dict()

    if before_result["status"] != OBS_NEW or before_result["masked_image"] is None:
        return SatelliteAnalysisResponse.error_response(
            farm_id=farm_id,
            status=STATUS_NO_USABLE_OBSERVATION,
            message="Could not retrieve a usable 'before' observation for the requested period.",
        ).to_dict()

    before_date  = before_result["observation_date"]
    before_image = before_result["masked_image"]
    print(f"[pipeline] Before observation: {before_date}")

    # ── Step 5: Find latest usable observation after previous ─────────────
    try:
        after_result = client.get_after_observation(
            geometry=geometry,
            after_date=before_date,
            until_date=req.end_date,
        )
    except Exception as exc:
        return SatelliteAnalysisResponse.error_response(
            farm_id=farm_id,
            status=STATUS_PROCESSING_ERROR,
            message=f"Error searching for new observation: {exc}",
        ).to_dict()

    # ── Step 6: Return early if no new observation ────────────────────────
    if after_result["status"] != OBS_NEW or after_result["masked_image"] is None:
        return {
            "status":   STATUS_NO_NEW_OBSERVATION,
            "farm_id":  farm_id,
            "processing_timestamp": now,
            "message":  after_result.get("message",
                "No new usable Sentinel-2 observation is available "
                "after the previous observation."),
            "observation": {
                "date":          None,
                "previous_date": before_date,
                "image_id":      None,
            },
        }

    after_date    = after_result["observation_date"]
    after_image   = after_result["masked_image"]
    after_quality = after_result["quality"]
    after_image_id = after_result["image_id"]
    print(f"[pipeline] After observation:  {after_date}")

    # ── Step 7: Quality assessment ────────────────────────────────────────
    quality_level   = after_quality.get("quality_level", QUALITY_REJECTED)
    usable_pct      = after_quality.get("usable_pixel_pct")
    cloud_prob_used = _CLOUD_THRESHOLD

    if not after_quality.get("is_usable", False):
        return SatelliteAnalysisResponse.error_response(
            farm_id=farm_id,
            status=STATUS_NO_USABLE_OBSERVATION,
            message=(
                f"Latest observation ({after_date}) has insufficient quality "
                f"({quality_level}, {usable_pct:.1f}% usable pixels)."
            ),
        ).to_dict()

    # ── Step 8: Temporal change detection ────────────────────────────────
    try:
        change = run_temporal_change(
            before_image=before_image,
            after_image=after_image,
            geometry=geometry,
            ndvi_threshold=-0.20,
        )
    except Exception as exc:
        return SatelliteAnalysisResponse.error_response(
            farm_id=farm_id,
            status=STATUS_PROCESSING_ERROR,
            message=f"Change detection error: {exc}",
        ).to_dict()

    print(f"[pipeline] NDVI change: {change.get('ndvi_change')}")

    # ── Step 9 + 10: Forest masks + loss area ─────────────────────────────
    try:
        loss = run_loss_analysis(
            before_image=before_image,
            after_image=after_image,
            geometry=geometry,
            ndvi_threshold=_FOREST_NDVI,
            min_cluster_ha=_MIN_CLUSTER_HA,
        )
    except Exception as exc:
        return SatelliteAnalysisResponse.error_response(
            farm_id=farm_id,
            status=STATUS_PROCESSING_ERROR,
            message=f"Forest loss analysis error: {exc}",
        ).to_dict()

    print(f"[pipeline] Forest loss: {loss.get('forest_loss_hectares')} ha")

    # ── Step 11: Boundary overlap + exclusion ─────────────────────────────
    overlap_stats    = None
    exclusion_result = None

    try:
        if loss.get("loss_mask") is not None and loss.get("forest_loss_hectares", 0) > 0:
            overlap_stats = calculate_overlap(
                loss_mask=loss["loss_mask"],
                farm_geometry=geometry,
            )
            exclusion_result = analyze_boundary_exclusion(overlap_stats)
    except Exception as exc:
        print(f"[pipeline] Warning: boundary analysis failed: {exc}")

    inside_ha   = (overlap_stats or {}).get("inside_loss_ha", 0.0)
    outside_ha  = (overlap_stats or {}).get("outside_loss_ha", 0.0)
    total_ha    = (overlap_stats or {}).get("total_detected_loss_ha", loss.get("forest_loss_hectares", 0.0))
    overlap_pct = (overlap_stats or {}).get("overlap_percentage", 100.0 if total_ha > 0 else 0.0)
    excl_assess = (exclusion_result or {}).get("assessment", "UNKNOWN")
    manip_score = (exclusion_result or {}).get("boundary_manipulation_score")

    # ── Step 12: ML features ──────────────────────────────────────────────
    obs_gap = calculate_observation_gap(before_date, after_date) if before_date and after_date else None

    features = build_features(
        ndvi_before=change.get("ndvi_before"),
        ndvi_after=change.get("ndvi_after"),
        ndvi_change=change.get("ndvi_change"),
        ndmi_before=change.get("ndmi_before"),
        ndmi_after=change.get("ndmi_after"),
        ndmi_change=change.get("ndmi_change"),
        forest_loss_ha=loss.get("forest_loss_hectares"),
        loss_pct=loss.get("loss_percentage"),
        forest_area_before=loss.get("forest_area_before_ha"),
        forest_area_after=loss.get("forest_area_after_ha"),
        usable_pixel_pct=usable_pct,
        overlap_pct=overlap_pct,
        excluded_loss_ha=outside_ha,
        inside_loss_ha=inside_ha,
        decline_area_ha=change.get("ndvi_decline_area_ha"),
        decline_pct=change.get("decline_pct"),
        observation_gap_days=obs_gap,
    )

    # ── Step 13: Risk scoring ─────────────────────────────────────────────
    model_path = _REGISTRY.get_production_model_path("risk_model")
    risk_result = predict_risk(features, model_path=model_path)

    print(f"[pipeline] Risk: {risk_result['rule_level']} (score={risk_result['rule_score']:.1f})")

    # ── Step 14: Evidence ─────────────────────────────────────────────────
    evidence_summary = build_evidence(
        ndvi_change=change.get("ndvi_change"),
        ndmi_change=change.get("ndmi_change"),
        forest_loss_ha=loss.get("forest_loss_hectares"),
        quality_level=quality_level,
        boundary_assessment=excl_assess,
        excluded_loss_ha=outside_ha,
        inside_loss_ha=inside_ha,
        decline_pct=change.get("decline_pct"),
        observation_date=after_date,
        previous_date=before_date,
    )

    # ── Step 15: Thumbnail URLs ───────────────────────────────────────────
    before_url = client.get_thumbnail_url(before_image, geometry)
    after_url  = client.get_thumbnail_url(after_image, geometry)

    # ── Assemble response ─────────────────────────────────────────────────
    response = SatelliteAnalysisResponse(
        status=STATUS_NEW_OBSERVATION,
        farm_id=farm_id,
        processing_timestamp=now,
        message=None,

        observation=ObservationInfo(
            date=after_date,
            previous_date=before_date,
            image_id=after_image_id,
        ),

        quality=QualityInfo(
            level=quality_level,
            usable_pixel_percentage=usable_pct,
            cloud_probability=float(cloud_prob_used),
        ),

        forest=ForestInfo(
            ndvi_before=change.get("ndvi_before"),
            ndvi_after=change.get("ndvi_after"),
            ndvi_change=change.get("ndvi_change"),
            ndmi_before=change.get("ndmi_before"),
            ndmi_after=change.get("ndmi_after"),
            ndmi_change=change.get("ndmi_change"),
            forest_area_before_ha=loss.get("forest_area_before_ha"),
            forest_area_after_ha=loss.get("forest_area_after_ha"),
            forest_loss_hectares=loss.get("forest_loss_hectares"),
        ),

        risk=RiskInfo(
            score=risk_result.get("final_score"),
            level=risk_result.get("final_level", RISK_REVIEW),
            model_version=risk_result.get("model_version"),
            model_status=risk_result.get("model_status", "RULE_BASED"),
        ),

        boundary=BoundaryInfo(
            boundary_manipulation_score=manip_score,
            excluded_loss_hectares=outside_ha if outside_ha else None,
            inside_loss_hectares=inside_ha if inside_ha else None,
            total_detected_loss_ha=total_ha if total_ha else None,
            overlap_percentage=overlap_pct,
        ),

        evidence=EvidenceInfo(
            before_image_url=before_url,
            after_image_url=after_url,
            loss_geojson=loss.get("loss_geojson"),
            summary=evidence_summary,
        ),
    )

    return response.to_dict()