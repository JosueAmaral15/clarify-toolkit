"""
Base classes for Clarify dock widgets.

Provides reusable components and patterns for creating tool docks.
"""

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QCheckBox, QMessageBox,
    QFileDialog, QSpinBox, QComboBox
)
from PySide6.QtGui import QIcon
from typing import Optional, Callable, List
import os
import re


def parse_extensions_to_globs(extensions_text: str) -> List[str]:
    """
    Parse extension filter text into glob patterns (v2.9.0).
    
    Args:
        extensions_text: Comma or semicolon separated extensions (e.g., ".py,.js,.tsx")
    
    Returns:
        List of glob patterns (e.g., ["*.py", "*.js", "*.tsx"])
    
    Examples:
        >>> parse_extensions_to_globs(".py,.js")
        ['*.py', '*.js']
        >>> parse_extensions_to_globs("py,js,tsx")
        ['*.py', '*.js', '*.tsx']
        >>> parse_extensions_to_globs("")
        []
    """
    if not extensions_text or not extensions_text.strip():
        return []
    
    extensions = [ext.strip() for ext in re.split(r"[;,]", extensions_text) if ext.strip()]
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    return [f"*{ext}" for ext in extensions]


class BaseDock(QDockWidget):
    """Base class for all tool docks with common functionality."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Override to setup UI components."""
        pass
    
    def _connect_signals(self):
        """Override to connect signals."""
        pass
    
    def show_error(self, title: str, message: str) -> None:
        """Show error message dialog."""
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title: str, message: str) -> None:
        """Show information message dialog."""
        QMessageBox.information(self, title, message)
    
    def show_warning(self, title: str, message: str) -> None:
        """Show warning message dialog."""
        QMessageBox.warning(self, title, message)


class FileInputMixin:
    """Mixin for file/directory input with browse button."""
    
    def create_file_input(
        self,
        label_text: str,
        placeholder: str = "",
        with_is_file_checkbox: bool = True
    ) -> tuple[QLabel, QLineEdit, QPushButton, Optional[QCheckBox]]:
        """
        Create file input widgets.
        
        Returns:
            tuple: (label, line_edit, browse_button, is_file_checkbox)
        """
        label = QLabel(label_text)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setMaximumWidth(100)
        
        is_file_chk = None
        if with_is_file_checkbox:
            is_file_chk = QCheckBox("Is file")
        
        return label, line_edit, browse_btn, is_file_chk
    
    def create_extension_filter(
        self,
        default_extensions: str = ".py,.js,.tsx,.jsx,.ts,.md"
    ) -> tuple[QLabel, QLineEdit]:
        """
        Create extension filter widgets (v2.9.0).
        
        Args:
            default_extensions: Default comma-separated extensions
        
        Returns:
            tuple: (label, line_edit)
        """
        label = QLabel("Extensions:")
        line_edit = QLineEdit(default_extensions)
        line_edit.setPlaceholderText("e.g., .py,.js,.tsx (leave empty for all)")
        line_edit.setToolTip(
            "Filter files by extensions. Examples:\n"
            "  .py          - Only Python files\n"
            "  .jsx,.tsx    - React files\n"
            "  .js,.ts      - JavaScript/TypeScript\n"
            "Leave empty to include all file types"
        )
        return label, line_edit
    
    def browse_file_or_directory(
        self,
        line_edit: QLineEdit,
        is_file: bool,
        file_filter: str = "All files (*)",
        title: str = "Select file or directory"
    ) -> None:
        """Browse for file or directory and set line edit."""
        if is_file:
            path, _ = QFileDialog.getOpenFileName(self, title, "", file_filter)
        else:
            path = QFileDialog.getExistingDirectory(self, title)
        
        if path:
            line_edit.setText(path)


class ProcessorWorkerBase(QThread):
    """Base class for background processing workers."""
    
    progress = Signal(str)  # Progress message
    finished_ok = Signal(object)  # Result data
    failed = Signal(str)  # Error message
    
    def __init__(self):
        super().__init__()
        self.interrupt_requested = False
    
    def request_interrupt(self) -> None:
        """Request worker to stop processing."""
        self.interrupt_requested = True
    
    def emit_progress(self, message: str) -> None:
        """Emit progress message."""
        self.progress.emit(message)
    
    def emit_error(self, error: str) -> None:
        """Emit error and finish."""
        self.failed.emit(error)
    
    def emit_success(self, result: any) -> None:
        """Emit success with result."""
        self.finished_ok.emit(result)
    
    def check_interrupt(self) -> bool:
        """Check if interrupt was requested."""
        return self.interrupt_requested


class ResultsOutputMixin:
    """Mixin for results output panel with search functionality."""
    
    def create_results_panel(self, label_text: str = "Results:") -> tuple[QLabel, QTextEdit]:
        """
        Create results output panel with search bar.
        
        Returns:
            tuple: (label, text_edit)
        """
        label = QLabel(label_text)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Add search shortcut (Ctrl+F)
        from PySide6.QtGui import QShortcut, QKeySequence
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), text_edit)
        search_shortcut.activated.connect(lambda: self._show_search_dialog(text_edit))
        
        return label, text_edit
    
    def _show_search_dialog(self, text_edit: QTextEdit) -> None:
        """Show search dialog for results panel."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
        
        dialog = QDialog(text_edit)
        dialog.setWindowTitle("Search in Results")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Search input
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Enter search term...")
        search_layout.addWidget(QLabel("Find:"))
        search_layout.addWidget(search_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_find_next = QPushButton("Find Next")
        btn_find_prev = QPushButton("Find Previous")
        btn_close = QPushButton("Close")
        
        btn_layout.addWidget(btn_find_next)
        btn_layout.addWidget(btn_find_prev)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(search_layout)
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        
        # Connect signals
        def find_next():
            term = search_input.text()
            if term:
                text_edit.find(term)
        
        def find_prev():
            term = search_input.text()
            if term:
                from PySide6.QtGui import QTextDocument
                text_edit.find(term, QTextDocument.FindBackward)
        
        btn_find_next.clicked.connect(find_next)
        btn_find_prev.clicked.connect(find_prev)
        btn_close.clicked.connect(dialog.close)
        search_input.returnPressed.connect(find_next)
        
        dialog.exec()
    
    def append_result(self, text_edit: QTextEdit, message: str) -> None:
        """Append message to results."""
        text_edit.append(message)
    
    def clear_results(self, text_edit: QTextEdit) -> None:
        """Clear results."""
        text_edit.clear()


class ActionButtonsMixin:
    """Mixin for common action buttons."""
    
    def create_action_buttons(
        self,
        buttons: List[tuple]  # [(text, callback), ...]
    ) -> QHBoxLayout:
        """
        Create horizontal layout with action buttons.
        
        Args:
            buttons: List of (button_text, callback_function) tuples
        
        Returns:
            QHBoxLayout with buttons
        """
        layout = QHBoxLayout()
        
        for text, callback in buttons:
            btn = QPushButton(text)
            if callback:
                btn.clicked.connect(callback)
            layout.addWidget(btn)
            
            # Store reference for later access
            attr_name = f"btn_{text.lower().replace(' ', '_')}"
            setattr(self, attr_name, btn)
        
        return layout


class OptionsGroupMixin:
    """Mixin for creating option groups."""
    
    def create_checkbox_group(
        self,
        options: List[tuple]  # [(text, default_checked, tooltip), ...]
    ) -> List[QCheckBox]:
        """
        Create group of checkboxes.
        
        Args:
            options: List of (text, default_checked, tooltip) tuples
        
        Returns:
            List of QCheckBox widgets
        """
        checkboxes = []
        
        for text, default, tooltip in options:
            chk = QCheckBox(text)
            chk.setChecked(default)
            if tooltip:
                chk.setToolTip(tooltip)
            checkboxes.append(chk)
        
        return checkboxes
    
    def create_spinbox_input(
        self,
        label_text: str,
        min_val: int,
        max_val: int,
        default: int,
        step: int = 1
    ) -> tuple[QLabel, QSpinBox]:
        """
        Create labeled spinbox.
        
        Returns:
            tuple: (label, spinbox)
        """
        label = QLabel(label_text)
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default)
        spinbox.setSingleStep(step)
        return label, spinbox


class ValidationMixin:
    """Mixin for input validation."""
    
    def validate_file_path(self, path: str, must_exist: bool = True) -> tuple:
        """
        Validate file path.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not path.strip():
            return False, "Path is empty"
        
        if must_exist and not os.path.exists(path):
            return False, f"Path does not exist: {path}"
        
        return True, ""
    
    def validate_not_empty(self, text: str, field_name: str) -> tuple:
        """
        Validate text is not empty.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not text.strip():
            return False, f"{field_name} cannot be empty"
        return True, ""
    
    def validate_file_writable(self, path: str) -> tuple:
        """
        Validate file can be written.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create directory: {str(e)}"
        
        if os.path.exists(path) and not os.access(path, os.W_OK):
            return False, f"File is not writable: {path}"
        
        return True, ""


# Convenience base class combining common mixins
class StandardToolDock(
    BaseDock,
    FileInputMixin,
    ResultsOutputMixin,
    ActionButtonsMixin,
    OptionsGroupMixin,
    ValidationMixin
):
    """
    Standard tool dock with all common mixins.
    
    Automatically enables Enter key execution on input fields when
    _execute_action method is defined.
    """
    
    def _setup_enter_key_execution(self, *line_edits: QLineEdit) -> None:
        """
        Setup Enter key to trigger execution on given line edits.
        
        Args:
            *line_edits: QLineEdit widgets to enable Enter key on
        """
        if not hasattr(self, '_execute_action'):
            return
        
        for line_edit in line_edits:
            line_edit.returnPressed.connect(self._execute_action)
    
    def _execute_action(self) -> None:
        """
        Override this method to define the action triggered by Enter key.
        This should typically call your main processing method (e.g., _process).
        """
        pass


class StandardToolDock(BaseDock, FileInputMixin, ResultsOutputMixin, ActionButtonsMixin):
    """
    Standard tool dock with all common functionality.
    
    Inherits from all mixins for maximum reusability.
    """
    pass
