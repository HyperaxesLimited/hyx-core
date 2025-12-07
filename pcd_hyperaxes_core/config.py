"""
Configuration classes for the pcd_hyperaxes_core module.

This module defines all configurable parameters for point cloud analysis,
allowing users to customize behavior without modifying code.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class PreprocessingConfig:
    """Configuration for point cloud preprocessing."""

    voxel_size: float = 0.1
    remove_outliers: bool = True
    outlier_nb_neighbors: int = 20
    outlier_std_ratio: float = 2.0
    estimate_normals: bool = True
    normal_search_radius_multiplier: float = 2.0
    normal_max_nn: int = 30


@dataclass
class RegistrationConfig:
    """Configuration for point cloud registration."""

    max_iterations: int = 100
    distance_threshold_multiplier: float = 2.0  # Multiplied by voxel_size
    relative_fitness: float = 1e-6
    relative_rmse: float = 1e-6
    registration_method: str = "point_to_plane"  # or "point_to_point"


@dataclass
class AnalysisConfig:
    """Configuration for change detection analysis."""

    distance_threshold: float = 0.2
    region_distance_threshold: float = 0.9
    region_size_threshold: int = 10
    cluster_neighbors: int = 20


@dataclass
class VisualizationConfig:
    """Configuration for visualization."""

    enable_plots: bool = True
    colormap_style: str = "blue_to_red"  # Options: "blue_to_red", "viridis"
    background_color: tuple[float, float, float] = (0.7, 0.7, 0.7)
    highlight_color: tuple[float, float, float] = (1.0, 0.0, 0.0)
    window_name: str = "Point Cloud Difference Analysis"
    show_heatmap: bool = False


@dataclass
class OutputConfig:
    """Configuration for output formatting."""

    mode: str = "full"  # Options: "full", "centroid_only", "summary"
    format: str = "json"  # Options: "json", "text", "csv"
    output_file: Optional[Path] = None
    save_visualization: bool = False
    visualization_output: Optional[Path] = None


@dataclass
class LoggingConfig:
    """Configuration for logging."""

    verbose: bool = True
    log_level: str = "INFO"  # Options: "DEBUG", "INFO", "WARNING", "ERROR"
    log_file: Optional[Path] = None


@dataclass
class PipelineConfig:
    """Complete pipeline configuration combining all sub-configurations."""

    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    registration: RegistrationConfig = field(default_factory=RegistrationConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Global pipeline options
    skip_registration: bool = False  # If clouds are already aligned
