"""Transactional reset of Clarify preferences without deleting user data."""

# pylint: disable=no-name-in-module  # PySide6 exposes extension types dynamically.

from __future__ import annotations

import base64
import copy
import io
import json
import os
import tempfile
import zipfile
from configparser import ConfigParser
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Mapping

import yaml
from PySide6.QtCore import QByteArray, QSettings

from .appearance_defaults import DEFAULT_THEME, DEFAULT_WINDOW_OPACITY_PERCENT
from .config_manager import ConfigManager
from .settings_manager import SettingsManager


@dataclass(frozen=True)
class ResetCategory:
    """A user-visible group of resettable preferences."""

    category_id: str
    label_key: str
    description_key: str
    restart_required: bool


@dataclass(frozen=True)
class ResetResult:
    """Result returned only after every selected store was synchronized."""

    backup_path: Path
    categories: tuple[str, ...]
    restart_required: bool


CATEGORIES = (
    ResetCategory("appearance", "settings_reset.category.appearance", "settings_reset.category.appearance_detail", False),
    ResetCategory("general", "settings_reset.category.general", "settings_reset.category.general_detail", True),
    ResetCategory("shortcuts", "settings_reset.category.shortcuts", "settings_reset.category.shortcuts_detail", True),
    ResetCategory("workspace", "settings_reset.category.workspace", "settings_reset.category.workspace_detail", True),
    ResetCategory("tools", "settings_reset.category.tools", "settings_reset.category.tools_detail", True),
    ResetCategory("advanced", "settings_reset.category.advanced", "settings_reset.category.advanced_detail", True),
)

_JSON_DEFAULT_KEYS = {
    "appearance": ("theme", "window_opacity"),
    "general": (
        "language", "max_recent_files", "auto_save", "completion_sound", "show_tooltips",
        "confirm_on_exit", "ai_provider", "remember_api_keys", "default_extensions",
    ),
    "shortcuts": ("custom_shortcuts",),
}
_JSON_REMOVE_KEYS = {
    "workspace": (
        "window_geometry", "tabs_open_tools", "tabs_fixed_open",
        "tabs_current_index", "tabs_current_tool",
    ),
}
_YAML_SECTIONS = {
    "appearance": ("app.theme", "app.window_opacity"),
    "general": (
        "app.language", "app.max_recent_files", "app.confirm_on_exit", "app.show_tooltips",
        "app.auto_save", "app.check_updates_on_startup", "paths.custom_extensions",
    ),
    "tools": (
        "editor.font_family", "editor.font_size", "editor.tab_width",
        "editor.auto_save_interval_sec", "editor.syntax_highlighting",
    ),
    "advanced": (
        "logging.level", "logging.max_file_size_mb", "logging.backup_count",
        "logging.console_output", "performance.thread_pool_size",
        "performance.max_file_size_mb", "performance.cache_duration_hours",
        "performance.batch_size", "ai.default_provider", "ai.remember_api_keys",
        "ai.max_tokens", "ai.temperature",
    ),
}
_QSETTINGS_KEYS = {
    "ClarifyApp": {
        "general": (
            "update_checker/enabled", "error_reporting/enabled",
            "error_reporting/include_system_info", "error_reporting/auto_open_github",
        ),
        "workspace": ("LastLayout", "accessibility/font_size"),
    },
    "EditorDock": {
        "tools": (
            "auto_save_enabled", "show_line_numbers_enabled", "word_wrap_enabled",
            "render_whitespace_enabled", "indent_use_tabs", "indent_width",
            "temp_note_retention_days", "recovery_retention_hours", "show_explorer_enabled",
            "find/case_sensitive", "find/whole_word", "find/regex", "find/scope",
            "find/inverted", "find/floating_geometry",
        ),
    },
    "FileExplorer": {
        "tools": (
            "reuse_previous_results", "show_hidden", "long_format",
            "human_readable", "recursive", "workspace_mode",
        ),
    },
    "FileList": {
        "tools": ("show_hidden", "long_format", "human_readable", "recursive"),
    },
}


class SettingsResetError(RuntimeError):
    """Raised when reset cannot complete or be rolled back safely."""


class SettingsResetService:
    """Reset allow-listed preferences across JSON, YAML, INI and QSettings."""

    def __init__(
        self,
        settings: SettingsManager,
        config: ConfigManager,
        *,
        qsettings_factory: Callable[[str, str], QSettings] = QSettings,
        legacy_paths: Iterable[Path] | None = None,
        backup_dir: Path | None = None,
    ) -> None:
        self.settings = settings
        self.config = config
        self._qsettings_factory = qsettings_factory
        self.legacy_paths = tuple(legacy_paths or (
            Path.home() / ".config" / "clarify.conf",
            Path.home() / ".clarify" / "preferences.ini",
        ))
        self.backup_dir = backup_dir or Path.home() / ".config" / "clarify" / "backups"

    @staticmethod
    def categories() -> tuple[ResetCategory, ...]:
        return CATEGORIES

    def reset(self, category_ids: Iterable[str]) -> ResetResult:
        selected = tuple(dict.fromkeys(category_ids))
        known = {category.category_id for category in CATEGORIES}
        if not selected or any(category not in known for category in selected):
            raise ValueError("At least one valid reset category is required")

        qstores = {
            name: self._qsettings_factory("Clarify", name)
            for name in _QSETTINGS_KEYS
        }
        snapshot = self._snapshot(qstores)
        backup_path = self._write_atomic_backup(snapshot, selected)
        try:
            self._apply_json(selected)
            self._apply_yaml(selected)
            self._apply_qsettings(selected, qstores)
            self._apply_legacy(selected)
        except Exception as error:
            try:
                self._restore(snapshot, qstores)
            except Exception as rollback_error:
                raise SettingsResetError(
                    f"Reset failed and rollback also failed: {rollback_error}"
                ) from error
            raise SettingsResetError(f"Reset failed; previous settings were restored: {error}") from error

        return ResetResult(
            backup_path=backup_path,
            categories=selected,
            restart_required=any(
                category.restart_required for category in CATEGORIES
                if category.category_id in selected
            ),
        )

    def _snapshot(self, qstores: Mapping[str, QSettings]) -> dict:
        return {
            "json": self.settings.get_all(),
            "json_bytes": (
                self.settings.config_file.read_bytes()
                if self.settings.config_file.exists() else None
            ),
            "json_stored_keys": sorted(self.settings._stored_keys),  # pylint: disable=protected-access
            "yaml": self.config.get_all(),
            "yaml_bytes": (
                self.config.config_file.read_bytes()
                if self.config.config_file.exists() else None
            ),
            "legacy": {
                str(path): path.read_bytes() if path.exists() else None
                for path in self.legacy_paths
            },
            "qsettings": {
                name: {key: store.value(key) for key in store.allKeys()}
                for name, store in qstores.items()
            },
        }

    def _write_atomic_backup(self, snapshot: dict, selected: tuple[str, ...]) -> Path:
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        destination = self.backup_dir / f"settings-reset-{stamp}.zip"
        fd, temp_name = tempfile.mkstemp(prefix=".settings-reset-", suffix=".tmp", dir=self.backup_dir)
        try:
            with os.fdopen(fd, "w+b") as raw:
                with zipfile.ZipFile(raw, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                    manifest = {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "categories": list(selected),
                        "format": 1,
                    }
                    archive.writestr("manifest.json", json.dumps(manifest, indent=2))
                    archive.writestr(
                        "settings.json",
                        snapshot["json_bytes"] or json.dumps(snapshot["json"], indent=2),
                    )
                    archive.writestr(
                        "config.yaml",
                        snapshot["yaml_bytes"] or yaml.safe_dump(snapshot["yaml"], sort_keys=False),
                    )
                    archive.writestr(
                        "qsettings.json",
                        json.dumps(self._json_safe(snapshot["qsettings"]), indent=2),
                    )
                    for index, (path, content) in enumerate(snapshot["legacy"].items()):
                        if content is not None:
                            archive.writestr(f"legacy/{index}.ini", content)
                        manifest_path = f"legacy/{index}.path"
                        archive.writestr(manifest_path, path)
                raw.flush()
                os.fsync(raw.fileno())
            os.replace(temp_name, destination)
            self._fsync_directory(self.backup_dir)
        except Exception:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
            raise
        return destination

    @classmethod
    def _json_safe(cls, value):
        if isinstance(value, QByteArray):
            return {"__type__": "QByteArray", "base64": base64.b64encode(bytes(value)).decode("ascii")}
        if isinstance(value, bytes):
            return {"__type__": "bytes", "base64": base64.b64encode(value).decode("ascii")}
        if isinstance(value, Mapping):
            return {str(key): cls._json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [cls._json_safe(item) for item in value]
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        return {"__type__": type(value).__name__, "repr": repr(value)}

    def _apply_json(self, selected: tuple[str, ...]) -> None:
        values = self.settings.get_all()
        for category in selected:
            for key in _JSON_DEFAULT_KEYS.get(category, ()):
                values[key] = copy.deepcopy(SettingsManager.DEFAULTS[key])
            for key in _JSON_REMOVE_KEYS.get(category, ()):
                values.pop(key, None)
        self._atomic_json(self.settings.config_file, values)
        self.settings.settings = values
        self.settings._stored_keys = set(values)  # pylint: disable=protected-access

    def _apply_yaml(self, selected: tuple[str, ...]) -> None:
        values = self.config.get_all()
        for category in selected:
            for dotted_key in _YAML_SECTIONS.get(category, ()):
                default = self._dotted_get(ConfigManager.DEFAULTS, dotted_key)
                self._dotted_set(values, dotted_key, copy.deepcopy(default))
        self._atomic_yaml(self.config.config_file, values)
        self.config.config = values

    @staticmethod
    def _apply_qsettings(selected: tuple[str, ...], qstores: Mapping[str, QSettings]) -> None:
        for name, categories in _QSETTINGS_KEYS.items():
            store = qstores[name]
            for category in selected:
                for key in categories.get(category, ()):
                    store.remove(key)
            if name == "ClarifyApp" and "appearance" in selected:
                store.setValue("theme", DEFAULT_THEME)
                store.setValue("window_opacity", DEFAULT_WINDOW_OPACITY_PERCENT)
            if name == "ClarifyApp" and "general" in selected:
                store.setValue("language", SettingsManager.DEFAULTS["language"])
            store.sync()
            if store.status() != QSettings.NoError:
                raise OSError(f"QSettings sync failed for {name}")

    def _apply_legacy(self, selected: tuple[str, ...]) -> None:
        if "appearance" not in selected:
            return
        for path in self.legacy_paths:
            if not path.exists():
                continue
            parser = ConfigParser()
            parser.read(path, encoding="utf-8")
            if not parser.has_section("THEME"):
                parser.add_section("THEME")
            parser.set("THEME", "mode", DEFAULT_THEME)
            buffer = io.StringIO()
            parser.write(buffer)
            self._atomic_bytes(path, buffer.getvalue().encode("utf-8"))

    def _restore(self, snapshot: dict, qstores: Mapping[str, QSettings]) -> None:
        if snapshot["json_bytes"] is None:
            self.settings.config_file.unlink(missing_ok=True)
        else:
            self._atomic_bytes(self.settings.config_file, snapshot["json_bytes"])
        self.settings.settings = copy.deepcopy(snapshot["json"])
        self.settings._stored_keys = set(snapshot["json_stored_keys"])  # pylint: disable=protected-access
        if snapshot["yaml_bytes"] is None:
            self.config.config_file.unlink(missing_ok=True)
        else:
            self._atomic_bytes(self.config.config_file, snapshot["yaml_bytes"])
        self.config.config = copy.deepcopy(snapshot["yaml"])
        for path_text, content in snapshot["legacy"].items():
            path = Path(path_text)
            if content is None:
                path.unlink(missing_ok=True)
            else:
                self._atomic_bytes(path, content)
        for name, store in qstores.items():
            store.clear()
            for key, value in snapshot["qsettings"][name].items():
                store.setValue(key, value)
            store.sync()

    @staticmethod
    def _dotted_get(mapping: dict, dotted_key: str):
        value = mapping
        for key in dotted_key.split("."):
            value = value[key]
        return value

    @staticmethod
    def _dotted_set(mapping: dict, dotted_key: str, value) -> None:
        parts = dotted_key.split(".")
        target = mapping
        for key in parts[:-1]:
            target = target.setdefault(key, {})
        target[parts[-1]] = value

    @staticmethod
    def _atomic_json(path: Path, value: dict) -> None:
        SettingsResetService._atomic_bytes(path, json.dumps(value, indent=2).encode("utf-8"))

    @staticmethod
    def _atomic_yaml(path: Path, value: dict) -> None:
        header = "# Clarify Configuration File\n# Reset to documented defaults\n\n"
        SettingsResetService._atomic_bytes(
            path, (header + yaml.safe_dump(value, sort_keys=False)).encode("utf-8")
        )

    @staticmethod
    def _atomic_bytes(path: Path, content: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, path)
            SettingsResetService._fsync_directory(path.parent)
        except Exception:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
            raise

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
