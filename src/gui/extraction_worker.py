#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExtractionWorker - Background worker for Text to JSON Converter operations.

Runs extraction operations in a separate thread to keep the UI responsive
and allow progress dialog updates.

Created: 2026-02-03 (Programmer #3)
Pattern: Based on FileExplorerWorker (file_explorer_worker.py)
"""

from PySide6.QtCore import QObject, Signal

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
    
    def __init__(self, extractor):
        """
        Initialize worker with extractor instance.
        
        Args:
            extractor: AdvancedExtractor instance (already configured)
        """
        super().__init__()
        self.extractor = extractor
        self._cancel_requested = False
    
    def execute_extraction(self, path: str = None, text_content: str = None,
                          input_type_index: int = 0,
                          typescript_export: bool = False,
                          with_quotation_marks: bool = True,
                          indent: int = 2):
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
            
            # Text mode
            if input_type_index == 2 and text_content:
                logger.debug("Processing text directly")
                self.progress.emit("Processing text input...")
                
                path_lines, merged_json = self.extractor.process_text("TextInput", text_content)
                text_output = "\n".join(path_lines)
                
                # Format JSON
                if merged_json:
                    if typescript_export:
                        json_output = self.extractor.json_to_typescript(merged_json, "ExtractedData", indent)
                    elif with_quotation_marks:
                        json_output = json.dumps(merged_json, indent=indent, ensure_ascii=False)
                    else:
                        json_output = self.extractor.json_to_js_literal(merged_json, indent=indent)
                else:
                    json_output = None
                
                self.finished.emit(text_output or "", json_output or "")
            
            # Directory/File mode
            elif path:
                import os
                logger.debug(f"Processing path: {path}")
                
                # Count total files to process
                if os.path.isdir(path):
                    file_extensions = self.extractor.file_extensions
                    total_files = 0
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if any(file.endswith(ext) for ext in file_extensions):
                                total_files += 1
                    logger.debug(f"Found {total_files} files to process")
                else:
                    total_files = 1
                
                # Track progress during extraction
                processed = 0
                
                # Hook into extractor's file processing
                original_process_file = self.extractor._process_single_file if hasattr(self.extractor, '_process_single_file') else None
                
                def progress_wrapper(file_path):
                    nonlocal processed
                    processed += 1
                    filename = os.path.basename(file_path)
                    self.progress.emit(f"Processing: {filename}")
                    self.progress_detailed.emit(processed, total_files, filename)
                    if original_process_file:
                        return original_process_file(file_path)
                    return None
                
                # Apply wrapper if method exists
                if original_process_file:
                    self.extractor._process_single_file = progress_wrapper
                
                # Run extraction
                text_output, json_output = self.extractor.run(path)
                
                # Restore original method
                if original_process_file:
                    self.extractor._process_single_file = original_process_file
                
                self.finished.emit(text_output or "", json_output or "")
            
            else:
                self.error.emit("No input provided")
            
        except Exception as e:
            logger.error(f"Extraction error: {str(e)}", exc_info=True)
            self.error.emit(str(e))
