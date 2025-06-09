#!/usr/bin/env python
"""
MindSonic Logging Utilities

This module contains utility functions for configuring and managing logging.
"""
import logging
from pathlib import Path


def setup_logging(log_level=logging.INFO):
    """
    Configure the logging system with file and console handlers.
    
    Args:
        log_level: The logging level to use (default: logging.INFO)
        
    Returns:
        None
    """
    # Create logs directory
    log_dir = Path(__file__).resolve().parents[3] / "logs"
    log_dir.mkdir(exist_ok=True)

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Create handlers
    trace_handler = logging.FileHandler(log_dir / "trace.log")
    trace_handler.setLevel(logging.INFO)

    error_handler = logging.FileHandler(log_dir / "errors.log")
    error_handler.setLevel(logging.ERROR)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[trace_handler, error_handler, stream_handler],
    )
    
    return logging.getLogger(__name__)
