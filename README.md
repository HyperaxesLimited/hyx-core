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
- ✅ **Flexible Output Formats**: JSON, CSV, or human-readable text
- ✅ **Visualization**: Interactive 3D visualization with Open3D
- ✅ **Command-Line Interface**: Easy-to-use CLI for batch processing
- ✅ **Python API**: Programmatic access for custom workflows

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/hyperaxes/pcd_hyperaxes_core.git
cd pcd_hyperaxes_core

# Install in editable mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Using pip (when published)

```bash
pip install pcd-hyperaxes-core
```

## Quick Start

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
- `--format {json,text,csv}`: Output format (default: json)
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
