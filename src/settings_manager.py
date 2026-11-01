#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Settings Manager for Clarify Application

Handles persistent application settings like theme, language, recent files, etc.
v2.9.33 - Added keyboard shortcuts customization support
"""

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Optional, Dict

from .appearance_defaults import DEFAULT_THEME, DEFAULT_WINDOW_OPACITY_PERCENT
from .utils.atomic_files import write_text_atomically
from .utils.logger import get_logger

logger = get_logger(__name__)


class SettingsManager:
    """Manages application settings with persistence."""

    # Default settings
    DEFAULTS = {
        "theme": DEFAULT_THEME,  # system, light, dark
        "window_opacity": DEFAULT_WINDOW_OPACITY_PERCENT,
        "language": "en",
        "recent_files": [],
        "max_recent_files": 10,
        "window_geometry": None,
        "last_directory": str(Path.home()),
        "auto_save": True,
        "completion_sound": False,
        "show_tooltips": True,
        "confirm_on_exit": True,
        "ai_provider": "OpenAI (ChatGPT)",
        "remember_api_keys": False,  # For security, default False
        "default_extensions": ".txt,.py,.js,.ts,.jsx,.tsx",
        "custom_shortcuts": {},  # v2.9.33 - Keyboard shortcuts customization
    }

    # State and user-data keys intentionally excluded: recent_files,
    # window_geometry, last_directory, and any unknown session keys.
    RESETTABLE_KEYS = frozenset({
        "theme", "window_opacity", "language", "max_recent_files",
        "auto_save", "completion_sound", "show_tooltips", "confirm_on_exit",
        "ai_provider", "remember_api_keys", "default_extensions",
        "custom_shortcuts",
    })

    def __init__(self, config_file: Optional[str] = None):
        """Initialize settings manager."""
        if config_file is None:
            self.config_file = Path(
                os.environ.get("CLARIFY_SETTINGS_FILE", str(Path.home() / '.clarify_settings.json'))
            ).expanduser()
        else:
            self.config_file = Path(config_file)

        self._stored_keys: set[str] = set()
        self.settings = deepcopy(self.DEFAULTS)
        self.load()

    def load(self) -> None:
        """Load settings from disk."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    if not isinstance(loaded, dict):
                        raise ValueError("Settings root must be a JSON object")
                    # Merge with defaults (in case new settings were added)
                    self._stored_keys.update(loaded)
                    self.settings.update(loaded)
            except Exception as e:  # pylint: disable=broad-exception-caught  # Robustness - keep defaults on error
                logger.warning(f"Failed to load settings: {e}")
                # Keep defaults on error

    def save(self, *, raise_on_error: bool = False) -> bool:
        """Save settings atomically and report whether persistence succeeded."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            content = json.dumps(self.settings, indent=2, ensure_ascii=False) + "\n"
            write_text_atomically(self.config_file, content)
            return True
        except Exception as e:  # pylint: disable=broad-exception-caught  # Robustness - fail gracefully
            logger.error(f"Failed to save settings: {e}")
            if raise_on_error:
                raise
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)

    def has_saved_value(self, key: str) -> bool:
        """Return whether a key came from, or was written to, persistent settings."""
        return key in self._stored_keys

    def set(self, key: str, value: Any) -> None:
        """Set a setting value and save."""
        self.settings[key] = value
        self._stored_keys.add(key)
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
        """Reset preferences while retaining user data and session state."""
        for key in self.RESETTABLE_KEYS:
            self.settings[key] = deepcopy(self.DEFAULTS[key])
        self._stored_keys.update(self.RESETTABLE_KEYS)
        self.save()

    def get_all(self) -> dict:
        """Get all settings."""
        return self.settings.copy()

    def update_multiple(self, settings_dict: dict) -> None:
        """Update multiple settings at once."""
        self.settings.update(settings_dict)
        self._stored_keys.update(settings_dict)
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
