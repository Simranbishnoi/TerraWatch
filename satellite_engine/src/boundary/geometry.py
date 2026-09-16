"""
TerraWatch — boundary geometry utilities.

Validates GeoJSON farm polygons and converts them to ee.Geometry objects
for use with Google Earth Engine.

GeoJSON coordinate order: [longitude, latitude]
"""

from typing import Any, Dict, List, Tuple

import ee


# ── Public API ───────────────────────────────────────────────────────────────

def validate_boundary(boundary: Dict[str, Any]) -> None:
    """
    Validate a GeoJSON Polygon geometry.

    Parameters
    ----------
    boundary : dict
        GeoJSON geometry object (type must be "Polygon").

    Raises
    ------
    ValueError
        With a descriptive message when validation fails.
    """
    if not isinstance(boundary, dict):
        raise ValueError(f"boundary must be a dict, got {type(boundary).__name__}")

    geom_type = boundary.get("type")
    if geom_type != "Polygon":
        raise ValueError(
            f"boundary.type must be 'Polygon', got {geom_type!r}. "
            "Use a GeoJSON Polygon geometry (not Feature or FeatureCollection)."
        )

    coords = boundary.get("coordinates")
    if not coords or not isinstance(coords, list):
        raise ValueError("boundary.coordinates is missing or empty")

    outer_ring = coords[0]
    if not isinstance(outer_ring, list):
        raise ValueError("boundary.coordinates[0] (outer ring) must be a list of positions")

    if len(outer_ring) < 4:
        raise ValueError(
            f"Outer ring must have at least 4 positions (first=last), got {len(outer_ring)}"
        )

    for i, pos in enumerate(outer_ring):
        if not isinstance(pos, (list, tuple)) or len(pos) < 2:
            raise ValueError(f"Position {i} is not a valid [lon, lat] pair: {pos!r}")
        lon, lat = pos[0], pos[1]
        if not (-180.0 <= lon <= 180.0):
            raise ValueError(
                f"Position {i}: longitude {lon} is out of range [-180, 180]. "
                "Remember GeoJSON uses [longitude, latitude] order."
            )
        if not (-90.0 <= lat <= 90.0):
            raise ValueError(
                f"Position {i}: latitude {lat} is out of range [-90, 90]."
            )

    # Ring closure check (first and last positions should be equal)
    if outer_ring[0] != outer_ring[-1]:
        raise ValueError(
            "Outer ring is not closed: first and last positions must be identical."
        )


def geojson_to_ee_geometry(boundary: Dict[str, Any]) -> ee.Geometry:
    """
    Convert a validated GeoJSON Polygon to an ee.Geometry.Polygon.

    Parameters
    ----------
    boundary : dict
        Valid GeoJSON Polygon geometry.

    Returns
    -------
    ee.Geometry.Polygon
    """
    validate_boundary(boundary)
    coordinates = boundary["coordinates"]
    return ee.Geometry.Polygon(coordinates)


def calculate_area_hectares(geometry: ee.Geometry) -> float:
    """
    Calculate the area of an ee.Geometry in hectares using
    GEE's built-in equal-area calculation.

    Parameters
    ----------
    geometry : ee.Geometry

    Returns
    -------
    float — area in hectares (rounded to 4 d.p.)
    """
    area_m2 = geometry.area(maxError=1).getInfo()
    return round(area_m2 / 10_000, 4)


def get_bounding_box(boundary: Dict[str, Any]) -> Tuple[float, float, float, float]:
    """
    Return (min_lon, min_lat, max_lon, max_lat) for the boundary.
    Useful for quick spatial sanity checks.
    """
    outer_ring = boundary["coordinates"][0]
    lons = [p[0] for p in outer_ring]
    lats = [p[1] for p in outer_ring]
    return min(lons), min(lats), max(lons), max(lats)


def boundary_from_geojson_feature(feature: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract the geometry dict from a GeoJSON Feature.

    Parameters
    ----------
    feature : dict — GeoJSON Feature

    Returns
    -------
    dict — GeoJSON Polygon geometry
    """
    if feature.get("type") == "Feature":
        return feature["geometry"]
    return feature  # already a geometry
