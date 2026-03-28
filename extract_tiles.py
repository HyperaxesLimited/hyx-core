#!/usr/bin/env python3
"""
Extract matching tiles from two point cloud files for algorithm testing.
"""

import numpy as np
from pathlib import Path
import sys


def load_xyz_file(filepath):
    """Load XYZ file and return as numpy array."""
    print(f"Loading {filepath}...")
    data = np.loadtxt(filepath)
    print(f"  Loaded {len(data)} points")
    return data


def get_bounds(points):
    """Get min/max bounds of point cloud."""
    return {
        'x_min': points[:, 0].min(),
        'x_max': points[:, 0].max(),
        'y_min': points[:, 1].min(),
        'y_max': points[:, 1].max(),
        'z_min': points[:, 2].min(),
        'z_max': points[:, 2].max(),
    }


def print_bounds(bounds, label):
    """Print bounds in a readable format."""
    print(f"\n{label} Bounds:")
    print(f"  X: [{bounds['x_min']:.4f}, {bounds['x_max']:.4f}] range: {bounds['x_max']-bounds['x_min']:.4f}")
    print(f"  Y: [{bounds['y_min']:.4f}, {bounds['y_max']:.4f}] range: {bounds['y_max']-bounds['y_min']:.4f}")
    if 'z_min' in bounds and 'z_max' in bounds:
        print(f"  Z: [{bounds['z_min']:.4f}, {bounds['z_max']:.4f}] range: {bounds['z_max']-bounds['z_min']:.4f}")


def find_overlap(bounds1, bounds2):
    """Find overlapping region between two bounding boxes."""
    overlap = {
        'x_min': max(bounds1['x_min'], bounds2['x_min']),
        'x_max': min(bounds1['x_max'], bounds2['x_max']),
        'y_min': max(bounds1['y_min'], bounds2['y_min']),
        'y_max': min(bounds1['y_max'], bounds2['y_max']),
    }

    # Check if there's actual overlap
    if overlap['x_min'] >= overlap['x_max'] or overlap['y_min'] >= overlap['y_max']:
        return None

    return overlap


def extract_tile(points, x_min, x_max, y_min, y_max):
    """Extract points within specified bounds."""
    mask = (
        (points[:, 0] >= x_min) & (points[:, 0] <= x_max) &
        (points[:, 1] >= y_min) & (points[:, 1] <= y_max)
    )
    return points[mask]


def select_tile_region(overlap, tile_size=50.0):
    """
    Select a tile region from the overlap area.

    Args:
        overlap: Dictionary with overlap bounds
        tile_size: Size of the tile in meters (default: 50m x 50m)

    Returns:
        Dictionary with tile bounds
    """
    overlap_width = overlap['x_max'] - overlap['x_min']
    overlap_height = overlap['y_max'] - overlap['y_min']

    print(f"\nOverlap area: {overlap_width:.2f}m x {overlap_height:.2f}m")

    # Use the center of the overlap area
    center_x = (overlap['x_min'] + overlap['x_max']) / 2
    center_y = (overlap['y_min'] + overlap['y_max']) / 2

    # Create tile centered on the overlap
    tile = {
        'x_min': center_x - tile_size / 2,
        'x_max': center_x + tile_size / 2,
        'y_min': center_y - tile_size / 2,
        'y_max': center_y + tile_size / 2,
    }

    # Ensure tile is within overlap
    tile['x_min'] = max(tile['x_min'], overlap['x_min'])
    tile['x_max'] = min(tile['x_max'], overlap['x_max'])
    tile['y_min'] = max(tile['y_min'], overlap['y_min'])
    tile['y_max'] = min(tile['y_max'], overlap['y_max'])

    return tile


def save_xyz_file(points, filepath):
    """Save points to XYZ file."""
    print(f"Saving {len(points)} points to {filepath}")
    np.savetxt(filepath, points, fmt='%.4f')


def main():
    # File paths
    base_dir = Path("/Users/nicolasabino/dev/3d-python-hyperaxes")
    file1 = base_dir / "2026-03-02-mbes-genova-0.25m_GB.xyz"
    file2 = base_dir / "2026-03-12-mbes-genova-0.25m_GB.xyz"

    # Load point clouds
    print("="*60)
    print("LOADING POINT CLOUDS")
    print("="*60)
    points1 = load_xyz_file(file1)
    points2 = load_xyz_file(file2)

    # Get bounds
    print("\n" + "="*60)
    print("ANALYZING BOUNDS")
    print("="*60)
    bounds1 = get_bounds(points1)
    bounds2 = get_bounds(points2)

    print_bounds(bounds1, "File 1 (2026-03-02)")
    print_bounds(bounds2, "File 2 (2026-03-12)")

    # Find overlap
    print("\n" + "="*60)
    print("FINDING OVERLAP")
    print("="*60)
    overlap = find_overlap(bounds1, bounds2)

    if overlap is None:
        print("ERROR: No overlap found between the two point clouds!")
        sys.exit(1)

    print_bounds(overlap, "Overlap Region")

    # Select tile region (adjustable size)
    tile_size = 50.0  # meters - you can adjust this
    print(f"\nSelecting {tile_size}m x {tile_size}m tile from center of overlap...")
    tile = select_tile_region(overlap, tile_size)
    print_bounds(tile, "Selected Tile")

    # Extract tiles
    print("\n" + "="*60)
    print("EXTRACTING TILES")
    print("="*60)
    tile1 = extract_tile(points1, tile['x_min'], tile['x_max'], tile['y_min'], tile['y_max'])
    tile2 = extract_tile(points2, tile['x_min'], tile['x_max'], tile['y_min'], tile['y_max'])

    print(f"\nTile 1 (2026-03-02): {len(tile1)} points")
    print(f"Tile 2 (2026-03-12): {len(tile2)} points")

    if len(tile1) == 0 or len(tile2) == 0:
        print("\nWARNING: One or both tiles are empty!")

        # Try with full overlap
        print("\nRetrying with full overlap area...")
        tile1 = extract_tile(points1, overlap['x_min'], overlap['x_max'], overlap['y_min'], overlap['y_max'])
        tile2 = extract_tile(points2, overlap['x_min'], overlap['x_max'], overlap['y_min'], overlap['y_max'])
        print(f"Full overlap Tile 1: {len(tile1)} points")
        print(f"Full overlap Tile 2: {len(tile2)} points")
        tile = overlap

    # Save tiles
    print("\n" + "="*60)
    print("SAVING TILES")
    print("="*60)
    output_file1 = base_dir / "tile_2026-03-02.xyz"
    output_file2 = base_dir / "tile_2026-03-12.xyz"

    save_xyz_file(tile1, output_file1)
    save_xyz_file(tile2, output_file2)

    # Save tile metadata
    metadata_file = base_dir / "tile_metadata.txt"
    with open(metadata_file, 'w') as f:
        f.write("TILE EXTRACTION METADATA\n")
        f.write("="*60 + "\n\n")
        f.write(f"Source files:\n")
        f.write(f"  File 1: {file1.name}\n")
        f.write(f"  File 2: {file2.name}\n\n")
        f.write(f"Tile bounds:\n")
        f.write(f"  X: [{tile['x_min']:.4f}, {tile['x_max']:.4f}]\n")
        f.write(f"  Y: [{tile['y_min']:.4f}, {tile['y_max']:.4f}]\n\n")
        f.write(f"Output files:\n")
        f.write(f"  Tile 1: {output_file1.name} ({len(tile1)} points)\n")
        f.write(f"  Tile 2: {output_file2.name} ({len(tile2)} points)\n")

    print(f"\nMetadata saved to: {metadata_file}")

    print("\n" + "="*60)
    print("DONE! ✓")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  - {output_file1}")
    print(f"  - {output_file2}")
    print(f"  - {metadata_file}")
    print(f"\nYou can now test your algorithm with these matching tiles!")


if __name__ == "__main__":
    main()
