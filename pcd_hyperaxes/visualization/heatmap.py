"""
Heatmap visualization for distance data.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import numpy as np
import open3d as o3d
import logging
from pcd_hyperaxes.config import VisualizationConfig

logger = logging.getLogger(__name__)


def create_distance_heatmap(
    source: o3d.geometry.PointCloud, distances: np.ndarray, config: VisualizationConfig = None
) -> o3d.geometry.PointCloud:
    """
    Create a heatmap point cloud based on distances.

    Args:
        source: Source point cloud
        distances: Distance values for each point
        config: Visualization configuration

    Returns:
        Colored point cloud representing the heatmap
    """
    config = config or VisualizationConfig()
    logger.info("Generating distance heatmap")

    # Create copy
    heatmap_pcd = o3d.geometry.PointCloud()
    heatmap_pcd.points = o3d.utility.Vector3dVector(np.asarray(source.points))

    # Normalize distances
    min_dist = np.min(distances)
    max_dist = np.max(distances)

    if max_dist > min_dist:
        normalized = (distances - min_dist) / (max_dist - min_dist)
    else:
        normalized = np.ones_like(distances) * 0.5

    # Apply colormap (blue to red)
    colors = np.zeros((len(distances), 3))
    colors[:, 0] = normalized  # Red channel
    colors[:, 2] = 1 - normalized  # Blue channel
    colors[:, 1] = np.where(normalized < 0.5, normalized * 2, (1 - normalized) * 2)  # Green

    heatmap_pcd.colors = o3d.utility.Vector3dVector(colors)

    logger.info(f"Heatmap range: Blue = {min_dist:.3f}m, Red = {max_dist:.3f}m")

    return heatmap_pcd
