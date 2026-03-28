# Quick Start Guide

Get up and running with pcd_hyperaxes_core in 2 minutes.

## Prerequisites

Ensure you have:
- Python 3.9 or higher
- Git

## Step 1: Activate Virtual Environment

```bash
cd /Users/nicolasabino/dev/3d-python-hyperaxes
source .venv/bin/activate
```

On Windows:
```cmd
.venv\Scripts\activate.bat
```

## Step 2: Verify Installation

```bash
pcd-hyperaxes --help
```

You should see the help message with all available options.

## Step 3: Choose Your Interface

### Option A: Interactive TUI (Recommended for Beginners)

Launch the Text User Interface for an interactive experience:

```bash
pcd-hyperaxes-tui
```

**TUI Features:**
- Easy file selection with file browser
- Visual parameter configuration
- Real-time progress tracking
- Results displayed in tables
- Export options

Simply follow the on-screen prompts to:
1. Select your source point cloud file
2. Select your target point cloud file
3. Configure analysis parameters (or use defaults)
4. Run the analysis
5. View and export results

### Option B: LLM Chat Interface (Natural Language)

Talk to HyperAxes in natural language using AI-powered conversation:

```bash
pcd-hyperaxes-chat
```

**Chat Features:**
- 🗣️ Natural language interaction
- 🤖 AI-guided workflow (step-by-step)
- 🎯 Automatic parameter configuration
- 🌐 Web-based 3D visualization with three.js
- 💬 Context-aware conversations

**Prerequisites:**
1. Install and start Ollama:
   ```bash
   # Install from https://ollama.ai
   ollama serve

   # Download model (in another terminal)
   ollama pull llama3.1
   ```

2. Launch chat interface:
   ```bash
   pcd-hyperaxes-chat
   ```

**Example Conversation:**
```
💬 You: I want to compare two point cloud scans

🤖 Assistant: I'd be happy to help! What are the file paths?

💬 You: Source is scan1.ply and target is scan2.ply

🤖 Assistant: Great! Run analysis with defaults?

💬 You: Yes, and show visualization

🤖 Assistant: Running analysis... [opens 3D web viewer]
```

**Chat Commands:**
- `status` - Show current configuration
- `quit` / `exit` / `bye` - End session
- Any natural language request for analysis

**Available Models:**
```bash
# Default - balanced quality and speed
pcd-hyperaxes-chat --model llama3.1

# Faster models (2-3x faster responses, MUST support function calling)
pcd-hyperaxes-chat --model llama3.2:3b   # Recommended for speed
pcd-hyperaxes-chat --model qwen2.5:3b    # Great for technical tasks
pcd-hyperaxes-chat --model mistral       # Fast and capable

# Download model first with: ollama pull llama3.2:3b
```

**Performance Tips:**
- ⚠️ **IMPORTANT**: Only use models that support function calling (tools)
- Smaller models (llama3.2:3b, qwen2.5:3b) = 2-3x faster
- Streaming output shows text as it's generated (no waiting!)
- Progress indicators show each analysis step in real-time

**Models that DON'T work:**
- ❌ phi3, phi3:mini (no function calling support)
- ❌ llama2 (outdated, no tools)
- ❌ codellama (not optimized for conversation)

### Option C: Command Line Interface

For automation and scripting, use the CLI directly.

## Basic CLI Examples

### 1. Simple Comparison with Visualization

```bash
pcd-hyperaxes MBES_Taranto_260225.ply MBES_Taranto_260225_modified.ply
```

This will:
- Load both point clouds
- Register and align them
- Detect differences
- Show 3D visualization

### 2. Save Results to JSON

```bash
pcd-hyperaxes MBES_Taranto_260225.ply MBES_Taranto_260225_modified.ply -o results.json
```

### 3. Fast Mode: Centroids Only (No Visualization)

```bash
pcd-hyperaxes MBES_Taranto_260225.ply MBES_Taranto_260225_modified.ply \
  --mode centroid \
  --no-plot \
  -o centroids.json
```

### 4. Export to CSV

```bash
pcd-hyperaxes MBES_Taranto_260225.ply MBES_Taranto_260225_modified.ply \
  --mode centroid \
  --format csv \
  --no-plot \
  -o results.csv
```

### 5. Export to GeoJSON for GIS Applications

```bash
pcd-hyperaxes MBES_Taranto_260225.ply MBES_Taranto_260225_modified.ply \
  --mode centroid \
  --format geojson \
  --no-plot \
  -o differences.geojson
```

Import the GeoJSON file directly into QGIS, ArcGIS, or web mapping tools.

### 6. Custom Parameters

```bash
pcd-hyperaxes MBES_Taranto_260225.ply MBES_Taranto_260225_modified.ply \
  --voxel-size 0.05 \
  --distance-threshold 0.3 \
  --region-threshold 1.0 \
  --format json \
  -o detailed_analysis.json
```

**Parameter Explanations:**
- `--voxel-size`: Resolution for downsampling (smaller = more detail, slower)
- `--distance-threshold`: Minimum distance to consider as a change
- `--region-threshold`: Distance for grouping changes into regions
- `--format`: Output format (json, csv, text, geojson)

## View Results

### JSON Output

```bash
cat results.json
```

Or with pretty formatting:

```bash
python -m json.tool results.json
```

### CSV Output

```bash
cat results.csv
```

Or open in Excel, LibreOffice, or Google Sheets.

## Supported File Formats

- **Input**: LAS, LAZ, PLY, PCD, XYZ
- **Output**: JSON, CSV, Text, GeoJSON

## Common Workflows

### Construction Monitoring

Compare scans from different dates:

```bash
pcd-hyperaxes scan_before.ply scan_after.ply \
  --voxel-size 0.05 \
  --region-threshold 0.5 \
  -o construction_changes.json
```

### Quality Control

Detect defects by comparing manufactured parts to CAD models:

```bash
pcd-hyperaxes manufactured.ply cad_model.ply \
  --distance-threshold 0.01 \
  --mode summary \
  -o quality_report.txt
```

### Batch Processing

Process multiple point cloud pairs:

```bash
for i in {1..10}; do
  pcd-hyperaxes source_$i.ply target_$i.ply \
    --mode centroid \
    --no-plot \
    -o results_$i.json
done
```

## Need Help?

- View all options: `pcd-hyperaxes --help`
- Check version: `pcd-hyperaxes --version`
- Read full documentation: [README.md](README.md)

## Troubleshooting

**Virtual environment not activated?**
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate.bat  # Windows
```

**Command not found?**
```bash
pip install -e .
```

**Visualization not working?**
```bash
# Use --no-plot flag to skip visualization
pcd-hyperaxes source.ply target.ply --no-plot -o results.json
```

**Chat interface not connecting to Ollama?**
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, check if model is installed
ollama list

# Pull model if needed
ollama pull llama3.1
```

## Next Steps

1. Try the LLM Chat: `pcd-hyperaxes-chat` (requires Ollama)
2. Try the TUI: `pcd-hyperaxes-tui`
3. Experiment with your own point cloud files
4. Read the full [README.md](README.md) for advanced features
5. Explore the Python API for custom workflows

Happy analyzing! 🚀
