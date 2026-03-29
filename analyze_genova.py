#!/usr/bin/env python3
"""
Analisi statistiche dei file point cloud di Genova.
Calcola superficie scansionata, overlap e differenze tra 03-02 e 03-12.
"""

import numpy as np
import json
from pathlib import Path
from pcd_hyperaxes_core import (
    preprocess_point_cloud,
    compute_cloud_distances,
    detect_missing_regions,
    PreprocessingConfig,
    AnalysisConfig
)

def load_xyz_points(filepath):
    """Carica punti da file XYZ."""
    print(f"Caricamento {filepath}...")
    points = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 3:
                    try:
                        x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                        points.append([x, y, z])
                    except ValueError:
                        continue
    return np.array(points)

def calculate_surface_area(points):
    """
    Calcola l'area della superficie scansionata in metri quadri.
    Usa l'estensione XY come proxy per la superficie.
    """
    if len(points) == 0:
        return 0.0

    x_coords = points[:, 0]
    y_coords = points[:, 1]

    x_min, x_max = np.min(x_coords), np.max(x_coords)
    y_min, y_max = np.min(y_coords), np.max(y_coords)

    area = (x_max - x_min) * (y_max - y_min)

    bounds = {
        'x_min': float(x_min),
        'x_max': float(x_max),
        'y_min': float(y_min),
        'y_max': float(y_max),
        'width': float(x_max - x_min),
        'height': float(y_max - y_min)
    }

    return area, bounds

def calculate_overlap(points1, points2, resolution=0.25):
    """
    Calcola l'area di sovrapposizione tra due point cloud.
    resolution: risoluzione della griglia in metri (default: 0.25m come nel nome del file)
    """
    # Trova i bounds di ciascun dataset
    x1_min, x1_max = np.min(points1[:, 0]), np.max(points1[:, 0])
    y1_min, y1_max = np.min(points1[:, 1]), np.max(points1[:, 1])

    x2_min, x2_max = np.min(points2[:, 0]), np.max(points2[:, 0])
    y2_min, y2_max = np.min(points2[:, 1]), np.max(points2[:, 1])

    # Calcola l'intersezione
    overlap_x_min = max(x1_min, x2_min)
    overlap_x_max = min(x1_max, x2_max)
    overlap_y_min = max(y1_min, y2_min)
    overlap_y_max = min(y1_max, y2_max)

    # Se non c'è sovrapposizione
    if overlap_x_min >= overlap_x_max or overlap_y_min >= overlap_y_max:
        return 0.0, None, None, None

    # Calcola l'area di sovrapposizione
    overlap_area = (overlap_x_max - overlap_x_min) * (overlap_y_max - overlap_y_min)

    # Filtra i punti che sono nell'area di sovrapposizione
    mask1 = (
        (points1[:, 0] >= overlap_x_min) & (points1[:, 0] <= overlap_x_max) &
        (points1[:, 1] >= overlap_y_min) & (points1[:, 1] <= overlap_y_max)
    )
    mask2 = (
        (points2[:, 0] >= overlap_x_min) & (points2[:, 0] <= overlap_x_max) &
        (points2[:, 1] >= overlap_y_min) & (points2[:, 1] <= overlap_y_max)
    )

    overlap_points1 = points1[mask1]
    overlap_points2 = points2[mask2]

    overlap_bounds = {
        'x_min': float(overlap_x_min),
        'x_max': float(overlap_x_max),
        'y_min': float(overlap_y_min),
        'y_max': float(overlap_y_max),
        'width': float(overlap_x_max - overlap_x_min),
        'height': float(overlap_y_max - overlap_y_min),
        'points_file1': len(overlap_points1),
        'points_file2': len(overlap_points2)
    }

    return overlap_area, overlap_bounds, overlap_points1, overlap_points2

def analyze_differences(points1, points2, voxel_size=0.5):
    """
    Analizza le differenze tra le due point cloud nell'area di sovrapposizione.
    Le point cloud sono già allineate, quindi non serve registrazione.
    """
    print("\nAnalisi differenze usando pcd-hyperaxes...")

    # Crea point cloud Open3D direttamente dai punti numpy
    import open3d as o3d
    pcd1 = o3d.geometry.PointCloud()
    pcd1.points = o3d.utility.Vector3dVector(points1)
    pcd2 = o3d.geometry.PointCloud()
    pcd2.points = o3d.utility.Vector3dVector(points2)

    # Preprocessing
    print("Preprocessing delle point cloud...")
    prep_config = PreprocessingConfig(voxel_size=voxel_size)
    pcd1_prep = preprocess_point_cloud(pcd1, prep_config)
    pcd2_prep = preprocess_point_cloud(pcd2, prep_config)

    print(f"Punti dopo preprocessing: {len(pcd1_prep.points)} e {len(pcd2_prep.points)}")

    # Calcola distanze (senza registrazione, i file sono già allineati)
    print("Calcolo delle distanze...")
    distances = compute_cloud_distances(pcd1_prep, pcd2_prep)

    # Statistiche sulle distanze
    distance_stats = {
        'min': float(np.min(distances)),
        'max': float(np.max(distances)),
        'mean': float(np.mean(distances)),
        'median': float(np.median(distances)),
        'std': float(np.std(distances))
    }

    # Rileva regioni di differenza
    print("Rilevamento regioni di differenza...")
    analysis_config = AnalysisConfig()
    regions, indices, labels = detect_missing_regions(
        pcd1_prep,
        pcd2_prep,
        distances,
        config=analysis_config
    )

    print(f"Trovate {len(regions)} regioni di differenza")

    # Converti regioni in formato con statistiche
    points1_array = np.asarray(pcd1_prep.points)
    region_stats = []
    for i, region_indices in enumerate(regions, 1):
        region_points = points1_array[region_indices]
        centroid = np.mean(region_points, axis=0)
        region_stats.append({
            'cluster_id': i,
            'num_points': len(region_indices),
            'centroid': centroid.tolist()
        })

    return distance_stats, region_stats

def main():
    # Percorsi dei file tile
    file1 = Path("/Users/nicolasabino/dev/3d-python-hyperaxes/tile_2026-03-02.xyz")
    file2 = Path("/Users/nicolasabino/dev/3d-python-hyperaxes/tile_2026-03-12.xyz")

    print("="*80)
    print("ANALISI STATISTICHE POINT CLOUD GENOVA")
    print("="*80)

    # Carica i punti
    points1 = load_xyz_points(file1)
    points2 = load_xyz_points(file2)

    print(f"\nPunti caricati:")
    print(f"  File 03-02: {len(points1):,} punti")
    print(f"  File 03-12: {len(points2):,} punti")

    # Calcola superfici totali
    print("\n" + "="*80)
    print("SUPERFICI SCANSIONATE")
    print("="*80)

    area1, bounds1 = calculate_surface_area(points1)
    area2, bounds2 = calculate_surface_area(points2)

    print(f"\nFile 03-02:")
    print(f"  Superficie: {area1:,.2f} m²")
    print(f"  Bounds X: [{bounds1['x_min']:.2f}, {bounds1['x_max']:.2f}] (larghezza: {bounds1['width']:.2f} m)")
    print(f"  Bounds Y: [{bounds1['y_min']:.2f}, {bounds1['y_max']:.2f}] (altezza: {bounds1['height']:.2f} m)")

    print(f"\nFile 03-12:")
    print(f"  Superficie: {area2:,.2f} m²")
    print(f"  Bounds X: [{bounds2['x_min']:.2f}, {bounds2['x_max']:.2f}] (larghezza: {bounds2['width']:.2f} m)")
    print(f"  Bounds Y: [{bounds2['y_min']:.2f}, {bounds2['y_max']:.2f}] (altezza: {bounds2['height']:.2f} m)")

    # Calcola sovrapposizione
    print("\n" + "="*80)
    print("SUPERFICIE SOVRAPPONIBILE")
    print("="*80)

    overlap_area, overlap_bounds, overlap_points1, overlap_points2 = calculate_overlap(points1, points2)

    if overlap_area > 0:
        print(f"\nSuperficie di overlap: {overlap_area:,.2f} m²")
        print(f"Percentuale rispetto a 03-02: {(overlap_area/area1)*100:.2f}%")
        print(f"Percentuale rispetto a 03-12: {(overlap_area/area2)*100:.2f}%")
        print(f"\nBounds dell'overlap:")
        print(f"  X: [{overlap_bounds['x_min']:.2f}, {overlap_bounds['x_max']:.2f}] (larghezza: {overlap_bounds['width']:.2f} m)")
        print(f"  Y: [{overlap_bounds['y_min']:.2f}, {overlap_bounds['y_max']:.2f}] (altezza: {overlap_bounds['height']:.2f} m)")
        print(f"\nPunti nell'area di overlap:")
        print(f"  File 03-02: {overlap_bounds['points_file1']:,} punti")
        print(f"  File 03-12: {overlap_bounds['points_file2']:,} punti")

        # Analizza differenze nell'area di overlap
        print("\n" + "="*80)
        print("DIFFERENZE NELL'AREA SOVRAPPONIBILE")
        print("="*80)

        distance_stats, regions = analyze_differences(overlap_points1, overlap_points2, voxel_size=0.25)

        print(f"\nStatistiche distanze (in metri):")
        print(f"  Min: {distance_stats['min']:.4f} m")
        print(f"  Max: {distance_stats['max']:.4f} m")
        print(f"  Media: {distance_stats['mean']:.4f} m")
        print(f"  Mediana: {distance_stats['median']:.4f} m")
        print(f"  Dev. Standard: {distance_stats['std']:.4f} m")

        print(f"\nRegioni di differenza rilevate: {len(regions)}")

        # Calcola area totale delle differenze (approssimata)
        if len(regions) > 0:
            total_diff_points = sum(region['num_points'] for region in regions)
            # Stima dell'area: numero di punti * risoluzione al quadrato
            estimated_diff_area = total_diff_points * (0.25 ** 2)  # 0.25m è la risoluzione del file

            print(f"\nStima area con differenze significative:")
            print(f"  Punti con differenze: {total_diff_points:,}")
            print(f"  Area stimata: {estimated_diff_area:,.2f} m²")
            print(f"  Percentuale dell'overlap: {(estimated_diff_area/overlap_area)*100:.2f}%")

            print(f"\nDettagli regioni:")
            for i, region in enumerate(regions, 1):
                print(f"  Regione {i}: {region['num_points']:,} punti, centroid: {region['centroid']}")

        # Salva risultati
        results = {
            'file1': str(file1.name),
            'file2': str(file2.name),
            'total_area_file1_m2': area1,
            'total_area_file2_m2': area2,
            'bounds_file1': bounds1,
            'bounds_file2': bounds2,
            'overlap_area_m2': overlap_area,
            'overlap_percentage_file1': (overlap_area/area1)*100,
            'overlap_percentage_file2': (overlap_area/area2)*100,
            'overlap_bounds': overlap_bounds,
            'distance_statistics': distance_stats,
            'num_difference_regions': len(regions),
            'difference_regions': regions,
            'estimated_difference_area_m2': estimated_diff_area if len(regions) > 0 else 0,
            'difference_percentage_of_overlap': (estimated_diff_area/overlap_area)*100 if len(regions) > 0 else 0
        }

        output_file = Path("/Users/nicolasabino/dev/3d-python-hyperaxes/genova_analysis_results.json")
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n" + "="*80)
        print(f"Risultati salvati in: {output_file}")
        print("="*80)

    else:
        print("\n⚠️  ATTENZIONE: Non c'è sovrapposizione tra i due file!")

        results = {
            'file1': str(file1.name),
            'file2': str(file2.name),
            'total_area_file1_m2': area1,
            'total_area_file2_m2': area2,
            'bounds_file1': bounds1,
            'bounds_file2': bounds2,
            'overlap_area_m2': 0,
            'message': 'No overlap between the two point clouds'
        }

        output_file = Path("/Users/nicolasabino/dev/3d-python-hyperaxes/genova_analysis_results.json")
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nRisultati salvati in: {output_file}")

if __name__ == "__main__":
    main()
