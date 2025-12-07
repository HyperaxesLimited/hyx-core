import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
import laspy
import os
import open3d as o3d


def load_point_cloud(file_path: str) -> o3d.geometry.PointCloud:
    """
    Load point cloud data from LAS/LAZ or PLY files
    """
    if file_path.endswith(".las") or file_path.endswith(".laz"):
        # Load LAS/LAZ file
        las = laspy.read(file_path)
        points = np.vstack((las.x, las.y, las.z)).transpose()
        # Create Open3D point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
    elif file_path.endswith(".ply"):
        # Load PLY file directly with Open3D
        pcd = o3d.io.read_point_cloud(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

    print(f"Loaded {len(pcd.points)} points from {file_path}")
    return pcd


def preprocess_point_cloud(
    pcd: o3d.geometry.PointCloud, voxel_size: float = 0.05, remove_outliers: bool = True
):
    """
    Preprocess point cloud: downsampling and outlier removal
    """
    # Downsample using voxel grid
    pcd_down = pcd.voxel_down_sample(voxel_size)

    # Estimate normals for the downsampled point cloud
    pcd_down.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(
            radius=voxel_size * 2, max_nn=30
        )
    )

    # Remove outliers if requested
    if remove_outliers:
        # Statistical outlier removal
        pcd_down, _ = pcd_down.remove_statistical_outlier(
            nb_neighbors=20, std_ratio=2.0
        )

    print(f"Preprocessed cloud has {len(pcd_down.points)} points")
    return pcd_down


if __name__ == "__main__":
    pcd = load_point_cloud("MBES_Taranto_260225.ply")
    pcd_t1 = load_point_cloud("MBES_Taranto_260225_modified.ply")
    pcd_processed = preprocess_point_cloud(pcd, voxel_size=0.1)
    pcd_processed_t1 = preprocess_point_cloud(pcd_t1, voxel_size=0.1)
    RED_COLOR = [1,0,0]
    GREEN_COLOR = [0,1,0]
    pcd_processed.paint_uniform_color(GREEN_COLOR)
    pcd_processed_t1.paint_uniform_color(RED_COLOR)
    o3d.visualization.draw_geometries([pcd_processed, pcd_processed_t1])
