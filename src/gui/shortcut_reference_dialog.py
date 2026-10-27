"""Non-blocking reference for shortcuts registered by Clarify."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from collections import defaultdict

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QColor, QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from src.i18n import get_translator, tr
from src.shortcut_manager import RegisteredShortcut, ShortcutManager


class ShortcutReferenceDialog(QDialog):
    """Searchable live view of effective shortcuts for one main window."""

    customize_requested = Signal()

    def __init__(self, owner):
        super().__init__(owner)
        self._owner = owner
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._run_scheduled_refresh)
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setMinimumSize(720, 500)

        layout = QVBoxLayout(self)
        search_layout = QHBoxLayout()
        self.search_label = QLabel(self)
        self.search_box = QLineEdit(self)
        self.search_box.setClearButtonEnabled(True)
        self.search_box.textChanged.connect(self._filter_items)
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_box, 1)
        layout.addLayout(search_layout)

        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(3)
        self.tree.setRootIsDecorated(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setAlternatingRowColors(True)
        layout.addWidget(self.tree, 1)

        button_layout = QHBoxLayout()
        self.customize_button = QPushButton(self)
        self.customize_button.clicked.connect(self.customize_requested)
        self.close_button = QPushButton(self)
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.customize_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        ShortcutManager.events().changed.connect(self.schedule_refresh)
        get_translator().languageChanged.connect(self.retranslate_ui)
        self.retranslate_ui()

    def present(self) -> None:
        """Show and focus the single reusable reference window."""
        self.refresh()
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_box.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def schedule_refresh(self) -> None:
        """Coalesce action rebuilds and customization updates."""
        if not self._refresh_timer.isActive():
            self._refresh_timer.start(0)

    def _run_scheduled_refresh(self) -> None:
        if self.isVisible():
            self.refresh()

    def retranslate_ui(self, _language: str | None = None) -> None:
        """Refresh static chrome and translated action labels at runtime."""
        title = tr("shortcuts.dialog.help_title")
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.search_label.setText(tr("app.lbl_shortcuts_search"))
        self.search_box.setPlaceholderText(tr("shortcuts.dialog.search"))
        self.search_box.setAccessibleName(tr("shortcuts.dialog.search"))
        self.tree.setHeaderLabels(
            (
                tr("shortcuts.dialog.action"),
                tr("shortcuts.dialog.shortcut"),
                tr("shortcuts.dialog.description"),
            )
        )
        self.tree.setAccessibleName(title)
        self.customize_button.setText(tr("shortcuts.dialog.customize"))
        self.customize_button.setAccessibleName(tr("shortcuts.dialog.customize"))
        self.close_button.setText(tr("app.btn_close"))
        self.close_button.setAccessibleName(tr("app.btn_close"))
        self.refresh()

    def refresh(self) -> None:
        """Rebuild from live registered bindings; no parallel shortcut list."""
        bindings = ShortcutManager.get_registered_shortcuts(self._owner)
        conflicts = self._conflicts(bindings)
        expanded = {
            self.tree.topLevelItem(index).data(0, Qt.ItemDataRole.UserRole)
            for index in range(self.tree.topLevelItemCount())
            if self.tree.topLevelItem(index).isExpanded()
        }
        self.tree.clear()

        grouped = defaultdict(list)
        for binding in bindings:
            grouped[binding.category].append(binding)

        for category in sorted(grouped, key=self._category_text):
            category_item = QTreeWidgetItem((self._category_text(category), "", ""))
            category_item.setData(0, Qt.ItemDataRole.UserRole, category)
            category_item.setFirstColumnSpanned(True)
            self.tree.addTopLevelItem(category_item)
            for binding in grouped[category]:
                sequence_text = " / ".join(
                    QKeySequence(sequence).toString(QKeySequence.NativeText) for sequence in binding.sequences
                )
                conflict_names = sorted(conflicts.get(binding.action_name, ()))
                status = ""
                if conflict_names:
                    status = tr("shortcuts.dialog.conflict_title") + ": " + ", ".join(conflict_names)
                item = QTreeWidgetItem((binding.label, sequence_text, status))
                item.setData(0, Qt.ItemDataRole.UserRole, binding.action_name)
                if conflict_names:
                    item.setForeground(2, QColor("#c62828"))
                    item.setToolTip(2, status)
                if not binding.enabled:
                    item.setDisabled(True)
                category_item.addChild(item)
            category_item.setExpanded(category in expanded or not expanded)

        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)
        self._filter_items(self.search_box.text())

    @staticmethod
    def _conflicts(bindings: list[RegisteredShortcut]) -> dict[str, set[str]]:
        users = defaultdict(set)
        for binding in bindings:
            for sequence in binding.sequences:
                normalized = QKeySequence(sequence).toString(QKeySequence.PortableText).casefold()
                if normalized:
                    users[normalized].add(binding.action_name)
        result = defaultdict(set)
        for action_names in users.values():
            if len(action_names) < 2:
                continue
            for action_name in action_names:
                result[action_name].update(action_names - {action_name})
        return result

    @staticmethod
    def _category_text(category: str) -> str:
        key = "shortcuts.category." + category.casefold().replace(" ", "_")
        return tr(key, category)

    def _filter_items(self, text: str) -> None:
        needle = text.strip().casefold()
        for category_index in range(self.tree.topLevelItemCount()):
            category = self.tree.topLevelItem(category_index)
            visible_children = 0
            category_match = needle in category.text(0).casefold()
            for child_index in range(category.childCount()):
                child = category.child(child_index)
                haystack = " ".join(child.text(column) for column in range(self.tree.columnCount())).casefold()
                visible = not needle or category_match or needle in haystack
                child.setHidden(not visible)
                visible_children += int(visible)
            category.setHidden(visible_children == 0)

    def reject(self) -> None:
        """Esc and Close hide the modeless reference without destroying state."""
        self.hide()
