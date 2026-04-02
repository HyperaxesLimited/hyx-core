"""
Output formatting for different output modes.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import json
import csv
from pathlib import Path
import logging
from pcd_hyperaxes.output.models import AnalysisResults
from pcd_hyperaxes.config import OutputConfig

logger = logging.getLogger(__name__)


class ResultFormatter:
    """Formats and outputs analysis results."""

    def __init__(self, config: OutputConfig = None):
        """Initialize formatter with configuration."""
        self.config = config or OutputConfig()

    def format_and_save(self, results: AnalysisResults) -> str:
        """Format results according to configuration and optionally save."""
        # Select data based on mode
        if self.config.mode == "centroid_only":
            data = results.to_centroid_only()
        elif self.config.mode == "summary":
            data = results.to_summary()
        else:  # full
            data = results.to_dict()

        # Format based on format type
        if self.config.format == "json":
            output = json.dumps(data, indent=2)
        elif self.config.format == "csv":
            output = self._to_csv(data)
        elif self.config.format == "geojson":
            output = self._to_geojson(data, results)
        else:  # text
            output = self._to_text(data)

        # Save if output file specified
        if self.config.output_file:
            self._save_output(output)

        return output

    def _to_csv(self, data: dict) -> str:
        """Format data as CSV."""
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        if "clusters" in data:
            # Header
            writer.writerow(["cluster_id", "num_points", "centroid_x", "centroid_y", "centroid_z"])
            # Rows
            for cluster in data["clusters"]:
                centroid = cluster["centroid"]
                writer.writerow([cluster["cluster_id"], cluster["num_points"], centroid[0], centroid[1], centroid[2]])
        else:
            # Summary CSV
            writer.writerow(["key", "value"])
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        writer.writerow([f"{key}.{sub_key}", sub_value])
                else:
                    writer.writerow([key, value])

        return output.getvalue()

    def _to_geojson(self, data: dict, results: AnalysisResults) -> str:
        """
        Format data as GeoJSON FeatureCollection.

        Each cluster becomes a Feature with:
        - Point geometry at centroid (or MultiPoint for all points in full mode)
        - Properties: cluster_id, num_points, centroid coordinates
        """
        features = []

        if "clusters" in data:
            for cluster in data["clusters"]:
                centroid = cluster["centroid"]

                # Create feature properties
                properties = {
                    "cluster_id": cluster["cluster_id"],
                    "num_points": cluster["num_points"],
                    "centroid_x": centroid[0],
                    "centroid_y": centroid[1],
                    "centroid_z": centroid[2],
                }

                # Add metadata if available
                if "source_file" in data:
                    properties["source_file"] = data["source_file"]
                    properties["target_file"] = data["target_file"]

                # Geometry based on mode
                if "points" in cluster and cluster["points"] and self.config.mode == "full":
                    # Full mode: MultiPoint with all points
                    coordinates = [[p[0], p[1], p[2]] for p in cluster["points"]]
                    geometry = {
                        "type": "MultiPoint",
                        "coordinates": coordinates
                    }
                else:
                    # Centroid mode: Single Point at centroid
                    geometry = {
                        "type": "Point",
                        "coordinates": [centroid[0], centroid[1], centroid[2]]
                    }

                feature = {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": properties
                }
                features.append(feature)

        # Create GeoJSON FeatureCollection
        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "num_clusters": len(features),
                "analysis_type": "point_cloud_difference_detection",
                "software": "pcd_hyperaxes_core",
                "version": "1.0.0"
            }
        }

        # Add statistics to metadata if available
        if "distance_stats" in data:
            geojson["metadata"]["distance_stats"] = data["distance_stats"]
        if "change_stats" in data:
            geojson["metadata"]["change_stats"] = data["change_stats"]

        return json.dumps(geojson, indent=2)

    def _to_text(self, data: dict) -> str:
        """Format data as human-readable text."""
        lines = []
        lines.append("=" * 60)
        lines.append("POINT CLOUD ANALYSIS RESULTS")
        lines.append("=" * 60)

        if "source_file" in data:
            lines.append(f"\nSource file: {data['source_file']}")
            lines.append(f"Target file: {data['target_file']}")

        if "distance_stats" in data:
            lines.append("\nDistance Statistics:")
            for key, value in data["distance_stats"].items():
                lines.append(f"  {key}: {value:.4f}")

        if "change_stats" in data:
            lines.append("\nChange Statistics:")
            for key, value in data["change_stats"].items():
                lines.append(f"  {key}: {value:.4f}")

        if "clusters" in data:
            lines.append(f"\nDetected Clusters: {len(data['clusters'])}")
            lines.append("=" * 60)

            for cluster in data["clusters"]:
                lines.append(f"\nCluster {cluster['cluster_id']}:")
                lines.append(f"  Number of points: {cluster['num_points']}")
                centroid = cluster["centroid"]
                lines.append(f"  Centroid: x={centroid[0]:.3f}, y={centroid[1]:.3f}, z={centroid[2]:.3f}")

                if "points" in cluster and cluster["points"]:
                    lines.append("  Points:")
                    for i, point in enumerate(cluster["points"][:10]):  # Limit to first 10
                        lines.append(f"    Point {i}: x={point[0]:.3f}, y={point[1]:.3f}, z={point[2]:.3f}")
                    if len(cluster["points"]) > 10:
                        lines.append(f"    ... and {len(cluster['points']) - 10} more points")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def _save_output(self, output: str) -> None:
        """Save output to file."""
        output_path = Path(self.config.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(output)

        logger.info(f"Results saved to {output_path}")
