"""
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
from typing import Optional, Union
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
def load_point_cloud(file_path: Union[str, Path]) -> o3d.geometry.PointCloud:
    """Load point cloud from file."""
    return PointCloudLoader.load(Path(file_path))
