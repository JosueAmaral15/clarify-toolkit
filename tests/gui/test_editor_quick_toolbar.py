"""Regressions for the Clarify Editor shared-action quick toolbar."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from functools import partial

import pytest
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QToolBar, QToolButton

from src.editor_recovery import UnsavedRecoveryStore
from src.gui import editor_dock as module

TOOLBAR_ITEMS = (
    "new",
    "open",
    "save",
    None,
    "undo",
    "redo",
    None,
    "cut",
    "copy",
    "paste",
    None,
    "find",
    "find_replace",
)


@pytest.fixture
def dock(qapp, qtbot, monkeypatch, tmp_path):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.Format.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    widget = module.EditorDock()
    widget.resize(900, 700)
    widget.show()
    qtbot.addWidget(widget)
    qapp.processEvents()
    yield widget
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


def toolbar_sequence(toolbar):
    """Represent separators as None and command actions by their stable IDs."""
    return tuple(None if action.isSeparator() else action.data() for action in toolbar.actions())


def test_quick_toolbar_is_icon_only_and_between_menu_and_workspace(dock):
    toolbar = dock.quick_toolbar

    assert isinstance(toolbar, QToolBar)
    assert toolbar.objectName() == "editor_quick_toolbar"
    assert toolbar.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
    assert not toolbar.isMovable()
    assert not toolbar.isFloatable()
    assert toolbar.accessibleName()
    assert toolbar.toolTip()
    assert toolbar_sequence(toolbar) == TOOLBAR_ITEMS

    menu_bottom = dock.menu_bar.mapTo(dock.main_widget, dock.menu_bar.rect().bottomLeft()).y()
    toolbar_top = toolbar.mapTo(dock.main_widget, toolbar.rect().topLeft()).y()
    toolbar_bottom = toolbar.mapTo(dock.main_widget, toolbar.rect().bottomLeft()).y()
    workspace_top = dock.editor_splitter.mapTo(dock.main_widget, dock.editor_splitter.rect().topLeft()).y()
    assert menu_bottom < toolbar_top <= toolbar_bottom < workspace_top


def test_quick_toolbar_reuses_the_exact_menu_actions_and_icons(dock):
    for action_id in (item for item in TOOLBAR_ITEMS if item is not None):
        action = dock._action_by_id[action_id]
        assert action in dock.quick_toolbar.actions()
        assert not action.icon().isNull()
        button = dock.quick_toolbar.widgetForAction(action)
        assert isinstance(button, QToolButton)
        assert button.defaultAction() is action
        assert button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
        assert button.accessibleName()
        assert button.toolTip()


def test_toolbar_click_has_one_shared_action_route(dock, qtbot):
    action = dock.action_new
    button = dock.quick_toolbar.widgetForAction(action)
    triggered = QSignalSpy(action.triggered)

    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert triggered.count() == 1
    assert dock.tab_widget.count() == 1
    assert dock.tab_widget.currentWidget() is not None


def test_toolbar_state_tracks_shared_actions_without_manual_sync(dock):
    assert not dock.action_save.isEnabled()
    assert not dock.quick_toolbar.widgetForAction(dock.action_save).isEnabled()

    dock._new_file()

    assert dock.action_save.isEnabled()
    assert dock.quick_toolbar.widgetForAction(dock.action_save).isEnabled()
    dock.action_save.setEnabled(False)
    assert not dock.quick_toolbar.widgetForAction(dock.action_save).isEnabled()


def test_toolbar_shared_redo_targets_the_active_split(dock, qtbot, monkeypatch):
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    tab.editor.insertPlainText("one")
    tab.editor.undo()
    assert dock._show_split_view(tab, Qt.Orientation.Horizontal)
    calls = []
    monkeypatch.setattr(tab.editor, "redo", lambda: calls.append("primary"))
    monkeypatch.setattr(dock.split_editor, "redo", lambda: calls.append("split"))

    button = dock.quick_toolbar.widgetForAction(dock.action_redo)
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert calls == ["split"]


def test_toolbar_remains_bounded_at_narrow_width(dock, qapp):
    dock.resize(360, 520)
    qapp.processEvents()

    assert dock.quick_toolbar.width() <= dock.main_widget.width()
    assert dock.editor_splitter.height() > 0
    assert dock.quick_toolbar.sizeHint().height() <= 48


def test_toolbar_accessibility_and_tooltips_retranslate(dock, monkeypatch):
    monkeypatch.setattr(module, "tr", lambda key, default=None: f"text:{key}")
    monkeypatch.setattr(module, "tooltip_tr", lambda key: f"tip:{key}")

    dock._retranslate_editor_ui("test")

    assert dock.quick_toolbar.accessibleName() == "text:editor.quick_toolbar"
    assert dock.quick_toolbar.toolTip() == "tip:editor.quick_toolbar"
    for action_id in (item for item in TOOLBAR_ITEMS if item is not None):
        action = dock._action_by_id[action_id]
        text_key = dock._ACTION_SPECS[action_id]["text_key"]
        button = dock.quick_toolbar.widgetForAction(action)
        assert action.text() == f"text:{text_key}"
        assert action.toolTip() == f"tip:{text_key}"
        assert button.accessibleName() == f"text:{text_key}"


def test_runtime_language_signal_refreshes_shared_toolbar_actions(dock):
    translator = module.get_translator()
    original = translator.current_language
    target = "pt_BR" if original != "pt_BR" else "en"

    try:
        translator.switch_language(target)
        assert dock.quick_toolbar.accessibleName() == translator.get("editor.quick_toolbar")
        assert dock.action_find.text() == translator.get("editor.btn_find")
        assert dock.quick_toolbar.widgetForAction(dock.action_find).accessibleName() == translator.get(
            "editor.btn_find"
        )
    finally:
        translator.switch_language(original)
