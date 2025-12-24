"""
Converter Selection Dialog

Allows user to choose between JSX Parameter Extractor and Text Format Converter.
Extracted from MainWindow._show_text_to_json() as part of Phase 3.8 refactoring.

Author: Refactoring Phase 3.8
Date: 2024-12-24
Version: v2.9.114
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QButtonGroup, QRadioButton
)


class ConverterSelectionDialog(QDialog):
    """
    Dialog for selecting between JSX and Text converters.
    
    Returns the selected converter type when accepted.
    """
    
    JSX_EXTRACTOR = "jsx"
    TEXT_CONVERTER = "text"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Converter Type")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.selected_converter = None
        self._build_ui()
    
    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("<b>Choose the type of converter:</b>")
        layout.addWidget(title_label)
        
        # Radio buttons
        self.btn_group = QButtonGroup(self)
        
        self.radio_jsx = QRadioButton("JSX Parameter Extractor")
        self.radio_jsx.setToolTip(
            "Extract parameters and attributes from JSX/TSX files.\n"
            "Scans React component files and generates hierarchical JSON."
        )
        self.radio_jsx.setChecked(True)  # Default
        self.btn_group.addButton(self.radio_jsx)
        layout.addWidget(self.radio_jsx)
        
        self.radio_text = QRadioButton("Text Format Converter")
        self.radio_text.setToolTip(
            "Convert text formats to JSON (CSV, YAML, INI, etc.).\n"
            "Paste text and convert to JSON structure."
        )
        self.btn_group.addButton(self.radio_text)
        layout.addWidget(self.radio_text)
        
        # Description labels
        layout.addSpacing(10)
        desc_jsx = QLabel(
            "• <b>JSX Parameter Extractor:</b> For React/JSX/TSX files<br>"
            "  Extract props, attributes, and tag content from components<br>"
            "  Requires file or directory path"
        )
        desc_jsx.setWordWrap(True)
        layout.addWidget(desc_jsx)
        
        layout.addSpacing(5)
        desc_text = QLabel(
            "• <b>Text Format Converter:</b> For text-based formats<br>"
            "  Convert CSV, YAML, INI, TOML, etc. to JSON<br>"
            "  Paste text directly into the converter"
        )
        desc_text.setWordWrap(True)
        layout.addWidget(desc_text)
        
        # Buttons
        layout.addSpacing(10)
        btn_ok = QPushButton("Open")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)
    
    def accept(self):
        """Handle dialog acceptance and store selection."""
        if self.radio_jsx.isChecked():
            self.selected_converter = self.JSX_EXTRACTOR
        else:
            self.selected_converter = self.TEXT_CONVERTER
        super().accept()
    
    def get_selected_converter(self):
        """
        Get the selected converter type.
        
        Returns:
            str: 'jsx' or 'text', or None if dialog was cancelled
        """
        return self.selected_converter
    
    @staticmethod
    def get_converter_choice(parent=None):
        """
        Static method to show dialog and return selection.
        
        Args:
            parent: Parent widget
            
        Returns:
            str: 'jsx', 'text', or None if cancelled
        """
        dialog = ConverterSelectionDialog(parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_selected_converter()
        return None
