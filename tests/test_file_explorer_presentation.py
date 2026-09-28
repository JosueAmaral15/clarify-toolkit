"""Final finite FE-PAR-08 presentation and bounded real-worker regressions."""

import json

import pytest
import shiboken6
from PySide6.QtCore import QCoreApplication, QEvent, QSettings
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from src.gui.file_explorer_dock import OPERATION_LOG_MAX_ENTRIES, OPERATION_LOG_MAX_ENTRY_CHARS
from src.gui.panels.file_explorer_operation import ExplorerOperationReceiver
from src.gui.panels.search_replace_panel import SearchReplacePanel
from src.gui.file_list_dock import FileListDock
from src.gui.widgets.file_filter_panel import FileFilterPanel
from src.gui.widgets.file_list_table_manager import FileListTableManager
from src.i18n.translator import tr
from src.ui import thread_manager
from test_file_explorer_lifecycle import docks, pause_at_first_checkpoint, request
from test_file_explorer_replace import populate_dock
from test_file_explorer_target_scope import select_paths, set_scope


def test_default_font_reuses_system_monospace_and_application_size(docks):
    dock = docks()
    expected = QFontDatabase.systemFont(QFontDatabase.FixedFont)
    assert dock.content_panel.ed_query.font().family() == expected.family()
    assert dock.content_panel.ed_query.font().pointSizeF() == dock.font().pointSizeF()
    assert dock.content_panel.ed_query.font() == dock.replace_panel.ed_replace.font()
    assert dock.operation_log.font() == dock.content_panel.ed_query.font()


def test_shared_search_font_is_reused_at_lazy_creation(docks):
    host = QMainWindow()
    host.tab_search = SearchReplacePanel(host)
    chosen = QFont('DejaVu Sans Mono', 17)
    host.tab_search.set_editor_fonts(chosen)
    dock = docks(host)
    assert dock.content_panel.ed_query.font() == host.tab_search.ed_query.font()
    assert dock.replace_panel.ed_replace.font() == host.tab_search.ed_repl.font()
    assert dock.operation_log.font() == chosen


def test_font_api_preserves_text_selection_and_dimensions(docks):
    dock = docks()
    dock.content_panel.set_query('first\nsecond')
    dock.replace_panel.set_replacement('replacement')
    query = dock.content_panel.ed_query
    cursor = query.textCursor()
    cursor.setPosition(2)
    query.setTextCursor(cursor)
    heights = (query.maximumHeight(), dock.replace_panel.ed_replace.maximumHeight())
    font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
    font.setPointSize(18)
    dock.set_editor_fonts(font)
    assert query.toPlainText() == 'first\nsecond'
    assert query.textCursor().position() == 2
    assert dock.replace_panel.get_replacement() == 'replacement'
    assert heights == (query.maximumHeight(), dock.replace_panel.ed_replace.maximumHeight())


def test_application_font_change_reuses_accessibility_size(qapp, docks):
    dock = docks()
    original = qapp.font()
    family = dock.content_panel.ed_query.font().family()
    try:
        changed = QFont(original)
        changed.setPointSize(16)
        qapp.setFont(changed)
        qapp.processEvents()
        assert dock.content_panel.ed_query.font().pointSize() == 16
        assert dock.content_panel.ed_query.font().family() == family
        assert dock.replace_panel.ed_replace.font() == dock.content_panel.ed_query.font()
    finally:
        qapp.setFont(original)
        qapp.processEvents()


@pytest.mark.parametrize('message', ['<b>literal</b>', 'a\nb\rc\u2028d\u2029e\x00f', 'x' * 10000])
def test_log_is_plain_single_block_and_bounded(docks, message):
    dock = docks()
    dock._append_operation_log(message)
    text = dock.operation_log.toPlainText()
    assert len(text) <= OPERATION_LOG_MAX_ENTRY_CHARS
    assert dock.operation_log.document().blockCount() == 1
    if message.startswith('<'):
        assert text == message
    assert dock.operation_log.isReadOnly()
    assert not dock.operation_log.isUndoRedoEnabled()


def test_log_retains_only_latest_entries_without_secondary_buffer(docks):
    dock = docks()
    for number in range(OPERATION_LOG_MAX_ENTRIES + 20):
        dock._append_operation_log(f'{number}:' + 'x' * 1000)
    entries = dock.operation_log.toPlainText().splitlines()
    assert len(entries) == OPERATION_LOG_MAX_ENTRIES
    assert entries[0].startswith('20:') and entries[-1].startswith('219:')
    assert all(len(entry) == OPERATION_LOG_MAX_ENTRY_CHARS for entry in entries)
    assert len(dock.operation_log.toPlainText()) <= OPERATION_LOG_MAX_ENTRIES * (OPERATION_LOG_MAX_ENTRY_CHARS + 1)


@pytest.mark.parametrize('reason', ['stale', 'cancel', 'closing'])
def test_receiver_does_not_append_late_diagnostic_or_progress(docks, reason):
    dock = docks()
    dock._active_operation = True
    receiver = ExplorerOperationReceiver(dock, dock._operation_generation)
    if reason == 'stale':
        dock._operation_generation += 1
    elif reason == 'cancel':
        dock._cancel_requested = True
    else:
        dock._discard_callbacks = True
    try:
        receiver.diagnostic('late')
        receiver.progress_detailed(1, 2, 'late')
        assert dock.operation_log.toPlainText() == ''
        assert dock.progress_dialog is None
    finally:
        dock._active_operation = False


def test_diagnostic_is_bounded_and_visible_without_log_expansion(docks):
    dock = docks()
    dock._active_operation = True
    receiver = ExplorerOperationReceiver(dock, dock._operation_generation)
    try:
        receiver.diagnostic('error' * 1000)
        assert len(dock.results_status.toolTip()) == 500
        assert len(dock.operation_log.toPlainText()) == OPERATION_LOG_MAX_ENTRY_CHARS
        assert dock.section_log.isCollapsed()
        dock.section_log.header_button.click()
        assert not dock.section_log.isCollapsed()
        dock.retranslateUi()
        assert dock.section_log.title() == tr('file_explorer.operation_log')
    finally:
        dock._active_operation = False


@pytest.mark.parametrize('enabled', [False, True])
def test_extension_draft_and_effective_filter_round_trip_clear(docks, enabled):
    dock = docks()
    panel = dock.filter_panel
    assert not panel.isCheckable()
    assert panel.chk_use_ext_filter.isEnabled()
    panel.ed_extensions.setText('.txt, md')
    panel.chk_use_ext_filter.setChecked(enabled)
    expected = dock._get_current_filters()
    assert expected['extensions'] == (['txt', 'md'] if enabled else [])
    panel.clear_filters()
    assert not panel.chk_use_ext_filter.isChecked() and not panel.ed_extensions.isEnabled()
    dock._apply_filters_to_widgets(expected)
    assert dock._get_current_filters() == expected
    assert panel.ed_extensions.text() == '.txt, md'
    assert panel.ed_extensions.isEnabled() == enabled
    state = 'on' if enabled else 'off'
    assert tr('file_explorer.extensions_' + state) in dock.section_filters.title()
    assert dock.section_filters.isCollapsed()


@pytest.mark.parametrize('preset,enabled,text', [
    ({'extensions': ['txt', 'md']}, True, 'txt,md'),
    ({'extensions': [], 'use_ext_filter': True}, True, ''),
    ({'extensions': ['txt'], 'use_ext_filter': False}, False, 'txt'),
    ({'extensions': []}, False, ''),
])
def test_legacy_extension_presets_have_explicit_compatible_state(docks, preset, enabled, text):
    dock = docks()
    dock._apply_filters_to_widgets(preset)
    assert dock.filter_panel.chk_use_ext_filter.isChecked() == enabled
    assert dock.filter_panel.ed_extensions.text() == text
    if enabled and not text:
        assert tr('file_explorer.extensions_all') in dock.section_filters.title()
    dock.retranslateUi()
    assert tr('file_explorer.extensions_all' if enabled and not text else
              'file_explorer.extensions_on' if enabled else 'file_explorer.extensions_off') in dock.section_filters.title()


@pytest.mark.parametrize('preset', [
    {'extensions': 'txt'}, {'extensions': [1]}, {'use_ext_filter': 'false'},
    {'extensions_text': 3}, {'extensions_text': 'x' * 32768},
    {'extensions': ['x'] * 32768}, {'extensions': ['x' * 32768]},
    {'extensions_text': '\U0001f600' * 20000},
])
def test_invalid_extension_preset_rejected_before_panel_mutation(docks, preset):
    dock = docks()
    dock.filter_panel.ed_extensions.setText('txt')
    before = dock._get_current_filters()
    with pytest.raises(ValueError):
        dock._apply_filters_to_widgets(dict(preset, regex={'pattern': 'would change'}))
    assert dock._get_current_filters() == before


@pytest.mark.parametrize('enabled', [False, True])
def test_extension_preset_json_and_settings_with_fe06_conditions(tmp_path, docks, monkeypatch, enabled):
    dock = docks()
    dock.conditions_grid.set_conditions([dict(field='content', operator='contains', value='cat',
                                            whole_word=True, scope_type='brackets', scope_value='')], 'OR')
    dock.filter_panel.ed_extensions.setText('.txt,md')
    dock.filter_panel.chk_use_ext_filter.setChecked(enabled)
    expected = dock._get_current_filters()
    manager = dock.preset_manager
    QSettings('Clarify', manager.settings_group).setValue('Presets/FE08', json.dumps(expected))
    manager.refresh()
    dock.filter_panel.clear_filters()
    dock.conditions_grid.clear_conditions()
    manager.set_current_preset('FE08')
    assert dock._get_current_filters() == expected
    path = tmp_path / 'preset.json'
    monkeypatch.setattr(QFileDialog, 'getSaveFileName', lambda *a: (str(path), ''))
    manager.export_preset()
    assert json.loads(path.read_text()) == expected
    dock.filter_panel.clear_filters()
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *a: (str(path), ''))
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.No)
    manager.import_preset()
    assert dock._get_current_filters() == expected


def test_shared_file_list_consumer_keeps_its_group_and_effective_extension_contract(qapp, qtbot):
    dock = FileListDock()
    qtbot.addWidget(dock)
    panel = dock.filter_panel
    assert isinstance(panel, FileFilterPanel) and panel.isCheckable()
    panel.setChecked(True)
    panel.set_filters({'extensions': ['txt'], 'use_ext_filter': False})
    assert dock._get_current_filters()['extensions'] == []
    assert panel.ed_extensions.text() == 'txt'
    panel.set_filters({'extensions': ['txt']})
    assert dock._get_current_filters()['extensions'] == ['txt']
    panel.clear_filters()
    assert not panel.chk_use_ext_filter.isChecked()


@pytest.mark.parametrize('view', [0, 1])
@pytest.mark.parametrize('scope', ['file', 'folder', 'selected'])
def test_real_worker_extensions_scopes_views_and_relaxed_cache(tmp_path, docks, qtbot, view, scope):
    chosen, sibling = tmp_path / 'chosen.txt', tmp_path / 'sibling.md'
    chosen.write_text('needle')
    sibling.write_text('needle')
    dock = docks()
    populate_dock(dock, [chosen, sibling])
    select_paths(dock, view, [sibling])
    set_scope(dock, scope)
    dock.ed_directory.setText(str(tmp_path if scope == 'folder' else sibling))
    dock.ed_exc.clear()
    dock.content_panel.set_query('needle')
    dock._user_manually_changed_view = True
    dock.filter_panel.ed_extensions.setText('txt')
    dock.filter_panel.chk_use_ext_filter.setChecked(True)
    signature = dock._snapshot_target()[-1]
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    expected = {str(chosen)} if scope == 'folder' else set()
    assert set(dock.last_search_results) == expected
    if scope == 'selected':
        # A new explicit selection is necessary after the result view became empty.
        populate_dock(dock, [chosen, sibling])
        select_paths(dock, view, [sibling])
    dock.filter_panel.chk_use_ext_filter.setChecked(False)
    assert dock._last_content_search_universe is None
    assert dock._snapshot_target()[-1] != signature
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    expected = {str(chosen), str(sibling)} if scope == 'folder' else {str(sibling)}
    assert set(dock.last_search_results) == expected
    assert dock.results_stack.currentIndex() == view
    if view == 1:
        table = dock.table_manager.table
        assert {table.item(row, FileListTableManager.COL_PATH).text()
                for row in range(table.rowCount())} == expected
    log = dock.operation_log.toPlainText()
    assert tr('file_explorer.log_started').format('search') in log
    assert tr('file_explorer.log_finished').format('search', len(expected)) in log


@pytest.mark.parametrize('view', [0, 1])
def test_extension_case_matches_executor_in_both_result_views(tmp_path, docks, qtbot, view):
    path = tmp_path / 'chosen.TXT'
    path.write_text('needle')
    dock = docks()
    dock.combo_view_mode.setCurrentIndex(view)
    dock._user_manually_changed_view = True
    dock.ed_directory.setText(str(tmp_path))
    dock.ed_exc.clear()
    dock.content_panel.set_query('needle')
    dock.filter_panel.set_filters({'extensions': ['.TXT']})
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert set(dock.last_search_results) == {str(path)}
    dock._sync_search_to_table()
    assert dock.table_manager.table.rowCount() == 1
    assert dock.table_manager.table.item(0, FileListTableManager.COL_PATH).text() == str(path)


def test_new_instance_reuses_font_not_previous_operation_log(docks):
    first = docks()
    first._append_operation_log('old operation')
    first.close()
    second = docks()
    assert second.operation_log.toPlainText() == ''
    assert second.content_panel.ed_query.font() == first.content_panel.ed_query.font()


@pytest.mark.parametrize('action', ['resume', 'cancel', 'close', 'delete'])
def test_paused_extension_change_never_restores_stale_cache_or_late_log(tmp_path, docks, qtbot,
                                                                     monkeypatch, action):
    (tmp_path / 'chosen.txt').write_text('needle')
    dock = docks()
    dock.ed_directory.setText(str(tmp_path))
    dock.ed_exc.clear()
    dock.content_panel.set_query('needle')
    dock.filter_panel.ed_extensions.setText('txt')
    dock.filter_panel.chk_use_ext_filter.setChecked(True)
    entered, _ = pause_at_first_checkpoint(dock, monkeypatch)
    dock._list_files()
    qtbot.waitUntil(entered.is_set, timeout=3000)
    before = dock.operation_log.toPlainText()
    dock.filter_panel.ed_extensions.setText('md')
    assert not dock._launch_operation('browse', request('browse', tmp_path))
    assert dock.operation_log.toPlainText() == before
    if action == 'resume':
        dock.executor.resume()
    elif action == 'cancel':
        dock._on_progress_canceled()
    elif action == 'close':
        dock.close()
    else:
        log = dock.operation_log
        dock.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        assert not shiboken6.isValid(log)
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=3000)
    if action != 'delete':
        assert not dock._operation_running()
        assert dock._last_content_search_universe is None
        if action == 'close':
            assert dock.operation_log.toPlainText() == before
        elif action == 'cancel':
            assert tr('file_explorer.log_cancelled').format('search', 0) in dock.operation_log.toPlainText()


def test_real_worker_error_is_logged_and_can_start_again(tmp_path, docks, qtbot, monkeypatch):
    dock = docks()
    monkeypatch.setattr(dock, '_on_browse_finished', lambda result: None)
    original = dock.executor.execute_browse
    monkeypatch.setattr(dock.executor, 'execute_browse', lambda **kw: (_ for _ in ()).throw(ValueError('failed operation')))
    assert dock._launch_operation('browse', request('browse', tmp_path))
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert 'failed operation' in dock.operation_log.toPlainText()
    monkeypatch.setattr(dock.executor, 'execute_browse', original)
    assert dock._launch_operation('browse', request('browse', tmp_path))
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert tr('file_explorer.log_finished').format('browse', 0) in dock.operation_log.toPlainText()
