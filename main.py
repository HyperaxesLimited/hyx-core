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

def register_point_clouds(source : o3d.geometry.PointCloud, target : o3d.geometry.PointCloud, voxel_size=0.05, max_iter=100):
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

def compute_cloud_distances(source : o3d.geometry.PointCloud, target : o3d.geometry.PointCloud) -> float:
   """
   Compute point-to-point distances between source and target clouds
   """
   # Convert target points to numpy array for KDTree
   target_points = np.asarray(target.points)
   source_points = np.asarray(source.points)
  
   # Build KDTree from target points
   tree = KDTree(target_points)
  
   # Query the tree for nearest neighbor distances
   distances, _ = tree.query(source_points)
  
   print(f"Computed distances for {len(source_points)} points")
   return distances

def analyze_changes(distances, threshold=0.1):
   """
   Analyze distances to identify significant changes
   """
   # Identify points with distance greater than threshold
   change_indices = np.where(distances > threshold)[0]
   change_distances = distances[change_indices]
  
   # Calculate statistics
   if len(change_distances) > 0:
       mean_change = np.mean(change_distances)
       max_change = np.max(change_distances)
       total_volume_change = len(change_indices) / len(distances)  # Approximate as percentage of points
      
       print(f"Detected {len(change_indices)} points with significant change")
       print(f"Mean change: {mean_change:.3f}m, Max change: {max_change:.3f}m")
       print(f"Approximate volume change: {total_volume_change*100:.2f}%")
      
       return change_indices, {
           "mean_change": mean_change,
           "max_change": max_change,
           "volume_change_percentage": total_volume_change*100
       }
   else:
       print("No significant changes detected")
       return [], {"mean_change": 0, "max_change": 0, "volume_change_percentage": 0}
   
def create_distance_heatmap(source, distances):
   """
   Visualize the entire point cloud as a heatmap based on distance values
   """
   # Create a copy of the source cloud
   heatmap_pcd = o3d.geometry.PointCloud()
   heatmap_pcd.points = o3d.utility.Vector3dVector(np.asarray(source.points))
  
   # Normalize distances for visualization
   min_dist = np.min(distances)
   max_dist = np.max(distances)
  
   # Create a colormap (blue=close, red=far)
   if max_dist > min_dist:
       normalized_dists = (distances - min_dist) / (max_dist - min_dist)
   else:
       normalized_dists = np.ones_like(distances) * 0.5
  
   # Create color array using a gradient from blue to red
   colors = np.zeros((len(distances), 3))
   colors[:, 0] = normalized_dists  # Red channel increases with distance
   colors[:, 2] = 1 - normalized_dists  # Blue channel decreases with distance
  
   # Add green component for a more dynamic color range
   colors[:, 1] = np.where(normalized_dists < 0.5,
                          normalized_dists * 2,
                          (1 - normalized_dists) * 2)
  
   heatmap_pcd.colors = o3d.utility.Vector3dVector(colors)
  
   print(f"Heatmap color scale: Blue = {min_dist:.3f}m, Red = {max_dist:.3f}m")
  
   return heatmap_pcd

def detect_missing_regions(source, target, distances, distance_threshold=0.1, region_size_threshold=10):
   """
   Detect regions in source that have no correspondence in target using distance thresholding and region growing
   """
   source_points = np.asarray(source.points)
  
   # Find points that are far from any point in the target (potentially missing)
   missing_indices = np.where(distances > distance_threshold)[0]
  
   if len(missing_indices) == 0:
       print("No significant differences detected")
       return [], [], []
  
   # Create a KDTree of the source points
   source_tree = KDTree(source_points)
  
   # Initialize variables for region growing
   all_regions = []
   processed = np.zeros(len(source_points), dtype=bool)
  
   # Process each unprocessed missing point
   for idx in missing_indices:
       if processed[idx]:
           continue
          
       # Start a new region with this point
       current_region = [idx]
       processed[idx] = True
      
       # Grow the region
       i = 0
       while i < len(current_region):
           # Get current point in the growing region
           current_idx = current_region[i]
          
           # Find neighbors within the 3D neighborhood (using KDTree)
           neighbors_dist, neighbors_idx = source_tree.query(
               source_points[current_idx].reshape(1, -1),
               k=20  # Consider 20 nearest neighbors
           )
          
           # Add unprocessed neighbors that are also missing
           for neighbor_idx in neighbors_idx[0][1:]:  # Skip the point itself
               if not processed[neighbor_idx] and neighbor_idx in missing_indices:
                   current_region.append(neighbor_idx)
                   processed[neighbor_idx] = True
          
           i += 1
      
       # Store region if it's large enough (to filter out noise)
       if len(current_region) >= region_size_threshold:
           all_regions.append(current_region)
  
   # Flatten all regions into a single list of indices
   all_missing_indices = []
   region_labels = np.zeros(len(source_points), dtype=int)
  
   for region_idx, region in enumerate(all_regions, 1):
       all_missing_indices.extend(region)
       # Label each point with its region number
       for point_idx in region:
           region_labels[point_idx] = region_idx
  
   print(f"Detected {len(all_regions)} missing regions with total {len(all_missing_indices)} points")
  
   # Return missing regions, all missing indices, and region labels
   return all_regions, np.array(all_missing_indices), region_labels


if __name__ == "__main__":
    RED_COLOR = [1,0,0]
    GREEN_COLOR = [0,1,0]
    BLUE_COLOR = [0,0,1]
    VOXELS_SIZE = 0.1

    ORIGINAL = "MBES_Taranto_260225.ply"
    MODIFIED = "MBES_Taranto_260225_modified.ply"

    # Hard code scan scenario
    IS_SCAN_EQUAL = False

    pcd_processed = preprocess_point_cloud(load_point_cloud(ORIGINAL), VOXELS_SIZE)

    target_pcd = pcd_processed
    source_pcd = preprocess_point_cloud(load_point_cloud(ORIGINAL if IS_SCAN_EQUAL else MODIFIED), voxel_size=0.1)
    source_aligned, _ = register_point_clouds(source_pcd, target_pcd, VOXELS_SIZE)

    target_pcd.paint_uniform_color(GREEN_COLOR)
    source_pcd.paint_uniform_color(BLUE_COLOR)
    source_aligned.paint_uniform_color(GREEN_COLOR)

    distances = compute_cloud_distances(source_aligned, target_pcd)
    analyze_changes(distances, threshold=0.2)

    # heatmap_pcd = create_distance_heatmap(source_aligned, distances)
    # o3d.visualization.draw_geometries([heatmap_pcd])

    regions, missing_indices, region_labels = detect_missing_regions(source_aligned, target_pcd, distances, distance_threshold=0.9)

    # Create visualization with missing regions highlighted
    missing_pcd = o3d.geometry.PointCloud()
    if len(missing_indices) > 0:
        missing_points = np.asarray(source_aligned.points)[missing_indices]
        missing_pcd.points = o3d.utility.Vector3dVector(missing_points)
        missing_pcd.paint_uniform_color(RED_COLOR)  # Yellow for missing regions

    # Visualize: target (red) + source (green) + missing regions (yellow)
    o3d.visualization.draw_geometries([target_pcd, missing_pcd])



