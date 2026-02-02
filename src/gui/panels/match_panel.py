"""
Match list model and panel for displaying search results.
Extracted from app.py (v2.9.114 - Phase 1.2).
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=missing-function-docstring  # Qt method overrides
# pylint: disable=invalid-name  # Qt convention (rowCount)

import os
import sys
from typing import List, Optional

from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListView, QMessageBox
)

from src.i18n.translator import tr


class MatchListModel(QAbstractListModel):
    """
    Simple list model for displaying file paths.
    """
    def __init__(self, items: List[str] = None):
        super().__init__()
        self.items = items or []

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.items[index.row()]
        return None

    def rowCount(self, _parent=QModelIndex()):
        return len(self.items)

    def set_items(self, items: List[str]):
        self.beginResetModel()
        self.items = list(items)
        self.endResetModel()


class MatchPanel(QWidget):
    """
    Shared 'Match results' panel used by both Search/Replace and Insert tabs.
    Features:
    - List view of matched files
    - Count display
    - Refresh button
    - Open in file manager button
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        top = QHBoxLayout()
        self.lbl_count = QLabel(tr("match_panel.lbl_matches").format(0))
        self.btn_refresh = QPushButton(tr("match_panel.btn_refresh"))
        self.btn_open_dir = QPushButton(tr("match_panel.btn_open_folder"))
        top.addWidget(self.lbl_count)
        top.addStretch(1)
        top.addWidget(self.btn_refresh)
        top.addWidget(self.btn_open_dir)
        v.addLayout(top)

        self.model = MatchListModel([])
        self.view = QListView()
        self.view.setModel(self.model)
        v.addWidget(self.view, 1)

        self.current_root: Optional[str] = None
        self.btn_open_dir.clicked.connect(self._open_dir_for_selected)

    def set_results(self, root: str, files: List[str]):
        """Set the list of matched files."""
        self.current_root = root
        self.model.set_items(files)
        self.lbl_count.setText(tr("match_panel.lbl_matches").format(len(files)))

    def selected_path(self) -> Optional[str]:
        """Get the currently selected file path."""
        idxs = self.view.selectedIndexes()
        if not idxs:
            return None
        return self.model.items[idxs[0].row()]

    def _open_dir_for_selected(self):
        """Open the folder containing the selected file in OS file manager."""
        path = self.selected_path()
        if not path:
            QMessageBox.information(self, tr("match_panel.msg_open_title"), tr("match_panel.msg_open"))
            return

        # Open in OS file manager
        if sys.platform.startswith("darwin"):
            os.system(f'open -R "{path}"')
        elif os.name == "nt":
            os.system(f'explorer /select,"{path}"')
        else:
            os.system(f'xdg-open "{os.path.dirname(path)}"')
