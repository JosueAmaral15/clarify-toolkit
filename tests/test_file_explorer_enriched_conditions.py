"""FE-PAR-06 scope controls, preset compatibility and exact worker targets."""

import json
import re
import threading

import pytest
from PySide6.QtCore import QSettings, QThread
from PySide6.QtWidgets import QFileDialog, QMessageBox

import src.core.filters as shared
import src.core.file_explorer_executor as core
from src.gui.widgets.search_widgets import ConditionsGrid
from src.ui import thread_manager
from test_file_explorer_lifecycle import docks
from test_file_explorer_replace import populate_dock
from test_file_explorer_target_scope import set_scope, select_paths


def condition(**kwargs):
    return {'field': 'content', 'operator': 'contains', 'value': 'needle', **kwargs}


SCOPES = [('brackets', '', '[needle]'), ('braces', '', '{needle}'),
          ('parentheses', '', '(needle)'), ('custom', 'begin,end', 'begin needle end'),
          ('tag', '', '<div>needle</div>'), ('specific-tag', 'div', '<div>needle</div>'),
          ('hierarchical', 'include div', '<div>needle</div>')]


@pytest.mark.parametrize('browse', [False, True])
@pytest.mark.parametrize('scope,param,body', SCOPES)
def test_scopes_use_shared_extraction_in_search_and_browse(tmp_path, monkeypatch, browse, scope, param, body):
    path = tmp_path / 'chosen.txt'
    path.write_text('outside ' + body)
    executor = core.UnifiedFileExplorerExecutor()
    calls = []
    original = shared.extract_scope_content
    def extract(*args, **kwargs):
        calls.append((args[1:3], kwargs['max_chars']))
        return original(*args, **kwargs)
    monkeypatch.setattr(shared, 'extract_scope_content', extract)
    options = dict(target_scope='file', conditions=[condition(scope_type=scope, scope_value=param)])
    if browse:
        result = executor.execute_browse(str(path), **options)
    else:
        result = executor.execute_search(str(path), content_query='needle', **options)
    assert [item.file_info.path for item in result['files']] == [str(path)]
    assert calls == [((scope, param), len(path.read_text()))]
    assert not result['stats']['errors']
    options['conditions'][0]['value'] = 'outside'
    method = executor.execute_browse if browse else executor.execute_search
    assert not method(str(path), **options)['files']


@pytest.mark.parametrize('operator,regex,value,text,expected', [
    ('contains', False, 'cat', 'cats hotdog', False),
    ('not contains', False, 'cat', 'cats hotdog', True),
    ('contains', True, 'cat|dog', 'cats hotdog', False),
    ('contains', True, 'cat|dog', 'DOG', True),
    ('starts with', False, 'cat', 'CAT dog', True),
    ('starts with', True, 'cat|dog', 'DOG cat', True),
    ('ends with', False, 'dog', 'cat DOG', True),
    ('ends with', True, 'cat|dog', 'hotdog catfish', False),
    ('ends with', True, 'cat|dog', 'cat dog\n', False),
])
def test_enriched_matching_reuses_condition_semantics(operator, regex, value, text, expected):
    obj = shared.Condition.from_mapping(dict(field='content', operator=operator, value=value,
                                            regex=regex, whole_word=True, case_sensitive=False))
    assert obj.matches('unused', content=text) == expected


@pytest.mark.parametrize('data', [
    condition(scope_type='unknown'), condition(scope_type=['brackets']),
    condition(scope_type='custom', scope_value='begin'),
    condition(scope_type='custom', scope_value=',end'),
    condition(scope_type='custom', scope_value='begin, '),
    condition(scope_type='specific-tag', scope_value=''),
    condition(scope_type='specific-tag', scope_value='('),
    condition(scope_type='hierarchical', scope_value=''),
    condition(scope_type='hierarchical', scope_value='invalid selector'),
    condition(scope_type='hierarchical', scope_value='include [', regex=True),
    condition(scope_type='hierarchical', scope_value='include (a)(b)', regex=True),
    condition(scope_type='specific-tag', scope_value='(div)'),
    condition(scope_type='brackets', scope_value=[]),
])
def test_invalid_scope_is_explicit_not_successful_empty_filter(tmp_path, data):
    path = tmp_path / 'chosen.txt'
    path.write_text('needle')
    result = core.UnifiedFileExplorerExecutor().execute_search(str(path), target_scope='file', conditions=[data])
    assert not result['files'] and 'Invalid conditions' in result['stats']['errors'][0]


@pytest.mark.parametrize('options', [{'whole_word': True}, {'operator': 'ends with'}])
def test_effective_wrapped_regex_validated_before_matching(options):
    with pytest.raises(re.error, match='global flags'):
        shared.Condition.from_mapping(condition(value='(?i)needle', regex=True, **options))


@pytest.mark.parametrize('key', ['value', 'scope_value'])
@pytest.mark.parametrize('value,valid', [('abcd', True), ('abcde', False),
                                       ('\u00e9\u00e9', True), ('\u00e9\u00e9x', False)])
def test_condition_utf8_limits(monkeypatch, key, value, valid):
    monkeypatch.setattr(shared, 'MAX_CONDITION_TEXT_BYTES', 4)
    data = condition()
    data['value'] = 'a'
    data[key] = value
    if valid:
        shared.Condition.from_mapping(data)
    else:
        with pytest.raises(ValueError, match='64 KiB'):
            shared.Condition.from_mapping(data)


@pytest.mark.parametrize('data', [{'field': 'size', 'operator': 'greater than', 'value': '2'},
                                 {'field': 'content', 'operator': 'regex', 'value': 'n.edle'},
                                 condition(use_regex=True, scope_type='none')])
def test_old_condition_mappings_defaults_and_aliases(qapp, data):
    grid = ConditionsGrid()
    try:
        grid.set_conditions([data], 'or')
        result = shared.Condition.from_mapping(grid.get_conditions()[0])
        expected = shared.Condition.from_mapping(data)
        assert (result.field, result.operator, result.value, result.use_regex,
                result.case_sensitive, result.whole_word) == (
                    expected.field, expected.operator, expected.value, expected.use_regex,
                    expected.case_sensitive, expected.whole_word)
        assert grid.get_logic_operator() == 'OR'
    finally:
        grid.deleteLater()


def test_hierarchical_output_limit_reuses_api_without_changing_unbounded_consumer(tmp_path):
    text = '<div>' + 'needle' * 30 + '</div>'
    selectors = 'include div, include div'
    assert shared.extract_scope_content(text, 'hierarchical', selectors).count('needle') == 60
    path = tmp_path / 'chosen.txt'
    path.write_text(text)
    result = core.UnifiedFileExplorerExecutor().execute_search(
        str(path), target_scope='file', conditions=[condition(scope_type='hierarchical', scope_value=selectors)])
    assert not result['files']
    assert 'scope output exceeds' in result['stats']['errors'][0]


def test_condition_count_and_shapes_are_bounded(monkeypatch, qapp):
    monkeypatch.setattr(shared, 'MAX_CONDITIONS', 2)
    executor = core.UnifiedFileExplorerExecutor()
    assert len(executor._prepare_conditions([condition()] * 2, 'AND')[0]) == 2
    for data in ([condition()] * 3, {}, 'invalid'):
        with pytest.raises(ValueError):
            executor._prepare_conditions(data, 'AND')
    grid = ConditionsGrid()
    try:
        with pytest.raises(ValueError):
            grid.set_conditions([condition()] * 3)
    finally:
        grid.deleteLater()


def test_grid_controls_round_trip_enabled_states_and_one_signal(qapp):
    grid = ConditionsGrid()
    try:
        changes = []
        grid.conditions_changed.connect(lambda values: changes.append(values))
        data = condition(scope_type='custom', scope_value='start,end', whole_word=True,
                         regex=True, case_sensitive=True)
        grid.set_conditions([data], 'OR')
        assert grid.get_conditions() == [data]
        assert changes == [[data]]
        row = grid.condition_rows[0]
        assert row['word'].isEnabled() and row['scope_value'].isEnabled()
        row['operator'].setCurrentIndex(row['operator'].findData('starts with'))
        assert not row['word'].isEnabled()
        row['field'].setCurrentIndex(row['field'].findData('size'))
        assert not row['scope'].isEnabled() and not row['scope_value'].isEnabled()
        assert not row['case'].isEnabled() and not row['regex'].isEnabled()
        assert grid.get_conditions()[0]['scope_type'] == ''
        row['field'].setCurrentIndex(row['field'].findData('content'))
        assert grid.get_conditions()[0]['scope_type'] == 'custom'
        row['scope'].setCurrentIndex(row['scope'].findData('brackets'))
        assert not row['scope_value'].isEnabled()
    finally:
        grid.deleteLater()


@pytest.mark.parametrize('width', [450, 900])
def test_grid_layout_does_not_force_wide_horizontal_row(qapp, qtbot, width):
    grid = ConditionsGrid()
    qtbot.addWidget(grid)
    grid.resize(width, 280)
    grid.show()
    qtbot.wait(10)
    assert grid.width() == width
    row = grid.condition_rows[0]
    for key in ('field', 'operator', 'value', 'case', 'regex', 'word', 'scope', 'scope_value'):
        widget = row[key]
        assert widget.geometry().right() < row['widget'].width()


def test_failed_preset_validation_leaves_panels_unchanged(tmp_path, docks):
    dock = docks()
    dock.conditions_grid.set_conditions([condition()])
    dock.filter_panel.ed_extensions.setText('txt')
    before = dock._get_current_filters()
    invalid = dict(extensions=['json'], conditions=[condition(scope_type='custom', scope_value='bad')])
    with pytest.raises(ValueError):
        dock._apply_filters_to_widgets(invalid)
    assert dock._get_current_filters() == before
    dock._apply_filters_to_widgets({'extensions': ['json']})
    assert dock.conditions_grid.get_conditions() == []
    assert dock.conditions_grid.get_logic_operator() == 'AND'
    assert dock.filter_panel.ed_extensions.text() == 'json'


def test_preset_manager_settings_and_json_round_trip(tmp_path, docks, monkeypatch):
    dock = docks()
    data = condition(scope_type='specific-tag', scope_value='div', whole_word=True,
                     regex=False, case_sensitive=True)
    dock.conditions_grid.set_conditions([data], 'OR')
    dock.filter_panel.ed_extensions.setText('txt')
    expected = dock._get_current_filters()
    manager = dock.preset_manager
    settings = QSettings('Clarify', manager.settings_group)
    settings.setValue('Presets/FE06-test', json.dumps(expected))
    manager.refresh()
    dock.conditions_grid.clear_conditions()
    manager.set_current_preset('FE06-test')
    assert dock._get_current_filters() == expected
    path = tmp_path / 'preset.json'
    monkeypatch.setattr(QFileDialog, 'getSaveFileName', lambda *a: (str(path), ''))
    manager.export_preset()
    assert json.loads(path.read_text()) == expected
    dock.conditions_grid.clear_conditions()
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *a: (str(path), ''))
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.No)
    manager.import_preset()
    assert dock._get_current_filters() == expected
    errors = []
    monkeypatch.setattr(QMessageBox, 'critical', lambda *a: errors.append(a[2]))
    settings.setValue('Presets/bad', json.dumps({'conditions': [condition(regex=True, value='[')]}))
    manager.refresh()
    manager.set_current_preset('bad')
    assert errors and dock._get_current_filters() == expected


@pytest.mark.parametrize('view', [0, 1])
@pytest.mark.parametrize('scope', ['file', 'selected', 'folder'])
def test_real_worker_enriched_condition_respects_exact_targets(tmp_path, docks, qtbot, qapp, monkeypatch,
                                                            view, scope):
    chosen, sibling = tmp_path / 'chosen.txt', tmp_path / 'sibling.txt'
    chosen.write_text('outside [needle]')
    sibling.write_text('outside [needle]')
    dock = docks()
    populate_dock(dock, [chosen, sibling])
    select_paths(dock, view, [chosen])
    set_scope(dock, scope)
    dock.ed_directory.setText(str(tmp_path if scope == 'folder' else chosen))
    dock.ed_exc.clear()
    dock.content_panel.set_query('needle')
    dock._user_manually_changed_view = True
    dock.conditions_grid.set_conditions([condition(scope_type='brackets', whole_word=True)])
    observed = []
    original = shared.extract_scope_content
    def extract(*args, **kwargs):
        observed.append(QThread.currentThread() != qapp.thread())
        return original(*args, **kwargs)
    monkeypatch.setattr(shared, 'extract_scope_content', extract)
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    expected = {str(chosen), str(sibling)} if scope == 'folder' else {str(chosen)}
    assert set(dock.last_search_results) == expected
    assert dock.results_stack.currentIndex() == view
    assert all(observed) and len(observed) == len(expected)
    assert dock.last_search_results[str(chosen)][0][:2] == (1, 9)


def test_relaxed_conditions_cannot_reuse_empty_incremental_cache(tmp_path, docks, qtbot):
    path = tmp_path / 'chosen.txt'
    path.write_text('outside [needle]')
    dock = docks()
    set_scope(dock, 'file')
    dock.ed_directory.setText(str(path))
    dock.ed_exc.clear()
    dock.content_panel.set_query('needle')
    dock.conditions_grid.set_conditions([condition(scope_type='brackets', value='outside')])
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert dock._last_content_search_universe['paths'] == []
    dock.conditions_grid.set_conditions([condition(scope_type='brackets')])
    assert dock._last_content_search_universe is None
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert list(dock.last_search_results) == [str(path)]


@pytest.mark.parametrize('action', ['resume', 'cancel', 'close'])
def test_condition_edit_while_paused_does_not_restore_stale_cache(tmp_path, docks, qtbot, monkeypatch, action):
    path = tmp_path / 'chosen.txt'
    path.write_text('[needle]')
    dock = docks()
    set_scope(dock, 'file')
    dock.ed_directory.setText(str(path))
    dock.ed_exc.clear()
    dock.content_panel.set_query('needle')
    dock.conditions_grid.set_conditions([condition(scope_type='brackets')])
    entered = threading.Event()
    original = dock.executor._matches_condition_objects
    def pause(*args, **kwargs):
        dock.executor.pause()
        entered.set()
        return original(*args, **kwargs)
    monkeypatch.setattr(dock.executor, '_matches_condition_objects', pause)
    dock._list_files()
    qtbot.waitUntil(entered.is_set, timeout=3000)
    dock.conditions_grid.condition_rows[0]['word'].setChecked(True)
    if action == 'resume':
        dock.executor.resume()
    elif action == 'cancel':
        dock._on_progress_canceled()
    else:
        dock.close()
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=3000)
    assert not dock._operation_running()
    assert dock._last_content_search_universe is None


def test_invalid_scope_does_not_launch_gui_worker(tmp_path, docks, monkeypatch):
    dock = docks()
    dock.ed_directory.setText(str(tmp_path))
    dock.content_panel.set_query('needle')
    grid = dock.conditions_grid
    grid.set_conditions([condition(scope_type='custom', scope_value='begin,end')])
    grid.condition_rows[0]['scope_value'].setText('bad')
    monkeypatch.setattr(dock, '_launch_operation', lambda *a: pytest.fail('worker'))
    errors = []
    monkeypatch.setattr(QMessageBox, 'critical', lambda *a: errors.append(a[2]))
    dock._list_files()
    assert errors and not dock._operation_running()
