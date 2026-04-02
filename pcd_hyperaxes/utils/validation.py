"""
Input validation utilities.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_file_exists(file_path: Path, file_type: str = "file") -> None:
    """
    Validate that a file exists.

    Args:
        file_path: Path to validate
        file_type: Description of file type for error messages

    Raises:
        ValidationError: If file does not exist
    """
    if not file_path.exists():
        raise ValidationError(f"{file_type} not found: {file_path}")

    if not file_path.is_file():
        raise ValidationError(f"{file_type} is not a file: {file_path}")


def validate_file_format(file_path: Path, allowed_formats: set) -> None:
    """
    Validate file format.

    Args:
        file_path: Path to validate
        allowed_formats: Set of allowed file extensions (e.g., {'.ply', '.las'})

    Raises:
        ValidationError: If file format is not allowed
    """
    suffix = file_path.suffix.lower()
    if suffix not in allowed_formats:
        raise ValidationError(
            f"Unsupported file format: {suffix}. " f"Allowed formats: {allowed_formats}"
        )


def validate_positive_number(value: float, name: str) -> None:
    """
    Validate that a number is positive.

    Args:
        value: Value to validate
        name: Parameter name for error messages

    Raises:
        ValidationError: If value is not positive
    """
    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")


def validate_range(
    value: float,
    name: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> None:
    """
    Validate that a value is within a range.

    Args:
        value: Value to validate
        name: Parameter name for error messages
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Raises:
        ValidationError: If value is out of range
    """
    if min_val is not None and value < min_val:
        raise ValidationError(f"{name} must be >= {min_val}, got {value}")

    if max_val is not None and value > max_val:
        raise ValidationError(f"{name} must be <= {max_val}, got {value}")
