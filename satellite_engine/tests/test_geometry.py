"""
Tests for boundary geometry utilities.
All tests are pure-Python (no GEE calls).
"""

import pytest
from unittest.mock import patch, MagicMock
from satellite_engine.src.boundary.geometry import (
    validate_boundary,
    get_bounding_box,
    boundary_from_geojson_feature,
)


VALID_POLYGON = {
    "type": "Polygon",
    "coordinates": [[
        [-62.20, -10.50],
        [-62.19, -10.50],
        [-62.19, -10.51],
        [-62.20, -10.51],
        [-62.20, -10.50],
    ]],
}


class TestValidateBoundary:
    def test_valid_polygon_passes(self):
        validate_boundary(VALID_POLYGON)  # must not raise

    def test_non_dict_raises(self):
        with pytest.raises(ValueError, match="must be a dict"):
            validate_boundary("not a dict")

    def test_wrong_type_raises(self):
        bad = {**VALID_POLYGON, "type": "LineString"}
        with pytest.raises(ValueError, match="must be 'Polygon'"):
            validate_boundary(bad)

    def test_missing_coordinates_raises(self):
        bad = {"type": "Polygon"}
        with pytest.raises(ValueError, match="missing or empty"):
            validate_boundary(bad)

    def test_too_few_positions_raises(self):
        bad = {
            "type": "Polygon",
            "coordinates": [[[-62.20, -10.50], [-62.19, -10.50], [-62.20, -10.50]]],
        }
        with pytest.raises(ValueError, match="at least 4"):
            validate_boundary(bad)

    def test_longitude_out_of_range_raises(self):
        bad = {
            "type": "Polygon",
            "coordinates": [[
                [200.0, -10.50],
                [201.0, -10.50],
                [201.0, -10.51],
                [200.0, -10.51],
                [200.0, -10.50],
            ]],
        }
        with pytest.raises(ValueError, match="longitude"):
            validate_boundary(bad)

    def test_latitude_out_of_range_raises(self):
        bad = {
            "type": "Polygon",
            "coordinates": [[
                [-62.20, -95.0],
                [-62.19, -95.0],
                [-62.19, -96.0],
                [-62.20, -96.0],
                [-62.20, -95.0],
            ]],
        }
        with pytest.raises(ValueError, match="latitude"):
            validate_boundary(bad)

    def test_unclosed_ring_raises(self):
        bad = {
            "type": "Polygon",
            "coordinates": [[
                [-62.20, -10.50],
                [-62.19, -10.50],
                [-62.19, -10.51],
                [-62.20, -10.51],
                # missing closing position
            ]],
        }
        with pytest.raises(ValueError, match="not closed|at least 4"):
            validate_boundary(bad)


class TestGetBoundingBox:
    def test_bounding_box(self):
        min_lon, min_lat, max_lon, max_lat = get_bounding_box(VALID_POLYGON)
        assert min_lon == pytest.approx(-62.20)
        assert max_lon == pytest.approx(-62.19)
        assert min_lat == pytest.approx(-10.51)
        assert max_lat == pytest.approx(-10.50)


class TestBoundaryFromGeoJsonFeature:
    def test_extracts_geometry_from_feature(self):
        feature = {
            "type": "Feature",
            "properties": {},
            "geometry": VALID_POLYGON,
        }
        result = boundary_from_geojson_feature(feature)
        assert result == VALID_POLYGON

    def test_returns_geometry_directly(self):
        result = boundary_from_geojson_feature(VALID_POLYGON)
        assert result == VALID_POLYGON
