"""
pcd_hyperaxes_core - Point Cloud Analysis for Hyperaxes Applications

A comprehensive Python module for point cloud comparison, registration, and difference detection.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

__version__ = "1.0.0"
__author__ = "Nicola Sabino"
__company__ = "Hyperaxes"
__license__ = "MIT"

# Export main classes and functions for easy access
from pcd_hyperaxes_core.core.io import load_point_cloud, save_point_cloud
from pcd_hyperaxes_core.core.preprocessing import preprocess_point_cloud
from pcd_hyperaxes_core.core.registration import register_point_clouds
from pcd_hyperaxes_core.core.analysis import compute_cloud_distances, analyze_changes
from pcd_hyperaxes_core.core.clustering import detect_missing_regions
from pcd_hyperaxes_core.core.tiling import (
    Bounds,
    compute_bounds,
    find_overlap,
    extract_tile,
    compute_tile_bounds,
    extract_comparable_tiles,
    save_tile_metadata,
)
from pcd_hyperaxes_core.config import (
    AnalysisConfig,
    PreprocessingConfig,
    RegistrationConfig,
    VisualizationConfig,
    OutputConfig,
    LoggingConfig,
    PipelineConfig,
)

__all__ = [
    "load_point_cloud",
    "save_point_cloud",
    "preprocess_point_cloud",
    "register_point_clouds",
    "compute_cloud_distances",
    "analyze_changes",
    "detect_missing_regions",
    "Bounds",
    "compute_bounds",
    "find_overlap",
    "extract_tile",
    "compute_tile_bounds",
    "extract_comparable_tiles",
    "save_tile_metadata",
    "AnalysisConfig",
    "PreprocessingConfig",
    "RegistrationConfig",
    "VisualizationConfig",
    "OutputConfig",
    "LoggingConfig",
    "PipelineConfig",
]
