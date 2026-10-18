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

## Draft Implementation

The uncommitted draft adds an immutable clipboard plan with the established
100,000-file, 50,000-match, 1 MiB-snippet and 20 MiB-output limits. Widget/model
snapshot and final `QApplication.clipboard()` publication stay on the GUI
thread; bounded formatting runs in a cooperative worker registered to the
existing owner gate. Cancellation, close and callback discard follow the
result-save lifecycle. Search/Replace and Insert retain the native thread until
`wait(0)` succeeds before scheduling deletion.

No feature commit was made because final validation found a blocking lifecycle
failure outside the new clipboard path.

## Validation Completed

Each GUI module ran in a separate process with temporary `HOME`, offscreen Qt,
RAM 85%, process-tree RSS 600 MiB, wall 180 s and pytest 20 s guards.

- New clipboard plan: 4 passed, peak 177.7 MiB.
- New Search/Replace clipboard lifecycle: 3 passed, peak 200.0 MiB.
- New Insert clipboard lifecycle: 1 passed, peak 194.6 MiB.
- New File Explorer clipboard lifecycle: 2 passed, peak 205.1 MiB.
- New AI Processor embedded contract: 1 passed, peak 199.8 MiB.
- Historical Search/Replace result save: 8 passed, peak 198.2 MiB.
- Historical Insert result save: 9 passed, peak 197.2 MiB.
- Historical File Explorer result save: 7 passed, peak 206.6 MiB.
- Historical ResultsTree hierarchy/Unicode: 21 passed, peak 193.4 MiB.
- Historical Search/Replace lifecycle: 9 passed, peak 201.8 MiB.

The 35 result-save and new clipboard tests passed. Including adjacent tree and
Search/Replace coverage, 65 distinct tests passed. No native crash, timeout,
RAM/RSS/wall abort or live provider/user-document access occurred.

## Blocking Failure

`tests/gui/test_insert_panel_lifecycle.py` passed its first five cases, then
failed `test_two_panels_have_independent_operations`. A queued
`ThreadManager._on_thread_finished()` attempted `wait(0)` on an already deleted
PySide6 `QThread`; teardown then found the stale registration and the remaining
three cases could not start. Peak RSS was 199.7 MiB and the guard did not abort.

This is a native ownership contract that Stage 15 must preserve. The run was not
retried and the implementation was not committed or pushed, as required by the
continuation stop condition.

## Required Resume

1. Start a separate bounded audit of `InsertPanel` search-thread ownership and
   `ThreadManager` registration order using the failing two-panel regression.
2. Retain the wrapper until both owner settlement and manager `wait(0)` complete;
   do not block the GUI and do not use `terminate()`.
3. Repeat the isolated Insert lifecycle module. Only after it passes, repeat all
   Stage 15 modules, static checks and the GDB lifecycle probe before committing.

