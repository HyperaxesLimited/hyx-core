"""
Point cloud registration (alignment) algorithms.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import numpy as np
import open3d as o3d
import logging
from typing import Tuple
from pcd_hyperaxes.config import RegistrationConfig

logger = logging.getLogger(__name__)


def register_point_clouds(
    source: o3d.geometry.PointCloud,
    target: o3d.geometry.PointCloud,
    voxel_size: float,
    config: RegistrationConfig = None,
) -> Tuple[o3d.geometry.PointCloud, np.ndarray]:
    """
    Register source point cloud to target using ICP.

    Args:
        source: Source point cloud to be aligned
        target: Target point cloud (reference)
        voxel_size: Voxel size used for preprocessing
        config: Registration configuration

    Returns:
        Tuple of (aligned source cloud, transformation matrix)
    """
    config = config or RegistrationConfig()
    logger.info("Starting point cloud registration")

    # Initialize with identity transformation
    init_transformation = np.identity(4)

    # Set convergence criteria
    criteria = o3d.pipelines.registration.ICPConvergenceCriteria(
        relative_fitness=config.relative_fitness,
        relative_rmse=config.relative_rmse,
        max_iteration=config.max_iterations,
    )

    # Distance threshold
    distance_threshold = voxel_size * config.distance_threshold_multiplier

    # Choose estimation method
    if config.registration_method == "point_to_plane":
        estimation = o3d.pipelines.registration.TransformationEstimationPointToPlane()
    else:
        estimation = o3d.pipelines.registration.TransformationEstimationPointToPoint()

    # Perform ICP registration
    result = o3d.pipelines.registration.registration_icp(
        source, target, distance_threshold, init_transformation, estimation, criteria
    )

    # Apply transformation
    source_transformed = source.transform(result.transformation)

    logger.info(
        f"Registration complete - Fitness: {result.fitness:.4f}, RMSE: {result.inlier_rmse:.4f}"
    )

    return source_transformed, result.transformation
