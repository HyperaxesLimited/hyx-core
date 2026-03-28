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
from typing import Tuple, Dict, Optional
from pcd_hyperaxes_core.config import AnalysisConfig, NoiseFilterConfig

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


def compute_mad(data: np.ndarray) -> float:
    """
    Compute Median Absolute Deviation (MAD).

    MAD is more robust to outliers than standard deviation.

    Args:
        data: Array of values

    Returns:
        MAD value
    """
    median = np.median(data)
    mad = np.median(np.abs(data - median))
    return mad


def apply_statistical_filter(
    distances: np.ndarray,
    preliminary_indices: np.ndarray,
    config: NoiseFilterConfig
) -> np.ndarray:
    """
    Apply statistical filtering to remove noise based on distribution.

    Args:
        distances: Array of all distances
        preliminary_indices: Indices of points that exceeded initial threshold
        config: Noise filter configuration

    Returns:
        Filtered indices after statistical validation
    """
    if not config.enable_statistical_filter or len(preliminary_indices) == 0:
        return preliminary_indices

    candidate_distances = distances[preliminary_indices]

    if config.use_mad:
        # Use MAD for robust statistics
        median = np.median(distances)
        mad = compute_mad(distances)
        # MAD to std conversion factor for normal distribution
        mad_to_std = 1.4826
        threshold = median + config.noise_tolerance_sigma * mad * mad_to_std
        logger.debug(f"Statistical filter (MAD): median={median:.3f}, MAD={mad:.3f}, threshold={threshold:.3f}")
    else:
        # Use mean and std
        mean = np.mean(distances)
        std = np.std(distances)
        threshold = mean + config.noise_tolerance_sigma * std
        logger.debug(f"Statistical filter (std): mean={mean:.3f}, std={std:.3f}, threshold={threshold:.3f}")

    # Keep only points that exceed the statistical threshold
    valid_mask = candidate_distances > threshold
    filtered_indices = preliminary_indices[valid_mask]

    filtered_count = len(preliminary_indices) - len(filtered_indices)
    if filtered_count > 0:
        logger.info(f"Statistical filter removed {filtered_count} points ({filtered_count/len(preliminary_indices)*100:.1f}%)")

    return filtered_indices


def apply_local_density_filter(
    source_points: np.ndarray,
    distances: np.ndarray,
    preliminary_indices: np.ndarray,
    config: NoiseFilterConfig,
    distance_threshold: float
) -> np.ndarray:
    """
    Apply local density validation to ensure spatial coherence.

    Args:
        source_points: Source point cloud points
        distances: Array of all distances
        preliminary_indices: Indices of candidate changed points
        config: Noise filter configuration
        distance_threshold: The distance threshold used for change detection

    Returns:
        Filtered indices after local density validation
    """
    if not config.enable_local_validation or len(preliminary_indices) == 0:
        return preliminary_indices

    # Build KDTree for source points
    tree = KDTree(source_points)

    valid_points = []

    for idx in preliminary_indices:
        point = source_points[idx].reshape(1, -1)

        # Find k nearest neighbors
        k = min(config.local_search_neighbors + 1, len(source_points))  # +1 to include the point itself
        neighbor_dists, neighbor_indices = tree.query(point, k=k)

        # Exclude the point itself
        neighbor_indices = neighbor_indices[0][1:]  # Skip first (itself)

        # Count how many neighbors also exceed the threshold
        neighbors_above_threshold = np.sum(distances[neighbor_indices] > distance_threshold)

        # Keep point if it has sufficient local support
        if neighbors_above_threshold >= config.min_local_support:
            valid_points.append(idx)

    filtered_indices = np.array(valid_points, dtype=np.int64)

    filtered_count = len(preliminary_indices) - len(filtered_indices)
    if filtered_count > 0:
        logger.info(f"Local density filter removed {filtered_count} points ({filtered_count/len(preliminary_indices)*100:.1f}%)")

    return filtered_indices


def analyze_changes(
    distances: np.ndarray,
    config: AnalysisConfig = None,
    source_points: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Analyze distances to identify significant changes with noise filtering.

    Args:
        distances: Array of point-to-point distances
        config: Analysis configuration
        source_points: Source point cloud points (required for local density filtering)

    Returns:
        Tuple of (indices of changed points, statistics dictionary)
    """
    config = config or AnalysisConfig()
    logger.info(f"Analyzing changes with threshold {config.distance_threshold}")

    # Step 1: Initial threshold filtering
    preliminary_indices = np.where(distances > config.distance_threshold)[0]
    initial_count = len(preliminary_indices)
    logger.info(f"Initial candidates: {initial_count} points")

    # Step 2: Apply noise filtering if enabled
    filtered_indices = preliminary_indices

    if config.noise_filter.enable_statistical_filter or config.noise_filter.enable_local_validation:
        # Statistical filtering
        if config.noise_filter.enable_statistical_filter:
            filtered_indices = apply_statistical_filter(
                distances, filtered_indices, config.noise_filter
            )

        # Local density validation
        if config.noise_filter.enable_local_validation:
            if source_points is None:
                logger.warning("Local density filtering requested but source_points not provided, skipping")
            else:
                filtered_indices = apply_local_density_filter(
                    source_points, distances, filtered_indices,
                    config.noise_filter, config.distance_threshold
                )

    change_indices = filtered_indices
    change_distances = distances[change_indices]

    # Step 3: Calculate statistics on final filtered points
    if len(change_distances) > 0:
        stats = {
            "num_changed_points": len(change_indices),
            "mean_change": float(np.mean(change_distances)),
            "max_change": float(np.max(change_distances)),
            "min_change": float(np.min(change_distances)),
            "std_change": float(np.std(change_distances)),
            "volume_change_percentage": float(len(change_indices) / len(distances) * 100),
        }

        total_filtered = initial_count - len(change_indices)
        if total_filtered > 0:
            logger.info(
                f"Final: {len(change_indices)} changed points ({stats['volume_change_percentage']:.2f}%) "
                f"- filtered {total_filtered} noise points ({total_filtered/initial_count*100:.1f}%)"
            )
        else:
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
