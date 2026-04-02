#!/usr/bin/env python3
"""
Build script per pcd-hyperaxes-core wheel.

Questo script:
1. Effettua backup di pyproject.toml
2. Copia pyproject-core.toml → pyproject.toml
3. Esegue build del wheel
4. Ripristina pyproject.toml originale
5. Rinomina MANIFEST-core.in → MANIFEST.in temporaneamente
"""

import shutil
import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).parent

    pyproject_orig = root / "pyproject.toml"
    pyproject_core = root / "pyproject-core.toml"
    pyproject_backup = root / "pyproject.toml.backup"
    manifest_core = root / "MANIFEST-core.in"
    manifest = root / "MANIFEST.in"

    # Verifica esistenza file necessari
    if not pyproject_core.exists():
        print("Error: pyproject-core.toml not found")
        return 1

    # Backup e swap configurazione
    print("Creating backup of pyproject.toml...")
    shutil.copy(pyproject_orig, pyproject_backup)

    print("Switching to core configuration...")
    shutil.copy(pyproject_core, pyproject_orig)

    # Gestione MANIFEST.in
    manifest_backup = None
    if manifest.exists():
        manifest_backup = root / "MANIFEST.in.backup"
        shutil.copy(manifest, manifest_backup)

    if manifest_core.exists():
        shutil.copy(manifest_core, manifest)

    try:
        # Build wheel
        print("Building pcd-hyperaxes-core wheel...")
        result = subprocess.run(
            [sys.executable, "-m", "build", "--wheel"],
            cwd=root,
            check=True
        )
        print("Build successful!")

    finally:
        # Ripristina configurazione originale
        print("Restoring original configuration...")
        shutil.copy(pyproject_backup, pyproject_orig)
        pyproject_backup.unlink()

        if manifest_backup:
            shutil.copy(manifest_backup, manifest)
            manifest_backup.unlink()
        elif manifest.exists() and manifest_core.exists():
            manifest.unlink()

    print(f"Core wheel created in dist/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
