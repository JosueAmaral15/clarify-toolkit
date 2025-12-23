#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin Base Class - API for Clarify Plugins

Defines the interface for creating custom Clarify plugins with:
- Lifecycle hooks (activate, deactivate)
- Event hooks (file_opened, search_completed, etc)
- UI integration (register_dock, add_menu_item)
- Settings access

Author: Josué Amaral
Date: 2025-12-23
Version: 2.9.109
"""

from typing import Any, Dict, Optional, Callable
from PySide6.QtWidgets import QAction, QDockWidget, QMenu
from PySide6.QtCore import QSettings


class PluginBase:
    """
    Base class for Clarify plugins.
    
    All plugins must inherit from this class and implement at least the `activate` method.
    
    Plugin Structure:
        plugins/
          my_plugin/
            plugin.json     # Metadata
            main.py         # Entry point (inherits PluginBase)
            requirements.txt # Optional dependencies
            README.md       # Documentation
    
    plugin.json format:
        {
          "id": "my_plugin",
          "name": "My Plugin",
          "version": "1.0.0",
          "description": "Description of my plugin",
          "author": "Author Name",
          "entry_point": "main.py",
          "dependencies": ["requests", "psycopg2"],
          "enabled": true
        }
    
    Example Plugin:
        class MyPlugin(PluginBase):
            name = "My Plugin"
            description = "Example plugin"
            
            def activate(self, app):
                # Register menu item
                self.add_menu_item(
                    app, 
                    menu_path="Tools/My Plugin",
                    text="Run Action",
                    callback=self.run_action
                )
                
            def run_action(self):
                print("Action executed!")
                
            def on_event(self, event_name, data):
                if event_name == "file_opened":
                    print(f"File opened: {data['path']}")
    """
    
    # Plugin metadata (override in subclass)
    name = "Base Plugin"
    description = "Base class for Clarify plugins"
    version = "0.0.0"
    
    def __init__(self):
        """Initialize plugin."""
        self.app = None  # Will be set during activation
        self.settings = QSettings("Clarify", "Clarify")
        self._registered_docks = []
        self._registered_actions = []
    
    def activate(self, app):
        """
        Activate the plugin (called when plugin is loaded).
        
        Args:
            app: Main application instance (MainWindow)
        
        This method MUST be implemented by subclasses.
        Use this to:
        - Register custom docks
        - Add menu items
        - Connect to signals
        - Initialize resources
        """
        self.app = app
        raise NotImplementedError(f"{self.__class__.__name__} must implement activate()")
    
    def deactivate(self, app):
        """
        Deactivate the plugin (called when plugin is unloaded).
        
        Args:
            app: Main application instance
        
        Optional method for cleanup:
        - Remove menu items
        - Disconnect signals
        - Close resources
        """
        # Default: remove registered UI elements
        for action in self._registered_actions:
            try:
                action.deleteLater()
            except:
                pass
        
        for dock in self._registered_docks:
            try:
                dock.deleteLater()
            except:
                pass
        
        self._registered_actions.clear()
        self._registered_docks.clear()
    
    def on_event(self, event_name: str, data: Dict[str, Any]):
        """
        Handle application events.
        
        Args:
            event_name: Event identifier
            data: Event data dictionary
        
        Common events:
        - file_opened: {"path": str}
        - file_saved: {"path": str}
        - search_completed: {"query": str, "results": list}
        - rewrite_completed: {"input_path": str, "output_path": str}
        - ai_request_completed: {"prompt": str, "response": str}
        """
        pass
    
    # Helper methods for UI integration
    
    def register_dock(self, app, dock: QDockWidget, area: str = "right"):
        """
        Register a custom dock widget.
        
        Args:
            app: Application instance
            dock: QDockWidget to register
            area: Dock area ("left", "right", "top", "bottom")
        """
        from PySide6.QtCore import Qt
        
        area_map = {
            "left": Qt.LeftDockWidgetArea,
            "right": Qt.RightDockWidgetArea,
            "top": Qt.TopDockWidgetArea,
            "bottom": Qt.BottomDockWidgetArea
        }
        
        qt_area = area_map.get(area, Qt.RightDockWidgetArea)
        app.addDockWidget(qt_area, dock)
        self._registered_docks.append(dock)
    
    def add_menu_item(
        self, 
        app, 
        menu_path: str, 
        text: str, 
        callback: Callable,
        shortcut: Optional[str] = None
    ) -> QAction:
        """
        Add a menu item to the application.
        
        Args:
            app: Application instance
            menu_path: Menu path (e.g., "Tools/My Plugin")
            text: Action text
            callback: Function to call when triggered
            shortcut: Optional keyboard shortcut
            
        Returns:
            Created QAction
        """
        menu_bar = app.menuBar()
        parts = menu_path.split("/")
        
        # Navigate/create menu hierarchy
        current_menu = None
        for part in parts:
            if current_menu is None:
                # Find or create top-level menu
                for action in menu_bar.actions():
                    if action.text() == part:
                        current_menu = action.menu()
                        break
                if current_menu is None:
                    current_menu = menu_bar.addMenu(part)
            else:
                # Find or create submenu
                found = False
                for action in current_menu.actions():
                    if action.text() == part and action.menu():
                        current_menu = action.menu()
                        found = True
                        break
                if not found:
                    current_menu = current_menu.addMenu(part)
        
        # Create action
        action = QAction(text, app)
        action.triggered.connect(callback)
        if shortcut:
            action.setShortcut(shortcut)
        
        if current_menu:
            current_menu.addAction(action)
        
        self._registered_actions.append(action)
        return action
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a plugin-specific setting.
        
        Args:
            key: Setting key (will be prefixed with plugin name)
            default: Default value if not found
            
        Returns:
            Setting value
        """
        plugin_key = f"plugins/{self.name}/{key}"
        return self.settings.value(plugin_key, default)
    
    def set_setting(self, key: str, value: Any):
        """
        Save a plugin-specific setting.
        
        Args:
            key: Setting key (will be prefixed with plugin name)
            value: Value to save
        """
        plugin_key = f"plugins/{self.name}/{key}"
        self.settings.setValue(plugin_key, value)
    
    def show_message(self, title: str, message: str, icon: str = "information"):
        """
        Show a message box to the user.
        
        Args:
            title: Dialog title
            message: Message text
            icon: Icon type ("information", "warning", "critical", "question")
        """
        from PySide6.QtWidgets import QMessageBox
        
        icon_map = {
            "information": QMessageBox.Information,
            "warning": QMessageBox.Warning,
            "critical": QMessageBox.Critical,
            "question": QMessageBox.Question
        }
        
        msg_box = QMessageBox(self.app)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon_map.get(icon, QMessageBox.Information))
        msg_box.exec()
