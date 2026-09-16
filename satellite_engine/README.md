# TerraWatch — Satellite Engine

The **satellite + ML engine** for TerraWatch farm deforestation monitoring.

## Ownership

This module (`satellite_engine/`) is owned by **Greeshma** on branch `greeshma-satellite-ml`.

| Branch | Owner | Scope |
|--------|-------|-------|
| `main` | Shared | Integration |
| `greeshma-satellite-ml` | Greeshma | `satellite_engine/` |
| `simran-backend` | Simran | `backend/` |

---

## What it does

Receives a farm boundary polygon → queries Google Earth Engine for Sentinel-2 observations → cloud-masks → NDVI → change detection → forest loss → boundary analysis → ML risk score → returns structured JSON.

---

## Setup

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r satellite_engine/requirements.txt

# 3. Create .env
copy satellite_engine\.env.example satellite_engine\.env
# Edit .env and set GEE_PROJECT_ID=your-gee-project-id

# 4. Authenticate with GEE (one-time)
python -c "import ee; ee.Authenticate()"
```

---

## Run the demo

```bash
python satellite_engine/run_demo.py
```

---

## Run tests

```bash
cd TerraWatch
pytest satellite_engine/tests/ -v
```

---

## Integration with Simran's backend

```python
from satellite_engine.src.pipeline import run_satellite_analysis

result = run_satellite_analysis({
    "farm_id": 1,
    "boundary": {...},          # GeoJSON Polygon
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "previous_observation_date": "2024-08-01"  # or None for first run
})
```

---

## Output statuses

| Status | Meaning |
|--------|---------|
| `NEW_OBSERVATION` | New usable Sentinel-2 image found and processed |
| `NO_NEW_OBSERVATION` | No usable image after the previous observation date |
| `NO_USABLE_OBSERVATION` | Images exist but quality is insufficient |
| `INVALID_BOUNDARY` | Farm polygon failed validation |
| `PROCESSING_ERROR` | Unexpected pipeline error |

---

## Important notes

- Sentinel-2 has a **nominal 5-day revisit** but usable observations depend on cloud cover
- NDVI decline alone is **not proof of deforestation** — it is one of several signals
- Risk scores are rule-based until a validated ML model is registered in `ml_models/`
- Never invent satellite dates or fake NDVI values

---

## Directory structure

```
satellite_engine/
├── config/          YAML thresholds and settings
├── gee/             Google Earth Engine JS scripts (for GEE Code Editor)
├── src/             Python source code
│   ├── pipeline.py  ← MAIN ENTRY POINT
│   ├── boundary/
│   ├── ndvi/
│   ├── change_detection/
│   ├── forest/
│   ├── quality/
│   ├── evidence/
│   ├── ml/
│   └── contracts/
├── models/          Feature/training schemas
├── ml_models/       Trained model files
├── tests/           pytest test suite
├── outputs/         Generated results
└── run_demo.py      Local demo runner
```
