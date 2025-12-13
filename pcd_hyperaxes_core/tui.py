"""
Text User Interface (TUI) for pcd_hyperaxes_core.

Interactive terminal-based interface for point cloud analysis.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header,
    Footer,
    Button,
    Input,
    Label,
    Static,
    DataTable,
    ProgressBar,
    TabbedContent,
    TabPane,
    Select,
)
from textual.binding import Binding
from textual.screen import Screen
from pathlib import Path
from typing import Optional
import asyncio
import json

from pcd_hyperaxes_core.core.io import load_point_cloud
from pcd_hyperaxes_core.core.preprocessing import preprocess_point_cloud
from pcd_hyperaxes_core.core.registration import register_point_clouds
from pcd_hyperaxes_core.core.analysis import compute_cloud_distances, analyze_changes
from pcd_hyperaxes_core.core.clustering import detect_missing_regions
from pcd_hyperaxes_core.output.models import AnalysisResults, ClusterInfo
from pcd_hyperaxes_core.config import (
    PreprocessingConfig,
    RegistrationConfig,
    AnalysisConfig,
    VisualizationConfig,
    OutputConfig,
)
import numpy as np


class ConfigScreen(Screen):
    """Configuration screen for analysis parameters."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("ctrl+r", "run_analysis", "Run Analysis"),
    ]

    def __init__(self, source_file: Optional[Path] = None, target_file: Optional[Path] = None):
        super().__init__()
        self.source_file = source_file
        self.target_file = target_file
        self.results = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Point Cloud Analysis Configuration", id="title")

        with ScrollableContainer():
            # File selection
            with Vertical(classes="box"):
                yield Label("📁 Input Files")
                yield Label(f"Source: {self.source_file or 'Not selected'}")
                yield Label(f"Target: {self.target_file or 'Not selected'}")
                with Horizontal(classes="button-group"):
                    yield Button("Select Source", id="select_source", variant="primary")
                    yield Button("Select Target", id="select_target", variant="primary")

            # Preprocessing parameters
            with Vertical(classes="box"):
                yield Label("⚙️  Preprocessing Parameters")
                yield Label("Voxel Size:")
                yield Input(placeholder="0.1", id="voxel_size", classes="parameter-input")
                yield Label("Remove Outliers:")
                yield Select(
                    [("Yes", True), ("No", False)],
                    value=True,
                    id="remove_outliers",
                    allow_blank=False,
                )

            # Analysis parameters
            with Vertical(classes="box"):
                yield Label("🔍 Analysis Parameters")
                yield Label("Distance Threshold:")
                yield Input(placeholder="0.2", id="distance_threshold", classes="parameter-input")
                yield Label("Region Threshold:")
                yield Input(placeholder="0.9", id="region_threshold", classes="parameter-input")
                yield Label("Minimum Region Size:")
                yield Input(placeholder="10", id="region_size", classes="parameter-input")

            # Output options
            with Vertical(classes="box"):
                yield Label("💾 Output Options")
                yield Label("Output Format:")
                yield Select(
                    [("JSON", "json"), ("CSV", "csv"), ("GeoJSON", "geojson"), ("Text", "text")],
                    id="output_format",
                    allow_blank=False,
                )
                yield Label("Output File:")
                yield Input(placeholder="results.json", id="output_file", classes="parameter-input")

            # Action buttons
            with Horizontal(classes="button-group"):
                yield Button("▶️  Run Analysis", id="run_analysis", variant="success")
                yield Button("❌ Cancel", id="cancel", variant="error")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "run_analysis":
            self.action_run_analysis()
        elif event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "select_source":
            self.notify("File selection not yet implemented - use CLI for now", severity="information")
        elif event.button.id == "select_target":
            self.notify("File selection not yet implemented - use CLI for now", severity="information")

    async def action_run_analysis(self) -> None:
        """Run the analysis with configured parameters."""
        if not self.source_file or not self.target_file:
            self.notify("Please select both source and target files", severity="error")
            return

        # Get parameters
        try:
            voxel_size = float(self.query_one("#voxel_size", Input).value or "0.1")
            distance_threshold = float(self.query_one("#distance_threshold", Input).value or "0.2")
            region_threshold = float(self.query_one("#region_threshold", Input).value or "0.9")
            region_size = int(self.query_one("#region_size", Input).value or "10")
            remove_outliers = self.query_one("#remove_outliers", Select).value
        except ValueError as e:
            self.notify(f"Invalid parameter value: {e}", severity="error")
            return

        # Show progress screen
        progress_screen = ProgressScreen(
            source_file=self.source_file,
            target_file=self.target_file,
            voxel_size=voxel_size,
            distance_threshold=distance_threshold,
            region_threshold=region_threshold,
            region_size=region_size,
            remove_outliers=remove_outliers,
        )
        self.app.push_screen(progress_screen)


class ProgressScreen(Screen):
    """Screen showing analysis progress."""

    def __init__(self, **params):
        super().__init__()
        self.params = params

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Analysis in Progress...", id="title")

        with ScrollableContainer():
            yield Label("🔄 Running point cloud analysis", classes="status info")
            yield ProgressBar(id="progress", total=100, show_eta=False)
            yield Label("", id="status_message")

        yield Footer()

    async def on_mount(self) -> None:
        """Start analysis when screen mounts."""
        asyncio.create_task(self.run_analysis())

    async def run_analysis(self) -> None:
        """Execute the analysis pipeline."""
        progress = self.query_one("#progress", ProgressBar)
        status = self.query_one("#status_message", Label)

        try:
            # Load point clouds
            status.update("Loading source point cloud...")
            progress.update(progress=10)
            source_orig = load_point_cloud(self.params["source_file"])

            status.update("Loading target point cloud...")
            progress.update(progress=20)
            target_orig = load_point_cloud(self.params["target_file"])

            # Preprocess
            status.update("Preprocessing point clouds...")
            progress.update(progress=30)
            prep_config = PreprocessingConfig(
                voxel_size=self.params["voxel_size"],
                remove_outliers=self.params["remove_outliers"],
            )
            source = preprocess_point_cloud(source_orig, prep_config)
            target = preprocess_point_cloud(target_orig, prep_config)

            # Register
            status.update("Registering point clouds...")
            progress.update(progress=50)
            source_aligned, _ = register_point_clouds(source, target, self.params["voxel_size"])

            # Analyze
            status.update("Computing distances...")
            progress.update(progress=70)
            distances = compute_cloud_distances(source_aligned, target)
            _, change_stats = analyze_changes(distances)

            # Detect regions
            status.update("Detecting change regions...")
            progress.update(progress=85)
            analysis_config = AnalysisConfig(
                distance_threshold=self.params["distance_threshold"],
                region_distance_threshold=self.params["region_threshold"],
                region_size_threshold=self.params["region_size"],
            )
            regions, missing_indices, region_labels = detect_missing_regions(
                source_aligned, target, distances, analysis_config
            )

            # Build results
            status.update("Generating results...")
            progress.update(progress=95)
            all_points = np.asarray(source_aligned.points)
            clusters = [
                ClusterInfo.from_indices(i, region, all_points, True)
                for i, region in enumerate(regions, 1)
            ]

            results = AnalysisResults(
                source_file=str(self.params["source_file"]),
                target_file=str(self.params["target_file"]),
                total_source_points=len(source_orig.points),
                total_target_points=len(target_orig.points),
                preprocessed_source_points=len(source.points),
                preprocessed_target_points=len(target.points),
                distance_stats={
                    "min": float(np.min(distances)),
                    "max": float(np.max(distances)),
                    "mean": float(np.mean(distances)),
                },
                change_stats=change_stats,
                num_clusters=len(regions),
                clusters=clusters,
            )

            progress.update(progress=100)
            status.update("✅ Analysis complete!")

            # Show results screen
            await asyncio.sleep(1)
            self.app.pop_screen()
            self.app.push_screen(ResultsScreen(results))

        except Exception as e:
            status.update(f"❌ Error: {str(e)}")
            self.notify(f"Analysis failed: {e}", severity="error")


class ResultsScreen(Screen):
    """Screen displaying analysis results."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("s", "save_results", "Save"),
    ]

    def __init__(self, results: AnalysisResults):
        super().__init__()
        self.results = results

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Analysis Results", id="title")

        with TabbedContent():
            with TabPane("Summary", id="summary_tab"):
                with ScrollableContainer():
                    yield Label(f"Source: {self.results.source_file}")
                    yield Label(f"Target: {self.results.target_file}")
                    yield Label(f"Total source points: {self.results.total_source_points:,}")
                    yield Label(f"Total target points: {self.results.total_target_points:,}")
                    yield Label(f"Clusters detected: {self.results.num_clusters}")

                    with Vertical(classes="box"):
                        yield Label("📊 Distance Statistics")
                        for key, value in self.results.distance_stats.items():
                            yield Label(f"  {key}: {value:.4f}")

                    with Vertical(classes="box"):
                        yield Label("📈 Change Statistics")
                        for key, value in self.results.change_stats.items():
                            yield Label(f"  {key}: {value:.4f}")

            with TabPane("Clusters", id="clusters_tab"):
                table = DataTable()
                table.add_columns("ID", "Points", "Centroid X", "Centroid Y", "Centroid Z")
                for cluster in self.results.clusters:
                    table.add_row(
                        str(cluster.cluster_id),
                        str(cluster.num_points),
                        f"{cluster.centroid[0]:.3f}",
                        f"{cluster.centroid[1]:.3f}",
                        f"{cluster.centroid[2]:.3f}",
                    )
                yield table

        with Horizontal(classes="button-group"):
            yield Button("💾 Save Results", id="save", variant="success")
            yield Button("🔙 Back", id="back", variant="primary")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save":
            self.action_save_results()
        elif event.button.id == "back":
            self.app.pop_screen()

    def action_save_results(self) -> None:
        """Save results to file."""
        output_file = Path("tui_analysis_results.json")
        with open(output_file, "w") as f:
            json.dump(self.results.to_dict(), f, indent=2)
        self.notify(f"Results saved to {output_file}", severity="information")


class PCDAnalyzerTUI(App):
    """Main TUI application for point cloud analysis."""

    CSS_PATH = "tui.tcss"
    TITLE = "PCD Hyperaxes Core - Point Cloud Analyzer"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
    ]

    def on_mount(self) -> None:
        """Initialize the application."""
        self.push_screen(ConfigScreen())

    def action_help(self) -> None:
        """Show help message."""
        self.notify(
            "Use arrow keys and tab to navigate. Press 'q' to quit.",
            title="Help",
            severity="information",
        )


def main():
    """Entry point for TUI application."""
    app = PCDAnalyzerTUI()
    app.run()


if __name__ == "__main__":
    main()
