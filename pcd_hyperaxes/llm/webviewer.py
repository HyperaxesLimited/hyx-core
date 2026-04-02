"""
Web visualization with three.js for point cloud results.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import json
import logging
import tempfile
import webbrowser
from pathlib import Path
from typing import Tuple
import numpy as np
import open3d as o3d

from pcd_hyperaxes.output.models import AnalysisResults

logger = logging.getLogger(__name__)


def generate_cluster_color(cluster_id: int) -> Tuple[float, float, float]:
    """
    Generate a distinct color for a cluster ID.

    Args:
        cluster_id: Cluster identifier

    Returns:
        RGB color tuple (0-1 range)
    """
    # Use golden ratio for good color distribution
    golden_ratio = 0.618033988749895
    hue = (cluster_id * golden_ratio) % 1.0

    # Convert HSV to RGB (S=0.8, V=0.95 for vivid colors)
    def hsv_to_rgb(h, s, v):
        if s == 0.0:
            return v, v, v
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        if i == 0:
            return v, t, p
        if i == 1:
            return q, v, p
        if i == 2:
            return p, v, t
        if i == 3:
            return p, q, v
        if i == 4:
            return t, p, v
        if i == 5:
            return v, p, q

    return hsv_to_rgb(hue, 0.8, 0.95)


def create_web_visualization(
    results: AnalysisResults,
    source_aligned: o3d.geometry.PointCloud,
    auto_open: bool = True,
) -> Path:
    """
    Create three.js web visualization of analysis results.

    Args:
        results: Analysis results with cluster information
        source_aligned: Aligned source point cloud
        auto_open: Whether to automatically open in browser

    Returns:
        Path to generated HTML file
    """
    logger.info("Creating web visualization...")

    # Extract points
    points = np.asarray(source_aligned.points)
    num_points = len(points)

    # Initialize all points as gray background
    colors = np.full((num_points, 3), 0.7, dtype=np.float32)

    # Color each cluster with distinct color
    cluster_colors_map = {}
    for cluster in results.clusters:
        cluster_color = generate_cluster_color(cluster.cluster_id)
        cluster_colors_map[cluster.cluster_id] = cluster_color

        # Find indices of points in this cluster
        # We need to map back from cluster points to original indices
        if cluster.points:
            for point in cluster.points:
                # Find closest point in source_aligned (should be exact match)
                distances = np.linalg.norm(points - np.array(point), axis=1)
                idx = np.argmin(distances)
                if distances[idx] < 0.001:  # Very close match
                    colors[idx] = cluster_color

    # Prepare JSON data
    data = {
        "points": points.tolist(),
        "colors": colors.tolist(),
        "stats": {
            "num_clusters": results.num_clusters,
            "total_points": num_points,
            "distance_stats": results.distance_stats,
            "change_stats": results.change_stats,
            "source_file": results.source_file,
            "target_file": results.target_file,
        },
        "clusters": [
            {
                "id": cluster.cluster_id,
                "num_points": cluster.num_points,
                "centroid": list(cluster.centroid),
                "color": cluster_colors_map.get(cluster.cluster_id, (1, 0, 0)),
            }
            for cluster in results.clusters
        ],
    }

    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="hyperaxes_viz_"))
    json_path = temp_dir / "data.json"
    html_path = temp_dir / "visualization.html"

    # Save JSON data
    with open(json_path, "w") as f:
        json.dump(data, f)

    # Generate HTML with three.js
    html_content = HTML_TEMPLATE.format(json_file="data.json")

    with open(html_path, "w") as f:
        f.write(html_content)

    logger.info(f"Visualization created at: {html_path}")

    # Open in browser
    if auto_open:
        webbrowser.open(f"file://{html_path}")
        logger.info("Opening visualization in browser...")

    return html_path


# HTML Template with embedded three.js
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HyperAxes Point Cloud Visualization</title>
    <style>
        body {{
            margin: 0;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #1a1a1a;
            color: #fff;
        }}
        #container {{
            width: 100vw;
            height: 100vh;
        }}
        #info {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 8px;
            max-width: 350px;
            backdrop-filter: blur(10px);
        }}
        #info h1 {{
            margin: 0 0 15px 0;
            font-size: 24px;
            font-weight: 600;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        #info h2 {{
            margin: 15px 0 8px 0;
            font-size: 14px;
            font-weight: 600;
            color: #aaa;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 13px;
        }}
        .stat-label {{
            color: #aaa;
        }}
        .stat-value {{
            font-weight: 600;
            color: #fff;
        }}
        .cluster {{
            display: flex;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 12px;
        }}
        .cluster-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            margin-right: 10px;
        }}
        .cluster-info {{
            flex: 1;
        }}
        #controls {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-radius: 8px;
            font-size: 12px;
            backdrop-filter: blur(10px);
        }}
        #controls div {{
            margin: 4px 0;
            color: #aaa;
        }}
        #legend {{
            max-height: 200px;
            overflow-y: auto;
        }}
        #legend::-webkit-scrollbar {{
            width: 6px;
        }}
        #legend::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}
        #legend::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.3);
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div id="container"></div>

    <div id="info">
        <h1>⚡ HyperAxes Analysis</h1>

        <h2>Statistics</h2>
        <div class="stat-row">
            <span class="stat-label">Clusters Found</span>
            <span class="stat-value" id="num-clusters">-</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Total Points</span>
            <span class="stat-value" id="total-points">-</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Mean Distance</span>
            <span class="stat-value" id="mean-distance">-</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Max Distance</span>
            <span class="stat-value" id="max-distance">-</span>
        </div>

        <h2>Clusters</h2>
        <div id="legend"></div>
    </div>

    <div id="controls">
        <div><strong>Controls:</strong></div>
        <div>🖱️ Left Click + Drag: Rotate</div>
        <div>🖱️ Right Click + Drag: Pan</div>
        <div>🎡 Scroll: Zoom</div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r150/three.min.js"></script>
    <script>
        // Load data and create visualization
        fetch('{json_file}')
            .then(response => response.json())
            .then(data => {{
                createVisualization(data);
                updateUI(data);
            }})
            .catch(error => console.error('Error loading data:', error));

        function createVisualization(data) {{
            const container = document.getElementById('container');
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a1a);

            // Camera
            const camera = new THREE.PerspectiveCamera(
                60,
                window.innerWidth / window.innerHeight,
                0.1,
                10000
            );

            // Renderer
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);

            // Point cloud geometry
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(data.points.flat());
            const colors = new Float32Array(data.colors.flat());

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
            geometry.computeBoundingSphere();

            // Material
            const material = new THREE.PointsMaterial({{
                size: 0.05,
                vertexColors: true,
                sizeAttenuation: true
            }});

            // Points
            const points = new THREE.Points(geometry, material);
            scene.add(points);

            // Lighting
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.4);
            directionalLight.position.set(10, 10, 10);
            scene.add(directionalLight);

            // Position camera
            const sphere = geometry.boundingSphere;
            const center = sphere.center;
            const radius = sphere.radius;
            camera.position.set(center.x, center.y, center.z + radius * 3);
            camera.lookAt(center);

            // Basic orbit controls (simplified without external library)
            let isDragging = false;
            let previousMousePosition = {{ x: 0, y: 0 }};
            let rotation = {{ x: 0, y: 0 }};
            let distance = radius * 3;

            renderer.domElement.addEventListener('mousedown', (e) => {{
                isDragging = true;
                previousMousePosition = {{ x: e.clientX, y: e.clientY }};
            }});

            renderer.domElement.addEventListener('mousemove', (e) => {{
                if (!isDragging) return;

                const deltaX = e.clientX - previousMousePosition.x;
                const deltaY = e.clientY - previousMousePosition.y;

                rotation.y += deltaX * 0.005;
                rotation.x += deltaY * 0.005;

                // Limit vertical rotation
                rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, rotation.x));

                previousMousePosition = {{ x: e.clientX, y: e.clientY }};
            }});

            renderer.domElement.addEventListener('mouseup', () => {{
                isDragging = false;
            }});

            renderer.domElement.addEventListener('wheel', (e) => {{
                e.preventDefault();
                distance += e.deltaY * 0.01;
                distance = Math.max(radius * 0.5, Math.min(radius * 10, distance));
            }});

            // Animation loop
            function animate() {{
                requestAnimationFrame(animate);

                // Update camera position based on rotation
                camera.position.x = center.x + distance * Math.sin(rotation.y) * Math.cos(rotation.x);
                camera.position.y = center.y + distance * Math.sin(rotation.x);
                camera.position.z = center.z + distance * Math.cos(rotation.y) * Math.cos(rotation.x);
                camera.lookAt(center);

                renderer.render(scene, camera);
            }}

            animate();

            // Handle window resize
            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});
        }}

        function updateUI(data) {{
            // Update statistics
            document.getElementById('num-clusters').textContent = data.stats.num_clusters;
            document.getElementById('total-points').textContent = data.stats.total_points.toLocaleString();
            document.getElementById('mean-distance').textContent = data.stats.distance_stats.mean.toFixed(3) + 'm';
            document.getElementById('max-distance').textContent = data.stats.distance_stats.max.toFixed(3) + 'm';

            // Update legend
            const legend = document.getElementById('legend');
            data.clusters.forEach(cluster => {{
                const div = document.createElement('div');
                div.className = 'cluster';

                const colorBox = document.createElement('div');
                colorBox.className = 'cluster-color';
                const rgb = cluster.color.map(c => Math.round(c * 255));
                colorBox.style.backgroundColor = `rgb(${{rgb[0]}}, ${{rgb[1]}}, ${{rgb[2]}})`;

                const info = document.createElement('div');
                info.className = 'cluster-info';
                info.textContent = `Cluster ${{cluster.id}}: ${{cluster.num_points}} points`;

                div.appendChild(colorBox);
                div.appendChild(info);
                legend.appendChild(div);
            }});
        }}
    </script>
</body>
</html>
"""
