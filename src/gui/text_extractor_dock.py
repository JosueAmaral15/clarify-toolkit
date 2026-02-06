"""
Text Extractor Dock Widget - Advanced Version

⚠️ DEPRECATED - Scheduled for removal in v3.1.0
===============================================

This tool has been superseded by the Unified Text to JSON Converter.

Migration Path:
- Use "Text to JSON Converter" from Tools menu
- Select "JSX/HTML Extraction" mode from dropdown
- All features from this tool are available in the unified tool

Deprecated: 2026-01-30 (v2.9.116)
Removal: Planned for v3.1.0
Replacement: src/gui/unified_text_to_json_dock.py

See: UNIFIED_TOOL_DESIGN_SPECIFICATION_3.md
See: TOOL_CONSOLIDATION_INVESTIGATION_REPORT_3.md

---

Original Description:

Provides UI for extracting text/attributes from HTML/JSX to structured JSON.

Features:
- JSX/HTML attribute extraction (e.g., label, title, placeholder)
- Hierarchical path building with file context
- Multiple normalization styles (snake_case, camelCase, PascalCase, kebab-case)
- Smart truncation with word boundary awareness
- Drop standard HTML tags option
- Add key/value to path options
- Nested JSON output generation
- Generic scope parser with custom delimiters
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=import-outside-toplevel  # Lazy imports
# pylint: disable=broad-exception-caught  # GUI robustness
# pylint: disable=line-too-long  # Long regex patterns

import json
import os
import re

from typing import Any, Dict, List

from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton
)

from src.i18n.translator import tooltip_tr, tr
from .base_dock import StandardToolDock


class TextExtractorDock(StandardToolDock):
    """
    Advanced dock widget for text/attribute extraction from JSX/HTML.

    Supports:
    - Parameter extraction (JSX attributes like label="...")
    - Tag content extraction (text between tags)
    - Hierarchical path construction
    - Multiple normalization options
    - Smart value truncation
    - Standard HTML tag filtering
    """

    def __init__(self, parent=None):
        super().__init__(tr("text_extractor.title"), parent)

    def _setup_ui(self):
        """Setup UI components with advanced options."""
        grid = QGridLayout()

        # Input file/directory
        lbl_input, self.ed_input, self.btn_browse_input, self.chk_is_file = self.create_file_input(
            "Input path:",
            "HTML/JSX file or directory"
        )
        grid.addWidget(lbl_input, 0, 0)
        grid.addWidget(self.ed_input, 0, 1, 1, 2)
        grid.addWidget(self.btn_browse_input, 0, 3)

        # Output file
        grid.addWidget(QLabel(tr("text_extractor.lbl_output")), 1, 0)
        self.ed_output = QLineEdit()
        self.ed_output.setPlaceholderText(tr("text_extractor.placeholder_output"))
        self.btn_browse_output = QPushButton(tr("text_extractor.btn_browse"))
        grid.addWidget(self.ed_output, 1, 1, 1, 2)
        grid.addWidget(self.btn_browse_output, 1, 3)

        # Extraction mode
        grid.addWidget(QLabel(tr("text_extractor.lbl_mode")), 2, 0)
        self.combo_mode = QComboBox()
        self.combo_mode.addItems([tr("text_extractor.mode_jsx"), tr("text_extractor.mode_tag"), tr("text_extractor.mode_generic")])
        grid.addWidget(self.combo_mode, 2, 1)

        # Parameter/Tag name
        grid.addWidget(QLabel(tr("text_extractor.lbl_param")), 2, 2)
        self.ed_param = QLineEdit()
        self.ed_param.setPlaceholderText(tr("text_extractor.placeholder_param"))
        grid.addWidget(self.ed_param, 2, 3)

        # Normalization options
        grid.addWidget(QLabel(tr("text_extractor.lbl_case")), 3, 0)
        self.combo_case = QComboBox()
        self.combo_case.addItems([tr("combo.case_snake"), tr("combo.case_camel"), tr("combo.case_pascal"), tr("combo.case_kebab")])
        grid.addWidget(self.combo_case, 3, 1)

        # Character limit
        grid.addWidget(QLabel(tr("text_extractor.lbl_limit")), 3, 2)
        self.ed_limit = QLineEdit("all")
        self.ed_limit.setPlaceholderText(tr("text_extractor.placeholder_limit"))
        grid.addWidget(self.ed_limit, 3, 3)

        # Advanced options group
        options_group = QGroupBox(tr("text_extractor.group_advanced"))
        options_layout = QGridLayout()

        self.chk_uppercase = QCheckBox(tr("text_extractor.chk_uppercase"))
        self.chk_avoid_cut = QCheckBox(tr("text_extractor.chk_avoid_cut"))
        self.chk_avoid_cut.setChecked(True)
        self.chk_drop_standard = QCheckBox(tr("text_extractor.chk_drop_standard"))
        self.chk_drop_standard.setChecked(True)

        options_layout.addWidget(self.chk_uppercase, 0, 0)
        options_layout.addWidget(self.chk_avoid_cut, 0, 1)
        options_layout.addWidget(self.chk_drop_standard, 0, 2)

        self.chk_add_key = QCheckBox(tr("text_extractor.chk_add_key"))
        self.chk_add_value = QCheckBox(tr("text_extractor.chk_add_value"))
        self.chk_nested_json = QCheckBox(tr("text_extractor.chk_nested_json"))
        self.chk_nested_json.setChecked(True)

        options_layout.addWidget(self.chk_add_key, 1, 0)
        options_layout.addWidget(self.chk_add_value, 1, 1)
        options_layout.addWidget(self.chk_nested_json, 1, 2)

        self.chk_is_file.setChecked(False)
        self.chk_ts_export = QCheckBox(tr("text_extractor.chk_ts_export"))
        self.chk_only_strings = QCheckBox(tr("text_extractor.chk_only_strings"))
        self.chk_only_strings.setChecked(True)

        options_layout.addWidget(self.chk_is_file, 2, 0)
        options_layout.addWidget(self.chk_ts_export, 2, 1)
        options_layout.addWidget(self.chk_only_strings, 2, 2)

        self.chk_exclude_numeric = QCheckBox(tr("text_extractor.chk_exclude_numeric"))
        self.chk_exclude_numeric.setToolTip(tr("text_extractor.tooltip_exclude_numeric"))
        self.chk_skip_empty = QCheckBox(tr("text_extractor.chk_skip_empty"))
        self.chk_skip_empty.setToolTip(tr("text_extractor.tooltip_skip_empty"))
        self.chk_exclude_numeric = QCheckBox(tr("text_extractor.chk_exclude_numeric"))
        self.chk_skip_empty = QCheckBox(tr("text_extractor.chk_skip_empty"))

        options_layout.addWidget(self.chk_exclude_numeric, 3, 0)
        options_layout.addWidget(self.chk_skip_empty, 3, 1)
        self.layout.addWidget(options_group)

        # Action buttons
        buttons = [
            ("Extract", self._extract),
            ("Clear", self._clear)
        ]
        btn_layout = self.create_action_buttons(buttons)
        self.layout.addLayout(btn_layout)

        # Results panel
        lbl_results, self.text_results = self.create_results_panel()
        self.layout.addWidget(lbl_results)
        self.layout.addWidget(self.text_results)

        # Open in Editor button (Task #6 - v2.9.19)
        editor_btn_layout = QHBoxLayout()
        self.add_open_in_editor_button(self.text_results, editor_btn_layout)
        self.layout.addLayout(editor_btn_layout)

    def _connect_signals(self):
        # Open in Editor button (Task #6 - v2.9.19)
        editor_btn_layout = QHBoxLayout()
        self.add_open_in_editor_button(self.text_results, editor_btn_layout)
        self.layout.addLayout(editor_btn_layout)

        # Store button references for tooltips (v2.9.66)
        self.btn_extract = [btn for btn in self.findChildren(QPushButton) if btn.text() == "Extract"][0]
        self.btn_clear = [btn for btn in self.findChildren(QPushButton) if btn.text() == "Clear"][0]

        # Setup tooltips AFTER all widgets are created (v2.9.66)
        self._apply_tooltips()
        # Enable Enter key execution on input fields
        self._setup_enter_key_execution(self.ed_input, self.ed_param, self.ed_limit)
    def _execute_action(self):
        """Execute extraction when Enter is pressed."""
        self._extract()

    def _apply_tooltips(self):
        """Apply internationalized tooltips to all widgets (v2.9.66)."""
        # Input/Output section
        self.ed_input.setToolTip(tooltip_tr("text_extractor.ed_input"))
        self.btn_browse_input.setToolTip(tooltip_tr("text_extractor.btn_browse_input"))
        self.chk_is_file.setToolTip(tooltip_tr("text_extractor.chk_is_file"))
        self.ed_output.setToolTip(tooltip_tr("text_extractor.ed_output"))
        self.btn_browse_output.setToolTip(tooltip_tr("text_extractor.btn_browse_output"))

        # Extraction mode section
        self.combo_mode.setToolTip(tooltip_tr("text_extractor.combo_mode"))
        self.ed_param.setToolTip(tooltip_tr("text_extractor.ed_param"))

        # Normalization section
        self.combo_case.setToolTip(tooltip_tr("text_extractor.combo_case"))
        self.ed_limit.setToolTip(tooltip_tr("text_extractor.ed_limit"))

        # Advanced options (11 checkboxes)
        self.chk_uppercase.setToolTip(tooltip_tr("text_extractor.chk_uppercase"))
        self.chk_avoid_cut.setToolTip(tooltip_tr("text_extractor.chk_avoid_cut"))
        self.chk_drop_standard.setToolTip(tooltip_tr("text_extractor.chk_drop_standard"))
        self.chk_add_key.setToolTip(tooltip_tr("text_extractor.chk_add_key"))
        self.chk_add_value.setToolTip(tooltip_tr("text_extractor.chk_add_value"))
        self.chk_nested_json.setToolTip(tooltip_tr("text_extractor.chk_nested_json"))
        self.chk_ts_export.setToolTip(tooltip_tr("text_extractor.chk_ts_export"))
        self.chk_only_strings.setToolTip(tooltip_tr("text_extractor.chk_only_strings"))
        self.chk_exclude_numeric.setToolTip(tooltip_tr("text_extractor.chk_exclude_numeric"))
        self.chk_skip_empty.setToolTip(tooltip_tr("text_extractor.chk_skip_empty"))

        # Action buttons
        self.btn_extract.setToolTip(tooltip_tr("text_extractor.btn_extract"))
        self.btn_clear.setToolTip(tooltip_tr("text_extractor.btn_clear"))

        # Results panel
        self.text_results.setToolTip(tooltip_tr("text_extractor.text_results"))

    def _on_enter_pressed(self):
        """Handle action when Enter is pressed."""
        self._extract()

    def _browse_input(self):
        """Browse for input file or directory."""
        self.browse_file_or_directory(
            self.ed_input,
            self.chk_is_file.isChecked(),
            "HTML/JSX files (*.html *.htm *.jsx *.tsx);;All files (*)"
        )

    def _browse_output(self):
        """Browse for output file."""
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Save output file", "",
            "JSON files (*.json);;TypeScript (*.ts);;All (*)"
        )
        if path:
            self.ed_output.setText(path)

    def _extract(self):
        """Extract text from HTML/JSX with advanced options."""
        try:
            input_path = self.ed_input.text().strip()
            output_path = self.ed_output.text().strip()

            # Validate
            valid, error = self.validate_file_path(input_path)
            if not valid:
                raise ValueError(error)

            if not output_path:
                raise ValueError("Output file path is required")

            valid, error = self.validate_file_writable(output_path)
            if not valid:
                raise ValueError(error)

            # Gather options
            options = {
                'mode': self.combo_mode.currentText(),
                'param': self.ed_param.text().strip() or None,
                'case_style': self.combo_case.currentText().split('_')[0].lower() if '_' in self.combo_case.currentText() else self.combo_case.currentText().lower().replace('case', ''),
                'limit': self.ed_limit.text().strip(),
                'uppercase': self.chk_uppercase.isChecked(),
                'avoid_cut': self.chk_avoid_cut.isChecked(),
                'drop_standard': self.chk_drop_standard.isChecked(),
                'add_key': self.chk_add_key.isChecked(),
                'add_value': self.chk_add_value.isChecked(),
                'nested': self.chk_nested_json.isChecked(),
                'only_strings': self.chk_only_strings.isChecked(),
                'exclude_numeric': self.chk_exclude_numeric.isChecked(),
                'skip_empty': self.chk_skip_empty.isChecked(),
            }

            # Extract
            self.clear_results(self.text_results)
            self.append_result(self.text_results, f"🔄 Extracting with {options['mode']} mode...\n")

            if self.chk_is_file.isChecked():
                result = self._extract_from_file(input_path, options)
                files_processed = 1
            else:
                result = self._extract_from_directory(input_path, options)
                files_processed = len([f for f in self._list_files(input_path)])

            # Convert to nested if requested
            if options['nested'] and isinstance(result, dict):
                result = self._flatten_to_nested(result, options['exclude_numeric'], options['skip_empty'])

            # Save result
            with open(output_path, 'w', encoding='utf-8') as f:
                if self.chk_ts_export.isChecked():
                    f.write("export default ")
                json.dump(result, f, indent=2, ensure_ascii=False)
                if self.chk_ts_export.isChecked():
                    f.write(";")

            # Calculate statistics
            total_keys = self._count_keys(result)

            self.append_result(self.text_results, "✅ Extraction complete!\n")
            self.append_result(self.text_results, f"Files processed: {files_processed}")
            self.append_result(self.text_results, f"Keys extracted: {total_keys}")
            self.append_result(self.text_results, f"Output: {output_path}\n")

            # Show preview
            preview = json.dumps(result, indent=2, ensure_ascii=False)
            if len(preview) > 800:
                preview = preview[:800] + "\n  ...(truncated)..."
            self.append_result(self.text_results, f"Preview:\n{preview}")

            self.show_info(tr("text_extractor.success_title"), tr("text_extractor.success_message").replace("{files}", str(files_processed)).replace("{keys}", str(total_keys)).replace("{path}", output_path))

        except Exception as e:
            import traceback
            self.append_result(self.text_results, f"\n❌ Error: {str(e)}\n")
            self.append_result(self.text_results, traceback.format_exc())
            self.show_error(tr("text_extractor.error_title"), str(e))

    def _clear(self):
        """Clear results."""
        self.clear_results(self.text_results)

    # ==================== Extraction Core Methods ====================

    def _extract_from_file(self, file_path: str, options: dict) -> Dict[str, Any]:
        """Extract from a single file."""
        result = {}
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            file_key = os.path.splitext(os.path.basename(file_path))[0]
            file_result = self._extract_from_content(content, file_key, options)
            result.update(file_result)
        except Exception as e:
            self.append_result(self.text_results, f"⚠️ Error in {file_path}: {e}\n")

        return result

    def _extract_from_directory(self, dir_path: str, options: dict) -> Dict[str, Any]:
        """Extract from all files in directory."""
        result = {}
        for file_path in self._list_files(dir_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                rel_path = os.path.relpath(file_path, dir_path)
                file_key = os.path.splitext(rel_path.replace(os.sep, '.'))[0]
                file_result = self._extract_from_content(content, file_key, options)
                result.update(file_result)
            except Exception as e:
                self.append_result(self.text_results, f"⚠️ Error in {file_path}: {e}\n")

        return result

    def _extract_from_content(self, content: str, file_key: str, options: dict) -> Dict[str, Any]:
        """Extract from file content based on mode."""
        mode = options['mode']

        if mode == "JSX Attributes":
            return self._extract_jsx_attributes(content, file_key, options)
        elif mode == "Tag Content":
            return self._extract_tag_content(content, file_key, options)
        else:  # Generic Scope
            return self._extract_generic_scope(content, file_key, options)

    def _extract_jsx_attributes(self, content: str, file_key: str, options: dict) -> Dict[str, Any]:
        """Extract JSX attributes (e.g., label="text")."""
        result = {}
        param = options['param']

        # Pattern for JSX attributes: param="value" or param='value' or param={"value"}
        if param:
            patterns = [
                rf'{re.escape(param)}\s*=\s*"([^"]*)"',  # param="value"
                rf"{re.escape(param)}\s*=\s*'([^']*)'",  # param='value'
                rf'{re.escape(param)}\s*=\s*{{\s*["\']([^"\']*)["\']',  # param={"value"}
            ]
        else:
            # Match any attribute
            patterns = [
                r'(\w+)\s*=\s*"([^"]*)"',
                r"(\w+)\s*=\s*'([^']*)'",
                r'(\w+)\s*=\s*{{\s*["\']([^"\']*)["\']',
            ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                if param:
                    value = match.group(1)
                    key_name = param
                else:
                    key_name = match.group(1)
                    value = match.group(2)

                # Filter only strings if requested
                if options['only_strings']:
                    if not value or value.startswith('{') or value.startswith('['):
                        continue

                # Normalize value
                normalized = self._normalize_value(value, options)

                # Build path
                path_parts = [file_key]
                if options['add_key']:
                    path_parts.append(key_name)
                if options['add_value'] and normalized:
                    path_parts.append(normalized)

                path = '.'.join(path_parts)
                result[path] = value

        return result

    def _extract_tag_content(self, content: str, file_key: str, options: dict) -> Dict[str, Any]:
        """Extract text content between tags."""
        result = {}
        param = options['param'] or r'\w+'  # Default to any tag

        # Pattern for tag content: <tag>content</tag>
        pattern = rf'<({param})(?:\s[^>]*)?>([^<]+)<\/\1>'

        for match in re.finditer(pattern, content, re.DOTALL):
            tag_name = match.group(1)
            value = match.group(2).strip()

            # Skip standard HTML if requested
            if options['drop_standard'] and self._is_standard_html_tag(tag_name):
                continue

            # Filter only text (no JSX expressions)
            if options['only_strings']:
                if '{' in value or '}' in value:
                    continue

            # Normalize value
            normalized = self._normalize_value(value, options)

            # Build path
            path_parts = [file_key, tag_name]
            if options['add_value'] and normalized:
                path_parts.append(normalized)

            path = '.'.join(path_parts)
            result[path] = value

        return result

    def _extract_generic_scope(self, content: str, file_key: str, options: dict) -> Dict[str, Any]:
        """Extract using generic regex delimiters."""
        result = {}
        # Simple implementation - can be extended with user-provided delimiters
        # For now, extract quoted strings
        pattern = r'["\']([^"\']{3,})["\']'

        for match in re.finditer(pattern, content):
            value = match.group(1)

            # Normalize value
            normalized = self._normalize_value(value, options)

            if normalized:
                path = f"{file_key}.{normalized}"
                result[path] = value

        return result

    # ==================== Helper Methods ====================

    def _normalize_value(self, value: str, options: dict) -> str:
        """Normalize value according to options."""
        # Truncate
        limit = options['limit']
        if limit != 'all':
            try:
                max_len = int(limit)
                if options['avoid_cut'] and len(value) > max_len:
                    # Cut at word boundary
                    truncated = value[:max_len]
                    last_space = truncated.rfind(' ')
                    if last_space > 0:
                        value = truncated[:last_space]
                    else:
                        value = truncated
                else:
                    value = value[:max_len] if len(value) > max_len else value
            except ValueError:
                pass

        # Remove special chars and split into tokens
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', value)
        tokens = [t for t in cleaned.split() if t]

        if not tokens:
            return ""

        # Apply case style
        case_style = options['case_style']
        if case_style == 'snake':
            result = '_'.join(t.lower() for t in tokens)
        elif case_style == 'camel':
            result = tokens[0].lower() + ''.join(t.capitalize() for t in tokens[1:])
        elif case_style == 'pascal':
            result = ''.join(t.capitalize() for t in tokens)
        elif case_style == 'kebab':
            result = '-'.join(t.lower() for t in tokens)
        else:
            result = '_'.join(t.lower() for t in tokens)

        # Apply uppercase
        if options['uppercase']:
            result = result.upper()

        return result

    def _flatten_to_nested(self, flat: Dict[str, Any], exclude_numeric: bool = False, skip_empty: bool = False) -> Dict[str, Any]:
        """Convert flat dot-notation dict to nested dict with optional filtering."""
        nested = {}
        for path, value in flat.items():
            # Skip empty values if requested
            if skip_empty and self._is_empty_value(value):
                continue

            parts = path.split('.')

            # Filter numeric keys if requested
            if exclude_numeric:
                parts = [p for p in parts if not p.isdigit()]
                if not parts:  # All parts were numeric
                    continue

            current = nested
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        return nested

    def _count_keys(self, obj: Any, count: int = 0) -> int:
        """Count total keys recursively."""
        if isinstance(obj, dict):
            count += len(obj)
            for value in obj.values():
                count = self._count_keys(value, count)
        return count

    def _list_files(self, root: str, extensions: List[str] = None) -> List[str]:
        """List files recursively."""
        if extensions is None:
            extensions = ['.tsx', '.jsx', '.html', '.htm', '.js', '.ts']

        files = []
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    files.append(os.path.join(dirpath, filename))
        return files

    def _is_standard_html_tag(self, tag: str) -> bool:
        """Check if tag is a standard HTML tag."""
        standard_tags = {
            'div', 'span', 'p', 'a', 'button', 'input', 'label', 'form',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li',
            'table', 'tr', 'td', 'th', 'thead', 'tbody', 'section',
            'article', 'nav', 'header', 'footer', 'main', 'aside',
            'img', 'video', 'audio', 'canvas', 'svg', 'iframe'
        }
        return tag.lower() in standard_tags

    def _is_empty_value(self, value: Any) -> bool:
        """Check if value is considered empty.

        Empty values include:
        - Empty strings: ""
        - None/null
        - Empty lists: []
        - Empty dicts: {}
        - Whitespace-only strings: "   "
        """
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        if isinstance(value, (list, dict)):
            return not value
        return False
