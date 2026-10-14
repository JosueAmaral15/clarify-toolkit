"""FE-PAR-05 independent queries, limits and real-thread Explorer regressions."""

import os
import threading
from types import SimpleNamespace

import pytest
import shiboken6
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QMessageBox

import src.core.file_explorer_executor as core
from src.core.multi_query import MultiQueryProcessor, split_multi_query
from src.gui.widgets.search_widgets import SearchOptionsPanel
from src.ui import thread_manager
from test_file_explorer_lifecycle import docks
from test_file_explorer_replace import populate_dock
from test_file_explorer_target_scope import set_scope, select_paths


def search(path, query='alpha\nbeta', executor=None, **options):
    return (executor or core.UnifiedFileExplorerExecutor()).execute_search(
        str(path), content_query=query, target_scope='file', search_options={'multi_query': True, **options}
    )


@pytest.mark.parametrize('newline', ['\n', '\r\n', '\r'])
def test_independent_queries_comments_duplicates_and_order(tmp_path, newline):
    path = tmp_path / 'target.txt'
    path.write_bytes(newline.join(['beta alpha', '', 'alpha beta']).encode())
    result = search(path, newline.join([' # comment', ' beta ', '', 'alpha', 'beta']))
    assert [(m.line, m.col) for m in result['files'][0].matches] == [(1, 0), (1, 5), (3, 0), (3, 6)]
    assert result['stats']['query_count'] == 2
    assert not result['stats']['partial']


@pytest.mark.parametrize('regex', [False, True])
def test_overlap_union_keeps_distinct_starts_and_combines_same_position(tmp_path, regex):
    path = tmp_path / 'target.txt'
    path.write_text('banana banana')
    query = 'ana\nnana\nana|nana\nana' if regex else 'ana\nnana\nana'
    result = search(path, query, regex=regex)
    assert [m.col for m in result['files'][0].matches] == [1, 2, 8, 9]
    assert result['stats']['total_matches'] == 4


@pytest.mark.parametrize('case,word,count', [(False, False, 4), (True, False, 3),
                                         (False, True, 2), (True, True, 1)])
def test_case_and_grouped_whole_word_alternation(tmp_path, case, word, count):
    path = tmp_path / 'target.txt'
    path.write_text('ALPHA beta xxalpha betaxx')
    result = search(path, 'alpha|beta\nalpha', regex=True, case_sensitive=case, whole_word=word)
    assert result['stats']['total_matches'] == count


def test_literal_metacharacters_and_escaped_comment_prefix(tmp_path):
    path = tmp_path / 'target.txt'
    path.write_text('[literal] #tag a+b')
    assert search(path, '[literal]\na+b')['stats']['total_matches'] == 2
    assert search(path, r'\#tag', regex=True)['files'][0].matches[0].col == 10


def test_text_regex_never_spans_target_lines_and_zero_width_is_bounded(tmp_path):
    path = tmp_path / 'target.txt'
    path.write_text('alpha\nbeta')
    assert search(path, r'alpha\s+beta' + '\nunused', regex=True)['stats']['total_matches'] == 0
    result = search(path, '^\n$', regex=True)
    assert [(m.line, m.col) for m in result['files'][0].matches] == [(1, 0), (1, 5), (2, 0), (2, 4)]


def test_unicode_columns_and_far_snippet(tmp_path):
    path = tmp_path / 'target.txt'
    path.write_text('\u00e9' * 300 + 'alpha beta')
    result = search(path)
    assert [m.col for m in result['files'][0].matches] == [300, 306]
    assert all('alpha' in m.snippet and len(m.snippet) <= core.MAX_SNIPPET_LENGTH
               for m in result['files'][0].matches)


@pytest.mark.parametrize('scope,expected', [('text', 1), ('binary', 1), ('both', 2)])
def test_all_content_scopes_preserve_text_positions_or_binary_byte_offsets(tmp_path, scope, expected):
    (tmp_path / 'text.txt').write_text('intro\nalpha beta')
    (tmp_path / 'raw.bin').write_bytes(b'\x00\xffalpha beta')
    result = core.UnifiedFileExplorerExecutor().execute_search(
        str(tmp_path), content_query='alpha\nbeta', search_options={'multi_query': True, 'content_scope': scope}
    )
    assert len(result['files']) == expected
    for item in result['files']:
        if item.file_info.name == 'raw.bin':
            assert [(m.line, m.col) for m in item.matches] == [(1, 2), (1, 8)]
            assert item.matches[0].snippet.startswith('bytes 2-7:')
        else:
            assert [(m.line, m.col) for m in item.matches] == [(2, 0), (2, 6)]
    assert not result['stats']['errors']


@pytest.mark.parametrize('query,options', [('', {}), (None, {}), (['alpha'], {}),
                                         (' # only\n \n', {}), ('alpha\n[', {'regex': True}),
                                         ('alpha', {'cross_line': True}),
                                         ('alpha', {'content_scope': 'invalid'}),
                                         (r'\u0061', {'regex': True, 'content_scope': 'both'}),
                                         ('\ud800', {}), ('\ud800', {'cross_line': True})])
def test_invalid_queries_fail_before_any_discovery(tmp_path, monkeypatch, query, options):
    monkeypatch.setattr(core.FileListExecutor, 'list_files', lambda *a, **kw: pytest.fail('traversal'))
    result = core.UnifiedFileExplorerExecutor().execute_search(
        str(tmp_path), content_query=query, search_options={'multi_query': True, **options}
    )
    assert result['files'] == []
    assert result['stats']['errors'] and result['stats']['partial']


@pytest.mark.parametrize('query,allowed', [('abcd', True), ('abcde', False),
                                         ('\u00e9\u00e9', True), ('\u00e9\u00e9x', False)])
def test_aggregate_utf8_query_limit(tmp_path, monkeypatch, query, allowed):
    monkeypatch.setattr(core, 'MAX_MULTI_QUERY_BYTES', 4)
    path = tmp_path / 'target.txt'
    path.write_text(query)
    result = search(path, query)
    assert bool(result['stats']['errors']) != allowed


def test_active_query_count_limit_includes_duplicate_lines(tmp_path, monkeypatch):
    monkeypatch.setattr(core, 'MAX_MULTI_QUERY_COUNT', 2)
    path = tmp_path / 'target.txt'
    path.write_text('alpha')
    assert not search(path, 'alpha\n# ignore\nalpha')['stats']['errors']
    assert search(path, 'alpha\nalpha\nalpha')['stats']['errors']


@pytest.mark.parametrize('binary', [False, True])
@pytest.mark.parametrize('size,allowed', [(8, True), (9, False)])
def test_file_limits_without_unbounded_reader(tmp_path, monkeypatch, binary, size, allowed):
    monkeypatch.setattr(core, 'MAX_MULTI_QUERY_FILE_BYTES', 8)
    monkeypatch.setattr(core, 'read_text', lambda *a: pytest.fail('unbounded reader'))
    path = tmp_path / 'target'
    path.write_bytes((b'\x00' if binary else b'a') + b'a' * (size - 1))
    result = search(path, 'a', content_scope='binary' if binary else 'text')
    assert bool(result['stats']['errors']) != allowed
    assert bool(result['files']) == allowed


def test_growth_read_is_not_prefix_truncation(tmp_path, monkeypatch):
    path = tmp_path / 'target.txt'
    path.write_text('a' * 100)
    monkeypatch.setattr(core, 'MAX_MULTI_QUERY_FILE_BYTES', 8)
    original = os.fstat
    monkeypatch.setattr(core.os, 'fstat', lambda fd: SimpleNamespace(st_size=0, st_mode=original(fd).st_mode))
    result = search(path, 'a')
    assert not result['files'] and '4 MiB limit' in result['stats']['errors'][0]


def test_cancellation_during_reader_closes_real_handle(tmp_path, monkeypatch):
    path = tmp_path / 'target.txt'
    path.write_bytes(b'a' * 70000)
    executor = core.UnifiedFileExplorerExecutor()
    calls = []
    original = os.fdopen
    def opened(*args, **kwargs):
        handle = original(*args, **kwargs)
        calls.append(handle)
        return handle
    monkeypatch.setattr(core.os, 'fdopen', opened)
    checks = []
    def checkpoint():
        checks.append(1)
        if len(checks) == 2:
            executor.cancel()
        return not executor._cancel
    monkeypatch.setattr(executor, 'checkpoint', checkpoint)
    assert executor._read_multi_query_content(str(path), False) is None
    assert len(calls) == 1 and calls[0].closed


@pytest.mark.parametrize('binary', [False, True])
def test_per_file_limit_counts_union_and_exact_budget_not_partial(tmp_path, monkeypatch, binary):
    monkeypatch.setattr(core, 'MAX_MULTI_QUERY_MATCHES', 2)
    path = tmp_path / 'target'
    prefix = b'\x00' if binary else b''
    path.write_bytes(prefix + b'a a')
    result = search(path, 'a\na.*', regex=True, content_scope='binary' if binary else 'text')
    assert result['stats']['total_matches'] == 2 and not result['stats']['partial']
    path.write_bytes(prefix + b'a a a')
    result = search(path, 'a\na.*', regex=True, content_scope='binary' if binary else 'text')
    assert result['stats']['total_matches'] == 2
    assert result['stats']['partial'] and result['stats']['match_limit_reached']


def test_global_budget_never_overshoots(tmp_path, monkeypatch):
    monkeypatch.setattr(core, 'MAX_TOTAL_MATCHES', 3)
    for name in ('one', 'two', 'three'):
        (tmp_path / name).write_text('a a')
    result = core.UnifiedFileExplorerExecutor().execute_search(
        str(tmp_path), content_query='a\na.*', search_options={'multi_query': True, 'regex': True}
    )
    assert result['stats']['total_matches'] == 3
    assert result['stats']['match_limit_reached'] and result['stats']['partial']


def test_cached_condition_content_obeys_byte_limit(tmp_path, monkeypatch):
    path = tmp_path / 'target.txt'
    path.write_text('a')
    monkeypatch.setattr(core, 'MAX_MULTI_QUERY_FILE_BYTES', 4)
    executor = core.UnifiedFileExplorerExecutor()
    def condition(path, objects, logic, cache):
        cache['text'] = '\u00e9' * 3
        return True
    monkeypatch.setattr(executor, '_matches_condition_objects', condition)
    result = search(path, 'a', executor=executor)
    assert result['stats']['errors'] and result['stats']['partial']


@pytest.mark.parametrize('view', [0, 1])
@pytest.mark.parametrize('scope', ['file', 'selected', 'folder'])
def test_real_worker_exact_scope_and_both_views(tmp_path, docks, qtbot, qapp, monkeypatch, view, scope):
    chosen, sibling = tmp_path / 'chosen.txt', tmp_path / 'sibling.txt'
    chosen.write_text('beta alpha')
    sibling.write_text('beta alpha')
    dock = docks()
    populate_dock(dock, [chosen, sibling])
    set_scope(dock, scope)
    select_paths(dock, view, [chosen])
    dock.ed_directory.setText(str(tmp_path if scope == 'folder' else chosen))
    dock.ed_exc.clear()
    dock.content_panel.set_query('alpha\nbeta')
    dock.search_options_panel.chk_multi_query.setChecked(True)
    dock._user_manually_changed_view = True
    observed = []
    original = dock.executor._search_multi_queries
    def capture(*args):
        observed.append(QThread.currentThread() != qapp.thread())
        return original(*args)
    monkeypatch.setattr(dock.executor, '_search_multi_queries', capture)
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    expected = {str(chosen), str(sibling)} if scope == 'folder' else {str(chosen)}
    assert set(dock.last_search_results) == expected
    assert all(observed) and len(observed) == len(expected)
    assert [m[:2] for m in dock.last_search_results[str(chosen)]] == [(1, 0), (1, 5)]
    assert dock.results_stack.currentIndex() == view


@pytest.mark.parametrize('action', ['resume', 'cancel', 'close', 'delete'])
@pytest.mark.parametrize('view', [0, 1])
def test_real_worker_pause_inside_union_then_settle(tmp_path, docks, qtbot, monkeypatch, action, view):
    path = tmp_path / 'target.txt'
    path.write_text('alpha beta')
    dock = docks()
    set_scope(dock, 'file')
    dock.results_stack.setCurrentIndex(view)
    dock._user_manually_changed_view = True
    dock.ed_directory.setText(str(path))
    dock.ed_exc.clear()
    dock.content_panel.set_query('alpha\nbeta')
    dock.search_options_panel.chk_multi_query.setChecked(True)
    entered = threading.Event()
    original = dock.executor._search_multi_queries
    def pause(*args):
        dock.executor.pause()
        entered.set()
        return original(*args)
    monkeypatch.setattr(dock.executor, '_search_multi_queries', pause)
    calls = []
    original_batch = dock._on_batch_ready
    def batch(*args):
        calls.append(1)
        return original_batch(*args)
    monkeypatch.setattr(dock, '_on_batch_ready', batch)
    dock._list_files()
    qtbot.waitUntil(entered.is_set, timeout=3000)
    qtbot.wait(30)
    assert dock._operation_running()
    if action == 'resume':
        dock.executor.resume()
    elif action == 'cancel':
        dock._on_progress_canceled()
    elif action == 'close':
        dock.close()
    else:
        dock.deleteLater()
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=3000)
    if shiboken6.isValid(dock):
        assert not dock._operation_running()
        assert bool(dock.last_search_results) == (action == 'resume')
        if action != 'resume':
            assert dock._last_content_search_universe is None
    if action in ('close', 'delete'):
        assert not calls
    if action == 'resume':
        assert calls


def test_mode_and_query_changes_invalidate_empty_cache(tmp_path, docks, qtbot):
    path = tmp_path / 'target.txt'
    path.write_text('alpha beta')
    dock = docks()
    set_scope(dock, 'file')
    dock.ed_directory.setText(str(path))
    dock.ed_exc.clear()
    dock.content_panel.set_query('alpha\nbeta')
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert dock._last_content_search_universe['paths'] == []
    dock.search_options_panel.chk_multi_query.setChecked(True)
    assert dock._last_content_search_universe is None
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert list(dock.last_search_results) == [str(path)]
    dock.content_panel.set_query('unseen\nother')
    assert dock._get_incremental_candidate_paths(str(tmp_path), 'unseen\nother', dock._snapshot_target()[-1]) is None
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert not dock.last_search_results
    assert dock._last_content_search_universe['content_query'] == 'unseen\nother'


def test_partial_results_are_visible_and_not_cached(tmp_path, docks, qtbot, monkeypatch):
    path = tmp_path / 'target.txt'
    path.write_text('alpha beta')
    monkeypatch.setattr(core, 'MAX_MULTI_QUERY_MATCHES', 1)
    dock = docks()
    set_scope(dock, 'file')
    dock.ed_directory.setText(str(path))
    dock.ed_exc.clear()
    dock.content_panel.set_query('alpha\nbeta')
    dock.search_options_panel.chk_multi_query.setChecked(True)
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert len(dock.last_search_results[str(path)]) == 1
    assert 'partial' in dock.results_status.toolTip()
    assert dock._last_content_search_universe is None


@pytest.mark.parametrize('query', ['', ' # only', 'alpha\n[', 'a' * 65537],
                         ids=['empty', 'comments', 'invalid-regex', 'oversized'])
def test_gui_validation_does_not_create_worker(tmp_path, docks, monkeypatch, query):
    dock = docks()
    dock.ed_directory.setText(str(tmp_path))
    dock.content_panel.set_query(query)
    dock.search_options_panel.set_options({'multi_query': True, 'regex': True})
    monkeypatch.setattr(dock, '_launch_operation', lambda *args: pytest.fail('worker'))
    errors = []
    monkeypatch.setattr(QMessageBox, 'critical', lambda *args: errors.append(args[2]))
    dock._list_files_smart()
    assert len(errors) == 1 and not dock._operation_running()


def test_gui_oversized_query_not_extracted_again_before_validation(tmp_path, docks, monkeypatch):
    dock = docks()
    dock.ed_directory.setText(str(tmp_path))
    dock.content_panel.set_query('a' * 65537)
    dock.search_options_panel.chk_multi_query.setChecked(True)
    monkeypatch.setattr(dock.content_panel, 'get_query', lambda: pytest.fail('oversized extraction'))
    dock._list_files_smart()
    assert not dock._operation_running()


def test_replacement_stays_rejected_in_core_and_gui(tmp_path, docks, monkeypatch):
    path = tmp_path / 'target.txt'
    path.write_text('alpha beta')
    executor = core.UnifiedFileExplorerExecutor()
    files = executor.execute_browse(str(tmp_path))['files']
    result = executor.execute_replace(files, 'alpha\nbeta', 'changed', search_options={'multi_query': True})
    assert result['errors'] and not result['files_modified']
    dock = docks()
    populate_dock(dock, [path])
    dock.content_panel.set_query('alpha\nbeta')
    dock.search_options_panel.chk_multi_query.setChecked(True)
    select_paths(dock, 0, [path])
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: pytest.fail('confirmation before mode guard'))
    dock._start_replace(True)
    assert path.read_text() == 'alpha beta'


def test_shared_legacy_processor_keeps_existing_fallback_and_parser_contract():
    assert split_multi_query(' alpha \n #ignore\n\nbeta ') == ['alpha', 'beta']
    processor = MultiQueryProcessor('[', use_regex=True)
    assert processor.get_query_count() == 1
    assert processor.search_in_text('[')[0][:2] == (1, 0)


@pytest.mark.skipif(not hasattr(os, 'mkfifo'), reason='POSIX special file')
def test_special_target_is_rejected_before_content_conditions(tmp_path, monkeypatch):
    path = tmp_path / 'special'
    os.mkfifo(path)
    executor = core.UnifiedFileExplorerExecutor()
    monkeypatch.setattr(executor, '_matches_condition_objects', lambda *a: pytest.fail('special-file read'))
    result = executor.execute_search(str(tmp_path), content_query='alpha\nbeta',
                                     search_options={'multi_query': True}, target_scope='selected',
                                     target_paths=[str(path)])
    assert result['stats']['partial'] and 'regular file' in result['stats']['errors'][0]


def test_error_limit_stops_remaining_files_with_explicit_partial(tmp_path, monkeypatch):
    monkeypatch.setattr(core, 'MAX_OPERATION_ERRORS', 2)
    monkeypatch.setattr(core, 'MAX_MULTI_QUERY_FILE_BYTES', 1)
    for name in ('one', 'two', 'three', 'four'):
        (tmp_path / name).write_text('alpha beta')
    result = core.UnifiedFileExplorerExecutor().execute_search(
        str(tmp_path), content_query='alpha\nbeta', search_options={'multi_query': True}
    )
    assert len(result['stats']['errors']) == 2
    assert result['stats']['partial']
    assert 'remaining files were not searched' in result['stats']['errors'][-1]


@pytest.mark.parametrize('suffix', [b'\x00binary', b'\xff'])
def test_late_binary_or_invalid_utf8_does_not_search_text_prefix(tmp_path, suffix):
    path = tmp_path / 'target.txt'
    path.write_bytes(b'alpha' + b'x' * core.TEXT_SAMPLE_BYTES + suffix)
    result = search(path, 'alpha')
    assert not result['files']
    assert result['stats']['errors'] and result['stats']['partial']


def test_prepared_cancellation_is_not_reset_by_multi_query_compilation(tmp_path):
    path = tmp_path / 'target.txt'
    path.write_text('alpha beta')
    executor = core.UnifiedFileExplorerExecutor()
    executor.prepare_operation()
    executor.cancel()
    result = executor.execute_search(str(path), content_query='alpha\nbeta', target_scope='file',
                                     search_options={'multi_query': True}, prepared=True)
    assert result['stats']['cancelled'] and result['stats']['partial']
    assert not result['files']


def test_options_round_trip_and_legacy_tooltip_key_preserved(qapp):
    panel = SearchOptionsPanel()
    try:
        panel.set_options({'multi_query': True, 'regex': True, 'content_scope': 'both'})
        panel.retranslateUi()
        assert panel.get_options()['multi_query'] and panel.get_options()['regex']
        assert panel.get_options()['content_scope'] == 'both'
        assert '128' in panel.chk_multi_query.toolTip()
        panel.chk_cross_line.setChecked(True)
        assert not panel.get_options()['multi_query']
    finally:
        panel.deleteLater()


def test_incremental_repeat_respects_exact_scope_and_options(tmp_path, docks, qtbot, monkeypatch):
    path = tmp_path / 'target.txt'
    path.write_text('alpha beta')
    dock = docks()
    dock.chk_reuse_previous.setChecked(True)
    set_scope(dock, 'file')
    dock.ed_directory.setText(str(path))
    dock.ed_exc.clear()
    dock.content_panel.set_query('alpha\nbeta')
    dock.search_options_panel.chk_multi_query.setChecked(True)
    requests = []
    original = dock.executor.execute_search
    def capture(*args, **kwargs):
        requests.append(dict(kwargs['filters']))
        return original(*args, **kwargs)
    monkeypatch.setattr(dock.executor, 'execute_search', capture)
    for _ in range(2):
        dock._list_files()
        qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert 'candidate_paths' not in requests[0]
    assert requests[1]['candidate_paths'] == [str(path)]
    dock.search_options_panel.chk_case.setChecked(True)
    assert dock._last_content_search_universe is None
