# APP-THREAD-01 Stage 13 - FileExplorerDock result saving

Date: 2026-10-16

## Scope

This bounded stage audits `FileExplorerDock._save_results`. It moves only
bounded immutable result serialization and atomic file IO off the Qt GUI
thread. The file dialog, result-tree extraction, widgets, models and final user
feedback remain on the GUI thread.

File Explorer target scopes, both result views, extension/filter state, cache
identity and invalidation, operation lifecycle and bounded log remain unchanged.
AI Processor Stages 6 through 10 and panel result-save Stages 11 and 12 are
preserved. CSV export, JSON Editor, TOON, WQXR, Editor UX, i18n and the legacy
backlog are excluded.

## Contract audit and defect proof

Source imports and runtime class resolution proved that File Explorer imports
`ResultsTree` from `src.gui.panels`, re-exported from
`src.gui.panels.results_tree`. This is the same tree and text format used by
InsertPanel and SearchReplacePanel. The separate `src.gui.results_tree` module
is a legacy implementation and is not the consumer on this path. The shared
Stage 11 export plan is therefore contract-compatible; no duplicate control or
format was added.

The original path called `ResultsTree.export_to_text()` and `open().write()`
directly after the GUI file dialog. An instrumented regression failed cleanly
because both serialization and writing ran on `Qt mainThread`. The guarded red
run reached 201.5 MiB peak tree RSS without a native crash, timeout or resource
trigger.

## Implementation

- The GUI snapshots `get_matches_data()` once and creates the frozen shared
  `MatchResultExportPlan`. Workers never read a Qt tree, widget or mutable result
  mapping.
- Existing limits remain 100,000 files, 50,000 matches, 4 KiB UTF-8 per path,
  1 MiB UTF-8 per snippet and 20 MiB total serialized output.
- Serialization and IO run in `MatchResultExportWorker`. A private temporary in
  the destination directory is published with `os.replace` only after complete
  success; cancellation or error removes it and preserves an existing target.
- Search, browse, replace and save use the dock's existing one-operation gate.
  Separate docks retain independent registered workers. Save is not pausable,
  so its progress control exposes cancel but disables pause.
- Close and shutdown request cooperative cancellation, wait for
  `QThread.finished`, suppress late feedback and never call `terminate()`.
- Success, cancellation and failures update the bounded operational log and
  controls only after worker settlement on the GUI thread.

## Validation

All tests used `.venv`, temporary HOME/settings, Qt offscreen and temporary
files. `/tmp/clarify_guard.py` enforced system RAM below 85%, process-tree RSS
below 600 MiB and wall time below 180 seconds. Pytest used a 20-second timeout
including fixtures. Every GUI module ran in a separate process.

| Module | Tests | Peak tree RSS MiB |
| --- | ---: | ---: |
| `tests/gui/test_file_explorer_result_save_lifecycle.py` | 7 | 208.3 |
| `tests/test_file_explorer_lifecycle.py` | 36 | 213.0 |
| `tests/test_file_explorer_progress_cancel.py` | 3 | 201.3 |
| `tests/test_file_explorer_incremental_search.py` | 8 | 214.5 |
| `tests/test_file_explorer_replace.py` | 33 | 207.4 |
| `tests/test_results_tree_unicode_hierarchy.py` | 21 | 193.9 |
| `tests/gui/test_insert_panel_result_save_lifecycle.py` | 9 | 197.9 |
| `tests/gui/test_search_replace_result_save_lifecycle.py` | 8 | 198.9 |
| `tests/test_file_explorer_v2_9_117.py` | 18 | 224.6 |

Total: 143 distinct focused tests passed. They cover GUI/worker affinity,
runtime consumer identity, one operation per dock, two independent docks,
cancel, IO failure, atomic destination safety, close settlement, shutdown
registration rejection and preservation of scopes, views, filters, cache and
bounded log. No post-fix run had a native crash, timeout or resource-guard abort.

## Remaining scope

`APP-THREAD-01` remains open because other synchronous consumers and workers
still require bounded audits. `FileExplorerDock._export_tree_to_csv` is one
concrete candidate: it still extracts and writes all CSV rows synchronously and
must be audited independently against its format and table-export consumers.
The shared tree's clipboard-only `_copy_all` is also synchronous, but is outside
this result-save stage. This work does not claim application-wide Qt lifecycle
or unresolved external CI/security gates fixed.
