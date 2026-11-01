"""
Window Settings Manager for MainWindow

Centralizes window state persistence logic, reducing MainWindow complexity.
Extracted from MainWindow as part of Phase 3.5 refactoring.

Handles:
- Window geometry save/restore
- Theme application
- Transparency settings
- Settings persistence
- Close event handling

Author: Refactoring Phase 3.5
Date: 2024-12-24
Version: v2.9.114
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=import-outside-toplevel  # Lazy imports for circular dependency avoidance
# pylint: disable=broad-exception-caught  # GUI robustness

from __future__ import annotations
from configparser import ConfigParser
from pathlib import Path
from typing import TYPE_CHECKING

from ..appearance_defaults import (
    DEFAULT_THEME,
    DEFAULT_WINDOW_OPACITY_PERCENT,
    normalize_opacity_percent,
    opacity_percent_to_qt,
)

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent
    from ..app import MainWindow


class WindowSettings:
    """Centralized window settings and state management."""

    @staticmethod
    def apply_saved_settings(main_window) -> None:
        """
        Apply saved settings on startup.

        Args:
            main_window: MainWindow instance
        """
        from ..theme_manager import ThemeManager
        from PySide6.QtWidgets import QApplication

        # Apply saved theme
        theme_mode = main_window.settings.get("theme", DEFAULT_THEME)
        if theme_mode == "light":
            main_window.act_theme_light.setChecked(True)
            ThemeManager.apply_theme(QApplication.instance(), "light")
        elif theme_mode == "dark":
            main_window.act_theme_dark.setChecked(True)
            ThemeManager.apply_theme(QApplication.instance(), "dark")
        else:
            main_window.act_theme_system.setChecked(True)
            ThemeManager.apply_theme(QApplication.instance(), "system")

        # Apply saved transparency (Task #18 - v2.9.9)
        saved_opacity = normalize_opacity_percent(
            main_window.settings.get("window_opacity", DEFAULT_WINDOW_OPACITY_PERCENT)
        )
        WindowSettings.apply_window_opacity_percent(main_window, saved_opacity)
        restyle_tabs = getattr(main_window, "_apply_tab_close_button_style", None)
        if callable(restyle_tabs):
            restyle_tabs()

    @staticmethod
    def apply_window_opacity_percent(main_window, opacity_percent: int) -> None:
        """Apply displayed opacity percent to the main and existing tool windows."""
        opacity = opacity_percent_to_qt(opacity_percent)
        main_window.setWindowOpacity(opacity)
        WindowSettings._apply_opacity_to_docks(main_window, opacity)

    @staticmethod
    def _apply_opacity_to_docks(main_window, opacity: float) -> None:
        """Apply opacity to all existing docks and detached tool hosts."""
        from PySide6.QtWidgets import QDockWidget

        dock_names = [
            'dock_translate', 'dock_rewriter', 'dock_text_extractor',
            'dock_placeholder_replacer', 'dock_ai_processor',
            'dock_json_search', 'dock_case_converter', 'dock_history'
        ]
        windows = list(main_window.findChildren(QDockWidget))
        for dock_name in dock_names:
            dock = getattr(main_window, dock_name, None)
            if dock is not None and dock not in windows:
                windows.append(dock)
        manager = getattr(main_window, "tool_window_manager", None)
        if manager is not None:
            windows.extend(manager.detached_windows())
        for window in windows:
            window.setWindowOpacity(opacity)

    @staticmethod
    def restore_prefs(main_window) -> None:
        """
        Migrate a legacy theme only when JSON settings have no explicit choice.

        Args:
            main_window: MainWindow instance
        """
        settings = main_window.settings
        has_saved_value = getattr(settings, "has_saved_value", None)
        if callable(has_saved_value) and has_saved_value("theme"):
            return

        for config_path in (
            Path.home() / ".config" / "clarify.conf",
            Path.home() / ".clarify" / "preferences.ini",
        ):
            if not config_path.exists():
                continue
            try:
                cfg = ConfigParser()
                cfg.read(config_path, encoding="utf-8")
                mode = cfg.get("THEME", "mode", fallback="").strip().lower()
            except (OSError, ValueError):
                continue
            if mode in {"system", "light", "dark"}:
                settings.set("theme", mode)
                return

    @staticmethod
    def save_geometry(main_window) -> None:
        """
        Save window geometry to settings.

        Args:
            main_window: MainWindow instance
        """
        geometry_hex = main_window.saveGeometry().toHex().data().decode()
        main_window.settings.set("window_geometry", geometry_hex)

    @staticmethod
    def restore_geometry(main_window) -> None:
        """
        Restore window geometry from settings.

        Args:
            main_window: MainWindow instance
        """
        from PySide6.QtCore import QByteArray

        geometry_hex = main_window.settings.get("window_geometry", None)
        if geometry_hex:
            try:
                geometry = QByteArray.fromHex(geometry_hex.encode())
                main_window.restoreGeometry(geometry)
            except Exception:
                pass  # Ignore errors in geometry restoration

    @staticmethod
    def handle_close_event(main_window, event) -> None:
        """
        Handle window close event with thread cleanup and settings save.

        Args:
            main_window: MainWindow instance
            event: QCloseEvent
        """
        from PySide6.QtWidgets import QMessageBox, QCheckBox
        from ..i18n.translator import tr
        from ..ui import thread_manager

        # Check if there are any active threads
        active_threads = thread_manager.get_active_threads()
        has_active_threads = any(count > 0 for count in active_threads.values())

        if has_active_threads:
            # Warn user about active threads
            reply = QMessageBox.warning(
                main_window,
                "Active Processing",
                "There are still active operations running:\n\n" +
                "\n".join([f"- {feature.value}: {count} active"
                          for feature, count in active_threads.items() if count > 0]) +
                "\n\nDo you want to cancel all operations and exit?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.No:
                event.ignore()
                return

            # User confirmed, wait for threads to finish
            main_window.statusBar().showMessage(tr("window_settings.status_canceling"))
            if not thread_manager.wait_all_threads(timeout_ms=5000):
                # Some threads didn't finish in time
                reply = QMessageBox.critical(
                    main_window,
                    "Force Close",
                    "Some operations did not finish in time.\n\n"
                    "Force close application? (may cause data loss)",
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.No:
                    thread_manager.resume_registration()
                    event.ignore()
                    return

                from ..ui import FeatureType

                cooperative_only = (
                    FeatureType.FILE_EXPLORER,
                    FeatureType.GOOGLE_TRANSLATE,
                    FeatureType.INSERT,
                    FeatureType.SEARCH_REPLACE,
                    FeatureType.TEXT_EXTRACTOR,
                )
                if any(
                    thread_manager.is_feature_running(feature)
                    for feature in cooperative_only
                ):
                    thread_manager.resume_registration()
                    event.ignore()
                    return
                # Force cleanup applies only after protected writers have stopped.
                thread_manager.force_cleanup()

        # Normal exit confirmation
        if main_window.settings.get("confirm_on_exit", True):
            # Create custom message box with checkbox
            msg_box = QMessageBox(main_window)
            msg_box.setWindowTitle(tr("dialog.exit.title"))
            msg_box.setText(tr("dialog.exit.message"))
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            msg_box.setIcon(QMessageBox.Question)

            # Add checkbox "Don't show this message again"
            checkbox = QCheckBox(tr("dialog.exit.dont_show_again"))
            msg_box.setCheckBox(checkbox)

            reply = msg_box.exec()

            # Save preference if checkbox is checked
            if checkbox.isChecked():
                main_window.settings.set("confirm_on_exit", False)
                main_window.settings.save()

            if reply == QMessageBox.Yes:
                WindowSettings.save_geometry(main_window)
                event.accept()
            else:
                thread_manager.resume_registration()
                event.ignore()
        else:
            WindowSettings.save_geometry(main_window)
            event.accept()
