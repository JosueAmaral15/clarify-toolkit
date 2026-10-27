"""Regressions for clean Clarify Editor file-open settlement."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from functools import partial

import pytest
from PySide6 import QtCore
from PySide6.QtGui import QTextCursor

from src.editor_notes import TemporaryNoteStore
from src.editor_recovery import UnsavedRecoveryStore
from src.gui import editor_dock as module


@pytest.fixture
def dock(qapp, qtbot, monkeypatch, tmp_path):
    settings = QtCore.QSettings(
        str(tmp_path / "editor.ini"),
        QtCore.QSettings.IniFormat,
    )
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    monkeypatch.setattr(
        module,
        "TemporaryNoteStore",
        partial(TemporaryNoteStore, root=tmp_path / "notes"),
    )
    widget = module.EditorDock()
    widget.show()
    qtbot.addWidget(widget)
    qapp.processEvents()
    yield widget
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


@pytest.mark.parametrize(
    ("name", "content"),
    (("sample.txt", "alpha\nbeta\n"), ("sample.json", '{"alpha": 1}\n')),
)
def test_successful_open_stays_clean_after_initial_highlighting(
    dock,
    qtbot,
    tmp_path,
    name,
    content,
):
    source = tmp_path / name
    source.write_text(content, encoding="utf-8")

    assert dock.open_file_path(str(source))
    tab = dock.tab_widget.currentWidget()
    qtbot.wait(900)

    assert tab.file_path == str(source)
    assert tab.editor.toPlainText() == content
    assert not tab.is_modified
    assert not tab.editor.document().isModified()
    assert "*" not in dock.tab_widget.tabText(dock.tab_widget.currentIndex())
    assert getattr(tab, "_clarify_external_state") == "clean"
    assert dock.recent_files == [str(source)]


def test_recent_open_reuses_the_clean_tab_without_reloading(dock, qtbot, tmp_path):
    source = tmp_path / "recent.py"
    source.write_text("answer = 42\n", encoding="utf-8")

    assert dock.open_file_path(str(source))
    tab = dock.tab_widget.currentWidget()
    highlighter = tab.highlighter
    assert dock.open_file_path(str(source))
    qtbot.wait(900)

    assert dock.tab_widget.count() == 1
    assert dock.tab_widget.currentWidget() is tab
    assert tab.highlighter is highlighter
    assert not tab.is_modified
    assert not tab.editor.document().isModified()
    assert dock.recent_files == [str(source)]


def test_edit_only_open_stays_clean_but_detaches_the_source(dock, qtbot, tmp_path):
    source = tmp_path / "reference.py"
    source.write_text("value = 1\n", encoding="utf-8")

    assert dock.open_file_path(str(source), edit_only=True)
    tab = dock.tab_widget.currentWidget()
    qtbot.wait(900)

    assert tab.file_path is None
    assert tab.editor.toPlainText() == "value = 1\n"
    assert not tab.is_modified
    assert not tab.editor.document().isModified()
    assert "*" not in dock.tab_widget.tabText(dock.tab_widget.currentIndex())
    assert str(source) not in dock.recent_files


def test_empty_read_only_split_stays_clean(dock, qtbot, tmp_path):
    source = tmp_path / "empty.py"
    source.write_text("", encoding="utf-8")

    assert dock.open_file_path(str(source))
    tab = dock.tab_widget.currentWidget()
    tab.editor.setReadOnly(True)
    assert dock._show_split_view(tab, QtCore.Qt.Orientation.Horizontal)
    qtbot.wait(900)

    assert tab.editor.isReadOnly()
    assert dock.split_editor.isReadOnly()
    assert dock.split_editor.document() is tab.editor.document()
    assert not tab.is_modified
    assert not tab.editor.document().isModified()
    assert "*" not in dock.tab_widget.tabText(dock.tab_widget.currentIndex())


@pytest.mark.parametrize(
    ("name", "content", "addition"),
    (("editable.py", "value = 1\n", "# changed"), ("editable.json", "{}\n", " ")),
)
def test_user_edit_after_open_is_the_first_dirty_transition(
    dock,
    qtbot,
    tmp_path,
    name,
    content,
    addition,
):
    source = tmp_path / name
    source.write_text(content, encoding="utf-8")
    assert dock.open_file_path(str(source))
    tab = dock.tab_widget.currentWidget()
    qtbot.wait(900)
    assert not tab.is_modified

    tab.editor.moveCursor(QTextCursor.MoveOperation.End)
    qtbot.keyClicks(tab.editor, addition)

    assert tab.is_modified
    assert tab.editor.document().isModified()
    assert "*" in dock.tab_widget.tabText(dock.tab_widget.currentIndex())


def test_failed_utf8_open_does_not_publish_tab_or_recent_entry(
    dock,
    monkeypatch,
    tmp_path,
):
    source = tmp_path / "invalid.txt"
    source.write_bytes(b"valid-prefix\xffinvalid")
    errors = []
    monkeypatch.setattr(
        module.QMessageBox,
        "critical",
        lambda *_args: errors.append(True),
    )

    assert not dock.open_file_path(str(source))

    assert dock.tab_widget.count() == 0
    assert str(source) not in dock.recent_files
    assert errors == [True]


def test_external_change_is_not_an_editor_dirty_state(dock, qtbot, tmp_path):
    source = tmp_path / "external.txt"
    source.write_text("before\n", encoding="utf-8")
    assert dock.open_file_path(str(source))
    tab = dock.tab_widget.currentWidget()
    qtbot.wait(900)

    source.write_text("after\n", encoding="utf-8")
    assert dock._check_tab_external_state(tab) == "modified"
    dock._update_tab_title(tab)

    assert not tab.is_modified
    assert not tab.editor.document().isModified()
    title = dock.tab_widget.tabText(dock.tab_widget.currentIndex())
    assert "*" not in title
    assert title.endswith("[external]")

    assert dock._reload_current_tab_from_disk()
    qtbot.wait(900)
    assert tab.editor.toPlainText() == "after\n"
    assert not tab.is_modified
    assert not tab.editor.document().isModified()
    assert dock.tab_widget.tabText(dock.tab_widget.currentIndex()) == "external.txt"


def test_first_save_as_stays_clean_after_highlighter_setup(
    dock,
    qtbot,
    monkeypatch,
    tmp_path,
):
    destination = tmp_path / "first.py"
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    tab.editor.setPlainText("value = 1\n")
    monkeypatch.setattr(
        module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(destination), "Python (*.py)"),
    )

    assert dock._save_file_as()
    qtbot.wait(900)

    assert destination.read_text(encoding="utf-8") == "value = 1\n"
    assert tab.file_path == str(destination)
    assert not tab.is_modified
    assert not tab.editor.document().isModified()
    assert dock.tab_widget.tabText(dock.tab_widget.currentIndex()) == "first.py"
