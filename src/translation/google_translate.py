#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Translate API Module (Free Web Scraping)

Provides free translation services using Google Translate web interface.
Includes caching, retry mechanism, and rate limiting.

Author: Josué Amaral
Date: December 21, 2025
Version: 2.9.78
"""

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TranslationResult:
    """Result of a translation operation."""
    success: bool
    translated_text: str = ""
    source_language: str = ""
    target_language: str = ""
    error_message: str = ""
    from_cache: bool = False


class GoogleTranslateAPI:
    """
    Free Google Translate API using web scraping.
    
    Features:
    - Free translation using Google Translate web interface
    - Local caching to reduce API calls
    - Automatic retry mechanism (3 attempts)
    - Rate limiting to avoid being blocked
    - Support for 7 languages from Clarify i18n system
    """
    
    # Language mapping (ISO 639-1 codes)
    LANGUAGES = {
        'en': 'English',
        'pt': 'Português',
        'es': 'Español', 
        'fr': 'Français',
        'de': 'Deutsch',
        'zh': '中文',
        'ja': '日本語'
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize Google Translate API.
        
        Args:
            cache_dir: Directory for cache files. Defaults to ~/.clarify/translate_cache/
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / '.clarify' / 'translate_cache'
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / 'translations.json'
        
        # Load cache
        self._cache = self._load_cache()
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.5  # 500ms between requests
    
    def _load_cache(self) -> Dict[str, Dict]:
        """Load translation cache from disk."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_cache(self) -> None:
        """Save translation cache to disk."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _get_cache_key(self, text: str, from_lang: str, to_lang: str) -> str:
        """Generate cache key for translation."""
        # Normalize text for consistent caching
        normalized_text = text.strip().lower()
        return f"{from_lang}_{to_lang}_{hash(normalized_text)}"
    
    def _apply_rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _translate_request(self, text: str, from_lang: str, to_lang: str) -> TranslationResult:
        """
        Make actual translation request to Google Translate.
        
        Uses the web interface endpoint that doesn't require API key.
        """
        try:
            self._apply_rate_limit()
            
            # Google Translate web endpoint
            base_url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': from_lang,
                'tl': to_lang,
                'dt': 't',
                'q': text
            }
            
            url = f"{base_url}?" + urllib.parse.urlencode(params)
            
            # Create request with headers to avoid being blocked
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                }
            )
            
            # Make request with timeout
            # nosec B310: URL is always HTTPS googleapis.com (safe)
            with urllib.request.urlopen(req, timeout=10) as response:  # nosec
                data = response.read().decode('utf-8')
            
            # Parse Google Translate response
            # Response format: [[["translated text","original text",null,null,0],...],null,"source_lang"]
            try:
                # Basic JSON parsing for Google Translate response
                result = json.loads(data)
                
                if result and len(result) > 0 and result[0]:
                    # Combine all translation parts
                    translated_parts = []
                    for part in result[0]:
                        if part and len(part) > 0 and part[0]:
                            translated_parts.append(part[0])
                    
                    translated_text = ''.join(translated_parts) if translated_parts else text
                    detected_lang = result[2] if len(result) > 2 else from_lang
                    
                    return TranslationResult(
                        success=True,
                        translated_text=translated_text,
                        source_language=detected_lang,
                        target_language=to_lang,
                        from_cache=False
                    )
            except (json.JSONDecodeError, IndexError, TypeError):
                pass
                
            return TranslationResult(
                success=False,
                error_message="Failed to parse translation response"
            )
            
        except Exception as e:
            return TranslationResult(
                success=False,
                error_message=f"Translation request failed: {str(e)}"
            )
    
    def translate_text(self, text: str, from_lang: str = 'auto', to_lang: str = 'pt') -> TranslationResult:
        """
        Translate text with caching and retry mechanism.
        
        Args:
            text: Text to translate
            from_lang: Source language code ('auto' for auto-detect)
            to_lang: Target language code
            
        Returns:
            TranslationResult with translation status and result
        """
        if not text or not text.strip():
            return TranslationResult(
                success=False,
                error_message="Empty text provided"
            )
        
        # Validate language codes
        if from_lang != 'auto' and from_lang not in self.LANGUAGES:
            return TranslationResult(
                success=False,
                error_message=f"Unsupported source language: {from_lang}"
            )
        
        if to_lang not in self.LANGUAGES:
            return TranslationResult(
                success=False,
                error_message=f"Unsupported target language: {to_lang}"
            )
        
        # Check cache first
        cache_key = self._get_cache_key(text, from_lang, to_lang)
        if cache_key in self._cache:
            cached_result = self._cache[cache_key]
            return TranslationResult(
                success=True,
                translated_text=cached_result['translated_text'],
                source_language=cached_result.get('source_language', from_lang),
                target_language=cached_result.get('target_language', to_lang),
                from_cache=True
            )
        
        # Attempt translation with retry mechanism
        max_attempts = 3
        last_error = ""
        
        for attempt in range(max_attempts):
            result = self._translate_request(text, from_lang, to_lang)
            
            if result.success:
                # Cache successful translation
                self._cache[cache_key] = {
                    'translated_text': result.translated_text,
                    'source_language': result.source_language,
                    'target_language': result.target_language,
                    'timestamp': time.time()
                }
                self._save_cache()
                return result
            
            last_error = result.error_message
            
            # Wait before retry
            if attempt < max_attempts - 1:
                time.sleep(1.0 * (attempt + 1))  # Exponential backoff
        
        return TranslationResult(
            success=False,
            error_message=f"Translation failed after {max_attempts} attempts. Last error: {last_error}"
        )
    
    def clear_cache(self) -> bool:
        """
        Clear translation cache.
        
        Returns:
            True if cache was cleared successfully
        """
        try:
            self._cache.clear()
            if self.cache_file.exists():
                self.cache_file.unlink()
            return True
        except Exception:
            return False
    
    def get_cache_info(self) -> Dict[str, any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        cache_size = len(self._cache)
        cache_file_size = 0
        
        try:
            if self.cache_file.exists():
                cache_file_size = self.cache_file.stat().st_size
        except Exception:
            pass
        
        return {
            'entries': cache_size,
            'file_size_bytes': cache_file_size,
            'cache_dir': str(self.cache_dir)
        }