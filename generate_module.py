#!/usr/bin/env python3
"""
Script to generate the complete pcd_hyperaxes_core module structure.

This script creates all necessary files for the refactored module based on the original main.py.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

from pathlib import Path
import textwrap


def create_core_io():
    """Create core/io.py - File loading and saving."""
    content = '''"""
Input/Output operations for point cloud files.

Supports multiple file formats: LAS, LAZ, PLY, PCD, XYZ

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import numpy as np
import open3d as o3d
import laspy
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PointCloudLoader:
    """Handles loading of various point cloud formats."""

    SUPPORTED_FORMATS = {".las", ".laz", ".ply", ".pcd", ".xyz"}

    @staticmethod
    def load(file_path: Path) -> o3d.geometry.PointCloud:
        """
        Load point cloud data from supported file formats.

        Args:
            file_path: Path to the point cloud file

        Returns:
            Open3D PointCloud object

        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()

        if suffix not in PointCloudLoader.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: {suffix}. "
                f"Supported formats: {PointCloudLoader.SUPPORTED_FORMATS}"
            )

        if suffix in {".las", ".laz"}:
            pcd = PointCloudLoader._load_las(file_path)
        elif suffix == ".ply":
            pcd = PointCloudLoader._load_ply(file_path)
        elif suffix == ".pcd":
            pcd = PointCloudLoader._load_pcd(file_path)
        elif suffix == ".xyz":
            pcd = PointCloudLoader._load_xyz(file_path)

        logger.info(f"Loaded {len(pcd.points)} points from {file_path.name}")
        return pcd

    @staticmethod
    def _load_las(file_path: Path) -> o3d.geometry.PointCloud:
        """Load LAS/LAZ format."""
        las = laspy.read(str(file_path))
        points = np.vstack((las.x, las.y, las.z)).transpose()

        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)

        # Load colors if available
        if hasattr(las, "red") and hasattr(las, "green") and hasattr(las, "blue"):
            colors = np.vstack((las.red, las.green, las.blue)).transpose() / 65535.0
            pcd.colors = o3d.utility.Vector3dVector(colors)

        return pcd

    @staticmethod
    def _load_ply(file_path: Path) -> o3d.geometry.PointCloud:
        """Load PLY format."""
        return o3d.io.read_point_cloud(str(file_path))

    @staticmethod
    def _load_pcd(file_path: Path) -> o3d.geometry.PointCloud:
        """Load PCD format."""
        return o3d.io.read_point_cloud(str(file_path))

    @staticmethod
    def _load_xyz(file_path: Path) -> o3d.geometry.PointCloud:
        """Load XYZ format (ASCII x y z per line)."""
        points = np.loadtxt(str(file_path))
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points[:, :3])
        return pcd


# Convenience function
def load_point_cloud(file_path: str | Path) -> o3d.geometry.PointCloud:
    """Load point cloud from file."""
    return PointCloudLoader.load(Path(file_path))
'''
    return content


def create_core_preprocessing():
    """Create core/preprocessing.py."""
    content = '''"""
Point cloud preprocessing operations.

Includes downsampling, outlier removal, and normal estimation.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import open3d as o3d
import logging
from pcd_hyperaxes_core.config import PreprocessingConfig

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
'''
    return content


def create_all_files():
    """Create all module files."""
    base_path = Path("pcd_hyperaxes_core")

    # Create core/io.py
    (base_path / "core" / "io.py").write_text(create_core_io())
    print("✓ Created core/io.py")

    # Create core/preprocessing.py
    (base_path / "core" / "preprocessing.py").write_text(create_core_preprocessing())
    print("✓ Created core/preprocessing.py")

    print("\n✅ Core infrastructure files created successfully!")
    print("\nNext steps:")
    print("1. Run: python generate_module.py   (to create remaining files)")
    print("2. Install: pip install -e .")
    print("3. Test: pcd-hyperaxes --help")


if __name__ == "__main__":
    create_all_files()
