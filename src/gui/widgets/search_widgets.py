"""
Reusable search/replace widgets for File Explorer integration.

Extracted from search_replace_panel.py to enable component reuse.
Part of v2.9.116 integration: Search/Replace → File Explorer.

Author: Josué Amaral
Date: 2025/12/25
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTextEdit,
    QCheckBox,
    QPushButton,
    QLabel,
    QComboBox,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from src.i18n.translator import tr


class FileNameQueryPanel(QWidget):
    """
    Widget for file name pattern input with optional regex support.

    Signals:
        pattern_changed: Emitted when pattern text changes
        clear_requested: Emitted when clear button is clicked
    """

    pattern_changed = Signal(str)
    clear_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label
        label = QLabel(tr("search.lbl_filename"))
        label.setToolTip(tr("search.tooltip_filename"))
        layout.addWidget(label)

        # Pattern input
        self.ed_pattern = QLineEdit()
        self.ed_pattern.setPlaceholderText(tr("search.placeholder_filename"))
        self.ed_pattern.textChanged.connect(self.pattern_changed.emit)
        layout.addWidget(self.ed_pattern, stretch=1)

        self.chk_filename_regex = QCheckBox(tr("search.chk_filename_regex", "Regex"))
        self.chk_filename_regex.setToolTip(
            tr(
                "search.tooltip_filename_regex",
                "Treat the filename pattern as a regular expression instead of a wildcard glob.",
            )
        )
        self.chk_filename_regex.toggled.connect(lambda _: self.pattern_changed.emit(self.get_pattern()))
        layout.addWidget(self.chk_filename_regex)

        # Clear button
        btn_clear = QPushButton(tr("search.btn_clear_filename"))
        btn_clear.setToolTip(tr("search.tooltip_clear_filename"))
        btn_clear.clicked.connect(self._on_clear)
        layout.addWidget(btn_clear)

    def _on_clear(self):
        self.ed_pattern.clear()
        self.clear_requested.emit()

    def get_pattern(self) -> str:
        """Get current filename pattern."""
        return self.ed_pattern.text().strip()

    def set_pattern(self, pattern: str):
        """Set filename pattern."""
        self.ed_pattern.setText(pattern)

    def get_use_regex(self) -> bool:
        """Return True when filename pattern should be treated as regex."""
        return self.chk_filename_regex.isChecked()

    def set_use_regex(self, enabled: bool):
        """Set filename regex mode."""
        self.chk_filename_regex.setChecked(enabled)

    def clear(self):
        """Clear filename pattern (v2.9.117)."""
        self.ed_pattern.clear()


class ContentQueryPanel(QWidget):
    """
    Multi-line text editor for content search queries.

    Signals:
        query_changed: Emitted when query text changes
    """

    query_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label
        label = QLabel(tr("search.lbl_content"))
        label.setToolTip(tr("search.tooltip_content"))
        layout.addWidget(label)

        # Text editor
        self.ed_query = QTextEdit()
        self.ed_query.setPlaceholderText(tr("search.placeholder_content"))
        self.ed_query.setMaximumHeight(80)
        self.ed_query.textChanged.connect(lambda: self.query_changed.emit(self.get_query()))
        layout.addWidget(self.ed_query)

    def get_query(self) -> str:
        """Get current search query."""
        return self.ed_query.toPlainText()

    def set_query(self, query: str):
        """Set search query."""
        self.ed_query.setPlainText(query)

    def set_font(self, font: QFont):
        """Set monospaced font for editor."""
        self.ed_query.setFont(font)

    def clear(self):
        """Clear search query (v2.9.117)."""
        self.ed_query.clear()


class SearchOptionsPanel(QWidget):
    """
    Checkboxes for content search options (case-sensitive, whole-word, regex).

    Signals:
        options_changed: Emitted when any option changes
    """

    options_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_options = QLabel(tr("search.lbl_options"))
        matching_row = QHBoxLayout()
        layout.addLayout(matching_row)
        matching_row.addWidget(self.lbl_options)

        # Case-sensitive
        self.chk_case = QCheckBox(tr("search.chk_case_sensitive"))
        self.chk_case.setToolTip(tr("search.tooltip_case_sensitive"))
        self.chk_case.toggled.connect(self._emit_options)
        matching_row.addWidget(self.chk_case)

        # Whole word
        self.chk_word = QCheckBox(tr("search.chk_whole_word"))
        self.chk_word.setToolTip(tr("search.tooltip_whole_word"))
        self.chk_word.toggled.connect(self._emit_options)
        matching_row.addWidget(self.chk_word)

        # Regex
        self.chk_regex = QCheckBox(tr("search.chk_regex"))
        self.chk_regex.setToolTip(tr("search.tooltip_regex"))
        self.chk_regex.toggled.connect(self._emit_options)
        matching_row.addWidget(self.chk_regex)
        matching_row.addStretch()

        self.chk_multi_query = QCheckBox(tr("search.chk_multi_query", "Multi-query"))
        self.chk_multi_query.setToolTip(tr("search.tooltip_independent_queries"))
        self.chk_cross_line = QCheckBox(tr("search.chk_cross_line", "Cross-line Block"))
        self.chk_cross_line.setToolTip(tr("search.tooltip_cross_line"))
        self.chk_multi_query.toggled.connect(self._on_multi_query_toggled)
        self.chk_cross_line.toggled.connect(self._on_cross_line_toggled)
        layout.addWidget(self.chk_multi_query, 0, Qt.AlignLeft)
        layout.addWidget(self.chk_cross_line, 0, Qt.AlignLeft)
        scope_row = QHBoxLayout()
        layout.addLayout(scope_row)

        scope_tooltip = tr(
            "search.tooltip_content_scope",
            "Text/ASCII (default): search decoded text files.\n"
            "Binary: scan raw bytes in 64 KiB chunks.\n"
            "Both: search both types.\n"
            "Binary previews are limited; Replace remains text-only.",
        )
        self.lbl_content_scope = QLabel(tr("search.lbl_content_scope", "Content type:"))
        self.lbl_content_scope.setToolTip(scope_tooltip)
        scope_row.addWidget(self.lbl_content_scope)

        self.combo_content_scope = QComboBox()
        self.combo_content_scope.addItem(tr("search.content_scope_text", "Text/ASCII"), "text")
        self.combo_content_scope.addItem(tr("search.content_scope_binary", "Binary"), "binary")
        self.combo_content_scope.addItem(tr("search.content_scope_both", "Both"), "both")
        self.combo_content_scope.setToolTip(scope_tooltip)
        self.combo_content_scope.currentIndexChanged.connect(lambda _: self._emit_options())
        scope_row.addWidget(self.combo_content_scope)

        scope_row.addStretch()

    def _on_multi_query_toggled(self, enabled):
        if enabled:
            self.chk_cross_line.setChecked(False)
        self._emit_options()

    def _on_cross_line_toggled(self, enabled):
        if enabled:
            self.chk_multi_query.setChecked(False)
        self._emit_options()

    def _emit_options(self):
        self.options_changed.emit(self.get_options())

    def get_options(self) -> dict:
        """Get current search options."""
        return {
            "case_sensitive": self.chk_case.isChecked(),
            "whole_word": self.chk_word.isChecked(),
            "regex": self.chk_regex.isChecked(),
            "multi_query": self.chk_multi_query.isChecked(),
            "cross_line": self.chk_cross_line.isChecked(),
            "content_scope": self.combo_content_scope.currentData() or "text",
        }

    def set_options(self, options: dict):
        """Set search options."""
        self.chk_case.setChecked(options.get("case_sensitive", False))
        self.chk_word.setChecked(options.get("whole_word", False))
        self.chk_regex.setChecked(options.get("regex", False))
        self.chk_multi_query.setChecked(options.get("multi_query", False))
        self.chk_cross_line.setChecked(options.get("cross_line", False))
        content_scope = options.get("content_scope", "text")
        index = self.combo_content_scope.findData(content_scope)
        self.combo_content_scope.setCurrentIndex(index if index >= 0 else 0)

    def retranslateUi(self):  # pylint: disable=invalid-name
        """Refresh labels and tooltips while preserving the selected scope."""
        self.lbl_options.setText(tr("search.lbl_options"))
        self.chk_case.setText(tr("search.chk_case_sensitive"))
        self.chk_case.setToolTip(tr("search.tooltip_case_sensitive"))
        self.chk_word.setText(tr("search.chk_whole_word"))
        self.chk_word.setToolTip(tr("search.tooltip_whole_word"))
        self.chk_regex.setText(tr("search.chk_regex"))
        self.chk_regex.setToolTip(tr("search.tooltip_regex"))
        self.chk_multi_query.setText(tr("search.chk_multi_query", "Multi-query"))
        self.chk_multi_query.setToolTip(tr("search.tooltip_independent_queries"))
        self.chk_cross_line.setText(tr("search.chk_cross_line", "Cross-line Block"))
        self.chk_cross_line.setToolTip(tr("search.tooltip_cross_line"))

        self.lbl_content_scope.setText(tr("search.lbl_content_scope", "Content type:"))
        scope_tooltip = tr(
            "search.tooltip_content_scope",
            "Text/ASCII (default): search decoded text files.\n"
            "Binary: scan raw bytes in 64 KiB chunks.\n"
            "Both: search both types.\n"
            "Binary previews are limited; Replace remains text-only.",
        )
        self.lbl_content_scope.setToolTip(scope_tooltip)
        self.combo_content_scope.setToolTip(scope_tooltip)
        self.combo_content_scope.setItemText(0, tr("search.content_scope_text", "Text/ASCII"))
        self.combo_content_scope.setItemText(1, tr("search.content_scope_binary", "Binary"))
        self.combo_content_scope.setItemText(2, tr("search.content_scope_both", "Both"))


class ReplacePanel(QWidget):
    """
    Panel with replace text editor and action buttons.

    Signals:
        replace_first_requested: Emitted when "Replace First" is clicked
        replace_all_requested: Emitted when "Replace All" is clicked
    """

    replace_first_requested = Signal()
    replace_all_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label
        self.lbl_replace = QLabel(tr("search.lbl_replace"))
        self.lbl_replace.setToolTip(tr("search.tooltip_replace"))
        layout.addWidget(self.lbl_replace)

        # Text editor
        self.ed_replace = QTextEdit()
        self.ed_replace.setPlaceholderText(tr("search.placeholder_replace"))
        self.ed_replace.setMaximumHeight(80)
        layout.addWidget(self.ed_replace)

        # Options row
        options_layout = QHBoxLayout()

        self.chk_preserve_case = QCheckBox(tr("search.chk_preserve_case"))
        self.chk_preserve_case.setToolTip(tr("search.tooltip_preserve_case"))
        options_layout.addWidget(self.chk_preserve_case)

        options_layout.addStretch()

        # Action buttons
        self.btn_replace_first = QPushButton(tr("search.btn_replace_first"))
        self.btn_replace_first.setToolTip(tr("search.tooltip_replace_first"))
        self.btn_replace_first.clicked.connect(self.replace_first_requested.emit)
        options_layout.addWidget(self.btn_replace_first)

        self.btn_replace_all = QPushButton(tr("search.btn_replace_all"))
        self.btn_replace_all.setToolTip(tr("search.tooltip_replace_all"))
        self.btn_replace_all.clicked.connect(self.replace_all_requested.emit)
        options_layout.addWidget(self.btn_replace_all)

        layout.addLayout(options_layout)

    def retranslateUi(self):  # pylint: disable=invalid-name
        """Refresh labels without replacing the shared widget state."""
        self.lbl_replace.setText(tr("search.lbl_replace"))
        self.lbl_replace.setToolTip(tr("search.tooltip_replace"))
        self.ed_replace.setPlaceholderText(tr("search.placeholder_replace"))
        self.chk_preserve_case.setText(tr("search.chk_preserve_case"))
        self.chk_preserve_case.setToolTip(tr("search.tooltip_preserve_case"))
        self.btn_replace_first.setText(tr("search.btn_replace_first"))
        self.btn_replace_first.setToolTip(tr("search.tooltip_replace_first"))
        self.btn_replace_all.setText(tr("search.btn_replace_all"))
        self.btn_replace_all.setToolTip(tr("search.tooltip_replace_all"))

    def get_replacement(self) -> str:
        """Get replacement text."""
        return self.ed_replace.toPlainText()

    def set_replacement(self, text: str):
        """Set replacement text."""
        self.ed_replace.setPlainText(text)

    def get_preserve_case(self) -> bool:
        """Check if preserve case is enabled."""
        return self.chk_preserve_case.isChecked()

    def set_preserve_case(self, enabled: bool):
        """Set preserve case option."""
        self.chk_preserve_case.setChecked(enabled)

    def set_font(self, font: QFont):
        """Set monospaced font for editor."""
        self.ed_replace.setFont(font)

    def set_buttons_enabled(self, enabled: bool):
        """Enable/disable action buttons."""
        self.btn_replace_first.setEnabled(enabled)
        self.btn_replace_all.setEnabled(enabled)


class ConditionsGrid(QWidget):
    """
    Dynamic grid for advanced search conditions with AND/OR logic.

    Signals:
        conditions_changed: Emitted when conditions are modified
    """

    conditions_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.condition_rows = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header row
        header_layout = QHBoxLayout()

        # Logic operator
        label_logic = QLabel(tr("search.lbl_logic"))
        header_layout.addWidget(label_logic)

        self.combo_logic = QComboBox()
        self.combo_logic.addItems(["AND", "OR"])
        self.combo_logic.setToolTip(tr("search.tooltip_logic"))
        self.combo_logic.currentTextChanged.connect(self._emit_conditions)
        header_layout.addWidget(self.combo_logic)

        header_layout.addStretch()

        # Buttons
        btn_add = QPushButton(tr("search.btn_add_condition"))
        btn_add.setToolTip(tr("search.tooltip_add_condition"))
        btn_add.clicked.connect(self.add_condition_row)
        header_layout.addWidget(btn_add)

        btn_clear = QPushButton(tr("search.btn_clear_all"))
        btn_clear.setToolTip(tr("search.tooltip_clear_all"))
        btn_clear.clicked.connect(self.clear_conditions)
        header_layout.addWidget(btn_clear)

        layout.addLayout(header_layout)

        # Conditions container (for dynamic rows)
        self.conditions_container = QWidget()
        self.conditions_layout = QVBoxLayout(self.conditions_container)
        self.conditions_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.conditions_container)

        # Add initial row
        self.add_condition_row()

    def add_condition_row(self):
        """Add a new condition row."""
        row_widget = QWidget()
        layout = QVBoxLayout(row_widget)
        layout.setContentsMargins(0, 2, 0, 2)
        row_layout = QHBoxLayout()
        layout.addLayout(row_layout)

        # Field selector (with technical names as user data)
        combo_field = QComboBox()
        combo_field.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        combo_field.setMinimumContentsLength(8)
        # Add items with display text (translated) and user data (technical field name)
        combo_field.addItem(tr("search.field_filename"), "filename")
        combo_field.addItem(tr("search.field_path"), "path")
        combo_field.addItem(tr("search.field_ext"), "ext")
        combo_field.addItem(tr("search.field_size"), "size")
        combo_field.addItem(tr("search.field_mtime"), "mtime")
        combo_field.addItem(tr("search.field_content"), "content")
        combo_field.setToolTip(tr("search.tooltip_field"))
        row_layout.addWidget(combo_field)

        # Operator selector
        combo_operator = QComboBox()
        combo_operator.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        combo_operator.setMinimumContentsLength(10)
        from ...core.filters import OPERATOR_ALIASES

        for label in ("equals", "not equals", "contains", "not contains",
                      "starts with", "ends with",
                      "greater than", "less than", "greater than or equal",
                      "less than or equal", "regex"):
            combo_operator.addItem(label, OPERATOR_ALIASES.get(label, label))
        combo_operator.setToolTip(tr("search.tooltip_operator"))
        row_layout.addWidget(combo_operator)

        # Value input
        line_value = QLineEdit()
        from ...core.filters import MAX_CONDITION_TEXT_BYTES
        line_value.setMaxLength(MAX_CONDITION_TEXT_BYTES)
        line_value.setMinimumWidth(40)
        line_value.setPlaceholderText(tr("search.placeholder_value"))
        line_value.setToolTip(tr("search.tooltip_value"))
        row_layout.addWidget(line_value, 1)  # Stretch to fill space

        options_layout = QHBoxLayout()
        layout.addLayout(options_layout)

        # Options for content field
        chk_case = QCheckBox(tr("search.chk_case"))
        chk_case.setToolTip(tr("search.tooltip_case"))
        chk_case.setEnabled(True)  # Enable by default, will be managed by field selection
        options_layout.addWidget(chk_case)

        chk_regex = QCheckBox(tr("search.chk_regex"))
        chk_regex.setToolTip(tr("search.tooltip_regex_option"))
        chk_regex.setEnabled(True)  # Enable by default, will be managed by field selection
        options_layout.addWidget(chk_regex)

        chk_word = QCheckBox(tr("search.chk_whole_word"))
        chk_word.setToolTip(tr("search.tooltip_condition_word"))
        options_layout.addWidget(chk_word)
        options_layout.addStretch()

        scope_layout = QHBoxLayout()
        layout.addLayout(scope_layout)
        combo_scope = QComboBox()
        combo_scope.setToolTip(tr("search.tooltip_condition_scope"))
        for value, label in (("", "No scope"), ("brackets", "[]"), ("braces", "{}"),
                             ("parentheses", "()"), ("custom", "Custom"), ("tag", "Any tag"),
                             ("specific-tag", "Specific tag"), ("hierarchical", "Hierarchical")):
            combo_scope.addItem(tr(f"search.condition_scope_{value or 'none'}", label), value)
        scope_layout.addWidget(combo_scope)
        line_scope = QLineEdit()
        line_scope.setMaxLength(MAX_CONDITION_TEXT_BYTES)
        line_scope.setPlaceholderText(tr("search_replace.placeholder_scope_value"))
        line_scope.setToolTip(tr("search.tooltip_condition_parameter"))
        scope_layout.addWidget(line_scope, 1)

        # Delete button
        btn_delete = QPushButton(tr("search.btn_delete"))
        btn_delete.setToolTip(tr("search.tooltip_delete"))
        btn_delete.setMaximumWidth(40)
        btn_delete.clicked.connect(lambda: self._remove_condition_row(row_widget))
        row_layout.addWidget(btn_delete)

        # Enable/disable options based on field type
        def on_field_changed(*_args):
            field_data = combo_field.currentData()
            # Enable Case and Regex for text fields: filename, path, ext, content
            is_text_field = field_data in ("filename", "path", "ext", "content")
            chk_case.setEnabled(is_text_field)
            chk_regex.setEnabled(is_text_field)
            chk_word.setEnabled(is_text_field and combo_operator.currentData() in
                                ("contains", "not contains", "regex"))
            combo_scope.setEnabled(field_data == "content")
            line_scope.setEnabled(field_data == "content" and combo_scope.currentData() in
                                  ("custom", "specific-tag", "hierarchical"))

        combo_field.currentIndexChanged.connect(on_field_changed)
        combo_operator.currentIndexChanged.connect(on_field_changed)
        combo_scope.currentIndexChanged.connect(on_field_changed)

        # Set initial state
        on_field_changed(combo_field.currentIndex())

        # Add to layout
        self.conditions_layout.addWidget(row_widget)

        # Store references
        row_data = {
            "widget": row_widget,
            "field": combo_field,
            "operator": combo_operator,
            "value": line_value,
            "case": chk_case,
            "regex": chk_regex,
            "word": chk_word,
            "scope": combo_scope,
            "scope_value": line_scope,
        }
        self.condition_rows.append(row_data)

        # Connect signals to emit changes
        combo_field.currentTextChanged.connect(self._emit_conditions)
        combo_operator.currentTextChanged.connect(self._emit_conditions)
        line_value.textChanged.connect(self._emit_conditions)
        chk_case.stateChanged.connect(self._emit_conditions)
        chk_regex.stateChanged.connect(self._emit_conditions)
        chk_word.stateChanged.connect(self._emit_conditions)
        combo_scope.currentIndexChanged.connect(self._emit_conditions)
        line_scope.textChanged.connect(self._emit_conditions)

    def _remove_condition_row(self, row_widget):
        """Remove a specific condition row."""
        # Find and remove from list
        for i, row_data in enumerate(self.condition_rows):
            if row_data["widget"] == row_widget:
                self.condition_rows.pop(i)
                break

        # Remove widget
        row_widget.deleteLater()
        self._emit_conditions()

    def clear_conditions(self):
        """Remove all condition rows."""
        for row in self.condition_rows:
            row["widget"].deleteLater()
        self.condition_rows.clear()
        self._emit_conditions()

    def _emit_conditions(self):
        conditions = self.get_conditions()
        self.conditions_changed.emit(conditions)

    def get_conditions(self) -> list:
        """Get all conditions as list of dicts."""
        conditions = []
        for row_data in self.condition_rows:
            # Get technical field name from user data (not translated text)
            field_combo = row_data["field"]
            field = field_combo.currentData()  # Get user data (technical name)
            if field is None:  # Fallback to text if no data
                field = field_combo.currentText().lower()

            operator = row_data["operator"].currentData() or row_data["operator"].currentText()
            value = row_data["value"].text().strip()

            # Skip empty conditions
            if not value:
                continue

            condition = {
                "field": field,  # Now uses technical name ("size", not "Tamanho")
                "operator": operator,
                "value": value,
                "case_sensitive": row_data["case"].isChecked(),
                "regex": row_data["regex"].isChecked(),
                "whole_word": row_data["word"].isChecked(),
                "scope_type": row_data["scope"].currentData() if field == "content" else "",
                "scope_value": row_data["scope_value"].text() if field == "content" else "",
            }
            conditions.append(condition)

        return conditions

    def set_conditions(self, conditions, logic_operator="AND"):
        """Restore validated mappings without emitting partially restored rows."""
        from ...core.filters import Condition, MAX_CONDITIONS

        if not isinstance(conditions, list) or len(conditions) > MAX_CONDITIONS:
            raise ValueError("Condition presets require a list of at most 128 entries")
        if not isinstance(logic_operator, str) or logic_operator.upper() not in {"AND", "OR"}:
            raise ValueError("Condition logic must be AND or OR")
        objects = [Condition.from_mapping(data) for data in conditions]
        blocked = self.blockSignals(True)
        try:
            self.clear_conditions()
            self.combo_logic.setCurrentText(logic_operator.upper())
            for condition in objects:
                self.add_condition_row()
                row = self.condition_rows[-1]
                row["field"].setCurrentIndex(row["field"].findData(condition.field))
                row["operator"].setCurrentIndex(row["operator"].findData(condition.operator))
                row["value"].setText(condition.value)
                row["case"].setChecked(condition.case_sensitive)
                row["regex"].setChecked(condition.use_regex)
                row["word"].setChecked(condition.whole_word)
                scope = "" if condition.scope_type == "none" else condition.scope_type
                row["scope"].setCurrentIndex(row["scope"].findData(scope))
                row["scope_value"].setText(condition.scope_value)
        finally:
            self.blockSignals(blocked)
        self._emit_conditions()

    def get_logic_operator(self) -> str:
        """Get selected logic operator (AND/OR)."""
        return self.combo_logic.currentText()
