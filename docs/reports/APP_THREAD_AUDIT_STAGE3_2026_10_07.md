# APP-THREAD-01 - Stage 3 Insert Search Lifecycle

Date: 2026-10-07

## Scope

This stage audited and repaired the background search owned by `InsertPanel`.
It does not complete the application-wide threading epic or change the File
Explorer/Search-Replace workspace contract.

## Proven Defects

- Search could not start: condition rows contain nine controls, but the launch
  path unpacked each row as three values. The error path also referenced signals
  that `InsertPanel` does not define.
- The worker received `self._iter_files`, so discovery read QWidget state from
  the worker thread instead of using an input captured on the GUI thread.
- Insert searches were not registered in `ThreadManager`; application shutdown
  could miss them and the emergency path could terminate them unsafely.
- Cancel immediately marked the panel idle and re-enabled controls before native
  settlement, allowing overlap and late callbacks.
- Pause/cancel used unsynchronized booleans and polling sleep. Discovery was
  accumulated without a file-count bound or an exception-to-settlement path.
- Embedded AI Processor and JSON Editor consumers still passed their historical
  settings-prefix string as the second constructor argument, which the newer
  signature could mistake for a progress manager.

## Changes

- Added an immutable search request captured on the GUI thread. Its pure file
  iterator is the only discovery callback used by the worker.
- Registered one `FeatureType.INSERT` operation per panel with non-exclusive
  feature registration, allowing independent panels while preventing overlap in
  the same panel.
- Added a GUI-owned generation receiver, cancellation/result suppression and
  deferred tab/close actions. Controls and references are released only after
  `QThread.finished`.
- Replaced pause/cancel booleans with `threading.Event`, made cancellation wake a
  paused worker and added a 100,000-file discovery limit with explicit errors.
- Protected Insert workers from `ThreadManager.force_cleanup()` and application
  force-close. Preserved the historical settings-prefix constructor form.

## Validation

Each Qt module ran in its own offscreen process with temporary HOME/config,
system RAM 85%, process-tree RSS 600 MiB, wall 180 seconds and per-test 20-second
limits. No provider or user document was used.

- `tests/gui/test_insert_panel_lifecycle.py`: 9 passed, final peak 200.6 MiB.
- `tests/gui/test_insert_panel.py`: 26 passed, final peak 242.6 MiB.
- `tests/test_thread_management_system.py`: 7 passed, peak 66.5 MiB.
- `tests/test_qt_completion_lifecycle.py`: 11 passed, peak 207.8 MiB.
- `tests/test_file_explorer_lifecycle.py`: 36 passed, peak 216.0 MiB.
- Total: 89 focused tests passed; no native crash or guard abort occurred.

AST/compileall, Pylint error checks and `git diff --check` passed. The new test
module passes Black and isort. Existing production modules retain pre-existing
Black/isort drift and were not globally reformatted.

`tests/gui/test_search_replace_panel.py` was also attempted but is stale: its
fixture expects removed `MainWindow.search_panel` ownership and fails before it
exercises `SearchWorker`. It is not counted as passing evidence or as a regression
caused by this stage.

## Remaining Limits

- A single blocking filesystem read or condition-content extraction cannot be
  interrupted mid-call; cancellation is honored immediately afterward.
- Search/Replace has its own ownership and stale-test problems and remains outside
  this bounded stage.
- Other legacy workers, synchronous GUI I/O, independent-tool concurrency and
  application-wide shutdown still require separate APP-THREAD-01 stages.
