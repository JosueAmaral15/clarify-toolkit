#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Update Notification Dialog - GUI for Update Checker

Non-modal dialog showing available updates with:
- Version info and changelog excerpt
- Download and "View Changelog" buttons
- "Don't show again for this version" option
- QSettings persistence for preferences

Author: Josué Amaral
Date: 2025-12-08
Version: 2.9.45
"""

import webbrowser
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QCheckBox, QTextEdit, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont, QIcon

from src.i18n.translator import tr


class UpdateNotificationDialog(QDialog):
    """
    Dialog to notify users about available Clarify updates.
    
    Features:
    - Non-modal display (doesn't block main window)
    - Shows version, release date, and changelog excerpt
    - Links to GitHub releases and CHANGELOG.md
    - "Don't show again" preference per version
    - QSettings persistence
    
    Example:
        >>> dialog = UpdateNotificationDialog(
        ...     parent=main_window,
        ...     latest_version="2.9.45",
        ...     release_url="https://github.com/.../releases/tag/v2.9.45",
        ...     changelog_url="https://github.com/.../CHANGELOG.md#v2945",
        ...     release_notes="## Added\\n- Update checker..."
        ... )
        >>> dialog.show()  # Non-modal
    """
    
    def __init__(
        self, 
        parent=None, 
        latest_version: str = "",
        release_url: str = "",
        changelog_url: str = "",
        release_notes: str = "",
        published_at: str = ""
    ):
        """
        Initialize update notification dialog.
        
        Args:
            parent: Parent widget (main window)
            latest_version: New version available (e.g., "2.9.45")
            release_url: GitHub release page URL
            changelog_url: Direct link to CHANGELOG.md section
            release_notes: Markdown release notes (excerpt)
            published_at: Publication date (ISO 8601)
        """
        super().__init__(parent)
        
        self.latest_version = latest_version
        self.release_url = release_url
        self.changelog_url = changelog_url
        self.release_notes = release_notes
        self.published_at = published_at
        
        self.settings = QSettings("Clarify", "ClarifyApp")
        
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Build dialog UI."""
        self.setWindowTitle(tr("update_notification.title"))
        self.setMinimumSize(500, 400)
        self.setModal(False)  # Non-modal
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # --- Header ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        # Title
        title = QLabel(tr("update_notification.header").replace("{version}", self.latest_version))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        # Publication date
        if self.published_at:
            date_label = QLabel(tr("update_notification.published_at").replace("{date}", self._format_date(self.published_at)))
            date_label.setStyleSheet("color: gray;")
            header_layout.addWidget(date_label)
        
        layout.addLayout(header_layout)
        
        # --- Release Notes ---
        notes_label = QLabel(tr("update_notification.whats_new"))
        layout.addWidget(notes_label)
        
        notes_text = QTextEdit()
        notes_text.setReadOnly(True)
        notes_text.setPlainText(self._format_release_notes(self.release_notes))
        notes_text.setMaximumHeight(150)
        notes_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(notes_text)
        
        # --- Changelog Link ---
        changelog_btn = QPushButton(tr("update_notification.btn_changelog"))
        changelog_btn.clicked.connect(self._open_changelog)
        changelog_btn.setStyleSheet("text-align: left; padding: 5px;")
        layout.addWidget(changelog_btn)
        
        # --- Spacer ---
        layout.addStretch()
        
        # --- "Don't show again" Option ---
        self.dont_show_checkbox = QCheckBox(
            tr("update_notification.chk_dont_show").replace("{version}", self.latest_version)
        )
        layout.addWidget(self.dont_show_checkbox)
        
        # --- Action Buttons ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Download button (primary)
        download_btn = QPushButton(tr("update_notification.btn_download"))
        download_btn.clicked.connect(self._download_update)
        download_btn.setDefault(True)
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        button_layout.addWidget(download_btn)
        
        # Remind me later button (secondary)
        later_btn = QPushButton(tr("update_notification.btn_later"))
        later_btn.clicked.connect(self._remind_later)
        later_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border: 1px solid gray;
                border-radius: 4px;
            }
        """)
        button_layout.addWidget(later_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _format_date(self, iso_date: str) -> str:
        """
        Format ISO 8601 date to readable format.
        
        Args:
            iso_date: ISO 8601 date (e.g., "2025-12-08T15:30:00Z")
        
        Returns:
            Formatted date (e.g., "08/12/2025")
        """
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
            return dt.strftime("%d/%m/%Y")
        except (ValueError, AttributeError):
            return iso_date
    
    def _format_release_notes(self, notes: str) -> str:
        """
        Extract and format release notes excerpt.
        
        Args:
            notes: Full markdown release notes
        
        Returns:
            Formatted excerpt (first 5 lines or 300 chars)
        """
        if not notes:
            return tr("update_notification.no_description")
        
        # Remove markdown headers
        lines = [line.strip() for line in notes.split('\n') if line.strip()]
        clean_lines = [line.lstrip('#').strip() for line in lines]
        
        # Take first 5 lines
        excerpt = '\n'.join(clean_lines[:5])
        
        # Truncate if too long
        if len(excerpt) > 300:
            excerpt = excerpt[:297] + "..."
        
        return excerpt
    
    def _open_changelog(self) -> None:
        """Open CHANGELOG.md in browser."""
        if self.changelog_url:
            webbrowser.open(self.changelog_url)
    
    def _download_update(self) -> None:
        """Open GitHub releases page and save preferences."""
        # Save "don't show again" preference
        if self.dont_show_checkbox.isChecked():
            self._save_skip_preference()
        
        # Open GitHub releases
        if self.release_url:
            webbrowser.open(self.release_url)
        
        self.accept()
    
    def _remind_later(self) -> None:
        """Close dialog without downloading (may show again next time)."""
        # Save "don't show again" preference if checked
        if self.dont_show_checkbox.isChecked():
            self._save_skip_preference()
        
        self.reject()
    
    def _save_skip_preference(self) -> None:
        """Save preference to skip this version in QSettings."""
        skip_versions = self.settings.value("update_checker/skip_versions", [])
        if not isinstance(skip_versions, list):
            skip_versions = []
        
        if self.latest_version not in skip_versions:
            skip_versions.append(self.latest_version)
            self.settings.setValue("update_checker/skip_versions", skip_versions)
    
    @staticmethod
    def should_show_for_version(version: str) -> bool:
        """
        Check if dialog should be shown for a given version.
        
        Args:
            version: Version to check (e.g., "2.9.45")
        
        Returns:
            True if should show, False if user opted to skip
        
        Example:
            >>> if UpdateNotificationDialog.should_show_for_version("2.9.45"):
            ...     dialog = UpdateNotificationDialog(...)
            ...     dialog.show()
        """
        settings = QSettings("Clarify", "ClarifyApp")
        skip_versions = settings.value("update_checker/skip_versions", [])
        
        if not isinstance(skip_versions, list):
            skip_versions = []
        
        return version not in skip_versions
    
    @staticmethod
    def clear_skip_preferences() -> None:
        """Clear all "don't show again" preferences (useful for testing)."""
        settings = QSettings("Clarify", "ClarifyApp")
        settings.setValue("update_checker/skip_versions", [])


# Convenience function for showing dialog
def show_update_notification(
    parent=None,
    latest_version: str = "",
    release_url: str = "",
    changelog_url: str = "",
    release_notes: str = "",
    published_at: str = ""
) -> UpdateNotificationDialog:
    """
    Show update notification dialog (non-modal).
    
    Args:
        parent: Parent widget
        latest_version: New version
        release_url: GitHub release URL
        changelog_url: CHANGELOG.md URL
        release_notes: Release notes markdown
        published_at: Publication date
    
    Returns:
        Dialog instance (already shown)
    
    Example:
        >>> dialog = show_update_notification(
        ...     parent=main_window,
        ...     latest_version="2.9.45",
        ...     release_url="https://...",
        ...     changelog_url="https://...",
        ...     release_notes="## Added...",
        ...     published_at="2025-12-08T15:30:00Z"
        ... )
    """
    dialog = UpdateNotificationDialog(
        parent=parent,
        latest_version=latest_version,
        release_url=release_url,
        changelog_url=changelog_url,
        release_notes=release_notes,
        published_at=published_at
    )
    dialog.show()  # Non-modal
    return dialog
