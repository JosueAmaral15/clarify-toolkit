# File Explorer: Cooperative Lifecycle Stage

Date: 2026-09-28
Branch: `COM-d6670c61-7bfa-4c1d-9edd-f26746140d8c`
Base: implementation checkpoint `584709e`, followed by dispatch journal `c5bd62c`.
Scope: **FE-PAR-07 only**, in the approved finite FE-PAR-01..08 batch.
The [first-stage report](FILE_EXPLORER_PARITY_IMPLEMENTATION_2026_09_28.md)
remains a historical record of FE-PAR-01/02, not the latest pending count.

## Delivered

- Search, browse and replacement enter a Qt-bound worker slot with a copied
  request. Tests verify that execution is outside the GUI thread.
- A thread-safe condition blocks at cooperative checkpoints without polling.
  Resume wakes the worker; Cancel clears pause and wakes it as well. Controls
  reset before dispatch, never inside a prepared nested browse/search call.
- Checkpoints cover directory traversal, metadata conversion, file/line/match
  loops, condition evaluation, replacement preparation, pre-commit and batches.
  Shared listing retains noncyclic directory links, rejects ancestor cycles and
  keeps its existing public API with optional checkpoint arguments.
- One operation per dock includes startup and pending settlement. Separate docks
  can operate independently. Existing feature-exclusive ThreadManager defaults
  are preserved; Explorer opts into per-dock ownership explicitly.
- GUI-affine receivers are scoped to an operation generation. Cancel/close
  discards further progress and batches; terminal results are handled only after
  the native thread stops. Warnings do not trigger terminal-error cleanup.
- The fixed-width progress dialog has a pause/resume icon and tooltip. Cancel
  disables it. The dialog remains owned until settlement and is then deleted.
  Direct bar updates avoid modal QProgressDialog.setValue event-loop reentrancy.
- Normal dock, tab, dialog and parent closure cancels asynchronously, suppresses
  completion dialogs/history and retries closure after settlement. Deferred
  deletion lets Qt destroy the receiver, detaches the registered thread from
  the dying dock, and deletes the thread only after it has stopped.
- Worker quit uses a direct, thread-safe QThread connection, so application
  shutdown can wait without requiring the GUI to deliver a queued quit call.
  Cancelled-but-live threads stay visible in active counts and shutdown waits.
  Explorer threads are never force-terminated; rejected exit restores registration.
- Cancellation during an atomic write lets that file finish and prevents the
  next file from being changed. Cancelling after a result signal but before
  settlement still marks cancellation, preserving completed replacement counts.

## Validation

Serial subprocesses used isolated HOME/settings/logs, Qt offscreen, 15/20-second
pytest timeouts and `/tmp/clarify_guard.py`. Guard limits: system RAM 85%,
validation process-tree RSS 600 MiB, wall time 180 seconds, core dumps disabled.
No provider, credentials, real user document or running user app was used.

| Final Test Set | Passed | Duration | Peak Process-Tree RSS |
| --- | --- | --- | --- |
| Explorer regressions plus 36 new lifecycle cases | 196 | 11.52 s | 237.5 MiB |
| Shared conditions, AND/OR, checkboxes and scopes | 52 | 0.76 s | 73.5 MiB |
| Editor layout/header/hidden files and Explorer-to-editor flows | 21 | 6.23 s | 244.8 MiB |
| Existing ThreadManager compatibility | 7 | 0.19 s | 65.6 MiB |

**276 distinct tests passed**, not whole-project/E2E or production certification.
`tests/test_file_explorer_lifecycle.py` exercises native affinity, GUI timer responsiveness
while paused, cancellation at startup/during pause/after queued completion,
atomic commits during cancellation and destruction, both views, failures,
warnings, rejected registration/close, two docks, tab/parent/deferred closure,
stale receivers and ten repeated operations. Qt workers, threads, receivers and
progress dialogs are destroyed and registry/widget counts return to baseline
in that repeated test. This is scoped leak evidence, not a global leak guarantee.

An offscreen progress capture was visually inspected: pause state, resume icon
and Cancel fit without overlap. It does not establish native desktop/theme UX.
Initial tests exposed a missing test-only search snapshot and an actual
DeferredDelete filtering flaw; both were corrected before the final runs.
AST parsing of eight production files plus the new test and diff checks passed.
Focused Pylint uses PySide6 extension support and dynamic connect/disconnect
members; its first attempt reported only the Qt disconnect inference warning.
The final eight-module error check passed (exit 0, peak 422.9 MiB, jobs=1).

## Limits And Next Stage

Pause/cancel is cooperative, not an interruption of a regex call or blocking OS
I/O already in progress. An atomic commit is intentionally not interrupted.
Ordinary text search still has existing full-read/list-collection behavior;
FE-PAR-04 is responsible for bounded cross-line inputs/results. Test guards are
not a new global memory cap for the application. No multi-file rollback was added.

Monitor 0.9.0 remains active for this finite batch. Hooks show current activity;
schema/integrity, five hooks, native queue and existing automation/native controls
are healthy. Doctor still returns error for the failed reply-observer service.
No restart, migration, control change, GUI input or secret-file access occurred.
The received FE07 marker confirms processing of the preceding dispatch.
Dry-run of the exact worker/session FE03 continuation passed; one real detached
native dispatch follows the local commit. Dispatch initiation alone does not
prove delivery, and uncertainty must never cause a retry.

Remaining approved items: **FE-PAR-03, 04, 05, 06 and 08**. Next is explicit target
scope (03), on a fresh COM-UUID branch from this stage's checkpoint. The 30 earlier
backlog items are outside automatic continuation; total open count is **35**.
No push or main/develop promotion while CI/security gates remain unresolved.
`example.py` and unrelated work are excluded from this checkpoint.
