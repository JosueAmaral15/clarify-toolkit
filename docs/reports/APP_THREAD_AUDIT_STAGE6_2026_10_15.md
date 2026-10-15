# APP-THREAD-01 - Stage 6 AI Processor Ownership and Qt Lifecycle

Date: 2026-10-15

## Scope

This stage audited and repaired AI Processor worker ownership, parent-tool close
settlement and its embedded Search/Replace and Insert operations. It also resolved
the native Qt teardown crash exposed by the required lifecycle validation. File
discovery, advanced-condition filtering, in-memory replacement and other tools
remain outside this bounded stage.

## Proven Defects

- AI processing was not registered in `ThreadManager`; application shutdown could
  not account for it and emergency cleanup did not protect it from termination.
- A dock could start without explicit generation-owned settlement. Results and
  errors were applied before the native `QThread.finished` ownership boundary.
- Removing the parent tool tab did not wait for AI work or embedded Search/Replace
  and Insert operations. Hidden work and late callbacks could outlive the tab.
- Two independent AI Processor docks had no registry evidence of independent
  ownership, while a dock had no explicit one-operation gate.
- The existing Search/Replace lifecycle suite reproduced a native `SIGSEGV` only
  after preceding replacement tests. Under `gdb`, the worker thread was inside
  `QObject::~QObject` while the GUI thread destroyed and waited in `QThread::~QThread`.
  Both search and replace used a native thread parented to the panel and also
  scheduled that thread for `deleteLater`, creating competing ownership paths.

## Changes

- Registered each AI Processor worker under a stable per-dock identifier and
  non-exclusive `AI_FILE_PROCESSOR` feature. One dock permits one operation while
  separate docks keep independent workers.
- Added generation-owned pending result/error state. Progress and completion are
  rejected after cancellation/close; visible result handling occurs only after
  native thread settlement.
- Parent tab and widget closure now request cooperative cancellation, suppress late
  callbacks and defer removal until the AI worker and both embedded panels settle.
  Search/Replace and Insert expose only bounded ownership/shutdown methods; they do
  not independently close their containing dock. Once settled, tab removal also
  schedules the closed dock for destruction instead of retaining a hidden widget.
- Protected AI Processor work from emergency `terminate()` cleanup.
- Removed QObject parent ownership from Search/Replace native threads. Explicit
  panel and registry references retain them until `finished`, after which GUI-thread
  `deleteLater` owns destruction. This removes the proven panel-teardown race.

## Validation

Each Qt module ran in its own offscreen process with a temporary HOME, system RAM
85%, process-tree RSS 600 MiB, wall 180 seconds and per-test 20-second limits. Tests
used temporary files and provider-free workers; no user document or live provider
was accessed.

- `tests/gui/test_ai_processor_lifecycle.py`: 4 passed, peak 206.8 MiB.
- `tests/gui/test_search_replace_lifecycle.py`: 9 passed, peak 200.3 MiB.
- `tests/gui/test_search_replace_replace_lifecycle.py`: 11 passed in three separate
  post-fix processes (33 total), maximum peak 200.6 MiB.
- `tests/gui/test_insert_panel_lifecycle.py`: 9 passed, peak 197.6 MiB.
- `tests/test_thread_management_system.py`: 7 passed, peak 65.7 MiB.
- `tests/test_qt_completion_lifecycle.py`: 11 passed, peak 205.0 MiB.
- `tests/gui/test_ai_processor_ollama.py`: 1 passed, peak 197.4 MiB.
- `tests/test_panels_integration.py -k test_ai_processor_has_panels`: 1 passed,
  16 deselected, peak 197.9 MiB.
- Total: 53 distinct focused tests and 75 post-fix passing executions. No native
  crash, timeout or guard abort occurred after the ownership correction.

Before the fix, the full replacement module crashed reproducibly after three
passing cases. The isolated fourth case passed under `gdb`; the ordered module then
captured the native destructor race above at 399.6 MiB. Pylint error checks,
`py_compile`, Black for the new test and `git diff --check` passed.

## Remaining Limits

- One active provider request cannot be interrupted mid-call. Cancellation is
  honored by the worker at its next cooperative checkpoint.
- AI Processor file discovery and advanced-condition filtering still run before
  worker start on the GUI thread and need bounded immutable planning.
- The AI Processor in-memory replacement consumer remains synchronous and needs an
  independent input-bound and GUI-latency audit.
- Other tool workers and application-wide ownership remain under APP-THREAD-01.
