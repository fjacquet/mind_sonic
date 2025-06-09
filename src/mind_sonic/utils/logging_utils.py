#!/usr/bin/env python
"""
MindSonic Logging Utilities

This module contains utility functions for configuring and managing logging.
It provides enhanced logging capabilities with different log levels,
formatting options, and file rotation.
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


def setup_logging(log_level=logging.INFO, component: Optional[str] = None) -> logging.Logger:
    """
    Configure the logging system with file and console handlers.
    
    Args:
        log_level: The logging level to use (default: logging.INFO)
        component: Optional component name to include in the logger name
        
    Returns:
        Logger: Configured logger instance
    """
    # Create logs directory
    log_dir = Path(__file__).resolve().parents[3] / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Create component subdirectory if specified
    if component:
        component_dir = log_dir / component
        component_dir.mkdir(exist_ok=True)
        trace_log_path = component_dir / "trace.log"
        error_log_path = component_dir / "errors.log"
    else:
        trace_log_path = log_dir / "trace.log"
        error_log_path = log_dir / "errors.log"

    # Define detailed log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    formatter = logging.Formatter(log_format)

    # Create handlers with rotation
    trace_handler = logging.handlers.RotatingFileHandler(
        trace_log_path, maxBytes=10*1024*1024, backupCount=5
    )
    trace_handler.setLevel(logging.INFO)
    trace_handler.setFormatter(formatter)

    error_handler = logging.handlers.RotatingFileHandler(
        error_log_path, maxBytes=5*1024*1024, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Console handler with color formatting
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    # Get logger
    logger_name = f"mind_sonic.{component}" if component else "mind_sonic"
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Remove existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Add handlers
    logger.addHandler(trace_handler)
    logger.addHandler(error_handler)
    logger.addHandler(stream_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(component: Optional[str] = None) -> logging.Logger:
    """
    Get a logger for a specific component.
    
    Args:
        component: Component name (e.g., 'research_crew', 'indexer_crew')
        
    Returns:
        Logger: Logger instance for the component
    """
    logger_name = f"mind_sonic.{component}" if component else "mind_sonic"
    logger = logging.getLogger(logger_name)
    
    # If logger doesn't have handlers, set it up
    if not logger.hasHandlers():
        return setup_logging(component=component)
    
    return logger


def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls with parameters and return values.
    
    Args:
        logger: Logger instance to use for logging
        
    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func_name} returned: {result}")
                return result
            except Exception as e:
                logger.error(f"Exception in {func_name}: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator


def log_crew_execution(logger: logging.Logger, crew_name: str, task_name: str, **context):
    """
    Log crew execution details.
    
    Args:
        logger: Logger instance
        crew_name: Name of the crew
        task_name: Name of the task
        context: Additional context to log
    """
    logger.info(f"Executing {crew_name} - {task_name}")
    if context:
        logger.debug(f"Context: {context}")

