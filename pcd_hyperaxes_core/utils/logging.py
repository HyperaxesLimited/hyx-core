"""
Logging configuration and utilities.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import logging
import sys
from pathlib import Path
from pcd_hyperaxes_core.config import LoggingConfig


def setup_logging(config: LoggingConfig = None) -> None:
    """
    Configure logging for the application.

    Args:
        config: Logging configuration. Uses defaults if None.
    """
    config = config or LoggingConfig()

    # Set log level
    level = getattr(logging, config.log_level.upper())

    # Create formatter
    if config.verbose:
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        fmt = "%(levelname)s - %(message)s"

    formatter = logging.Formatter(fmt)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    handlers = [console_handler]

    # File handler if specified
    if config.log_file:
        log_path = Path(config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(level=level, handlers=handlers, force=True)

    # Set third-party loggers to WARNING to reduce noise
    for logger_name in ["open3d", "matplotlib", "PIL"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
