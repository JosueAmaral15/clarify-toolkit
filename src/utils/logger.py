#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clarify Logging System

Provides structured logging with:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File rotation (max size 10MB, keep 5 backups)
- Console and file output
- Formatted timestamps and contextual information
- Thread-safe operations

Usage:
    from src.utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Application started")
    logger.debug("Debug information", extra={"user": "admin"})
    logger.error("Error occurred", exc_info=True)

Configuration:
    Set environment variable CLARIFY_LOG_LEVEL to override default level:
    - DEBUG: Detailed information for debugging
    - INFO: General informational messages (default)
    - WARNING: Warning messages
    - ERROR: Error messages
    - CRITICAL: Critical errors
"""

import logging
import logging.handlers
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional


# Default configuration
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
)
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_DIR = Path.home() / ".clarify" / "logs"
DEFAULT_LOG_FILE = "clarify.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 backup files


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        """Format log record with colors for console."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )

        # Format the message
        result = super().format(record)

        # Reset levelname (in case record is reused)
        record.levelname = levelname

        return result


class ClarifyLogger:
    """
    Singleton logger manager for Clarify application.

    Manages centralized logging configuration and provides logger instances.
    """

    _instance: Optional['ClarifyLogger'] = None
    _initialized: bool = False

    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize logger manager (only once)."""
        if not self._initialized:
            self._setup_logging()
            ClarifyLogger._initialized = True

    def _setup_logging(self):
        """Configure root logger with file and console handlers."""
        # Get log level from environment or use default
        log_level_name = os.getenv("CLARIFY_LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_name, DEFAULT_LOG_LEVEL)

        # Get root logger
        root_logger = logging.getLogger("clarify")
        root_logger.setLevel(log_level)

        # Remove existing handlers (avoid duplicates)
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = ColoredFormatter(
            fmt=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        requested_log_dir = os.getenv("CLARIFY_LOG_DIR")
        primary_log_dir = Path(requested_log_dir).expanduser() if requested_log_dir else DEFAULT_LOG_DIR
        fallback_log_dir = (
            Path(tempfile.gettempdir())
            / f"clarify-{getattr(os, 'getuid', lambda: 'user')()}"
            / "logs"
        )
        log_dir = primary_log_dir
        log_file = primary_log_dir / DEFAULT_LOG_FILE
        file_error = None

        for candidate in dict.fromkeys((primary_log_dir, fallback_log_dir)):
            try:
                candidate.mkdir(parents=True, exist_ok=True, mode=0o700)
                candidate_file = candidate / DEFAULT_LOG_FILE
                file_handler = logging.handlers.RotatingFileHandler(
                    filename=candidate_file,
                    maxBytes=MAX_LOG_SIZE,
                    backupCount=BACKUP_COUNT,
                    encoding='utf-8'
                )
                file_handler.setLevel(log_level)
                file_handler.setFormatter(logging.Formatter(
                    fmt=DEFAULT_LOG_FORMAT,
                    datefmt=DEFAULT_DATE_FORMAT
                ))
                root_logger.addHandler(file_handler)
                log_dir = candidate
                log_file = candidate_file
                break
            except OSError as exc:
                file_error = exc
        else:
            log_dir = primary_log_dir
            log_file = primary_log_dir / DEFAULT_LOG_FILE

        if file_error and log_dir != primary_log_dir:
            root_logger.warning(
                "Primary log directory unavailable (%s); using fallback: %s",
                file_error,
                log_dir,
            )
        elif file_error and not any(
            isinstance(handler, logging.handlers.RotatingFileHandler)
            for handler in root_logger.handlers
        ):
            root_logger.warning(
                "File logging unavailable (%s); continuing with console logging only",
                file_error,
            )

        # Log initialization
        root_logger.info(
            "Logging system initialized | Level: %s | Log file: %s",
            log_level_name, log_file
        )

        # Store configuration
        self.log_level = log_level
        self.log_dir = log_dir
        self.log_file = log_file

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module.

        Args:
            name: Logger name (typically __name__ of the module)

        Returns:
            Logger instance configured with Clarify settings

        Example:
            >>> logger = get_logger(__name__)
            >>> logger.info("Module initialized")
        """
        # Ensure name starts with "clarify."
        if not name.startswith("clarify"):
            name = f"clarify.{name}"

        return logging.getLogger(name)

    def set_level(self, level: str):
        """
        Change log level at runtime.

        Args:
            level: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Example:
            >>> logger_manager = ClarifyLogger()
            >>> logger_manager.set_level("DEBUG")
        """
        level_value = getattr(logging, level.upper(), DEFAULT_LOG_LEVEL)
        root_logger = logging.getLogger("clarify")
        root_logger.setLevel(level_value)

        # Update all handlers
        for handler in root_logger.handlers:
            handler.setLevel(level_value)

        root_logger.info("Log level changed to %s", level.upper())
        self.log_level = level_value  # pylint: disable=attribute-defined-outside-init  # Dynamic config update

    def get_log_file_path(self) -> Path:
        """
        Get current log file path.

        Returns:
            Path object pointing to current log file
        """
        return self.log_file

    def clear_logs(self):
        """
        Clear all log files (current and backups).

        Warning: This permanently deletes log files!
        """
        root_logger = logging.getLogger("clarify")
        root_logger.warning("Clearing all log files...")

        # Clear all log files
        for log_file in self.log_dir.glob("clarify.log*"):
            try:
                log_file.unlink()
                root_logger.info("Deleted: %s", log_file.name)
            except Exception as e:  # pylint: disable=broad-exception-caught  # File deletion robustness
                root_logger.error("Failed to delete %s: %s", log_file.name, e)

        # Reinitialize logging
        self._setup_logging()


# Module-level convenience functions

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    This is the primary function to use for getting loggers in modules.

    Args:
        name: Logger name (use __name__ for module logger)

    Returns:
        Configured logger instance

    Example:
        >>> from src.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Module loaded successfully")
        >>> logger.debug("Debug info", extra={"key": "value"})
        >>> logger.error("Error occurred", exc_info=True)
    """
    manager = ClarifyLogger()
    return manager.get_logger(name)


def set_log_level(level: str):
    """
    Change global log level.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> from src.utils.logger import set_log_level
        >>> set_log_level("DEBUG")  # Enable debug logging
    """
    manager = ClarifyLogger()
    manager.set_level(level)


def get_log_file() -> Path:
    """
    Get path to current log file.

    Returns:
        Path to log file

    Example:
        >>> from src.utils.logger import get_log_file
        >>> print(f"Logs are at: {get_log_file()}")
    """
    manager = ClarifyLogger()
    return manager.get_log_file_path()


def clear_all_logs():
    """
    Clear all log files (use with caution!).

    Example:
        >>> from src.utils.logger import clear_all_logs
        >>> clear_all_logs()  # Permanently deletes all logs
    """
    manager = ClarifyLogger()
    manager.clear_logs()


# Initialize logging on module import
_logger_manager = ClarifyLogger()


if __name__ == "__main__":
    # Demo/test code
    print("=" * 70)
    print("Clarify Logging System Demo")
    print("=" * 70)

    # Get logger
    logger = get_logger(__name__)

    # Test all log levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")

    # Test with extra context
    logger.info("User logged in", extra={"username": "admin", "ip": "192.168.1.1"})

    # Test exception logging
    try:
        1 / 0
    except Exception:  # pylint: disable=broad-exception-caught  # Demo error handling
        logger.error("Division by zero error", exc_info=True)

    # Show log file location
    print(f"\nLog file: {get_log_file()}")
    print(f"Log level: {logging.getLevelName(_logger_manager.log_level)}")
    print("=" * 70)
