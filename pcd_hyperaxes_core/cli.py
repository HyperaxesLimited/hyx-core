"""
Command-line interface for pcd_hyperaxes_core.

Provides a comprehensive CLI for point cloud analysis with multiple execution modes.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import argparse
import sys
from pathlib import Path
import logging
from typing import Optional
import numpy as np

__version__ = "1.0.0"
__author__ = "Nicola Sabino"
__company__ = "Hyperaxes"

from pcd_hyperaxes_core.config import (
    PipelineConfig,
    PreprocessingConfig,
    RegistrationConfig,
    AnalysisConfig,
    NoiseFilterConfig,
    VisualizationConfig,
    OutputConfig,
    LoggingConfig,
)
from pcd_hyperaxes_core.core.io import load_point_cloud
from pcd_hyperaxes_core.core.preprocessing import preprocess_point_cloud
from pcd_hyperaxes_core.core.registration import register_point_clouds
from pcd_hyperaxes_core.core.analysis import compute_cloud_distances, analyze_changes
from pcd_hyperaxes_core.core.clustering import detect_missing_regions
from pcd_hyperaxes_core.visualization.heatmap import create_distance_heatmap
from pcd_hyperaxes_core.visualization.viewer import visualize_regions, show_visualization
from pcd_hyperaxes_core.output.models import AnalysisResults, ClusterInfo
from pcd_hyperaxes_core.output.formatters import ResultFormatter
from pcd_hyperaxes_core.utils.logging import setup_logging
from pcd_hyperaxes_core.utils.validation import (
    validate_file_exists,
    validate_file_format,
    validate_positive_number,
)

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""

    parser = argparse.ArgumentParser(
        prog="pcd-hyperaxes",
        description=(
            f"Point Cloud Difference Analysis Tool\n"
            f"Author: {__author__} | Company: {__company__}\n"
            "Analyzes differences between two point clouds using registration and clustering."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic comparison with visualization
  pcd-hyperaxes source.ply target.ply

  # Save results to JSON file
  pcd-hyperaxes source.las target.las -o results.json

  # Centroid-only mode without plots
  pcd-hyperaxes source.ply target.ply --mode centroid --no-plot

  # Custom voxel size and thresholds
  pcd-hyperaxes source.ply target.ply --voxel-size 0.05 --distance-threshold 0.3

  # Verbose output with CSV export
  pcd-hyperaxes source.ply target.ply -v --format csv -o results.csv

  # Generate full report without point arrays (smaller file)
  pcd-hyperaxes source.ply target.ply --no-points -o results.json

  # Export to GeoJSON for GIS applications
  pcd-hyperaxes source.ply target.ply --format geojson -o differences.geojson
        """,
    )

    # Version
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # Required arguments
    parser.add_argument("source", type=Path, help="Source point cloud file (LAS/LAZ/PLY/PCD/XYZ)")
    parser.add_argument("target", type=Path, help="Target point cloud file (LAS/LAZ/PLY/PCD/XYZ)")

    # Preprocessing options
    preproc_group = parser.add_argument_group("Preprocessing Options")
    preproc_group.add_argument(
        "--voxel-size", type=float, default=0.1, metavar="SIZE", help="Voxel size for downsampling (default: 0.1)"
    )
    preproc_group.add_argument("--no-outlier-removal", action="store_true", help="Disable outlier removal")

    # Registration options
    reg_group = parser.add_argument_group("Registration Options")
    reg_group.add_argument(
        "--skip-registration", action="store_true", help="Skip registration (assume clouds are already aligned)"
    )
    reg_group.add_argument(
        "--max-iterations", type=int, default=100, metavar="N", help="Maximum ICP iterations (default: 100)"
    )

    # Analysis options
    analysis_group = parser.add_argument_group("Analysis Options")
    analysis_group.add_argument(
        "--distance-threshold",
        type=float,
        default=0.2,
        metavar="DIST",
        help="Distance threshold for change detection (default: 0.2)",
    )
    analysis_group.add_argument(
        "--region-threshold",
        type=float,
        default=0.9,
        metavar="DIST",
        help="Distance threshold for region detection (default: 0.9)",
    )
    analysis_group.add_argument(
        "--region-size", type=int, default=10, metavar="N", help="Minimum region size in points (default: 10)"
    )
    analysis_group.add_argument(
        "--no-noise-filtering",
        action="store_true",
        help="Disable noise filtering (use raw threshold only)",
    )
    analysis_group.add_argument(
        "--noise-sigma",
        type=float,
        default=2.0,
        metavar="SIGMA",
        help="Statistical noise tolerance in sigma units (default: 2.0)",
    )
    analysis_group.add_argument(
        "--min-local-support",
        type=int,
        default=3,
        metavar="N",
        help="Minimum neighbors for local validation (default: 3)",
    )

    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--mode",
        choices=["full", "centroid", "summary"],
        default="full",
        help="Output mode: full (all details), centroid (centroids only), summary (statistics only)",
    )
    output_group.add_argument(
        "--format", choices=["json", "text", "csv", "geojson"], default="json", help="Output format (default: json)"
    )
    output_group.add_argument("-o", "--output", type=Path, metavar="FILE", help="Save results to file")
    output_group.add_argument(
        "--no-points", action="store_true", help="Exclude point arrays from output (reduces file size)"
    )

    # Visualization options
    viz_group = parser.add_argument_group("Visualization Options")
    viz_group.add_argument("--no-plot", action="store_true", help="Disable visualization windows")
    viz_group.add_argument("--show-heatmap", action="store_true", help="Show distance heatmap visualization")

    # Logging options
    log_group = parser.add_argument_group("Logging Options")
    log_group.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    log_group.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Logging level (default: INFO)"
    )

    return parser


def build_config_from_args(args: argparse.Namespace) -> PipelineConfig:
    """Build configuration from command-line arguments."""
    config = PipelineConfig()

    # Preprocessing
    config.preprocessing = PreprocessingConfig(voxel_size=args.voxel_size, remove_outliers=not args.no_outlier_removal)

    # Registration
    config.registration = RegistrationConfig(max_iterations=args.max_iterations)
    config.skip_registration = args.skip_registration

    # Analysis
    noise_filter = NoiseFilterConfig(
        enable_statistical_filter=not args.no_noise_filtering,
        enable_local_validation=not args.no_noise_filtering,
        noise_tolerance_sigma=args.noise_sigma,
        min_local_support=args.min_local_support,
    )
    config.analysis = AnalysisConfig(
        distance_threshold=args.distance_threshold,
        region_distance_threshold=args.region_threshold,
        region_size_threshold=args.region_size,
        noise_filter=noise_filter,
    )

    # Visualization
    config.visualization = VisualizationConfig(enable_plots=not args.no_plot, show_heatmap=args.show_heatmap)

    # Output
    mode_map = {"centroid": "centroid_only", "summary": "summary", "full": "full"}
    config.output = OutputConfig(
        mode=mode_map[args.mode], format=args.format, output_file=args.output, include_points=not args.no_points
    )

    # Logging
    config.logging = LoggingConfig(verbose=args.verbose, log_level=args.log_level)

    return config


def validate_inputs(args: argparse.Namespace) -> None:
    """Validate command-line inputs."""
    try:
        validate_file_exists(args.source, "Source file")
        validate_file_exists(args.target, "Target file")

        allowed_formats = {".las", ".laz", ".ply", ".pcd", ".xyz"}
        validate_file_format(args.source, allowed_formats)
        validate_file_format(args.target, allowed_formats)

        validate_positive_number(args.voxel_size, "voxel_size")
        validate_positive_number(args.distance_threshold, "distance_threshold")
        validate_positive_number(args.region_threshold, "region_threshold")

    except Exception as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)


def run_analysis(config: PipelineConfig, source_path: Path, target_path: Path) -> AnalysisResults:
    """Run the complete analysis pipeline."""

    # Load point clouds
    logger.info("Loading point clouds...")
    source_orig = load_point_cloud(source_path)
    target_orig = load_point_cloud(target_path)

    orig_source_count = len(source_orig.points)
    orig_target_count = len(target_orig.points)

    # Preprocess
    logger.info("Preprocessing point clouds...")
    source = preprocess_point_cloud(source_orig, config.preprocessing)
    target = preprocess_point_cloud(target_orig, config.preprocessing)

    proc_source_count = len(source.points)
    proc_target_count = len(target.points)

    # Registration
    if not config.skip_registration:
        logger.info("Registering point clouds...")
        source, transformation = register_point_clouds(source, target, config.preprocessing.voxel_size, config.registration)

    # Compute distances
    logger.info("Computing distances...")
    distances = compute_cloud_distances(source, target, config.analysis)

    distance_stats = {
        "min": float(np.min(distances)),
        "max": float(np.max(distances)),
        "mean": float(np.mean(distances)),
        "median": float(np.median(distances)),
        "std": float(np.std(distances)),
    }

    # Analyze changes
    logger.info("Analyzing changes...")
    source_points = np.asarray(source.points)
    change_indices, change_stats = analyze_changes(distances, config.analysis, source_points)

    # Detect regions
    logger.info("Detecting regions...")
    regions, missing_indices, region_labels = detect_missing_regions(source, target, distances, config.analysis)

    # Build cluster info
    all_points = np.asarray(source.points)
    include_points = config.output.include_points

    clusters = [ClusterInfo.from_indices(i, region, all_points, include_points) for i, region in enumerate(regions, 1)]

    # Create results
    results = AnalysisResults(
        source_file=str(source_path),
        target_file=str(target_path),
        total_source_points=orig_source_count,
        total_target_points=orig_target_count,
        preprocessed_source_points=proc_source_count,
        preprocessed_target_points=proc_target_count,
        distance_stats=distance_stats,
        change_stats=change_stats,
        num_clusters=len(regions),
        clusters=clusters,
    )

    # Visualization
    if config.visualization.enable_plots:
        if config.visualization.show_heatmap:
            heatmap = create_distance_heatmap(source, distances, config.visualization)
            show_visualization([heatmap], config.visualization)

        if len(missing_indices) > 0:
            colored_pcd = visualize_regions(source, missing_indices, config.visualization)
            show_visualization([colored_pcd], config.visualization)

    return results


def main(argv: Optional[list] = None) -> int:
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Setup logging
    logging_config = LoggingConfig(verbose=args.verbose, log_level=args.log_level)
    setup_logging(logging_config)

    logger.info(f"pcd_hyperaxes_core v{__version__}")
    logger.info(f"Author: {__author__} | Company: {__company__}")

    # Validate inputs
    validate_inputs(args)

    # Build configuration
    config = build_config_from_args(args)

    try:
        # Run analysis
        results = run_analysis(config, args.source, args.target)

        # Format and output results
        formatter = ResultFormatter(config.output)
        output = formatter.format_and_save(results)

        # Print to console
        print(output)

        logger.info("Analysis complete")
        return 0

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
