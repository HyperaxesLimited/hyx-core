"""
Text User Interface (TUI) for pcd_hyperaxes_core.

Retro-style terminal interface for point cloud analysis.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-13
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Footer,
    Button,
    Input,
    Label,
    Static,
    DataTable,
    ProgressBar,
    Select,
)
from textual.binding import Binding
from textual.screen import Screen
from pathlib import Path
from typing import Optional
import asyncio
import json

from pcd_hyperaxes.core.io import load_point_cloud
from pcd_hyperaxes.core.preprocessing import preprocess_point_cloud
from pcd_hyperaxes.core.registration import register_point_clouds
from pcd_hyperaxes.core.analysis import compute_cloud_distances, analyze_changes
from pcd_hyperaxes.core.clustering import detect_missing_regions
from pcd_hyperaxes.output.models import AnalysisResults, ClusterInfo
from pcd_hyperaxes.config import (
    PreprocessingConfig,
    AnalysisConfig,
)
import numpy as np


LOGO = """    __  __                      ___
   / / / /_  ______  ___  _____/   |  _  _____  _____
  / /_/ / / / / __ \\/ _ \\/ ___/ /| | | |/_/ _ \\/ ___/
 / __  / /_/ / /_/ /  __/ /  / ___ |_>  </  __(__  )
/_/ /_/\\__, / .___/\\___/_/  /_/  |_/_/|_|\\___/____/
      /____/_/                                       """


class ConfigScreen(Screen):
    """Configuration screen for analysis parameters."""

    BINDINGS = [
        Binding("escape", "quit", "Quit"),
        Binding("ctrl+r", "run_analysis", "Run"),
    ]

    def __init__(self, source_file: Optional[Path] = None, target_file: Optional[Path] = None):
        super().__init__()
        self.source_file = source_file
        self.target_file = target_file

    def compose(self) -> ComposeResult:
        # Logo
        yield Static(LOGO, id="logo")
        yield Static("Point Cloud Difference Detection", id="subtitle")

        with ScrollableContainer():
            # File inputs
            with Vertical(classes="box"):
                yield Label("INPUT FILES", classes="box-title")
                yield Label("Source file:")
                yield Input(
                    placeholder="path/to/source.ply",
                    id="source_file",
                    value=str(self.source_file) if self.source_file else "",
                )
                yield Label("Target file:")
                yield Input(
                    placeholder="path/to/target.ply",
                    id="target_file",
                    value=str(self.target_file) if self.target_file else "",
                )

            # Parameters
            with Vertical(classes="box"):
                yield Label("PARAMETERS", classes="box-title")
                yield Label("Voxel size:")
                yield Input(placeholder="0.1", id="voxel_size", value="0.1")
                yield Label("Distance threshold:")
                yield Input(placeholder="0.2", id="distance_threshold", value="0.2")
                yield Label("Region threshold:")
                yield Input(placeholder="0.9", id="region_threshold", value="0.9")
                yield Label("Noise filtering:")
                yield Select(
                    [("Enabled", "true"), ("Disabled", "false")],
                    id="noise_filtering",
                    value="true",
                    allow_blank=False,
                )
                yield Label("Noise sigma:")
                yield Input(placeholder="2.0", id="noise_sigma", value="2.0")
                yield Label("Min local support:")
                yield Input(placeholder="3", id="min_local_support", value="3")

            # Output
            with Vertical(classes="box"):
                yield Label("OUTPUT", classes="box-title")
                yield Label("Format:")
                yield Select(
                    [("JSON", "json"), ("CSV", "csv"), ("GeoJSON", "geojson"), ("Text", "text")],
                    id="output_format",
                    value="json",
                    allow_blank=False,
                )
                yield Label("Save to file (optional):")
                yield Input(placeholder="results.json", id="output_file")

            # Action buttons
            with Horizontal(classes="button-group"):
                yield Button("RUN ANALYSIS", id="run_btn", variant="primary")
                yield Button("QUIT", id="quit_btn")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "run_btn":
            self.action_run_analysis()
        elif event.button.id == "quit_btn":
            self.app.exit()

    async def action_run_analysis(self) -> None:
        """Run the analysis with configured parameters."""
        # Get file paths
        source_path = self.query_one("#source_file", Input).value.strip()
        target_path = self.query_one("#target_file", Input).value.strip()

        if not source_path or not target_path:
            self.notify("Please specify both source and target files", severity="error")
            return

        source_file = Path(source_path)
        target_file = Path(target_path)

        if not source_file.exists():
            self.notify(f"Source file not found: {source_file}", severity="error")
            return
        if not target_file.exists():
            self.notify(f"Target file not found: {target_file}", severity="error")
            return

        # Get parameters
        try:
            voxel_size = float(self.query_one("#voxel_size", Input).value or "0.1")
            distance_threshold = float(self.query_one("#distance_threshold", Input).value or "0.2")
            region_threshold = float(self.query_one("#region_threshold", Input).value or "0.9")
            noise_filtering = self.query_one("#noise_filtering", Select).value == "true"
            noise_sigma = float(self.query_one("#noise_sigma", Input).value or "2.0")
            min_local_support = int(self.query_one("#min_local_support", Input).value or "3")
            output_format = self.query_one("#output_format", Select).value
            output_file = self.query_one("#output_file", Input).value.strip()
        except ValueError as e:
            self.notify(f"Invalid parameter value: {e}", severity="error")
            return

        # Show progress screen
        progress_screen = ProgressScreen(
            source_file=source_file,
            target_file=target_file,
            voxel_size=voxel_size,
            distance_threshold=distance_threshold,
            region_threshold=region_threshold,
            noise_filtering=noise_filtering,
            noise_sigma=noise_sigma,
            min_local_support=min_local_support,
            output_format=output_format,
            output_file=output_file if output_file else None,
        )
        self.app.push_screen(progress_screen)


class ProgressScreen(Screen):
    """Screen showing analysis progress."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, **params):
        super().__init__()
        self.params = params

    def compose(self) -> ComposeResult:
        yield Static(LOGO, id="logo")
        yield Static("Running Analysis...", id="subtitle")

        with ScrollableContainer():
            yield Label("", id="status_msg", classes="status status-info")
            yield ProgressBar(id="progress", total=100, show_eta=False)

        yield Footer()

    async def on_mount(self) -> None:
        """Start analysis when screen mounts."""
        asyncio.create_task(self.run_analysis())

    async def run_analysis(self) -> None:
        """Execute the analysis pipeline."""
        progress = self.query_one("#progress", ProgressBar)
        status = self.query_one("#status_msg", Label)

        try:
            # Load point clouds
            status.update("[ 1/6 ] Loading source point cloud...")
            status.remove_class("status-error")
            status.add_class("status-info")
            progress.update(progress=10)
            await asyncio.sleep(0.1)
            source_orig = load_point_cloud(self.params["source_file"])

            status.update("[ 2/6 ] Loading target point cloud...")
            progress.update(progress=20)
            await asyncio.sleep(0.1)
            target_orig = load_point_cloud(self.params["target_file"])

            # Preprocess
            status.update("[ 3/6 ] Preprocessing clouds...")
            progress.update(progress=35)
            await asyncio.sleep(0.1)
            prep_config = PreprocessingConfig(voxel_size=self.params["voxel_size"])
            source = preprocess_point_cloud(source_orig, prep_config)
            target = preprocess_point_cloud(target_orig, prep_config)

            # Register
            status.update("[ 4/6 ] Registering clouds (ICP)...")
            progress.update(progress=50)
            await asyncio.sleep(0.1)
            source_aligned, _ = register_point_clouds(source, target, self.params["voxel_size"])

            # Analyze
            status.update("[ 5/6 ] Computing distances...")
            progress.update(progress=70)
            await asyncio.sleep(0.1)
            from pcd_hyperaxes.config import NoiseFilterConfig
            noise_filter = NoiseFilterConfig(
                enable_statistical_filter=self.params["noise_filtering"],
                enable_local_validation=self.params["noise_filtering"],
                noise_tolerance_sigma=self.params["noise_sigma"],
                min_local_support=self.params["min_local_support"],
            )
            analysis_config = AnalysisConfig(
                distance_threshold=self.params["distance_threshold"],
                region_distance_threshold=self.params["region_threshold"],
                noise_filter=noise_filter,
            )
            distances = compute_cloud_distances(source_aligned, target, analysis_config)
            source_points = np.asarray(source_aligned.points)
            _, change_stats = analyze_changes(distances, analysis_config, source_points)

            # Detect regions
            status.update("[ 6/6 ] Detecting change regions...")
            progress.update(progress=85)
            await asyncio.sleep(0.1)
            regions, missing_indices, region_labels = detect_missing_regions(
                source_aligned, target, distances, analysis_config
            )

            # Build results
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
                    "median": float(np.median(distances)),
                    "std": float(np.std(distances)),
                },
                change_stats=change_stats,
                num_clusters=len(regions),
                clusters=clusters,
            )

            progress.update(progress=100)
            status.update("[ DONE ] Analysis complete")
            status.remove_class("status-info")
            status.add_class("status-success")

            # Show results screen
            await asyncio.sleep(0.5)
            self.app.pop_screen()
            self.app.push_screen(
                ResultsScreen(
                    results,
                    output_format=self.params.get("output_format", "json"),
                    output_file=self.params.get("output_file"),
                )
            )

        except Exception as e:
            status.update(f"[ ERROR ] {str(e)}")
            status.remove_class("status-info")
            status.add_class("status-error")
            self.notify(f"Analysis failed: {e}", severity="error", timeout=10)


class ResultsScreen(Screen):
    """Screen displaying analysis results."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("s", "save_results", "Save"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        results: AnalysisResults,
        output_format: str = "json",
        output_file: Optional[str] = None,
    ):
        super().__init__()
        self.results = results
        self.output_format = output_format
        self.output_file = output_file

    def compose(self) -> ComposeResult:
        yield Static(LOGO, id="logo")
        yield Static("Analysis Results", id="subtitle")

        with ScrollableContainer():
            # Summary
            with Vertical(classes="box"):
                yield Label("SUMMARY", classes="box-title")
                yield Label(f"Source: {Path(self.results.source_file).name}")
                yield Label(f"Target: {Path(self.results.target_file).name}")
                yield Label(f"Clusters detected: {self.results.num_clusters}")
                yield Label(
                    f"Changed points: {self.results.change_stats.get('num_changed_points', 0)}"
                )

            # Distance stats
            with Vertical(classes="box"):
                yield Label("DISTANCE STATISTICS", classes="box-title")
                for key, value in self.results.distance_stats.items():
                    yield Label(f"{key:12s} : {value:.4f}")

            # Change stats
            with Vertical(classes="box"):
                yield Label("CHANGE STATISTICS", classes="box-title")
                for key, value in self.results.change_stats.items():
                    yield Label(f"{key:20s} : {value:.4f}")

            # Clusters table
            if self.results.clusters:
                with Vertical(classes="box"):
                    yield Label("DETECTED CLUSTERS", classes="box-title")
                    table = DataTable()
                    table.add_columns("ID", "Points", "X", "Y", "Z")
                    for cluster in self.results.clusters:
                        table.add_row(
                            str(cluster.cluster_id),
                            str(cluster.num_points),
                            f"{cluster.centroid[0]:.2f}",
                            f"{cluster.centroid[1]:.2f}",
                            f"{cluster.centroid[2]:.2f}",
                        )
                    yield table

            # Action buttons
            with Horizontal(classes="button-group"):
                yield Button("SAVE", id="save_btn", variant="primary")
                yield Button("BACK", id="back_btn")
                yield Button("QUIT", id="quit_btn")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save_btn":
            self.action_save_results()
        elif event.button.id == "back_btn":
            self.app.pop_screen()
        elif event.button.id == "quit_btn":
            self.app.exit()

    def action_save_results(self) -> None:
        """Save results to file."""
        from pcd_hyperaxes.output.formatters import ResultFormatter
        from pcd_hyperaxes.config import OutputConfig

        if not self.output_file:
            self.output_file = f"results.{self.output_format}"

        output_config = OutputConfig(
            mode="full", format=self.output_format, output_file=Path(self.output_file)
        )
        formatter = ResultFormatter(output_config)
        formatter.format_and_save(self.results)

        self.notify(f"Results saved to {self.output_file}", severity="information")


class PCDAnalyzerTUI(App):
    """Main TUI application for point cloud analysis."""

    CSS_PATH = "tui.tcss"
    TITLE = "HyperAxes Point Cloud Analyzer"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """Initialize the application."""
        self.push_screen(ConfigScreen())


def main():
    """Entry point for TUI application."""
    app = PCDAnalyzerTUI()
    app.run()


if __name__ == "__main__":
    main()
