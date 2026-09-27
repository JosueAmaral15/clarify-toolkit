"""Persistent recent paths shared by Clarify translation tools."""

from __future__ import annotations

import os
import logging
from typing import Any

from PySide6.QtCore import QSettings

logger = logging.getLogger(__name__)


class TranslationRecentPaths:
    """Store bounded recent source and dictionary paths without file contents."""

    MAX_ITEMS = 10
    _KEYS = {
        "source": "recent_source_paths",
        "dictionary": "recent_dictionary_paths",
    }

    def __init__(self, settings: Any | None = None) -> None:
        self.settings = settings or QSettings("Clarify", "Translation")

    def get(self, category: str) -> list[str]:
        """Return existing paths in most-recent-first order."""
        key = self._key(category)
        stored = self.settings.value(key, [], type=list)
        if not isinstance(stored, list):
            stored = []

        recent = [str(path) for path in stored if path and os.path.exists(str(path))]
        if recent != stored:
            self.settings.setValue(key, recent)
        return recent

    def add(self, category: str, path: str) -> None:
        """Add an existing path and keep at most ``MAX_ITEMS`` entries."""
        if not path:
            return
        normalized = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(normalized):
            return

        recent = self.get(category)
        if normalized in recent:
            recent.remove(normalized)
        recent.insert(0, normalized)
        self.settings.setValue(self._key(category), recent[: self.MAX_ITEMS])

    def clear(self, category: str) -> None:
        """Clear one recent-path category."""
        self.settings.setValue(self._key(category), [])

    @classmethod
    def _key(cls, category: str) -> str:
        try:
            return cls._KEYS[category]
        except KeyError as exc:
            raise ValueError(f"Unknown translation recent-path category: {category}") from exc


def record_translation_operation(
    owner: Any,
    operation_type: str,
    display_name: str,
    details: dict[str, Any],
) -> None:
    """Record metadata in persistent history and the visible dock when present."""
    try:
        from src.gui.progress import OperationHistory

        OperationHistory().add_operation(operation_type, details)
    except Exception as exc:  # History must never break a completed translation.
        logger.warning("Failed to persist translation history: %s", exc)

    try:
        parent = owner.parentWidget()
        history_dock = getattr(parent, "dock_history", None)
        if history_dock is not None:
            history_dock.add_operation(display_name, details)
    except Exception as exc:  # The optional dock can be absent or closing.
        logger.warning("Failed to update translation history dock: %s", exc)
