#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Set Operation Executor - Core execution logic component

Extracted from set_operations_dock.py (v2.9.114 - Phase 2.3.3)
Handles validation, file loading, operation execution, and statistics.

Features:
- File validation and loading with security checks
- Operation execution (intersection, union, difference, symmetric)
- Statistics calculation
- Result formatting
- Error handling
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from src.document_set_loader import load_document_set, validate_document_set_path

from src.set_operations import (
    difference,
    intersection,
    symmetric_difference,
    union,
)


# pylint: disable=too-few-public-methods  # Data container class
class ExecutionResult:
    """Container for execution results and metadata."""

    # pylint: disable=too-many-positional-arguments  # Data container initialization
    def __init__(
        self,
        success: bool,
        results: Dict[str, Any] = None,
        stats_lines: List[str] = None,
        file_a_data: Dict = None,
        file_b_data: Dict = None,
        error: str = None
    ):
        """
        Initialize execution result.

        Args:
            success: Whether execution was successful
            results: Operation results dictionary
            stats_lines: Statistics text lines
            file_a_data: First file data (for diff viewer)
            file_b_data: Second file data (for diff viewer)
            error: Error message if failed
        """
        self.success = success
        self.results = results or {}
        self.stats_lines = stats_lines or []
        self.file_a_data = file_a_data or {}
        self.file_b_data = file_b_data or {}
        self.error = error


class SetOperationExecutor:
    """Executor for set operations on JSON files."""

    @staticmethod
    def validate_and_load_files(file_paths: List[str]) -> Tuple[bool, List[Dict], str]:
        """
        Validate and load JSON files with security checks.

        Args:
            file_paths: List of file paths to load

        Returns:
            Tuple of (success, file_dicts, error_message)
        """
        if len(file_paths) < 2:
            return False, [], "Please select at least 2 JSON files."

        file_dicts = []

        try:
            for file_path in file_paths:
                # Security validation (CWE-22)
                if not validate_document_set_path(file_path):
                    return False, [], (
                        f"Invalid or insecure file path:\n{file_path}\n\n"
                        "File must exist, be at most 50 MiB, and use JSON, TXT, "
                        "DOCX, ODT, IPYNB, or PDF format."
                    )

                file_dicts.append(load_document_set(file_path))

            return True, file_dicts, ""

        except FileNotFoundError as e:
            return False, [], f"File not found: {e.filename}"
        except Exception as e:  # pylint: disable=broad-exception-caught  # File loading robustness
            return False, [], f"Error loading files: {e}"

    @staticmethod
    def execute_operations(
        file_dicts: List[Dict],
        operations: List[str],
        comparison_mode: str,
        options: Dict[str, bool]
    ) -> ExecutionResult:
        """
        Execute set operations on loaded file data.

        Args:
            file_dicts: List of loaded JSON dictionaries
            operations: List of operation symbols ('∩', '∪', '−', '⊕')
            comparison_mode: Comparison mode string
            options: Operation options dictionary

        Returns:
            ExecutionResult with results or error
        """
        if not operations:
            return ExecutionResult(
                success=False,
                error="Please select at least one operation."
            )

        # Convert comparison mode for set_operations module
        if comparison_mode == "full_path":
            comparison_mode = "full_path_value"

        # Prepare options
        exec_options = {
            "comparison_mode": comparison_mode,
            **options
        }

        results = {}
        stats_lines = []

        try:
            # Execute each selected operation
            if '∩' in operations:
                result = intersection(file_dicts, **exec_options)
                results["intersection"] = result
                count = len(result.get("intersection", []))
                stats_lines.append(f"✓ Intersection: {count} items")

            if '∪' in operations:
                result = union(file_dicts, **exec_options)
                results["union"] = result
                count = len(result.get("union", []))
                stats_lines.append(f"✓ Union: {count} items")

            if '−' in operations:
                result = difference(file_dicts, **exec_options)
                results["difference"] = result
                count = len(result.get("difference", []))
                stats_lines.append(f"✓ Difference: {count} items")

            if '⊕' in operations:
                if len(file_dicts) < 2:
                    return ExecutionResult(
                        success=False,
                        error="Symmetric difference requires at least 2 files."
                    )
                result = symmetric_difference(file_dicts[0], file_dicts[1], **exec_options)
                results["symmetric_difference"] = result
                count = len(result.get("symmetric_difference", []))
                stats_lines.append(f"✓ Symmetric Difference: {count} items")

            # Store original data for diff viewer
            file_a_data = file_dicts[0] if len(file_dicts) > 0 else {}
            file_b_data = file_dicts[1] if len(file_dicts) > 1 else {}

            return ExecutionResult(
                success=True,
                results=results,
                stats_lines=stats_lines,
                file_a_data=file_a_data,
                file_b_data=file_b_data
            )

        except Exception as e:  # pylint: disable=broad-exception-caught  # Operation execution robustness
            return ExecutionResult(
                success=False,
                error=f"Error executing operations: {e}"
            )

    @staticmethod
    def format_results_json(results: Dict[str, Any]) -> str:
        """
        Format results as pretty JSON string.

        Args:
            results: Results dictionary

        Returns:
            Formatted JSON string
        """
        return json.dumps(results, indent=2, ensure_ascii=False)

    @staticmethod
    def calculate_result_count(results: Dict[str, Any]) -> int:
        """
        Calculate total count of items in all results.

        Args:
            results: Results dictionary

        Returns:
            Total item count
        """
        try:
            return sum(
                len(r.get(list(r.keys())[0], []))
                for r in results.values()
                if r and isinstance(r, dict)
            )
        except Exception:  # pylint: disable=broad-exception-caught  # Stats calculation robustness
            return 0


__all__ = ['SetOperationExecutor', 'ExecutionResult']
