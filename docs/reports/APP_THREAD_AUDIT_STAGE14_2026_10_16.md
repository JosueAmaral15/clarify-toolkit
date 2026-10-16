# APP-THREAD-01 Stage 14 - File Explorer CSV export (incomplete)

Date: 2026-10-16
Status: stopped after native crash; root cause unresolved

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

## Experimental state

The work branch contains an incomplete experimental implementation and its
reproducer. It adds a frozen bounded CSV plan, atomic temporary-file publication,
cooperative cancellation and dock-lifecycle registration. The embedded table
button delegates to the dock while the manager's standalone fallback remains.
Limits are 100,000 rows, 16 columns, 1 MiB UTF-8 per cell, 20 MiB total and a
4 KiB output path.

The initial two-case post-edit check passed at 204.0 MiB peak RSS. This is not
sufficient validation and does not establish the implementation as safe.

## Native crash barrier

The expanded 12-case module passed its first five cases, then crashed during
`test_one_export_per_dock_and_independent_docks`. Python reported a segmentation
fault followed by abort while one worker was in `src/gui/csv_export.py:170` and
the GUI thread was settling feedback through
`FileExplorerDock._finish_csv_export`. The process exited 250; peak process-tree
RSS was 207.9 MiB and the resource guard reported no trigger.

Per the stage instruction, the test was not retried and no root-cause claim is
made. The implementation is incomplete, unpromoted and unsuitable for merge.
Stage 14 requires a fresh explicit authorization before any diagnostic rerun or
repair. `APP-THREAD-01` remains open.
