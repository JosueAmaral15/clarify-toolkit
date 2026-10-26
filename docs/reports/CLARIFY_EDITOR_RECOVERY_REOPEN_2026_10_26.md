# Clarify Editor Recovery Reopen - 2026-10-26

## Scope

This bounded stage implements `CE-RECOVERY-REOPEN-01`. It reuses the existing
`UnsavedRecoveryStore` and recovery lifecycle. It does not change temporary-note
semantics, F1 shortcuts, File Explorer, `APP-THREAD-01`, broader i18n or legacy
work.

## Proven Gap

The existing lifecycle safely persisted dirty saved buffers and Untitled
buffers across the required close routes. Folder sessions also reopened dirty
saved buffers inside their canonical root. A new Editor instance did not,
however, surface pending Untitled or out-of-folder snapshots automatically;
recovery required the user to discover and open the modal File menu action.

A guarded pre-edit regression failed on the absent `recovery_offer` attribute
at 201.2 MiB. It exited normally without a native crash or guard abort.

## Implementation

The Editor now shows one non-modal startup bar when recoverable snapshots remain.
It offers explicit Recover, Discard and Cancel actions while leaving the
workspace usable. Cancel only dismisses the offer for that Editor instance; the
snapshot remains available on a later instance.

Pending snapshots are filtered against recovery IDs already restored by the
canonical folder session or represented by active tabs. This prevents duplicate
tabs while preserving root isolation. Recovery continues through the existing
bounded restorer and always opens a detached unsaved copy; it never writes to
the original file. A changed, removed, non-text or otherwise unavailable
reference remains stored and produces an honest failure count.

Discard applies only to pending snapshots and reports per-item failures without
hiding the surviving offer. The existing private atomic store remains the only
recovery backend, with limits of 2 MiB per document, 20 documents and 20 MiB
total. Existing close handling still stops timers, watchers and connections and
rejects late callbacks.

## Validation

Each Qt module ran in its own offscreen process with temporary HOME, disabled
core dumps, pytest timeout 20 seconds, system RAM 85%, process-tree RSS 600 MiB
and wall 180 second guards.

- `tests/gui/test_editor_recovery_reopen.py`: 5 passed, peak 207.3 MiB.
- `tests/gui/test_editor_recovery_lifecycle.py`: 53 passed, peak 219.0 MiB.
- `tests/test_editor_recovery.py`: 39 passed, peak 63.3 MiB.
- `tests/gui/test_editor_priority_stage5_sessions.py`: 12 passed, peak 215.6 MiB.
- `tests/gui/test_editor_priority_stage5_notes.py`: 5 passed, peak 203.6 MiB.
- `tests/gui/test_editor_priority_stage1.py`: 6 passed, peak 209.8 MiB.
- `tests/gui/test_editor_priority_stage3.py`: 8 passed, peak 199.9 MiB.
- `tests/gui/test_editor_priority_stage4_tabs.py`: 8 passed, peak 210.0 MiB.
- `tests/gui/test_editor_dock.py`: 69 passed, peak 226.8 MiB.
- `tests/gui/test_editor_layout.py`: 20 passed, peak 251.6 MiB.
- `tests/gui/test_editor_status_info.py`: 9 passed, peak 211.0 MiB.
- `tests/gui/test_editor_quick_toolbar.py`: 8 passed, peak 226.6 MiB.
- `tests/gui/test_tool_dock_toggle.py`: 10 passed, peak 202.8 MiB.

Total: 252 distinct passing tests. No native crash, timeout or guard abort
occurred. Compilation, Pylint errors-only, scoped Black, JSON parsing and
`git diff --check` passed.

## Boundary

The startup offer handles unsaved-document recovery only. Temporary notes keep
their separate persisted identity and lifecycle. Automatic conversion of a
recovered copy back into its former source file remains intentionally excluded;
the user must choose Save or Save As, preserving the no-overwrite contract.
