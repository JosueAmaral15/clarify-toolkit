#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for Error Handler & Crash Reporter
-----------------------------------------
Comprehensive test suite for src/utils/error_handler.py

Sprint: v2.9.61 - Error Reporting & Crash Handler
Author: Josué Amaral
Date: 2025-12-10
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the module to test
from src.utils.error_handler import (
    CrashHandler,
    install_crash_handler,
    uninstall_crash_handler
)


class TestCrashHandlerInit(unittest.TestCase):
    """Test CrashHandler initialization."""
    
    def setUp(self):
        """Reset singleton before each test."""
        CrashHandler.reset_instance()
    
    def test_init_default_params(self):
        """Test initialization with default parameters."""
        handler = CrashHandler()
        self.assertFalse(handler.enabled)
        self.assertTrue(handler.show_dialog)
        self.assertFalse(handler.report_crashes)
        self.assertIsNone(handler.callback)
        self.assertEqual(handler._crash_count, 0)
        self.assertIsNone(handler._last_crash_time)
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        callback = Mock()
        handler = CrashHandler(
            show_dialog=False,
            report_crashes=True,
            callback=callback
        )
        self.assertFalse(handler.show_dialog)
        self.assertTrue(handler.report_crashes)
        self.assertEqual(handler.callback, callback)
    
    def test_singleton_pattern(self):
        """Test that get_instance returns same instance."""
        handler1 = CrashHandler.get_instance()
        handler2 = CrashHandler.get_instance()
        self.assertIs(handler1, handler2)
    
    def test_reset_instance(self):
        """Test reset_instance clears singleton."""
        handler1 = CrashHandler.get_instance()
        CrashHandler.reset_instance()
        handler2 = CrashHandler.get_instance()
        self.assertIsNot(handler1, handler2)


class TestCrashHandlerInstall(unittest.TestCase):
    """Test CrashHandler installation and uninstallation."""
    
    def setUp(self):
        """Reset singleton and save original excepthook."""
        CrashHandler.reset_instance()
        self.original_excepthook = sys.excepthook
    
    def tearDown(self):
        """Restore original excepthook."""
        sys.excepthook = self.original_excepthook
        CrashHandler.reset_instance()
    
    def test_install_changes_excepthook(self):
        """Test that install() changes sys.excepthook."""
        handler = CrashHandler()
        original = sys.excepthook
        
        handler.install()
        
        self.assertNotEqual(sys.excepthook, original)
        self.assertTrue(handler.enabled)
        self.assertEqual(handler._original_excepthook, original)
    
    def test_install_twice_warning(self):
        """Test that installing twice logs warning."""
        handler = CrashHandler()
        handler.install()
        
        # Second install should log warning but not crash
        handler.install()
        
        self.assertTrue(handler.enabled)
    
    def test_uninstall_restores_excepthook(self):
        """Test that uninstall() restores original excepthook."""
        handler = CrashHandler()
        original = sys.excepthook
        
        handler.install()
        handler.uninstall()
        
        self.assertEqual(sys.excepthook, original)
        self.assertFalse(handler.enabled)
        self.assertIsNone(handler._original_excepthook)
    
    def test_uninstall_without_install(self):
        """Test that uninstall without install does nothing."""
        handler = CrashHandler()
        handler.uninstall()  # Should not crash
        self.assertFalse(handler.enabled)


class TestCrashHandlerExceptionHandling(unittest.TestCase):
    """Test CrashHandler exception handling."""
    
    def setUp(self):
        """Reset singleton."""
        CrashHandler.reset_instance()
        self.handler = CrashHandler(show_dialog=False, report_crashes=False)
    
    def tearDown(self):
        """Clean up."""
        CrashHandler.reset_instance()
    
    def test_exception_handler_increments_crash_count(self):
        """Test that handling exception increments crash count."""
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_info = sys.exc_info()
            self.handler._exception_handler(*exc_info)
        
        self.assertEqual(self.handler._crash_count, 1)
        self.assertIsNotNone(self.handler._last_crash_time)
    
    def test_exception_handler_skips_keyboard_interrupt(self):
        """Test that KeyboardInterrupt is not handled."""
        original_excepthook = Mock()
        self.handler._original_excepthook = original_excepthook
        
        try:
            raise KeyboardInterrupt()
        except KeyboardInterrupt:
            exc_info = sys.exc_info()
            self.handler._exception_handler(*exc_info)
        
        # Should call original excepthook
        original_excepthook.assert_called_once()
        
        # Should not increment crash count
        self.assertEqual(self.handler._crash_count, 0)
    
    @patch('src.utils.error_handler.CrashHandler._save_crash_report')
    def test_exception_handler_saves_crash_report(self, mock_save):
        """Test that exception handler saves crash report."""
        mock_save.return_value = Path("/tmp/crash.txt")
        
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_info = sys.exc_info()
            self.handler._exception_handler(*exc_info)
        
        mock_save.assert_called_once()
    
    @patch('src.utils.error_handler.CrashHandler._show_error_dialog')
    def test_exception_handler_shows_dialog_when_enabled(self, mock_dialog):
        """Test that exception handler shows dialog when enabled."""
        self.handler.show_dialog = True
        
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_info = sys.exc_info()
            self.handler._exception_handler(*exc_info)
        
        mock_dialog.assert_called_once()
    
    def test_exception_handler_calls_callback(self):
        """Test that exception handler calls custom callback."""
        callback = Mock()
        self.handler.callback = callback
        
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_info = sys.exc_info()
            self.handler._exception_handler(*exc_info)
        
        callback.assert_called_once()


class TestCrashHandlerPathStripping(unittest.TestCase):
    """Test sensitive path stripping."""
    
    def setUp(self):
        """Create handler."""
        CrashHandler.reset_instance()
        self.handler = CrashHandler()
    
    def test_strip_home_directory(self):
        """Test that home directory is replaced with ~."""
        home = str(Path.home())
        text = f"File {home}/project/file.py"
        
        result = self.handler._strip_sensitive_paths(text)
        
        self.assertIn("~/project/file.py", result)
        self.assertNotIn(home, result)
    
    def test_strip_current_directory(self):
        """Test that current directory is replaced with dot."""
        cwd = str(Path.cwd())
        text = f"File {cwd}/src/app.py"
        
        result = self.handler._strip_sensitive_paths(text)
        
        # Path stripping replaces cwd first, then home
        # So the result depends on whether cwd is under home
        # Just verify cwd is not in result anymore
        self.assertNotIn(cwd, result)
    
    def test_strip_handles_exceptions(self):
        """Test that path stripping handles exceptions gracefully."""
        # Should not crash on invalid input
        result = self.handler._strip_sensitive_paths(None)
        self.assertIsNone(result)


class TestCrashHandlerSaveReport(unittest.TestCase):
    """Test crash report saving."""
    
    def setUp(self):
        """Create handler and temp directory."""
        CrashHandler.reset_instance()
        self.handler = CrashHandler()
    
    def test_save_crash_report_creates_file(self):
        """Test that crash report file is created."""
        import traceback
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
            crash_file = self.handler._save_crash_report(exc_type, exc_value, tb_text)
        
        self.assertTrue(crash_file.exists())
        self.assertTrue(crash_file.name.startswith("crash_"))
        self.assertTrue(crash_file.name.endswith(".txt"))
        
        # Clean up
        crash_file.unlink()
    
    def test_save_crash_report_content(self):
        """Test that crash report contains expected content."""
        import traceback
        try:
            raise ValueError("Test error message")
        except ValueError:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
            crash_file = self.handler._save_crash_report(exc_type, exc_value, tb_text)
        
        content = crash_file.read_text()
        
        self.assertIn("CLARIFY CRASH REPORT", content)
        self.assertIn("System Information:", content)
        self.assertIn("platform:", content)
        self.assertIn("python_version:", content)
        self.assertIn("exception_type: ValueError", content)
        self.assertIn("exception_message: Test error message", content)
        self.assertIn("Traceback:", content)
        
        # Clean up
        crash_file.unlink()


class TestCrashHandlerContextManager(unittest.TestCase):
    """Test CrashHandler.handle_errors() context manager."""
    
    def setUp(self):
        """Reset singleton."""
        CrashHandler.reset_instance()
    
    def test_context_manager_catches_exception(self):
        """Test that context manager catches and re-raises exception."""
        with self.assertRaises(ValueError):
            with CrashHandler.handle_errors(show_dialog=False):
                raise ValueError("Test error")
    
    def test_context_manager_calls_callback(self):
        """Test that context manager calls custom callback."""
        callback = Mock()
        
        with self.assertRaises(ValueError):
            with CrashHandler.handle_errors(show_dialog=False, callback=callback):
                raise ValueError("Test error")
        
        callback.assert_called_once()
    
    def test_context_manager_no_exception(self):
        """Test that context manager works without exception."""
        with CrashHandler.handle_errors(show_dialog=False):
            result = 1 + 1
        
        self.assertEqual(result, 2)


class TestInstallUninstall(unittest.TestCase):
    """Test module-level install/uninstall functions."""
    
    def setUp(self):
        """Reset singleton and save original excepthook."""
        CrashHandler.reset_instance()
        self.original_excepthook = sys.excepthook
    
    def tearDown(self):
        """Restore original excepthook."""
        sys.excepthook = self.original_excepthook
        CrashHandler.reset_instance()
    
    def test_install_crash_handler(self):
        """Test install_crash_handler function."""
        handler = install_crash_handler(show_dialog=False)
        
        self.assertIsInstance(handler, CrashHandler)
        self.assertTrue(handler.enabled)
        self.assertNotEqual(sys.excepthook, self.original_excepthook)
    
    def test_install_with_callback(self):
        """Test install_crash_handler with custom callback."""
        callback = Mock()
        handler = install_crash_handler(show_dialog=False, callback=callback)
        
        self.assertEqual(handler.callback, callback)
    
    def test_uninstall_crash_handler(self):
        """Test uninstall_crash_handler function."""
        install_crash_handler(show_dialog=False)
        uninstall_crash_handler()
        
        handler = CrashHandler.get_instance()
        self.assertFalse(handler.enabled)
        # sys.excepthook might be wrapped by pytest, so just check it's not our handler
        self.assertNotEqual(sys.excepthook, handler._exception_handler)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete error handling flow."""
    
    def setUp(self):
        """Reset singleton."""
        CrashHandler.reset_instance()
        self.original_excepthook = sys.excepthook
    
    def tearDown(self):
        """Restore original excepthook."""
        sys.excepthook = self.original_excepthook
        CrashHandler.reset_instance()
    
    @patch('src.utils.error_handler.CrashHandler._show_error_dialog')
    @patch('src.utils.error_handler.CrashHandler._save_crash_report')
    def test_full_crash_handling_flow(self, mock_save, mock_dialog):
        """Test complete crash handling flow."""
        mock_save.return_value = Path("/tmp/crash.txt")
        callback = Mock()
        
        # Don't install handler globally to avoid pytest interference
        handler = CrashHandler(
            show_dialog=True,
            report_crashes=False,
            callback=callback
        )
        
        # Simulate crash by calling _exception_handler directly
        try:
            raise RuntimeError("Integration test error")
        except RuntimeError:
            exc_info = sys.exc_info()
            # Call exception handler directly (not via sys.excepthook)
            with patch.object(handler, '_original_excepthook'):
                handler._exception_handler(*exc_info)
        
        # Verify all components were called
        self.assertEqual(handler._crash_count, 1)
        mock_save.assert_called_once()
        mock_dialog.assert_called_once()
        callback.assert_called_once()


if __name__ == '__main__':
    unittest.main()
