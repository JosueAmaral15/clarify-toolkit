"""
Error Report Dialog

UI dialog for displaying errors and allowing users to report bugs to GitHub.
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules


        from datetime import datetime

import webbrowser
import pyperclip
from PySide6.QtWidgets import (
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QIcon, QFont
        from PySide6.QtWidgets import QFileDialog

from src.i18n.translator import tr, tooltip_tr
        from src.utils.error_reporter import get_error_reporter

    def _save_log(self):
        """Save full error log to file."""
        if not self.current_error_info:
            return

        from PySide6.QtWidgets import QFileDialog
        from datetime import datetime

        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"clarify_error_{timestamp}.log"

        # Ask user for save location
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Error Log",
            default_filename,
            "Log Files (*.log);;Text Files (*.txt);;All Files (*)"
        )

        if not filename:
            return

        # Write to file
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=== Clarify Error Report ===\n\n")
                f.write(f"Type: {self.current_error_info['type']}\n")
                f.write(f"Message: {self.current_error_info['message']}\n")
                f.write(f"Location: {self.current_error_info['file']}:{self.current_error_info['line']} in {self.current_error_info['function']}\n")
                f.write(f"Timestamp: {self.current_error_info['timestamp']}\n\n")
                f.write("Traceback:\n")
                f.write(self.current_error_info['full_traceback'])
                f.write("\n")

                if "system_info" in self.current_error_info:
                    sys_info = self.current_error_info["system_info"]
                    f.write("\nSystem Information:\n")
                    f.write(f"OS: {sys_info['os']} {sys_info['os_version']}\n")
                    f.write(f"Python: {sys_info['python_version']}\n")
                    f.write(f"Clarify: {sys_info['clarify_version']}\n")
                    f.write(f"PySide6: {sys_info['pyside6_version']}\n")
                    f.write(f"Architecture: {sys_info['architecture']}\n")

            QMessageBox.information(
                self,
                tr("error_report.msg_saved_title"),
                tr("error_report.msg_saved").format(filename=filename)
            )
        except Exception as e:
            QMessageBox.warning(self, tr("error_report.msg_browser_error_title"),
                tr("error_report.msg_save_error").format(error=e))

    def _close_dialog(self):
        """Close dialog and update settings if needed."""
        # Update settings if checkbox is checked
        if self.dont_show_checkbox.isChecked():
            self.settings.setValue("error_reporting/enabled", False)
            QMessageBox.information(
                self,
                tr("error_report.msg_reporting_disabled_title"),
                tr("error_report.msg_reporting_disabled")
            )

        self.close()
