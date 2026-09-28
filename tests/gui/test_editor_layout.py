"""The editor workspace must expand between its compact menu and status rows."""

from functools import partial
from pathlib import Path

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


@pytest.mark.parametrize("name", [
    "notes", "abcdefghijklmnopqrstuvw", "abcdefghijklmnopqrstuvwx", "abcdefghijklmnopqrstuvwxy",
    "<b>folder-long-name", "\u6587\u4ef6\u5939" * 9,
])
def test_explorer_header_shows_current_folder_with_24_character_limit(
    editor_window, tmp_path, name
):
    _, dock = editor_window
    folder = tmp_path / name
    folder.mkdir()

    assert dock._set_explorer_root(str(folder))
    expected = name if len(name) <= 24 else name[:21] + "..."
    assert dock.explorer_folder_label.text() == expected
    assert len(dock.explorer_folder_label.text()) <= 24
    assert dock.explorer_folder_label.toolTip() == str(folder)
    assert dock.explorer_folder_label.textFormat() == QtCore.Qt.TextFormat.PlainText
    assert dock.explorer_title_label.text() == module.tr("editor.lbl_explorer")
    assert dock.explorer_model.rootPath() == str(folder)


def test_explorer_header_initial_root_and_fallback(editor_window, tmp_path):
    _, dock = editor_window
    name = tmp_path.name
    assert dock.explorer_folder_label.text() == (name if len(name) <= 24 else name[:21] + "...")
    assert dock.explorer_folder_label.toolTip() == str(tmp_path)

    dock._set_explorer_root(str(tmp_path / "missing"))
    assert dock.explorer_folder_label.toolTip() == str(Path.home())
    assert dock.explorer_model.rootPath() == str(Path.home())

    dock._set_explorer_root(str(Path.home().anchor))
    assert dock.explorer_folder_label.text() == Path.home().anchor


def test_open_folder_updates_header_and_cancel_preserves_it(
    editor_window, tmp_path, monkeypatch
):
    _, dock = editor_window
    folder = tmp_path / "selected-folder-with-a-long-name"
    folder.mkdir()
    monkeypatch.setattr(module.QFileDialog, "getExistingDirectory", lambda *args: str(folder))
    dock._open_explorer_folder()
    assert dock.explorer_folder_label.text() == folder.name[:21] + "..."
    assert dock.explorer_folder_label.toolTip() == str(folder)

    monkeypatch.setattr(module.QFileDialog, "getExistingDirectory", lambda *args: "")
    dock._open_explorer_folder()
    assert dock.explorer_folder_label.toolTip() == str(folder)

    dock._set_explorer_root(str(tmp_path))
    assert dock.explorer_folder_label.toolTip() == str(tmp_path)


def test_explorer_header_fits_narrow_sidebar(editor_window, tmp_path, qtbot):
    window, dock = editor_window
    folder = tmp_path / ("W" * 30)
    folder.mkdir()
    dock._set_explorer_root(str(folder))
    window.resize(800, 500)
    window.show()
    dock.editor_splitter.setSizes([180, 620])
    qtbot.waitUntil(lambda: dock.explorer_folder_label.width() > 0)

    caption = dock.explorer_title_label
    name = dock.explorer_folder_label
    assert caption.geometry().right() < name.geometry().left()
    assert name.geometry().right() < dock.explorer_panel.width()
    assert dock.explorer_panel.width() <= 240
    assert name.fontMetrics().horizontalAdvance(name.text()) <= name.contentsRect().width()
    dock.editor_splitter.setSizes([450, 350])
    qtbot.waitUntil(lambda: name.text() == folder.name[:21] + "...")
    assert len(name.text()) == 24


def test_explorer_lists_hidden_files_and_directories(editor_window, tmp_path, qtbot):
    window, dock = editor_window
    folder = tmp_path / "dotfiles"
    folder.mkdir()
    expected = {".env", ".env.example", ".env example", "README.txt", ".config"}
    for name in expected - {".config"}:
        (folder / name).write_text("example content", encoding="utf-8")
    hidden_folder = folder / ".config"
    hidden_folder.mkdir()
    (hidden_folder / ".settings").write_text("example settings", encoding="utf-8")
    window.show()
    with qtbot.waitSignal(
        dock.explorer_model.directoryLoaded,
        check_params_cb=lambda path: path == str(folder),
        timeout=5000,
    ):
        dock._set_explorer_root(str(folder))

    def visible_names(index):
        return {dock.explorer_model.fileName(dock.explorer_model.index(row, 0, index))
                for row in range(dock.explorer_model.rowCount(index))}

    def root_loaded():
        assert dock.explorer_tree.rootIndex().isValid()
        assert dock.explorer_model.filePath(dock.explorer_tree.rootIndex()) == str(folder)
        names = visible_names(dock.explorer_tree.rootIndex())
        assert expected <= names, names

    qtbot.waitUntil(root_loaded)
    root = dock.explorer_tree.rootIndex()
    assert visible_names(root) == expected
    assert "." not in visible_names(root) and ".." not in visible_names(root)
    directory_index = dock.explorer_model.index(str(hidden_folder))
    assert dock.explorer_model.isDir(directory_index)
    dock.explorer_tree.expand(directory_index)
    qtbot.waitUntil(lambda: ".settings" in visible_names(
        dock.explorer_model.index(str(hidden_folder))
    ))


def test_explorer_rebinds_loaded_root_but_ignores_stale_directory(editor_window, tmp_path, qtbot):
    _, dock = editor_window
    previous = tmp_path / "previous"
    current = tmp_path / "current"
    previous.mkdir()
    current.mkdir()
    dock._set_explorer_root(str(previous))
    dock._set_explorer_root(str(current))
    qtbot.waitUntil(lambda: dock.explorer_model.index(str(current)).isValid())
    dock.explorer_tree.setRootIndex(QtCore.QModelIndex())
    dock.explorer_model.directoryLoaded.emit(str(previous))
    assert dock.explorer_model.filePath(dock.explorer_tree.rootIndex()) == str(current)
    dock.explorer_model.directoryLoaded.emit(str(current))
    assert dock.explorer_tree.rootIndex().isValid()
    assert dock.explorer_model.filePath(dock.explorer_tree.rootIndex()) == str(current)
    assert dock.explorer_root_path == str(current)


@pytest.mark.parametrize("name", [".env", ".env.example", ".env example"])
def test_explorer_opens_hidden_file(editor_window, tmp_path, qtbot, name):
    _, dock = editor_window
    folder = tmp_path / "hidden-open"
    folder.mkdir()
    source = folder / name
    source.write_text("EXAMPLE_SETTING=demo", encoding="utf-8")
    dock._set_explorer_root(str(folder))
    root = dock.explorer_tree.rootIndex()
    qtbot.waitUntil(lambda: dock.explorer_model.rowCount(root) == 1)
    index = dock.explorer_model.index(0, 0, root)
    assert dock.explorer_model.fileName(index) == name

    dock._open_explorer_index(index)
    tab = dock.tab_widget.currentWidget()
    assert tab.file_path == str(source)
    assert tab.editor.toPlainText() == "EXAMPLE_SETTING=demo"
