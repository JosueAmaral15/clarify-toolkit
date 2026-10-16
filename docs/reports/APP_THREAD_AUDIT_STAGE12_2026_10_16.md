# APP-THREAD-01 Stage 12 - SearchReplacePanel result saving

Date: 2026-10-16

## Scope

This bounded stage audits `SearchReplacePanel._save_results` and its shared
`src.gui.panels.results_tree.ResultsTree` consumer. It moves only bounded
immutable result serialization and atomic file IO off the Qt GUI thread. The
file dialog, result-tree extraction, widgets and final feedback remain on the
GUI thread.

Search and file-replacement behavior, AI Processor Stages 6 through 10 and
InsertPanel Stage 11 remain unchanged. File Explorer is not included. JSON
Editor, TOON, WQXR, Editor UX, i18n and the legacy backlog are also excluded.

Stage 13 correction: later source and runtime inspection proved that File
Explorer imports the same `src.gui.panels.results_tree.ResultsTree`; the separate
`src.gui.results_tree` module is not the consumer on this path.

## Defect proof

The original path called `ResultsTree.export_to_text()` and `open().write()`
directly after the GUI file dialog. An instrumented regression failed cleanly
because serialization ran on `Qt mainThread`. The guarded red run reached
195.6 MiB peak tree RSS without a native crash, timeout or resource trigger.

Source-consumer inspection confirmed that this panels ResultsTree format is
shared with InsertPanel, while File Explorer imports another tree class. The
existing synchronous `export_to_text()` API and text format therefore remain
unchanged.

## Implementation

- The GUI extracts the result mapping once and snapshots it through the frozen
  Stage 11 `MatchResultExportPlan`. No worker reads a Qt tree, widget or mutable
  results mapping.
- The shared limits remain 100,000 files, 50,000 matches, 4 KiB UTF-8 per path,
  1 MiB UTF-8 per snippet and 20 MiB of serialized output. Exact UTF-8 checks
  execute in the worker with cooperative checkpoints.
- Serialization uses a private temporary file in the destination directory and
  publishes with `os.replace` only after complete success. Cancellation or IO
  failure removes the temporary and preserves an existing destination.
- Search, file replacement and result saving share one operation gate per panel.
  A second command cancels or declines the current operation according to the
  panel's established behavior; separate panels retain independent workers.
- Result-save threads are parentless, registered before worker affinity moves,
  and settle through `QThread.finished`. Tab, parent and widget close paths request
  cooperative cancellation, suppress late feedback and never call `terminate()`.

## Validation

All tests used `.venv`, temporary HOME/settings, Qt offscreen and temporary
files. `/tmp/clarify_guard.py` enforced system RAM below 85%, process-tree RSS
below 600 MiB and wall time below 180 seconds. Pytest used a 20-second timeout
including fixtures. Every GUI module ran in a separate process.

The temporary guard wrapper had been removed before the first post-edit command,
so that command exited before starting pytest or Qt. The equivalent wrapper was
recreated and all reported runs below used it successfully.

| Module | Tests | Peak tree RSS MiB |
| --- | ---: | ---: |
| `tests/gui/test_search_replace_result_save_lifecycle.py` | 8 | 198.7 |
| `tests/gui/test_search_replace_lifecycle.py` | 9 | 202.6 |
| `tests/gui/test_search_replace_replace_lifecycle.py` | 11 | 202.9 |
| `tests/gui/test_search_replace_panel.py` | 22 | 235.9 |
| `tests/gui/test_insert_panel_result_save_lifecycle.py` | 9 | 197.9 |
| `tests/test_results_tree_unicode_hierarchy.py` | 21 | 193.7 |
| `tests/test_save_results_feature.py` | 10 | 62.5 |

Total: 90 distinct focused tests passed. They cover GUI/worker affinity, one
operation per panel, two independent panels, cancellation, atomic destination
safety, IO errors, shutdown registration rejection, empty/cancelled input and
tab-close settlement. No executed post-fix test had a native crash, timeout or
resource-guard abort.

Python compilation, Pylint error-only checks, Black checks for the new test and
`git diff --check` passed. Full-file Black was not applied to the legacy panel
because it would create unrelated formatting churn.

## Remaining scope

`APP-THREAD-01` remains open because other synchronous consumers and workers
still require bounded audits. The File Explorer result-save path is one concrete
candidate; Stage 13 subsequently audited it and proved the shared ResultsTree
contract. This stage does not claim application-wide Qt lifecycle or external
CI/security gates resolved.
