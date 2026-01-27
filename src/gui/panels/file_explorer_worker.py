#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FileExplorerWorker - Background worker for File Explorer operations.

Runs search, browse, and replace operations in a separate thread to keep
the UI responsive and allow progress dialog updates.

Created: 2026-01-12 (v2.9.122)
Pattern: Based on SearchWorker (search_worker.py)
Author: GitHub Copilot CLI (following Protocolo Simplicidade 3)
"""

from PySide6.QtCore import QObject, Signal

from ...core.file_explorer_executor import UnifiedFileExplorerExecutor
from ...utils.logger import get_logger

logger = get_logger(__name__)


class FileExplorerWorker(QObject):
    """
    Worker for running File Explorer operations in background thread.
    
    This worker wraps UnifiedFileExplorerExecutor operations and forwards their
    signals to allow progress tracking in the UI thread. It follows the
    same pattern as SearchWorker for consistency.
    
    Signals:
        progress: Simple progress message (file being processed)
        progress_detailed: Detailed progress (current, total, message)
        finished: Operation completed successfully (emits result)
        error: Operation failed (emits error message)
    
    Threading:
        - Created in UI thread
        - Moved to worker thread with moveToThread()
        - Slots execute in worker thread
        - Signals received in UI thread
    
    Version: v2.9.122
    """
    
    # Signals
    progress = Signal(str)                      # Current file/message
    progress_detailed = Signal(int, int, str)   # (current, total, message)
    finished = Signal(object)                   # Result object
    error = Signal(str)                         # Error message
    
    # Batch processing signal (v2.9.123)
    batch_ready = Signal(list, int, int)        # (batch_items, batch_num, total_batches)
    
    def __init__(self, executor: UnifiedFileExplorerExecutor):
        """
        Initialize worker with executor instance.
        
        Args:
            executor: UnifiedFileExplorerExecutor instance to use for operations
                     (already configured with all necessary settings)
        """
        super().__init__()
        self.executor = executor
        self._cancel_requested = False  # For cancellation support (v2.9.123)
    
    def _build_matches_dict(self, result: dict) -> dict:
        """
        Build matches dictionary from executor result.
        
        This runs in WORKER THREAD to avoid blocking UI.
        
        Args:
            result: Result dict from executor with 'files' key
        
        Returns:
            Dict mapping file_path → list of (line, col, snippet) tuples
        
        Version: v2.9.123
        """
        matches_dict = {}
        
        for search_result in result.get("files", []):
            file_info = search_result.file_info
            file_path = file_info.path
            
            if search_result.matches:
                # Content search: collect all matches
                matches_list = []
                for match in search_result.matches:
                    snippet = match.snippet if hasattr(match, "snippet") else ""
                    matches_list.append((match.line, match.col, snippet))
                matches_dict[file_path] = matches_list
            else:
                # Filename search: show file with line 1
                matches_dict[file_path] = [(1, 0, f"📄 {file_info.name}")]
        
        return matches_dict
    
    def _emit_in_batches(self, matches_dict: dict, batch_size: int = 100):
        """
        Emit matches dictionary in batches to avoid blocking UI.
        
        This allows UI to process items incrementally while keeping
        the event loop responsive.
        
        Args:
            matches_dict: Complete matches dictionary
            batch_size: Number of items per batch (default: 100)
        
        Version: v2.9.123
        """
        # Convert dict to list of items for batching
        all_items = list(matches_dict.items())
        total_items = len(all_items)
        
        if total_items == 0:
            logger.debug("No items to emit")
            return  # Nothing to emit
        
        # Calculate number of batches
        total_batches = (total_items + batch_size - 1) // batch_size  # Ceiling division
        
        logger.debug("Emitting %d items in %d batches of %d", total_items, total_batches, batch_size)
        
        # Emit batches
        for batch_num in range(total_batches):
            # Check for cancellation
            if self._cancel_requested:
                logger.debug("Cancellation requested, stopping batch emission at %d/%d", batch_num+1, total_batches)
                break
            
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, total_items)
            
            batch = all_items[start_idx:end_idx]
            
            logger.debug("Emitting batch %d/%d (%d items)", batch_num+1, total_batches, len(batch))
            self.batch_ready.emit(batch, batch_num + 1, total_batches)
    
    def execute_search(
        self,
        directory: str,
        filename_pattern: str,
        content_query: str,
        search_options: dict,
        show_hidden: bool,
        recursive: bool,
        filters: dict,
        conditions: list
    ):
        """
        Execute search operation in worker thread.
        
        This method runs in the worker thread. It connects executor signals
        to worker signals so progress updates reach the UI thread.
        
        Args:
            directory: Root directory to search
            filename_pattern: Filename pattern (wildcards)
            content_query: Content to search for
            search_options: Search options dict
            show_hidden: Show hidden files
            recursive: Search recursively
            filters: Filters dict
            conditions: Advanced conditions list
        """
        try:
            logger.debug("Worker.execute_search() called - running in thread")
            # Forward executor signals to worker signals
            # This allows UI thread to receive progress updates
            self.executor.progress.connect(self.progress)
            self.executor.progress_detailed.connect(self.progress_detailed)
            logger.debug("Executor signals connected to worker")
            
            # Execute search (blocking in worker thread)
            logger.debug("Calling executor.execute_search(directory=%s)", directory)
            result = self.executor.execute_search(
                directory=directory,
                filename_pattern=filename_pattern,
                content_query=content_query,
                search_options=search_options,
                show_hidden=show_hidden,
                recursive=recursive,
                filters=filters,
                conditions=conditions
            )
            logger.debug("Search complete! Found %d files", len(result.get('files', [])))
            
            # NEW v2.9.123: Process results in worker thread
            logger.debug("Building matches dict in worker thread")
            matches_dict = self._build_matches_dict(result)
            logger.debug("Built matches dict with %d entries", len(matches_dict))
            
            # NEW v2.9.123: Emit in batches for non-blocking UI
            logger.debug("Emitting matches in batches")
            self._emit_in_batches(matches_dict, batch_size=100)
            
            # Emit finished with original result (for stats, history, etc.)
            logger.debug("Emitting finished signal")
            self.finished.emit(result)
            logger.debug("Finished signal emitted")
            
        except Exception as e:
            # Emit error to UI thread
            self.error.emit(str(e))
        
        finally:
            # Disconnect signals to prevent memory leaks
            try:
                self.executor.progress.disconnect(self.progress)
                self.executor.progress_detailed.disconnect(self.progress_detailed)
            except:
                pass  # Already disconnected or never connected
    
    def execute_browse(
        self,
        directory: str,
        show_hidden: bool,
        recursive: bool,
        filters: dict
    ):
        """
        Execute browse operation in worker thread.
        
        Args:
            directory: Directory to browse
            show_hidden: Show hidden files
            recursive: Browse recursively
            filters: Filters dict
        """
        try:
            # Forward signals
            self.executor.progress.connect(self.progress)
            self.executor.progress_detailed.connect(self.progress_detailed)
            
            # Execute browse (blocking in worker thread)
            result = self.executor.execute_browse(
                directory=directory,
                show_hidden=show_hidden,
                recursive=recursive,
                filters=filters
            )
            
            # Emit result to UI thread
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
        
        finally:
            try:
                self.executor.progress.disconnect(self.progress)
                self.executor.progress_detailed.disconnect(self.progress_detailed)
            except:
                pass
    
    def execute_replace(
        self,
        files: list,
        search_text: str,
        replace_text: str,
        search_options: dict
    ):
        """
        Execute replace operation in worker thread.
        
        Args:
            files: List of file paths to process
            search_text: Text to search for
            replace_text: Replacement text
            search_options: Search options dict
        """
        try:
            # Forward signals (replace only uses simple progress)
            self.executor.progress.connect(self.progress)
            
            # Execute replace (blocking in worker thread)
            result = self.executor.execute_replace(
                files=files,
                search_text=search_text,
                replace_text=replace_text,
                search_options=search_options
            )
            
            # Emit result to UI thread
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
        
        finally:
            try:
                self.executor.progress.disconnect(self.progress)
            except:
                pass
