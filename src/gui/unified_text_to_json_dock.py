#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unified Text to JSON Converter Dock
====================================

Combines two tools into one with mode switching:
1. Format Conversion (CSV, YAML, INI, TOML, etc. → JSON)
2. JSX/HTML Extraction (extract attributes from code → JSON)

Architecture:
- Delegates to original tool classes (composition pattern)
- Mode selector switches between two embedded widgets
- Keeps original code intact (no duplication)

Author: Programmer #3
Date: 2026-01-30
Version: 2.9.116
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QFrame
)

from .base_dock import BaseDock
from .text_to_json_dock import TextToJsonDock
from .advanced_extractor_dock import AdvancedExtractorDock
from src.i18n.translator import tooltip_tr, tr

# Type checking imports
if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QWidgetType


class UnifiedTextToJsonDock(BaseDock):
    """
    Unified Text to JSON Converter with two modes using composition pattern.
    
    Instead of copying code, this class embeds the original tool widgets
    and switches between them. This keeps code DRY and maintainable.
    
    Modes:
    1. Format Conversion - TextToJsonDock widget
    2. JSX/HTML Extraction - AdvancedExtractorDock widget
    """
    
    def __init__(self, parent: QWidgetType | None = None):
        # Initialize state BEFORE calling super().__init__
        # because _setup_ui() is called by parent and needs these attributes
        self.current_mode = "format_conversion"  # Default mode
        self.format_conversion_widget: TextToJsonDock | None = None
        self.jsx_extraction_widget: AdvancedExtractorDock | None = None
        
        super().__init__(tr("text_to_json.title", "Text to JSON Converter"), parent)
        self.setObjectName("UnifiedTextToJsonDock")
    
    def _setup_ui(self) -> None:
        """Setup main UI with mode selector and embedded tool widgets."""
        # Main container
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)
        
        # Mode selector section at top
        mode_section = self._create_mode_selector()
        main_layout.addLayout(mode_section)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Create scroll area for tool content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container for embedded tool widget (goes inside scroll area)
        self.tool_container = QWidget()
        self.tool_layout = QVBoxLayout(self.tool_container)
        self.tool_layout.setContentsMargins(0, 0, 0, 0)
        
        # Put container in scroll area
        scroll_area.setWidget(self.tool_container)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area, 1)  # Stretch factor 1
        
        # Set main widget
        self.setWidget(main_widget)
        
        # Load default mode
        self._switch_mode(self.current_mode)
    
    def _create_mode_selector(self) -> QHBoxLayout:
        """Create mode selector dropdown at top."""
        layout = QHBoxLayout()
        
        # Mode label
        mode_label = QLabel(tr("text_to_json.mode_label", "Mode:"))
        mode_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(mode_label)
        
        # Mode combo box
        self.mode_combo = QComboBox()
        self.mode_combo.addItem(
            tr("text_to_json.mode_format_conversion", "Format Conversion"), 
            "format_conversion"
        )
        self.mode_combo.addItem(
            tr("text_to_json.mode_jsx_extraction", "JSX/HTML Extraction"), 
            "jsx_extraction"
        )
        self.mode_combo.setToolTip(
            tooltip_tr("text_to_json.mode_tooltip",
                      "Switch between format conversion (CSV, YAML, etc.) and JSX/HTML extraction modes")
        )
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.mode_combo.setMinimumWidth(250)
        layout.addWidget(self.mode_combo)
        
        # Spacer
        layout.addStretch()
        
        return layout
    
    def _on_mode_changed(self, index: int) -> None:
        """Handle mode dropdown change."""
        mode_key = self.mode_combo.itemData(index)
        if mode_key != self.current_mode:
            self._switch_mode(mode_key)
    
    def _switch_mode(self, mode_key: str) -> None:
        """
        Switch between modes by showing/hiding embedded tool widgets.
        
        Args:
            mode_key: Either "format_conversion" or "jsx_extraction"
        """
        # Hide current widget
        if self.format_conversion_widget:
            self.format_conversion_widget.setVisible(False)
        if self.jsx_extraction_widget:
            self.jsx_extraction_widget.setVisible(False)
        
        # Show requested mode widget (create if needed)
        if mode_key == "format_conversion":
            if not self.format_conversion_widget:
                self._create_format_conversion_widget()
            self.format_conversion_widget.setVisible(True)
            
        elif mode_key == "jsx_extraction":
            if not self.jsx_extraction_widget:
                self._create_jsx_extraction_widget()
            self.jsx_extraction_widget.setVisible(True)
        else:
            raise ValueError(f"Unknown mode: {mode_key}")
        
        self.current_mode = mode_key
    
    def _create_format_conversion_widget(self) -> None:
        """Create and embed Format Conversion tool widget."""
        # Create TextToJsonDock widget (without window decorations)
        self.format_conversion_widget = TextToJsonDock(self)
        
        # Extract the content widget from the dock
        content_widget = self.format_conversion_widget.widget()
        
        # Add to our container
        self.tool_layout.addWidget(content_widget)
    
    def _create_jsx_extraction_widget(self) -> None:
        """Create and embed JSX Extraction tool widget."""
        # Create AdvancedExtractorDock widget (without window decorations)
        self.jsx_extraction_widget = AdvancedExtractorDock(self)
        
        # Extract the content widget from the dock
        content_widget = self.jsx_extraction_widget.widget()
        
        # Add to our container
        self.tool_layout.addWidget(content_widget)
