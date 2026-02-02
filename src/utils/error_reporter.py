"""
Error Reporter Module

Global exception handler that captures unhandled exceptions,
logs them, and provides UI for users to report bugs to GitHub.
"""

import sys
import traceback
import platform
from datetime import datetime
from typing import Optional
from PySide6.QtCore import QSettings  # pylint: disable=no-name-in-module  # Qt dynamic


class ErrorReporter:
    """Global error reporter for Clarify application."""

    def __init__(self, app_version: str = "2.9.89"):
        """
        Initialize error reporter.

        Args:
            app_version: Current application version
        """
        self.app_version = app_version
        self.settings = QSettings("Clarify", "Clarify")
        self.dialog = None  # Will be set by app

    def install(self):
        """Install global exception handler."""
        sys.excepthook = self.handle_exception

    def is_enabled(self) -> bool:
        """Check if error reporting is enabled in settings."""
        return self.settings.value("error_reporting/enabled", True, type=bool)

    def should_include_system_info(self) -> bool:
        """Check if system info should be included in reports."""
        return self.settings.value("error_reporting/include_system_info", True, type=bool)

    def should_auto_open_github(self) -> bool:
        """Check if GitHub Issues should auto-open on error."""
        return self.settings.value("error_reporting/auto_open_github", False, type=bool)

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """
        Global exception handler.

        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
        """
        # Ignore KeyboardInterrupt (Ctrl+C)
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Format exception info
        error_info = self.format_error(exc_type, exc_value, exc_traceback)

        # Log to file
        self.log_error(error_info)

        # Show dialog if enabled
        if self.is_enabled() and self.dialog:
            try:
                # pylint: disable=import-outside-toplevel,no-name-in-module  # Lazy Qt import
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    self.dialog.show_error(error_info)
            except Exception as e:  # pylint: disable=broad-exception-caught  # Dialog robustness
                # Fallback if dialog fails
                print(f"Error showing dialog: {e}", file=sys.stderr)
                print(error_info["full_traceback"], file=sys.stderr)
        else:
            # Print to stderr if reporting disabled
            print(error_info["full_traceback"], file=sys.stderr)

    def format_error(self, exc_type, exc_value, exc_traceback) -> dict:
        """
        Format exception information into structured dict.

        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback

        Returns:
            Dictionary with error details
        """
        # Extract traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        full_traceback = "".join(tb_lines)

        # Get last frame info
        last_frame = traceback.extract_tb(exc_traceback)[-1] if exc_traceback else None

        error_info = {
            "type": exc_type.__name__,
            "message": str(exc_value),
            "full_traceback": full_traceback,
            "timestamp": datetime.now().isoformat(),
            "file": last_frame.filename if last_frame else "Unknown",
            "line": last_frame.lineno if last_frame else 0,
            "function": last_frame.name if last_frame else "Unknown",
        }

        # Add system info if enabled
        if self.should_include_system_info():
            error_info["system_info"] = self.get_system_info()

        return error_info

    def get_system_info(self) -> dict:
        """
        Collect system information for debugging.

        Returns:
            Dictionary with system details
        """
        try:
            import PySide6  # pylint: disable=import-outside-toplevel  # Optional version check
            pyside_version = PySide6.__version__
        except Exception:  # pylint: disable=broad-exception-caught  # Version detection robustness
            pyside_version = "Unknown"

        return {
            "os": platform.system(),
            "os_version": platform.release(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "clarify_version": self.app_version,
            "pyside6_version": pyside_version,
            "architecture": platform.machine(),
        }

    def log_error(self, error_info: dict):
        """
        Log error to file.

        Args:
            error_info: Error information dictionary
        """
        import logging  # pylint: disable=import-outside-toplevel  # Lazy import
        logger = logging.getLogger("clarify.errors")

        # Log with full context
        logger.error(
            "Unhandled exception: %s: %s\nFile: %s:%s in %s\nTraceback:\n%s",
            error_info['type'], error_info['message'],
            error_info['file'], error_info['line'], error_info['function'],
            error_info['full_traceback']
        )

    def generate_github_issue_url(self, error_info: dict,
                                  steps_to_reproduce: str = "",
                                  expected_behavior: str = "",
                                  actual_behavior: str = "") -> str:
        """
        Generate GitHub issue URL with pre-filled data.

        Args:
            error_info: Error information dictionary
            steps_to_reproduce: User-provided steps
            expected_behavior: User-provided expected behavior
            actual_behavior: User-provided actual behavior

        Returns:
            GitHub issue URL with query parameters
        """
        import urllib.parse  # pylint: disable=import-outside-toplevel  # Lazy import

        # Build issue title
        title = f"[Bug] {error_info['type']}: {error_info['message'][:80]}"

        # Build issue body
        body_parts = [
            "## Bug Report",
            "",
            "**Describe the bug**",
            actual_behavior or f"An error occurred: {error_info['message']}",
            "",
            "**Steps to Reproduce**",
            steps_to_reproduce or "1. (User to fill)",
            "",
            "**Expected Behavior**",
            expected_behavior or "(User to fill)",
            "",
            "**Error Details**",
            f"- **Type**: `{error_info['type']}`",
            f"- **Message**: `{error_info['message']}`",
            f"- **File**: `{error_info['file']}:{error_info['line']}`",
            f"- **Function**: `{error_info['function']}`",
            "",
            "**Traceback**",
            "```python",
            error_info['full_traceback'],
            "```",
            "",
        ]

        # Add system info if available
        if "system_info" in error_info:
            sys_info = error_info["system_info"]
            body_parts.extend([
                "**System Information**",
                f"- **OS**: {sys_info['os']} {sys_info['os_version']}",
                f"- **Python**: {sys_info['python_version']}",
                f"- **Clarify**: {sys_info['clarify_version']}",
                f"- **PySide6**: {sys_info['pyside6_version']}",
                f"- **Architecture**: {sys_info['architecture']}",
                "",
            ])

        body_parts.append(f"**Timestamp**: {error_info['timestamp']}")

        body = "\n".join(body_parts)

        # URL encode
        params = {
            "title": title,
            "body": body,
            "labels": "bug,needs-triage"
        }

        query_string = urllib.parse.urlencode(params)
        base_url = "https://github.com/JosueAmaral15/clarify/issues/new"

        return f"{base_url}?{query_string}"


# Global instance
_error_reporter: Optional[ErrorReporter] = None  # pylint: disable=invalid-name


def get_error_reporter() -> ErrorReporter:
    """Get global error reporter instance."""
    global _error_reporter  # pylint: disable=global-statement  # Singleton pattern
    if _error_reporter is None:
        _error_reporter = ErrorReporter()
    return _error_reporter


def install_error_reporter(app_version: str = "2.9.89"):
    """
    Install global error reporter.

    Args:
        app_version: Current application version
    """
    global _error_reporter  # pylint: disable=global-statement  # Singleton pattern
    _error_reporter = ErrorReporter(app_version)
    _error_reporter.install()
    return _error_reporter
