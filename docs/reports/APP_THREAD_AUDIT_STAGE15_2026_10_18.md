# APP-THREAD-01 Stage 15 Audit - 2026-10-18

## Scope

This stage audited shared `ResultsTree._copy_all` use by Search/Replace,
Insert, File Explorer and the AI Processor's embedded panels. It did not start
Editor UX, TOON, WQXR, i18n, dependency or legacy work.

## Evidence Before Editing

- `_copy_all()` called `format_match_results()` and joined every result on the
  GUI thread before accessing the clipboard.
- A bounded 1,000-file/50,000-match sample produced about 9.4 million
  characters and spent about 66 ms in formatting alone.
- Search/Replace and Insert own independent operation gates; File Explorer owns
  a per-dock gate. AI Processor consumes the same trees through its embedded
  Search/Replace and Insert panels.

## Implementation

The shared immutable clipboard plan uses the established 100,000-file,
50,000-match, 1 MiB-snippet and 20 MiB-output limits. Widget/model snapshots and
final `QApplication.clipboard()` publication stay on the GUI thread; bounded
formatting runs in a cooperative worker registered to the existing owner gate.
Cancellation, close and callback discard follow the result-save lifecycle.

Search/Replace, Insert and File Explorer allow one operation per owner while
independent instances remain concurrent. AI Processor keeps using its embedded
Search/Replace and Insert ownership instead of adding a duplicate gate.

## Blocking Failure Investigation And Repair

The first validation stopped after `tests/gui/test_insert_panel_lifecycle.py`
failed its two-panel case. `ThreadManager._on_thread_finished()` attempted
`wait(0)` on an already deleted PySide6 `QThread`, leaving a stale registration.

The defect was an integration regression between earlier stages:

- Stage 3 still created Insert search threads as `QThread(self)` and connected
  `QThread.finished` directly to `QThread.deleteLater`.
- Stage 14 correctly changed `ThreadManager` to retain ownership until
  `wait(0)` confirms native/platform teardown.
- The old owner-side deletion could therefore destroy the Qt wrapper before the
  manager's new settlement callback completed. Two concurrent panels made the
  ordering reproducible.

Insert search now uses a parentless thread, retains its explicit references,
polls `wait(0)` through `QTimer` without blocking and schedules deletion only
from confirmed cleanup. The analogous Search/Replace search and file-replace
paths received the same correction because they had the same premature
`finished -> deleteLater` contract. No path uses `terminate()`.

## Validation Completed

Each GUI module ran in a separate process with temporary `HOME`, offscreen Qt,
RAM 85%, process-tree RSS 600 MiB, wall 180 s and pytest 20 s guards.

- New clipboard plan and owner integrations: 11 passed, peak 206.0 MiB.
- Insert search lifecycle, including the former blocker: 9 passed, peak
  199.9 MiB.
- Search/Replace search and file-replace lifecycle: 20 passed, peak 203.8 MiB.
- Historical result-save paths: 24 passed, peak 207.9 MiB.
- File Explorer CSV and broad lifecycle: 48 passed, peak 212.9 MiB.
- ThreadManager completion lifecycle: 12 passed, peak 208.6 MiB.
- ResultsTree hierarchy/Unicode: 21 passed, peak 193.2 MiB.
- AI Processor parent/embedded lifecycle: 4 passed, peak 210.2 MiB.

The final matrix contains 149 distinct passing tests. The 12 completion tests
and 36 broad Explorer lifecycle tests were also repeated under GDB; both
inferiors exited normally, with process-tree peaks of 382.6 MiB and 387.2 MiB.
There was no native crash, Qt event-loop exception, timeout, RAM/RSS/wall guard
abort or access to live providers and user documents.

Compilation, Pylint errors-only and `git diff --check` passed. Black was applied
only to the five new test files; the large production modules retain their
pre-existing formatting to avoid unrelated churn.

## Result And Remaining Scope

Stage 15 is complete. `ResultsTree._copy_all` no longer performs bounded result
formatting on the GUI thread for application consumers, clipboard access remains
GUI-only and all owners preserve safe native settlement. `APP-THREAD-01` remains
open for separate audits of other synchronous consumers; `Copy All Content` is a
concrete next candidate because it still performs bounded filesystem reads on
the GUI thread.

