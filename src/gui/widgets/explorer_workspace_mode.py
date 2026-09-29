"""Presentation-only mode controls for the shared file/search workspace."""

# pylint: disable=no-name-in-module  # Qt extension types

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QButtonGroup, QLabel, QStyle

from src.i18n.translator import tr


class ExplorerWorkspaceMode(QGroupBox):
    """One selector and bounded status; no second query or result state."""

    mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "QPushButton:checked { background-color: palette(highlight); " "color: palette(highlighted-text); }"
        )
        layout = QVBoxLayout(self)
        buttons = QVBoxLayout()
        self.group = QButtonGroup(self)
        self.buttons = {}
        for mode, icon in (
            ("compact", QStyle.SP_FileDialogContentsView),
            ("advanced", QStyle.SP_FileDialogDetailedView),
        ):
            button = QPushButton()
            button.setCheckable(True)
            button.setIcon(self.style().standardIcon(icon))
            button.setMinimumHeight(32)
            self.group.addButton(button)
            self.buttons[mode] = button
            button.clicked.connect(lambda _checked, value=mode: self.mode_changed.emit(value))
            buttons.addWidget(button)
        layout.addLayout(buttons)
        self.summary = QLabel()
        self.summary.setTextFormat(Qt.PlainText)
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.retranslateUi()

    def retranslateUi(self):  # pylint: disable=invalid-name
        self.setTitle(tr("file_explorer.workspace_mode"))
        for mode, button in self.buttons.items():
            text = tr("file_explorer.mode_" + mode)
            button.setText(text)
            button.setToolTip(text)
            button.setAccessibleName(text)

    def set_mode(self, mode):
        self.buttons[mode].setChecked(True)
        self.summary.setVisible(mode == "compact")

    def set_summary(self, text):
        self.summary.setText(text[:1024])
        self.summary.setToolTip(text[:1024])
