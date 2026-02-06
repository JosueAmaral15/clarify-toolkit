#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Translator - Runtime internationalization system for Clarify.

Features:
- Lazy loading: Load translations only when requested
- Runtime switching: Change language without restarting
- Signal-based: Emit languageChanged signal for UI updates
- Auto-detect: Detect system language on first run
- Fallback: Fall back to English for missing translations

Architecture:
    Translator (singleton) → loads JSON files → provides get() method
    MainWindow listens to languageChanged signal → calls retranslate()
"""

# pylint: disable=no-name-in-module  # PySide6 has dynamic module structure

import json
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal


class Translator(QObject):
    """Singleton translator with runtime language switching."""

    languageChanged = Signal(str)  # Emitted when language changes

    _instance: Optional['Translator'] = None

    # pylint: disable=no-value-for-parameter  # False positive - cls is implicit in __new__
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False  # pylint: disable=access-member-before-definition  # Set in singleton pattern
        return cls._instance

    def __init__(self):
        if self._initialized:  # pylint: disable=access-member-before-definition  # Set in __new__
            return

        super().__init__()
        self._initialized = True

        self._current_language: str = "en"  # Default to English
        self._translations: Dict[str, Dict[str, str]] = {}
        self._available_languages = ["en", "pt_BR", "es", "fr", "de", "zh", "ja"]

        # Auto-detect system language or use saved preference
        detected_lang = self._detect_system_locale()
        if detected_lang in self._available_languages:
            self._current_language = detected_lang

        # Load initial language
        self._load_language(self._current_language)

    def _detect_system_locale(self) -> str:
        """
        Detect system language using QLocale.

        Returns:
            Language code ('en', 'pt_BR', 'es', 'fr', 'de', 'zh', 'ja')
            Falls back to 'en' if system language not supported.
        """
        try:
            from PySide6.QtCore import QLocale  # pylint: disable=import-outside-toplevel  # Lazy import

            # Get system locale (e.g., 'pt_BR', 'es_ES', 'fr_FR')
            system_locale = QLocale.system().name()  # Returns format: 'en_US', 'pt_BR'

            # Map locale variants to our internal codes
            locale_map = {
                "en": "en",
                "pt_BR": "pt_BR",
                "pt_PT": "pt_BR",  # European Portuguese → Brazilian Portuguese
                "es": "es",
                "es_ES": "es",  # Spain Spanish
                "es_MX": "es",  # Mexican Spanish
                "es_AR": "es",  # Argentine Spanish
                "fr": "fr",
                "fr_FR": "fr",  # France French
                "fr_CA": "fr",  # Canadian French
                "de": "de",
                "de_DE": "de",  # German German
                "de_AT": "de",  # Austrian German
                "de_CH": "de",  # Swiss German
                "zh": "zh",
                "zh_CN": "zh",  # Simplified Chinese
                "zh_TW": "zh",  # Traditional Chinese (use same for now)
                "ja": "ja",
                "ja_JP": "ja",  # Japanese
            }

            # Direct match
            if system_locale in locale_map:
                return locale_map[system_locale]

            # Try language code only (first 2 chars)
            lang_code = system_locale[:2]
            if lang_code in locale_map:
                return locale_map[lang_code]

            # Fallback to English
            return "en"

        except Exception as e:  # pylint: disable=broad-exception-caught  # Fallback to English on any error
            print(f"Error detecting system locale: {e}")
            return "en"

    def _load_language(self, lang: str) -> None:
        """Load translation file for the given language."""
        if lang in self._translations:
            return  # Already loaded

        # Find translations directory
        i18n_dir = Path(__file__).parent
        translation_file = i18n_dir / f"{lang}.json"

        if not translation_file.exists():
            print(f"Warning: Translation file not found: {translation_file}")
            self._translations[lang] = {}
            return

        try:
            with open(translation_file, 'r', encoding='utf-8') as f:
                self._translations[lang] = json.load(f)
        except Exception as e:  # pylint: disable=broad-exception-caught  # Translation loading errors vary
            print(f"Error loading translation {lang}: {e}")
            self._translations[lang] = {}

    def get(self, key: str, default: Optional[str] = None) -> str:
        """
        Get translated string for the given key.

        Args:
            key: Translation key (e.g., 'menu.file', 'dialog.ok')
            default: Default value if key not found (defaults to key itself)

        Returns:
            Translated string or default
        """
        # Get current language translations
        translations = self._translations.get(self._current_language, {})

        # Try to find translation
        result = translations.get(key)

        if result is None:
            # Fallback to English
            if self._current_language != "en":
                en_translations = self._translations.get("en", {})
                result = en_translations.get(key)

        # Return result or default
        if result is None:
            return default if default is not None else key

        return result

    def switch_language(self, lang: str) -> None:
        """
        Switch to a different language at runtime.

        Args:
            lang: Language code ('en', 'pt_BR')
        """
        if lang not in self._available_languages:
            print(f"Warning: Language '{lang}' not available")
            return

        if lang == self._current_language:
            return  # Already using this language

        # Load new language if not loaded
        self._load_language(lang)

        # Switch language
        self._current_language = lang

        # Emit signal to update UI
        self.languageChanged.emit(lang)

    @property
    def current_language(self) -> str:
        """Get current language code."""
        return self._current_language

    @property
    def available_languages(self) -> list:
        """Get list of available languages."""
        return self._available_languages.copy()

    def get_language_name(self, lang: str) -> str:
        """Get human-readable language name."""
        names = {
            "en": "English",
            "pt_BR": "Português (Brasil)",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
            "zh": "中文 (简体)",  # Simplified Chinese
            "ja": "日本語"  # Japanese
        }
        return names.get(lang, lang)


# Global singleton instance
_translator: Optional[Translator] = None  # pylint: disable=invalid-name  # Module-level singleton


def get_translator() -> Translator:
    """Get global translator instance."""
    global _translator  # pylint: disable=global-statement  # Singleton pattern
    if _translator is None:
        _translator = Translator()
    return _translator


def switch_language(lang: str) -> None:
    """Switch language at runtime (convenience function)."""
    get_translator().switch_language(lang)


# Convenience helper for shorter syntax
def tr(key: str, default: Optional[str] = None) -> str:
    """
    Shorthand for get_translator().get()

    Usage:
        from src.i18n import tr
        print(tr("menu.file"))
    """
    return get_translator().get(key, default)


def tooltip_tr(key: str, default: Optional[str] = None) -> str:
    """
    Shorthand for tooltip translations with 'tooltip.' prefix.

    This is a convenience function specifically for tooltip translations.
    It automatically prepends 'tooltip.' to the key.

    Usage:
        from src.i18n import tooltip_tr
        widget.setToolTip(tooltip_tr("set_ops.file_a"))
        # Equivalent to: tr("tooltip.set_ops.file_a")

    Args:
        key: Tooltip key without 'tooltip.' prefix (e.g., 'set_ops.file_a')
        default: Default value if key not found

    Returns:
        Translated tooltip string

    Example:
        # In Set Operations Dock:
        self.ed_file_a.setToolTip(tooltip_tr("set_ops.file_a"))

        # In JSON file (src/i18n/en.json):
        {
            "tooltip": {
                "set_ops": {
                    "file_a": "First JSON file for set operation"
                }
            }
        }
    """
    return get_translator().get(f"tooltip.{key}", default)
