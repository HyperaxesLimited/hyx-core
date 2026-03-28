#!/usr/bin/env python3
"""
Quick test script for tile extraction functionality.
"""

from pathlib import Path
from pcd_hyperaxes_core import (
    load_point_cloud,
    extract_comparable_tiles,
    save_tile_metadata,
)
from pcd_hyperaxes_core.core.io import save_point_cloud


def main():
    base_dir = Path(__file__).parent

    # Input files
    files = [
        base_dir / "2026-03-02-mbes-genova-0.25m_GB.xyz",
        base_dir / "2026-03-12-mbes-genova-0.25m_GB.xyz",
    ]

    print("Loading point clouds...")
    pcds = [load_point_cloud(str(f)) for f in files]

    print("\nExtracting comparable tiles (50m x 50m)...")
    tiles, tile_bounds, original_bounds = extract_comparable_tiles(
        pcds,
        tile_size=50.0
    )

    print(f"\nTile bounds: {tile_bounds}")
    print(f"Tile area: {tile_bounds.x_range:.2f}m x {tile_bounds.y_range:.2f}m")

    # Save tiles
    output_files = []
    tile_counts = []

    for i, (tile, f) in enumerate(zip(tiles, files), 1):
        date = "-".join(f.stem.split("-")[:3])
        output_file = base_dir / f"tile_{date}.ply"
        print(f"\nSaving tile {i}: {output_file.name} ({len(tile.points)} points)")
        save_point_cloud(tile, str(output_file))
        output_files.append(output_file)
        tile_counts.append(len(tile.points))

    # Save metadata
    metadata_file = base_dir / "tiles_metadata.txt"
    save_tile_metadata(
        metadata_file,
        [f.name for f in files],
        tile_bounds,
        original_bounds,
        tile_counts,
    )

    print(f"\n✓ Done! Files saved:")
    for f in output_files:
        print(f"  - {f.name}")
    print(f"  - {metadata_file.name}")

    print(f"\nTest comparison with:")
    print(f"  pcd-hyperaxes {output_files[0].name} {output_files[1].name}")


if __name__ == "__main__":
    main()
