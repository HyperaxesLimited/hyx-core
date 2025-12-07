"""
Setup script for pcd_hyperaxes_core

This file exists to enable editable installs with older pip versions.
For modern pip versions (>=21.3), setup.py is not needed.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

from setuptools import setup, find_packages

setup(
    packages=find_packages(include=["pcd_hyperaxes_core", "pcd_hyperaxes_core.*"]),
)
