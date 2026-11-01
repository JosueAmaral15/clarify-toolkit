#!/usr/bin/env python3
"""
Configuration Manager for Clarify Application - Sprint v2.9.60

Centralized configuration management with YAML support, validation, and migration.
Provides a single source of truth for all application settings.

Features:
- YAML-based configuration (config.yaml)
- JSON Schema validation
- Automatic migration from QSettings/JSON
- Backup before overwrites
- Priority: CLI args > config.yaml > defaults
- Thread-safe operations
"""
# pylint: disable=logging-fstring-interpolation  # F-strings clearer

import json
import shutil
from copy import deepcopy
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .utils.logger import get_logger
from .utils.atomic_files import write_text_atomically
from .appearance_defaults import DEFAULT_THEME, DEFAULT_WINDOW_OPACITY_PERCENT

logger = get_logger(__name__)

try:
    from PySide6.QtCore import QSettings
    HAS_QT = True
except ImportError:
    HAS_QT = False


class ConfigManager:
    """
    Centralized configuration manager with YAML storage and validation.

    Usage:
        config = ConfigManager()
        theme = config.get("app.theme", "system")
        config.set("app.theme", "dark")
        config.save()
    """

    # Default configuration structure
    DEFAULTS = {
        "app": {
            "theme": DEFAULT_THEME,  # system | light | dark
            "window_opacity": DEFAULT_WINDOW_OPACITY_PERCENT,
            "language": "en",  # en | pt-br | es | fr | de | zh | ja
            "max_recent_files": 10,
            "confirm_on_exit": True,
            "show_tooltips": True,
            "auto_save": True,
            "check_updates_on_startup": True,
        },
        "logging": {
            "level": "INFO",  # DEBUG | INFO | WARNING | ERROR | CRITICAL
            "max_file_size_mb": 10,
            "backup_count": 5,
            "console_output": True,
        },
        "performance": {
            "thread_pool_size": 4,
            "max_file_size_mb": 50,
            "cache_duration_hours": 24,
            "batch_size": 100,
        },
        "ai": {
            "default_provider": "OpenAI",  # OpenAI | Gemini
            "remember_api_keys": False,  # Security: default False
            "max_tokens": 4096,
            "temperature": 0.7,
        },
        "editor": {
            "font_family": "Consolas",
            "font_size": 12,
            "tab_width": 4,
            "auto_save_interval_sec": 60,
            "syntax_highlighting": True,
        },
        "paths": {
            "default_directory": str(Path.home()),
            "custom_extensions": ".txt,.py,.js,.ts,.jsx,.tsx,.json",
        },
    }

    # JSON Schema for validation
    SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "app": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string", "enum": ["system", "light", "dark"]},
                    "window_opacity": {"type": "integer", "minimum": 20, "maximum": 100},
                    "language": {"type": "string", "pattern": "^[a-z]{2}(-[a-z]{2})?$"},
                    "max_recent_files": {"type": "integer", "minimum": 0, "maximum": 50},
                    "confirm_on_exit": {"type": "boolean"},
                    "show_tooltips": {"type": "boolean"},
                    "auto_save": {"type": "boolean"},
                    "check_updates_on_startup": {"type": "boolean"},
                },
            },
            "logging": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                    "max_file_size_mb": {"type": "integer", "minimum": 1, "maximum": 100},
                    "backup_count": {"type": "integer", "minimum": 0, "maximum": 20},
                    "console_output": {"type": "boolean"},
                },
            },
            "performance": {
                "type": "object",
                "properties": {
                    "thread_pool_size": {"type": "integer", "minimum": 1, "maximum": 16},
                    "max_file_size_mb": {"type": "integer", "minimum": 1, "maximum": 500},
                    "cache_duration_hours": {"type": "integer", "minimum": 0, "maximum": 168},
                    "batch_size": {"type": "integer", "minimum": 10, "maximum": 1000},
                },
            },
            "ai": {
                "type": "object",
                "properties": {
                    "default_provider": {"type": "string", "enum": ["OpenAI", "Gemini"]},
                    "remember_api_keys": {"type": "boolean"},
                    "max_tokens": {"type": "integer", "minimum": 100, "maximum": 32000},
                    "temperature": {"type": "number", "minimum": 0.0, "maximum": 2.0},
                },
            },
            "editor": {
                "type": "object",
                "properties": {
                    "font_family": {"type": "string"},
                    "font_size": {"type": "integer", "minimum": 8, "maximum": 24},
                    "tab_width": {"type": "integer", "minimum": 2, "maximum": 8},
                    "auto_save_interval_sec": {"type": "integer", "minimum": 10, "maximum": 600},
                    "syntax_highlighting": {"type": "boolean"},
                },
            },
            "paths": {
                "type": "object",
                "properties": {
                    "default_directory": {"type": "string"},
                    "custom_extensions": {"type": "string"},
                },
            },
        },
    }

    def __init__(
        self,
        config_file: Optional[str] = None,
        *,
        migrate_legacy: Optional[bool] = None,
    ):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to config.yaml (default: ~/.config/clarify/config.yaml)
        """
        using_default_path = config_file is None
        if using_default_path:
            config_dir = Path.home() / ".config" / "clarify"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_file = config_dir / "config.yaml"
        else:
            self.config_file = Path(config_file)

        # Explicit paths are commonly used for tests and isolated profiles. They
        # must never inspect or move legacy files from the real HOME implicitly.
        self._migrate_legacy = using_default_path if migrate_legacy is None else migrate_legacy

        self.config: Dict[str, Any] = {}
        self._load_or_create()

    def _load_or_create(self) -> None:
        """Load config from file or create with defaults."""
        if self.config_file.exists():
            self._load()
        else:
            # First time: try migration from old formats
            migrated = self._migrate_from_legacy() if self._migrate_legacy else False
            if not migrated:
                # No legacy config, use defaults
                self.config = self._deep_copy(self.DEFAULTS)
            self.save()

    def _load(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)

            if not loaded:
                loaded = {}

            # Merge with defaults (in case new settings were added)
            self.config = self._merge_configs(self.DEFAULTS, loaded)

            # Validate
            self._validate()

        except yaml.YAMLError as e:
            logger.warning(f"Invalid YAML in {self.config_file}: {e}")
            logger.warning("Using defaults and backing up invalid file")
            self._backup_file(suffix="_invalid")
            self.config = self._deep_copy(self.DEFAULTS)
            self.save()
        except Exception as e:  # pylint: disable=broad-exception-caught  # Robustness - fallback to defaults
            logger.error(f"Error loading config: {e}")
            self.config = self._deep_copy(self.DEFAULTS)

    def _validate(self) -> None:
        """Validate configuration against schema."""
        try:
            import jsonschema  # pylint: disable=import-outside-toplevel  # Optional dependency
            jsonschema.validate(instance=self.config, schema=self.SCHEMA)
        except ImportError:
            # jsonschema not installed, skip validation
            pass
        except Exception as e:  # pylint: disable=broad-exception-caught  # Validation errors vary
            logger.warning(f"Config validation failed: {e}")
            logger.warning("Some settings may be invalid")

    def save(self, *, raise_on_error: bool = False) -> bool:
        """Save configuration atomically and report whether it succeeded."""
        try:
            # Backup existing file before overwrite
            if self.config_file.exists():
                self._backup_file()

            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            content = (
                "# Clarify Configuration File\n"
                f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                "# Edit with care or use Settings -> Advanced in the app\n\n"
                + yaml.dump(self.config, default_flow_style=False, sort_keys=False)
            )
            write_text_atomically(self.config_file, content)
            return True

        except Exception as e:  # pylint: disable=broad-exception-caught  # File write errors vary
            logger.error(f"Error saving config: {e}")
            if raise_on_error:
                raise
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Dot-separated key (e.g., "app.theme", "logging.level")
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            theme = config.get("app.theme", "system")
            font_size = config.get("editor.font_size", 12)
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any, save: bool = True) -> None:
        """
        Set configuration value using dot notation.

        Args:
            key: Dot-separated key (e.g., "app.theme")
            value: New value
            save: Whether to save immediately (default: True)

        Example:
            config.set("app.theme", "dark")
            config.set("editor.font_size", 14)
        """
        keys = key.split(".")
        target = self.config

        # Navigate to parent
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]

        # Set value
        target[keys[-1]] = value

        if save:
            self.save()

    def update(self, updates: Dict[str, Any], save: bool = True) -> None:
        """
        Update multiple settings at once.

        Args:
            updates: Dictionary with dot-notation keys
            save: Whether to save immediately

        Example:
            config.update({
                "app.theme": "dark",
                "editor.font_size": 14,
                "logging.level": "DEBUG"
            })
        """
        for key, value in updates.items():
            self.set(key, value, save=False)

        if save:
            self.save()

    def reset_to_defaults(self) -> None:
        """Reset known preferences while preserving unknown user-owned keys."""
        self._backup_file(suffix="_before_reset")
        self.config = self._reset_known_values(self.config, self.DEFAULTS)
        self.save()

    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary."""
        return self._deep_copy(self.config)

    def _merge_configs(self, defaults: Dict, loaded: Dict) -> Dict:
        """
        Merge loaded config with defaults (recursive).

        Args:
            defaults: Default configuration
            loaded: Loaded configuration

        Returns:
            Merged configuration
        """
        result = self._deep_copy(defaults)

        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def _deep_copy(self, obj: Any) -> Any:
        """Deep copy of dict/list structures."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj

    def _reset_known_values(self, current: Dict, defaults: Dict) -> Dict:
        """Overlay default leaves without deleting unknown nested keys."""
        result = deepcopy(current) if isinstance(current, dict) else {}
        for key, value in defaults.items():
            if isinstance(value, dict):
                result[key] = self._reset_known_values(result.get(key, {}), value)
            else:
                result[key] = deepcopy(value)
        return result

    def _backup_file(self, suffix: str = "") -> None:
        """
        Create backup of config file.

        Args:
            suffix: Optional suffix for backup filename
        """
        if not self.config_file.exists():
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.config_file.stem}_{timestamp}{suffix}.yaml.bak"
        backup_path = self.config_file.parent / backup_name

        try:
            shutil.copy2(self.config_file, backup_path)

            # Keep only last 5 backups
            backups = sorted(self.config_file.parent.glob("*.yaml.bak"))
            if len(backups) > 5:
                for old_backup in backups[:-5]:
                    old_backup.unlink()
        except Exception as e:  # pylint: disable=broad-exception-caught  # Backup is non-critical
            logger.warning(f"Failed to create backup: {e}")

    def _migrate_from_legacy(self) -> bool:
        """
        Migrate from legacy configuration formats.

        Supports:
        - QSettings (binary/ini format)
        - JSON (.clarify_settings.json)
        - ConfigParser (~/.config/clarify.conf)

        Returns:
            True if migration successful, False otherwise
        """
        migrated = False

        # Try QSettings first
        if HAS_QT and self._migrate_from_qsettings():
            migrated = True

        # Try JSON settings
        json_file = Path.home() / ".clarify_settings.json"
        if json_file.exists() and self._migrate_from_json(json_file):
            migrated = True

        # Try ConfigParser
        conf_file = Path.home() / ".config" / "clarify.conf"
        if conf_file.exists() and self._migrate_from_configparser(conf_file):
            migrated = True

        return migrated

    def _migrate_from_qsettings(self) -> bool:
        """Migrate from QSettings format."""
        try:
            settings = QSettings("Clarify", "ClarifyApp")

            migrated_any = False

            # Migrate app settings (only if they exist and are not None)
            if settings.contains("theme"):
                value = settings.value("theme")
                if value is not None:
                    self.set("app.theme", value, save=False)
                    migrated_any = True

            if settings.contains("language"):
                value = settings.value("language")
                if value is not None:
                    self.set("app.language", value, save=False)
                    migrated_any = True

            if settings.contains("window_opacity"):
                value = settings.value("window_opacity", type=int)
                if value is not None:
                    self.set("app.window_opacity", value, save=False)
                    migrated_any = True

            # Migrate update checker
            if settings.contains("update_checker/enabled"):
                value = settings.value("update_checker/enabled", type=bool)
                if value is not None:
                    self.set("app.check_updates_on_startup", value, save=False)
                    migrated_any = True

            if migrated_any:
                logger.info("Migrated settings from QSettings")

            return migrated_any

        except Exception as e:  # pylint: disable=broad-exception-caught  # Migration is non-critical
            logger.warning(f"QSettings migration failed: {e}")
            return False

    def _migrate_from_json(self, json_file: Path) -> bool:
        """Migrate from JSON settings file."""
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                old_settings = json.load(f)

            # Map old keys to new structure
            mapping = {
                "theme": "app.theme",
                "window_opacity": "app.window_opacity",
                "language": "app.language",
                "max_recent_files": "app.max_recent_files",
                "confirm_on_exit": "app.confirm_on_exit",
                "show_tooltips": "app.show_tooltips",
                "auto_save": "app.auto_save",
                "last_directory": "paths.default_directory",
                "default_extensions": "paths.custom_extensions",
                "ai_provider": "ai.default_provider",
                "remember_api_keys": "ai.remember_api_keys",
            }

            for old_key, new_key in mapping.items():
                if old_key in old_settings:
                    self.set(new_key, old_settings[old_key], save=False)

            # Backup old file
            backup = json_file.with_suffix(".json.migrated")
            shutil.move(json_file, backup)

            logger.info(f"Migrated settings from {json_file}")
            logger.info(f"Backup saved to {backup}")
            return True

        except Exception as e:  # pylint: disable=broad-exception-caught  # Migration is non-critical
            logger.warning(f"JSON migration failed: {e}")
            return False

    def _migrate_from_configparser(self, conf_file: Path) -> bool:
        """Migrate from ConfigParser format."""
        try:
            parser = ConfigParser()
            parser.read(conf_file)

            # Migrate THEME section
            if parser.has_section("THEME"):
                theme = parser.get("THEME", "mode", fallback="system")
                self.set("app.theme", theme, save=False)

            # Backup old file
            backup = conf_file.with_suffix(".conf.migrated")
            shutil.move(conf_file, backup)

            logger.info(f"Migrated settings from {conf_file}")
            logger.info(f"Backup saved to {backup}")
            return True

        except Exception as e:  # pylint: disable=broad-exception-caught  # Migration is non-critical
            logger.warning(f"ConfigParser migration failed: {e}")
            return False


# Global instance
_config_instance: Optional[ConfigManager] = None  # pylint: disable=invalid-name  # Module-level singleton


def get_config() -> ConfigManager:
    """Get global config instance."""
    global _config_instance  # pylint: disable=global-statement  # Singleton pattern
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


def reset_config_instance():
    """Reset global instance (useful for testing)."""
    global _config_instance  # pylint: disable=global-statement  # Singleton pattern
    _config_instance = None


# Demo usage
if __name__ == "__main__":
    print("=== ConfigManager Demo ===\n")

    config = ConfigManager()

    # Get values
    print("Current settings:")
    print(f"  Theme: {config.get('app.theme')}")
    print(f"  Language: {config.get('app.language')}")
    print(f"  Font size: {config.get('editor.font_size')}")
    print(f"  Log level: {config.get('logging.level')}")

    # Set values
    print("\nUpdating settings...")
    config.update({
        "app.theme": "dark",
        "editor.font_size": 14,
        "logging.level": "DEBUG"
    })

    print("\nNew settings:")
    print(f"  Theme: {config.get('app.theme')}")
    print(f"  Font size: {config.get('editor.font_size')}")
    print(f"  Log level: {config.get('logging.level')}")

    print(f"\nConfig file: {config.config_file}")
    print("✅ ConfigManager demo complete")
