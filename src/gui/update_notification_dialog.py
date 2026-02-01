"""
Update Notification Dialog

Non-modal dialog to notify users of available updates.

Author: Josué Amaral
Date: 2025-12-23
Version: 2.9.109
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules


                from datetime import datetime

import webbrowser
from PySide6.QtWidgets import (
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from src.i18n.translator import tr

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
