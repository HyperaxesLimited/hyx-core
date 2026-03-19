"""
State management for LLM conversational interface.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict
import open3d as o3d

from pcd_hyperaxes_core.config import (
    PreprocessingConfig,
    RegistrationConfig,
    AnalysisConfig,
    OutputConfig,
    PipelineConfig,
)
from pcd_hyperaxes_core.output.models import AnalysisResults


@dataclass
class ConversationState:
    """Maintains the state of the conversational session."""

    # File paths
    source_file: Optional[Path] = None
    target_file: Optional[Path] = None

    # Configuration objects
    preprocessing_config: Optional[PreprocessingConfig] = None
    registration_config: Optional[RegistrationConfig] = None
    analysis_config: Optional[AnalysisConfig] = None
    output_config: Optional[OutputConfig] = None

    # Results
    last_results: Optional[AnalysisResults] = None
    source_aligned: Optional[o3d.geometry.PointCloud] = None

    # Conversation history for Ollama
    conversation_history: List[Dict[str, str]] = field(default_factory=list)

    def is_ready_for_analysis(self) -> bool:
        """Check if we have the minimum required data to run analysis."""
        return self.source_file is not None and self.target_file is not None

    def get_summary(self) -> str:
        """Get a summary of the current state for LLM context."""
        parts = []

        if self.source_file:
            parts.append(f"Source: {self.source_file.name}")

        if self.target_file:
            parts.append(f"Target: {self.target_file.name}")

        if self.preprocessing_config:
            parts.append(f"Voxel size: {self.preprocessing_config.voxel_size}")

        if self.analysis_config:
            parts.append(f"Distance threshold: {self.analysis_config.distance_threshold}")

        if self.last_results:
            parts.append(f"Last analysis: {self.last_results.num_clusters} clusters found")

        return " | ".join(parts) if parts else "No configuration yet"

    def get_config(self) -> PipelineConfig:
        """Build complete pipeline config with defaults where not specified."""
        return PipelineConfig(
            preprocessing=self.preprocessing_config or PreprocessingConfig(),
            registration=self.registration_config or RegistrationConfig(),
            analysis=self.analysis_config or AnalysisConfig(),
            visualization=None,  # Not used in LLM interface
            output=self.output_config or OutputConfig(),
            logging=None,  # Managed separately
        )
