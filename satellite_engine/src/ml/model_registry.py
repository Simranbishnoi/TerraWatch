"""
TerraWatch — model registry.

Tracks model versions, training metadata, and production paths.
Provides a single place to look up the active production model.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


REGISTRY_PATH = Path(__file__).resolve().parents[3] / "ml_models" / "registry.json"


@dataclass
class ModelRecord:
    name: str
    version: str
    model_type: str          # "rule_based" | "random_forest" | "isolation_forest"
    training_date: str
    features: List[str]
    metrics: Dict[str, float]
    model_path: Optional[str] = None
    notes: str = ""
    is_production: bool = False


class ModelRegistry:
    """
    Simple file-backed model registry.

    Usage
    -----
    registry = ModelRegistry()
    registry.register(ModelRecord(...))
    prod = registry.get_production_model("risk_model")
    """

    def __init__(self, registry_path: Path = REGISTRY_PATH) -> None:
        self.registry_path = registry_path
        self._records: List[ModelRecord] = []
        self._load()

    def _load(self) -> None:
        if self.registry_path.exists():
            with open(self.registry_path, "r") as f:
                raw = json.load(f)
            self._records = [ModelRecord(**r) for r in raw.get("models", [])]

    def _save(self) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"models": [asdict(r) for r in self._records]}
        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def register(self, record: ModelRecord) -> None:
        """Add or update a model record."""
        self._records = [r for r in self._records
                         if not (r.name == record.name and r.version == record.version)]
        self._records.append(record)
        self._save()

    def set_production(self, name: str, version: str) -> None:
        """Mark a specific version as the production model."""
        for r in self._records:
            if r.name == name:
                r.is_production = (r.version == version)
        self._save()

    def get_production_model(self, name: str) -> Optional[ModelRecord]:
        """Return the current production model for a given name."""
        for r in self._records:
            if r.name == name and r.is_production:
                return r
        return None

    def list_models(self, name: Optional[str] = None) -> List[ModelRecord]:
        if name:
            return [r for r in self._records if r.name == name]
        return list(self._records)

    def get_production_model_path(self, name: str) -> Optional[Path]:
        """Return the Path to the production model file, or None."""
        record = self.get_production_model(name)
        if record and record.model_path:
            return Path(record.model_path)
        return None
