# APP-THREAD-01 - Stage 4 Search/Replace Search Lifecycle

Date: 2026-10-07

## Scope

This stage audited and repaired only the background search owned by
`SearchReplacePanel`. It does not complete APP-THREAD-01, change File Explorer
behavior or move the synchronous replace path off the GUI thread.

## Proven Defects

- A valid search reached duplicated error-handling code that referenced an
  exception variable outside its handler. Invalid regular expressions tried to
  emit nonexistent panel signals. All eight initial lifecycle regressions failed.
- The worker received the bound `self._iter_files` method and therefore read
  QWidget state from its worker thread.
- Global exclusive feature registration prevented two independent panels from
  searching concurrently, while cancel released panel state before native thread
  settlement and allowed overlap or late callbacks.
- There was no deferred tab/close contract, and emergency/app shutdown could
  invoke `QThread.terminate()` for Search/Replace work.
- AI Processor passed its historical settings-prefix string as the second
  constructor argument; the panel treated that value as a progress manager.
- `tests/gui/test_search_replace_panel.py` started a full `MainWindow` and looked
  for removed `main_window.search_panel` ownership before testing the panel.

## Changes

- Added an immutable file-discovery request and immutable condition transfer
  objects captured on the GUI thread. Worker-local `Condition` objects are built
  only after transfer, so no widget/model is touched by discovery.
- Registered one non-exclusive `FeatureType.SEARCH_REPLACE` operation per panel.
  Each panel still permits one operation; separate panels have independent
  workers, generation receivers and ownership.
- Search setup errors now remain local to the panel. Completion data is applied
  only after `QThread.finished`; cancellation, pause, deferred tab close and panel
  close remain cooperative and do not call `terminate()`.
- Added generation/discard checks, immutable completion metadata and deferred
  reference cleanup to reject stale callbacks. Search/Replace is protected in
  both emergency cleanup and application close handling.
- Preserved the historical settings-prefix constructor form and replaced the
  stale full-window panel fixture with a lightweight real panel.

## Validation

Every Qt module ran in its own offscreen process with temporary HOME/config,
system RAM 85%, process-tree RSS 600 MiB, wall 180 seconds and per-test 20-second
limits. No provider or user document was used.

- `tests/gui/test_search_replace_lifecycle.py`: 9 passed, peak 202.1 MiB.
- `tests/gui/test_search_replace_panel.py`: 22 passed, peak 235.0 MiB.
- `tests/gui/test_insert_panel_lifecycle.py`: 9 passed, peak 199.9 MiB.
- `tests/gui/test_insert_panel.py`: 26 passed, peak 242.3 MiB.
- `tests/test_thread_management_system.py`: 7 passed, peak 65.7 MiB.
- `tests/test_qt_completion_lifecycle.py`: 11 passed, peak 207.7 MiB.
- `tests/test_file_explorer_lifecycle.py`: 36 passed, peak 213.1 MiB.
- `tests/test_progress_system.py`: 18 passed, peak 62.6 MiB.
- Total: 138 focused tests passed; no native crash or guard abort occurred.

The first output collection for the completion module returned before its footer;
the process exited normally. A single explicit-session rerun captured the full
result above. Compileall, Pylint error checks, Black/isort for changed tests and
`git diff --check` passed.

## Non-gating Legacy Audit

`tests/test_panels_integration.py` was inspected separately: 2 tests passed and
15 failed without a native crash. It expects several removed Search/Replace and
Insert convenience APIs, uses the obsolete PySide signal form for `receivers()`,
and also exposes an existing JSON Editor call to missing
`InsertPanel.set_line_number()`. These failures predate and do not exercise the
Stage 4 lifecycle contract, so they were not counted as passing evidence or
silently rewritten in this bounded stage.

## Remaining Limits

- A blocking filesystem read or condition-content extraction cannot be
  interrupted mid-call; cancellation is honored at the next worker checkpoint.
- `SearchReplacePanel._do_replace` still performs file discovery, reads and writes
  synchronously on the GUI thread. It is the next concrete APP-THREAD candidate.
- Other tool workers, stale integration contracts and application-wide shutdown
  still require separate APP-THREAD-01 stages.
