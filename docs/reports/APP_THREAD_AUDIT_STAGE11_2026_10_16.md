# APP-THREAD-01 Stage 11 - InsertPanel result saving

Date: 2026-10-16

## Scope

This bounded stage audits the embedded `InsertPanel._save_results` path and its
shared `ResultsTree.export_to_text` consumer. It moves only immutable result
serialization and file IO off the Qt GUI thread. The file dialog, result-tree
extraction, widgets and final feedback remain on the GUI thread.

AI Processor Stages 6 through 10 and Search/Replace public behavior remain
unchanged. JSON Editor, TOON, WQXR, Editor UX, i18n and the legacy backlog are not
included.

## Defect proof and native failure

The original path called `ResultsTree.export_to_text()` and wrote the selected
file directly after the GUI file dialog. An instrumented regression failed
cleanly because both serialization and `open().write()` ran on `Qt mainThread`.
The guarded red run reached 194.2 MiB peak tree RSS without a resource trigger.

The first complete nine-test run of the provisional implementation then crashed
natively with signal 11 while two panels settled concurrent exports. The guard
reported exit `-11`, 194.8 MiB peak tree RSS and 8.1 seconds elapsed, with no RAM,
RSS, wall-time or pytest-timeout trigger. Work stopped immediately. No core dump
was retained by the system, so this report does not claim a native backtrace.

After explicit authorization to resume, the ownership audit found that the save
thread was parented to the panel and the worker was scheduled for deletion from
its own settlement signal before native thread settlement. This differed from
the project's stable operation pattern and could couple panel teardown to a
running native thread. The test was not blindly rerun before correcting those
lifetime risks.

## Implementation

- `ResultsTree.export_to_text()` keeps its synchronous public API and exact text
  format, delegating to one shared formatter also used by the worker plan.
- The GUI snapshots the result mapping into frozen tuples. No worker reads a Qt
  tree, widget or mutable results mapping.
- Exports permit at most 100,000 files, 50,000 matches, 4 KiB UTF-8 per path,
  1 MiB UTF-8 per snippet and 20 MiB of serialized output. Cheap character and
  count checks happen during the GUI snapshot; exact UTF-8 checks run in the
  worker with cooperative checkpoints.
- The worker writes a private temporary file in the destination directory and
  publishes it with `os.replace` only after complete serialization. Cancellation
  or IO failure removes the temporary and preserves an existing destination.
- Each panel owns at most one search or save operation; separate panels retain
  independent registered workers.
- Save threads are parentless and registered before worker affinity moves off the
  GUI thread. Worker deletion and UI settlement occur only through
  `QThread.finished`; close requests cancel cooperatively, suppress late feedback
  and never use `terminate()`.

## Validation

All tests used `.venv`, temporary HOME/settings, Qt offscreen, temporary files and
provider-free workers. `/tmp/clarify_guard.py` enforced system RAM below 85%,
process-tree RSS below 600 MiB and wall time below 180 seconds. Pytest used a
20-second timeout including fixtures. Every GUI module ran in a separate process.

| Module | Tests | Peak tree RSS MiB |
| --- | ---: | ---: |
| `tests/gui/test_insert_panel_result_save_lifecycle.py` | 9 | 196.1 |
| `tests/gui/test_insert_panel_lifecycle.py` | 9 | 199.4 |
| `tests/gui/test_insert_panel.py` | 26 | 241.6 |
| `tests/gui/test_ai_processor_result_save_lifecycle.py` | 9 | 208.6 |
| `tests/gui/test_search_replace_lifecycle.py` | 9 | 200.3 |
| `tests/gui/test_search_replace_replace_lifecycle.py` | 11 | 200.5 |
| `tests/test_results_tree_unicode_hierarchy.py` | 21 | 192.5 |
| `tests/gui/test_search_replace_panel.py` | 22 | 233.7 |
| `tests/test_save_results_feature.py` | 10 | 62.5 |

Total: 126 distinct focused tests passed. The formerly crashing two-panel case
also passed alone after the ownership correction at 194.6 MiB peak tree RSS. No
post-fix native crash, timeout or resource-guard abort occurred.

Python compilation, Pylint error-only checks, Black checks for the two new files
and `git diff --check` passed. Full-file Black was not applied to the two legacy
panels because it would create unrelated formatting churn.

## Remaining scope

`APP-THREAD-01` remains open because other synchronous consumers and workers
still require bounded audits. Cancellation is cooperative between serialized
lines; an individual bounded Python `TextIO.write` call cannot be interrupted in
its middle. This stage does not claim application-wide Qt lifecycle or external
CI/security gates resolved.
