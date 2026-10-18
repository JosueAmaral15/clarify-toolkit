# APP-THREAD-01 Stage 16 Audit - 2026-10-18

## Scope

This stage audited shared `ResultsTree._copy_all_content` use by Search/Replace,
Insert, File Explorer and the AI Processor's embedded panels. It did not start
Editor UX, TOON, WQXR, i18n, dependency or legacy work. Only temporary test
files were opened; no provider or user document was accessed.

## Evidence Before Editing

- The shared context-menu action called `_copy_all_content()` directly on the
  GUI thread.
- That path synchronously performed existence/type/size checks, binary sampling,
  UTF-8 reads and output joining before publishing to `QApplication.clipboard()`.
- A maximum-content temporary sample confirmed `gui_thread=True` while reading
  and joining 2,097,152 content bytes. Cached local IO took about 6.6 ms, but the
  filesystem calls had no execution deadline.
- Search/Replace, Insert and File Explorer use the same ResultsTree. AI Processor
  embeds the Search/Replace and Insert panels and therefore must reuse their
  ownership rather than add another operation gate.

## Implementation

`MatchContentClipboardPlan` receives an immutable GUI-thread snapshot of exact
result paths. It enforces the existing 512 KiB/file and 2 MiB total-content
limits plus the shared 100,000-file, 4 KiB/path and 20 MiB path-snapshot bounds.
Workers read in 64 KiB chunks with cooperative checkpoints, preserve result
order and the established text/status format, and report binary, directory,
missing, oversized, total-limit, decode and IO skips separately.

Search/Replace, Insert and File Explorer register a content-copy handler on the
shared tree and launch it through their existing one-operation gate. Independent
owners remain concurrent. Widget/model snapshots, clipboard publication,
feedback and File Explorer logging stay on the GUI thread after native
`QThread.finished` plus `wait(0)` settlement. Close/cancel discards late results;
no path uses `terminate()`. Standalone ResultsTree keeps the bounded synchronous
fallback for compatibility.

## Validation

Each GUI module ran in a separate process with temporary `HOME`, offscreen Qt,
RAM 85%, process-tree RSS 600 MiB, wall 180 s and pytest 20 s guards.

- New content plan and owner integrations: 11 passed.
- ResultsTree and Stage 15 clipboard compatibility: 31 passed.
- Insert and Search/Replace search/replace lifecycle: 29 passed.
- Historical result-save paths: 24 passed.
- File Explorer CSV lifecycle: 12 passed.
- ThreadManager completion lifecycle: 12 passed.
- Broad File Explorer lifecycle: 36 passed.
- AI Processor lifecycle: 4 passed.

The matrix contains 159 distinct passing tests. Peak guarded process-tree RSS
outside GDB was 213.1 MiB.

The 12 completion cases passed under GDB with a 380.5 MiB internal peak and a
normal inferior exit. The first broad Explorer GDB pass stopped after five tests
because a 60 ms fixed heartbeat assertion observed one event instead of three;
there was no crash, Qt exception or guard abort, and the full module had passed
outside GDB. The isolated failing parameter then passed under GDB. The regression
was made deterministic by waiting up to 500 ms for the same three heartbeats
while still requiring the paused worker to produce no result. The complete
36-case Explorer module then passed under GDB with a normal inferior exit and a
385.8 MiB internal peak.

Compilation, Pylint errors-only for the five production modules and five new or
updated tests, focused Black and `git diff --check` passed. The historical broad
Explorer test retains its pre-existing PySide6/Shiboken dynamic-binding Pylint
false positives; runtime and GDB validation passed.

## Result And Remaining Scope

Stage 16 is complete. Application consumers no longer perform result-file reads,
binary detection or content serialization on the GUI thread. `APP-THREAD-01`
remains open for separately proven synchronous consumers; no unrelated backlog
item is completed by this stage.
