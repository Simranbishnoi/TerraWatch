"""
TerraWatch — satellite_service.py
===================================
Bridges Simran's backend with Greeshma's satellite engine.

Called by the analysis route to trigger real GEE analysis and
persist the result to the database.

Usage (in analysis.py route):
    from app.services.satellite_service import run_analysis_for_farm
    result = await run_analysis_for_farm(db, farm_id)
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone, date
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

# ── Import Greeshma's satellite engine ───────────────────────────────────────
# Add repo root to path so satellite_engine is importable
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from satellite_engine.src.pipeline import run_satellite_analysis

from app.models.farm import Farm
from app.models.analysis import Analysis


# ── Main service function ─────────────────────────────────────────────────────

def run_analysis_for_farm(
    db: Session,
    farm_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the satellite analysis pipeline for a farm and save results to DB.

    Parameters
    ----------
    db        : SQLAlchemy session.
    farm_id   : Farm primary key.
    start_date: "YYYY-MM-DD" — defaults to 1 year ago.
    end_date  : "YYYY-MM-DD" — defaults to today.

    Returns
    -------
    dict — full pipeline result (Simran's expected JSON format).

    Raises
    ------
    ValueError if farm not found or boundary missing.
    """
    # 1. Fetch farm from DB
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise ValueError(f"Farm {farm_id} not found.")

    if not farm.boundary:
        raise ValueError(f"Farm {farm_id} has no boundary polygon.")

    # 2. Set date range defaults
    today = date.today().isoformat()
    one_year_ago = date(date.today().year - 1, date.today().month, date.today().day).isoformat()

    start = start_date or one_year_ago
    end   = end_date   or today

    # 3. Get previous observation date (last analysis for this farm)
    last_analysis = (
        db.query(Analysis)
        .filter(Analysis.farm_id == farm_id)
        .order_by(Analysis.created_at.desc())
        .first()
    )
    previous_obs_date = _extract_observation_date(last_analysis)

    # 4. Build request for Greeshma's pipeline
    request = {
        "farm_id":                   farm_id,
        "boundary":                  farm.boundary,   # GeoJSON Polygon dict
        "start_date":                start,
        "end_date":                  end,
        "previous_observation_date": previous_obs_date,
    }

    # 5. Run satellite analysis
    result = run_satellite_analysis(request)

    # 6. Persist result to DB if a new observation was found
    if result.get("status") == "NEW_OBSERVATION":
        _save_analysis_to_db(db, farm_id, result)

    return result


def _save_analysis_to_db(
    db: Session,
    farm_id: int,
    result: Dict[str, Any],
) -> Analysis:
    """
    Save the pipeline result to the analyses table.
    Maps Greeshma's output fields → Simran's DB columns.
    """
    analysis = Analysis(
        farm_id=farm_id,
        image_url=result.get("after_image"),           # thumbnail URL or None
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
    """Extract the current_date from the last analysis record if available."""
    if analysis is None:
        return None
    # Try to get current_date from result_data if stored, else use created_at
    if hasattr(analysis, "current_date") and analysis.current_date:
        return analysis.current_date
    return None
