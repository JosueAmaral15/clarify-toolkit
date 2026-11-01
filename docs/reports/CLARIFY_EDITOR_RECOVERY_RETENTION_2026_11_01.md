# Clarify Editor Recovery Retention Evidence (2026-11-01)

## Scope

This bounded stage completed only `CE-RECOVERY-RETENTION-30D-01`. It did not
change recovery quotas, original files, temporary notes, File Searcher, default
appearance, settings reset, or any legacy task.

## Reproduced defects

- `src/editor_recovery.py` used a 24-hour default.
- `EditorDock` independently used another literal 24-hour default.
- Cleanup silently removed expired, corrupt, over-count, and over-total
  snapshots, so `Recover Unsaved...` could only report an apparently empty
  store.
- The first lifecycle validation exposed two compatibility regressions in the
  new implementation: `list_with_report()` bypassed consumers that intercept
  the public `list()` API, and an I/O failure opened a blocking warning dialog.

## Delivered behavior

- New profiles use one shared 720-hour (30-day) default.
- Existing `recovery_retention_hours` values remain authoritative within the
  supported 1-to-720-hour range.
- `RecoveryPruneReport` reports expired, invalid, over-count, and over-total
  removals without storing document content.
- An explicit recovery request distinguishes a genuinely empty store, cleanup
  reasons, snapshots already represented by the current session, and I/O or
  lock failures.
- The public `list()` contract remains compatible; `list_with_report()` adds
  diagnostics without bypassing existing consumers.
- Transient I/O failures do not classify and delete a snapshot as corrupt, and
  they report through the non-blocking status surface.
- The existing private atomic storage and limits of 2 MiB/document,
  20 documents, and 20 MiB total remain unchanged.

## Validation

All tests ran serially through `scripts/diagnostics/qt_lifecycle_probe.py` with
temporary HOME, system RAM 85%, process-tree RSS 600 MiB, wall 180 seconds and
pytest timeout 20 seconds:

- `editor-recovery-store`: 42 passed; peak tree RSS 81.4 MiB.
- `editor-recovery-retention`: 5 passed; peak tree RSS 204.3 MiB.
- `editor-recovery-lifecycle`: 53 passed; peak tree RSS 220.5 MiB.
- `editor-recovery-reopen`: 5 passed; peak tree RSS 209.9 MiB.

The final recovery set is 105 distinct tests. Another 10 translation-catalog
tests passed. No final run had a native crash, timeout, or resource-guard abort.
Python compilation, seven JSON catalog parses, focused Pylint-E with the known
PySide dynamic-member suppressions, and `git diff --check` also passed.

`example.py` remained untracked and byte-identical at SHA-256
`058053d87c818d699cde0f00d670bca0e1c6ad857caa9758ea6a556d7c64fcee`.
