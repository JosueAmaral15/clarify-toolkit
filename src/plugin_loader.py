# pylint: disable=no-name-in-module  # PySide6 uses dynamic module structure
# pylint: disable=broad-exception-caught  # Plugin loader must handle all errors gracefully
# pylint: disable=too-few-public-methods  # PluginMetadata is a simple data class

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin Loader - Dynamic Plugin System for Clarify

Discovers, loads, and manages plugins with:
- Metadata from plugin.json
- Event hooks (file_opened, search_completed, etc)
- Custom dock registration
- Menu item integration
- Settings persistence via QSettings

Author: Josué Amaral
Date: 2025-12-23
Version: 2.9.109
"""

import importlib.util
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from PySide6.QtCore import QObject, Signal, QSettings



from .utils.logger import get_logger
from .plugins.plugin_base import PluginBase

logger = get_logger(__name__)

class PluginMetadata:
    """Metadata from plugin.json file."""

    def __init__(self, data: dict, plugin_dir: Path):
        self.id = data.get("id", "")
        self.name = data.get("name", "Unknown Plugin")
        self.version = data.get("version", "0.0.0")
        self.description = data.get("description", "")
        self.author = data.get("author", "Unknown")
        self.entry_point = data.get("entry_point", "main.py")
        self.dependencies = data.get("dependencies", [])
        self.enabled = data.get("enabled", True)
        self.plugin_dir = plugin_dir

    def __repr__(self):
        return f"<PluginMetadata {self.id} v{self.version}>"


class PluginLoader(QObject):
    """
    Plugin loader with discovery, loading, and lifecycle management.

    Features:
    - Auto-discovery from plugins/ folder
    - Metadata validation (plugin.json)
    - Event hook system
    - QSettings integration (enable/disable)
    - Error handling and logging

    Example:
        >>> loader = PluginLoader(app)
        >>> loader.discover_plugins()
        >>> loader.activate_all_plugins()
        >>> loader.emit_event("file_opened", {"path": "data.json"})
    """

    # Signals for plugin communication
    plugin_loaded = Signal(str)  # plugin_id
    plugin_activated = Signal(str)  # plugin_id
    plugin_error = Signal(str, str)  # plugin_id, error_message

    def __init__(self, app):
        """
        Initialize plugin loader.

        Args:
            app: Main application instance (MainWindow)
        """
        super().__init__()
        self.app = app
        self.plugins: Dict[str, Any] = {}  # plugin_id -> plugin_instance
        self.metadata: Dict[str, PluginMetadata] = {}  # plugin_id -> metadata
        self.settings = QSettings("Clarify", "Clarify")

        # Default plugin directory
        self.plugin_dir = Path(__file__).parent.parent / "plugins"
        self.plugin_dir.mkdir(exist_ok=True)

    def discover_plugins(self) -> List[PluginMetadata]:
        """
        Discover all plugins in plugins/ directory.

        Returns:
            List of discovered plugin metadata
        """
        discovered = []

        if not self.plugin_dir.exists():
            return discovered

        for item in self.plugin_dir.iterdir():
            if not item.is_dir():
                continue

            # Check for plugin.json
            metadata_file = item / "plugin.json"
            if not metadata_file.exists():
                continue

            try:
                # Load metadata
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                metadata = PluginMetadata(data, item)

                # Check if enabled in settings
                enabled = self.settings.value(
                    f"plugins/{metadata.id}/enabled",
                    metadata.enabled,
                    type=bool
                )
                metadata.enabled = enabled

                self.metadata[metadata.id] = metadata
                discovered.append(metadata)

            except Exception as e:
                logger.error(f"[PluginLoader] Failed to load metadata from {item}: {e}")

        return discovered

    def load_plugin(self, plugin_id: str) -> Optional[Any]:
        """
        Load a plugin by ID.

        Args:
            plugin_id: Unique plugin identifier

        Returns:
            Plugin instance or None if failed
        """
        if plugin_id not in self.metadata:
            return None

        metadata = self.metadata[plugin_id]

        # Check if already loaded
        if plugin_id in self.plugins:
            return self.plugins[plugin_id]

        try:
            # Load module
            entry_path = metadata.plugin_dir / metadata.entry_point
            if not entry_path.exists():
                raise FileNotFoundError(f"Entry point not found: {entry_path}")

            spec = importlib.util.spec_from_file_location(
                f"clarify_plugin_{plugin_id}",
                str(entry_path)
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"Failed to create module spec for {plugin_id}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # Find plugin class (must inherit from PluginBase)
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, PluginBase) and
                    attr is not PluginBase):
                    plugin_class = attr
                    break

            if plugin_class is None:
                raise ValueError(f"No PluginBase subclass found in {metadata.entry_point}")

            # Instantiate plugin
            plugin_instance = plugin_class()
            self.plugins[plugin_id] = plugin_instance

            self.plugin_loaded.emit(plugin_id)
            return plugin_instance

        except Exception as e:
            error_msg = f"Failed to load plugin {plugin_id}: {e}"
            logger.error(f"[PluginLoader] {error_msg}")
            self.plugin_error.emit(plugin_id, error_msg)
            return None

    def activate_plugin(self, plugin_id: str) -> bool:
        """
        Activate a loaded plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if activation succeeded
        """
        # Load if not already loaded
        plugin = self.plugins.get(plugin_id) or self.load_plugin(plugin_id)
        if plugin is None:
            return False

        metadata = self.metadata.get(plugin_id)
        if not metadata or not metadata.enabled:
            return False

        try:
            # Call activate with app context
            plugin.activate(self.app)
            self.plugin_activated.emit(plugin_id)
            return True

        except Exception as e:
            error_msg = f"Failed to activate plugin {plugin_id}: {e}"
            logger.error(f"[PluginLoader] {error_msg}")
            self.plugin_error.emit(plugin_id, error_msg)
            return False

    def activate_all_plugins(self) -> int:
        """
        Activate all enabled plugins.

        Returns:
            Number of successfully activated plugins
        """
        count = 0
        for plugin_id, metadata in self.metadata.items():
            if metadata.enabled:
                if self.activate_plugin(plugin_id):
                    count += 1
        return count

    def deactivate_plugin(self, plugin_id: str) -> bool:
        """
        Deactivate a plugin (if it supports deactivation).

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if deactivation succeeded
        """
        plugin = self.plugins.get(plugin_id)
        if plugin is None:
            return False

        try:
            if hasattr(plugin, 'deactivate'):
                plugin.deactivate(self.app)
            return True
        except Exception as e:
            logger.error(f"[PluginLoader] Failed to deactivate {plugin_id}: {e}")
            return False

    def enable_plugin(self, plugin_id: str, enabled: bool = True):
        """
        Enable or disable a plugin in settings.

        Args:
            plugin_id: Plugin identifier
            enabled: Enable (True) or disable (False)
        """
        self.settings.setValue(f"plugins/{plugin_id}/enabled", enabled)

        if plugin_id in self.metadata:
            self.metadata[plugin_id].enabled = enabled

    def set_plugin_enabled(self, plugin_id: str, enabled: bool) -> bool:
        """Keep persisted and displayed state unchanged when a transition fails."""
        metadata = self.metadata.get(plugin_id)
        if metadata is None:
            return False
        previous = metadata.enabled
        if previous == enabled:
            return True
        self.enable_plugin(plugin_id, enabled)
        success = (self.activate_plugin(plugin_id) if enabled else
                   plugin_id not in self.plugins or self.deactivate_plugin(plugin_id))
        if not success:
            self.enable_plugin(plugin_id, previous)
        return bool(success)

    def emit_event(self, event_name: str, data: Dict[str, Any]):
        """
        Emit an event to all active plugins.

        Args:
            event_name: Event identifier (e.g., "file_opened", "search_completed")
            data: Event data dictionary
        """
        for plugin_id, plugin in self.plugins.items():
            metadata = self.metadata.get(plugin_id)
            if metadata and metadata.enabled:
                try:
                    if hasattr(plugin, 'on_event'):
                        plugin.on_event(event_name, data)
                except Exception as e:
                    logger.error(f"[PluginLoader] Plugin {plugin_id} event handler error: {e}")

    def get_plugin(self, plugin_id: str) -> Optional[Any]:
        """Get a loaded plugin instance by ID."""
        return self.plugins.get(plugin_id)

    def get_all_metadata(self) -> List[PluginMetadata]:
        """Get metadata for all discovered plugins."""
        return list(self.metadata.values())

    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin from memory.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if unload succeeded
        """
        if plugin_id not in self.plugins:
            return False

        try:
            # Deactivate first
            self.deactivate_plugin(plugin_id)

            # Remove from loaded plugins
            del self.plugins[plugin_id]
            return True

        except Exception as e:
            logger.error(f"[PluginLoader] Failed to unload {plugin_id}: {e}")
            return False
