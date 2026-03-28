"""
Function executor that calls HyperAxes Core functionality.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any

from pcd_hyperaxes_core import (
    load_point_cloud,
    preprocess_point_cloud,
    register_point_clouds,
    compute_cloud_distances,
    analyze_changes,
    detect_missing_regions,
)
from pcd_hyperaxes_core.config import (
    PreprocessingConfig,
    AnalysisConfig,
    NoiseFilterConfig,
    OutputConfig,
)
from pcd_hyperaxes_core.output.models import AnalysisResults, ClusterInfo
from pcd_hyperaxes_core.output.formatters import ResultFormatter
from pcd_hyperaxes_core.llm.state import ConversationState

logger = logging.getLogger(__name__)


class HyperAxesFunctionExecutor:
    """Executes functions called by the LLM using HyperAxes Core."""

    # Supported file formats
    SUPPORTED_FORMATS = {".las", ".laz", ".ply", ".pcd", ".xyz"}

    def __init__(self, state: ConversationState):
        self.state = state

    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function and return result.

        Args:
            function_name: Name of function to execute
            arguments: Function arguments

        Returns:
            Dict with 'success', 'message', and optionally 'data'
        """
        try:
            if function_name == "set_source_file":
                return self._set_source_file(arguments["file_path"])
            elif function_name == "set_target_file":
                return self._set_target_file(arguments["file_path"])
            elif function_name == "configure_preprocessing":
                return self._configure_preprocessing(arguments)
            elif function_name == "configure_analysis":
                return self._configure_analysis(arguments)
            elif function_name == "configure_output":
                return self._configure_output(arguments)
            elif function_name == "run_analysis":
                return self._run_analysis(arguments)
            elif function_name == "get_current_state":
                return self._get_current_state()
            elif function_name == "get_results_summary":
                return self._get_results_summary()
            elif function_name == "save_results":
                return self._save_results(arguments)
            else:
                return {"success": False, "message": f"Unknown function: {function_name}"}

        except Exception as e:
            logger.error(f"Error executing {function_name}: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def _set_source_file(self, file_path: str) -> Dict:
        """Set source point cloud file."""
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            return {"success": False, "message": f"File not found: {file_path}"}

        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return {
                "success": False,
                "message": f"Unsupported format: {path.suffix}. Supported: {', '.join(self.SUPPORTED_FORMATS)}",
            }

        self.state.source_file = path
        logger.info(f"Source file set to: {path}")

        return {
            "success": True,
            "message": f"Source file set to: {path.name}",
            "data": {"file_path": str(path), "format": path.suffix},
        }

    def _set_target_file(self, file_path: str) -> Dict:
        """Set target point cloud file."""
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            return {"success": False, "message": f"File not found: {file_path}"}

        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return {
                "success": False,
                "message": f"Unsupported format: {path.suffix}. Supported: {', '.join(self.SUPPORTED_FORMATS)}",
            }

        self.state.target_file = path
        logger.info(f"Target file set to: {path}")

        return {
            "success": True,
            "message": f"Target file set to: {path.name}",
            "data": {"file_path": str(path), "format": path.suffix},
        }

    def _configure_preprocessing(self, arguments: Dict) -> Dict:
        """Configure preprocessing parameters."""
        # Get existing config or create new one
        config = self.state.preprocessing_config or PreprocessingConfig()

        # Update with provided arguments
        if "voxel_size" in arguments:
            config.voxel_size = arguments["voxel_size"]
        if "remove_outliers" in arguments:
            config.remove_outliers = arguments["remove_outliers"]

        self.state.preprocessing_config = config
        logger.info(f"Preprocessing configured: voxel_size={config.voxel_size}, remove_outliers={config.remove_outliers}")

        return {
            "success": True,
            "message": f"Preprocessing configured: voxel size={config.voxel_size}m, outlier removal={'enabled' if config.remove_outliers else 'disabled'}",
            "data": {"voxel_size": config.voxel_size, "remove_outliers": config.remove_outliers},
        }

    def _configure_analysis(self, arguments: Dict) -> Dict:
        """Configure analysis parameters."""
        # Get existing config or create new one
        config = self.state.analysis_config or AnalysisConfig()

        # Update with provided arguments
        if "distance_threshold" in arguments:
            config.distance_threshold = arguments["distance_threshold"]
        if "region_threshold" in arguments:
            config.region_distance_threshold = arguments["region_threshold"]
        if "region_size" in arguments:
            config.region_size_threshold = arguments["region_size"]

        # Update noise filtering parameters
        if any(key in arguments for key in ["enable_noise_filtering", "noise_sigma", "min_local_support"]):
            if "enable_noise_filtering" in arguments:
                config.noise_filter.enable_statistical_filter = arguments["enable_noise_filtering"]
                config.noise_filter.enable_local_validation = arguments["enable_noise_filtering"]
            if "noise_sigma" in arguments:
                config.noise_filter.noise_tolerance_sigma = arguments["noise_sigma"]
            if "min_local_support" in arguments:
                config.noise_filter.min_local_support = arguments["min_local_support"]

        self.state.analysis_config = config
        logger.info(
            f"Analysis configured: distance_threshold={config.distance_threshold}, "
            f"region_threshold={config.region_distance_threshold}, region_size={config.region_size_threshold}, "
            f"noise_filtering={config.noise_filter.enable_statistical_filter}"
        )

        return {
            "success": True,
            "message": f"Analysis configured: distance threshold={config.distance_threshold}m, region threshold={config.region_distance_threshold}m, min region size={config.region_size_threshold} points, noise filtering={'enabled' if config.noise_filter.enable_statistical_filter else 'disabled'}",
            "data": {
                "distance_threshold": config.distance_threshold,
                "region_threshold": config.region_distance_threshold,
                "region_size": config.region_size_threshold,
                "noise_filtering_enabled": config.noise_filter.enable_statistical_filter,
                "noise_sigma": config.noise_filter.noise_tolerance_sigma,
                "min_local_support": config.noise_filter.min_local_support,
            },
        }

    def _configure_output(self, arguments: Dict) -> Dict:
        """Configure output parameters."""
        # Get existing config or create new one
        config = self.state.output_config or OutputConfig()

        # Update with provided arguments
        if "format" in arguments:
            config.format = arguments["format"]
        if "mode" in arguments:
            config.mode = arguments["mode"]
        if "output_file" in arguments:
            config.output_file = Path(arguments["output_file"])

        self.state.output_config = config
        logger.info(f"Output configured: format={config.format}, mode={config.mode}")

        return {
            "success": True,
            "message": f"Output configured: format={config.format}, mode={config.mode}",
            "data": {"format": config.format, "mode": config.mode},
        }

    def _run_analysis(self, arguments: Dict) -> Dict:
        """Execute the complete analysis pipeline."""
        if not self.state.is_ready_for_analysis():
            return {
                "success": False,
                "message": "Missing required files. Please set both source and target files first.",
            }

        show_visualization = arguments.get("show_visualization", False)

        try:
            # Get configurations with defaults
            pipeline_config = self.state.get_config()
            prep_config = pipeline_config.preprocessing
            reg_config = pipeline_config.registration
            analysis_config = pipeline_config.analysis

            logger.info("Starting analysis pipeline...")

            # 1. Load point clouds
            print("   📂 Loading point clouds...", flush=True)
            logger.info("Loading point clouds...")
            source_orig = load_point_cloud(self.state.source_file)
            target_orig = load_point_cloud(self.state.target_file)

            orig_source_points = len(source_orig.points)
            orig_target_points = len(target_orig.points)

            # 2. Preprocess
            print("   🔧 Preprocessing point clouds...", flush=True)
            logger.info("Preprocessing point clouds...")
            source = preprocess_point_cloud(source_orig, prep_config)
            target = preprocess_point_cloud(target_orig, prep_config)

            prep_source_points = len(source.points)
            prep_target_points = len(target.points)

            # 3. Register
            print("   🔄 Registering with ICP (this may take a moment)...", flush=True)
            logger.info("Registering point clouds with ICP...")
            source_aligned, transform = register_point_clouds(source, target, prep_config.voxel_size, reg_config)
            self.state.source_aligned = source_aligned

            # 4. Compute distances
            print("   📏 Computing distances...", flush=True)
            logger.info("Computing point-to-point distances...")
            distances = compute_cloud_distances(source_aligned, target, analysis_config)

            # 5. Analyze changes
            print("   🔍 Analyzing changes...", flush=True)
            logger.info("Analyzing changes...")
            all_points = np.asarray(source_aligned.points)
            change_indices, change_stats = analyze_changes(distances, analysis_config, all_points)

            # 6. Detect regions
            print("   🎯 Clustering change regions...", flush=True)
            logger.info("Detecting change regions...")
            regions, missing_indices, region_labels = detect_missing_regions(
                source_aligned, target, distances, analysis_config
            )

            # 7. Build results
            print("   📊 Building results...", flush=True)
            logger.info("Building results...")
            clusters = [
                ClusterInfo.from_indices(i, region, all_points, include_points=True) for i, region in enumerate(regions, 1)
            ]

            # Distance statistics
            distance_stats = {
                "min": float(np.min(distances)),
                "max": float(np.max(distances)),
                "mean": float(np.mean(distances)),
                "median": float(np.median(distances)),
                "std": float(np.std(distances)),
            }

            results = AnalysisResults(
                source_file=str(self.state.source_file),
                target_file=str(self.state.target_file),
                total_source_points=orig_source_points,
                total_target_points=orig_target_points,
                preprocessed_source_points=prep_source_points,
                preprocessed_target_points=prep_target_points,
                distance_stats=distance_stats,
                change_stats=change_stats,
                num_clusters=len(regions),
                clusters=clusters,
            )

            self.state.last_results = results

            print(f"   ✅ Analysis complete! Found {len(regions)} change regions", flush=True)
            logger.info(f"Analysis complete. Found {len(regions)} regions of differences.")

            # 8. Visualize if requested
            if show_visualization:
                try:
                    from pcd_hyperaxes_core.llm.webviewer import create_web_visualization

                    print("   🌐 Creating 3D web visualization...", flush=True)
                    logger.info("Creating web visualization...")
                    viz_path = create_web_visualization(results, source_aligned, auto_open=True)
                    print("   ✅ Visualization opened in browser", flush=True)
                    logger.info(f"Visualization opened at: {viz_path}")
                except Exception as viz_error:
                    logger.warning(f"Visualization failed: {viz_error}")

            return {
                "success": True,
                "message": f"Analysis complete. Found {len(regions)} regions of differences with {change_stats.get('num_changed_points', 0)} changed points.",
                "data": {
                    "num_clusters": len(regions),
                    "num_changed_points": change_stats.get("num_changed_points", 0),
                    "mean_distance": distance_stats["mean"],
                    "max_distance": distance_stats["max"],
                    "total_points_analyzed": prep_source_points,
                },
            }

        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            return {"success": False, "message": f"Analysis failed: {str(e)}"}

    def _get_current_state(self) -> Dict:
        """Get current configuration state."""
        summary = self.state.get_summary()

        data = {
            "summary": summary,
            "source_file": str(self.state.source_file) if self.state.source_file else None,
            "target_file": str(self.state.target_file) if self.state.target_file else None,
            "ready_for_analysis": self.state.is_ready_for_analysis(),
        }

        if self.state.preprocessing_config:
            data["preprocessing"] = {
                "voxel_size": self.state.preprocessing_config.voxel_size,
                "remove_outliers": self.state.preprocessing_config.remove_outliers,
            }

        if self.state.analysis_config:
            data["analysis"] = {
                "distance_threshold": self.state.analysis_config.distance_threshold,
                "region_threshold": self.state.analysis_config.region_distance_threshold,
                "region_size": self.state.analysis_config.region_size_threshold,
            }

        return {"success": True, "message": summary, "data": data}

    def _get_results_summary(self) -> Dict:
        """Get summary of last analysis results."""
        if not self.state.last_results:
            return {"success": False, "message": "No analysis results available. Run analysis first."}

        results = self.state.last_results

        summary = f"Found {results.num_clusters} clusters. "
        summary += f"Distance stats: mean={results.distance_stats['mean']:.3f}m, "
        summary += f"max={results.distance_stats['max']:.3f}m. "
        summary += f"Changed points: {results.change_stats.get('num_changed_points', 0)}"

        data = {
            "num_clusters": results.num_clusters,
            "distance_stats": results.distance_stats,
            "change_stats": results.change_stats,
            "total_source_points": results.total_source_points,
            "preprocessed_source_points": results.preprocessed_source_points,
        }

        return {"success": True, "message": summary, "data": data}

    def _save_results(self, arguments: Dict) -> Dict:
        """Save analysis results to file."""
        if not self.state.last_results:
            return {"success": False, "message": "No analysis results available. Run analysis first."}

        output_path = Path(arguments["output_path"]).expanduser()
        format_type = arguments.get("format") or (self.state.output_config.format if self.state.output_config else "json")
        mode = self.state.output_config.mode if self.state.output_config else "full"

        try:
            formatter = ResultFormatter(self.state.last_results, mode=mode, format_type=format_type)
            formatter.save(output_path)
            logger.info(f"Results saved to: {output_path}")

            return {
                "success": True,
                "message": f"Results saved to: {output_path}",
                "data": {"output_path": str(output_path), "format": format_type, "mode": mode},
            }

        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return {"success": False, "message": f"Failed to save results: {str(e)}"}
