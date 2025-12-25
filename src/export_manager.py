"""
Export Manager Module

Multi-format export for JSON data (CSV, Excel, YAML, TOML).
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import openpyxl  # type: ignore[import-not-found]  # Optional dependency
    from openpyxl.styles import Font, PatternFill  # type: ignore[import-not-found]
    _EXCEL_AVAILABLE = True
except ImportError:
    _EXCEL_AVAILABLE = False

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

try:
    import tomli_w
    _TOML_AVAILABLE = True
except ImportError:
    _TOML_AVAILABLE = False


class ExportManager:
    """
    Export JSON data to multiple formats.
    
    Supported formats:
    - CSV (flat key-value pairs)
    - Excel (XLSX with formatting)
    - YAML
    - TOML
    - JSON (pretty-printed)
    """
    
    @staticmethod
    def flatten_dict(data: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """
        Flatten nested dictionary with dot notation.
        
        Args:
            data: Nested dictionary
            parent_key: Parent key prefix
            sep: Separator for keys (default: '.')
            
        Returns:
            Flattened dictionary
            
        Example:
            {'a': {'b': {'c': 1}}} → {'a.b.c': 1}
        """
        items = []
        
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(ExportManager.flatten_dict(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                # Convert list to string representation
                items.append((new_key, json.dumps(value, ensure_ascii=False)))
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    @staticmethod
    def add_metadata(data: Dict, operation: str = "export") -> Dict:
        """
        Add export metadata to data.
        
        Args:
            data: Original data
            operation: Operation type (e.g., "intersection", "union")
            
        Returns:
            Data with metadata
        """
        metadata = {
            '_metadata': {
                'exported_at': datetime.now().isoformat(),
                'operation': operation,
                'export_tool': 'Clarify v2.9.93'
            }
        }
        
        return {**metadata, **data}
    
    @staticmethod
    def export_to_csv(
        data: Dict,
        output_path: Path,
        flatten: bool = True,
        include_metadata: bool = True
    ) -> None:
        """
        Export to CSV format.
        
        Args:
            data: Dictionary to export
            output_path: Output file path
            flatten: Flatten nested keys with dot notation
            include_metadata: Add export metadata
        """
        if include_metadata:
            data = ExportManager.add_metadata(data, "export")
        
        if flatten:
            data = ExportManager.flatten_dict(data)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Key', 'Value'])
            
            for key, value in data.items():
                # Handle complex values
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                writer.writerow([key, value])
    
    @staticmethod
    def export_to_excel(
        data: Dict,
        output_path: Path,
        flatten: bool = True,
        include_metadata: bool = True
    ) -> None:
        """
        Export to Excel (XLSX) format with formatting.
        
        Args:
            data: Dictionary to export
            output_path: Output file path
            flatten: Flatten nested keys with dot notation
            include_metadata: Add export metadata
            
        Raises:
            ImportError: If openpyxl not installed
        """
        if not _EXCEL_AVAILABLE:
            raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")
        
        if include_metadata:
            data = ExportManager.add_metadata(data, "export")
        
        if flatten:
            data = ExportManager.flatten_dict(data)
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Export"
        
        # Header formatting
        header_font = Font(bold=True, size=12)
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        
        # Write headers
        ws['A1'] = 'Key'
        ws['B1'] = 'Value'
        ws['A1'].font = header_font
        ws['B1'].font = header_font
        ws['A1'].fill = header_fill
        ws['B1'].fill = header_fill
        
        # Write data
        row = 2
        for key, value in data.items():
            # Handle complex values
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            ws[f'A{row}'] = key
            ws[f'B{row}'] = value
            row += 1
        
        # Auto-adjust column widths
        ws.column_dimensions['A'].width = 50
        ws.column_dimensions['B'].width = 80
        
        # Save
        wb.save(output_path)
    
    @staticmethod
    def export_to_yaml(
        data: Dict,
        output_path: Path,
        include_metadata: bool = True
    ) -> None:
        """
        Export to YAML format.
        
        Args:
            data: Dictionary to export
            output_path: Output file path
            include_metadata: Add export metadata
            
        Raises:
            ImportError: If pyyaml not installed
        """
        if not _YAML_AVAILABLE:
            raise ImportError("pyyaml is required for YAML export. Install with: pip install pyyaml")
        
        if include_metadata:
            data = ExportManager.add_metadata(data, "export")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    @staticmethod
    def export_to_toml(
        data: Dict,
        output_path: Path,
        flatten: bool = True,
        include_metadata: bool = True
    ) -> None:
        """
        Export to TOML format.
        
        Args:
            data: Dictionary to export
            output_path: Output file path
            flatten: Flatten nested keys (TOML doesn't support deep nesting well)
            include_metadata: Add export metadata
            
        Raises:
            ImportError: If tomli-w not installed
        """
        if not _TOML_AVAILABLE:
            raise ImportError("tomli-w is required for TOML export. Install with: pip install tomli-w")
        
        if include_metadata:
            data = ExportManager.add_metadata(data, "export")
        
        if flatten:
            data = ExportManager.flatten_dict(data)
        
        with open(output_path, 'wb') as f:
            tomli_w.dump(data, f)
    
    @staticmethod
    def export_to_json(
        data: Dict,
        output_path: Path,
        include_metadata: bool = True,
        indent: int = 2
    ) -> None:
        """
        Export to pretty-printed JSON.
        
        Args:
            data: Dictionary to export
            output_path: Output file path
            include_metadata: Add export metadata
            indent: JSON indentation spaces
        """
        if include_metadata:
            data = ExportManager.add_metadata(data, "export")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def export(
        data: Dict,
        output_path: Path,
        format: str = 'json',
        flatten: bool = True,
        include_metadata: bool = True
    ) -> None:
        """
        Main export function - delegates to format-specific exporters.
        
        Args:
            data: Dictionary to export
            output_path: Output file path
            format: Export format ('csv', 'excel', 'yaml', 'toml', 'json')
            flatten: Flatten nested keys (for CSV/Excel/TOML)
            include_metadata: Add export metadata
            
        Raises:
            ValueError: If format is unsupported
        """
        format = format.lower()
        
        exporters = {
            'csv': ExportManager.export_to_csv,
            'excel': ExportManager.export_to_excel,
            'xlsx': ExportManager.export_to_excel,
            'yaml': ExportManager.export_to_yaml,
            'yml': ExportManager.export_to_yaml,
            'toml': ExportManager.export_to_toml,
            'json': ExportManager.export_to_json
        }
        
        exporter = exporters.get(format)
        if not exporter:
            raise ValueError(f"Unsupported format: {format}. Supported: {', '.join(exporters.keys())}")
        
        # Call appropriate exporter
        if format in ['csv', 'excel', 'xlsx', 'toml']:
            exporter(data, output_path, flatten=flatten, include_metadata=include_metadata)
        elif format in ['yaml', 'yml']:
            exporter(data, output_path, include_metadata=include_metadata)
        else:  # json
            exporter(data, output_path, include_metadata=include_metadata)
