#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Settings Manager for Clarify Application

Handles persistent application settings like theme, language, recent files, etc.
v2.9.33 - Added keyboard shortcuts customization support
"""

import json
import os
from pathlib import Path
from typing import Any, Optional, Dict

from .utils.logger import get_logger

logger = get_logger(__name__)


class SettingsManager:
    """Manages application settings with persistence."""

    # Default settings
    DEFAULTS = {
        "theme": "system",  # system, light, dark
        "language": "en",
        "recent_files": [],
        "max_recent_files": 10,
        "window_geometry": None,
        "last_directory": str(Path.home()),
        "auto_save": True,
        "show_tooltips": True,
        "confirm_on_exit": True,
        "ai_provider": "OpenAI (ChatGPT)",
        "remember_api_keys": False,  # For security, default False
        "default_extensions": ".txt,.py,.js,.ts,.jsx,.tsx",
        "custom_shortcuts": {},  # v2.9.33 - Keyboard shortcuts customization
    }

    def __init__(self, config_file: Optional[str] = None):
        """Initialize settings manager."""
        if config_file is None:
            self.config_file = Path.home() / '.clarify_settings.json'
        else:
            self.config_file = Path(config_file)

        self.settings = self.DEFAULTS.copy()
        self.load()

    def load(self) -> None:
        """Load settings from disk."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults (in case new settings were added)
                    self.settings.update(loaded)
            except Exception as e:  # pylint: disable=broad-exception-caught  # Robustness - keep defaults on error
                logger.warning(f"Failed to load settings: {e}")
                # Keep defaults on error

    def save(self) -> None:
        """Save settings to disk."""
        try:
            # Create directory if needed
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:  # pylint: disable=broad-exception-caught  # Robustness - fail gracefully
            logger.error(f"Failed to save settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting value and save."""
        self.settings[key] = value
        self.save()

    def add_recent_file(self, file_path: str) -> None:
        """Add a file to recent files list."""
        recent = self.get("recent_files", [])

        # Remove if already in list
        if file_path in recent:
            recent.remove(file_path)

        # Add to beginning
        recent.insert(0, file_path)

        # Limit size
        max_files = self.get("max_recent_files", 10)
        recent = recent[:max_files]

        self.set("recent_files", recent)

    def get_recent_files(self) -> list:
        """Get list of recent files (only existing ones)."""
        recent = self.get("recent_files", [])
        # Filter out non-existent files
        existing = [f for f in recent if os.path.exists(f)]

        # Update list if some files were removed
        if len(existing) != len(recent):
            self.set("recent_files", existing)

        return existing

    def clear_recent_files(self) -> None:
        """Clear recent files list."""
        self.set("recent_files", [])

    def get_custom_shortcuts(self) -> Dict[str, str]:
        """Get custom keyboard shortcuts (v2.9.33)."""
        return self.get("custom_shortcuts", {})

    def set_custom_shortcuts(self, shortcuts: Dict[str, str]) -> None:
        """Set custom keyboard shortcuts (v2.9.33)."""
        self.set("custom_shortcuts", shortcuts)

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.settings = self.DEFAULTS.copy()
        self.save()

    def get_all(self) -> dict:
        """Get all settings."""
        return self.settings.copy()

    def update_multiple(self, settings_dict: dict) -> None:
        """Update multiple settings at once."""
        self.settings.update(settings_dict)
        self.save()


# Global settings instance
_settings_instance: Optional[SettingsManager] = None  # pylint: disable=invalid-name


def get_settings() -> SettingsManager:
    """Get global settings instance."""
    global _settings_instance  # pylint: disable=global-statement  # Singleton pattern
    if _settings_instance is None:
        _settings_instance = SettingsManager()
    return _settings_instance


def reset_settings_instance():
    """Reset global instance (useful for testing)."""
    global _settings_instance  # pylint: disable=global-statement  # Singleton pattern
    _settings_instance = None
