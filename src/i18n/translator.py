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

import json
import locale
import os
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal


class Translator(QObject):
    """Singleton translator with runtime language switching."""
    
    languageChanged = Signal(str)  # Emitted when language changes
    
    _instance: Optional['Translator'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        super().__init__()
        self._initialized = True
        
        self._current_language: str = "en"  # Default to English
        self._translations: Dict[str, Dict[str, str]] = {}
        self._available_languages = ["en", "pt_BR"]
        
        # Load initial language (always English by default)
        self._load_language(self._current_language)
    
    # Removed: Auto-detect system language (now defaults to English)
    # User can manually switch to pt_BR via menu if desired
    
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
        except Exception as e:
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
            "pt_BR": "Português (Brasil)"
        }
        return names.get(lang, lang)


# Global singleton instance
_translator: Optional[Translator] = None


def get_translator() -> Translator:
    """Get global translator instance."""
    global _translator
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
