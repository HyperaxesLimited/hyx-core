"""
Tile extraction and spatial operations for point clouds.

This module provides functionality to extract comparable tiles from multiple
point clouds for testing and analysis purposes.

Author: Nicola Sabino
Company: Hyperaxes
"""

import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import numpy as np
import open3d as o3d

logger = logging.getLogger(__name__)


class Bounds:
    """Represents spatial bounds of a point cloud."""

    def __init__(
        self,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        z_min: Optional[float] = None,
        z_max: Optional[float] = None,
    ):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.z_min = z_min
        self.z_max = z_max

    @property
    def x_range(self) -> float:
        """X dimension range."""
        return self.x_max - self.x_min

    @property
    def y_range(self) -> float:
        """Y dimension range."""
        return self.y_max - self.y_min

    @property
    def z_range(self) -> Optional[float]:
        """Z dimension range."""
        if self.z_min is not None and self.z_max is not None:
            return self.z_max - self.z_min
        return None

    @property
    def center(self) -> Tuple[float, float, Optional[float]]:
        """Center point of bounds."""
        center_x = (self.x_min + self.x_max) / 2
        center_y = (self.y_min + self.y_max) / 2
        center_z = None
        if self.z_min is not None and self.z_max is not None:
            center_z = (self.z_min + self.z_max) / 2
        return (center_x, center_y, center_z)

    def to_dict(self) -> Dict[str, float]:
        """Convert bounds to dictionary."""
        result = {
            "x_min": self.x_min,
            "x_max": self.x_max,
            "y_min": self.y_min,
            "y_max": self.y_max,
        }
        if self.z_min is not None:
            result["z_min"] = self.z_min
        if self.z_max is not None:
            result["z_max"] = self.z_max
        return result

    def __repr__(self) -> str:
        z_str = f", z=[{self.z_min:.4f}, {self.z_max:.4f}]" if self.z_min is not None else ""
        return (
            f"Bounds(x=[{self.x_min:.4f}, {self.x_max:.4f}], "
            f"y=[{self.y_min:.4f}, {self.y_max:.4f}]{z_str})"
        )


def compute_bounds(
    point_cloud: Union[o3d.geometry.PointCloud, np.ndarray]
) -> Bounds:
    """
    Compute spatial bounds of a point cloud.

    Args:
        point_cloud: Open3D point cloud or numpy array (N x 3)

    Returns:
        Bounds object containing min/max values

    Example:
        >>> import open3d as o3d
        >>> from pcd_hyperaxes_core import load_point_cloud, compute_bounds
        >>> pcd = load_point_cloud("pointcloud.xyz")
        >>> bounds = compute_bounds(pcd)
        >>> print(f"X range: {bounds.x_range:.2f}m")
    """
    if isinstance(point_cloud, o3d.geometry.PointCloud):
        points = np.asarray(point_cloud.points)
    else:
        points = point_cloud

    if len(points) == 0:
        raise ValueError("Point cloud is empty")

    return Bounds(
        x_min=float(points[:, 0].min()),
        x_max=float(points[:, 0].max()),
        y_min=float(points[:, 1].min()),
        y_max=float(points[:, 1].max()),
        z_min=float(points[:, 2].min()) if points.shape[1] > 2 else None,
        z_max=float(points[:, 2].max()) if points.shape[1] > 2 else None,
    )


def find_overlap(bounds1: Bounds, bounds2: Bounds) -> Optional[Bounds]:
    """
    Find overlapping region between two bounding boxes.

    Args:
        bounds1: First bounds
        bounds2: Second bounds

    Returns:
        Bounds of overlap region, or None if no overlap exists

    Example:
        >>> bounds1 = compute_bounds(pcd1)
        >>> bounds2 = compute_bounds(pcd2)
        >>> overlap = find_overlap(bounds1, bounds2)
        >>> if overlap:
        ...     print(f"Overlap area: {overlap.x_range:.2f}m x {overlap.y_range:.2f}m")
    """
    overlap_x_min = max(bounds1.x_min, bounds2.x_min)
    overlap_x_max = min(bounds1.x_max, bounds2.x_max)
    overlap_y_min = max(bounds1.y_min, bounds2.y_min)
    overlap_y_max = min(bounds1.y_max, bounds2.y_max)

    # Check if there's actual overlap
    if overlap_x_min >= overlap_x_max or overlap_y_min >= overlap_y_max:
        logger.warning("No spatial overlap found between point clouds")
        return None

    logger.info(
        f"Found overlap: {overlap_x_max - overlap_x_min:.2f}m x "
        f"{overlap_y_max - overlap_y_min:.2f}m"
    )

    return Bounds(
        x_min=overlap_x_min,
        x_max=overlap_x_max,
        y_min=overlap_y_min,
        y_max=overlap_y_max,
    )


def extract_tile(
    point_cloud: Union[o3d.geometry.PointCloud, np.ndarray],
    bounds: Bounds,
) -> Union[o3d.geometry.PointCloud, np.ndarray]:
    """
    Extract points within specified spatial bounds.

    Args:
        point_cloud: Input point cloud (Open3D or numpy array)
        bounds: Spatial bounds to extract

    Returns:
        Extracted tile as same type as input

    Example:
        >>> tile_bounds = Bounds(x_min=100, x_max=150, y_min=200, y_max=250)
        >>> tile = extract_tile(pcd, tile_bounds)
        >>> print(f"Extracted {len(tile.points)} points")
    """
    is_o3d = isinstance(point_cloud, o3d.geometry.PointCloud)
    points = np.asarray(point_cloud.points) if is_o3d else point_cloud

    if len(points) == 0:
        raise ValueError("Point cloud is empty")

    # Create mask for points within bounds
    mask = (
        (points[:, 0] >= bounds.x_min)
        & (points[:, 0] <= bounds.x_max)
        & (points[:, 1] >= bounds.y_min)
        & (points[:, 1] <= bounds.y_max)
    )

    extracted_points = points[mask]
    logger.info(f"Extracted {len(extracted_points)} points from {len(points)} total")

    if is_o3d:
        # Create new Open3D point cloud
        tile = o3d.geometry.PointCloud()
        tile.points = o3d.utility.Vector3dVector(extracted_points)

        # Copy colors if present
        if point_cloud.has_colors():
            colors = np.asarray(point_cloud.colors)
            tile.colors = o3d.utility.Vector3dVector(colors[mask])

        # Copy normals if present
        if point_cloud.has_normals():
            normals = np.asarray(point_cloud.normals)
            tile.normals = o3d.utility.Vector3dVector(normals[mask])

        return tile
    else:
        return extracted_points


def compute_tile_bounds(
    overlap: Bounds,
    tile_size: Optional[float] = None,
    tile_width: Optional[float] = None,
    tile_height: Optional[float] = None,
    center: Optional[Tuple[float, float]] = None,
) -> Bounds:
    """
    Compute bounds for a tile within an overlap region.

    Args:
        overlap: Overlap region bounds
        tile_size: Size for square tile (in meters)
        tile_width: Width of rectangular tile (in meters)
        tile_height: Height of rectangular tile (in meters)
        center: Optional center point (x, y). If None, uses overlap center

    Returns:
        Bounds for the computed tile

    Example:
        >>> # Square 50m x 50m tile at center
        >>> tile_bounds = compute_tile_bounds(overlap, tile_size=50.0)
        >>>
        >>> # Rectangular 100m x 50m tile
        >>> tile_bounds = compute_tile_bounds(overlap, tile_width=100.0, tile_height=50.0)
        >>>
        >>> # Custom center point
        >>> tile_bounds = compute_tile_bounds(overlap, tile_size=50.0, center=(1000.0, 2000.0))
    """
    # Determine tile dimensions
    if tile_size is not None:
        width = height = tile_size
    elif tile_width is not None and tile_height is not None:
        width = tile_width
        height = tile_height
    else:
        # Use full overlap if no dimensions specified
        width = overlap.x_range
        height = overlap.y_range
        logger.info(f"Using full overlap area: {width:.2f}m x {height:.2f}m")

    # Determine center point
    if center is None:
        center_x, center_y, _ = overlap.center
    else:
        center_x, center_y = center

    # Compute tile bounds
    tile_x_min = center_x - width / 2
    tile_x_max = center_x + width / 2
    tile_y_min = center_y - height / 2
    tile_y_max = center_y + height / 2

    # Constrain to overlap region
    tile_x_min = max(tile_x_min, overlap.x_min)
    tile_x_max = min(tile_x_max, overlap.x_max)
    tile_y_min = max(tile_y_min, overlap.y_min)
    tile_y_max = min(tile_y_max, overlap.y_max)

    logger.info(
        f"Computed tile: {tile_x_max - tile_x_min:.2f}m x "
        f"{tile_y_max - tile_y_min:.2f}m"
    )

    return Bounds(x_min=tile_x_min, x_max=tile_x_max, y_min=tile_y_min, y_max=tile_y_max)


def extract_comparable_tiles(
    point_clouds: List[Union[o3d.geometry.PointCloud, np.ndarray]],
    tile_size: Optional[float] = 50.0,
    tile_width: Optional[float] = None,
    tile_height: Optional[float] = None,
    center: Optional[Tuple[float, float]] = None,
) -> Tuple[List[Union[o3d.geometry.PointCloud, np.ndarray]], Bounds, List[Bounds]]:
    """
    Extract comparable tiles from multiple point clouds.

    This function finds the overlapping region between all input point clouds
    and extracts tiles of the same spatial area from each.

    Args:
        point_clouds: List of point clouds (Open3D or numpy arrays)
        tile_size: Size for square tile in meters (default: 50.0)
        tile_width: Width of rectangular tile in meters
        tile_height: Height of rectangular tile in meters
        center: Optional center point (x, y) for tile

    Returns:
        Tuple containing:
        - List of extracted tiles (same type as input)
        - Bounds of the extracted tile
        - List of original bounds for each point cloud

    Raises:
        ValueError: If point clouds don't overlap or are empty

    Example:
        >>> from pcd_hyperaxes_core import load_point_cloud, extract_comparable_tiles
        >>> pcd1 = load_point_cloud("scan_day1.xyz")
        >>> pcd2 = load_point_cloud("scan_day2.xyz")
        >>> tiles, tile_bounds, original_bounds = extract_comparable_tiles(
        ...     [pcd1, pcd2],
        ...     tile_size=50.0
        ... )
        >>> print(f"Tile 1: {len(tiles[0].points)} points")
        >>> print(f"Tile 2: {len(tiles[1].points)} points")
    """
    if len(point_clouds) < 2:
        raise ValueError("At least 2 point clouds required for comparison")

    logger.info(f"Extracting comparable tiles from {len(point_clouds)} point clouds")

    # Compute bounds for all point clouds
    all_bounds = []
    for i, pcd in enumerate(point_clouds):
        bounds = compute_bounds(pcd)
        all_bounds.append(bounds)
        logger.info(f"Point cloud {i+1}: {bounds}")

    # Find overlap between all point clouds
    overlap = all_bounds[0]
    for bounds in all_bounds[1:]:
        overlap = find_overlap(overlap, bounds)
        if overlap is None:
            raise ValueError("No common overlap found between all point clouds")

    logger.info(f"Common overlap: {overlap}")

    # Compute tile bounds within overlap
    tile_bounds = compute_tile_bounds(
        overlap,
        tile_size=tile_size,
        tile_width=tile_width,
        tile_height=tile_height,
        center=center,
    )

    # Extract tiles from each point cloud
    tiles = []
    for i, pcd in enumerate(point_clouds):
        tile = extract_tile(pcd, tile_bounds)
        tiles.append(tile)

        # Count points
        if isinstance(tile, o3d.geometry.PointCloud):
            num_points = len(tile.points)
        else:
            num_points = len(tile)

        logger.info(f"Extracted tile {i+1}: {num_points} points")

        if num_points == 0:
            logger.warning(f"Tile {i+1} is empty!")

    return tiles, tile_bounds, all_bounds


def save_tile_metadata(
    filepath: Union[str, Path],
    source_files: List[str],
    tile_bounds: Bounds,
    original_bounds: List[Bounds],
    tile_point_counts: List[int],
) -> None:
    """
    Save tile extraction metadata to a text file.

    Args:
        filepath: Output file path
        source_files: List of source file names
        tile_bounds: Bounds of extracted tile
        original_bounds: Original bounds of each source file
        tile_point_counts: Number of points in each extracted tile
    """
    filepath = Path(filepath)

    with open(filepath, "w") as f:
        f.write("TILE EXTRACTION METADATA\n")
        f.write("=" * 60 + "\n\n")

        f.write("Source files:\n")
        for i, fname in enumerate(source_files, 1):
            f.write(f"  File {i}: {fname}\n")
        f.write("\n")

        f.write("Original bounds:\n")
        for i, bounds in enumerate(original_bounds, 1):
            f.write(f"  File {i}:\n")
            f.write(f"    X: [{bounds.x_min:.4f}, {bounds.x_max:.4f}] ({bounds.x_range:.2f}m)\n")
            f.write(f"    Y: [{bounds.y_min:.4f}, {bounds.y_max:.4f}] ({bounds.y_range:.2f}m)\n")
            if bounds.z_min is not None:
                f.write(f"    Z: [{bounds.z_min:.4f}, {bounds.z_max:.4f}] ({bounds.z_range:.2f}m)\n")
        f.write("\n")

        f.write("Extracted tile bounds:\n")
        f.write(f"  X: [{tile_bounds.x_min:.4f}, {tile_bounds.x_max:.4f}] ({tile_bounds.x_range:.2f}m)\n")
        f.write(f"  Y: [{tile_bounds.y_min:.4f}, {tile_bounds.y_max:.4f}] ({tile_bounds.y_range:.2f}m)\n")
        f.write("\n")

        f.write("Extracted tiles:\n")
        for i, count in enumerate(tile_point_counts, 1):
            f.write(f"  Tile {i}: {count} points\n")

    logger.info(f"Metadata saved to {filepath}")
