"""
Function definitions for Ollama function calling.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

# Function tools that Ollama can call to interact with HyperAxes Core
HYPERAXES_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "set_source_file",
            "description": "Set the source point cloud file path for analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the source point cloud file (LAS/LAZ/PLY/PCD/XYZ format)",
                    }
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_target_file",
            "description": "Set the target point cloud file path for comparison",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the target point cloud file (LAS/LAZ/PLY/PCD/XYZ format)",
                    }
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "configure_preprocessing",
            "description": "Configure point cloud preprocessing parameters like voxel size and outlier removal",
            "parameters": {
                "type": "object",
                "properties": {
                    "voxel_size": {
                        "type": "number",
                        "description": "Voxel size for downsampling in meters (default: 0.1). Smaller values preserve more detail but are slower.",
                    },
                    "remove_outliers": {
                        "type": "boolean",
                        "description": "Whether to remove outlier points (default: true)",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "configure_analysis",
            "description": "Configure analysis parameters for change detection and region clustering",
            "parameters": {
                "type": "object",
                "properties": {
                    "distance_threshold": {
                        "type": "number",
                        "description": "Distance threshold in meters for detecting changes (default: 0.2)",
                    },
                    "region_threshold": {
                        "type": "number",
                        "description": "Distance threshold in meters for grouping points into regions (default: 0.9)",
                    },
                    "region_size": {
                        "type": "integer",
                        "description": "Minimum number of points required to form a region (default: 10)",
                    },
                    "enable_noise_filtering": {
                        "type": "boolean",
                        "description": "Enable noise filtering to reduce false positives (default: true)",
                    },
                    "noise_sigma": {
                        "type": "number",
                        "description": "Statistical noise tolerance in sigma units (default: 2.0)",
                    },
                    "min_local_support": {
                        "type": "integer",
                        "description": "Minimum neighbors for local validation (default: 3)",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "configure_output",
            "description": "Configure output format and detail level for analysis results",
            "parameters": {
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["json", "csv", "geojson", "text"],
                        "description": "Output format (default: json)",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["full", "centroid", "summary"],
                        "description": "Output detail level - full: all points, centroid: only cluster centroids, summary: statistics only (default: full)",
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Optional path to save results to file",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_analysis",
            "description": "Execute the complete point cloud analysis pipeline including loading, preprocessing, registration, distance computation, and change detection",
            "parameters": {
                "type": "object",
                "properties": {
                    "show_visualization": {
                        "type": "boolean",
                        "description": "Whether to open a web browser with 3D visualization of results (default: false)",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_state",
            "description": "Get a summary of the current analysis configuration including files, parameters, and status",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_results_summary",
            "description": "Get a summary of the last analysis results including number of clusters, distance statistics, and change statistics",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_results",
            "description": "Save the last analysis results to a file in the specified format",
            "parameters": {
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": "Path where to save the results file",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "csv", "geojson", "text"],
                        "description": "Output format (optional, uses configured format if not specified)",
                    },
                },
                "required": ["output_path"],
            },
        },
    },
]
