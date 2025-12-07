"""
Data models for analysis results.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import numpy as np
import json


@dataclass
class ClusterInfo:
    """Information about a detected cluster."""

    cluster_id: int
    num_points: int
    centroid: tuple[float, float, float]
    points: Optional[List[tuple[float, float, float]]] = None

    @classmethod
    def from_indices(
        cls, cluster_id: int, indices: List[int], all_points: np.ndarray, include_points: bool = False
    ):
        """Create ClusterInfo from point indices."""
        cluster_points = all_points[indices]
        centroid = tuple(np.mean(cluster_points, axis=0).tolist())

        points = None
        if include_points:
            points = [tuple(p.tolist()) for p in cluster_points]

        return cls(cluster_id=cluster_id, num_points=len(indices), centroid=centroid, points=points)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AnalysisResults:
    """Complete analysis results."""

    source_file: str
    target_file: str
    total_source_points: int
    total_target_points: int
    preprocessed_source_points: int
    preprocessed_target_points: int
    distance_stats: Dict[str, float]
    change_stats: Dict[str, float]
    num_clusters: int
    clusters: List[ClusterInfo]
    registration_fitness: Optional[float] = None
    registration_rmse: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        result = asdict(self)
        result["clusters"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in self.clusters]
        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_centroid_only(self) -> Dict:
        """Return only cluster centroids."""
        return {
            "num_clusters": self.num_clusters,
            "clusters": [
                {"cluster_id": c.cluster_id, "num_points": c.num_points, "centroid": c.centroid}
                for c in self.clusters
            ],
        }

    def to_summary(self) -> Dict:
        """Return summary statistics only."""
        return {
            "source_file": self.source_file,
            "target_file": self.target_file,
            "total_source_points": self.total_source_points,
            "total_target_points": self.total_target_points,
            "distance_stats": self.distance_stats,
            "change_stats": self.change_stats,
            "num_clusters": self.num_clusters,
        }
