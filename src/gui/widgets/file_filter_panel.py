#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File Filter Panel - Advanced file filtering widget

Extracted from file_list_dock.py (v2.9.114 - Phase 2.4.1)
Provides comprehensive file filtering options.

Features:
- Regex pattern matching
- Size filters (min/max with units)
- MTime filters (before/after dates)
- Extension filters (comma-separated)
- Depth limit for recursion
- Exclude directories (common + custom)
- Collapsible panel
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, Any, Tuple, List

from PySide6.QtWidgets import (
    QWidget, QGroupBox, QGridLayout, QLabel, QLineEdit,
    QCheckBox, QComboBox, QSpinBox, QDateEdit, QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Signal, QDate


class FileFilterPanel(QGroupBox):
    """Widget for advanced file filtering options."""
    
    # Signal emitted when any filter changes
    filters_changed = Signal()
    
    # Size unit multipliers
    SIZE_UNITS = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3
    }
    
    def __init__(self, title: str = "Advanced Filters", parent: QWidget | None = None):
        """
        Initialize filter panel.
        
        Args:
            title: Panel title
            parent: Parent widget
        """
        super().__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(False)  # Initially collapsed
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Setup UI components."""
        grid = QGridLayout(self)
        grid.setSpacing(8)
        
        # Row 0: Regex filter
        grid.addWidget(QLabel("Regex Pattern:"), 0, 0)
        self.ed_regex = QLineEdit()
        self.ed_regex.setPlaceholderText("e.g., ^test_.*\\.py$")
        grid.addWidget(self.ed_regex, 0, 1, 1, 2)
        
        self.chk_regex_enabled = QCheckBox("Enable Regex")
        grid.addWidget(self.chk_regex_enabled, 0, 3)
        
        # Row 1: Size filter (min)
        grid.addWidget(QLabel("Size Min:"), 1, 0)
        self.ed_size_min = QLineEdit()
        self.ed_size_min.setPlaceholderText("0")
        self.ed_size_min.setMaximumWidth(100)
        grid.addWidget(self.ed_size_min, 1, 1)
        
        self.cmb_size_min_unit = QComboBox()
        self.cmb_size_min_unit.addItems(["B", "KB", "MB", "GB"])
        self.cmb_size_min_unit.setCurrentText("KB")
        self.cmb_size_min_unit.setMaximumWidth(70)
        grid.addWidget(self.cmb_size_min_unit, 1, 2)
        
        # Row 2: Size filter (max)
        grid.addWidget(QLabel("Size Max:"), 2, 0)
        self.ed_size_max = QLineEdit()
        self.ed_size_max.setPlaceholderText("∞")
        self.ed_size_max.setMaximumWidth(100)
        grid.addWidget(self.ed_size_max, 2, 1)
        
        self.cmb_size_max_unit = QComboBox()
        self.cmb_size_max_unit.addItems(["B", "KB", "MB", "GB"])
        self.cmb_size_max_unit.setCurrentText("MB")
        self.cmb_size_max_unit.setMaximumWidth(70)
        grid.addWidget(self.cmb_size_max_unit, 2, 2)
        
        # Row 3: Modified time (after)
        grid.addWidget(QLabel("Modified After:"), 3, 0)
        self.dte_mtime_after = QDateEdit()
        self.dte_mtime_after.setCalendarPopup(True)
        self.dte_mtime_after.setSpecialValueText("No limit")
        self.dte_mtime_after.setDate(QDate(2000, 1, 1))
        grid.addWidget(self.dte_mtime_after, 3, 1, 1, 2)
        
        self.chk_mtime_after_enabled = QCheckBox("Enable")
        grid.addWidget(self.chk_mtime_after_enabled, 3, 3)
        
        # Row 4: Modified time (before)
        grid.addWidget(QLabel("Modified Before:"), 4, 0)
        self.dte_mtime_before = QDateEdit()
        self.dte_mtime_before.setCalendarPopup(True)
        self.dte_mtime_before.setSpecialValueText("No limit")
        self.dte_mtime_before.setDate(QDate.currentDate())
        grid.addWidget(self.dte_mtime_before, 4, 1, 1, 2)
        
        self.chk_mtime_before_enabled = QCheckBox("Enable")
        grid.addWidget(self.chk_mtime_before_enabled, 4, 3)
        
        # Row 5: Extensions filter
        grid.addWidget(QLabel("Extensions:"), 5, 0)
        self.ed_extensions = QLineEdit()
        self.ed_extensions.setPlaceholderText("e.g., py,js,txt")
        grid.addWidget(self.ed_extensions, 5, 1, 1, 3)
        
        # Row 6: Depth limit
        grid.addWidget(QLabel("Max Depth:"), 6, 0)
        self.spn_depth = QSpinBox()
        self.spn_depth.setMinimum(0)
        self.spn_depth.setMaximum(10)
        self.spn_depth.setValue(0)
        self.spn_depth.setSpecialValueText("Unlimited")
        self.spn_depth.setMaximumWidth(100)
        grid.addWidget(self.spn_depth, 6, 1)
        
        # Row 7-8: Exclude directories
        grid.addWidget(QLabel("Exclude Dirs:"), 7, 0)
        
        # Common excludes (checkboxes)
        exclude_layout = QVBoxLayout()
        self.chk_exclude_node_modules = QCheckBox("node_modules")
        self.chk_exclude_git = QCheckBox(".git")
        self.chk_exclude_pycache = QCheckBox("__pycache__")
        self.chk_exclude_dist = QCheckBox("dist")
        self.chk_exclude_build = QCheckBox("build")
        
        # Default: check common excludes
        self.chk_exclude_node_modules.setChecked(True)
        self.chk_exclude_git.setChecked(True)
        self.chk_exclude_pycache.setChecked(True)
        
        exclude_layout.addWidget(self.chk_exclude_node_modules)
        exclude_layout.addWidget(self.chk_exclude_git)
        exclude_layout.addWidget(self.chk_exclude_pycache)
        exclude_layout.addWidget(self.chk_exclude_dist)
        exclude_layout.addWidget(self.chk_exclude_build)
        exclude_layout.addStretch()
        
        grid.addLayout(exclude_layout, 7, 1, 2, 2)
        
        # Custom exclude patterns
        grid.addWidget(QLabel("Custom:"), 9, 0)
        self.ed_exclude_custom = QLineEdit()
        self.ed_exclude_custom.setPlaceholderText("e.g., temp,cache,*.tmp")
        grid.addWidget(self.ed_exclude_custom, 9, 1, 1, 3)
    
    def _connect_signals(self) -> None:
        """Connect internal signals."""
        # Emit filters_changed when any filter is modified
        self.ed_regex.textChanged.connect(self.filters_changed.emit)
        self.chk_regex_enabled.toggled.connect(self.filters_changed.emit)
        self.ed_size_min.textChanged.connect(self.filters_changed.emit)
        self.ed_size_max.textChanged.connect(self.filters_changed.emit)
        self.cmb_size_min_unit.currentIndexChanged.connect(self.filters_changed.emit)
        self.cmb_size_max_unit.currentIndexChanged.connect(self.filters_changed.emit)
        self.dte_mtime_after.dateChanged.connect(self.filters_changed.emit)
        self.dte_mtime_before.dateChanged.connect(self.filters_changed.emit)
        self.chk_mtime_after_enabled.toggled.connect(self.filters_changed.emit)
        self.chk_mtime_before_enabled.toggled.connect(self.filters_changed.emit)
        self.ed_extensions.textChanged.connect(self.filters_changed.emit)
        self.spn_depth.valueChanged.connect(self.filters_changed.emit)
        self.chk_exclude_node_modules.toggled.connect(self.filters_changed.emit)
        self.chk_exclude_git.toggled.connect(self.filters_changed.emit)
        self.chk_exclude_pycache.toggled.connect(self.filters_changed.emit)
        self.chk_exclude_dist.toggled.connect(self.filters_changed.emit)
        self.chk_exclude_build.toggled.connect(self.filters_changed.emit)
        self.ed_exclude_custom.textChanged.connect(self.filters_changed.emit)
    
    # Public API
    
    def get_filters(self) -> Dict[str, Any]:
        """
        Get current filter configuration.
        
        Returns:
            Dictionary with all filter values
        """
        filters = {
            'regex': {
                'pattern': self.ed_regex.text(),
                'enabled': self.chk_regex_enabled.isChecked()
            },
            'size': {
                'min': self._parse_size(self.ed_size_min.text(), self.cmb_size_min_unit.currentText()),
                'max': self._parse_size(self.ed_size_max.text(), self.cmb_size_max_unit.currentText())
            },
            'mtime': {
                'after': self.dte_mtime_after.date().toPython() if self.chk_mtime_after_enabled.isChecked() else None,
                'before': self.dte_mtime_before.date().toPython() if self.chk_mtime_before_enabled.isChecked() else None
            },
            'extensions': self._parse_extensions(self.ed_extensions.text()),
            'depth': self.spn_depth.value(),
            'exclude_dirs': self._get_excluded_dirs()
        }
        return filters
    
    def set_filters(self, filters: Dict[str, Any]) -> None:
        """
        Set filter configuration.
        
        Args:
            filters: Filter dictionary
        """
        # Regex
        if 'regex' in filters:
            self.ed_regex.setText(filters['regex'].get('pattern', ''))
            self.chk_regex_enabled.setChecked(filters['regex'].get('enabled', False))
        
        # Size
        if 'size' in filters:
            size_min = filters['size'].get('min', 0)
            size_max = filters['size'].get('max')
            
            if size_min:
                self.ed_size_min.setText(str(size_min))
            if size_max:
                self.ed_size_max.setText(str(size_max))
        
        # MTime
        if 'mtime' in filters:
            after = filters['mtime'].get('after')
            before = filters['mtime'].get('before')
            
            if after:
                self.dte_mtime_after.setDate(QDate(after))
                self.chk_mtime_after_enabled.setChecked(True)
            
            if before:
                self.dte_mtime_before.setDate(QDate(before))
                self.chk_mtime_before_enabled.setChecked(True)
        
        # Extensions
        if 'extensions' in filters:
            self.ed_extensions.setText(','.join(filters['extensions']))
        
        # Depth
        if 'depth' in filters:
            self.spn_depth.setValue(filters['depth'])
        
        # Exclude dirs
        if 'exclude_dirs' in filters:
            exclude_dirs = filters['exclude_dirs']
            self.chk_exclude_node_modules.setChecked('node_modules' in exclude_dirs)
            self.chk_exclude_git.setChecked('.git' in exclude_dirs)
            self.chk_exclude_pycache.setChecked('__pycache__' in exclude_dirs)
            self.chk_exclude_dist.setChecked('dist' in exclude_dirs)
            self.chk_exclude_build.setChecked('build' in exclude_dirs)
    
    def clear_filters(self) -> None:
        """Clear all filters to defaults."""
        self.ed_regex.clear()
        self.chk_regex_enabled.setChecked(False)
        self.ed_size_min.clear()
        self.ed_size_max.clear()
        self.chk_mtime_after_enabled.setChecked(False)
        self.chk_mtime_before_enabled.setChecked(False)
        self.ed_extensions.clear()
        self.spn_depth.setValue(0)
        
        # Reset exclude dirs to defaults
        self.chk_exclude_node_modules.setChecked(True)
        self.chk_exclude_git.setChecked(True)
        self.chk_exclude_pycache.setChecked(True)
        self.chk_exclude_dist.setChecked(False)
        self.chk_exclude_build.setChecked(False)
        self.ed_exclude_custom.clear()
    
    def validate_filters(self) -> Tuple[bool, str]:
        """
        Validate current filter configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate regex
        if self.chk_regex_enabled.isChecked():
            pattern = self.ed_regex.text()
            if pattern:
                try:
                    re.compile(pattern)
                except re.error as e:
                    return False, f"Invalid regex pattern: {e}"
        
        # Validate size range
        size_min = self._parse_size(self.ed_size_min.text(), self.cmb_size_min_unit.currentText())
        size_max = self._parse_size(self.ed_size_max.text(), self.cmb_size_max_unit.currentText())
        
        if size_min and size_max and size_min > size_max:
            return False, "Size min cannot be greater than size max"
        
        # Validate date range
        if self.chk_mtime_after_enabled.isChecked() and self.chk_mtime_before_enabled.isChecked():
            after = self.dte_mtime_after.date()
            before = self.dte_mtime_before.date()
            if after > before:
                return False, "Modified after date cannot be later than before date"
        
        return True, ""
    
    # Helper methods
    
    def _parse_size(self, text: str, unit: str) -> int | None:
        """Parse size string to bytes."""
        if not text or not text.strip():
            return None
        
        try:
            value = float(text)
            multiplier = self.SIZE_UNITS.get(unit, 1)
            return int(value * multiplier)
        except ValueError:
            return None
    
    def _parse_extensions(self, text: str) -> List[str]:
        """Parse comma-separated extensions."""
        if not text or not text.strip():
            return []
        
        # Split by comma, strip whitespace, remove dots if present
        extensions = [
            ext.strip().lstrip('.')
            for ext in text.split(',')
            if ext.strip()
        ]
        return extensions
    
    def _get_excluded_dirs(self) -> List[str]:
        """Get list of excluded directories."""
        excluded = []
        
        if self.chk_exclude_node_modules.isChecked():
            excluded.append('node_modules')
        if self.chk_exclude_git.isChecked():
            excluded.append('.git')
        if self.chk_exclude_pycache.isChecked():
            excluded.append('__pycache__')
        if self.chk_exclude_dist.isChecked():
            excluded.append('dist')
        if self.chk_exclude_build.isChecked():
            excluded.append('build')
        
        # Add custom excludes
        custom = self.ed_exclude_custom.text()
        if custom:
            excluded.extend([d.strip() for d in custom.split(',') if d.strip()])
        
        return excluded


__all__ = ['FileFilterPanel']
