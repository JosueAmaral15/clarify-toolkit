"""
Error Report Dialog

UI dialog for displaying errors and allowing users to report bugs to GitHub.
"""

import webbrowser
import pyperclip
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QCheckBox, QGroupBox, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QIcon, QFont
from src.i18n.translator import tr


class ErrorReportDialog(QDialog):
    """Dialog for displaying errors and reporting to GitHub."""
    
    def __init__(self, parent=None):
        """Initialize error report dialog."""
        super().__init__(parent)
        self.setWindowTitle(tr("error_report.title"))
        self.resize(700, 600)
        self.setModal(True)
        
        self.current_error_info = None
        self.settings = QSettings("Clarify", "Clarify")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(tr("error_report.header"))
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(
            "We're sorry for the inconvenience. You can help us fix this by reporting the error to GitHub."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Error Summary Group
        error_group = QGroupBox(tr("error_report.group_summary"))
        error_layout = QVBoxLayout()
        
        self.error_type_label = QLabel(tr("error_report.lbl_type"))
        self.error_message_label = QLabel(tr("error_report.lbl_message"))
        self.error_message_label.setWordWrap(True)
        self.error_location_label = QLabel(tr("error_report.lbl_location"))
        
        error_layout.addWidget(self.error_type_label)
        error_layout.addWidget(self.error_message_label)
        error_layout.addWidget(self.error_location_label)
        error_group.setLayout(error_layout)
        layout.addWidget(error_group)
        
        # Steps to Reproduce
        steps_group = QGroupBox(tr("error_report.group_steps"))
        steps_layout = QVBoxLayout()
        self.steps_edit = QTextEdit()
        self.steps_edit.setPlaceholderText(tr("error_report.placeholder_steps"))
        self.steps_edit.setMaximumHeight(100)
        steps_layout.addWidget(self.steps_edit)
        steps_group.setLayout(steps_layout)
        layout.addWidget(steps_group)
        
        # Expected/Actual Behavior
        behavior_group = QGroupBox(tr("error_report.group_behavior"))
        behavior_layout = QVBoxLayout()
        
        QLabel_expected = QLabel(tr("error_report.lbl_expected"))
        self.expected_edit = QTextEdit()
        self.expected_edit.setPlaceholderText(tr("error_report.placeholder_expected"))
        self.expected_edit.setMaximumHeight(60)
        
        QLabel_actual = QLabel(tr("error_report.lbl_actual"))
        self.actual_edit = QTextEdit()
        self.actual_edit.setPlaceholderText(tr("error_report.placeholder_actual"))
        self.actual_edit.setMaximumHeight(60)
        
        behavior_layout.addWidget(QLabel_expected)
        behavior_layout.addWidget(self.expected_edit)
        behavior_layout.addWidget(QLabel_actual)
        behavior_layout.addWidget(self.actual_edit)
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        # Checkbox: Don't show again
        self.dont_show_checkbox = QCheckBox(tr("error_report.chk_dont_show"))
        layout.addWidget(self.dont_show_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.github_button = QPushButton(tr("error_report.btn_github"))
        self.github_button.setToolTip("Open GitHub Issues with pre-filled bug report")
        self.github_button.clicked.connect(self._send_to_github)
        
        self.copy_button = QPushButton(tr("error_report.btn_copy"))
        self.copy_button.setToolTip("Copy error info to clipboard")
        self.copy_button.clicked.connect(self._copy_to_clipboard)
        
        self.save_button = QPushButton(tr("error_report.btn_save"))
        self.save_button.setToolTip("Save full error log to file")
        self.save_button.clicked.connect(self._save_log)
        
        self.close_button = QPushButton(tr("error_report.btn_close"))
        self.close_button.clicked.connect(self._close_dialog)
        
        button_layout.addWidget(self.github_button)
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def show_error(self, error_info: dict):
        """
        Display error information in dialog.
        
        Args:
            error_info: Error information dictionary from ErrorReporter
        """
        self.current_error_info = error_info
        
        # Update labels
        self.error_type_label.setText(f"Type: {error_info['type']}")
        self.error_message_label.setText(f"Message: {error_info['message']}")
        self.error_location_label.setText(
            f"Location: {error_info['file']}:{error_info['line']} in {error_info['function']}"
        )
        
        # Clear previous input
        self.steps_edit.clear()
        self.expected_edit.clear()
        self.actual_edit.clear()
        
        # Show dialog
        self.show()
        self.raise_()
        self.activateWindow()
    
    def _send_to_github(self):
        """Open GitHub Issues with pre-filled bug report."""
        if not self.current_error_info:
            return
        
        from src.utils.error_reporter import get_error_reporter
        reporter = get_error_reporter()
        
        # Get user input
        steps = self.steps_edit.toPlainText().strip()
        expected = self.expected_edit.toPlainText().strip()
        actual = self.actual_edit.toPlainText().strip()
        
        # Generate URL
        url = reporter.generate_github_issue_url(
            self.current_error_info,
            steps_to_reproduce=steps,
            expected_behavior=expected,
            actual_behavior=actual
        )
        
        # Open in browser
        try:
            webbrowser.open(url)
            QMessageBox.information(
                self,
                tr("error_report.msg_github_issues_title"),
                tr("error_report.msg_github_issues")
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                tr("error_report.msg_browser_error_title"),
                tr("error_report.msg_browser_error").format(error=e)
            )
        
        self._close_dialog()
    
    def _copy_to_clipboard(self):
        """Copy error information to clipboard."""
        if not self.current_error_info:
            return
        
        # Format error info
        lines = [
            "=== Clarify Error Report ===",
            "",
            f"Type: {self.current_error_info['type']}",
            f"Message: {self.current_error_info['message']}",
            f"Location: {self.current_error_info['file']}:{self.current_error_info['line']} in {self.current_error_info['function']}",
            f"Timestamp: {self.current_error_info['timestamp']}",
            "",
            "Traceback:",
            self.current_error_info['full_traceback'],
        ]
        
        # Add system info if available
        if "system_info" in self.current_error_info:
            sys_info = self.current_error_info["system_info"]
            lines.extend([
                "",
                "System Information:",
                f"OS: {sys_info['os']} {sys_info['os_version']}",
                f"Python: {sys_info['python_version']}",
                f"Clarify: {sys_info['clarify_version']}",
                f"PySide6: {sys_info['pyside6_version']}",
                f"Architecture: {sys_info['architecture']}",
            ])
        
        text = "\n".join(lines)
        
        # Copy to clipboard
        try:
            pyperclip.copy(text)
            QMessageBox.information(
                self,
                tr("error_report.msg_copied_title"),
                tr("error_report.msg_copied")
            )
        except Exception as e:
            QMessageBox.warning(self, tr("error_report.msg_browser_error_title"), 
                tr("error_report.msg_clipboard_error").format(error=e))
    
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
