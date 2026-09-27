"""User-controlled feedback emitted after successful processing."""

from typing import Any, Optional


def completion_sound_enabled(settings: Optional[Any] = None) -> bool:
    """Return the persisted completion-sound preference (silent by default)."""
    if settings is None:
        from .settings_manager import get_settings

        settings = get_settings()
    return bool(settings.get("completion_sound", False))


def notify_processing_completed(settings: Optional[Any] = None, app=None) -> bool:
    """Emit one system beep when enabled; return whether feedback was emitted."""
    if not completion_sound_enabled(settings):
        return False

    if app is None:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
    if app is None:
        return False

    app.beep()
    return True
