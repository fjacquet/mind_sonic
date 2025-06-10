"""
MindSonic Logging Utilities

This module contains utility functions for configuring and managing logging.
It provides enhanced logging capabilities with different log levels,
formatting options, and file rotation.
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from mind_sonic.config.settings import settings
from typing import Optional, Any, Type


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log messages based on their level.

    This enhances readability in terminal output by color-coding different log levels.
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[1;31m",  # Bold Red
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with color codes based on log level.

        Args:
            record: LogRecord to format

        Returns:
            Formatted log message with appropriate color codes
        """
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )
        return super().format(record)


def setup_logging(
    log_level=logging.INFO, component: Optional[str] = None
) -> logging.Logger:
    """
    Configure the logging system with file and console handlers.

    Args:
        log_level: The logging level to use (default: logging.INFO)
        component: Optional component name to include in the logger name

    Returns:
        Logger: Configured logger instance
    """
    # Use logs directory from settings
    log_dir = settings.LOGS_DIR
    log_dir.mkdir(parents=True, exist_ok=True)  # Ensure it exists (settings.py also does this)

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
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    formatter = logging.Formatter(log_format)

    # Create handlers with rotation
    trace_handler = logging.handlers.RotatingFileHandler(
        trace_log_path, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    trace_handler.setLevel(logging.INFO)
    trace_handler.setFormatter(formatter)

    error_handler = logging.handlers.RotatingFileHandler(
        error_log_path, maxBytes=5 * 1024 * 1024, backupCount=5
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

    # Remove existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()

    # Set log level
    if isinstance(log_level, str):
        level = getattr(logging, log_level.upper(), logging.INFO)
    else:
        level = log_level or logging.INFO
    logger.setLevel(level)

    # Create formatters
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(log_format))
    logger.addHandler(console_handler)

    # File handler with rotation, using settings.LOGS_DIR
    log_file = settings.LOGS_DIR / f"mind_sonic_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

    # Add exception formatting
    def handle_exception(
        exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: Any
    ) -> None:
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception

    return logger


def log_execution_time(logger: logging.Logger):
    """Decorator to log execution time of functions."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                elapsed = (datetime.now() - start_time).total_seconds()
                logger.debug("%s executed in %.2f seconds", func.__qualname__, elapsed)
                return result
            except Exception as e:
                logger.exception("Error in %s: %s", func.__qualname__, str(e))
                raise

        return wrapper

    return decorator


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


def log_crew_execution(
    logger: logging.Logger, crew_name: str, task_name: str, **context
):
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
