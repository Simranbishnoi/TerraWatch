"""
Tests for the JSON contract (request validation + response structure).
"""

import pytest
from satellite_engine.src.contracts.request import SatelliteAnalysisRequest
from satellite_engine.src.contracts.response import (
    SatelliteAnalysisResponse,
    STATUS_INVALID_BOUNDARY,
)


VALID_BOUNDARY = {
    "type": "Polygon",
    "coordinates": [[
        [-62.20, -10.50], [-62.19, -10.50],
        [-62.19, -10.51], [-62.20, -10.51],
        [-62.20, -10.50],
    ]],
}

VALID_REQUEST = dict(
    farm_id=1,
    boundary=VALID_BOUNDARY,
    start_date="2023-01-01",
    end_date="2024-01-01",
    previous_observation_date=None,
)


class TestRequestValidation:
    def test_valid_request_passes(self):
        req = SatelliteAnalysisRequest.from_dict(VALID_REQUEST)
        req.validate()  # must not raise

    def test_negative_farm_id_raises(self):
        bad = {**VALID_REQUEST, "farm_id": -1}
        req = SatelliteAnalysisRequest.from_dict(bad)
        with pytest.raises(ValueError, match="farm_id"):
            req.validate()

    def test_start_after_end_raises(self):
        bad = {**VALID_REQUEST, "start_date": "2025-01-01", "end_date": "2024-01-01"}
        req = SatelliteAnalysisRequest.from_dict(bad)
        with pytest.raises(ValueError, match="start_date"):
            req.validate()

    def test_invalid_start_date_raises(self):
        bad = {**VALID_REQUEST, "start_date": "not-a-date"}
        req = SatelliteAnalysisRequest.from_dict(bad)
        with pytest.raises(ValueError):
            req.validate()

    def test_from_dict_roundtrip(self):
        req = SatelliteAnalysisRequest.from_dict(VALID_REQUEST)
        d   = req.to_dict()
        assert d["farm_id"] == VALID_REQUEST["farm_id"]
        assert d["boundary"] == VALID_BOUNDARY


class TestResponseStructure:
    def test_error_response_has_required_keys(self):
        resp = SatelliteAnalysisResponse.error_response(
            farm_id=1,
            status=STATUS_INVALID_BOUNDARY,
            message="Test error",
        ).to_dict()

        required = {
            "status", "farm_id", "processing_timestamp",
            "ndvi_before", "ndvi_after", "ndvi_change",
            "forest_loss_hectares", "risk_score", "risk_level",
            "evidence_summary", "loss_geojson",
        }
        for key in required:
            assert key in resp, f"Missing key: {key}"

    def test_error_response_no_fake_scores(self):
        resp = SatelliteAnalysisResponse.error_response(
            farm_id=1,
            status=STATUS_INVALID_BOUNDARY,
            message="Test",
        ).to_dict()
        assert resp["risk_score"] is None
        assert resp["ndvi_change"] is None
