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

from ...core.file_explorer_executor import FileExplorerExecutor


class FileExplorerWorker(QObject):
    """
    Worker for running File Explorer operations in background thread.
    
    This worker wraps FileExplorerExecutor operations and forwards their
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
    
    def __init__(self, executor: FileExplorerExecutor):
        """
        Initialize worker with executor instance.
        
        Args:
            executor: FileExplorerExecutor instance to use for operations
                     (already configured with all necessary settings)
        """
        super().__init__()
        self.executor = executor
    
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
            # Forward executor signals to worker signals
            # This allows UI thread to receive progress updates
            self.executor.progress.connect(self.progress)
            self.executor.progress_detailed.connect(self.progress_detailed)
            
            # Execute search (blocking in worker thread)
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
            
            # Emit result to UI thread
            self.finished.emit(result)
            
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
