# Clarify Editor Recovery Retention - Partial Evidence (2026-11-01)

## Scope

This bounded stage addresses only `CE-RECOVERY-RETENTION-30D-01`. It does not
change recovery quotas, original files, temporary notes, File Searcher, default
appearance, settings reset, or any legacy task.

## Reproduction

- `src/editor_recovery.py` used a 24-hour default.
- `EditorDock` independently used another literal 24-hour default.
- Recovery cleanup silently removed expired, corrupt, over-count, and
  over-total snapshots, so `Recover Unsaved...` could only report an apparently
  empty store.
- A regression test reproduced the incorrect default: expected 720 hours,
  observed 24 hours.

## Implemented checkpoint

- New profiles use one shared 720-hour (30-day) default.
- Existing `recovery_retention_hours` values remain authoritative within the
  already supported 1-to-720-hour range.
- `RecoveryPruneReport` reports expired, invalid, over-count, and over-total
  removals without storing document content.
- An explicit recovery request distinguishes a genuinely empty store, cleanup
  reasons, snapshots already represented by the current session, and I/O or
  lock failures.
- Transient I/O failures no longer cause a snapshot to be treated as corrupt
  and deleted.
- The existing 2 MiB/document, 20-document, and 20 MiB total limits remain
  unchanged.

## Validation evidence

- Initial guarded store suite: 41 passed, peak tree RSS 91.0 MiB, no native
  crash, timeout, or guard abort. This run preceded the final I/O-propagation
  hardening and therefore is not claimed as final-suite approval.
- Final Python compilation passed for every changed Python module.
- All seven translation catalogs parsed successfully.
- Focused Pylint error checks passed with PySide6 dynamic extensions enabled.
- `git diff --check` passed.
- `example.py` remained untracked and byte-identical at SHA-256
  `058053d87c818d699cde0f00d670bca0e1c6ad857caa9758ea6a556d7c64fcee`.

## Unresolved validation barrier

The isolated GUI module was started serially under the required guard, but the
guard stopped it before test execution when global system RAM reached 85%.
Process-tree RSS was only 111.5 MiB; there was no SIGSEGV. The task remains open
in `docs/TASKS.md` until the final store suite, the new GUI module, and the
existing recovery lifecycle/reopen regressions can run safely and serially.

No default branch was promoted, and this checkpoint is not a completed-task
claim.
