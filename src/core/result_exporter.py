#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Result Exporter - Export and save results component

Extracted from set_operations_dock.py (v2.9.114 - Phase 2.3.4)
Handles saving and exporting operation results in multiple formats.

Features:
- Save results as JSON
- Export to CSV, Excel, YAML, TOML
- Format detection and extension handling
- Error handling for missing dependencies
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class ResultExporter:
    """Handles saving and exporting operation results."""

    # Format mapping
    FORMAT_MAP = {
        "CSV Files (*.csv)": "csv",
        "Excel Files (*.xlsx)": "xlsx",
        "YAML Files (*.yaml)": "yaml",
        "TOML Files (*.toml)": "toml",
        "JSON Files (*.json)": "json"
    }

    # Format filters for file dialog
    FORMAT_FILTER = (
        "CSV Files (*.csv);;Excel Files (*.xlsx);;"
        "YAML Files (*.yaml);;TOML Files (*.toml);;JSON Files (*.json)"
    )

    @staticmethod
    def save_json(data: str, file_path: str) -> Tuple[bool, str]:
        """
        Save JSON text to file.

        Args:
            data: JSON text string
            file_path: Target file path

        Returns:
            Tuple of (success, message)
        """
        if not data:
            return False, "No data to save"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(data)
            return True, f"Results saved to:\n{file_path}"
        except Exception as e:  # pylint: disable=broad-exception-caught  # File save robustness
            return False, f"Error saving file: {e}"

    @staticmethod
    def export_multi_format(
        data: Dict[str, Any],
        file_path: str,
        selected_filter: str,
        parent_widget: 'QWidget' | None = None
    ) -> Tuple[bool, str]:
        """
        Export results to multiple formats.

        Args:
            data: Result data dictionary
            file_path: Target file path
            selected_filter: Selected format filter from dialog
            parent_widget: Parent widget for progress modal (optional)

        Returns:
            Tuple of (success, message)
        """
        if not data:
            return False, "No data to export"

        try:
            # Determine format from filter
            export_format = ResultExporter.FORMAT_MAP.get(selected_filter, "json")

            # Ensure correct extension
            path = Path(file_path)
            if not path.suffix:
                path = path.with_suffix(f".{export_format}")

            # Export using ExportManager
            from ..export_manager import ExportManager  # pylint: disable=import-outside-toplevel  # Lazy import

            ExportManager.export(
                data=data,
                output_path=path,
                format=export_format,
                flatten=True,  # Flatten for CSV/Excel/TOML
                include_metadata=True,  # Add timestamp + operation type
                parent_widget=parent_widget  # Pass parent for progress modal
            )

            return True, f"Results exported to:\n{path}"

        except ImportError as e:
            return False, f"Missing dependency:\n{e}\n\nInstall with: pip install openpyxl tomli-w"
        except Exception as e:  # pylint: disable=broad-exception-caught  # Export robustness
            return False, f"Export failed: {e}"

    @staticmethod
    def validate_export_data(data: Any) -> Tuple[bool, str]:
        """
        Validate data before export.

        Args:
            data: Data to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if data is None:
            return False, "No results to export. Please execute an operation first."

        if not data:
            return False, "Empty results. Nothing to export."

        return True, ""

    @staticmethod
    def get_format_from_filter(selected_filter: str) -> str:
        """
        Get format code from filter string.

        Args:
            selected_filter: Filter string from QFileDialog

        Returns:
            Format code (csv, xlsx, yaml, toml, json)
        """
        return ResultExporter.FORMAT_MAP.get(selected_filter, "json")

    @staticmethod
    def ensure_extension(file_path: str, format_code: str) -> Path:
        """
        Ensure file has correct extension.

        Args:
            file_path: Original file path
            format_code: Format code (csv, xlsx, etc.)

        Returns:
            Path with correct extension
        """
        path = Path(file_path)
        if not path.suffix:
            path = path.with_suffix(f".{format_code}")
        return path

    @staticmethod
    def save_json_dict(data: Dict[str, Any], file_path: str) -> Tuple[bool, str]:
        """
        Save dictionary as JSON file.

        Args:
            data: Dictionary to save
            file_path: Target file path

        Returns:
            Tuple of (success, message)
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True, f"Results saved to:\n{file_path}"
        except Exception as e:  # pylint: disable=broad-exception-caught  # File save robustness
            return False, f"Error saving file: {e}"

    @staticmethod
    def format_json_for_display(data: Dict[str, Any]) -> str:
        """
        Format dictionary as pretty JSON for display.

        Args:
            data: Dictionary to format

        Returns:
            Formatted JSON string
        """
        return json.dumps(data, indent=2, ensure_ascii=False)


__all__ = ['ResultExporter']
