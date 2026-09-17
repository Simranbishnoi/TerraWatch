"""
TerraWatch Google Earth Engine client.

Handles authentication and initialisation of the Earth Engine API.
Uses service account credentials from gee_credentials.json for reliable
server-side authentication (no user login needed).
"""

import os
from pathlib import Path

import ee
from dotenv import load_dotenv

# Load .env from satellite_engine/ directory (one level above src/)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)

_GEE_INITIALIZED = False

# Repo root = two levels up from src/
_REPO_ROOT = Path(__file__).resolve().parents[2]


def get_project_id() -> str:
    """Return the configured GEE project ID."""
    project_id = os.getenv("GEE_PROJECT_ID", "").strip()
    if not project_id:
        raise EnvironmentError(
            "GEE_PROJECT_ID is not set. "
            "Create satellite_engine/.env with GEE_PROJECT_ID=your-project-id."
        )
    return project_id


def _get_credentials_path() -> Path | None:
    """Return path to service account credentials JSON, or None if not set."""
    creds_path = os.getenv("GEE_CREDENTIALS_PATH", "").strip()
    if not creds_path:
        return None
    # Try absolute first, then relative to repo root
    p = Path(creds_path)
    if p.is_absolute() and p.exists():
        return p
    relative = _REPO_ROOT / creds_path
    if relative.exists():
        return relative
    return None


def initialize_gee(project_id: str | None = None) -> None:
    """
    Initialize Google Earth Engine.

    Authentication priority:
    1. Service account credentials (GEE_CREDENTIALS_PATH in .env)
    2. Application default credentials (gcloud auth / user login)

    Parameters
    ----------
    project_id : str | None
        GCP project registered for Earth Engine. When None the value is read
        from the GEE_PROJECT_ID environment variable.
    """
    global _GEE_INITIALIZED

    if _GEE_INITIALIZED:
        return  # already initialised in this process

    project = project_id or get_project_id()
    creds_path = _get_credentials_path()

    try:
        if creds_path:
            # ── Service account auth (server-side, no user login needed) ──
            credentials = ee.ServiceAccountCredentials(
                email=os.getenv(
                    "GEE_SERVICE_ACCOUNT",
                    "terrawatch@terrawatch-508816.iam.gserviceaccount.com"
                ),
                key_file=str(creds_path),
            )
            ee.Initialize(credentials=credentials, project=project)
            print(f"[GEE] Initialized with service account: {creds_path.name}")
        else:
            # ── Fallback: application default credentials ──────────────────
            ee.Initialize(project=project)
            print(f"[GEE] Initialized with project: {project}")

        _GEE_INITIALIZED = True

    except ee.EEException as exc:
        raise RuntimeError(
            f"Earth Engine initialization failed for project '{project}'. "
            "Ensure the service account has the 'Earth Engine Resource Writer' IAM role "
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