#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON Tree Widget - Tree navigation for JSON structures

Extracted from json_editor_tab.py (v2.9.114 - Phase 2.6.1)
Provides hierarchical tree view for JSON data with visual indicators.

Features:
- Click node → jump to line in editor
- Collapse/Expand controls
- Visual indicators: {} for objects, [] for arrays
- Color coding by type (Object, Array, String, Number, Boolean, Null)

Pattern: Composite (GoF) - recursive tree structure
"""

from __future__ import annotations
from typing import Optional, Dict, Any
import json

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtGui import QColor


class JsonTreeWidget(QTreeWidget):
    """
    Tree widget for JSON structure navigation.

    Pattern: Composite (GoF)
    - Recursive tree structure
    - Each node can have children (objects/arrays)

    Features:
    - Click node → jump to line in editor
    - Collapse/Expand controls
    - Visual indicators: {} for objects, [] for arrays
    - Color coding by type

    Signals:
    - node_clicked(int): Emitted when node is clicked (line number)
    """

    node_clicked = Signal(int)  # Emits line number when node clicked

    def __init__(self, parent=None):
        """
        Initialize JSON tree widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setHeaderLabels([tr("json_tree_widget.header_key"), tr("json_tree_widget.header_value"), tr("json_tree_widget.header_type")])
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 300)
        self.setColumnWidth(2, 80)
        self.setAlternatingRowColors(True)
        self.itemClicked.connect(self._on_item_clicked)

        # Store line numbers for each node
        self.line_map: Dict[QTreeWidgetItem, int] = {}

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Handle tree item click - emit line number.

        Args:
            item: Clicked tree item
            column: Column index (unused)
        """
        if item in self.line_map:
            self.node_clicked.emit(self.line_map[item])

    def build_tree(self, json_text: str):
        """
        Build tree from JSON text.

        Pattern: Composite (recursive tree building)

        Args:
            json_text: JSON string to parse and build tree from
        """
        self.clear()
        self.line_map.clear()

        try:
            obj = json.loads(json_text)
            self._add_node(None, "root", obj, 1)
            self.expandAll()
        except json.JSONDecodeError:
            # Invalid JSON - don't build tree
            pass

    def _add_node(self, parent: Optional[QTreeWidgetItem], key: str, value: Any, line: int):
        """
        Recursively add node to tree.

        Pattern: Composite (GoF) - recursive structure

        Args:
            parent: Parent tree item (None for root)
            key: Key name for this node
            value: Value (can be dict, list, str, number, bool, None)
            line: Line number in editor
        """
        if parent is None:
            item = QTreeWidgetItem(self)
        else:
            item = QTreeWidgetItem(parent)

        # Store line number
        self.line_map[item] = line

        if isinstance(value, dict):
            # Object node
            item.setText(0, key)
            item.setText(1, f"{{...}} ({len(value)} keys)")
            item.setText(2, "Object")
            item.setForeground(0, QColor("#9CDCFE"))  # Light blue

            # Add children
            for child_key, child_value in value.items():
                self._add_node(item, child_key, child_value, line + 1)

        elif isinstance(value, list):
            # Array node
            item.setText(0, key)
            item.setText(1, f"[...] ({len(value)} items)")
            item.setText(2, "Array")
            item.setForeground(0, QColor("#4EC9B0"))  # Teal

            # Add children
            for i, child_value in enumerate(value):
                self._add_node(item, f"[{i}]", child_value, line + 1)

        elif isinstance(value, str):
            # String value
            item.setText(0, key)
            display_value = value[:50] + "..." if len(value) > 50 else value
            item.setText(1, f'"{display_value}"')
            item.setText(2, "String")
            item.setForeground(1, QColor("#CE9178"))  # Orange

        elif isinstance(value, bool):
            # Boolean value
            item.setText(0, key)
            item.setText(1, str(value).lower())
            item.setText(2, "Boolean")
            item.setForeground(1, QColor("#569CD6"))  # Blue

        elif isinstance(value, (int, float)):
            # Number value
            item.setText(0, key)
            item.setText(1, str(value))
            item.setText(2, "Number")
            item.setForeground(1, QColor("#B5CEA8"))  # Light green

        elif value is None:
            # Null value
            item.setText(0, key)
            item.setText(1, "null")
            item.setText(2, "Null")
            item.setForeground(1, QColor("#808080"))  # Gray


__all__ = ['JsonTreeWidget']
