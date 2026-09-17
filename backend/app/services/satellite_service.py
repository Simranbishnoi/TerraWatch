"""
TerraWatch — satellite_service.py
Bridges Simran's backend with Greeshma's satellite engine.
Uses new terrawatch-508816 GEE project with service account auth.
"""

import sys
from pathlib import Path
from datetime import date
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

# ── Import Greeshma's satellite engine ───────────────────────────────────────
# File path: backend/app/services/satellite_service.py
# parents[0]=services  parents[1]=app  parents[2]=backend  parents[3]=TerraWatch
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from satellite_engine.src.pipeline import run_satellite_analysis

from app.models.farm import Farm
from app.models.analysis import Analysis


# ── Direct boundary analysis (frontend primary flow) ─────────────────────────

def run_analysis_direct(
    boundary: Dict[str, Any],
    start_date: str,
    end_date: str,
    previous_observation_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run satellite analysis directly from a boundary polygon.
    Called by POST /api/analysis/analyze (what the frontend 'Analyze' button uses).
    No farm record needed.
    """
    request = {
        "farm_id":                   0,
        "boundary":                  boundary,
        "start_date":                start_date,
        "end_date":                  end_date,
        "previous_observation_date": previous_observation_date,
    }
    result = run_satellite_analysis(request)
    return _enrich_result(result)


# ── Farm-based analysis (saves to DB) ────────────────────────────────────────

def run_analysis_for_farm(
    db: Session,
    farm_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run satellite analysis for a saved farm and persist result to DB.
    """
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise ValueError(f"Farm {farm_id} not found.")
    if not farm.boundary:
        raise ValueError(f"Farm {farm_id} has no boundary polygon.")

    today = date.today().isoformat()
    one_year_ago = date(date.today().year - 1, date.today().month, date.today().day).isoformat()

    last_analysis = (
        db.query(Analysis)
        .filter(Analysis.farm_id == farm_id)
        .order_by(Analysis.created_at.desc())
        .first()
    )

    request = {
        "farm_id":                   farm_id,
        "boundary":                  farm.boundary,
        "start_date":                start_date or one_year_ago,
        "end_date":                  end_date or today,
        "previous_observation_date": _extract_observation_date(last_analysis),
    }

    result = run_satellite_analysis(request)
    result = _enrich_result(result)

    if result.get("status") == "NEW_OBSERVATION":
        _save_analysis_to_db(db, farm_id, result)

    return result


# ── Result enrichment ─────────────────────────────────────────────────────────

def _enrich_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Add frontend-friendly fields: risk_score_pct, deforestation_detected, alert_message."""
    # Map risk_level → percentage for the progress bar
    if result.get("risk_score") is None:
        level = result.get("risk_level", "low")
        result["risk_score_pct"] = {"low": 20, "medium": 55, "high": 87, "very_high": 95}.get(level, 20)
    else:
        result["risk_score_pct"] = round((result["risk_score"] or 0), 1)

    # Fix deforestation_detected — true if measurable loss found
    loss_ha = result.get("forest_loss_hectares") or 0.0
    result["deforestation_detected"] = loss_ha > 0.5 and result.get("status") == "NEW_OBSERVATION"

    # Human-readable alert for the frontend banner
    result["alert_message"] = _build_alert(result)
    return result


def _build_alert(result: Dict[str, Any]) -> str:
    level = result.get("risk_level", "low").upper()
    loss = result.get("forest_loss_hectares") or 0
    pct = result.get("deforestation_percentage") or 0
    if result.get("deforestation_detected"):
        return f"FRAUD RISK: {level} — {loss:.1f} ha forest loss ({pct:.1f}% of farm area)"
    return f"RISK: {level} — No significant deforestation detected"


def _save_analysis_to_db(db: Session, farm_id: int, result: Dict[str, Any]) -> Analysis:
    analysis = Analysis(
        farm_id=farm_id,
        image_url=result.get("after_image"),
        analysis_type="deforestation_detection",
        deforestation_percentage=result.get("deforestation_percentage"),
        confidence_score=result.get("confidence_score"),
        risk_level=result.get("risk_level"),
        result_status="completed",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def _extract_observation_date(analysis: Optional[Analysis]) -> Optional[str]:
    if analysis is None:
        return None
    if hasattr(analysis, "current_date") and analysis.current_date:
        return analysis.current_date
    return None
