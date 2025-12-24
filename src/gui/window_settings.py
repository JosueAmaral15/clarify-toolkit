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

from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict

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
        theme_mode = main_window.settings.get("theme", "system")
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
        saved_opacity = int(main_window.settings.get("window_opacity", 100))
        opacity = saved_opacity / 100.0
        main_window.setWindowOpacity(opacity)
        
        # Apply to all existing docks
        WindowSettings._apply_opacity_to_docks(main_window, opacity)
    
    @staticmethod
    def _apply_opacity_to_docks(main_window, opacity: float) -> None:
        """Apply opacity to all existing docks."""
        dock_names = [
            'dock_translate', 'dock_rewriter', 'dock_text_extractor',
            'dock_placeholder_replacer', 'dock_ai_processor',
            'dock_json_search', 'dock_case_converter', 'dock_history'
        ]
        for dock_name in dock_names:
            if hasattr(main_window, dock_name):
                getattr(main_window, dock_name).setWindowOpacity(opacity)
    
    @staticmethod
    def restore_prefs(main_window) -> None:
        """
        Restore preferences (theme) from config file.
        
        Args:
            main_window: MainWindow instance
        """
        from ..translators import load_translation_dict  # Import from helpers
        from ..theme_manager import ThemeManager
        from PySide6.QtWidgets import QApplication
        
        # Note: load_prefs is now in translators.json_translate_helpers
        # This is a simplified version that loads theme only
        try:
            from configparser import ConfigParser
            from pathlib import Path
            import os
            
            cfg = ConfigParser()
            config_path = Path.home() / ".clarify" / "preferences.ini"
            if config_path.exists():
                cfg.read(config_path)
                mode = cfg.get("THEME", "mode", fallback="system")
            else:
                mode = "system"
        except Exception:
            mode = "system"
        
        # Apply theme
        if mode == "light":
            main_window.act_theme_light.setChecked(True)
        elif mode == "dark":
            main_window.act_theme_dark.setChecked(True)
        else:
            main_window.act_theme_system.setChecked(True)
        ThemeManager.apply_theme(QApplication.instance(), mode)
    
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
        from PySide6.QtWidgets import QMessageBox
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
            main_window.statusBar().showMessage("Canceling active operations...")
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
                    event.ignore()
                    return
                
                # Force cleanup
                thread_manager.force_cleanup()
        
        # Normal exit confirmation
        if main_window.settings.get("confirm_on_exit", True):
            reply = QMessageBox.question(
                main_window,
                "Exit Clarify",
                "Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                WindowSettings.save_geometry(main_window)
                event.accept()
            else:
                event.ignore()
        else:
            WindowSettings.save_geometry(main_window)
            event.accept()
