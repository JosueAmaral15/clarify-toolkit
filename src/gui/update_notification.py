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
# pylint: disable=no-name-in-module  # Qt dynamic modules


            from datetime import datetime

import webbrowser
from PySide6.QtWidgets import (
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont, QIcon

from src.i18n.translator import tr
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
