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

def register_point_clouds(source, target, voxel_size=0.05, max_iter=100):
    """
    Register source point cloud to target using point-to-plane ICP
    """
    # Initialize transformation with identity matrix
    init_transformation = np.identity(4)

    # Set convergence criteria
    criteria = o3d.pipelines.registration.ICPConvergenceCriteria(
        relative_fitness=1e-6,
        relative_rmse=1e-6,
        max_iteration=max_iter
    )

    # Point-to-plane ICP registration
    result = o3d.pipelines.registration.registration_icp(
        source, target, voxel_size*2, init_transformation,
        o3d.pipelines.registration.TransformationEstimationPointToPlane(),
        criteria
    )

    # Apply transformation to source
    source_transformed = source.transform(result.transformation)
  
    print(f"Registration finished with fitness: {result.fitness}, RMSE: {result.inlier_rmse}")
    return source_transformed, result.transformation



if __name__ == "__main__":
    RED_COLOR = [1,0,0]
    GREEN_COLOR = [0,1,0]
    BLUE_COLOR = [0,0,1]
    VOXELS_SIZE = 0.1

    ORIGINAL = "MBES_Taranto_260225.ply"
    MODIFIED = "MBES_Taranto_260225_modified.ply"

    pcd_processed = preprocess_point_cloud(load_point_cloud(ORIGINAL), VOXELS_SIZE)

    target_pcd = pcd_processed
    source_pcd = preprocess_point_cloud(load_point_cloud(MODIFIED), voxel_size=0.1)
    source_aligned, transformation = register_point_clouds(source_pcd, target_pcd, VOXELS_SIZE)

    target_pcd.paint_uniform_color(RED_COLOR)
    source_pcd.paint_uniform_color(BLUE_COLOR)
    source_aligned.paint_uniform_color(GREEN_COLOR)

    o3d.visualization.draw_geometries([source_pcd, source_aligned, target_pcd])


