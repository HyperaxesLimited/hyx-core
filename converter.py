"""
Module to convert XYZ point cloud files to PLY format
"""
import numpy as np


def xyz_to_ply(xyz_file, ply_file):
    """
    Convert XYZ file to PLY format

    Args:
        xyz_file: Path to input XYZ file
        ply_file: Path to output PLY file
    """
    print(f"Converting {xyz_file} to {ply_file}...")

    # Read XYZ file
    points = np.loadtxt(xyz_file)

    # Extract coordinates (first 3 columns)
    coords = points[:, :3]
    num_points = len(coords)

    print(f"Read {num_points} points from XYZ file")

    # Write PLY file
    with open(ply_file, 'w') as f:
        # Write header
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {num_points}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("end_header\n")

        # Write point data
        for point in coords:
            f.write(f"{point[0]} {point[1]} {point[2]}\n")

    print(f"Successfully converted to {ply_file}")


if __name__ == "__main__":
    # Test conversion
    xyz_to_ply("MBES_Taranto_260225.xyz", "MBES_Taranto_260225.ply")
