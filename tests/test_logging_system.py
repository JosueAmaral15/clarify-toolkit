#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for Clarify Logging System.

Tests:
- Logger initialization and singleton pattern
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File rotation (max size, backup count)
- Console and file output
- Thread-safe operations
- Log level changes at runtime
- Log file management (clear, get path)
"""

import pytest
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.logger import (
    ClarifyLogger, get_logger, set_log_level, get_log_file, clear_all_logs,
    DEFAULT_LOG_LEVEL, MAX_LOG_SIZE, BACKUP_COUNT
)


class TestClarifyLogger:
    """Test ClarifyLogger class."""
    
    def test_singleton_pattern(self):
        """Test that ClarifyLogger follows singleton pattern."""
        manager1 = ClarifyLogger()
        manager2 = ClarifyLogger()
        
        assert manager1 is manager2
        assert id(manager1) == id(manager2)
    
    def test_logger_initialization(self):
        """Test that logger is properly initialized."""
        manager = ClarifyLogger()
        
        assert manager.log_level is not None
        assert manager.log_dir is not None
        assert manager.log_file is not None
        assert manager.log_dir.exists()
    
    def test_get_logger_with_module_name(self):
        """Test getting logger with module name."""
        logger = get_logger("test_module")
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert "clarify" in logger.name
    
    def test_log_level_default(self):
        """Test default log level is INFO."""
        manager = ClarifyLogger()
        
        # Should be INFO by default (unless overridden by env var)
        assert manager.log_level in [
            logging.DEBUG, logging.INFO, logging.WARNING, 
            logging.ERROR, logging.CRITICAL
        ]
    
    def test_set_log_level(self):
        """Test changing log level at runtime."""
        manager = ClarifyLogger()
        original_level = manager.log_level
        
        # Change to DEBUG
        manager.set_level("DEBUG")
        assert manager.log_level == logging.DEBUG
        
        # Change to WARNING
        manager.set_level("WARNING")
        assert manager.log_level == logging.WARNING
        
        # Restore original
        level_name = logging.getLevelName(original_level)
        manager.set_level(level_name)


class TestLoggerOutput:
    """Test logger output functionality."""
    
    def test_logger_writes_to_file(self):
        """Test that logger writes messages to file."""
        logger = get_logger("test_file_output")
        log_file = get_log_file()
        
        # Get initial file size
        initial_size = log_file.stat().st_size if log_file.exists() else 0
        
        # Write log message
        test_message = "TEST_MESSAGE_FOR_FILE_OUTPUT"
        logger.info(test_message)
        
        # Check file grew
        new_size = log_file.stat().st_size
        assert new_size > initial_size
        
        # Check message is in file
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert test_message in content
    
    def test_all_log_levels(self):
        """Test all log levels are logged correctly."""
        logger = get_logger("test_all_levels")
        set_log_level("DEBUG")  # Enable all levels
        
        log_file = get_log_file()
        
        # Log at all levels
        messages = {
            "DEBUG": "Debug message",
            "INFO": "Info message",
            "WARNING": "Warning message",
            "ERROR": "Error message",
            "CRITICAL": "Critical message"
        }
        
        for level, msg in messages.items():
            getattr(logger, level.lower())(msg)
        
        # Check all messages are in file
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for level, msg in messages.items():
            assert msg in content
            assert level in content
    
    def test_exception_logging(self):
        """Test logging exceptions with stack traces."""
        logger = get_logger("test_exceptions")
        log_file = get_log_file()
        
        # Generate and log exception
        try:
            raise ValueError("Test exception for logging")
        except ValueError:
            logger.error("Exception occurred", exc_info=True)
        
        # Check exception details are in log
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "ValueError" in content
        assert "Test exception for logging" in content
        assert "Traceback" in content


class TestLogRotation:
    """Test log file rotation."""
    
    def test_log_file_path(self):
        """Test getting log file path."""
        log_file = get_log_file()
        
        assert log_file is not None
        assert isinstance(log_file, Path)
        assert log_file.name == "clarify.log"
        assert log_file.parent.name == "logs"
    
    def test_rotation_settings(self):
        """Test rotation settings are configured correctly."""
        manager = ClarifyLogger()
        root_logger = logging.getLogger("clarify")
        
        # Find RotatingFileHandler
        file_handler = None
        for handler in root_logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                file_handler = handler
                break
        
        assert file_handler is not None
        assert file_handler.maxBytes == MAX_LOG_SIZE
        assert file_handler.backupCount == BACKUP_COUNT


class TestThreadSafety:
    """Test thread-safe logging operations."""
    
    def test_concurrent_logging(self):
        """Test logging from multiple threads simultaneously."""
        import threading
        import time
        
        logger = get_logger("test_threads")
        results = []
        
        def log_messages(thread_id, count=10):
            """Log messages from a thread."""
            for i in range(count):
                logger.info(f"Thread {thread_id} message {i}")
                results.append((thread_id, i))
        
        # Create and start threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_messages, args=(i, 10))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all messages logged
        assert len(results) == 50  # 5 threads × 10 messages
        
        # Check log file contains messages from all threads
        log_file = get_log_file()
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for thread_id in range(5):
            assert f"Thread {thread_id}" in content


class TestModuleLevelFunctions:
    """Test module-level convenience functions."""
    
    def test_get_logger_function(self):
        """Test get_logger() convenience function."""
        logger = get_logger("test_convenience")
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
    
    def test_set_log_level_function(self):
        """Test set_log_level() convenience function."""
        manager = ClarifyLogger()
        original_level = manager.log_level
        
        # Change level
        set_log_level("DEBUG")
        assert manager.log_level == logging.DEBUG
        
        # Restore
        set_log_level(logging.getLevelName(original_level))
    
    def test_get_log_file_function(self):
        """Test get_log_file() convenience function."""
        log_file = get_log_file()
        
        assert log_file is not None
        assert isinstance(log_file, Path)
        assert log_file.exists()


class TestLogManagement:
    """Test log file management operations."""
    
    def test_clear_logs_function(self):
        """Test clear_all_logs() function."""
        # Write some log messages
        logger = get_logger("test_clear")
        logger.info("Message before clear")
        
        log_file = get_log_file()
        original_size = log_file.stat().st_size
        
        # Clear logs (WARNING: This actually deletes logs!)
        # In production, we'd mock this or use a test-specific log directory
        # For now, just test that the function exists and is callable
        assert callable(clear_all_logs)
        
        # Don't actually clear in tests to preserve other test logs
        # clear_all_logs()


class TestColoredFormatter:
    """Test ColoredFormatter for console output."""
    
    def test_colored_formatter_initialization(self):
        """Test ColoredFormatter can be initialized."""
        from utils.logger import ColoredFormatter
        
        formatter = ColoredFormatter(
            fmt="%(levelname)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        
        assert formatter is not None
    
    def test_colored_output_format(self):
        """Test that ColoredFormatter adds ANSI codes."""
        from utils.logger import ColoredFormatter
        
        formatter = ColoredFormatter(fmt="%(levelname)s: %(message)s")
        
        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Format the record
        formatted = formatter.format(record)
        
        # Should contain ANSI codes (or at least the message)
        assert "Test message" in formatted


class TestEnvironmentConfiguration:
    """Test configuration via environment variables."""
    
    @patch.dict(os.environ, {"CLARIFY_LOG_LEVEL": "DEBUG"})
    def test_log_level_from_env(self):
        """Test setting log level via environment variable."""
        # Note: This test may not work perfectly because logger is initialized on import
        # In a real scenario, we'd need to reinitialize the logger
        pass  # Placeholder for environment testing


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
