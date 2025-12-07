"""
Point cloud distance computation and change analysis.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import numpy as np
from scipy.spatial import KDTree
import open3d as o3d
import logging
from typing import Tuple, Dict
from pcd_hyperaxes_core.config import AnalysisConfig

logger = logging.getLogger(__name__)


def compute_cloud_distances(
    source: o3d.geometry.PointCloud, target: o3d.geometry.PointCloud, config: AnalysisConfig = None
) -> np.ndarray:
    """
    Compute point-to-point distances between clouds.

    Args:
        source: Source point cloud
        target: Target point cloud
        config: Analysis configuration

    Returns:
        Array of distances for each source point
    """
    logger.info("Computing point-to-point distances")

    target_points = np.asarray(target.points)
    source_points = np.asarray(source.points)

    # Build KDTree for efficient nearest neighbor search
    tree = KDTree(target_points)

    # Query distances
    distances, _ = tree.query(source_points)

    logger.info(f"Computed distances for {len(source_points)} points")
    return distances


def analyze_changes(
    distances: np.ndarray, config: AnalysisConfig = None
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Analyze distances to identify significant changes.

    Args:
        distances: Array of point-to-point distances
        config: Analysis configuration

    Returns:
        Tuple of (indices of changed points, statistics dictionary)
    """
    config = config or AnalysisConfig()
    logger.info(f"Analyzing changes with threshold {config.distance_threshold}")

    # Identify points exceeding threshold
    change_indices = np.where(distances > config.distance_threshold)[0]
    change_distances = distances[change_indices]

    # Calculate statistics
    if len(change_distances) > 0:
        stats = {
            "num_changed_points": len(change_indices),
            "mean_change": float(np.mean(change_distances)),
            "max_change": float(np.max(change_distances)),
            "min_change": float(np.min(change_distances)),
            "std_change": float(np.std(change_distances)),
            "volume_change_percentage": float(len(change_indices) / len(distances) * 100),
        }

        logger.info(
            f"Detected {len(change_indices)} changed points ({stats['volume_change_percentage']:.2f}%)"
        )
    else:
        stats = {
            "num_changed_points": 0,
            "mean_change": 0.0,
            "max_change": 0.0,
            "min_change": 0.0,
            "std_change": 0.0,
            "volume_change_percentage": 0.0,
        }
        logger.info("No significant changes detected")

    return change_indices, stats
