"""
Point cloud preprocessing operations.

Includes downsampling, outlier removal, and normal estimation.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import open3d as o3d
import logging
from pcd_hyperaxes.config import PreprocessingConfig

logger = logging.getLogger(__name__)


class PointCloudPreprocessor:
    """Handles point cloud preprocessing operations."""

    def __init__(self, config: PreprocessingConfig = None):
        """
        Initialize preprocessor with configuration.

        Args:
            config: Preprocessing configuration. Uses defaults if None.
        """
        self.config = config or PreprocessingConfig()

    def preprocess(self, pcd: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
        """
        Apply full preprocessing pipeline to point cloud.

        Args:
            pcd: Input point cloud

        Returns:
            Preprocessed point cloud
        """
        logger.info(f"Starting preprocessing of {len(pcd.points)} points")

        # Downsample
        pcd_down = pcd.voxel_down_sample(self.config.voxel_size)
        logger.debug(f"Downsampled to {len(pcd_down.points)} points")

        # Estimate normals
        if self.config.estimate_normals:
            search_radius = self.config.voxel_size * self.config.normal_search_radius_multiplier
            pcd_down.estimate_normals(
                search_param=o3d.geometry.KDTreeSearchParamHybrid(
                    radius=search_radius, max_nn=self.config.normal_max_nn
                )
            )
            logger.debug("Normals estimated")

        # Remove outliers
        if self.config.remove_outliers:
            pcd_clean, _ = pcd_down.remove_statistical_outlier(
                nb_neighbors=self.config.outlier_nb_neighbors,
                std_ratio=self.config.outlier_std_ratio,
            )
            removed = len(pcd_down.points) - len(pcd_clean.points)
            logger.debug(f"Removed {removed} outlier points")
            pcd_down = pcd_clean

        logger.info(f"Preprocessing complete: {len(pcd_down.points)} points remaining")
        return pcd_down


# Convenience function
def preprocess_point_cloud(
    pcd: o3d.geometry.PointCloud, config: PreprocessingConfig = None
) -> o3d.geometry.PointCloud:
    """Preprocess point cloud with given configuration."""
    preprocessor = PointCloudPreprocessor(config)
    return preprocessor.preprocess(pcd)
