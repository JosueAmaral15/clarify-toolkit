"""
Path Entry Widget - v2.9.114

Reusable widget for file/directory path input with browse functionality.
Extracted from ai_processor_dock.py for better modularity.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFileDialog
)
from src.i18n.translator import tr


class PathEntry(QWidget):
    """Widget for a single path entry with browse and remove buttons."""
    
    def __init__(self, path_number, on_remove_callback, parent=None):
        super().__init__(parent)
        self.path_number = path_number
        self.on_remove_callback = on_remove_callback
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        
        # Path label
        self.lbl_path = QLabel(f"Path {path_number}:")
        self.lbl_path.setMinimumWidth(60)
        
        # Path input
        self.ed_path = QLineEdit()
        self.ed_path.setPlaceholderText(tr("path_entry.placeholder"))
        
        # Browse button
        self.btn_browse = QPushButton(tr("path_entry.btn_browse"))
        self.btn_browse.setMaximumWidth(80)
        self.btn_browse.clicked.connect(self._browse)
        
        # Is file checkbox
        self.chk_is_file = QCheckBox("File")
        
        # Remove button (disabled for first path)
        self.btn_remove = QPushButton(tr("path_entry.btn_remove"))
        self.btn_remove.setMaximumWidth(30)
        self.btn_remove.setStyleSheet("QPushButton { color: red; font-weight: bold; }")
        self.btn_remove.clicked.connect(self._remove)
        self.btn_remove.setEnabled(path_number > 1)
        
        layout.addWidget(self.lbl_path)
        layout.addWidget(self.ed_path)
        layout.addWidget(self.btn_browse)
        layout.addWidget(self.chk_is_file)
        layout.addWidget(self.btn_remove)
    
    def _browse(self):
        """Browse for file or directory."""
        if self.chk_is_file.isChecked():
            path, _ = QFileDialog.getOpenFileName(self, "Select File")
        else:
            path = QFileDialog.getExistingDirectory(self, "Select Directory")
        
        if path:
            self.ed_path.setText(path)
    
    def _remove(self):
        """Remove this path entry."""
        if self.on_remove_callback:
            self.on_remove_callback(self)
    
    def get_path(self):
        """Get the path value."""
        return self.ed_path.text().strip()
    
    def is_file(self):
        """Check if marked as file."""
        return self.chk_is_file.isChecked()
