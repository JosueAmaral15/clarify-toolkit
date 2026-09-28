"""Isolated recovery/closure regressions, without importing the full application."""

import ast
import gc
from functools import partial
from pathlib import Path
from types import SimpleNamespace
import weakref

import pytest
from PySide6 import QtCore
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from shiboken6 import isValid

from src.editor_recovery import UnsavedRecoveryStore
from src.gui import editor_dock as module


@pytest.fixture
def workspace(qtbot, tmp_path, monkeypatch):
    settings = QtCore.QSettings(str(tmp_path / 'editor.ini'), QtCore.QSettings.IniFormat)
    settings.setValue('explorer_root_path', str(tmp_path))
    monkeypatch.setattr(QtCore, 'QSettings', lambda *args: settings)
    monkeypatch.setattr(module, 'UnsavedRecoveryStore',
                        partial(UnsavedRecoveryStore, root=tmp_path / 'recovery'))
    window = QMainWindow()
    tabs = QTabWidget(window)
    window.setCentralWidget(tabs)
    dock = module.EditorDock(window)
    tabs.addTab(dock, 'Clarify Editor')
    window.show()
    yield window, dock
    if isValid(window):
        window.deleteLater()
        QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)


@pytest.mark.parametrize('extension', ['.txt', '.json'])
@pytest.mark.parametrize('route', ['dock', 'tool-tab', 'parent', 'delete-dock', 'delete-parent', 'quit'])
def test_immediate_close_preserves_latest_buffers_in_new_instance(
    workspace, qapp, tmp_path, route, extension, qtbot
):
    window, dock = workspace
    first = dock.load_generated_content('initial', 'draft' + extension, extension=extension)
    first.editor.setPlainText('latest\n\u6587\u4ef6')
    cursor = first.editor.textCursor()
    cursor.setPosition(3)
    first.editor.setTextCursor(cursor)
    dock.load_generated_content('', 'empty.txt')
    dock.load_generated_content('sandbox', 'generated.txt', edit_only=True)
    assert dock._recovery_timer.isActive()
    store = UnsavedRecoveryStore(tmp_path / 'recovery')
    if route == 'dock':
        assert dock.close()
    elif route == 'tool-tab':
        assert dock.request_tab_close()
        window.centralWidget().removeTab(0)
    elif route == 'parent':
        assert window.close()
    elif route.startswith('delete'):
        target = dock if route == 'delete-dock' else window
        target.deleteLater()
        QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
        assert not isValid(target)
    else:
        qapp.aboutToQuit.emit()
        assert not dock._recovery_timer.isActive()
        assert dock._recovery_suspended

    snapshots = store.list()
    assert len(snapshots) == 3
    assert {item.content for item in snapshots} == {'latest\n\u6587\u4ef6', '', 'sandbox'}
    # Use a different widget/store instance; restore never connects to originals.
    recovered = module.EditorDock()
    qtbot.addWidget(recovered)
    recovered.recovery_store = store
    for snapshot in snapshots:
        tab = recovered._restore_recovery_snapshot(snapshot)
        assert tab.editor.toPlainText() == snapshot.content
        assert tab.file_path is None
        assert tab.is_modified
        if snapshot.content.startswith('latest'):
            assert tab.editor.textCursor().position() == 3


def test_repeated_edits_reschedule_checkpoint_after_first_modification(workspace):
    _, dock = workspace
    tab = dock.load_generated_content('first', 'draft.txt')
    dock._checkpoint_unsaved_tabs()
    tab.editor.moveCursor(QTextCursor.MoveOperation.End)
    tab.editor.insertPlainText(' second')
    assert dock._recovery_timer.isActive()
    assert dock.request_tab_close()
    assert dock.recovery_store.list()[0].content == 'first second'


@pytest.mark.parametrize('state', ['unchanged', 'changed', 'missing', 'large'])
def test_saved_file_references_do_not_extract_or_overwrite_original(
    workspace, tmp_path, monkeypatch, state
):
    _, dock = workspace
    source = tmp_path / 'saved.txt'
    source.write_text('original', encoding='utf-8')
    dock.open_file_path(str(source))
    tab = dock.tab_widget.currentWidget()
    monkeypatch.setattr(tab.editor, 'toPlainText', lambda: pytest.fail('saved content was copied'))
    if state == 'large':
        source.write_bytes(b'x' * (2 * 1024 * 1024 + 1))
        dock._track_tab_disk_state(tab)
    assert dock.request_tab_close()
    snapshot = dock.recovery_store.list()[0]
    assert snapshot.kind == 'reference'
    assert snapshot.content == ''
    assert (dock.recovery_store.root / (snapshot.snapshot_id + '.json')).stat().st_size < 1024
    if state == 'changed':
        source.write_text('external revision', encoding='utf-8')
    elif state == 'missing':
        source.unlink()
    restored = dock._restore_recovery_snapshot(snapshot)
    if state == 'unchanged':
        assert restored.editor.toPlainText() == 'original'
        assert restored.file_path is None
        assert restored.is_modified
    else:
        assert restored is None
        assert snapshot.snapshot_id not in dock._restored_recovery_ids
        assert snapshot.snapshot_id in {item.snapshot_id for item in dock.recovery_store.list()}
    if source.exists():
        assert source.read_bytes() == (b'x' * (2 * 1024 * 1024 + 1) if state == 'large'
                                       else b'external revision' if state == 'changed' else b'original')


@pytest.mark.parametrize('origin', ['changed', 'missing'])
def test_unsaved_snapshot_survives_changed_or_removed_origin(workspace, tmp_path, origin):
    _, dock = workspace
    source = tmp_path / 'saved.txt'
    source.write_text('original', encoding='utf-8')
    dock.open_file_path(str(source))
    dock.tab_widget.currentWidget().editor.setPlainText('unsaved revision')
    if origin == 'changed':
        source.write_text('external', encoding='utf-8')
    else:
        source.unlink()
    assert dock.request_tab_close()
    snapshot = dock.recovery_store.list()[0]
    restored = dock._restore_recovery_snapshot(snapshot)
    assert restored.editor.toPlainText() == 'unsaved revision'
    assert restored.file_path is None
    assert restored._clarify_recovery_source_path == str(source)
    if source.exists():
        assert source.read_text(encoding='utf-8') == 'external'


@pytest.mark.parametrize('fault', ['size', 'count', 'bytes', 'io'])
@pytest.mark.parametrize('route', ['dock', 'tool-tab', 'parent', 'final'])
def test_failed_checkpoint_is_honest_and_normal_close_is_blocked(
    workspace, tmp_path, monkeypatch, caplog, fault, route
):
    window, dock = workspace
    tab = dock.load_generated_content('secret-draft-do-not-log', 'draft.txt')
    store = dock.recovery_store
    if fault == 'size':
        store.max_document_bytes = 4
        monkeypatch.setattr(tab.editor, 'toPlainText', lambda: pytest.fail('oversized extraction'))
    elif fault == 'count':
        store.max_snapshots = 1
        store.save('existing', title='other.txt', content='preserve')
    elif fault == 'bytes':
        store.max_total_bytes = 1
    else:
        def fail(*args, **kwargs):
            raise OSError('synthetic I/O failure')
        monkeypatch.setattr(store, 'save', fail)
    if route == 'dock':
        assert not dock.close()
    elif route == 'tool-tab':
        assert not dock.request_tab_close()
    elif route == 'parent':
        assert not window.close()
    else:
        assert not dock._flush_recovery_on_close(final=True)
        assert dock._recovery_suspended
    assert dock._recovery_failures == 1
    assert 'failed' in dock.lbl_status.text().lower()
    assert 'secret-draft-do-not-log' not in caplog.text
    assert 'checkpoint failed' in caplog.text
    assert not dock._recovery_timer.isActive()
    if fault == 'count':
        assert store.list()[0].content == 'preserve'


@pytest.mark.parametrize('choice', [QMessageBox.Cancel, QMessageBox.Discard, QMessageBox.Save])
def test_document_tab_close_preserves_save_discard_cancel(workspace, tmp_path, monkeypatch, choice):
    _, dock = workspace
    tab = dock.load_generated_content('draft', 'draft.txt')
    assert dock._checkpoint_unsaved_tabs()
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: choice)
    output = tmp_path / 'saved.txt'
    monkeypatch.setattr(module.QFileDialog, 'getSaveFileName', lambda *args: (str(output), ''))
    dock._close_tab(0)
    if choice == QMessageBox.Cancel:
        assert dock.tab_widget.count() == 1
        assert dock.recovery_store.list()[0].content == 'draft'
    else:
        assert dock.tab_widget.count() == 0
        assert dock.recovery_store.list() == []
        assert output.exists() == (choice == QMessageBox.Save)


def test_cancelled_save_as_does_not_close_document(workspace, monkeypatch):
    _, dock = workspace
    dock.load_generated_content('draft', 'draft.txt')
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.Save)
    monkeypatch.setattr(module.QFileDialog, 'getSaveFileName', lambda *args: ('', ''))
    dock._close_tab(0)
    assert dock.tab_widget.count() == 1


def test_discard_io_failure_keeps_tab_and_disk_tracking(workspace, tmp_path, monkeypatch):
    _, dock = workspace
    source = tmp_path / 'saved.txt'
    source.write_text('original', encoding='utf-8')
    dock.open_file_path(str(source))
    tab = dock.tab_widget.currentWidget()
    tab.editor.setPlainText('draft')
    dock._checkpoint_unsaved_tabs()
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.Discard)
    def fail(*args):
        raise OSError('synthetic unlink failure')
    monkeypatch.setattr(dock.recovery_store, 'discard', fail)
    dock._close_tab(0)
    assert dock.tab_widget.count() == 1
    assert tab._clarify_disk_path == str(source)


def test_deleted_workspace_has_no_recovery_callbacks_or_retained_widgets(workspace, qapp, qtbot):
    window, dock = workspace
    tab = dock.load_generated_content('{"x":1}', 'draft.json')
    lifecycle = dock._recovery_lifecycle
    weak_dock = weakref.ref(dock)
    weak_lifecycle = weakref.ref(lifecycle)
    calls = []
    store = dock.recovery_store
    original = store.save
    def counted(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)
    store.save = counted
    assert tab.validation_timer.isActive()
    window.deleteLater()
    QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
    assert not isValid(dock)
    assert not isValid(lifecycle)
    count = len(calls)
    qapp.aboutToQuit.emit()
    qtbot.wait(1600)
    assert len(calls) == count
    del dock, lifecycle, tab
    # The workspace fixture retains the wrapper, but no Qt callbacks remain.
    gc.collect()
    assert weak_dock() is None or not isValid(weak_dock())
    assert weak_lifecycle() is None or not isValid(weak_lifecycle())


def test_reparented_tool_tracks_new_parent_close(workspace, qtbot):
    _, dock = workspace
    dock.load_generated_content('draft', 'draft.txt')
    new_parent = QMainWindow()
    qtbot.addWidget(new_parent)
    dock.setParent(new_parent)
    new_parent.setCentralWidget(dock)
    assert new_parent.close()
    assert dock.recovery_store.list()[0].content == 'draft'


def test_reopened_dock_resumes_checkpointing(workspace):
    _, dock = workspace
    tab = dock.load_generated_content('first', 'draft.txt')
    assert dock.close()
    dock.show()
    tab.editor.setPlainText('second')
    assert dock._recovery_timer.isActive()
    assert dock.request_tab_close()
    assert dock.recovery_store.list()[0].content == 'second'


@pytest.mark.parametrize('success', [True, False])
def test_actual_mainwindow_tool_close_uses_recovery_contract_without_full_startup(
    workspace, monkeypatch, success
):
    window, dock = workspace
    dock.load_generated_content('draft', 'draft.txt')
    monkeypatch.setattr(dock, 'has_unsaved_changes', lambda: True)
    monkeypatch.setattr(QMessageBox, 'question', lambda *args: pytest.fail('duplicate close prompt'))
    if not success:
        dock.recovery_store.max_document_bytes = 2
    tree = ast.parse(Path('src/app.py').read_text(encoding='utf-8'))
    node = next(item for item in ast.walk(tree)
                if isinstance(item, ast.FunctionDef) and item.name == '_close_tab')
    function_tree = ast.Module(body=[node], type_ignores=[])
    namespace = {'QMessageBox': QMessageBox, 'tr': lambda key, **kwargs: key}
    exec(compile(function_tree, 'src/app.py', 'exec'), namespace)  # pylint: disable=exec-used
    controller = SimpleNamespace(tabs=window.centralWidget(),
                                 tool_tabs={'editor': (dock, 0)},
                                 _restore_window_flags=lambda: None,
                                 _save_tab_state=lambda: None)
    namespace['_close_tab'](controller, 0)
    assert window.centralWidget().count() == (0 if success else 1)
    if success:
        assert dock.recovery_store.list()[0].content == 'draft'
    else:
        assert dock.tab_widget.currentWidget().editor.toPlainText() == 'draft'


@pytest.mark.parametrize('choice', ['recover', 'discard', 'cancel'])
def test_explicit_recovery_dialog_and_active_snapshot_isolation(workspace, monkeypatch, choice):
    _, dock = workspace
    dock.load_generated_content('active draft', 'active.txt')
    dock._checkpoint_unsaved_tabs()
    dock.recovery_store.save('older', title='older.txt', content='older draft')
    def choose(dialog):
        role = {'recover': QMessageBox.AcceptRole, 'discard': QMessageBox.DestructiveRole,
                'cancel': QMessageBox.RejectRole}[choice]
        button = next(item for item in dialog.buttons() if dialog.buttonRole(item) == role)
        monkeypatch.setattr(dialog, 'clickedButton', lambda: button)
        return 0
    monkeypatch.setattr(QMessageBox, 'exec_', choose)
    dock._show_recovery_dialog()
    assert any(snapshot.content == 'active draft' for snapshot in dock.recovery_store.list())
    if choice == 'recover':
        assert dock.tab_widget.count() == 2
        assert dock.tab_widget.currentWidget().editor.toPlainText() == 'older draft'
    else:
        assert dock.tab_widget.count() == 1
        assert ('older' in {item.snapshot_id for item in dock.recovery_store.list()}) == (choice == 'cancel')


def test_recovery_list_io_error_is_reported_without_modal(workspace, monkeypatch):
    _, dock = workspace
    def fail():
        raise OSError('synthetic list failure')
    monkeypatch.setattr(dock.recovery_store, 'list', fail)
    dock._show_recovery_dialog()
    assert 'failed' in dock.lbl_status.text().lower()


def test_failed_reference_restore_keeps_reference_and_reports_actual_count(workspace, tmp_path, monkeypatch):
    _, dock = workspace
    dock.recovery_store.save('buffer', title='draft.txt', content='draft')
    dock.recovery_store.save_reference('missing', title='missing.txt', file_path=str(tmp_path / 'missing'))
    warnings = []
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args: warnings.append(args[2]))
    def accept(dialog):
        button = next(item for item in dialog.buttons()
                      if dialog.buttonRole(item) == QMessageBox.AcceptRole)
        monkeypatch.setattr(dialog, 'clickedButton', lambda: button)
        return 0
    monkeypatch.setattr(QMessageBox, 'exec_', accept)
    dock._show_recovery_dialog()
    assert dock.tab_widget.count() == 1
    assert dock.lbl_status.text() == module.tr('editor.status_recovered_documents').format(count=1)
    assert len(warnings) == 1
    assert 'missing' not in dock._restored_recovery_ids
    assert 'missing' in {item.snapshot_id for item in dock.recovery_store.list()}


def test_closing_tool_stops_timers_watchers_and_late_notifications(workspace, tmp_path, monkeypatch):
    _, dock = workspace
    source = tmp_path / 'saved.txt'
    source.write_text('original', encoding='utf-8')
    dock.open_file_path(str(source))
    tab = dock.tab_widget.currentWidget()
    dock._set_auto_save_enabled(True)
    tab.editor.setPlainText('draft')
    assert tab.auto_save_timer.isActive()
    assert dock._file_watcher.files()
    assert dock.request_tab_close()
    assert not any(timer.isActive() for timer in dock.findChildren(QtCore.QTimer))
    assert dock._file_watcher.files() == []
    assert dock._file_watcher.directories() == []
    def unexpected(*args, **kwargs):
        pytest.fail('late callback after close')
    monkeypatch.setattr(dock.recovery_store, 'save', unexpected)
    monkeypatch.setattr(dock, '_check_external_state_for_path', unexpected)
    dock._recovery_timer.timeout.emit()
    dock._on_tab_recovery_state_changed(tab, True)
    dock._file_watcher.fileChanged.emit(str(source))
    dock._file_watcher.directoryChanged.emit(str(tmp_path))
    assert source.read_text(encoding='utf-8') == 'original'
    assert dock.recovery_store.list()[0].content == 'draft'


def test_cancelled_parent_close_does_not_suspend_live_editor(workspace, monkeypatch):
    window, dock = workspace
    dock.load_generated_content('first', 'draft.txt')
    monkeypatch.setattr(window, 'closeEvent', lambda event: event.ignore())
    assert not window.close()
    assert not dock._recovery_suspended
    dock.tab_widget.currentWidget().editor.setPlainText('second')
    assert dock._recovery_timer.isActive()
    assert dock.request_tab_close()
    assert dock.recovery_store.list()[0].content == 'second'


def test_destroyed_editor_and_lifecycle_wrappers_can_be_collected(workspace):
    # Construct a separate parent not retained by the fixture or qtbot.
    window = QMainWindow()
    dock = module.EditorDock(window)
    window.setCentralWidget(dock)
    dock.load_generated_content('draft', 'draft.txt')
    dock_reference = weakref.ref(dock)
    lifecycle_reference = weakref.ref(dock._recovery_lifecycle)
    window.deleteLater()
    QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
    del window, dock
    gc.collect()
    assert dock_reference() is None
    assert lifecycle_reference() is None
