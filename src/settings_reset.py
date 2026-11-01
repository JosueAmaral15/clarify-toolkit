"""Coordinated, data-preserving reset of Clarify preference stores."""

# pylint: disable=no-name-in-module  # PySide6 exposes extension types dynamically.

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
from configparser import ConfigParser
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Iterable

from PySide6.QtCore import QSettings

from .appearance_defaults import DEFAULT_THEME, DEFAULT_WINDOW_OPACITY_PERCENT
from .config_manager import ConfigManager
from .settings_manager import SettingsManager
from .utils.atomic_files import write_text_atomically


class ResetSection(str, Enum):
    """User-visible reset groups."""

    APPEARANCE = "appearance"
    GENERAL = "general"
    SHORTCUTS = "shortcuts"
    ADVANCED = "advanced"


ALL_RESET_SECTIONS = tuple(ResetSection)


@dataclass(frozen=True)
class SettingsResetResult:
    """Successful reset outcome presented to the UI."""

    sections: tuple[ResetSection, ...]
    backup_path: Path
    restart_required: bool


class SettingsResetError(RuntimeError):
    """Raised when backup, reset, or rollback cannot complete safely."""


class SettingsResetCoordinator:
    """Reset known preferences across active stores without deleting user data."""

    MAX_BACKUP_FILE_BYTES = 8 * 1024 * 1024
    MAX_BACKUP_TOTAL_BYTES = 32 * 1024 * 1024

    JSON_KEYS = {
        ResetSection.APPEARANCE: ("theme", "window_opacity"),
        ResetSection.GENERAL: (
            "language", "max_recent_files", "auto_save", "completion_sound",
            "show_tooltips", "confirm_on_exit", "ai_provider",
            "remember_api_keys", "default_extensions",
        ),
        ResetSection.SHORTCUTS: ("custom_shortcuts",),
        ResetSection.ADVANCED: (),
    }

    YAML_KEYS = {
        ResetSection.APPEARANCE: ("app.theme", "app.window_opacity"),
        ResetSection.GENERAL: (
            "app.language", "app.max_recent_files", "app.confirm_on_exit",
            "app.show_tooltips", "app.auto_save", "app.check_updates_on_startup",
        ),
        ResetSection.SHORTCUTS: (),
        ResetSection.ADVANCED: tuple(
            f"{section}.{key}"
            for section in ("logging", "performance", "ai", "editor", "paths")
            for key in ConfigManager.DEFAULTS[section]
        ),
    }

    QSETTINGS_DEFAULTS = {
        ResetSection.APPEARANCE: {
            "theme": DEFAULT_THEME,
            "window_opacity": DEFAULT_WINDOW_OPACITY_PERCENT,
        },
        ResetSection.GENERAL: {
            "language": "en",
            "update_checker/enabled": True,
        },
        ResetSection.SHORTCUTS: {},
        ResetSection.ADVANCED: {
            "error_reporting/enabled": True,
            "error_reporting/include_system_info": True,
            "error_reporting/auto_open_github": False,
        },
    }

    def __init__(
        self,
        settings: SettingsManager,
        *,
        config: ConfigManager | None = None,
        qsettings: QSettings | None = None,
        backup_root: Path | None = None,
        home: Path | None = None,
    ) -> None:
        self.settings = settings
        self.home = Path.home() if home is None else Path(home)
        config_path = self.home / ".config" / "clarify" / "config.yaml"
        self.config = config or ConfigManager(str(config_path), migrate_legacy=False)
        self.qsettings = qsettings or getattr(settings, "qsettings", None)
        if self.qsettings is None:
            self.qsettings = QSettings("Clarify", "ClarifyApp")
        self.backup_root = backup_root or (
            self.home / ".config" / "clarify" / "backups" / "settings-reset"
        )

    def reset(self, sections: Iterable[ResetSection | str]) -> SettingsResetResult:
        """Back up all relevant stores, then reset only the selected categories."""
        selected = self._normalize_sections(sections)
        if not selected:
            raise SettingsResetError("Select at least one settings category")

        self.qsettings.sync()
        paths = self._store_paths()
        snapshots = self._capture_paths(paths)
        backup_path = self._create_backup_bundle(snapshots)
        json_before = deepcopy(self.settings.settings)
        stored_before = set(self.settings._stored_keys)  # pylint: disable=protected-access
        yaml_before = deepcopy(self.config.config)
        qsettings_before = self._capture_qsettings_values(selected)

        try:
            self._reset_json(selected)
            self._reset_yaml(selected)
            self._reset_legacy(selected)
            self._reset_qsettings(selected)
        except Exception as exc:
            rollback_errors = self._rollback(
                snapshots,
                json_before,
                stored_before,
                yaml_before,
                qsettings_before,
            )
            detail = f"Settings reset failed: {exc}"
            if rollback_errors:
                detail += "; rollback also failed: " + "; ".join(rollback_errors)
            raise SettingsResetError(detail) from exc

        return SettingsResetResult(
            sections=selected,
            backup_path=backup_path,
            restart_required=ResetSection.ADVANCED in selected,
        )

    @staticmethod
    def _normalize_sections(
        sections: Iterable[ResetSection | str],
    ) -> tuple[ResetSection, ...]:
        selected = {ResetSection(section) for section in sections}
        return tuple(section for section in ALL_RESET_SECTIONS if section in selected)

    def _store_paths(self) -> tuple[Path, ...]:
        candidates = [
            Path(self.settings.config_file),
            Path(self.config.config_file),
            Path(self.qsettings.fileName()),
            self.home / ".config" / "clarify.conf",
            self.home / ".clarify" / "preferences.ini",
        ]
        unique: list[Path] = []
        for path in candidates:
            path = path.expanduser().absolute()
            if path not in unique:
                unique.append(path)
        return tuple(unique)

    def _capture_paths(self, paths: Iterable[Path]) -> dict[Path, bytes | None]:
        snapshots: dict[Path, bytes | None] = {}
        total = 0
        for path in paths:
            if not os.path.lexists(path):
                snapshots[path] = None
                continue
            info = os.lstat(path)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise SettingsResetError(f"Unsafe settings store: {path}")
            if info.st_size > self.MAX_BACKUP_FILE_BYTES:
                raise SettingsResetError(f"Settings store exceeds backup limit: {path}")
            total += info.st_size
            if total > self.MAX_BACKUP_TOTAL_BYTES:
                raise SettingsResetError("Settings backup exceeds the 32 MiB limit")
            snapshots[path] = path.read_bytes()
        return snapshots

    def _create_backup_bundle(self, snapshots: dict[Path, bytes | None]) -> Path:
        self.backup_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.backup_root, 0o700)
        pending = Path(tempfile.mkdtemp(prefix=".pending-", dir=self.backup_root))
        os.chmod(pending, 0o700)
        manifest = {"created_at": datetime.now().isoformat(), "stores": []}
        try:
            for index, (source, content) in enumerate(snapshots.items()):
                entry = {"source": str(source), "existed": content is not None}
                if content is not None:
                    name = f"{index:02d}-{source.name}.bak"
                    target = pending / name
                    target.write_bytes(content)
                    os.chmod(target, 0o600)
                    entry.update({
                        "backup": name,
                        "bytes": len(content),
                        "sha256": hashlib.sha256(content).hexdigest(),
                    })
                manifest["stores"].append(entry)
            manifest_path = pending / "manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            os.chmod(manifest_path, 0o600)
            final = self.backup_root / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            os.replace(pending, final)
            return final
        except Exception:
            shutil.rmtree(pending, ignore_errors=True)
            raise

    def _reset_json(self, selected: tuple[ResetSection, ...]) -> None:
        for section in selected:
            for key in self.JSON_KEYS[section]:
                self.settings.settings[key] = deepcopy(SettingsManager.DEFAULTS[key])
                self.settings._stored_keys.add(key)  # pylint: disable=protected-access
        self.settings.save(raise_on_error=True)

    def _reset_yaml(self, selected: tuple[ResetSection, ...]) -> None:
        for section in selected:
            for key in self.YAML_KEYS[section]:
                self.config.set(key, deepcopy(self._yaml_default(key)), save=False)
        self.config.save(raise_on_error=True)

    @staticmethod
    def _yaml_default(key: str):
        value = ConfigManager.DEFAULTS
        for part in key.split("."):
            value = value[part]
        return value

    def _reset_qsettings(self, selected: tuple[ResetSection, ...]) -> None:
        for section in selected:
            for key, value in self.QSETTINGS_DEFAULTS[section].items():
                self.qsettings.setValue(key, value)
        self.qsettings.sync()
        if self.qsettings.status() != QSettings.Status.NoError:
            raise SettingsResetError("QSettings could not persist reset values")

    def _reset_legacy(self, selected: tuple[ResetSection, ...]) -> None:
        if ResetSection.APPEARANCE not in selected:
            return
        for path in (
            self.home / ".config" / "clarify.conf",
            self.home / ".clarify" / "preferences.ini",
        ):
            if not path.exists():
                continue
            parser = ConfigParser()
            parser.read(path, encoding="utf-8")
            if not parser.has_section("THEME"):
                parser.add_section("THEME")
            parser.set("THEME", "mode", DEFAULT_THEME)
            from io import StringIO
            output = StringIO()
            parser.write(output)
            write_text_atomically(path, output.getvalue())

    def _capture_qsettings_values(
        self, selected: tuple[ResetSection, ...]
    ) -> dict[str, tuple[bool, object]]:
        keys = {
            key
            for section in selected
            for key in self.QSETTINGS_DEFAULTS[section]
        }
        return {
            key: (self.qsettings.contains(key), self.qsettings.value(key))
            for key in keys
        }

    def _rollback(
        self,
        snapshots: dict[Path, bytes | None],
        json_before: dict,
        stored_before: set[str],
        yaml_before: dict,
        qsettings_before: dict[str, tuple[bool, object]],
    ) -> list[str]:
        errors: list[str] = []
        for path, content in snapshots.items():
            try:
                if content is None:
                    if path.exists():
                        path.unlink()
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    write_text_atomically(path, content.decode("utf-8"))
            except Exception as exc:  # pylint: disable=broad-exception-caught
                errors.append(f"{path}: {exc}")
        self.settings.settings = json_before
        self.settings._stored_keys = stored_before  # pylint: disable=protected-access
        self.config.config = yaml_before
        try:
            for key, (existed, value) in qsettings_before.items():
                if existed:
                    self.qsettings.setValue(key, value)
                else:
                    self.qsettings.remove(key)
            self.qsettings.sync()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            errors.append(f"QSettings: {exc}")
        return errors
