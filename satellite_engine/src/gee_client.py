"""
TerraWatch Google Earth Engine client.

Handles authentication and initialisation of the Earth Engine API.
Reads project ID from the GEE_PROJECT_ID environment variable or
the satellite_engine/.env file.
"""

import os
from pathlib import Path

import ee
from dotenv import load_dotenv

# Load .env from satellite_engine/ directory (one level above src/)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)

_GEE_INITIALIZED = False


def get_project_id() -> str:
    """Return the configured GEE project ID."""
    project_id = os.getenv("GEE_PROJECT_ID", "").strip()
    if not project_id:
        raise EnvironmentError(
            "GEE_PROJECT_ID is not set. "
            "Create satellite_engine/.env with GEE_PROJECT_ID=your-project-id."
        )
    return project_id


def initialize_gee(project_id: str | None = None) -> None:
    """
    Initialize Google Earth Engine.

    Parameters
    ----------
    project_id : str | None
        GCP project registered for Earth Engine.  When None the value is read
        from the GEE_PROJECT_ID environment variable.

    Raises
    ------
    EnvironmentError
        When no project ID is available.
    RuntimeError
        When Earth Engine authentication or initialisation fails.
    """
    global _GEE_INITIALIZED

    if _GEE_INITIALIZED:
        return  # already initialised in this process

    project = project_id or get_project_id()

    try:
        ee.Initialize(project=project)
        _GEE_INITIALIZED = True
        print(f"[GEE] Initialized with project: {project}")

    except ee.EEException as exc:
        raise RuntimeError(
            f"Earth Engine initialization failed for project '{project}'. "
            "Ensure the account has the 'Earth Engine Resource Writer' IAM role "
            "and the Earth Engine API is enabled. "
            f"Original error: {exc}"
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            "Unexpected error initializing Google Earth Engine. "
            f"Original error: {exc}"
        ) from exc


def require_gee(project_id: str | None = None) -> None:
    """Call initialize_gee if not already done."""
    if not _GEE_INITIALIZED:
        initialize_gee(project_id)


if __name__ == "__main__":
    initialize_gee()
    print("GEE client test: OK")