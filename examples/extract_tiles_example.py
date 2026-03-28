#!/usr/bin/env python3
"""
Example: Extract Comparable Tiles from Multiple Point Clouds

This example demonstrates how to use the tiling functionality to extract
comparable tiles from multiple point cloud files for algorithm testing.

Author: Nicola Sabino
Company: Hyperaxes
"""

from pathlib import Path
from pcd_hyperaxes_core import (
    load_point_cloud,
    extract_comparable_tiles,
    save_tile_metadata,
)
from pcd_hyperaxes_core.core.io import save_point_cloud
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Extract comparable tiles from MBES Genova datasets."""

    # Input files
    base_dir = Path(__file__).parent.parent
    file_paths = [
        base_dir / "2026-03-02-mbes-genova-0.25m_GB.xyz",
        base_dir / "2026-03-12-mbes-genova-0.25m_GB.xyz",
    ]

    # Verify files exist
    for fpath in file_paths:
        if not fpath.exists():
            logger.error(f"File not found: {fpath}")
            return

    logger.info("="*60)
    logger.info("EXTRACTING COMPARABLE TILES")
    logger.info("="*60)

    # Load point clouds
    logger.info("\nLoading point clouds...")
    point_clouds = []
    for fpath in file_paths:
        logger.info(f"  Loading {fpath.name}...")
        pcd = load_point_cloud(str(fpath))
        point_clouds.append(pcd)
        logger.info(f"    Loaded {len(pcd.points)} points")

    # Extract comparable tiles (50m x 50m from center of overlap)
    logger.info("\nExtracting tiles...")
    tiles, tile_bounds, original_bounds = extract_comparable_tiles(
        point_clouds,
        tile_size=50.0  # 50m x 50m tile
    )

    # Display results
    logger.info("\n" + "="*60)
    logger.info("EXTRACTION RESULTS")
    logger.info("="*60)
    logger.info(f"\nTile bounds: {tile_bounds}")
    logger.info(f"Tile area: {tile_bounds.x_range:.2f}m x {tile_bounds.y_range:.2f}m")

    tile_point_counts = []
    for i, tile in enumerate(tiles, 1):
        num_points = len(tile.points)
        tile_point_counts.append(num_points)
        logger.info(f"\nTile {i}: {num_points} points")

    # Save extracted tiles
    logger.info("\n" + "="*60)
    logger.info("SAVING TILES")
    logger.info("="*60)

    output_dir = base_dir / "tiles_output"
    output_dir.mkdir(exist_ok=True)

    output_files = []
    for i, (tile, fpath) in enumerate(zip(tiles, file_paths), 1):
        # Create output filename based on original
        date_str = fpath.stem.split("-")[0:3]
        date_str = "-".join(date_str)
        output_file = output_dir / f"tile_{date_str}.ply"

        logger.info(f"Saving tile {i} to {output_file.name}...")
        save_point_cloud(tile, str(output_file))
        output_files.append(output_file)

    # Save metadata
    metadata_file = output_dir / "tiles_metadata.txt"
    logger.info(f"Saving metadata to {metadata_file.name}...")

    save_tile_metadata(
        filepath=metadata_file,
        source_files=[f.name for f in file_paths],
        tile_bounds=tile_bounds,
        original_bounds=original_bounds,
        tile_point_counts=tile_point_counts,
    )

    # Summary
    logger.info("\n" + "="*60)
    logger.info("DONE! ✓")
    logger.info("="*60)
    logger.info(f"\nOutput directory: {output_dir}")
    logger.info("\nGenerated files:")
    for f in output_files:
        logger.info(f"  - {f.name}")
    logger.info(f"  - {metadata_file.name}")

    logger.info("\nYou can now compare these tiles using:")
    logger.info(f"  pcd-hyperaxes {output_files[0]} {output_files[1]}")


if __name__ == "__main__":
    main()
