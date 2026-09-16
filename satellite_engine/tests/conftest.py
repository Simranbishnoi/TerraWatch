"""
pytest conftest.py for satellite_engine tests.
Adds the TerraWatch project root to sys.path so imports resolve
without installing the package.
"""

import sys
from pathlib import Path

# Project root = two levels above satellite_engine/tests/
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
