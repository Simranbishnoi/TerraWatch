"""
TerraWatch — change_detection package.
"""
from .ndvi_change import detect_ndvi_decline, compute_ndvi_change_image
from .spectral_change import compute_spectral_change, add_spectral_indices
from .temporal_change import run_temporal_change

__all__ = [
    "detect_ndvi_decline",
    "compute_ndvi_change_image",
    "compute_spectral_change",
    "add_spectral_indices",
    "run_temporal_change",
]
