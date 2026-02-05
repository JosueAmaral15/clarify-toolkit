#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Operation Options Widget - Set operations configuration component

Extracted from set_operations_dock.py (v2.9.114 - Phase 2.3.2)
Provides UI for selecting operations, comparison modes, and options.

Features:
- Operation checkboxes (Intersection, Union, Difference, Symmetric)
- Comparison mode radio buttons
- Advanced options (case sensitivity, empty values, arrays)
- Output format selection
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules

from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from src.i18n import tooltip_tr
from src.i18n.translator import tr
from src.accessibility_manager import AccessibilityManager


class OperationOptionsWidget(QWidget):
    """Widget for configuring set operation options."""

    # Signal emitted when any option changes
    options_changed = Signal()

    def __init__(self, parent: QWidget | None = None):
        """
        Initialize operation options widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        self._apply_accessibility()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # === Operations Section ===
        ops_group = QGroupBox(tr("operation_options.operations_group"))
        ops_layout = QVBoxLayout()

        ops_layout.addWidget(QLabel(tr("operation_options.select_operations")))
        self.chk_intersection = QCheckBox(tr("operation_options.chk_intersection"))
        self.chk_intersection.setToolTip(tooltip_tr("set_ops.intersection"))
        self.chk_union = QCheckBox(tr("operation_options.chk_union"))
        self.chk_union.setToolTip(tooltip_tr("set_ops.union"))
        self.chk_difference = QCheckBox(tr("operation_options.chk_difference"))
        self.chk_difference.setToolTip(tooltip_tr("set_ops.difference"))
        self.chk_symmetric = QCheckBox(tr("operation_options.chk_symmetric"))
        self.chk_symmetric.setToolTip(tooltip_tr("set_ops.symmetric"))

        ops_layout.addWidget(self.chk_intersection)
        ops_layout.addWidget(self.chk_union)
        ops_layout.addWidget(self.chk_difference)
        ops_layout.addWidget(self.chk_symmetric)

        ops_group.setLayout(ops_layout)
        main_layout.addWidget(ops_group)

        # === Comparison Mode Section ===
        comp_group = QGroupBox(tr("operation_options.comparison_mode"))
        comp_layout = QVBoxLayout()

        self.radio_key_value = QRadioButton(tr("operation_options.radio_key_value"))
        self.radio_key_value.setChecked(True)
        self.radio_key_value.setToolTip(tooltip_tr("set_ops.radio_key_value"))
        self.radio_full_path = QRadioButton(tr("operation_options.radio_full_path"))
        self.radio_full_path.setToolTip(tooltip_tr("set_ops.radio_full_path"))
        self.radio_key_only = QRadioButton(tr("operation_options.radio_key_only"))
        self.radio_key_only.setToolTip(tooltip_tr("set_ops.radio_key_only"))

        self.comp_mode_group = QButtonGroup()
        self.comp_mode_group.addButton(self.radio_key_value)
        self.comp_mode_group.addButton(self.radio_full_path)
        self.comp_mode_group.addButton(self.radio_key_only)

        comp_layout.addWidget(self.radio_key_value)
        comp_layout.addWidget(self.radio_full_path)
        comp_layout.addWidget(self.radio_key_only)

        comp_group.setLayout(comp_layout)
        main_layout.addWidget(comp_group)

        # === Options Section ===
        opts_group = QGroupBox(tr("operation_options.options_group"))
        opts_layout = QVBoxLayout()

        self.chk_ignore_case_keys = QCheckBox(tr("operation_options.chk_ignore_case_keys"))
        self.chk_ignore_case_keys.setToolTip(tooltip_tr("set_ops.ignore_case_keys"))
        self.chk_ignore_case_values = QCheckBox(tr("operation_options.chk_ignore_case_values"))
        self.chk_ignore_case_values.setToolTip(tooltip_tr("set_ops.ignore_case_values"))
        self.chk_skip_empty = QCheckBox(tr("operation_options.chk_skip_empty"))
        self.chk_skip_empty.setToolTip(tooltip_tr("set_ops.skip_empty"))
        self.chk_arrays_ignore_order = QCheckBox(tr("operation_options.chk_arrays_ignore_order"))
        self.chk_arrays_ignore_order.setToolTip(tooltip_tr("set_ops.arrays_ignore_order"))

        opts_layout.addWidget(self.chk_ignore_case_keys)
        opts_layout.addWidget(self.chk_ignore_case_values)
        opts_layout.addWidget(self.chk_skip_empty)
        opts_layout.addWidget(self.chk_arrays_ignore_order)

        opts_group.setLayout(opts_layout)
        main_layout.addWidget(opts_group)

        # === Output Format Section ===
        output_group = QGroupBox(tr("operation_options.output_format"))
        output_layout = QVBoxLayout()

        output_layout.addWidget(QLabel(tr("operation_options.select_output")))
        self.combo_output = QComboBox()
        self.combo_output.addItems([
            tr("operation_options.output_json_nested"),
            tr("operation_options.output_separate"),
            tr("operation_options.output_display_only")
        ])
        self.combo_output.setToolTip(tooltip_tr("set_ops.combo_output"))
        output_layout.addWidget(self.combo_output)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        # Emit options_changed when any option is modified
        self.chk_intersection.toggled.connect(self.options_changed.emit)
        self.chk_union.toggled.connect(self.options_changed.emit)
        self.chk_difference.toggled.connect(self.options_changed.emit)
        self.chk_symmetric.toggled.connect(self.options_changed.emit)

        self.comp_mode_group.buttonToggled.connect(self.options_changed.emit)

        self.chk_ignore_case_keys.toggled.connect(self.options_changed.emit)
        self.chk_ignore_case_values.toggled.connect(self.options_changed.emit)
        self.chk_skip_empty.toggled.connect(self.options_changed.emit)
        self.chk_arrays_ignore_order.toggled.connect(self.options_changed.emit)

        self.combo_output.currentIndexChanged.connect(self.options_changed.emit)

    def _apply_accessibility(self) -> None:
        """Apply accessibility labels."""
        # Operations
        AccessibilityManager.set_accessible_widget(
            self.chk_intersection, "Set Operations - Checkbox - Intersection",
            "Calculate intersection (common keys between files)"
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_union, "Set Operations - Checkbox - Union",
            "Calculate union (all keys from all files)"
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_difference, "Set Operations - Checkbox - Difference",
            "Calculate difference (keys in A not in B)"
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_symmetric, "Set Operations - Checkbox - Symmetric Difference",
            "Calculate symmetric difference (keys in A or B but not both)"
        )

        # Comparison modes
        AccessibilityManager.set_accessible_widget(
            self.radio_key_value, "Set Operations - Radio - Key Value Mode",
            "Compare keys and values with strict types"
        )
        AccessibilityManager.set_accessible_widget(
            self.radio_full_path, "Set Operations - Radio - Full Path Mode",
            "Compare full paths using dot notation (deep nested)"
        )
        AccessibilityManager.set_accessible_widget(
            self.radio_key_only, "Set Operations - Radio - Key Only Mode",
            "Compare only keys ignoring values"
        )

        # Advanced options
        AccessibilityManager.set_accessible_widget(
            self.chk_ignore_case_keys, "Set Operations - Checkbox - Ignore Case Keys",
            "Treat 'Name' and 'name' as identical keys"
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_ignore_case_values, "Set Operations - Checkbox - Ignore Case Values",
            "Treat 'Hello' and 'hello' as identical values"
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_skip_empty, "Set Operations - Checkbox - Skip Empty",
            "Skip null, empty string, empty array, empty object values"
        )

    # Public API

    def get_selected_operations(self) -> List[str]:
        """
        Get list of selected operations.

        Returns:
            List of operation symbols: ['∩', '∪', '−', '⊕']
        """
        operations = []
        if self.chk_intersection.isChecked():
            operations.append('∩')
        if self.chk_union.isChecked():
            operations.append('∪')
        if self.chk_difference.isChecked():
            operations.append('−')
        if self.chk_symmetric.isChecked():
            operations.append('⊕')
        return operations

    def get_comparison_mode(self) -> str:
        """
        Get selected comparison mode.

        Returns:
            Mode string: 'key_value', 'full_path', or 'key_only'
        """
        if self.radio_full_path.isChecked():
            return 'full_path'
        elif self.radio_key_only.isChecked():
            return 'key_only'
        else:
            return 'key_value'

    def get_options(self) -> Dict[str, bool]:
        """
        Get all option flags.

        Returns:
            Dictionary with option flags
        """
        return {
            'ignore_case_keys': self.chk_ignore_case_keys.isChecked(),
            'ignore_case_values': self.chk_ignore_case_values.isChecked(),
            'skip_empty': self.chk_skip_empty.isChecked(),
            'arrays_ignore_order': self.chk_arrays_ignore_order.isChecked(),
        }

    def get_output_format(self) -> str:
        """
        Get selected output format.

        Returns:
            Format string: 'nested', 'separate', or 'display'
        """
        index = self.combo_output.currentIndex()
        return ['nested', 'separate', 'display'][index]

    def set_configuration(self, config: Dict) -> None:
        """
        Set configuration from dictionary.

        Args:
            config: Configuration dictionary
        """
        # Set operations
        operations = config.get('operations', [])
        self.chk_intersection.setChecked('∩' in operations)
        self.chk_union.setChecked('∪' in operations)
        self.chk_difference.setChecked('−' in operations)
        self.chk_symmetric.setChecked('⊕' in operations)

        # Set comparison mode
        mode = config.get('comparison_mode', 'key_value')
        if mode == 'full_path':
            self.radio_full_path.setChecked(True)
        elif mode == 'key_only':
            self.radio_key_only.setChecked(True)
        else:
            self.radio_key_value.setChecked(True)

        # Set options
        options = config.get('options', {})
        self.chk_ignore_case_keys.setChecked(options.get('ignore_case_keys', False))
        self.chk_ignore_case_values.setChecked(options.get('ignore_case_values', False))
        self.chk_skip_empty.setChecked(options.get('skip_empty', False))
        self.chk_arrays_ignore_order.setChecked(options.get('arrays_ignore_order', False))

        # Set output format
        output_format = config.get('output_format', 'nested')
        format_index = {'nested': 0, 'separate': 1, 'display': 2}.get(output_format, 0)
        self.combo_output.setCurrentIndex(format_index)

    def clear(self) -> None:
        """Clear all selections."""
        self.chk_intersection.setChecked(False)
        self.chk_union.setChecked(False)
        self.chk_difference.setChecked(False)
        self.chk_symmetric.setChecked(False)

        self.radio_key_value.setChecked(True)

        self.chk_ignore_case_keys.setChecked(False)
        self.chk_ignore_case_values.setChecked(False)
        self.chk_skip_empty.setChecked(False)
        self.chk_arrays_ignore_order.setChecked(False)

        self.combo_output.setCurrentIndex(0)


__all__ = ['OperationOptionsWidget']
