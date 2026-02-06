#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Theme Manager for Clarify
--------------------------
Manages application themes: Light, Dark, and System.
Provides consistent styling across all components.

Author: Josué Amaral
Date: 2025/11/28
Version: 2.9.4
"""

from typing import Literal

# pylint: disable=no-name-in-module  # Qt dynamic imports
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

ThemeMode = Literal["system", "light", "dark"]


class ThemeManager:
    """Manages application theming with light, dark, and system modes."""

    @staticmethod
    def apply_theme(app: QApplication, mode: ThemeMode):
        """
        Apply the specified theme to the application.

        Args:
            app: QApplication instance
            mode: "system", "light", or "dark"
        """
        if mode == "light":
            ThemeManager._apply_light_theme(app)
        elif mode == "dark":
            ThemeManager._apply_dark_theme(app)
        else:  # system
            ThemeManager._apply_system_theme(app)

    @staticmethod
    def _apply_system_theme(app: QApplication):
        """Apply system default theme (Fusion style with system palette)."""
        app.setStyle("Fusion")
        app.setPalette(app.style().standardPalette())
        app.setStyleSheet("")  # Clear custom styles

    @staticmethod
    def _apply_light_theme(app: QApplication):
        """Apply light theme with clean, professional colors."""
        app.setStyle("Fusion")

        # Create light palette
        palette = QPalette()

        # Base colors
        palette.setColor(QPalette.Window, QColor(250, 250, 250))
        palette.setColor(QPalette.WindowText, QColor(30, 30, 30))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(30, 30, 30))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(30, 30, 30))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))

        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

        # Disabled colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(150, 150, 150))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(150, 150, 150))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(150, 150, 150))
        palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(200, 200, 200))

        # Link colors
        palette.setColor(QPalette.Link, QColor(0, 100, 200))
        palette.setColor(QPalette.LinkVisited, QColor(150, 50, 150))

        app.setPalette(palette)

        # Apply stylesheet for additional styling
        stylesheet = """
            /* GroupBox styling */
            QGroupBox {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #1e1e1e;
            }
            
            /* Input fields */
            QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox {
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                padding: 3px;
                background-color: #ffffff;
                selection-background-color: #0078d7;
            }
            QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QSpinBox:focus {
                border: 2px solid #0078d7;
            }
            
            /* Buttons */
            QPushButton {
                border: 1px solid #b0b0b0;
                border-radius: 3px;
                padding: 5px 15px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #0078d7;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #a0a0a0;
            }
            
            /* Checkboxes and Radio buttons */
            QCheckBox::indicator, QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #b0b0b0;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background-color: #0078d7;
                border-color: #0078d7;
            }
            
            /* ComboBox */
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                padding: 3px;
                background-color: #ffffff;
            }
            QComboBox:hover {
                border-color: #0078d7;
            }
            QComboBox::drop-down {
                border: none;
            }
            
            /* TabWidget */
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                border-radius: 3px;
            }
            QTabBar::tab {
                border: 1px solid #d0d0d0;
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                padding: 5px 15px;
                background-color: #f0f0f0;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 1px solid #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #e5f1fb;
            }
            
            /* TreeView / ListView */
            QTreeView, QListView {
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                background-color: #ffffff;
                selection-background-color: #0078d7;
            }
            QTreeView::item:hover, QListView::item:hover {
                background-color: #e5f1fb;
            }
            
            /* Scrollbar */
            QScrollBar:vertical {
                border: none;
                background-color: #f0f0f0;
                width: 12px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar:horizontal {
                border: none;
                background-color: #f0f0f0;
                height: 12px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #a0a0a0;
            }
            
            /* MenuBar */
            QMenuBar {
                background-color: #f8f8f8;
                border-bottom: 1px solid #d0d0d0;
            }
            QMenuBar::item {
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #e5f1fb;
            }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
            }
            QMenu::item:selected {
                background-color: #e5f1fb;
            }
            
            /* StatusBar */
            QStatusBar {
                background-color: #f0f0f0;
                border-top: 1px solid #d0d0d0;
            }
            
            /* DockWidget */
            QDockWidget {
                border: 1px solid #d0d0d0;
            }
            QDockWidget::title {
                background-color: #f0f0f0;
                padding: 5px;
            }
            
            /* CollapsibleSection (File Explorer) */
            QPushButton[objectName="collapsible_header"] {
                background-color: #3498db;
                color: white;
                text-align: left;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton[objectName="collapsible_header"]:hover {
                background-color: #2980b9;
            }
            QPushButton[objectName="collapsible_header"]:checked {
                background-color: #2c3e50;
            }
            QFrame[objectName="collapsible_content"] {
                border: 1px solid #d0d0d0;
                border-top: none;
                border-radius: 0 0 4px 4px;
                background-color: #ffffff;
            }
        """
        app.setStyleSheet(stylesheet)

    @staticmethod
    def _apply_dark_theme(app: QApplication):
        """Apply dark theme with modern, eye-friendly colors."""
        app.setStyle("Fusion")

        # Create dark palette
        palette = QPalette()

        # Base colors
        palette.setColor(QPalette.Window, QColor(45, 45, 48))
        palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        palette.setColor(QPalette.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
        palette.setColor(QPalette.ToolTipBase, QColor(60, 60, 60))
        palette.setColor(QPalette.ToolTipText, QColor(240, 240, 240))
        palette.setColor(QPalette.Text, QColor(240, 240, 240))
        palette.setColor(QPalette.Button, QColor(60, 60, 60))
        palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))

        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(0, 122, 204))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

        # Disabled colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(100, 100, 100))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(100, 100, 100))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(100, 100, 100))
        palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(70, 70, 70))

        # Link colors
        palette.setColor(QPalette.Link, QColor(100, 180, 255))
        palette.setColor(QPalette.LinkVisited, QColor(200, 120, 200))

        app.setPalette(palette)

        # Apply stylesheet for additional styling
        stylesheet = """
            /* GroupBox styling */
            QGroupBox {
                border: 1px solid #505050;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #f0f0f0;
            }
            
            /* Input fields */
            QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox {
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 3px;
                background-color: #1e1e1e;
                color: #f0f0f0;
                selection-background-color: #007acc;
            }
            QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QSpinBox:focus {
                border: 2px solid #007acc;
            }
            
            /* Buttons */
            QPushButton {
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 5px 15px;
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
                border-color: #007acc;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #646464;
            }
            
            /* Checkboxes and Radio buttons */
            QCheckBox::indicator, QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #505050;
                border-radius: 3px;
                background-color: #1e1e1e;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background-color: #007acc;
                border-color: #007acc;
            }
            
            /* ComboBox */
            QComboBox {
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 3px;
                background-color: #1e1e1e;
                color: #f0f0f0;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d30;
                border: 1px solid #505050;
                selection-background-color: #007acc;
            }
            
            /* TabWidget */
            QTabWidget::pane {
                border: 1px solid #505050;
                border-radius: 3px;
            }
            QTabBar::tab {
                border: 1px solid #505050;
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                padding: 5px 15px;
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QTabBar::tab:selected {
                background-color: #2d2d30;
                border-bottom: 1px solid #2d2d30;
            }
            QTabBar::tab:hover {
                background-color: #4c4c4c;
            }
            
            /* TreeView / ListView */
            QTreeView, QListView {
                border: 1px solid #505050;
                border-radius: 3px;
                background-color: #1e1e1e;
                color: #f0f0f0;
                selection-background-color: #007acc;
            }
            QTreeView::item:hover, QListView::item:hover {
                background-color: #3c3c3c;
            }
            
            /* Scrollbar */
            QScrollBar:vertical {
                border: none;
                background-color: #2d2d30;
                width: 12px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #686868;
            }
            QScrollBar:horizontal {
                border: none;
                background-color: #2d2d30;
                height: 12px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background-color: #555555;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #686868;
            }
            
            /* MenuBar */
            QMenuBar {
                background-color: #3c3c3c;
                border-bottom: 1px solid #505050;
                color: #f0f0f0;
            }
            QMenuBar::item {
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #4c4c4c;
            }
            QMenu {
                background-color: #2d2d30;
                border: 1px solid #505050;
                color: #f0f0f0;
            }
            QMenu::item:selected {
                background-color: #4c4c4c;
            }
            
            /* StatusBar */
            QStatusBar {
                background-color: #007acc;
                border-top: 1px solid #505050;
                color: #ffffff;
            }
            
            /* DockWidget */
            QDockWidget {
                border: 1px solid #505050;
                color: #f0f0f0;
            }
            QDockWidget::title {
                background-color: #3c3c3c;
                padding: 5px;
            }
            
            /* CollapsibleSection (File Explorer) - DARK THEME */
            QPushButton[objectName="collapsible_header"] {
                background-color: #3498db;
                color: white;
                text-align: left;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton[objectName="collapsible_header"]:hover {
                background-color: #2980b9;
            }
            QPushButton[objectName="collapsible_header"]:checked {
                background-color: #2c3e50;
            }
            QFrame[objectName="collapsible_content"] {
                border: 1px solid #505050;
                border-top: none;
                border-radius: 0 0 4px 4px;
                background-color: #2d2d30;
            }
        """
        app.setStyleSheet(stylesheet)
