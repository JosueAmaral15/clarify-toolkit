# APP-THREAD-01 Stage 14 - File Explorer CSV export

Date: 2026-10-16
Status: native lifetime race repaired; guarded validation passed

## Scope and contracts

This bounded audit covered only File Explorer CSV export. Source and consumer
inspection established two distinct contracts:

- Search view reads the shared panels `ResultsTree`, keeps translated
  File/Line/Column/Match headers, strips match snippets and reports match/file
  totals.
- Browse view reads the current visual order of the five-column
  `FileListTableManager`, keeps its established English header row and emits
  `files_exported` after success. Its embedded export button directly called the
  synchronous manager path and bypassed the dock operation gate.

No JSON Editor, TOON, WQXR, Editor UX, i18n or legacy work was included.

## Defect proof

An instrumented two-case regression proved that `csv.writer` and `open` both ran
on `Qt mainThread` for search and browse exports. The guarded red run failed with
the two expected assertions, used 204.3 MiB peak process-tree RSS and had no
native crash, timeout or resource trigger.

## Implementation

The work branch adds a frozen bounded CSV plan, atomic temporary-file
publication, cooperative cancellation and dock-lifecycle registration. The
embedded table button delegates to the dock while the manager's standalone
fallback remains. Limits are 100,000 rows, 16 columns, 1 MiB UTF-8 per cell,
20 MiB total and a 4 KiB output path.

The initial two-case post-edit check passed at 204.0 MiB peak RSS, before the
expanded matrix exposed the lifecycle defect below.

## Native crash evidence

The expanded 12-case module passed its first five cases, then crashed during
`test_one_export_per_dock_and_independent_docks`. Python reported a segmentation
fault followed by abort while one worker was in `src/gui/csv_export.py:170` and
the GUI thread was settling feedback through
`FileExplorerDock._finish_csv_export`. The process exited 250; peak process-tree
RSS was 207.9 MiB and the resource guard reported no trigger.

Per the stage instruction, the test was not retried and no root-cause claim is
made in the incomplete checkpoint. The preserved systemd core for PID 9657 was
later inspected after explicit repair authorization. It showed that SIGABRT was
secondary: one worker first received SIGSEGV while processing a Qt
`DeferredDelete` inside `QObject::~QObject`. The GUI thread then detected
`malloc(): unaligned tcache chunk detected` while updating a status label and
aborted. No OOM, MCE, EDAC, timeout or resource-guard event accompanied it.

## Root cause and repair

`QThread.finished` may be delivered while platform thread teardown and deferred
QObject deletion are not yet complete. The GUI-owned completion receivers could
therefore remove `ThreadInfo` and dock references while the Python-owned worker
was still being destroyed in its affinity thread. Two workers settling together
made that ownership race visible.

The repair keeps ownership until actual native exit without blocking the GUI:

- `ThreadManager._on_thread_finished()` now polls `QThread.wait(0)`. Its
  GUI-owned receiver schedules a one-millisecond event-loop retry while teardown
  remains pending, retaining the worker and cancellation callback.
- `FileExplorerDock._finish_operation()` does not apply feedback or release its
  worker/thread references until the same zero-time poll succeeds.
- `_cleanup_worker_thread()` refuses early cleanup for every File Explorer
  operation, not only CSV export.
- A deterministic regression holds a native thread inside its `finished` signal
  and proves that the registry continues owning the worker until real exit.

The installed PySide6, Qt and Shiboken versions remain 6.9.3 and are internally
consistent. No dependency upgrade was mixed into this repair. PySide 6.11.1's
PYSIDE-3288 wrong-thread QObject deletion safeguard remains a separate possible
hardening step, not evidence required for this local fix.

## Validation

Every GUI module ran in a separate guarded process with temporary settings. No
automatic retry loop was used.

| Check | Result | Peak tree RSS |
| --- | --- | --- |
| New native-exit ownership regression | 1 passed | 183.2 MiB |
| Formerly crashing two-dock CSV case, GDB | 1 passed | 377.4 MiB |
| Complete Stage 14 CSV lifecycle module, GDB | 12 passed | 383.5 MiB |
| Shared completion/GC module, GDB | 12 passed | 382.5 MiB |
| Shared ThreadManager module | 7 passed | 66.4 MiB |
| Stage 13 File Explorer result-save module | 7 passed | 207.9 MiB |
| Stage 12 Search/Replace result-save module | 8 passed | 198.3 MiB |
| Historical File Explorer lifecycle module, GDB | 36 passed | 387.6 MiB |

This is 82 distinct passing tests plus the focused duplicate checkpoints. Python
compilation, Pylint error-only on production files, focused Black for the new
test and `git diff --check` passed. The two touched production files retain
pre-existing broad Black drift; no unrelated formatting rewrite was applied.

Stage 14 is complete on this isolated branch. `APP-THREAD-01` remains open for
other bounded consumers and workers; this evidence does not justify a general
claim that every historical Qt crash is fixed.
