"""Read-only interface for bounded information structure analyzers."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.information_structure import (
    document_visual_structures,
    folder_map_from_paths,
    organize_text_hierarchy,
    python_context_graph,
    scientific_reference_graph,
    sqlite_schema_graph,
)


class InformationStructureDock(QWidget):
    """Analyze structures without changing source files."""

    open_in_editor_requested = Signal(str, str)
    MAX_OUTPUT_CHARS = 2_000_000

    MODES = (
        ("folder", "Folder map from File Explorer"),
        ("sqlite", "SQLite schema graph"),
        ("python", "Python context and function graph"),
        ("text", "Loose text hierarchy"),
        ("references", "Scientific reference graph"),
        ("document", "Document visual structures"),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InformationStructureDock")
        self._folder_root = ""
        self._folder_paths: list[str] = []
        self._build_ui()
        self._mode_changed()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Analysis:"))
        self.mode_combo = QComboBox()
        for mode_id, label in self.MODES:
            self.mode_combo.addItem(label, mode_id)
        self.mode_combo.currentIndexChanged.connect(self._mode_changed)
        mode_row.addWidget(self.mode_combo, 1)
        layout.addLayout(mode_row)

        path_row = QHBoxLayout()
        self.path_label = QLabel("Source:")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select a source file")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse)
        path_row.addWidget(self.path_label)
        path_row.addWidget(self.path_input, 1)
        path_row.addWidget(self.browse_button)
        layout.addLayout(path_row)

        identifier_row = QHBoxLayout()
        self.identifier_label = QLabel("Module identifier:")
        self.identifier_input = QLineEdit()
        self.identifier_input.setPlaceholderText("Optional stable identifier; defaults to filename")
        identifier_row.addWidget(self.identifier_label)
        identifier_row.addWidget(self.identifier_input, 1)
        layout.addLayout(identifier_row)

        self.input_label = QLabel("Input text:")
        layout.addWidget(self.input_label)
        self.input_edit = QPlainTextEdit()
        self.input_edit.setPlaceholderText("Paste text, Python source, article JSON, or nested JSON here")
        layout.addWidget(self.input_edit, 2)

        actions = QHBoxLayout()
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.analyze)
        self.open_editor_button = QPushButton("Open JSON in Clarify Editor")
        self.open_editor_button.clicked.connect(self._open_in_editor)
        self.open_editor_button.setEnabled(False)
        actions.addWidget(self.analyze_button)
        actions.addStretch()
        actions.addWidget(self.open_editor_button)
        layout.addLayout(actions)

        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText("Analysis output")
        self.output_edit.document().setMaximumBlockCount(50_000)
        layout.addWidget(self.output_edit, 3)

    def _mode(self) -> str:
        return self.mode_combo.currentData()

    def _mode_changed(self) -> None:
        mode = self._mode()
        uses_path = mode in {"folder", "sqlite", "python"}
        self.path_label.setVisible(uses_path)
        self.path_input.setVisible(uses_path)
        self.browse_button.setVisible(mode in {"sqlite", "python"})
        self.identifier_label.setVisible(mode == "python")
        self.identifier_input.setVisible(mode == "python")
        self.input_label.setVisible(mode not in {"folder", "sqlite"})
        self.input_edit.setVisible(mode not in {"folder", "sqlite"})
        if mode == "folder":
            self.path_input.setPlaceholderText("Use File Explorer > Folder map from results")
        elif mode == "sqlite":
            self.path_input.setPlaceholderText("Select a read-only SQLite database")
        elif mode == "python":
            self.path_input.setPlaceholderText("Optional .py source file")

    def _browse(self) -> None:
        if self._mode() == "sqlite":
            selected, _ = QFileDialog.getOpenFileName(self, "Open SQLite database", "", "SQLite (*.db *.sqlite *.sqlite3)")
        else:
            selected, _ = QFileDialog.getOpenFileName(self, "Open Python source", "", "Python (*.py);;All files (*)")
        if selected:
            self.path_input.setText(selected)

    def prepare_folder_map(self, root: str, paths: list[str]) -> None:
        """Receive an existing File Explorer result set without rescanning."""
        self._folder_root = root
        self._folder_paths = list(paths)
        self.mode_combo.setCurrentIndex(self.mode_combo.findData("folder"))
        self.path_input.setText(f"{root} ({len(paths)} collected paths)")
        self.analyze()

    def _source_text(self) -> str:
        path = self.path_input.text().strip()
        if self._mode() == "python" and path:
            source_path = Path(path).expanduser()
            if source_path.stat().st_size > 2_000_000:
                raise ValueError("Python source exceeds 2,000,000 bytes")
            return source_path.read_text(encoding="utf-8")
        return self.input_edit.toPlainText()

    def analyze(self) -> None:
        """Run the selected analyzer synchronously over bounded local input."""
        try:
            mode = self._mode()
            if mode == "folder":
                if not self._folder_root or not self._folder_paths:
                    raise ValueError("Open this mode from File Explorer results")
                result = folder_map_from_paths(self._folder_root, self._folder_paths)
            elif mode == "sqlite":
                result = sqlite_schema_graph(self.path_input.text().strip())
            elif mode == "python":
                module_name = self.identifier_input.text().strip()
                if not module_name:
                    module_name = Path(self.path_input.text().strip()).stem if self.path_input.text().strip() else "module"
                result = python_context_graph(self._source_text(), module_name)
            elif mode == "text":
                result = organize_text_hierarchy(self._source_text())
            elif mode == "references":
                source = self._source_text()
                try:
                    parsed = json.loads(source)
                    if not isinstance(parsed, dict) or not all(isinstance(value, str) for value in parsed.values()):
                        raise ValueError
                    articles = parsed
                except (json.JSONDecodeError, ValueError):
                    articles = {"document": source}
                result = scientific_reference_graph(articles)
            else:
                source = self._source_text()
                try:
                    data = json.loads(source)
                except json.JSONDecodeError:
                    data = organize_text_hierarchy(source)
                result = document_visual_structures(data)
            rendered = json.dumps(result, ensure_ascii=False, indent=2)
            if len(rendered) > self.MAX_OUTPUT_CHARS:
                raise ValueError(f"Output exceeds {self.MAX_OUTPUT_CHARS:,} characters")
            self.output_edit.setPlainText(rendered)
            self.open_editor_button.setEnabled(True)
        except (OSError, UnicodeError, ValueError, SyntaxError) as exc:
            self.open_editor_button.setEnabled(False)
            QMessageBox.warning(self, "Analysis unavailable", str(exc))

    def _open_in_editor(self) -> None:
        content = self.output_edit.toPlainText()
        if content:
            self.open_in_editor_requested.emit(content, "information-structure.json")
