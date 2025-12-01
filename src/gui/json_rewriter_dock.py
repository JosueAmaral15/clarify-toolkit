#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON Rewriter Dock - Modular implementation
Rewrites JSON/TS files with options to join keys, eliminate duplicates, and format output.
"""

from __future__ import annotations
import argparse
import os
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
    QSpinBox, QFileDialog, QMessageBox, QComboBox
)
from PySide6.QtCore import QSettings

from .base_dock import BaseDock
from ..utils.advanced_conditions import get_conditions_from_ui, apply_conditions_to_files
from ..core.filters import Condition

# Type checking imports
if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QWidgetType


def format_removal_statistics(stats: dict) -> str:
    """
    Format removal statistics for display.
    
    Args:
        stats: Dictionary with removal counters
    
    Returns:
        Formatted string or empty string if nothing was removed
    """
    lines = []
    total = 0
    
    # Map operation keys to display labels (Q4: specific terms)
    labels = {
        'dedupe': ('Removed duplicate key-value pairs', 'key-value pairs'),
        'eliminate': ('Eliminated duplicate values', 'values'),
        'numeric_keys': ('Excluded numeric keys', 'keys'),
        'empty_values': ('Skipped empty key-value pairs', 'key-value pairs'),
        'duplicate_child': ('Avoided duplicate child hierarchies', 'object hierarchies'),
        'array_duplicates_consecutive': ('Removed consecutive duplicate array elements', 'array elements'),
        'array_duplicates_all': ('Removed all duplicate array elements', 'array elements'),
        'no_siblings': ('Skipped orphan object chains', 'object chains'),
        'duplicate_objects': ('Removed duplicate objects', 'objects'),
        'advanced_filters_filtered': ('🔍 Filtered by Advanced Conditions', 'files')
    }
    
    # Omit operations with 0 count (Q5-B)
    for key, (label, unit) in labels.items():
        count = stats.get(key, 0)
        if count > 0:
            lines.append(f"• {label}: {count} {unit}")
            total += count
    
    # If nothing was removed, return empty (Q5-C handled in caller)
    if total == 0:
        return ""
    
    # Format final message
    result = "✂️ Removal Statistics:\n"
    result += "\n".join(lines)
    result += f"\n\nTotal: {total} items removed"
    
    return result


def cli_dedupe(args: argparse.Namespace, advanced_conditions: Optional[list[Condition]] = None, 
               apply_all_types: bool = False):
    """Execute the dedupe/rewrite operation based on args.
    
    Args:
        args: Command-line arguments (or GUI-generated args)
        advanced_conditions: Optional list of Condition objects for filtering files (Sprint B Feature #1)
        apply_all_types: If True, apply filters to all files; if False, auto-detect .json (Sprint B Feature #1)
    
    Returns:
        tuple: (output_text, substitution_map, removal_stats) where:
            - output_text: processed file content
            - substitution_map: maps removed keys to replacements (Task #23)
            - removal_stats: dict with removal counters (Task v2.9.22)
    """
    from .. import rewriter as rw
    
    # Initialize removal statistics counter
    stats = {
        'dedupe': 0,
        'eliminate': 0,
        'numeric_keys': 0,
        'empty_values': 0,
        'duplicate_child': 0,
        'array_duplicates_consecutive': 0,
        'array_duplicates_all': 0,
        'no_siblings': 0,
        'advanced_filters_filtered': 0  # Sprint B Feature #1
    }
    
    # Apply advanced filters BEFORE processing (Sprint B Feature #1)
    if advanced_conditions:
        # Auto-detect JSON files unless apply_all_types is True
        input_file = args.input
        should_filter = apply_all_types or input_file.endswith(('.json', '.JSON'))
        
        if should_filter:
            # Apply filters
            filtered_files, filtered_out = apply_conditions_to_files(
                [input_file],
                advanced_conditions,
                logic_op="AND",
                enabled=True
            )
            
            stats['advanced_filters_filtered'] = filtered_out
            
            # If file was filtered out, skip processing (Q6: process all if zero files pass)
            # But since we're only checking single file here, if it's filtered out, we skip it
            if not filtered_files:
                # Return empty result (file was filtered out)
                return "", {}, stats
    
    # Read input
    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Parse based on format
    if args.from_ts:
        # TypeScript/JavaScript object literal
        obj = rw.ts_process_full_preserving(text)
    else:
        # Pure JSON
        obj = rw.parse_json_preserving_duplicates_text(text)
    
    # Apply transformations with counting
    obj, stats['dedupe'] = rw.dedupe(obj)
    
    if args.join_keys:
        obj, _ = rw.join_keys(obj)  # join_keys doesn't remove items
    
    # Build substitution map for eliminated keys (Task #23 - v2.9.14 COMPLETO)
    substitution_map = {}
    if args.eliminate_duplicates:
        # Extract all keys AND values before elimination
        old_keys_values = rw.extract_all_keys_from_obj(obj.data if hasattr(obj, 'data') else obj, prefix='t')
        obj, stats['eliminate'] = rw.eliminate_duplicates(obj)
        # Extract all keys AND values after elimination
        new_keys_values = rw.extract_all_keys_from_obj(obj.data if hasattr(obj, 'data') else obj, prefix='t')
        # Build substitution map based on VALUE EQUALITY (not string similarity)
        substitution_map = rw.build_substitution_map_by_value(old_keys_values, new_keys_values)
    
    # Exclude numeric keys if requested
    if hasattr(args, 'exclude_numeric') and args.exclude_numeric:
        obj, stats['numeric_keys'] = rw.exclude_numeric_keys(obj)
    
    # Skip empty values if requested
    if hasattr(args, 'skip_empty') and args.skip_empty:
        obj, stats['empty_values'] = rw.skip_empty_values(obj)
    
    # Avoid duplicate child keys if requested
    if hasattr(args, 'avoid_duplicate_child_keys') and args.avoid_duplicate_child_keys:
        obj, stats['duplicate_child'] = rw.avoid_duplicate_child_keys(obj)
    
    # Remove duplicate array values if requested (Task #8 - v2.9.8)
    if hasattr(args, 'remove_dup_consecutive') and args.remove_dup_consecutive:
        obj, stats['array_duplicates_consecutive'] = rw.remove_duplicate_array_values(obj, consecutive_only=True)
    
    if hasattr(args, 'remove_dup_all') and args.remove_dup_all:
        obj, stats['array_duplicates_all'] = rw.remove_duplicate_array_values(obj, consecutive_only=False)
    
    # Skip keys without siblings if requested (Task #35 - v2.9.11)
    if hasattr(args, 'skip_no_siblings') and args.skip_no_siblings:
        obj, stats['no_siblings'] = rw.skip_keys_without_siblings(obj)
    
    # Remove duplicate objects if requested (Task #52 - v2.9.27)
    if hasattr(args, 'remove_duplicate_objects') and args.remove_duplicate_objects:
        threshold = getattr(args, 'duplicate_threshold', 100) / 100.0  # Convert percentage to 0.0-1.0
        include_arrays = getattr(args, 'include_duplicate_arrays', False)
        mode = getattr(args, 'duplicate_mode', 'remove')
        obj, stats['duplicate_objects'], dup_stats = rw.remove_duplicate_objects(
            obj,
            threshold=threshold,
            include_arrays=include_arrays,
            mode=mode
        )
    
    # Enforce consistent case if requested (Task #9 - v2.9.8)
    if hasattr(args, 'enforce_case') and args.enforce_case:
        case_style = getattr(args, 'case_style', 'camel')
        obj, warnings = rw.enforce_consistent_case(obj, target_case=case_style, warn_inconsistencies=True)
        if warnings:
            print(f"\n⚠️ Case inconsistencies detected and corrected ({len(warnings)} warnings):")
            for warning in warnings[:10]:  # Show first 10 warnings
                print(f"  - {warning}")
            if len(warnings) > 10:
                print(f"  ... and {len(warnings) - 10} more warnings")
    
    # Serialize output
    if args.ts_out:
        output_text = rw.dump_ts_node(obj, indent=args.indent)
        if not args.no_line_break:
            output_text = rw.collapse_blank_lines(output_text)
    else:
        output_text = rw.dump_ts_obj(obj, indent=args.indent, level=0)
    
    # Write output
    out_path = args.output or args.input
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    return output_text, substitution_map, stats


class JsonRewriterDock(BaseDock):
    """
    Dock widget for JSON rewriter functionality.
    Rewrites JSON/TS files with deduplication and formatting options.
    
    Features:
    - Input/output file selection
    - From TS/JS option (preserve TypeScript format)
    - Emit export default option
    - Join keys option
    - Eliminate duplicates option
    - No blank lines option
    - Configurable indentation
    """
    
    def __init__(self, parent: QWidgetType | None = None):
        super().__init__("JSON Rewriter", parent)
        self._load_preferences()
    
    def _setup_ui(self) -> None:
        """Setup UI components."""
        self._create_widgets()
        self._create_layout()
    
    def _create_widgets(self) -> None:
        """Create all widgets for the rewriter dock."""
        # Input file section
        self.lbl_in = QLabel("Input file:")
        self.ed_in = QLineEdit()
        self.ed_in.setToolTip("JSON, TypeScript, or JavaScript file to rewrite")
        self.btn_in = QPushButton("Open…")
        self.btn_in.setToolTip("Browse for input file")
        
        # Output file section
        self.lbl_out = QLabel("Output file (optional):")
        self.ed_out = QLineEdit()
        self.ed_out.setToolTip("Optional output file path (defaults to input file if empty)")
        self.btn_out = QPushButton("Save as…")
        self.btn_out.setToolTip("Browse for output file")
        
        # Options checkboxes
        self.chk_from_ts = QCheckBox("From TS/JS (preserve file)")
        self.chk_from_ts.setToolTip("Parse as TypeScript/JavaScript and preserve format")
        self.chk_ts_out = QCheckBox("Emit export default …;")
        self.chk_ts_out.setToolTip("Add 'export default' statement to output")
        self.chk_join = QCheckBox("Join keys")
        self.chk_join.setToolTip("Join nested keys into single level (e.g., a.b.c)")
        self.chk_elim = QCheckBox("Eliminate duplicates")
        self.chk_elim.setToolTip("Remove duplicate keys, keeping the last occurrence")
        self.chk_nlb = QCheckBox("No blank lines")
        self.chk_nlb.setToolTip("Remove blank lines from output")
        self.chk_exclude_numeric = QCheckBox("Exclude numeric keys")
        self.chk_exclude_numeric.setToolTip("Skip keys that are purely numeric (e.g., '0', '123')")
        self.chk_skip_empty = QCheckBox("Skip empty values")
        self.chk_skip_empty.setToolTip("Skip empty strings, null, [], {}, and whitespace-only values")
        self.chk_avoid_dup_child = QCheckBox("Avoid duplicate child keys")
        self.chk_avoid_dup_child.setToolTip("Merge parent.child.child -> parent.child (e.g., t.pages.home.home -> t.pages.home)")
        self.chk_normalize_escaping = QCheckBox("Normalize escaping")
        self.chk_normalize_escaping.setToolTip("Auto-detect excessive escaping (\\\\\\' or more) and normalize to \\' (Task #22)")
        self.chk_convert_arrays = QCheckBox("Convert arrays to objects")
        self.chk_convert_arrays.setToolTip("Convert string arrays to objects with generated keys (Task #21)")
        self.chk_skip_no_siblings = QCheckBox("Skip keys without siblings")
        self.chk_skip_no_siblings.setToolTip("Remove serial hierarchies (chains) where keys don't have siblings (Task #35)")
        
        # Task #52 - Remove duplicate objects
        self.chk_remove_dup_objects = QCheckBox("Remove duplicate objects")
        self.chk_remove_dup_objects.setToolTip("Remove objects with identical or similar values, keeping the first occurrence (smallest line number)")
        self.chk_include_dup_arrays = QCheckBox("Include arrays")
        self.chk_include_dup_arrays.setToolTip("Also check arrays for duplicates (only when all elements match)")
        self.lbl_dup_threshold = QLabel("Similarity:")
        self.spin_dup_threshold = QSpinBox()
        self.spin_dup_threshold.setRange(50, 100)
        self.spin_dup_threshold.setValue(100)
        self.spin_dup_threshold.setSuffix("%")
        self.spin_dup_threshold.setToolTip("Minimum similarity percentage (100% = exact match only, 80% = allow 20% field differences)")
        self.combo_dup_mode = QComboBox()
        self.combo_dup_mode.addItems(["Remove (default)", "Reference ($ref)"])
        self.combo_dup_mode.setToolTip("Remove: delete duplicates | Reference: replace with $ref:path to original")
        
        # Task #23 - Update orphaned references
        self.chk_update_refs = QCheckBox("Update references in project")
        self.chk_update_refs.setToolTip("Update orphaned translation references (t.key.path) in .tsx/.jsx files after eliminating duplicates (Task #23)")
        self.ed_project_dir = QLineEdit()
        self.ed_project_dir.setToolTip("Project directory containing .tsx/.jsx/.ts/.js files to update")
        self.btn_project_browse = QPushButton("Browse…")
        self.btn_project_browse.setToolTip("Browse for project directory")
        self.chk_ref_backup = QCheckBox("Create backups")
        self.chk_ref_backup.setToolTip("Create .bak files before modifying references")
        self.chk_ref_backup.setChecked(True)
        
        self.chk_remove_dup_consecutive = QCheckBox("Remove consecutive duplicates")
        self.chk_remove_dup_consecutive.setToolTip("Remove only consecutive duplicates in arrays: ['a','a','b'] → ['a','b']")
        self.chk_remove_dup_all = QCheckBox("Remove all duplicates")
        self.chk_remove_dup_all.setToolTip("Remove all duplicates in arrays (set behavior): ['a','b','a'] → ['a','b']")
        self.chk_enforce_case = QCheckBox("Enforce consistent case")
        self.chk_enforce_case.setToolTip("Automatically convert all keys to consistent case style (warns on inconsistencies)")
        self.chk_enforce_case.setChecked(True)  # Applied automatically
        self.combo_case_style = QComboBox()
        self.combo_case_style.addItems(["camelCase", "PascalCase", "snake_case", "kebab-case"])
        self.combo_case_style.setCurrentIndex(0)  # Default: camelCase
        self.combo_case_style.setToolTip("Target case style for key conversion")
        self.chk_validate_case = QCheckBox("Validate case before applying")
        self.chk_validate_case.setToolTip("Show preview dialog with before/after comparison before applying case conversion")
        self.chk_validate_case.setChecked(False)  # Optional validation
        self.chk_is_file = QCheckBox("Is file")
        self.chk_is_file.setToolTip("Input path is a single file (unchecked for directory)")
        self.chk_is_file.setChecked(True)
        
        # Sprint B Feature #1: Advanced Filters
        self.btn_advanced_filters = QPushButton("🔍 Advanced Filters...")
        self.btn_advanced_filters.setToolTip("Configure advanced file filters (filename, size, content patterns, etc.)")
        self.chk_apply_all_types = QCheckBox("Apply to all file types")
        self.chk_apply_all_types.setToolTip("Apply filters to all files, not just JSON (default: auto-detect .json)")
        self.chk_apply_all_types.setChecked(False)
        self.advanced_conditions: list[Condition] = []  # Storage for configured conditions
        self.advanced_filters_enabled = False  # Whether filters are active
        
        # Indent spinner
        self.lbl_indent = QLabel("Indent (<=0 compact):")
        self.spin_indent = QSpinBox()
        self.spin_indent.setRange(-1, 16)
        self.spin_indent.setValue(2)
        self.spin_indent.setToolTip("Number of spaces for indentation (0 or negative for compact output)")
        
        # Action button
        self.btn_run = QPushButton("Rewrite")
    
    def _create_layout(self) -> None:
        """Arrange widgets in the dock."""
        g = QGridLayout()
        self.main_widget.setLayout(g)
        
        # Row 0: Input file
        g.addWidget(self.lbl_in, 0, 0)
        g.addWidget(self.ed_in, 0, 1, 1, 3)
        g.addWidget(self.btn_in, 0, 4)
        
        # Row 1: Output file
        g.addWidget(self.lbl_out, 1, 0)
        g.addWidget(self.ed_out, 1, 1, 1, 3)
        g.addWidget(self.btn_out, 1, 4)
        
        # Row 2: Options checkboxes (line 1)
        g.addWidget(self.chk_from_ts, 2, 0)
        g.addWidget(self.chk_ts_out, 2, 1)
        g.addWidget(self.chk_join, 2, 2)
        g.addWidget(self.chk_elim, 2, 3)
        g.addWidget(self.chk_nlb, 2, 4)
        
        # Row 3: Options checkboxes (line 2)
        g.addWidget(self.chk_exclude_numeric, 3, 0)
        g.addWidget(self.chk_skip_empty, 3, 1)
        g.addWidget(self.chk_avoid_dup_child, 3, 2)
        g.addWidget(self.chk_normalize_escaping, 3, 3)
        g.addWidget(self.chk_is_file, 3, 4)
        
        # Row 4: Options checkboxes (line 3) - Array operations
        g.addWidget(self.chk_convert_arrays, 4, 0, 1, 2)
        g.addWidget(self.chk_remove_dup_consecutive, 4, 2, 1, 1)
        g.addWidget(self.chk_remove_dup_all, 4, 3, 1, 1)
        g.addWidget(self.chk_skip_no_siblings, 4, 4, 1, 1)
        
        # Row 5: Update references (Task #23)
        g.addWidget(self.chk_update_refs, 5, 0, 1, 1)
        g.addWidget(self.ed_project_dir, 5, 1, 1, 2)
        g.addWidget(self.btn_project_browse, 5, 3)
        g.addWidget(self.chk_ref_backup, 5, 4)
        
        # Row 6: Enforce consistent case
        g.addWidget(self.chk_enforce_case, 6, 0, 1, 2)
        g.addWidget(QLabel("Case style:"), 6, 2)
        g.addWidget(self.combo_case_style, 6, 3)
        g.addWidget(self.chk_validate_case, 6, 4)
        
        # Row 7: Remove duplicate objects (Task #52)
        g.addWidget(self.chk_remove_dup_objects, 7, 0, 1, 1)
        g.addWidget(self.chk_include_dup_arrays, 7, 1)
        g.addWidget(self.lbl_dup_threshold, 7, 2)
        g.addWidget(self.spin_dup_threshold, 7, 3)
        g.addWidget(self.combo_dup_mode, 7, 4)
        
        # Row 8: Advanced Filters (Sprint B Feature #1)
        g.addWidget(self.btn_advanced_filters, 8, 0, 1, 2)
        g.addWidget(self.chk_apply_all_types, 8, 2, 1, 2)
        
        # Row 9: Indent and run button
        g.addWidget(self.lbl_indent, 9, 0)
        g.addWidget(self.spin_indent, 9, 1)
        g.addWidget(self.btn_run, 9, 4)
    
    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.btn_in.clicked.connect(self._open_in)
        self.btn_out.clicked.connect(self._open_out)
        self.btn_project_browse.clicked.connect(self._browse_project_dir)
        self.btn_run.clicked.connect(self._rewrite)
        self.btn_advanced_filters.clicked.connect(self._open_advanced_filters_dialog)
    
    # UI Helper Methods
    
    def _open_in(self) -> None:
        """Browse for input file."""
        f, _ = QFileDialog.getOpenFileName(
            self, "Select input", "",
            "JSON/TS/JS (*.json *.ts *.tsx *.js *.jsx);;All (*)"
        )
        if f:
            self.ed_in.setText(f)
    
    def _open_out(self) -> None:
        """Browse for output file."""
        f, _ = QFileDialog.getSaveFileName(self, "Save output", "", "All (*)")
        if f:
            self.ed_out.setText(f)
    
    def _browse_project_dir(self) -> None:
        """Browse for project directory (Task #23)."""
        d = QFileDialog.getExistingDirectory(
            self, "Select project directory",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if d:
            self.ed_project_dir.setText(d)
    
    def _open_advanced_filters_dialog(self) -> None:
        """Open dialog to configure advanced file filters (Sprint B Feature #1)."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QGroupBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Advanced File Filters")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        
        # Info label
        info = QLabel("Configure filters to apply BEFORE processing files.\nFilters use AND logic (all conditions must match).")
        layout.addWidget(info)
        
        # Create 3 condition rows (same UI as AI Processor)
        cond_group = QGroupBox("Filter Conditions")
        cond_layout = QGridLayout()
        
        # Headers
        cond_layout.addWidget(QLabel("Field"), 0, 0)
        cond_layout.addWidget(QLabel("Operator"), 0, 1)
        cond_layout.addWidget(QLabel("Value"), 0, 2)
        cond_layout.addWidget(QLabel("Scope"), 0, 3)
        cond_layout.addWidget(QLabel("Case"), 0, 4)
        cond_layout.addWidget(QLabel("Regex"), 0, 5)
        
        # Create condition rows
        cond_rows = []
        for row in range(3):
            combo_field = QComboBox()
            combo_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])
            
            combo_op = QComboBox()
            combo_op.addItems(["", "contains", "not contains", "equals", "not equals", 
                              "starts with", "ends with", ">", "<", ">=", "<="])
            
            ed_value = QLineEdit()
            ed_value.setPlaceholderText("Filter value")
            
            combo_scope = QComboBox()
            combo_scope.addItems(["none", "brackets", "braces", "parentheses", 
                                 "custom", "tag", "specific-tag", "hierarchical"])
            
            chk_case = QCheckBox()
            chk_case.setChecked(True)
            
            chk_regex = QCheckBox()
            
            grid_row = row + 1
            cond_layout.addWidget(combo_field, grid_row, 0)
            cond_layout.addWidget(combo_op, grid_row, 1)
            cond_layout.addWidget(ed_value, grid_row, 2)
            cond_layout.addWidget(combo_scope, grid_row, 3)
            cond_layout.addWidget(chk_case, grid_row, 4)
            cond_layout.addWidget(chk_regex, grid_row, 5)
            
            cond_rows.append((combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex))
        
        cond_group.setLayout(cond_layout)
        layout.addWidget(cond_group)
        
        # Load existing conditions into UI
        for i, cond in enumerate(self.advanced_conditions[:3]):  # Max 3 rows
            if i < len(cond_rows):
                combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex = cond_rows[i]
                combo_field.setCurrentText(cond.field)
                combo_op.setCurrentText(cond.operator)
                ed_value.setText(cond.value)
                combo_scope.setCurrentText(cond.scope_type)
                chk_case.setChecked(cond.case_sensitive)
                chk_regex.setChecked(cond.use_regex)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Show dialog and save conditions if accepted
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.advanced_conditions = get_conditions_from_ui(cond_rows)
            self.advanced_filters_enabled = len(self.advanced_conditions) > 0
            
            # Feedback
            if self.advanced_filters_enabled:
                QMessageBox.information(
                    self, 
                    "Filters Configured", 
                    f"✅ {len(self.advanced_conditions)} filter(s) configured.\n\n"
                    "Filters will be applied BEFORE processing files."
                )
            else:
                QMessageBox.information(
                    self, 
                    "Filters Cleared", 
                    "❌ No filters configured. All files will be processed."
                )
    
    # Core Processing
    
    def _rewrite(self) -> None:
        """Execute rewrite operation on selected file."""
        if not self.ed_in.text().strip():
            QMessageBox.warning(self, "Missing", "Choose an input file.")
            return
        
        # Case validation dialog (if enabled)
        if self.chk_enforce_case.isChecked() and self.chk_validate_case.isChecked():
            try:
                # Read and parse input file
                from .. import rewriter as rw
                with open(self.ed_in.text().strip(), 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Parse based on format
                if self.chk_from_ts.isChecked():
                    obj = rw.ts_process_full_preserving(text)
                else:
                    obj = rw.parse_json_preserving_duplicates_text(text)
                
                # Show validation dialog
                from .case_validator_dialog import show_case_validator
                accepted, obj_converted, warnings = show_case_validator(obj, self)
                
                # User cancelled
                if not accepted:
                    QMessageBox.information(self, "Cancelled", "Case conversion cancelled by user.")
                    return
                
                # User accepted - we'll use the converted object
                # But first, temporarily disable enforce_case to avoid double conversion
                # (We'll write the already-converted object)
                self.chk_enforce_case.setChecked(False)
                
                # Write the converted object to a temporary state
                # and let cli_dedupe handle the rest
                # Actually, we need to serialize it back to text first
                if self.chk_ts_out.isChecked():
                    temp_text = rw.dump_ts_node(obj_converted, indent=self.spin_indent.value())
                    if not self.chk_nlb.isChecked():
                        temp_text = rw.collapse_blank_lines(temp_text)
                else:
                    temp_text = rw.dump_ts_obj(obj_converted, indent=self.spin_indent.value())
                
                # Write to output
                out_path = self.ed_out.text().strip() or self.ed_in.text().strip()
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(temp_text)
                
                QMessageBox.information(self, "Done", f"Rewriter finished with {len(warnings)} case conversions.")
                
                # Re-enable enforce_case for next run
                self.chk_enforce_case.setChecked(True)
                return
                
            except Exception as e:
                QMessageBox.critical(self, "Validation Error", f"Failed to validate case: {e}")
                return
        
        # Build argparse namespace with all options
        ns = argparse.Namespace(
            input=self.ed_in.text().strip(),
            output=self.ed_out.text().strip() or None,
            indent=self.spin_indent.value(),
            from_ts=self.chk_from_ts.isChecked(),
            ts_out=self.chk_ts_out.isChecked(),
            join_keys=self.chk_join.isChecked(),
            eliminate_duplicates=self.chk_elim.isChecked(),
            no_line_break=self.chk_nlb.isChecked(),
            exclude_numeric=self.chk_exclude_numeric.isChecked(),
            skip_empty=self.chk_skip_empty.isChecked(),
            avoid_duplicate_child_keys=self.chk_avoid_dup_child.isChecked(),
            normalize_escaping=self.chk_normalize_escaping.isChecked(),
            convert_arrays_to_objects=self.chk_convert_arrays.isChecked(),
            remove_dup_consecutive=self.chk_remove_dup_consecutive.isChecked(),
            remove_dup_all=self.chk_remove_dup_all.isChecked(),
            skip_no_siblings=self.chk_skip_no_siblings.isChecked(),
            enforce_case=self.chk_enforce_case.isChecked(),
            case_style=self.combo_case_style.currentText().lower().replace('-', '').replace('case', ''),  # 'camelCase' -> 'camel'
            is_file=self.chk_is_file.isChecked(),
            remove_duplicate_objects=self.chk_remove_dup_objects.isChecked(),
            duplicate_threshold=self.spin_dup_threshold.value(),
            include_duplicate_arrays=self.chk_include_dup_arrays.isChecked(),
            duplicate_mode='reference' if self.combo_dup_mode.currentIndex() == 1 else 'remove',
        )
        
        # Execute rewrite (Sprint B Feature #1: pass advanced conditions)
        try:
            output_text, substitution_map, removal_stats = cli_dedupe(
                ns,
                advanced_conditions=self.advanced_conditions if self.advanced_filters_enabled else None,
                apply_all_types=self.chk_apply_all_types.isChecked()
            )
            
            # Task #23: Update orphaned references in project (if enabled)
            if self.chk_update_refs.isChecked() and substitution_map:
                project_dir = self.ed_project_dir.text().strip()
                
                if not project_dir:
                    QMessageBox.warning(self, "Missing", "Choose a project directory to update references.")
                    return
                
                if not os.path.isdir(project_dir):
                    QMessageBox.warning(self, "Invalid", f"Project directory does not exist: {project_dir}")
                    return
                
                # Show preview dialog with substitutions
                from .. import rewriter as rw
                results = rw.update_references_in_project(
                    project_dir,
                    substitution_map,
                    create_backup=self.chk_ref_backup.isChecked()
                )
                
                if results:
                    # Show summary
                    total_subs = sum(results.values())
                    file_count = len(results)
                    msg = f"Updated {total_subs} references in {file_count} files:\n\n"
                    for filepath, count in list(results.items())[:10]:
                        msg += f"  - {os.path.basename(filepath)}: {count} changes\n"
                    if file_count > 10:
                        msg += f"  ... and {file_count - 10} more files\n"
                    QMessageBox.information(self, "References Updated", msg)
                else:
                    QMessageBox.information(self, "No Changes", "No orphaned references found in project.")
            
            # Task v2.9.22: Format and display removal statistics (Q3: MessageBox only)
            stats_msg = format_removal_statistics(removal_stats)
            if stats_msg:
                QMessageBox.information(self, "Done", f"Rewriter finished.\n\n{stats_msg}")
            else:
                # Q5-C: Special message if nothing was removed
                QMessageBox.information(self, "Done", "Rewriter finished.\n\nℹ️ No items were removed by any operation.")
            
            # Save preferences after successful execution
            self._save_preferences()
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error", f"{str(e)}\n\n{traceback.format_exc()}")
    
    def _load_preferences(self) -> None:
        """Load preferences from QSettings (Task #52 + Sprint B Feature #1)."""
        settings = QSettings("Clarify", "JsonRewriter")
        
        # Load duplicate objects settings
        if hasattr(self, 'chk_remove_dup_objects'):
            self.chk_remove_dup_objects.setChecked(settings.value("remove_duplicate_objects", False, type=bool))
            self.chk_include_dup_arrays.setChecked(settings.value("include_duplicate_arrays", False, type=bool))
            self.spin_dup_threshold.setValue(settings.value("duplicate_threshold", 100, type=int))
            self.combo_dup_mode.setCurrentIndex(settings.value("duplicate_mode_index", 0, type=int))
        
        # Load advanced filters settings (Sprint B Feature #1)
        if hasattr(self, 'chk_apply_all_types'):
            self.chk_apply_all_types.setChecked(settings.value("advanced_filters_apply_all_types", False, type=bool))
            self.advanced_filters_enabled = settings.value("advanced_filters_enabled", False, type=bool)
            
            # Load serialized conditions (JSON format)
            import json
            conditions_json = settings.value("advanced_filters_conditions", "[]", type=str)
            try:
                conditions_data = json.loads(conditions_json)
                self.advanced_conditions = [
                    Condition(
                        field=c['field'],
                        operator=c['operator'],
                        value=c['value'],
                        scope_type=c.get('scope_type', 'none'),
                        scope_value=c.get('scope_value', ''),
                        case_sensitive=c.get('case_sensitive', True),
                        whole_word=c.get('whole_word', False),
                        use_regex=c.get('use_regex', False)
                    )
                    for c in conditions_data
                ]
            except (json.JSONDecodeError, KeyError):
                self.advanced_conditions = []
    
    def _save_preferences(self) -> None:
        """Save preferences to QSettings (Task #52 + Sprint B Feature #1)."""
        settings = QSettings("Clarify", "JsonRewriter")
        
        # Save duplicate objects settings
        settings.setValue("remove_duplicate_objects", self.chk_remove_dup_objects.isChecked())
        settings.setValue("include_duplicate_arrays", self.chk_include_dup_arrays.isChecked())
        settings.setValue("duplicate_threshold", self.spin_dup_threshold.value())
        settings.setValue("duplicate_mode_index", self.combo_dup_mode.currentIndex())
        
        # Save advanced filters settings (Sprint B Feature #1)
        settings.setValue("advanced_filters_apply_all_types", self.chk_apply_all_types.isChecked())
        settings.setValue("advanced_filters_enabled", self.advanced_filters_enabled)
        
        # Serialize conditions to JSON
        import json
        conditions_data = [
            {
                'field': c.field,
                'operator': c.operator,
                'value': c.value,
                'scope_type': c.scope_type,
                'scope_value': c.scope_value,
                'case_sensitive': c.case_sensitive,
                'whole_word': c.whole_word,
                'use_regex': c.use_regex
            }
            for c in self.advanced_conditions
        ]
        settings.setValue("advanced_filters_conditions", json.dumps(conditions_data))
    
    def _execute_action(self) -> None:
        """Execute the main action when ENTER is pressed."""
        self._rewrite()
