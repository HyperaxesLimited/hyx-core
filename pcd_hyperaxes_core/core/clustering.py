"""
Region detection and clustering for point cloud differences.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import numpy as np
from scipy.spatial import KDTree
import open3d as o3d
import logging
from typing import List, Tuple
from pcd_hyperaxes_core.config import AnalysisConfig

logger = logging.getLogger(__name__)


def detect_missing_regions(
    source: o3d.geometry.PointCloud,
    target: o3d.geometry.PointCloud,
    distances: np.ndarray,
    config: AnalysisConfig = None,
) -> Tuple[List[List[int]], np.ndarray, np.ndarray]:
    """
    Detect regions of missing/changed points using region growing.

    Args:
        source: Source point cloud
        target: Target point cloud
        distances: Pre-computed distances
        config: Analysis configuration

    Returns:
        Tuple of (list of regions, all missing indices, region labels)
        where each region is a list of point indices
    """
    config = config or AnalysisConfig()
    logger.info(f"Detecting regions with threshold {config.region_distance_threshold}")

    source_points = np.asarray(source.points)

    # Find points exceeding threshold
    missing_indices = np.where(distances > config.region_distance_threshold)[0]

    if len(missing_indices) == 0:
        logger.info("No significant differences detected")
        return [], np.array([]), np.zeros(len(source_points), dtype=int)

    # Build KDTree for region growing
    source_tree = KDTree(source_points)

    # Region growing
    all_regions = []
    processed = np.zeros(len(source_points), dtype=bool)

    for idx in missing_indices:
        if processed[idx]:
            continue

        # Start new region
        region = [idx]
        processed[idx] = True

        # Grow the region
        i = 0
        while i < len(region):
            current_idx = region[i]

            # Find neighbors
            neighbors_dist, neighbors_idx = source_tree.query(
                source_points[current_idx].reshape(1, -1), k=config.cluster_neighbors
            )

            # Add unprocessed missing neighbors
            for neighbor_idx in neighbors_idx[0][1:]:  # Skip self
                if not processed[neighbor_idx] and neighbor_idx in missing_indices:
                    region.append(neighbor_idx)
                    processed[neighbor_idx] = True

            i += 1

        # Keep region if large enough
        if len(region) >= config.region_size_threshold:
            all_regions.append(region)

    # Create outputs
    all_missing_indices = []
    region_labels = np.zeros(len(source_points), dtype=int)

    for region_idx, region in enumerate(all_regions, 1):
        all_missing_indices.extend(region)
        for point_idx in region:
            region_labels[point_idx] = region_idx

    logger.info(
        f"Detected {len(all_regions)} regions with {len(all_missing_indices)} total points"
    )

    return all_regions, np.array(all_missing_indices), region_labels
