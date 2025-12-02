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

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.accessibility_manager import AccessibilityManager
from src.core.filters import Condition
from src.utils.advanced_conditions import apply_conditions_to_files, get_conditions_from_ui
from .base_dock import BaseDock

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
        "dedupe": ("Removed duplicate key-value pairs", "key-value pairs"),
        "eliminate": ("Eliminated duplicate values", "values"),
        "numeric_keys": ("Excluded numeric keys", "keys"),
        "empty_values": ("Skipped empty key-value pairs", "key-value pairs"),
        "duplicate_child": ("Avoided duplicate child hierarchies", "object hierarchies"),
        "array_duplicates_consecutive": ("Removed consecutive duplicate array elements", "array elements"),
        "array_duplicates_all": ("Removed all duplicate array elements", "array elements"),
        "no_siblings": ("Skipped orphan object chains", "object chains"),
        "duplicate_objects": ("Removed duplicate objects", "objects"),
        "advanced_filters_filtered": ("🔍 Filtered by Advanced Conditions", "files"),
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


def cli_dedupe(
    args: argparse.Namespace, advanced_conditions: Optional[list[Condition]] = None, apply_all_types: bool = False
):
    """Execute the dedupe/rewrite operation based on args.

    Args:
        args: Command-line arguments (or GUI-generated args)
        advanced_conditions: Optional list of Condition objects for filtering files (Sprint B Feature #1)
        apply_all_types: If True, apply filters to all files; if False, auto-detect .json (Sprint B Feature #1)

    Returns:
        tuple: (output_text, substitution_map, removal_stats, detailed_stats) where:
            - output_text: processed file content
            - substitution_map: maps removed keys to replacements (Task #23)
            - removal_stats: dict with removal counters (Task v2.9.22)
            - detailed_stats: list of DetailedStatEntry objects (Sprint B Feature #3 v2.9.31)
    """
    from .. import rewriter as rw
    from ..rewriter.detailed_stats import get_global_collector

    # Enable detailed stats collection (Sprint B Feature #3)
    collector = get_global_collector()
    collector.clear()
    collector.enable()

    # Initialize removal statistics counter
    stats = {
        "dedupe": 0,
        "eliminate": 0,
        "numeric_keys": 0,
        "empty_values": 0,
        "duplicate_child": 0,
        "array_duplicates_consecutive": 0,
        "array_duplicates_all": 0,
        "no_siblings": 0,
        "advanced_filters_filtered": 0,  # Sprint B Feature #1
    }

    # Apply advanced filters BEFORE processing (Sprint B Feature #1)
    if advanced_conditions:
        # Auto-detect JSON files unless apply_all_types is True
        input_file = args.input
        should_filter = apply_all_types or input_file.endswith((".json", ".JSON"))

        if should_filter:
            # Apply filters
            filtered_files, filtered_out = apply_conditions_to_files(
                [input_file], advanced_conditions, logic_op="AND", enabled=True
            )

            stats["advanced_filters_filtered"] = filtered_out

            # If file was filtered out, skip processing (Q6: process all if zero files pass)
            # But since we're only checking single file here, if it's filtered out, we skip it
            if not filtered_files:
                # Return empty result (file was filtered out)
                collector.disable()
                return "", {}, stats, []

    # Read input
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    # Parse based on format
    if args.from_ts:
        # TypeScript/JavaScript object literal
        obj = rw.ts_process_full_preserving(text)
    else:
        # Pure JSON
        obj = rw.parse_json_preserving_duplicates_text(text)

    # Sprint A v2.9.29: Resolve existing references FIRST (if enabled)
    if hasattr(args, "resolve_references") and args.resolve_references:
        obj, ref_stats = rw.resolve_references(obj)
        stats["references_resolved"] = ref_stats.get("resolved", 0)
        stats["references_invalid"] = ref_stats.get("invalid", 0)

    # Apply transformations with counting
    obj, stats["dedupe"] = rw.dedupe(obj)

    if args.join_keys:
        obj, _ = rw.join_keys(obj)  # join_keys doesn't remove items

    # Build substitution map for eliminated keys (Task #23 - v2.9.14 COMPLETO)
    substitution_map = {}
    if args.eliminate_duplicates:
        # Extract all keys AND values before elimination
        old_keys_values = rw.extract_all_keys_from_obj(obj.data if hasattr(obj, "data") else obj, prefix="t")
        obj, stats["eliminate"] = rw.eliminate_duplicates(obj)
        # Extract all keys AND values after elimination
        new_keys_values = rw.extract_all_keys_from_obj(obj.data if hasattr(obj, "data") else obj, prefix="t")
        # Build substitution map based on VALUE EQUALITY (not string similarity)
        substitution_map = rw.build_substitution_map_by_value(old_keys_values, new_keys_values)

    # Exclude numeric keys if requested
    if hasattr(args, "exclude_numeric") and args.exclude_numeric:
        obj, stats["numeric_keys"] = rw.exclude_numeric_keys(obj)

    # Skip empty values if requested
    if hasattr(args, "skip_empty") and args.skip_empty:
        obj, stats["empty_values"] = rw.skip_empty_values(obj)

    # Avoid duplicate child keys if requested
    if hasattr(args, "avoid_duplicate_child_keys") and args.avoid_duplicate_child_keys:
        obj, stats["duplicate_child"] = rw.avoid_duplicate_child_keys(obj)

    # Remove duplicate array values if requested (Task #8 - v2.9.8)
    if hasattr(args, "remove_dup_consecutive") and args.remove_dup_consecutive:
        obj, stats["array_duplicates_consecutive"] = rw.remove_duplicate_array_values(obj, consecutive_only=True)

    if hasattr(args, "remove_dup_all") and args.remove_dup_all:
        obj, stats["array_duplicates_all"] = rw.remove_duplicate_array_values(obj, consecutive_only=False)

    # Skip keys without siblings if requested (Task #35 - v2.9.11)
    if hasattr(args, "skip_no_siblings") and args.skip_no_siblings:
        obj, stats["no_siblings"] = rw.skip_keys_without_siblings(obj)

    # Remove duplicate objects if requested (Task #52 - v2.9.27 + Sprint A v2.9.29 + Sprint B Feature #4 v2.9.30)
    if hasattr(args, "remove_duplicate_objects") and args.remove_duplicate_objects:
        # Sprint A v2.9.29: Use create_references() if use_references mode enabled
        if hasattr(args, "use_references") and args.use_references:
            # Use new reference resolver (Sprint A + Sprint B Feature #4)
            format_type = getattr(args, "reference_format", "$ref")
            include_line_numbers = getattr(args, "include_line_numbers_ref", True)
            use_relative_paths = getattr(args, "use_relative_paths", False)

            obj, ref_stats = rw.create_references(
                obj,
                mode="references",
                include_line_numbers=include_line_numbers,
                format_type=format_type,
                use_relative_path=use_relative_paths,
            )
            stats["references_created"] = ref_stats.get("created", 0)
            stats["duplicate_objects"] = ref_stats.get("created", 0)  # For backward compatibility
        else:
            # Use legacy remove_duplicate_objects (delete mode)
            threshold = getattr(args, "duplicate_threshold", 100) / 100.0  # Convert percentage to 0.0-1.0
            include_arrays = getattr(args, "include_duplicate_arrays", False)
            mode = getattr(args, "duplicate_mode", "remove")
            obj, stats["duplicate_objects"], dup_stats = rw.remove_duplicate_objects(
                obj, threshold=threshold, include_arrays=include_arrays, mode=mode
            )

    # Enforce consistent case if requested (Task #9 - v2.9.8)
    if hasattr(args, "enforce_case") and args.enforce_case:
        case_style = getattr(args, "case_style", "camel")
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
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output_text)

    # Collect detailed stats and disable collector (Sprint B Feature #3)
    detailed_stats = [entry.to_dict() for entry in collector.get_entries()]
    collector.disable()

    return output_text, substitution_map, stats, detailed_stats


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
        self._apply_accessibility()

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
        self.chk_avoid_dup_child.setToolTip(
            "Merge parent.child.child -> parent.child (e.g., t.pages.home.home -> t.pages.home)"
        )
        self.chk_normalize_escaping = QCheckBox("Normalize escaping")
        self.chk_normalize_escaping.setToolTip(
            "Auto-detect excessive escaping (\\\\\\' or more) and normalize to \\' (Task #22)"
        )
        self.chk_convert_arrays = QCheckBox("Convert arrays to objects")
        self.chk_convert_arrays.setToolTip("Convert string arrays to objects with generated keys (Task #21)")
        self.chk_skip_no_siblings = QCheckBox("Skip keys without siblings")
        self.chk_skip_no_siblings.setToolTip(
            "Remove serial hierarchies (chains) where keys don't have siblings (Task #35)"
        )

        # Task #52 - Remove duplicate objects
        self.chk_remove_dup_objects = QCheckBox("Remove duplicate objects")
        self.chk_remove_dup_objects.setToolTip(
            "Remove objects with identical or similar values, keeping the first occurrence (smallest line number)"
        )
        self.chk_include_dup_arrays = QCheckBox("Include arrays")
        self.chk_include_dup_arrays.setToolTip("Also check arrays for duplicates (only when all elements match)")
        self.lbl_dup_threshold = QLabel("Similarity:")
        self.spin_dup_threshold = QSpinBox()
        self.spin_dup_threshold.setRange(50, 100)
        self.spin_dup_threshold.setValue(100)
        self.spin_dup_threshold.setSuffix("%")
        self.spin_dup_threshold.setToolTip(
            "Minimum similarity percentage (100% = exact match only, 80% = allow 20% field differences)"
        )
        self.combo_dup_mode = QComboBox()
        self.combo_dup_mode.addItems(["Remove (default)", "Reference ($ref)"])
        self.combo_dup_mode.setToolTip("Remove: delete duplicates | Reference: replace with $ref:path to original")

        # Task #23 - Update orphaned references
        self.chk_update_refs = QCheckBox("Update references in project")
        self.chk_update_refs.setToolTip(
            "Update orphaned translation references (t.key.path) in .tsx/.jsx files after eliminating duplicates (Task #23)"
        )
        self.ed_project_dir = QLineEdit()
        self.ed_project_dir.setToolTip("Project directory containing .tsx/.jsx/.ts/.js files to update")
        self.btn_project_browse = QPushButton("Browse…")
        self.btn_project_browse.setToolTip("Browse for project directory")
        self.chk_ref_backup = QCheckBox("Create backups")
        self.chk_ref_backup.setToolTip("Create .bak files before modifying references")
        self.chk_ref_backup.setChecked(True)

        self.chk_remove_dup_consecutive = QCheckBox("Remove consecutive duplicates")
        self.chk_remove_dup_consecutive.setToolTip(
            "Remove only consecutive duplicates in arrays: ['a','a','b'] → ['a','b']"
        )
        self.chk_remove_dup_all = QCheckBox("Remove all duplicates")
        self.chk_remove_dup_all.setToolTip("Remove all duplicates in arrays (set behavior): ['a','b','a'] → ['a','b']")
        self.chk_enforce_case = QCheckBox("Enforce consistent case")
        self.chk_enforce_case.setToolTip(
            "Automatically convert all keys to consistent case style (warns on inconsistencies)"
        )
        self.chk_enforce_case.setChecked(True)  # Applied automatically
        self.combo_case_style = QComboBox()
        self.combo_case_style.addItems(["camelCase", "PascalCase", "snake_case", "kebab-case"])
        self.combo_case_style.setCurrentIndex(0)  # Default: camelCase
        self.combo_case_style.setToolTip("Target case style for key conversion")
        self.chk_validate_case = QCheckBox("Validate case before applying")
        self.chk_validate_case.setToolTip(
            "Show preview dialog with before/after comparison before applying case conversion"
        )
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

        # Sprint A Feature: Reference Resolver (v2.9.29)
        self.lbl_ref_mode = QLabel("Duplicate handling:")
        self.radio_delete_dups = QRadioButton("Delete duplicates")
        self.radio_delete_dups.setToolTip("Remove duplicate objects (default behavior)")
        self.radio_delete_dups.setChecked(True)  # Default mode
        self.radio_use_refs = QRadioButton("Use references ($ref)")
        self.radio_use_refs.setToolTip("Replace duplicates with $ref:path:line references")
        self.chk_resolve_refs = QCheckBox("Resolve existing references")
        self.chk_resolve_refs.setToolTip("Expand $ref:path:line to actual values before processing")
        self.chk_resolve_refs.setChecked(False)

        # Sprint B Feature #4: Reference Format Configuration (v2.9.30)
        self.btn_configure_format = QPushButton("⚙️ Configure Format...")
        self.btn_configure_format.setToolTip("Configure reference format style and options")

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
        # Clear the existing VBoxLayout and replace with QGridLayout
        g = QGridLayout()

        # Remove the old layout and set the new one
        old_layout = self.main_widget.layout()
        if old_layout:
            QWidget().setLayout(old_layout)  # Take ownership to delete
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

        # Row 9: Reference Resolver (Sprint A v2.9.29)
        g.addWidget(self.lbl_ref_mode, 9, 0)
        g.addWidget(self.radio_delete_dups, 9, 1, 1, 2)
        g.addWidget(self.radio_use_refs, 9, 3, 1, 2)

        # Row 10: Resolve references checkbox + Configure Format button (Sprint B Feature #4)
        g.addWidget(self.chk_resolve_refs, 10, 0, 1, 2)
        g.addWidget(self.btn_configure_format, 10, 2, 1, 2)

        # Row 11: Indent and run button
        g.addWidget(self.lbl_indent, 11, 0)
        g.addWidget(self.spin_indent, 11, 1)
        g.addWidget(self.btn_run, 11, 4)

    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.btn_in.clicked.connect(self._open_in)
        self.btn_out.clicked.connect(self._open_out)
        self.btn_project_browse.clicked.connect(self._browse_project_dir)
        self.btn_run.clicked.connect(self._rewrite)
        self.btn_advanced_filters.clicked.connect(self._open_advanced_filters_dialog)
        self.btn_configure_format.clicked.connect(self._open_format_config_dialog)

        # Sprint A v2.9.29: Save preferences when reference resolver options change
        self.radio_delete_dups.toggled.connect(self._save_preferences)
        self.radio_use_refs.toggled.connect(self._save_preferences)
        self.chk_resolve_refs.toggled.connect(self._save_preferences)

    # UI Helper Methods

    def _open_in(self) -> None:
        """Browse for input file."""
        f, _ = QFileDialog.getOpenFileName(
            self, "Select input", "", "JSON/TS/JS (*.json *.ts *.tsx *.js *.jsx);;All (*)"
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
        d = QFileDialog.getExistingDirectory(self, "Select project directory", "", QFileDialog.Option.ShowDirsOnly)
        if d:
            self.ed_project_dir.setText(d)

    def _open_format_config_dialog(self) -> None:
        """Open dialog to configure reference format (Sprint B Feature #4 - v2.9.30)."""
        settings = QSettings("Clarify", "JsonRewriter")

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Reference Format Configuration")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)

        # Active options group
        active_group = QGroupBox("Format Options")
        active_layout = QVBoxLayout()

        # Format dropdown
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Reference format:"))
        combo_format = QComboBox()
        combo_format.addItems(["$ref: (Default)", "#/ (JSON Pointer)", "@ (Compact)"])
        current_format = settings.value("reference_format", "$ref")
        if current_format == "$ref":
            combo_format.setCurrentIndex(0)
        elif current_format == "#/":
            combo_format.setCurrentIndex(1)
        elif current_format == "@":
            combo_format.setCurrentIndex(2)
        format_layout.addWidget(combo_format)
        active_layout.addLayout(format_layout)

        # Checkboxes
        chk_line_numbers = QCheckBox("Include line numbers")
        chk_line_numbers.setChecked(settings.value("include_line_numbers_ref", True, type=bool))
        chk_line_numbers.setToolTip("Append :line_number to references (e.g., $ref:path:123)")
        active_layout.addWidget(chk_line_numbers)

        chk_relative = QCheckBox("Use relative paths")
        chk_relative.setChecked(settings.value("use_relative_paths", False, type=bool))
        chk_relative.setToolTip("Remove 'root.' prefix from paths (e.g., users.admin instead of root.users.admin)")
        active_layout.addWidget(chk_relative)

        # Preview label
        preview_label = QLabel()
        preview_label.setStyleSheet(
            "background-color: #f0f0f0; padding: 8px; border: 1px solid #ccc; font-family: monospace;"
        )
        preview_label.setWordWrap(True)

        def update_preview():
            fmt = ["$ref", "#/", "@"][combo_format.currentIndex()]
            path = "users.admin" if chk_relative.isChecked() else "root.users.admin"
            line = ":123" if chk_line_numbers.isChecked() else ""
            example = f"{fmt}:{path}{line}" if fmt == "$ref" else f"{fmt}{path}{line}"
            preview_label.setText(f"Example: <b>{example}</b>")

        combo_format.currentIndexChanged.connect(update_preview)
        chk_line_numbers.toggled.connect(update_preview)
        chk_relative.toggled.connect(update_preview)
        update_preview()

        active_layout.addWidget(QLabel("Preview:"))
        active_layout.addWidget(preview_label)
        active_group.setLayout(active_layout)
        layout.addWidget(active_group)

        # Future features group (grayed out)
        future_group = QGroupBox("Cross-File References (Coming Soon)")
        future_group.setEnabled(False)
        future_layout = QVBoxLayout()
        future_layout.addWidget(QCheckBox("Enable cross-file references"))
        future_layout.addWidget(QCheckBox("Use absolute file paths"))
        future_group.setLayout(future_layout)
        layout.addWidget(future_group)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )

        def reset_defaults():
            combo_format.setCurrentIndex(0)
            chk_line_numbers.setChecked(True)
            chk_relative.setChecked(False)
            update_preview()

        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(reset_defaults)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show dialog and save if accepted
        if dialog.exec() == QDialog.DialogCode.Accepted:
            format_map = {0: "$ref", 1: "#/", 2: "@"}
            settings.setValue("reference_format", format_map[combo_format.currentIndex()])
            settings.setValue("include_line_numbers_ref", chk_line_numbers.isChecked())
            settings.setValue("use_relative_paths", chk_relative.isChecked())

    def _open_advanced_filters_dialog(self) -> None:
        """Open dialog to configure advanced file filters (Sprint B Feature #1)."""
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Advanced File Filters")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(400)

        layout = QVBoxLayout(dialog)

        # Info label
        info = QLabel(
            "Configure filters to apply BEFORE processing files.\nFilters use AND logic (all conditions must match)."
        )
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
            combo_op.addItems(
                [
                    "",
                    "contains",
                    "not contains",
                    "equals",
                    "not equals",
                    "starts with",
                    "ends with",
                    ">",
                    "<",
                    ">=",
                    "<=",
                ]
            )

            ed_value = QLineEdit()
            ed_value.setPlaceholderText("Filter value")

            combo_scope = QComboBox()
            combo_scope.addItems(
                ["none", "brackets", "braces", "parentheses", "custom", "tag", "specific-tag", "hierarchical"]
            )

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
                    "Filters will be applied BEFORE processing files.",
                )
            else:
                QMessageBox.information(
                    self, "Filters Cleared", "❌ No filters configured. All files will be processed."
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

                with open(self.ed_in.text().strip(), "r", encoding="utf-8") as f:
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
                with open(out_path, "w", encoding="utf-8") as f:
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
            case_style=self.combo_case_style.currentText()
            .lower()
            .replace("-", "")
            .replace("case", ""),  # 'camelCase' -> 'camel'
            is_file=self.chk_is_file.isChecked(),
            remove_duplicate_objects=self.chk_remove_dup_objects.isChecked(),
            duplicate_threshold=self.spin_dup_threshold.value(),
            include_duplicate_arrays=self.chk_include_dup_arrays.isChecked(),
            duplicate_mode="reference" if self.combo_dup_mode.currentIndex() == 1 else "remove",
            # Sprint A v2.9.29: Reference Resolver
            resolve_references=self.chk_resolve_refs.isChecked(),
            use_references=self.radio_use_refs.isChecked(),
            # Sprint B Feature #4 v2.9.30: Reference Format Configuration
            reference_format=QSettings("Clarify", "JsonRewriter").value("reference_format", "$ref", type=str),
            include_line_numbers_ref=QSettings("Clarify", "JsonRewriter").value(
                "include_line_numbers_ref", True, type=bool
            ),
            use_relative_paths=QSettings("Clarify", "JsonRewriter").value("use_relative_paths", False, type=bool),
        )

        # Execute rewrite (Sprint B Feature #1: pass advanced conditions, Sprint B Feature #3: get detailed stats)
        try:
            output_text, substitution_map, removal_stats, detailed_stats = cli_dedupe(
                ns,
                advanced_conditions=self.advanced_conditions if self.advanced_filters_enabled else None,
                apply_all_types=self.chk_apply_all_types.isChecked(),
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
                    project_dir, substitution_map, create_backup=self.chk_ref_backup.isChecked()
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

                # Sprint B Feature #3 (v2.9.31): Show detailed statistics dialog if there are stats
                if detailed_stats:
                    from .statistics_dialog import StatisticsDialog

                    # Collect reference stats
                    ref_stats = {
                        "created": removal_stats.get("references_created", 0),
                        "resolved": removal_stats.get("references_resolved", 0),
                        "invalid": removal_stats.get("references_invalid", 0),
                        "deleted": removal_stats.get("deleted", 0),
                        "kept": removal_stats.get("kept", 0),
                    }
                    dialog = StatisticsDialog(detailed_stats, ref_stats, self)
                    dialog.exec()
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
        if hasattr(self, "chk_remove_dup_objects"):
            self.chk_remove_dup_objects.setChecked(settings.value("remove_duplicate_objects", False, type=bool))
            self.chk_include_dup_arrays.setChecked(settings.value("include_duplicate_arrays", False, type=bool))
            self.spin_dup_threshold.setValue(settings.value("duplicate_threshold", 100, type=int))
            self.combo_dup_mode.setCurrentIndex(settings.value("duplicate_mode_index", 0, type=int))

        # Load reference resolver settings (Sprint A v2.9.29)
        if hasattr(self, "radio_use_refs"):
            use_refs = settings.value("use_references", False, type=bool)
            if use_refs:
                self.radio_use_refs.setChecked(True)
            else:
                self.radio_delete_dups.setChecked(True)

            self.chk_resolve_refs.setChecked(settings.value("resolve_references", False, type=bool))

        # Load reference format settings (Sprint B Feature #4 v2.9.30)
        # Note: These are loaded but applied in _rewrite() when calling create_references()
        # Default values: reference_format="$ref", include_line_numbers_ref=True, use_relative_paths=False

        # Load advanced filters settings (Sprint B Feature #1)
        if hasattr(self, "chk_apply_all_types"):
            self.chk_apply_all_types.setChecked(settings.value("advanced_filters_apply_all_types", False, type=bool))
            self.advanced_filters_enabled = settings.value("advanced_filters_enabled", False, type=bool)

            # Load serialized conditions (JSON format)
            import json

            conditions_json = settings.value("advanced_filters_conditions", "[]", type=str)
            try:
                conditions_data = json.loads(conditions_json)
                self.advanced_conditions = [
                    Condition(
                        field=c["field"],
                        operator=c["operator"],
                        value=c["value"],
                        scope_type=c.get("scope_type", "none"),
                        scope_value=c.get("scope_value", ""),
                        case_sensitive=c.get("case_sensitive", True),
                        whole_word=c.get("whole_word", False),
                        use_regex=c.get("use_regex", False),
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

        # Save reference resolver settings (Sprint A v2.9.29)
        settings.setValue("use_references", self.radio_use_refs.isChecked())
        settings.setValue("resolve_references", self.chk_resolve_refs.isChecked())

        # Save advanced filters settings (Sprint B Feature #1)
        settings.setValue("advanced_filters_apply_all_types", self.chk_apply_all_types.isChecked())
        settings.setValue("advanced_filters_enabled", self.advanced_filters_enabled)

        # Serialize conditions to JSON
        import json

        conditions_data = [
            {
                "field": c.field,
                "operator": c.operator,
                "value": c.value,
                "scope_type": c.scope_type,
                "scope_value": c.scope_value,
                "case_sensitive": c.case_sensitive,
                "whole_word": c.whole_word,
                "use_regex": c.use_regex,
            }
            for c in self.advanced_conditions
        ]
        settings.setValue("advanced_filters_conditions", json.dumps(conditions_data))

    def _execute_action(self) -> None:
        """Execute the main action when ENTER is pressed."""
        self._rewrite()

    def _apply_accessibility(self) -> None:
        """Apply accessibility labels to all widgets (v2.9.37)."""
        # Input/Output file section
        AccessibilityManager.set_accessible_widget(
            self.lbl_in, "JSON Rewriter - Label - Input File", "Label indicating input file path field"
        )
        AccessibilityManager.set_accessible_widget(
            self.ed_in, "JSON Rewriter - Input - Input File Path", "JSON or TypeScript file to rewrite"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_in, "JSON Rewriter - Button - Browse Input File", "Open file browser to select input file"
        )
        AccessibilityManager.set_accessible_widget(
            self.lbl_out, "JSON Rewriter - Label - Output File", "Label indicating output file path field"
        )
        AccessibilityManager.set_accessible_widget(
            self.ed_out,
            "JSON Rewriter - Input - Output File Path",
            "Optional output file path (defaults to overwriting input file)",
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_out,
            "JSON Rewriter - Button - Browse Output File",
            "Open file browser to select output file location",
        )

        # Format options
        AccessibilityManager.set_accessible_widget(
            self.chk_from_ts,
            "JSON Rewriter - Checkbox - From TypeScript/JavaScript",
            "Parse input as TypeScript/JavaScript object literal (preserves file format)",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_ts_out,
            "JSON Rewriter - Checkbox - Emit Export Default",
            "Add 'export default ...' wrapper to output (TypeScript/JavaScript format)",
        )

        # Core transformation options
        AccessibilityManager.set_accessible_widget(
            self.chk_join,
            "JSON Rewriter - Checkbox - Join Keys",
            "Merge nested object keys into flat structure (e.g., user.name)",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_elim,
            "JSON Rewriter - Checkbox - Eliminate Duplicates",
            "Remove duplicate values and consolidate keys",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_nlb,
            "JSON Rewriter - Checkbox - No Blank Lines",
            "Remove blank lines from output for compact formatting",
        )

        # Advanced filtering options
        AccessibilityManager.set_accessible_widget(
            self.chk_exclude_numeric,
            "JSON Rewriter - Checkbox - Exclude Numeric Keys",
            "Skip keys with numeric names (e.g., '0', '123')",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_skip_empty,
            "JSON Rewriter - Checkbox - Skip Empty Values",
            "Remove key-value pairs with empty values (empty strings, null, undefined)",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_avoid_dup_child,
            "JSON Rewriter - Checkbox - Avoid Duplicate Child Keys",
            "Prevent duplicate keys in nested child objects",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_normalize_escaping,
            "JSON Rewriter - Checkbox - Normalize Escaping",
            "Standardize escape sequences (e.g., \\n, \\t) across file",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_convert_arrays,
            "JSON Rewriter - Checkbox - Convert Arrays to Objects",
            "Transform arrays into objects with indexed keys",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_skip_no_siblings,
            "JSON Rewriter - Checkbox - Skip Keys Without Siblings",
            "Remove object keys that have no sibling keys",
        )

        # Duplicate objects section
        AccessibilityManager.set_accessible_widget(
            self.chk_remove_dup_objects,
            "JSON Rewriter - Checkbox - Remove Duplicate Objects",
            "Detect and remove duplicate object structures",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_include_dup_arrays,
            "JSON Rewriter - Checkbox - Include Arrays in Duplicate Detection",
            "Also check arrays for duplicates (not just objects)",
        )
        AccessibilityManager.set_accessible_widget(
            self.lbl_dup_threshold,
            "JSON Rewriter - Label - Similarity Threshold",
            "Label indicating similarity percentage threshold",
        )
        AccessibilityManager.set_accessible_widget(
            self.spin_dup_threshold,
            "JSON Rewriter - SpinBox - Similarity Threshold Percentage",
            "Percentage threshold for detecting similar objects (0-100)",
        )
        AccessibilityManager.set_accessible_widget(
            self.combo_dup_mode,
            "JSON Rewriter - ComboBox - Duplicate Detection Mode",
            "Algorithm for detecting duplicates (exact, fuzzy, semantic)",
        )

        # Reference update section
        AccessibilityManager.set_accessible_widget(
            self.chk_update_refs,
            "JSON Rewriter - Checkbox - Update References in Project",
            "Update all references in project files when keys are renamed",
        )
        AccessibilityManager.set_accessible_widget(
            self.ed_project_dir,
            "JSON Rewriter - Input - Project Directory",
            "Root directory of project to scan for references",
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_project_browse,
            "JSON Rewriter - Button - Browse Project Directory",
            "Open folder browser to select project directory",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_ref_backup,
            "JSON Rewriter - Checkbox - Create Backups",
            "Create backup files (.bak) before updating references",
        )

        # Array duplicate options
        AccessibilityManager.set_accessible_widget(
            self.chk_remove_dup_consecutive,
            "JSON Rewriter - Checkbox - Remove Consecutive Array Duplicates",
            "Remove only consecutive duplicate elements in arrays",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_remove_dup_all,
            "JSON Rewriter - Checkbox - Remove All Array Duplicates",
            "Remove all duplicate elements in arrays (keeps first occurrence)",
        )

        # Case enforcement section
        AccessibilityManager.set_accessible_widget(
            self.chk_enforce_case,
            "JSON Rewriter - Checkbox - Enforce Consistent Case",
            "Convert all keys to consistent naming convention",
        )
        AccessibilityManager.set_accessible_widget(
            self.combo_case_style,
            "JSON Rewriter - ComboBox - Case Style",
            "Naming convention style (camelCase, snake_case, PascalCase, etc.)",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_validate_case,
            "JSON Rewriter - Checkbox - Validate Case Before Applying",
            "Show preview and warnings before converting case style",
        )

        # File type filter
        AccessibilityManager.set_accessible_widget(
            self.chk_is_file,
            "JSON Rewriter - Checkbox - Is File",
            "Treat input path as single file (unchecked for directory)",
        )

        # Advanced filters
        AccessibilityManager.set_accessible_widget(
            self.btn_advanced_filters,
            "JSON Rewriter - Button - Advanced Filters",
            "Open advanced filtering dialog with custom conditions",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_apply_all_types,
            "JSON Rewriter - Checkbox - Apply to All File Types",
            "Apply filters to all file types (not just JSON files)",
        )

        # Reference mode section
        AccessibilityManager.set_accessible_widget(
            self.lbl_ref_mode,
            "JSON Rewriter - Label - Duplicate Handling Mode",
            "Label indicating duplicate handling mode selection",
        )
        AccessibilityManager.set_accessible_widget(
            self.radio_delete_dups,
            "JSON Rewriter - RadioButton - Delete Duplicates",
            "Delete duplicate objects permanently",
        )
        AccessibilityManager.set_accessible_widget(
            self.radio_use_refs,
            "JSON Rewriter - RadioButton - Use References",
            "Replace duplicates with $ref pointers (JSON Schema standard)",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_resolve_refs,
            "JSON Rewriter - Checkbox - Resolve Existing References",
            "Expand existing $ref pointers back to full objects",
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_configure_format,
            "JSON Rewriter - Button - Configure Reference Format",
            "Configure reference format settings ($ref, JSONPath, custom)",
        )

        # Indentation section
        AccessibilityManager.set_accessible_widget(
            self.lbl_indent, "JSON Rewriter - Label - Indentation", "Label indicating indentation setting"
        )
        AccessibilityManager.set_accessible_widget(
            self.spin_indent,
            "JSON Rewriter - SpinBox - Indentation Spaces",
            "Number of spaces for indentation (0 or negative for compact mode)",
        )

        # Action button
        AccessibilityManager.set_accessible_widget(
            self.btn_run, "JSON Rewriter - Button - Run Rewrite", "Execute JSON rewrite operation with selected options"
        )
