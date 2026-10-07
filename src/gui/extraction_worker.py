#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExtractionWorker - Background worker for Text to JSON Converter operations.

Runs extraction operations in a separate thread to keep the UI responsive
and allow progress dialog updates.

Created: 2026-02-03 (Programmer #3)
Pattern: Based on FileExplorerWorker (file_explorer_worker.py)
"""

import os
import threading

from PySide6.QtCore import QObject, Signal, Slot

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExtractionWorker(QObject):
    """
    Worker for running extraction operations in background thread.
    
    This worker wraps AdvancedExtractor operations and provides progress
    updates to allow tracking in the UI thread.
    
    Signals:
        progress: Progress message (file being processed)
        progress_detailed: Detailed progress (current, total, message)
        finished: Operation completed (emits text_output, json_output)
        error: Operation failed (emits error message)
    
    Threading:
        - Created in UI thread
        - Moved to worker thread with moveToThread()
        - Slots execute in worker thread
        - Signals received in UI thread
    """
    
    # Signals
    progress = Signal(str)                      # Current file/message
    progress_detailed = Signal(int, int, str)   # (current, total, message)
    finished = Signal(str, str)                 # (text_output, json_output)
    error = Signal(str)                         # Error message
    cancelled = Signal()
    MAX_DISCOVERED_FILES = 100_000
    
    def __init__(self, extractor):
        """
        Initialize worker with extractor instance.
        
        Args:
            extractor: AdvancedExtractor instance (already configured)
        """
        super().__init__()
        self.extractor = extractor
        self._cancel_event = threading.Event()
        self._operation = None

    @property
    def is_cancelled(self) -> bool:
        """Return whether cooperative cancellation was requested."""
        return self._cancel_event.is_set()

    def cancel(self) -> None:
        """Request cancellation at the next safe checkpoint."""
        self._cancel_event.set()

    def _stop_if_cancelled(self) -> bool:
        if not self.is_cancelled:
            return False
        self.cancelled.emit()
        return True

    def _discover_files(self, path, patterns):
        """Discover matching files with cancellation checkpoints."""
        if os.path.isfile(path):
            return [path]

        files = []
        for root, _directories, filenames in os.walk(path):
            if self.is_cancelled:
                return None
            for filename in filenames:
                if self.is_cancelled:
                    return None
                if not patterns or any(filename.endswith(pattern) for pattern in patterns):
                    files.append(os.path.join(root, filename))
                    if len(files) > self.MAX_DISCOVERED_FILES:
                        raise RuntimeError(
                            "Extraction exceeds the "
                            f"{self.MAX_DISCOVERED_FILES}-file safety limit"
                        )
        return files

    def configure_operation(
        self,
        path=None,
        text_content=None,
        input_type_index=0,
        with_quotation_marks=True,
        indent=2,
    ) -> None:
        """Capture immutable inputs before the worker moves to its thread."""
        self._operation = (
            path,
            text_content,
            input_type_index,
            with_quotation_marks,
            indent,
        )

    @Slot()
    def execute_configured(self) -> None:
        """Execute the configured operation with QObject thread affinity."""
        if self._operation is None:
            self.error.emit("Extraction operation was not configured")
            return
        self.execute_extraction(*self._operation)
    
    def execute_extraction(
        self,
        path: str = None,
        text_content: str = None,
        input_type_index: int = 0,
        with_quotation_marks: bool = True,
        indent: int = 2,
    ):
        """
        Execute extraction operation in worker thread.
        
        Args:
            path: File/directory path (None for Text mode)
            text_content: Text content (None for Directory/File mode)
            input_type_index: 0=Directory, 1=File, 2=Text
            typescript_export: Export as TypeScript
            with_quotation_marks: Include quotes in JSON keys
            indent: JSON indentation level
        """
        try:
            import json
            logger.debug(f"Worker.execute_extraction() | path={path}, input_type={input_type_index}")

            if self._stop_if_cancelled():
                return
            
            # Text mode
            if input_type_index == 2 and text_content:
                logger.debug("Processing text directly")
                self.progress.emit("Processing text input...")

                if self._stop_if_cancelled():
                    return
                path_lines, merged_json = self.extractor.process_text("TextInput", text_content)
                if self._stop_if_cancelled():
                    return
                text_output = "\n".join(path_lines)
                
                # Format JSON
                if merged_json:
                    '''
                    if typescript_export:
                        json_output = self.extractor.json_to_typescript(merged_json, "ExtractedData")
                    '''
                    if with_quotation_marks:
                        json_output = json.dumps(merged_json, indent=indent, ensure_ascii=False)
                    else:
                        json_output = self.extractor.json_to_js_literal(merged_json, indent=indent)
                else:
                    json_output = None
                
                self.finished.emit(text_output or "", json_output or "")
            
            # Directory/File mode
            elif path:
                logger.debug(f"Processing path: {path}")

                # Pre-scan to count total files
                file_extensions = self.extractor.file_extensions
                all_files = self._discover_files(path, file_extensions)
                if all_files is None or self._stop_if_cancelled():
                    return
                total_files = len(all_files)
                logger.debug(f"Found {total_files} files to process")

                # Emit initial progress
                self.progress.emit(f"Starting extraction...")
                self.progress_detailed.emit(0, total_files, "Initializing...")
                
                # Process files manually to emit progress
                from src.extractors.advanced_extractor import read_text
                import re
                import json
                
                all_lines = []
                merged_json = {}
                
                for idx, fp in enumerate(all_files, 1):
                    # Check for cancellation FIRST
                    if self.is_cancelled:
                        logger.info(f"Extraction canceled by user at file {idx}/{total_files}")
                        self.cancelled.emit()
                        return
                    
                    # Emit progress for each file
                    filename = os.path.basename(fp)
                    self.progress.emit(f"Processing: {filename}")
                    self.progress_detailed.emit(idx, total_files, filename)
                    
                    try:
                        text = read_text(fp)
                    except Exception as e:
                        all_lines.append(f"<<ERROR reading {fp}: {e}>>")
                        continue

                    if self._stop_if_cancelled():
                        return
                    # Derive file-root token from filename
                    base = os.path.splitext(os.path.basename(fp))[0]
                    
                    # Try to find exported component/function name
                    export_m = re.search(r'\bexport\s+default\s+function\s+([A-Za-z_]\w*)', text)
                    if not export_m:
                        export_m = re.search(r'\bexport\s+default\s+([A-Za-z_]\w*)\b', text)
                    
                    if export_m:
                        file_root = export_m.group(1)
                    else:
                        # Fallback: Pascalize filename
                        file_root = base[0:1].upper() + base[1:]
                    
                    lines, j = self.extractor.process_text(file_root, text)

                    if self._stop_if_cancelled():
                        return
                    if lines:
                        all_lines.append(f"# File: {fp}")
                        all_lines.extend(lines)
                    
                    if self.extractor.convert_to_json and j:
                        merged_json = self.extractor.deep_merge(merged_json, j)
                
                # Format results
                result_text = "\n".join(all_lines) if all_lines else "(no matches)"
                
                if self.extractor.convert_to_json:
                    # TypeScript export feature commented out (not implemented yet)
                    # if typescript_export:
                    #     json_output = self.extractor.json_to_typescript(merged_json, "ExtractedData")
                    if with_quotation_marks:
                        json_output = json.dumps(merged_json, ensure_ascii=False, indent=indent)
                    else:
                        json_output = self.extractor.json_to_js_literal(merged_json, indent=indent)
                else:
                    json_output = None
                
                self.finished.emit(result_text, json_output or "")
            
            else:
                self.error.emit("No input provided")
            
        except Exception as e:
            if self._stop_if_cancelled():
                return
            logger.error(f"Extraction error: {str(e)}", exc_info=True)
            self.error.emit(str(e))
