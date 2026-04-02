"""
Visualization utilities for point clouds.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import numpy as np
import open3d as o3d
import logging
from typing import List
from pcd_hyperaxes.config import VisualizationConfig

logger = logging.getLogger(__name__)


def visualize_regions(
    source: o3d.geometry.PointCloud, missing_indices: np.ndarray, config: VisualizationConfig = None
) -> o3d.geometry.PointCloud:
    """
    Create visualization with highlighted regions.

    Args:
        source: Source point cloud
        missing_indices: Indices of points to highlight
        config: Visualization configuration

    Returns:
        Colored point cloud
    """
    config = config or VisualizationConfig()

    colored_pcd = o3d.geometry.PointCloud()
    colored_pcd.points = source.points

    # Initialize with background color
    colors = np.tile(config.background_color, (len(source.points), 1))

    # Highlight regions
    if len(missing_indices) > 0:
        colors[missing_indices] = config.highlight_color

    colored_pcd.colors = o3d.utility.Vector3dVector(colors)

    return colored_pcd


def show_visualization(geometries: List[o3d.geometry.Geometry], config: VisualizationConfig = None) -> None:
    """Display geometries in viewer."""
    config = config or VisualizationConfig()

    if not config.enable_plots:
        logger.info("Visualization disabled")
        return

    logger.info("Opening visualization window")
    o3d.visualization.draw_geometries(geometries, window_name=config.window_name)
