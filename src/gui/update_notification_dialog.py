"""
Update Notification Dialog

Non-modal dialog to notify users of available updates.

Author: Josué Amaral
Date: 2025-12-23
Version: 2.9.109
"""

import webbrowser
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QCheckBox,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from src.i18n.translator import tr


class UpdateNotificationDialog(QDialog):
    """Dialog to notify users of available updates."""

    # Signals
    check_now_requested = Signal()
    skip_version_requested = Signal(str)

    def __init__(self, parent=None):
        """Initialize update notification dialog."""
        super().__init__(parent)

        self.current_result = None

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle(tr("update_notification.window_title_available"))
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        # Main layout
        layout = QVBoxLayout(self)

        # Header with emoji
        header = QLabel(tr("update_notification.header_new_version"))
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        # Version info group
        version_group = QGroupBox(tr("update_notification.group_version"))
        version_layout = QVBoxLayout(version_group)

        self.lbl_current = QLabel(tr("update_notification.lbl_current"))
        self.lbl_latest = QLabel(tr("update_notification.lbl_latest"))
        self.lbl_published = QLabel(tr("update_notification.lbl_published"))

        version_layout.addWidget(self.lbl_current)
        version_layout.addWidget(self.lbl_latest)
        version_layout.addWidget(self.lbl_published)

        layout.addWidget(version_group)

        # Release notes
        notes_label = QLabel(tr("update_notification.lbl_whats_new"))
        notes_label_font = QFont()
        notes_label_font.setBold(True)
        notes_label.setFont(notes_label_font)
        layout.addWidget(notes_label)

        self.text_notes = QTextEdit()
        self.text_notes.setReadOnly(True)
        self.text_notes.setMaximumHeight(150)
        layout.addWidget(self.text_notes)

        # Checkbox to skip this version
        self.chk_skip_version = QCheckBox(tr("update_notification.chk_skip_version"))
        layout.addWidget(self.chk_skip_version)

        # Buttons
        btn_layout = QHBoxLayout()

        self.btn_download = QPushButton(f"📥 {tr('update_notification.btn_download')}")
        self.btn_download.setStyleSheet(
            "QPushButton { background-color: #0078D4; color: white; font-weight: bold; padding: 8px; }"
            "QPushButton:hover { background-color: #005A9E; }"
        )

        self.btn_remind_later = QPushButton(tr("update_notification.btn_remind_later"))
        self.btn_close = QPushButton(tr("update_notification.btn_close"))

        btn_layout.addWidget(self.btn_download)
        btn_layout.addWidget(self.btn_remind_later)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

    def _connect_signals(self):
        """Connect signals to slots."""
        self.btn_download.clicked.connect(self._on_download_clicked)
        self.btn_remind_later.clicked.connect(self.accept)
        self.btn_close.clicked.connect(self.reject)

    def show_update(self, result: dict):
        """
        Show update notification with result data.

        Args:
            result: Dict from UpdateChecker.check_for_updates()
        """
        self.current_result = result

        # Populate labels
        current = result.get("current_version", "Unknown")
        latest = result.get("latest_version", "Unknown")
        published = result.get("published_at", "")

        self.lbl_current.setText(f"Current version: v{current}")
        self.lbl_latest.setText(f"Latest version: v{latest}")

        # Format published date
        if published:
            try:
                from datetime import datetime

                dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                formatted = dt.strftime("%B %d, %Y")
                self.lbl_published.setText(f"Published: {formatted}")
            except:
                self.lbl_published.setText(f"Published: {published}")
        else:
            self.lbl_published.setText(tr("update_notification.text_published_unknown"))

        # Release notes
        notes = result.get("release_notes", "No release notes available.")
        self.text_notes.setPlainText(notes)

        # Show dialog
        self.exec()

    def _on_download_clicked(self):
        """Handle download button click."""
        if self.current_result:
            download_url = self.current_result.get("download_url", "")

            if download_url:
                # Open browser
                try:
                    webbrowser.open(download_url)

                    # Handle skip version checkbox
                    if self.chk_skip_version.isChecked():
                        latest = self.current_result.get("latest_version", "")
                        if latest:
                            self.skip_version_requested.emit(latest)

                    self.accept()
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        tr("update.browser_error_title"),
                        tr("update.browser_error").format(error=str(e), url=download_url),
                    )
            else:
                QMessageBox.warning(self, tr("update.browser_error_title"), tr("update.url_unavailable"))


class ManualCheckDialog(QDialog):
    """Dialog for manual update check results."""

    def __init__(self, parent=None):
        """Initialize manual check dialog."""
        super().__init__(parent)

        self.setWindowTitle(tr("update_notification.window_title_check"))
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Status label
        self.lbl_status = QLabel(tr("update_notification.lbl_checking"))
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_close = QPushButton(tr("update_notification.btn_close"))
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

    def show_checking(self):
        """Show checking status."""
        self.lbl_status.setText("🔍 Checking for updates...")
        self.btn_close.setEnabled(False)
        self.show()

    def show_result(self, result: dict):
        """
        Show check result.

        Args:
            result: Dict from UpdateChecker.check_for_updates()
        """
        if not result.get("success"):
            # Error occurred
            error = result.get("error", "Unknown error")
            self.lbl_status.setText(f"❌ Error checking for updates:\n\n{error}")
        elif result.get("update_available"):
            # Update available
            latest = result.get("latest_version", "Unknown")
            current = result.get("current_version", "Unknown")
            self.lbl_status.setText(
                f"✅ Update available!\n\n"
                f"Current version: v{current}\n"
                f"Latest version: v{latest}\n\n"
                f"The update notification will be shown."
            )
        else:
            # Up to date
            current = result.get("current_version", "Unknown")
            self.lbl_status.setText(
                f"✅ You're up to date!\n\n" f"Current version: v{current}\n\n" f"No updates available at this time."
            )

        self.btn_close.setEnabled(True)
