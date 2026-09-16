"""
TerraWatch Satellite Engine — Local Demo Runner
================================================
Runs a standalone end-to-end test against Google Earth Engine
without the FastAPI backend.

Usage
-----
    cd TerraWatch
    python satellite_engine/run_demo.py

Prerequisites
-------------
1. GEE authenticated:  ee.Authenticate()
2. satellite_engine/.env  contains GEE_PROJECT_ID=your-project-id
3. Dependencies installed: pip install -r satellite_engine/requirements.txt
"""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path so imports resolve
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from satellite_engine.src.pipeline import run_satellite_analysis


DEMO_REQUEST = {
    "farm_id": 1,
    "boundary": {
        "type": "Polygon",
        "coordinates": [[
            [-62.20, -10.50],
            [-62.19, -10.50],
            [-62.19, -10.51],
            [-62.20, -10.51],
            [-62.20, -10.50],
        ]],
    },
    # Use a 1-year window covering recent Sentinel-2 data
    "start_date": "2023-01-01",
    "end_date":   "2024-01-01",
    # Simulate monitoring: look for observations after this date
    "previous_observation_date": "2023-06-01",
}


def main() -> None:
    print("=" * 60)
    print("  TerraWatch Satellite Engine — Demo Run")
    print("=" * 60)
    print(f"  Farm ID  : {DEMO_REQUEST['farm_id']}")
    print(f"  Start    : {DEMO_REQUEST['start_date']}")
    print(f"  End      : {DEMO_REQUEST['end_date']}")
    print(f"  Previous : {DEMO_REQUEST['previous_observation_date']}")
    print("=" * 60)
    print()

    result = run_satellite_analysis(DEMO_REQUEST)

    print()
    print("=" * 60)
    print("  RESULT")
    print("=" * 60)
    print(f"  Status           : {result.get('status')}")
    print(f"  Observation date : {result.get('observation_date')}")
    print(f"  Previous date    : {result.get('previous_observation_date')}")
    print(f"  Quality          : {result.get('quality_level')}")
    print(f"  Usable pixels    : {result.get('usable_pixel_percentage')}%")
    print(f"  NDVI before      : {result.get('ndvi_before')}")
    print(f"  NDVI after       : {result.get('ndvi_after')}")
    print(f"  NDVI change      : {result.get('ndvi_change')}")
    print(f"  Forest loss      : {result.get('forest_loss_hectares')} ha")
    print(f"  Risk level       : {result.get('risk_level')}")
    print(f"  Risk score       : {result.get('risk_score')}")
    print(f"  Boundary score   : {result.get('boundary_manipulation_score')}")
    print()
    print("  Evidence:")
    for line in (result.get("evidence_summary") or []):
        print(f"    • {line}")
    print()

    if result.get("loss_geojson"):
        n_features = len(result["loss_geojson"].get("features", []))
        print(f"  Loss polygons    : {n_features} feature(s)")

    print()
    print("Full JSON saved to: satellite_engine/outputs/demo_result.json")
    out_path = ROOT / "satellite_engine" / "outputs" / "demo_result.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    print("=" * 60)


if __name__ == "__main__":
    main()
