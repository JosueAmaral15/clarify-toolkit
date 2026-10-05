# Qt Completion Investigation - 2026-09-29

Status: **OPEN. A demonstrated registration race is fixed locally; the native
crash is not resolved. No commit, push, promotion or automated continuation.**

## Theme/MainWindow Follow-up - 2026-10-05

The separate system-theme/MainWindow path was retested under the same temporary
HOME/settings/logs, offscreen Qt, RAM85%, treeRSS600MiB and wall120s guards.
Ten simple-widget cycles (`dark -> light -> system`) passed with zero remaining
widgets and peak treeRSS62.6MiB. Three full MainWindow recreation cycles then
passed with zero remaining/top-level widgets and peak208.8MiB.

That first full run exposed a deterministic Qt warning rather than a crash:
`AA_UseDesktopOpenGL` was set after QApplication construction by
`AccessibilityManager.enable_screen_reader_support()`. The real entry point
already sets the application attribute before constructing QApplication. The
late call neither enables AT-SPI nor satisfies Qt's ordering requirement, so the
accessibility hook now preserves its API without mutating global Qt attributes.
A regression asserts that the warning is not emitted after QApplication exists.

After the repair,24 accessibility tests,14 ThemeManager tests and65 diagnostic
probe tests passed in isolated guarded processes. A second three-cycle full
MainWindow run passed, emitted no `AA_UseDesktopOpenGL` warning, retained zero
widgets after every cycle and peaked at209.2MiB. Pylint-E, py_compile and
`git diff --check` passed for this change. Black still reports pre-existing
formatting drift in the two legacy accessibility files; no broad formatting
rewrite was applied.

This removes one invalid late Qt mutation and provides stronger non-reproduction
evidence. It does not identify the historical suite-order segfault or the FE05
native fault, so this investigation and its TASKS checkbox remain open.

## Scope

User requested another attempt to solve the historical Qt crash. Base `eeeefca`,
branch `COM-52f97c90-b745-4dbf-b9e0-883dabf9069c`. Focus: FE05 native signal11 in
cross-line pause/resume completion. The older MainWindow/system-theme crash is
separate and was not reproduced or fixed here. No legacy features were started.

All diagnostic children used temporary HOME/settings/logs, offscreen Qt, system
RAM85%, treeRSS600MiB, wall180s and pytest20s including fixtures. Core dumps were
disabled. No full MainWindow construction, real documents, live providers,
package upgrades or monitor dispatch. `example.py` remains untouched/untracked.

## Findings And Local Patch

- Archived FE05 Python trace reaches `_finish_operation`, `_on_search_finished`
  and `_update_statistics`. It contains no native backtrace or proven cause.
  Logging appearing in a trace is not evidence that logging caused the crash.
- A real-thread regression demonstrated a different lifecycle bug: after
  explicit settlement and reuse of a public thread ID, the old queued
  `QThread.finished` callback removed the new, still-running registration and
  could release its feature lock. The test failed before the patch.
- Automatic cleanup now carries a unique registration token, for Qt and the
  existing non-PySide fallback. Explicit one-argument cleanup remains compatible
  with current consumers. Tokens also distinguish restarts of the same QThread.
- Deferred receiver destruction worked in the ownership probe. An initial
  assertion requiring a Qt parent was unsupported and removed; this was not a
  demonstrated premature-deletion bug. No speculative reparenting was applied.
- Existing progress-bar updates already avoid modal QProgressDialog.setValue
  reentrancy. No replacement workaround was added.

## Evidence

Runtime: Python3.12.10, PySide6/Qt6.9.3, Linux offscreen. RSS figures include GDB
where used. Diagnostic passes do not establish stability of ordinary execution.

| Run | Result | Peak tree RSS |
| --- | --- | --- |
| Current multi-query + cross-line, GDB, before patch | 118 passed | 383.1MiB |
| Final FE05 checkpoint d924e4b, four-module order, GDB | 223 passed | 388.0MiB |
| Final new completion/ownership/GC/pause module, GDB | 11 passed | 376.8MiB |
| Existing shared ThreadManager module, ordinary isolated | 7 passed | 65.9MiB |
| Final mocked diagnostic launcher module (no GUI startup) | 20 passed | 63.9MiB |
| Existing lifecycle module, ordinary isolated, after patch | ABORT signal6, exit134 | 205.8MiB |
| Atomic-commit cancellation cases alone, GDB | 3 passed | 373.2MiB |
| Lifecycle module, GDB, tcache disabled/allocator perturbation | 36 passed | 382.7MiB |
| Lifecycle module, GDB, normal allocator | 36 passed | 381.4MiB |
| Lifecycle module, temporary native signal tracer/GC thresholds50,5,5 | 36 passed | 215.7MiB |

The checkpoint run follows the historical module order but has 223 cases,
not the original failing214-case transient state. It is not an exact replay.
The explicitly bounded combined runs were crash diagnostics, not general GUI
validation; the normal validation runner uses one GUI module per process.

The ordinary isolated abort occurred after 11 completed cases, during
`test_cancel_during_atomic_commit_finishes_current_file_only`, with Python frames:

```text
ExplorerOperationReceiver.thread_finished
FileExplorerDock._finish_operation
FileExplorerDock._append_operation_log -> operation_log.appendPlainText
```

No RAM/RSS/wall guard fired. These are Python frames, not a C++ cause or proof of
the same FE05 signal11 defect. The serial runner stopped immediately: later
cross-line, multi-query and target-scope modules were not run after the patch.
Only explicitly targeted crash-capture experiments followed; all passed, so no
native backtrace was captured. Neither the token patch nor diagnostic passes
justify declaring the native fault fixed. Regression/causality remains unknown.

The last temporary tracer was compiled locally outside the repository, used
only in one child and did not alter the application or installed environment.
The read-only detached historical worktree was clean and removed afterwards.
Final checks: Pylint-E on the two production/diagnostic files, AST parsing on all
four changed Python files, Black on the three new/updated diagnostic-test files,
and `git diff --check` passed. These are not full-suite or promotion evidence.

## Repeatable Diagnostic

Existing probe now supports a single test module with optional installed GDB:

```bash
.venv/bin/python scripts/diagnostics/qt_lifecycle_probe.py --mode completion --gdb
.venv/bin/python scripts/diagnostics/qt_lifecycle_probe.py --mode explorer-lifecycle --gdb
```

Run serially, only when deliberately investigating the fault. No automatic retry
loop. Each test mode preserves native exits, bounds resources and refuses direct
`--child` execution. GDB initialization/network symbol downloads are disabled.
The default window/theme probes retain their existing120s limit. Mocked launcher
tests cover commands, private environment, RAM
preflight, missing GDB, native exit mapping and prevention of guard bypass.

## Remaining Work

1. Capture a native failure/fingerprint for the ordinary isolated abort before
   attributing it to GC, log widgets, allocator corruption or worker disposal.
2. Establish the fault on the unmodified base and validate any proposed fix in
   both ordinary execution and guarded diagnostics. MainWindow/theme remains a
   separate unresolved investigation.
3. Retest affected Explorer/shared consumers and CE recovery only after the
   native safety barrier is addressed. No broad suite or continuation now.

Upstream6.11.1 release notes mention wrong-thread QObject GC deletion handling
(PYSIDE-3288) and patched slot receiver crashes (PYSIDE-3307). These are hypotheses,
not attribution or approval to upgrade the installed6.9.3 environment.
[Primary Qt release notes](https://doc.qt.io/qtforpython-6/release_notes/pyside6_release_notes.html).

TASKS.md retains30 open legacy/stability/security/CI/integration items; the native
investigation is still open, with no duplicate checkbox or completion claim.
