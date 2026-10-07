# APP-THREAD-01 - Stage 5 Search/Replace File Replacement

Date: 2026-10-07

## Scope

This stage audited and repaired only `SearchReplacePanel._do_replace`, the path
that changes files on disk. The AI Processor's separate in-memory signal consumer,
parent-tool ownership and other APP-THREAD work remain outside this bounded stage.

## Proven Defects

- Discovery, condition filtering, reads, replacement and writes all ran directly
  inside the GUI callback. Ten initial lifecycle regressions failed; the executor
  interception was never reached because no worker existed.
- Replace had no per-panel worker ownership, pause/cancel settlement, progress or
  deferred close. It could overlap conceptually with search and could not report
  cancellation without first returning from all synchronous I/O.
- The path had no file-count, input, output or match budgets. An empty query was
  accepted as a regular expression matching every position.
- Writes used direct UTF-8 truncation. They did not reject links, preserve metadata
  atomically or detect an external edit between read and write.
- Per-file exceptions were logged and then hidden behind an unconditional success
  dialog. The immutable external `replace_requested` signal contract is separate
  and did not need file-worker behavior.

## Changes

- Added a frozen `ReplaceFileRequest` and `SearchReplaceFileWorker`. Widget state is
  captured once on the GUI thread; discovery receives only immutable values.
- Reused `UnifiedFileExplorerExecutor.execute_replace` instead of duplicating file
  mutation rules. This retains its 4 MiB file/input/output bound, 1,000-file bound,
  10,000 matches per file, 50-error bound, text-only policy, atomic replacement,
  metadata preservation and stale-revision/link protection.
- Extended shared discovery with optional cooperative checkpoints. Pause and cancel
  wake through the executor's condition variable; one blocking filesystem read can
  still finish before the next checkpoint.
- Search and replace now share one operation slot per panel, while different panels
  register independent non-exclusive `SEARCH_REPLACE` workers. Controls and
  references are retained until `QThread.finished`.
- Added generation-owned progress, bounded error summaries, partial/cancelled result
  reporting, deferred panel/tab close and suppression of late dialogs. No path uses
  `QThread.terminate()`.
- Preserved `emit_replace_request()` for the AI Processor as a synchronous signal
  over its in-memory result widget; it does not start a file worker.

## Validation

Each Qt module ran in its own offscreen process with temporary HOME/config, system
RAM 85%, process-tree RSS 600 MiB, wall 180 seconds and per-test 20-second limits.
Only temporary files were modified; no provider or user document was used.

- `tests/gui/test_search_replace_replace_lifecycle.py`: 11 passed, peak 201.9 MiB.
- `tests/gui/test_search_replace_lifecycle.py`: 9 passed, peak 201.7 MiB.
- `tests/gui/test_search_replace_panel.py`: 22 passed, peak 235.3 MiB.
- `tests/test_file_explorer_replace.py`: 33 passed, peak 206.2 MiB.
- `tests/gui/test_insert_panel_lifecycle.py`: 9 passed, peak 200.5 MiB.
- `tests/test_thread_management_system.py`: 7 passed, peak 66.7 MiB.
- `tests/test_qt_completion_lifecycle.py`: 11 passed, peak 208.2 MiB.
- `tests/test_file_explorer_lifecycle.py`: 36 passed, peak 212.8 MiB.
- `tests/test_panels_integration.py -k ai_processor_has_panels`: 1 passed,
  16 deselected, peak 199.8 MiB.
- `tests/test_progress_system.py`: 18 passed, peak 62.7 MiB.
- Total: 157 focused tests passed; no native crash or guard abort occurred.

Before implementation, all 10 new regressions failed with peak 205.4 MiB and no
native crash. Compileall/AST, Pylint error and unused-import checks, Black/isort for
the new modules and `git diff --check` passed.

## Remaining Limits

- Cancellation cannot interrupt one active filesystem or condition-content read;
  it is honored immediately afterward.
- `AIProcessorDock` remains referenced when its parent tool tab is removed and does
  not propagate close settlement to embedded Search/Replace and Insert panels. This
  can leave hidden work active, although app shutdown still uses `ThreadManager`.
- The AI Processor's in-memory replacement handler still runs synchronously on the
  GUI thread. Its input bound and parent/child ownership need a separate audit.
- Other tool workers and application-wide ownership remain under APP-THREAD-01.
