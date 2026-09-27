"""The editor workspace must expand between its compact menu and status rows."""

from functools import partial

import pytest
from PySide6 import QtCore
from PySide6.QtWidgets import QMainWindow, QTabWidget

from src.gui import editor_dock as module


@pytest.fixture
def editor_window(qtbot, tmp_path, monkeypatch):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module, "UnsavedRecoveryStore",
        partial(module.UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    window = QMainWindow()
    tabs = QTabWidget(window)
    window.setCentralWidget(tabs)
    dock = module.EditorDock(window)
    tabs.addTab(dock, "Clarify Editor")
    qtbot.addWidget(window)
    return window, dock


@pytest.mark.parametrize("extension", [None, ".txt", ".json"])
@pytest.mark.parametrize("explorer_visible", [True, False])
def test_workspace_fills_available_height_on_resize(editor_window, qtbot, extension, explorer_visible):
    window, dock = editor_window
    dock._set_explorer_visible(explorer_visible)
    if extension:
        content = '{"message": "Full-height editor"}' if extension == ".json" else "Full-height editor"
        dock.load_generated_content(content, "example" + extension, extension=extension)

    previous_height = 0
    for width, height in [(800, 500), (1200, 650), (1440, 900)]:
        window.resize(width, height)
        window.show()
        qtbot.waitUntil(lambda: dock.main_widget.height() > previous_height)
        QtCore.QCoreApplication.processEvents()

        workspace = dock.editor_splitter.geometry()
        menu_bottom = dock.menu_bar.mapTo(dock.main_widget, dock.menu_bar.rect().bottomLeft()).y()
        status_top = dock.lbl_status.mapTo(dock.main_widget, dock.lbl_status.rect().topLeft()).y()
        assert workspace.top() - menu_bottom <= 16
        assert status_top - workspace.bottom() <= 16
        assert workspace.height() >= dock.main_widget.height() - 100
        assert dock.tab_widget.height() >= workspace.height() - 4
        if extension:
            assert dock.tab_widget.currentWidget().editor.height() >= workspace.height() - 120
        if not explorer_visible:
            assert dock.tab_widget.width() == dock.editor_splitter.width()
        previous_height = dock.main_widget.height()
