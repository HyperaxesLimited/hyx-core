# pcd_hyperaxes_core

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python module for point cloud comparison, registration, and difference detection.

**Author:** Nicola Sabino  
**Company:** Hyperaxes  
**Date:** 2025-12-07

## Features

- ✅ **Multi-format Support**: LAS, LAZ, PLY, PCD, XYZ
- ✅ **Automatic Registration**: ICP-based point cloud alignment
- ✅ **Change Detection**: Statistical analysis and clustering
- ✅ **Multiple Output Modes**: Full details, centroids only, or summary statistics
- ✅ **Flexible Output Formats**: JSON, CSV, GeoJSON, or human-readable text
- ✅ **GeoJSON Export**: Direct export for GIS applications (QGIS, ArcGIS, web mapping)
- ✅ **Visualization**: Interactive 3D visualization with Open3D
- ✅ **Text User Interface (TUI)**: Modern terminal UI with Textual
- ✅ **Command-Line Interface**: Easy-to-use CLI for batch processing
- ✅ **Python API**: Programmatic access for custom workflows

## Prerequisites

Before installing, ensure you have the following installed on your system:

### Python 3.9 or higher

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python@3.9

# Or download from python.org
# https://www.python.org/downloads/
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3.9 python3.9-venv python3-pip
```

**Linux (RHEL/CentOS/Fedora):**
```bash
sudo dnf install python39 python39-pip
# or
sudo yum install python39 python39-pip
```

**Windows:**
- Download installer from [python.org](https://www.python.org/downloads/)
- **Important:** During installation, check "Add Python to PATH"
- Verify installation: Open Command Prompt and run `python --version`

### Git

**macOS:**
```bash
# Using Homebrew
brew install git

# Or install Xcode Command Line Tools
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install git
```

**Linux (RHEL/CentOS/Fedora):**
```bash
sudo dnf install git
```

**Windows:**
- Download from [git-scm.com](https://git-scm.com/download/win)
- During installation, select "Git from the command line and also from 3rd-party software"

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/hyperaxes/pcd_hyperaxes_core.git
cd pcd_hyperaxes_core
```

Or if using a different repository URL:
```bash
git clone <your-repository-url>
cd 3d-python-hyperaxes
```

### 2. Create Virtual Environment (Recommended)

Using a virtual environment isolates dependencies and prevents conflicts with system packages.

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1
```

*Note: If you get an execution policy error on PowerShell, run:*
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install the Package

After activating your virtual environment:

```bash
# Install in editable mode with all dependencies
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### 4. Verify Installation

```bash
# Check that CLI commands are available
pcd-hyperaxes --help
pcd-hyperaxes-tui --help

# Verify Python can import the module
python -c "import pcd_hyperaxes_core; print('✓ Installation successful')"
```

### Using pip (when published to PyPI)

```bash
pip install pcd-hyperaxes-core
```

## Troubleshooting

### Common Issues

**1. "pip: command not found" or "pip3: command not found"**
- Ensure Python is installed correctly
- Try using `python -m pip` instead of `pip`
- On Linux, install pip: `sudo apt-get install python3-pip`

**2. Permission Errors on macOS/Linux**
- Use a virtual environment (recommended)
- Or use `--user` flag: `pip install --user -e .`
- Avoid using `sudo pip` (can cause system-wide conflicts)

**3. Open3D Installation Issues**
- Open3D requires a recent C++ compiler
- **macOS:** Install Xcode Command Line Tools: `xcode-select --install`
- **Linux:** Install build tools: `sudo apt-get install build-essential`
- **Windows:** Ensure Visual C++ redistributables are installed

**4. PowerShell Execution Policy Error (Windows)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**5. "Module not found" after installation**
- Ensure your virtual environment is activated
- Try deactivating and reactivating: `deactivate` then `source .venv/bin/activate`
- Reinstall: `pip install -e .`

**6. Git Clone Issues**
- If using SSH: Ensure your SSH key is added to GitHub/GitLab
- If using HTTPS: May need to configure credentials
- Check firewall/proxy settings

### Platform-Specific Notes

**macOS (Apple Silicon M1/M2/M3):**
- Some dependencies may require Rosetta 2
- If you encounter issues, try installing x86_64 Python via Homebrew
- Open3D has native ARM support in recent versions

**Linux:**
- Some distributions may require additional system dependencies for Open3D
- Ubuntu/Debian: `sudo apt-get install libgl1-mesa-glx libglib2.0-0`
- CentOS/RHEL: `sudo yum install mesa-libGL`

**Windows:**
- Ensure Visual C++ Redistributables are installed (required by Open3D)
- Download from: https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads
- If visualization doesn't work, update your graphics drivers

## Quick Start

### Interactive TUI (Text User Interface)

The easiest way to use the tool is through the interactive TUI:

```bash
# Launch the TUI
pcd-hyperaxes-tui

# Or with Python module
python3 -m pcd_hyperaxes_core.tui
```

**TUI Features:**
- 🖥️  Interactive terminal interface
- 📁 Easy file selection
- ⚙️  Visual parameter configuration
- 📊 Real-time progress tracking
- 📈 Results visualization in tables
- 💾 Export results directly

### Command Line

```bash
# Basic comparison with visualization
pcd-hyperaxes source.ply target.ply

# Save results to JSON file
pcd-hyperaxes source.las target.las -o results.json

# Centroid-only mode without plots
pcd-hyperaxes source.ply target.ply --mode centroid --no-plot -o centroids.json

# Custom parameters
pcd-hyperaxes source.ply target.ply \
  --voxel-size 0.05 \
  --distance-threshold 0.3 \
  --region-threshold 1.0 \
  --format csv -o results.csv

# Export to GeoJSON for GIS applications
pcd-hyperaxes source.ply target.ply \
  --mode centroid \
  --format geojson \
  --no-plot \
  -o differences.geojson
```

### Python API

```python
from pcd_hyperaxes_core import (
    load_point_cloud,
    preprocess_point_cloud,
    register_point_clouds,
    compute_cloud_distances,
    detect_missing_regions,
    PreprocessingConfig,
    AnalysisConfig
)

# Load point clouds
source = load_point_cloud("source.ply")
target = load_point_cloud("target.ply")

# Preprocess
prep_config = PreprocessingConfig(voxel_size=0.1)
source_prep = preprocess_point_cloud(source, prep_config)
target_prep = preprocess_point_cloud(target, prep_config)

# Register
source_aligned, transform = register_point_clouds(source_prep, target_prep, voxel_size=0.1)

# Analyze differences
distances = compute_cloud_distances(source_aligned, target_prep)
regions, indices, labels = detect_missing_regions(source_aligned, target_prep, distances)

print(f"Found {len(regions)} regions of differences")
```

## Command-Line Options

### Required Arguments

- `source`: Path to source point cloud file
- `target`: Path to target point cloud file

### Preprocessing Options

- `--voxel-size SIZE`: Voxel size for downsampling (default: 0.1)
- `--no-outlier-removal`: Disable outlier removal

### Registration Options

- `--skip-registration`: Skip registration (assume clouds are already aligned)
- `--max-iterations N`: Maximum ICP iterations (default: 100)

### Analysis Options

- `--distance-threshold DIST`: Distance threshold for change detection (default: 0.2)
- `--region-threshold DIST`: Distance threshold for region detection (default: 0.9)
- `--region-size N`: Minimum region size in points (default: 10)

### Output Options

- `--mode {full,centroid,summary}`: Output mode (default: full)
  - `full`: All cluster details including point coordinates
  - `centroid`: Only cluster centroids
  - `summary`: Statistics only
- `--format {json,text,csv,geojson}`: Output format (default: json)
- `-o, --output FILE`: Save results to file

### Visualization Options

- `--no-plot`: Disable visualization windows
- `--show-heatmap`: Show distance heatmap visualization

### Logging Options

- `-v, --verbose`: Enable verbose output
- `--log-level {DEBUG,INFO,WARNING,ERROR}`: Logging level (default: INFO)

## Output Examples

### Full Mode (JSON)

```json
{
  "source_file": "source.ply",
  "target_file": "target.ply",
  "total_source_points": 1000000,
  "total_target_points": 1000000,
  "preprocessed_source_points": 50000,
  "preprocessed_target_points": 50000,
  "distance_stats": {
    "min": 0.001,
    "max": 2.5,
    "mean": 0.15,
    "median": 0.12,
    "std": 0.25
  },
  "change_stats": {
    "num_changed_points": 1500,
    "mean_change": 0.45,
    "max_change": 2.5,
    "volume_change_percentage": 3.0
  },
  "num_clusters": 3,
  "clusters": [
    {
      "cluster_id": 1,
      "num_points": 850,
      "centroid": [10.5, 20.3, 5.2],
      "points": [[10.1, 20.2, 5.1], ...]
    }
  ]
}
```

### Centroid Mode (CSV)

```csv
cluster_id,num_points,centroid_x,centroid_y,centroid_z
1,850,10.5,20.3,5.2
2,450,15.2,25.1,3.8
3,200,8.3,18.9,6.1
```

### Summary Mode (Text)

```
============================================================
POINT CLOUD ANALYSIS RESULTS
============================================================

Source file: source.ply
Target file: target.ply

Distance Statistics:
  min: 0.0010
  max: 2.5000
  mean: 0.1500
  median: 0.1200
  std: 0.2500

Change Statistics:
  num_changed_points: 1500
  mean_change: 0.4500
  max_change: 2.5000
  volume_change_percentage: 3.0000

Detected Clusters: 3
============================================================
```

### GeoJSON Mode

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [10.5, 20.3, 5.2]
      },
      "properties": {
        "cluster_id": 1,
        "num_points": 850,
        "centroid_x": 10.5,
        "centroid_y": 20.3,
        "centroid_z": 5.2,
        "source_file": "source.ply",
        "target_file": "target.ply"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [15.2, 25.1, 3.8]
      },
      "properties": {
        "cluster_id": 2,
        "num_points": 450,
        "centroid_x": 15.2,
        "centroid_y": 25.1,
        "centroid_z": 3.8,
        "source_file": "source.ply",
        "target_file": "target.ply"
      }
    }
  ],
  "metadata": {
    "num_clusters": 2,
    "analysis_type": "point_cloud_difference_detection",
    "software": "pcd_hyperaxes_core",
    "version": "1.0.0",
    "distance_stats": {
      "min": 0.001,
      "max": 2.5,
      "mean": 0.15,
      "median": 0.12,
      "std": 0.25
    },
    "change_stats": {
      "num_changed_points": 1500,
      "mean_change": 0.45,
      "max_change": 2.5,
      "volume_change_percentage": 3.0
    }
  }
}
```

**GeoJSON can be directly imported into:**
- QGIS (Quantum GIS)
- ArcGIS / ArcGIS Pro
- Web mapping libraries (Leaflet, Mapbox, OpenLayers)
- PostGIS databases
- Google Earth (convert to KML)

## Module Structure

```
pcd_hyperaxes_core/
├── __init__.py          # Package exports
├── __main__.py          # Entry point for python -m
├── cli.py               # Command-line interface
├── config.py            # Configuration classes
├── core/                # Core functionality
│   ├── io.py           # File I/O
│   ├── preprocessing.py # Preprocessing
│   ├── registration.py  # Registration
│   ├── analysis.py      # Analysis
│   └── clustering.py    # Clustering
├── visualization/       # Visualization
│   ├── heatmap.py
│   └── viewer.py
├── utils/               # Utilities
│   ├── logging.py
│   └── validation.py
└── output/              # Output formatting
    ├── models.py
    └── formatters.py
```

## Use Cases

### 1. Construction Monitoring

Compare scans from different dates to detect changes:

```bash
pcd-hyperaxes scan_before.ply scan_after.ply \
  --voxel-size 0.05 \
  --region-threshold 0.5 \
  --format json -o construction_changes.json
```

### 2. Quality Control

Detect defects by comparing manufactured parts to CAD models:

```bash
pcd-hyperaxes manufactured.ply cad_model.ply \
  --distance-threshold 0.01 \
  --mode summary \
  -o quality_report.txt
```

### 3. Batch Processing

Process multiple point cloud pairs:

```bash
for i in {1..10}; do
  pcd-hyperaxes source_$i.ply target_$i.ply \
    --mode centroid \
    --no-plot \
    -o results_$i.json
done
```

## Requirements

- Python ≥ 3.9
- numpy ≥ 1.21.0
- scipy ≥ 1.7.0
- matplotlib ≥ 3.5.0
- open3d ≥ 0.17.0
- laspy ≥ 2.3.0
- textual ≥ 0.47.0 (for TUI)

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check pcd_hyperaxes_core

# Run type checking
mypy pcd_hyperaxes_core
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please contact:
- **Email:** nicola.sabino@hyperaxes.com
- **Company:** Hyperaxes

## Citation

If you use this software in your research, please cite:

```bibtex
@software{pcd_hyperaxes_core,
  title = {pcd_hyperaxes_core: Point Cloud Analysis Module},
  author = {Sabino, Nicola},
  year = {2025},
  organization = {Hyperaxes},
  version = {1.0.0}
}
```

## Acknowledgments

Built with:
- [Open3D](http://www.open3d.org/) - 3D data processing
- [NumPy](https://numpy.org/) - Numerical computing
- [SciPy](https://scipy.org/) - Scientific computing
