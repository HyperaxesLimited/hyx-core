# Tile Extraction Guide

This guide explains how to use the tiling functionality in `pcd_hyperaxes_core` to extract comparable spatial regions from multiple point clouds for testing and analysis.

## Overview

The tiling module provides functions to:
- Compute spatial bounds of point clouds
- Find overlapping regions between multiple point clouds
- Extract tiles (spatial subsets) of the same area from different point clouds
- Save tiles and metadata for reproducible testing

## Use Cases

### 1. Algorithm Testing
Extract identical spatial regions from point clouds captured at different times to test change detection algorithms.

### 2. Multi-Temporal Analysis
Compare the same geographic area across multiple surveys or time periods.

### 3. Reduced Dataset Creation
Create smaller, manageable test datasets from large point clouds while maintaining spatial coherence.

## Quick Start

### Basic Usage

```python
from pcd_hyperaxes_core import (
    load_point_cloud,
    extract_comparable_tiles,
    save_point_cloud,
)

# Load multiple point clouds
pcd1 = load_point_cloud("scan_2026-03-02.xyz")
pcd2 = load_point_cloud("scan_2026-03-12.xyz")

# Extract 50m x 50m tiles from the same area
tiles, tile_bounds, original_bounds = extract_comparable_tiles(
    [pcd1, pcd2],
    tile_size=50.0
)

# Save tiles
save_point_cloud(tiles[0], "tile_day1.ply")
save_point_cloud(tiles[1], "tile_day2.ply")

print(f"Extracted {len(tiles[0].points)} and {len(tiles[1].points)} points")
```

## API Reference

### `extract_comparable_tiles()`

Extract tiles of the same spatial area from multiple point clouds.

**Parameters:**
- `point_clouds` (List): List of Open3D PointCloud objects
- `tile_size` (float, optional): Size for square tile in meters (default: 50.0)
- `tile_width` (float, optional): Width of rectangular tile in meters
- `tile_height` (float, optional): Height of rectangular tile in meters
- `center` (Tuple[float, float], optional): Custom center point (x, y)

**Returns:**
- `tiles`: List of extracted tiles (same type as input)
- `tile_bounds`: Bounds object with tile coordinates
- `original_bounds`: List of original bounds for each input

**Example:**
```python
# Square tile (50m x 50m)
tiles, bounds, _ = extract_comparable_tiles([pcd1, pcd2], tile_size=50.0)

# Rectangular tile (100m x 50m)
tiles, bounds, _ = extract_comparable_tiles(
    [pcd1, pcd2],
    tile_width=100.0,
    tile_height=50.0
)

# Custom center point
tiles, bounds, _ = extract_comparable_tiles(
    [pcd1, pcd2],
    tile_size=50.0,
    center=(494800.0, 4915530.0)
)
```

### `compute_bounds()`

Compute spatial bounds of a point cloud.

**Parameters:**
- `point_cloud`: Open3D PointCloud or numpy array (N x 3)

**Returns:**
- `Bounds` object containing min/max values for x, y, z

**Example:**
```python
from pcd_hyperaxes_core import load_point_cloud, compute_bounds

pcd = load_point_cloud("pointcloud.xyz")
bounds = compute_bounds(pcd)

print(f"X range: {bounds.x_range:.2f}m")
print(f"Y range: {bounds.y_range:.2f}m")
print(f"Z range: {bounds.z_range:.2f}m")
print(f"Center: {bounds.center}")
```

### `find_overlap()`

Find overlapping region between two bounding boxes.

**Parameters:**
- `bounds1`: First Bounds object
- `bounds2`: Second Bounds object

**Returns:**
- `Bounds` object representing overlap, or `None` if no overlap

**Example:**
```python
from pcd_hyperaxes_core import compute_bounds, find_overlap

bounds1 = compute_bounds(pcd1)
bounds2 = compute_bounds(pcd2)

overlap = find_overlap(bounds1, bounds2)
if overlap:
    print(f"Overlap area: {overlap.x_range:.2f}m x {overlap.y_range:.2f}m")
else:
    print("No overlap found")
```

### `extract_tile()`

Extract points within specified spatial bounds from a single point cloud.

**Parameters:**
- `point_cloud`: Open3D PointCloud or numpy array
- `bounds`: Bounds object specifying extraction area

**Returns:**
- Extracted tile (same type as input)

**Example:**
```python
from pcd_hyperaxes_core import Bounds, extract_tile

# Define custom bounds
tile_bounds = Bounds(
    x_min=494750.0,
    x_max=494800.0,
    y_min=4915500.0,
    y_max=4915550.0
)

tile = extract_tile(pcd, tile_bounds)
print(f"Extracted {len(tile.points)} points")
```

### `save_tile_metadata()`

Save tile extraction metadata to a text file.

**Parameters:**
- `filepath`: Output file path
- `source_files`: List of source file names
- `tile_bounds`: Bounds of extracted tile
- `original_bounds`: Original bounds of each source
- `tile_point_counts`: Number of points in each tile

**Example:**
```python
from pcd_hyperaxes_core import save_tile_metadata

save_tile_metadata(
    filepath="tiles_metadata.txt",
    source_files=["scan1.xyz", "scan2.xyz"],
    tile_bounds=tile_bounds,
    original_bounds=original_bounds,
    tile_point_counts=[35327, 33438],
)
```

## Complete Example

Here's a complete workflow for extracting and analyzing tiles:

```python
from pathlib import Path
from pcd_hyperaxes_core import (
    load_point_cloud,
    extract_comparable_tiles,
    save_point_cloud,
    save_tile_metadata,
)

# 1. Load point clouds
files = [
    "2026-03-02-mbes-genova.xyz",
    "2026-03-12-mbes-genova.xyz",
]

point_clouds = [load_point_cloud(f) for f in files]

# 2. Extract comparable tiles
tiles, tile_bounds, original_bounds = extract_comparable_tiles(
    point_clouds,
    tile_size=50.0  # 50m x 50m tile
)

# 3. Save tiles
output_dir = Path("tiles_output")
output_dir.mkdir(exist_ok=True)

tile_files = []
tile_counts = []

for i, tile in enumerate(tiles, 1):
    output_file = output_dir / f"tile_{i}.ply"
    save_point_cloud(tile, str(output_file))
    tile_files.append(output_file)
    tile_counts.append(len(tile.points))
    print(f"Saved tile {i}: {len(tile.points)} points")

# 4. Save metadata
save_tile_metadata(
    filepath=output_dir / "metadata.txt",
    source_files=files,
    tile_bounds=tile_bounds,
    original_bounds=original_bounds,
    tile_point_counts=tile_counts,
)

# 5. Compare tiles using the main comparison tool
print("\nCompare tiles with:")
print(f"  pcd-hyperaxes {tile_files[0]} {tile_files[1]}")
```

## Advanced Usage

### Custom Tile Regions

You can specify custom tile regions instead of using the overlap center:

```python
from pcd_hyperaxes_core import compute_bounds, find_overlap, compute_tile_bounds, extract_tile

# Compute overlap
bounds1 = compute_bounds(pcd1)
bounds2 = compute_bounds(pcd2)
overlap = find_overlap(bounds1, bounds2)

# Define custom tile region (e.g., northwest corner)
tile_bounds = compute_tile_bounds(
    overlap,
    tile_size=50.0,
    center=(overlap.x_min + 25, overlap.y_max - 25)  # Near NW corner
)

# Extract from each point cloud
tile1 = extract_tile(pcd1, tile_bounds)
tile2 = extract_tile(pcd2, tile_bounds)
```

### Multiple Tiles

Extract multiple tiles from the same overlap region:

```python
# Extract 4 tiles in a grid pattern
overlap_width = overlap.x_range
overlap_height = overlap.y_range

tile_size = 25.0
centers = [
    (overlap.x_min + overlap_width * 0.25, overlap.y_min + overlap_height * 0.25),  # SW
    (overlap.x_min + overlap_width * 0.75, overlap.y_min + overlap_height * 0.25),  # SE
    (overlap.x_min + overlap_width * 0.25, overlap.y_min + overlap_height * 0.75),  # NW
    (overlap.x_min + overlap_width * 0.75, overlap.y_min + overlap_height * 0.75),  # NE
]

for i, center in enumerate(centers, 1):
    tiles, bounds, _ = extract_comparable_tiles(
        [pcd1, pcd2],
        tile_size=tile_size,
        center=center
    )
    save_point_cloud(tiles[0], f"tile_day1_region{i}.ply")
    save_point_cloud(tiles[1], f"tile_day2_region{i}.ply")
```

### Working with NumPy Arrays

The tiling functions also work with NumPy arrays:

```python
import numpy as np
from pcd_hyperaxes_core import compute_bounds, extract_tile

# Load as numpy array
points1 = np.loadtxt("scan1.xyz")
points2 = np.loadtxt("scan2.xyz")

# Compute bounds
bounds1 = compute_bounds(points1)
bounds2 = compute_bounds(points2)

# Extract tiles (returns numpy arrays)
tile1 = extract_tile(points1, tile_bounds)
tile2 = extract_tile(points2, tile_bounds)

# Save as XYZ
np.savetxt("tile1.xyz", tile1, fmt="%.4f")
np.savetxt("tile2.xyz", tile2, fmt="%.4f")
```

## Best Practices

1. **Choose appropriate tile size**: Balance between having enough points for analysis and manageable file sizes
   - Small tiles (10-30m): Quick processing, good for testing
   - Medium tiles (50-100m): Good balance for most use cases
   - Large tiles (>100m): Preserves more spatial context

2. **Verify overlap**: Always check that your point clouds have sufficient overlap
   ```python
   overlap = find_overlap(bounds1, bounds2)
   if overlap is None:
       print("ERROR: No overlap found!")
   elif overlap.x_range < 50 or overlap.y_range < 50:
       print("WARNING: Overlap area may be too small")
   ```

3. **Save metadata**: Always save tile metadata for reproducibility and documentation

4. **Check point counts**: Verify that tiles have sufficient points
   ```python
   MIN_POINTS = 1000
   for i, tile in enumerate(tiles, 1):
       if len(tile.points) < MIN_POINTS:
           print(f"WARNING: Tile {i} has only {len(tile.points)} points")
   ```

## Troubleshooting

### No Overlap Found
**Problem**: Point clouds don't overlap spatially

**Solution**:
- Verify that point clouds are in the same coordinate system
- Check bounds using `compute_bounds()`
- Consider registration if clouds should overlap but don't align

### Empty or Small Tiles
**Problem**: Extracted tiles have few or no points

**Solutions**:
- Reduce tile size
- Use full overlap area (omit `tile_size` parameter)
- Check point cloud density

### Memory Issues
**Problem**: Large point clouds cause memory errors

**Solutions**:
- Work with downsampled versions first
- Extract smaller tiles
- Process one tile at a time instead of loading all clouds

## See Also

- Main README: [README.md](../README.md)
- API Documentation: [API.md](API.md)
- Point Cloud Comparison: See CLI documentation

## Support

For issues or questions:
- Email: nicola.sabino@hyperaxes.com
- Company: Hyperaxes
