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
# pylint: disable=broad-exception-caught  # Translation robustness

import json
import time
import urllib.parse
import urllib.request
import re
from pathlib import Path
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass


@dataclass
class TranslationResult:
    """Result of a translation operation."""
    success: bool
    translated_text: str = ""
    source_language: str = ""
    target_language: str = ""
    error_message: str = ""
    from_cache: bool = False


class ChunkTranslationError(Exception):
    """
    Enhanced error for chunk translation failures.
    
    Phase C.5: Provides detailed context about which chunk failed and why.
    """
    
    def __init__(
        self,
        chunk_number: int,
        total_chunks: int,
        chunk_start: int,
        chunk_end: int,
        chunk_preview: str,
        attempts: int,
        last_error: str
    ):
        self.chunk_number = chunk_number
        self.total_chunks = total_chunks
        self.chunk_start = chunk_start
        self.chunk_end = chunk_end
        self.chunk_preview = chunk_preview
        self.attempts = attempts
        self.last_error = last_error
        
        # Generate detailed error message
        message = f"""Translation failed at chunk {chunk_number}/{total_chunks}:
  Position: characters {chunk_start}-{chunk_end}
  Chunk size: {chunk_end - chunk_start} chars
  Content preview: {chunk_preview}
  Attempts: {attempts}
  Last error: {last_error}
  
Suggestions:
  - The chunk may still be too large (try reducing max_chunk_size)
  - Network timeout (check your internet connection)
  - Rate limiting (wait a moment and retry)
  - Try translating a smaller portion manually"""
        
        super().__init__(message)


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

    def _find_semantic_boundaries(self, text: str) -> List[int]:
        """
        Find semantic break points in HTML text.
        
        Phase C.3: Semantic splitting - identifies paragraph, table, heading boundaries.
        
        Args:
            text: HTML or plain text to analyze
        
        Returns:
            List of positions suitable for breaking (sorted), or empty list for plain text
        """
        boundaries = []
        
        # Check if text contains HTML tags (more lenient detection)
        has_html_tags = bool(re.search(r'<[a-zA-Z/][^>]*>', text))
        
        if not has_html_tags:
            # Plain text: look for double newlines (paragraph breaks)
            for match in re.finditer(r'\n\n', text):
                boundaries.append(match.end())
            return sorted(boundaries)
        
        # HTML semantic boundaries (priority order: highest to lowest)
        
        # Priority 1: Table ends (never split tables)
        for match in re.finditer(r'</table>', text, re.IGNORECASE):
            boundaries.append(match.end())
        
        # Priority 2: Major section ends
        for match in re.finditer(r'</section>', text, re.IGNORECASE):
            boundaries.append(match.end())
        
        for match in re.finditer(r'</article>', text, re.IGNORECASE):
            boundaries.append(match.end())
        
        # Priority 3: Heading ends
        for match in re.finditer(r'</h[1-6]>', text, re.IGNORECASE):
            boundaries.append(match.end())
        
        # Priority 4: Paragraph ends
        for match in re.finditer(r'</p>', text, re.IGNORECASE):
            boundaries.append(match.end())
        
        # Priority 5: List ends
        for match in re.finditer(r'</(ul|ol|li)>', text, re.IGNORECASE):
            boundaries.append(match.end())
        
        # Priority 6: Div ends (lower priority, very common)
        for match in re.finditer(r'</div>', text, re.IGNORECASE):
            boundaries.append(match.end())
        
        # Sort and remove duplicates
        boundaries = sorted(set(boundaries))
        return boundaries

    def _is_inside_html_tag(self, text: str, position: int) -> bool:
        """
        Check if position is inside an HTML tag.
        
        Phase C.4: HTML tag preservation - prevents breaking mid-tag.
        
        Args:
            text: Text to check
            position: Position to check
        
        Returns:
            True if position is between < and > (inside a tag)
        """
        if position <= 0 or position >= len(text):
            return False
        
        # Look backward for nearest < and >
        last_open = text.rfind('<', 0, position)
        last_close = text.rfind('>', 0, position)
        
        # If last < is more recent than last >, we're inside a tag
        return last_open > last_close

    def _find_safe_break_position(self, text: str, target_pos: int, max_adjustment: int = 200) -> int:
        """
        Find safe position to break, avoiding splitting HTML tags.
        
        Phase C.4: HTML tag preservation.
        
        Strategy:
        1. If target_pos is safe, use it
        2. Otherwise, move forward to next tag close (>)
        3. If too far, move backward to previous tag close
        4. If still unsafe, return target (rare edge case)
        
        Args:
            text: Text to search
            target_pos: Target position to break at
            max_adjustment: Maximum chars to adjust position (default 200)
        
        Returns:
            Safe position to break (not inside HTML tag)
        """
        if target_pos <= 0 or target_pos >= len(text):
            return target_pos
        
        # Check if already safe
        if not self._is_inside_html_tag(text, target_pos):
            return target_pos
        
        # Look forward for next > (close tag)
        next_close = text.find('>', target_pos)
        if next_close != -1 and (next_close - target_pos) <= max_adjustment:
            # Close tag is nearby, use position after it
            return next_close + 1
        
        # Look backward for previous > (close tag)
        prev_close = text.rfind('>', 0, target_pos)
        if prev_close != -1 and (target_pos - prev_close) <= max_adjustment:
            # Use position after previous close tag
            return prev_close + 1
        
        # No safe position found within adjustment range, use target
        # (This should be rare with semantic splitting)
        return target_pos

    def _find_sentence_boundary(self, text: str, target_pos: int, search_window: int = 500) -> int:
        """
        Find last sentence boundary before target position.
        
        Helper method extracted from _split_into_chunks for reuse.
        
        Args:
            text: Text to search
            target_pos: Target position to search backward from
            search_window: Maximum chars to search backward (default 500)
        
        Returns:
            Position of sentence boundary, or target_pos if none found
        """
        search_start = max(target_pos - search_window, 0)
        chunk_text = text[search_start:target_pos]
        
        sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        best_break = -1
        
        for ending in sentence_endings:
            pos = chunk_text.rfind(ending)
            if pos > best_break:
                best_break = pos
        
        if best_break != -1:
            # Break after sentence ending (include punctuation + space)
            return search_start + best_break + 2  # +2 for punctuation and space
        
        return target_pos  # No boundary found, use target

    def _split_with_semantic_boundaries(
        self,
        text: str,
        max_size: int = 4800,
        overlap_size: int = 200
    ) -> List[tuple]:
        """
        Split text at semantic boundaries (paragraphs, tables, headings).
        
        Phase C.3: Semantic splitting with fallback to sentence boundaries.
        
        Args:
            text: Text to split
            max_size: Maximum chunk size in characters (default 4800)
            overlap_size: Overlap size for context (default 200)
        
        Returns:
            List of (chunk_text, chunk_start, chunk_end, actual_start) tuples
        """
        # Find all semantic boundaries
        semantic_boundaries = self._find_semantic_boundaries(text)
        
        chunks = []
        current_pos = 0
        text_len = len(text)
        
        while current_pos < text_len:
            # Calculate target chunk end
            target_end = min(current_pos + max_size, text_len)
            
            # Look for best semantic boundary near target_end
            best_boundary = None
            min_distance = float('inf')
            
            for boundary in semantic_boundaries:
                if current_pos < boundary <= target_end:
                    # Prefer boundaries closer to target_end (maximize chunk size)
                    distance = target_end - boundary
                    if distance < min_distance:
                        min_distance = distance
                        best_boundary = boundary
            
            if best_boundary:
                # Use semantic boundary (already safe - ends at closing tags)
                chunk_end = best_boundary
            elif target_end < text_len:
                # No semantic boundary found, fallback to sentence boundary
                chunk_end = self._find_sentence_boundary(text, target_end)
                
                # Phase C.4: Ensure chunk_end is not inside HTML tag
                chunk_end = self._find_safe_break_position(text, chunk_end)
            else:
                # End of text
                chunk_end = text_len
            
            # Include overlap from previous chunk for context
            if current_pos > 0 and current_pos >= overlap_size:
                actual_start = current_pos - overlap_size
            else:
                actual_start = 0
            
            # Extract chunk with overlap
            chunk_text = text[actual_start:chunk_end]
            
            if chunk_text.strip():
                chunks.append((chunk_text, current_pos, chunk_end, actual_start))
            
            # Move to next chunk (non-overlapping position)
            current_pos = chunk_end
        
        return chunks

    def _split_into_chunks_with_overlap(
        self, 
        text: str, 
        max_size: int = 4800, 
        overlap_size: int = 200
    ) -> List[tuple]:
        """
        Split text into overlapping chunks for better context preservation.
        
        Phase C: Advanced splitting with 200-char overlap between chunks.
        
        Args:
            text: Text to split
            max_size: Maximum chunk size in characters (default 4800)
            overlap_size: Number of characters to overlap between chunks (default 200)
        
        Returns:
            List of (chunk_text, chunk_start, chunk_end, actual_start) tuples
            - chunk_text: The text of this chunk (may include overlap from previous)
            - chunk_start: Start position in original text (non-overlapping part)
            - chunk_end: End position in original text
            - actual_start: Actual start position including overlap
        """
        chunks = []
        current_pos = 0
        text_len = len(text)
        
        while current_pos < text_len:
            # Calculate chunk end (max 4800 chars from current position)
            chunk_end = min(current_pos + max_size, text_len)
            
            # Find sentence boundary (same as Phase B)
            if chunk_end < text_len:
                search_start = max(chunk_end - 500, current_pos)
                chunk_text = text[search_start:chunk_end]
                
                sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
                best_break = -1
                
                for ending in sentence_endings:
                    pos = chunk_text.rfind(ending)
                    if pos > best_break:
                        best_break = pos
                
                if best_break != -1:
                    chunk_end = search_start + best_break + len(sentence_endings[0])
                
                # Phase C.4: Ensure not breaking inside HTML tag
                chunk_end = self._find_safe_break_position(text, chunk_end)
            
            # Include overlap from previous chunk for context
            if current_pos > 0 and current_pos >= overlap_size:
                # Include last 200 chars from previous chunk
                actual_start = current_pos - overlap_size
            else:
                # First chunk or overlap would go before start
                actual_start = 0
            
            # Extract chunk with overlap
            chunk_text = text[actual_start:chunk_end]
            
            if chunk_text.strip():
                # Store: (text, non_overlap_start, end, actual_start_with_overlap)
                chunks.append((chunk_text, current_pos, chunk_end, actual_start))
            
            # Move to next chunk (non-overlapping position)
            current_pos = chunk_end
        
        return chunks

    def _deduplicate_translated_overlaps(
        self,
        translated_chunks: List[str],
        chunk_info: List[tuple]
    ) -> str:
        """
        Remove overlapping regions from translated chunks.
        
        Phase C: Deduplication strategy for overlapped translations.
        
        Args:
            translated_chunks: List of translated chunk texts
            chunk_info: List of (original_text, start, end, actual_start) from splitting
        
        Returns:
            Deduplicated concatenated translation
        """
        if not translated_chunks:
            return ""
        
        result_parts = []
        
        for i, (translated, info) in enumerate(zip(translated_chunks, chunk_info)):
            _, chunk_start, chunk_end, actual_start = info
            
            if i == 0:
                # First chunk: use entire translation (no overlap to remove)
                result_parts.append(translated)
            else:
                # Calculate overlap in original text
                overlap_original = chunk_start - actual_start
                
                if overlap_original > 0:
                    # Calculate proportional overlap in translated text
                    # (translation may change length)
                    original_length = chunk_end - actual_start
                    if original_length > 0:
                        # Calculate ratio and proportional overlap
                        # Round down to avoid skipping too much
                        ratio = len(translated) / original_length
                        overlap_translated = int(overlap_original * ratio)
                        
                        # Ensure we don't skip the entire translation
                        overlap_translated = min(overlap_translated, len(translated) - 1)
                        
                        # Skip overlapping portion of translation
                        result_parts.append(translated[overlap_translated:])
                    else:
                        # Edge case: zero-length original (shouldn't happen)
                        result_parts.append(translated)
                else:
                    # No overlap (shouldn't happen for i > 0, but handle it)
                    result_parts.append(translated)
        
        return ''.join(result_parts)

    def _split_into_chunks(self, text: str, max_size: int = 4800) -> List[str]:
        """
        Split text into chunks of max_size, breaking at sentence boundaries.
        
        Phase B: Simple character-based splitting with sentence boundary detection.
        
        Args:
            text: Text to split
            max_size: Maximum chunk size in characters (default 4800)
        
        Returns:
            List of text chunks
        """
        chunks = []
        current_pos = 0
        text_len = len(text)
        
        while current_pos < text_len:
            # Calculate chunk end (max 4800 chars from current position)
            chunk_end = min(current_pos + max_size, text_len)
            
            # If not at end of document, find last sentence boundary
            if chunk_end < text_len:
                # Look for sentence endings: . ! ? followed by space or newline
                # Search backward from chunk_end (max 500 chars back)
                search_start = max(chunk_end - 500, current_pos)
                chunk_text = text[search_start:chunk_end]
                
                # Find last sentence boundary
                sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
                best_break = -1
                
                for ending in sentence_endings:
                    pos = chunk_text.rfind(ending)
                    if pos > best_break:
                        best_break = pos
                
                if best_break != -1:
                    # Break after sentence ending (include punctuation + space)
                    chunk_end = search_start + best_break + len(sentence_endings[0])
                # else: No sentence boundary found, use hard break at max_size
            
            # Extract chunk
            chunk = text[current_pos:chunk_end]
            if chunk.strip():  # Skip empty chunks
                chunks.append(chunk)
            
            # Move to next chunk
            current_pos = chunk_end
        
        return chunks

    def translate_text_chunked(
        self,
        text: str,
        from_lang: str = 'auto',
        to_lang: str = 'pt',
        progress_callback: Optional[Callable[[int, int, int, str], None]] = None,
        max_chunk_size: int = 4800,
        use_overlap: bool = True,
        use_semantic_splitting: bool = True
    ) -> TranslationResult:
        """
        Translate text with automatic chunking for large documents.
        
        Phase B: Basic pagination with progress tracking.
        Phase C: Advanced features (overlap, semantic splitting).
        
        Args:
            text: Text to translate
            from_lang: Source language code ('auto' for auto-detect)
            to_lang: Target language code
            progress_callback: Optional callback function(current_chunk, total_chunks, percentage, status_msg)
            max_chunk_size: Maximum characters per chunk (default 4800)
            use_overlap: Use 200-char context overlap between chunks (default True, Phase C.2)
            use_semantic_splitting: Use semantic boundaries (paragraphs, tables) for splitting (default True, Phase C.3)
        
        Returns:
            TranslationResult with concatenated translation
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
        
        # Phase C.3: Semantic splitting (highest quality)
        if use_semantic_splitting and use_overlap:
            chunk_data = self._split_with_semantic_boundaries(text, max_chunk_size, overlap_size=200)
            chunks = [chunk_text for chunk_text, _, _, _ in chunk_data]
        elif use_overlap:
            # Phase C.2: Overlap without semantic (fallback)
            chunk_data = self._split_into_chunks_with_overlap(text, max_chunk_size, overlap_size=200)
            chunks = [chunk_text for chunk_text, _, _, _ in chunk_data]
        else:
            # Phase B: Simple splitting (backward compatibility)
            chunks = self._split_into_chunks(text, max_chunk_size)
            chunk_data = None
        
        total_chunks = len(chunks)
        
        # Progress callback: Preparation phase
        if progress_callback:
            try:
                progress_callback(0, total_chunks, 0, f"Preparing translation... ({total_chunks} chunks)")
            except Exception:
                pass  # Don't let callback errors abort translation
        
        # Translate each chunk sequentially
        translated_chunks = []
        detected_source_lang = from_lang
        
        for i, chunk in enumerate(chunks, start=1):
            # Update progress: Starting chunk
            percentage = int((i - 1) / total_chunks * 100)
            if progress_callback:
                try:
                    progress_callback(
                        i, total_chunks, percentage,
                        f"Translating chunk {i}/{total_chunks}... ({len(chunk)} chars)"
                    )
                except Exception:
                    pass
            
            # Translate chunk with retry mechanism (3 attempts)
            max_attempts = 3
            last_error = ""
            chunk_result = None
            
            for attempt in range(max_attempts):
                chunk_result = self._translate_request(chunk, from_lang, to_lang)
                
                if chunk_result.success:
                    break
                
                last_error = chunk_result.error_message
                
                # Wait before retry (exponential backoff)
                if attempt < max_attempts - 1:
                    time.sleep(1.0 * (attempt + 1))
            
            # Check if chunk translation succeeded
            if not chunk_result or not chunk_result.success:
                # Phase C.5: Enhanced error with context
                chunk_preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
                
                # Get chunk position info if using overlap/semantic
                if chunk_data:
                    _, chunk_start, chunk_end, _ = chunk_data[i-1]
                else:
                    # Estimate positions for simple chunking
                    chunk_start = (i - 1) * max_chunk_size
                    chunk_end = chunk_start + len(chunk)
                
                # Create detailed error
                error = ChunkTranslationError(
                    chunk_number=i,
                    total_chunks=total_chunks,
                    chunk_start=chunk_start,
                    chunk_end=chunk_end,
                    chunk_preview=chunk_preview,
                    attempts=max_attempts,
                    last_error=last_error
                )
                
                # Return result with enhanced error message
                return TranslationResult(
                    success=False,
                    error_message=str(error)
                )
            
            # Store translated chunk
            translated_chunks.append(chunk_result.translated_text)
            
            # Capture detected language from first chunk
            if i == 1 and chunk_result.source_language:
                detected_source_lang = chunk_result.source_language
            
            # Rate limiting between chunks (avoid being blocked)
            if i < total_chunks:
                time.sleep(0.5)
        
        # Progress callback: Completion
        if progress_callback:
            try:
                progress_callback(
                    total_chunks, total_chunks, 100,
                    f"Translation complete! (Processed {total_chunks} chunks)"
                )
            except Exception:
                pass
        
        # Phase C: Deduplicate overlaps, or simple concatenation
        if use_overlap and chunk_data:
            translated_text = self._deduplicate_translated_overlaps(translated_chunks, chunk_data)
        else:
            translated_text = ''.join(translated_chunks)
        
        return TranslationResult(
            success=True,
            translated_text=translated_text,
            source_language=detected_source_lang,
            target_language=to_lang,
            from_cache=False
        )

    def translate_text(self, text: str, from_lang: str = 'auto', to_lang: str = 'pt') -> TranslationResult:
        """
        Translate text with caching and retry mechanism.
        
        Phase B: Automatically uses chunking for large texts (> 4500 chars).

        Args:
            text: Text to translate
            from_lang: Source language code ('auto' for auto-detect)
            to_lang: Target language code

        Returns:
            TranslationResult with translation status and result
        """
        # Phase B: Automatic chunking for large documents
        if len(text) > 4500:
            # Use chunked translation (no progress callback in automatic mode)
            return self.translate_text_chunked(text, from_lang, to_lang, progress_callback=None)
        
        # Original logic for small texts (< 4500 chars)
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
