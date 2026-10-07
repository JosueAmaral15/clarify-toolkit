# APP-THREAD-01 - Stage 2 Extraction Lifecycle

Date: 2026-10-07

## Scope

This stage audited and repaired the extraction worker owned by
`UnifiedTextToJsonDock` (Format Converter). The application-wide threading epic
remains open.

## Proven Defects

- `QThread.started` invoked extraction through a Python lambda. The first guarded
  regression captured `ExtractionWorker.execute_extraction()` and `read_text()` on
  the main Qt thread, so large extraction work could freeze the GUI despite the
  presence of a `QThread`.
- Cancellation blocked worker signals, waited up to five seconds on the GUI thread,
  then called `QThread.terminate()`. References could be cleared while native work
  was still active.
- The extraction thread was not registered globally, so application shutdown could
  miss it. Closing the tool tab also had no deferred-settlement contract.
- Directory discovery accumulated an unbounded path list before extraction.

## Changes

- Added a configured zero-argument `@Slot` on `ExtractionWorker`; the bound QObject
  slot is connected directly to `QThread.started`, preserving worker affinity.
- Added thread-safe cooperative cancellation with checkpoints before/after text
  processing, during directory discovery, and around each file read/extraction.
- Added a 100,000-file discovery limit with an explicit error instead of unbounded
  path accumulation.
- Registered each dock operation as `FeatureType.TEXT_EXTRACTOR`; only one operation
  may run per dock, while independent docks retain separate identities.
- Native completion now owns cleanup. Cancel, dock close, tab close and application
  close never call `terminate()` or block the GUI waiting for settlement.
- Reused existing translated status keys instead of adding new catalog asymmetry.

## Validation

Every Qt module ran in a separate offscreen process with temporary HOME/config,
RAM 85%, process-tree RSS 600 MiB, wall 180 seconds and pytest 20-second guards.

- `tests/gui/test_unified_extraction_lifecycle.py`: 8 passed, peak 201.7 MiB.
- `tests/gui/test_extractor_output_controls.py`: 2 passed, peak 198.7 MiB.
- `tests/gui/test_unified_text_to_json_editor_switch.py`: 2 passed, peak 198.3 MiB.
- `tests/gui/test_unified_text_search_replace.py`: 4 passed, peak 198.4 MiB.
- `tests/test_thread_management_system.py`: 7 passed, peak 66.5 MiB.
- `tests/test_qt_completion_lifecycle.py`: 11 passed, peak 207.5 MiB.
- `tests/test_file_explorer_lifecycle.py`: 36 passed, peak 213.1 MiB.
- Total: 70 focused tests passed after the fix.

The first pre-fix lifecycle run timed out during its third test at 197.6 MiB. Its
Python stack proved that `read_text()` was executing in `MainThread`; there was no
native crash or memory guard abort. After replacing the lambda with the worker slot,
all isolated runs above passed.

## Remaining Limits

- Cancellation cannot preempt an individual blocking filesystem read or one
  `AdvancedExtractor.process_text()` call; it takes effect immediately afterward.
- Other legacy workers and synchronous GUI I/O remain unaudited. In particular,
  emergency termination remains available for feature types that do not yet have a
  cooperative lifecycle contract.
- `APP-THREAD-01` therefore remains open and requires additional bounded stages.
