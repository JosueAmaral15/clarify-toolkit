#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Error Handler & Crash Reporter for Clarify
-------------------------------------------
Centralized error handling system with crash reporting capabilities.

Features:
- Global exception handler (catches unhandled exceptions)
- Error dialog with user-friendly messages
- Optional error reporting to GitHub Issues
- Stack trace capture with context
- Integration with logging system (v2.9.58)
- Privacy-aware (strips sensitive paths)

Usage:
    from src.utils.error_handler import install_crash_handler, CrashHandler

    # Install at app startup
    install_crash_handler()

    # Or use context manager for specific sections
    with CrashHandler.handle_errors():
        risky_operation()

Author: Josué Amaral
Date: 2025-12-10
Sprint: v2.9.61 - Error Reporting & Crash Handler
"""

import sys
import traceback
import platform
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Any
from contextlib import contextmanager

# Import logging system (v2.9.58)
from .logger import get_logger

logger = get_logger("clarify.utils.error_handler")


class CrashHandler:
    """
    Global crash handler for unhandled exceptions.

    Captures uncaught exceptions, logs them, and optionally shows a dialog
    or sends a report to GitHub Issues.

    Attributes:
        enabled (bool): Whether crash handler is active
        show_dialog (bool): Show error dialog to user
        report_crashes (bool): Send crash reports to GitHub
        callback (Callable): Custom callback after handling error
    """

    _instance: Optional['CrashHandler'] = None
    _original_excepthook: Optional[Callable] = None

    def __init__(
        self,
        show_dialog: bool = True,
        report_crashes: bool = False,
        callback: Optional[Callable[[Exception, str], None]] = None
    ):
        """
        Initialize crash handler.

        Args:
            show_dialog: Show error dialog to user (requires GUI)
            report_crashes: Automatically send crash reports (opt-in)
            callback: Custom callback(exception, traceback_text) after handling
        """
        self.enabled = False
        self.show_dialog = show_dialog
        self.report_crashes = report_crashes
        self.callback = callback
        self._crash_count = 0
        self._last_crash_time: Optional[datetime] = None

    @classmethod
    def get_instance(cls) -> 'CrashHandler':
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset singleton (for testing)."""
        cls._instance = None

    def install(self):
        """Install as global exception handler."""
        if self.enabled:
            logger.warning("Crash handler already installed")
            return

        self._original_excepthook = sys.excepthook
        sys.excepthook = self._exception_handler
        self.enabled = True
        logger.info("Crash handler installed successfully")

    def uninstall(self):
        """Restore original exception handler."""
        if not self.enabled:
            return

        if self._original_excepthook:
            sys.excepthook = self._original_excepthook
            self._original_excepthook = None

        self.enabled = False
        logger.info("Crash handler uninstalled")

    def _exception_handler(
        self,
        exc_type: type,
        exc_value: Exception,
        exc_traceback: Any
    ):
        """
        Handle uncaught exception.

        Args:
            exc_type: Exception class
            exc_value: Exception instance
            exc_traceback: Traceback object
        """
        # Skip KeyboardInterrupt (Ctrl+C)
        if issubclass(exc_type, KeyboardInterrupt):
            if self._original_excepthook:
                self._original_excepthook(exc_type, exc_value, exc_traceback)
            return

        # Track crash frequency
        now = datetime.now()
        self._crash_count += 1
        self._last_crash_time = now

        # Format traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = ''.join(tb_lines)

        # Strip sensitive paths (privacy)
        tb_text_clean = self._strip_sensitive_paths(tb_text)

        # Log error
        logger.critical(
            "Unhandled exception (%d crashes):\n%s", self._crash_count, tb_text_clean,
            exc_info=(exc_type, exc_value, exc_traceback)
        )

        # Save crash report to file
        crash_file = self._save_crash_report(exc_type, exc_value, tb_text_clean)
        logger.info("Crash report saved to %s", crash_file)

        # Show dialog to user (if GUI available)
        if self.show_dialog:
            try:
                self._show_error_dialog(exc_value, tb_text_clean, crash_file)
            except Exception as e:  # pylint: disable=broad-exception-caught  # Dialog robustness
                logger.error("Failed to show error dialog: %s", e)

        # Send report to GitHub (if enabled)
        if self.report_crashes:
            try:
                self._send_crash_report(exc_value, tb_text_clean)
            except Exception as e:  # pylint: disable=broad-exception-caught  # Report robustness
                logger.error("Failed to send crash report: %s", e)

        # Call custom callback
        if self.callback:
            try:
                self.callback(exc_value, tb_text_clean)
            except Exception as e:  # pylint: disable=broad-exception-caught  # Callback robustness
                logger.error("Error in crash handler callback: %s", e)

        # Call original handler (prints to stderr)
        if self._original_excepthook:
            self._original_excepthook(exc_type, exc_value, exc_traceback)

    def _strip_sensitive_paths(self, text: str) -> str:
        """
        Strip sensitive file paths from traceback.

        Replaces absolute paths with relative paths for privacy.

        Args:
            text: Traceback text

        Returns:
            Cleaned text with relative paths
        """
        try:
            home = str(Path.home())
            cwd = str(Path.cwd())

            # Replace home directory
            text = text.replace(home, "~")

            # Replace current directory
            text = text.replace(cwd, ".")

            # Replace common system paths
            text = text.replace("/usr/local/lib/python", "python")
            text = text.replace("/usr/lib/python", "python")
            text = text.replace("C:\\Users\\", "~\\")
            text = text.replace("C:\\Program Files\\", "")

        except Exception as e:  # pylint: disable=broad-exception-caught  # Path sanitization robustness
            logger.warning("Failed to strip sensitive paths: %s", e)

        return text

    def _save_crash_report(
        self,
        exc_type: type,
        exc_value: Exception,
        tb_text: str,
        tb_object: Any = None  # pylint: disable=unused-argument  # Future use / API consistency
    ) -> Path:
        """
        Save crash report to file.

        Args:
            exc_type: Exception class
            exc_value: Exception instance
            tb_text: Formatted traceback (string)
            tb_object: Traceback object (unused, for compatibility)

        Returns:
            Path to crash report file
        """
        # Create crash reports directory
        crash_dir = Path.home() / ".config" / "clarify" / "crashes"
        crash_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        crash_file = crash_dir / f"crash_{timestamp}.txt"

        # Gather system information
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "crash_time": datetime.now().isoformat(),
            "crash_count": self._crash_count,
            "exception_type": exc_type.__name__,
            "exception_message": str(exc_value),
        }

        # Write crash report
        with open(crash_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("CLARIFY CRASH REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write("System Information:\n")
            f.write("-" * 80 + "\n")
            for key, value in system_info.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

            f.write("Traceback:\n")
            f.write("-" * 80 + "\n")
            f.write(tb_text)
            f.write("\n")

            f.write("=" * 80 + "\n")
            f.write("End of crash report\n")
            f.write("=" * 80 + "\n")

        return crash_file

    def _show_error_dialog(
        self,
        exception: Exception,
        traceback_text: str,
        crash_file: Path
    ):
        """
        Show error dialog to user (GUI only).

        Args:
            exception: Exception instance
            traceback_text: Formatted traceback
            crash_file: Path to crash report file
        """
        try:
            # pylint: disable=import-outside-toplevel  # Lazy Qt import
            from PySide6.QtWidgets import QApplication, QMessageBox

            # Ensure QApplication exists
            app = QApplication.instance()
            if not app:
                logger.warning("No QApplication instance, cannot show dialog")
                return

            # Create error dialog
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Clarify - Unexpected Error")
            msg.setText(
                f"<b>An unexpected error occurred:</b><br><br>"
                f"<code>{type(exception).__name__}: {str(exception)}</code>"
            )
            msg.setInformativeText(
                f"The application may be in an unstable state. "
                f"It's recommended to save your work and restart.<br><br>"
                f"Crash report saved to:<br>"
                f"<code>{crash_file}</code>"
            )
            msg.setDetailedText(traceback_text)
            msg.setStandardButtons(QMessageBox.Close)
            msg.setDefaultButton(QMessageBox.Close)

            # Add "Report Bug" button if reporting enabled
            report_btn = None
            if self.report_crashes:
                report_btn = msg.addButton("Report Bug", QMessageBox.ActionRole)

            msg.exec()

            # Handle "Report Bug" click
            if self.report_crashes and report_btn and msg.clickedButton() == report_btn:
                self._send_crash_report(exception, traceback_text)

        except ImportError:
            logger.warning("PySide6 not available, cannot show error dialog")
        except Exception as e:  # pylint: disable=broad-exception-caught  # Dialog robustness
            logger.error("Error showing dialog: %s", e)

    def _send_crash_report(self, _exception: Exception, _traceback_text: str):
        """
        Send crash report to GitHub Issues (opt-in).

        Args:
            exception: Exception instance
            traceback_text: Formatted traceback
        """
        # Note: This is a placeholder for future implementation
        # Would require GitHub API integration or email service
        logger.info("Crash report sending not yet implemented")

        # Future implementation could:
        # 1. Use GitHub API to create issue
        # 2. Send email with crash details
        # 3. POST to error tracking service (Sentry, Rollbar)

    @staticmethod
    @contextmanager
    def handle_errors(
        show_dialog: bool = False,
        callback: Optional[Callable[[Exception], None]] = None
    ):
        """
        Context manager for handling errors in specific code blocks.

        Usage:
            with CrashHandler.handle_errors():
                risky_operation()

        Args:
            show_dialog: Show error dialog if exception occurs
            callback: Custom callback(exception) on error
        """
        try:
            yield
        except Exception as e:
            # Log error
            logger.error("Error in handled context: %s", e, exc_info=True)

            # Show dialog if requested
            if show_dialog:
                try:
                    error_handler = CrashHandler.get_instance()
                    tb_text = traceback.format_exc()
                    crash_file = error_handler._save_crash_report(type(e), e, tb_text)  # pylint: disable=protected-access  # Internal handler method
                    error_handler._show_error_dialog(e, tb_text, crash_file)  # pylint: disable=protected-access  # Internal handler method
                except Exception as dialog_error:  # pylint: disable=broad-exception-caught  # Dialog robustness
                    logger.error("Failed to show error dialog: %s", dialog_error)

            # Call custom callback
            if callback:
                try:
                    callback(e)
                except Exception as callback_error:  # pylint: disable=broad-exception-caught  # Callback robustness
                    logger.error("Error in callback: %s", callback_error)

            # Re-raise exception
            raise


def install_crash_handler(
    show_dialog: bool = True,
    report_crashes: bool = False,
    callback: Optional[Callable[[Exception, str], None]] = None
) -> CrashHandler:
    """
    Install global crash handler.

    Call this at application startup to catch all unhandled exceptions.

    Args:
        show_dialog: Show error dialog to user (requires GUI)
        report_crashes: Automatically send crash reports (opt-in)
        callback: Custom callback(exception, traceback_text) after handling

    Returns:
        CrashHandler instance

    Example:
        install_crash_handler(show_dialog=True, report_crashes=False)
    """
    crash_handler = CrashHandler(
        show_dialog=show_dialog,
        report_crashes=report_crashes,
        callback=callback
    )
    crash_handler.install()
    return crash_handler


def uninstall_crash_handler():
    """
    Uninstall global crash handler.

    Restores original sys.excepthook.
    """
    crash_handler = CrashHandler.get_instance()
    crash_handler.uninstall()


# Demo code
if __name__ == "__main__":
    # Configure logging
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("Error Handler Demo")
    print("=" * 80)

    # Install crash handler (no dialog in CLI mode)
    handler = install_crash_handler(show_dialog=False)
    print(f"✅ Crash handler installed (dialog={handler.show_dialog})")

    # Test 1: Context manager
    print("\nTest 1: Context manager with handled error")
    try:
        with CrashHandler.handle_errors():
            result = 10 / 0  # ZeroDivisionError
    except ZeroDivisionError:
        print("✅ Error caught and handled")

    # Test 2: Unhandled exception (will be caught by crash handler)
    print("\nTest 2: Unhandled exception (triggers crash handler)")
    print("This will cause the program to crash with a crash report...")

    # Uncomment to test crash handler:
    # raise ValueError("Test crash for demonstration purposes")

    print("\n✅ Error handler demo complete")
    print(f"Crash reports directory: {Path.home() / '.config' / 'clarify' / 'crashes'}")
