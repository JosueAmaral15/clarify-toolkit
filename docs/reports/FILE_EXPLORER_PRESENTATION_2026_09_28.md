# File Explorer Presentation - FE-PAR-08 (2026-09-28)

## Scope And Checkpoint

FINAL item in the approved finite FE-PAR/Editor queue only. Base FE06 checkpoint
7353fc7 plus dispatch journal09e6952 verified; incoming FE08 marker confirms
processing of that one-shot continuation, not a reason to resend it. Fresh branch:
COM-31276ed6-c7bd-4919-b03d-ec7d2076d144. No legacy work, push or promotion.

## Implementation

- Reuse SearchReplacePanel.set_editor_fonts and existing ContentQueryPanel/ReplacePanel
  set_font APIs. Lazy Explorer copies the active Search/Replace font, or uses the
  same Qt FixedFont fallback. FontChange/ApplicationFontChange retain monospace
  family while updating the shared application/accessibility size. Query, replacement
  and log use that font; no second font control or settings/config storage. This
  reuses the existing font mechanism, not an invented monospace preference toggle.
- Read-only QPlainTextEdit log in a click-expanded CollapsibleSection. Qt retains
  only200 blocks; each event is sliced before normalization to512 characters and
  embedded line/paragraph/NUL separators become spaces. Plain text, no HTML, undo
  history, secondary Python list, global logger subscription, timer or disk log.
  Logs start, per-file search progress, diagnostics, finish/error/cancel summaries;
  replacement summaries count modified files. Entries survive automatic post-replace
  refresh but disappear with the dock; document recovery storage is unrelated.
  Closing discards updates through the existing Qt-owned generation receiver.
- Existing filter header shows Extensions Off/On/All even collapsed. Enabled with
  an empty list honestly means all extensions. The existing checkbox is reused;
  the redundant group checkbox is removed in Explorer only. File List retains its
  own checkable shared panel. No hover expansion or duplicate filter control.
- Effective extensions remain empty while disabled; extensions_text preserves the
  inactive draft separately for presets. Restore applies the boolean and field
  enabled state, Clear unchecks and disables it. Legacy presets without the flag
  infer activation from a nonempty list; explicit false remains authoritative.
  Validate types, list count/aggregate length and32767 UTF-16 field-unit limit
  before mutating widgets or joining oversized lists. Search/Replace presets and
  FE06 conditions/AND-OR/extraction limits remain unchanged.
- Extension activation/list are part of target cache identity and changes invalidate
  the incremental universe, including while paused. Table-side extension comparison
  now matches the shared executor's lower-case/dot normalization. Exact targets,
  both views, query modes, budgets and one-operation lifecycle are preserved.
- CE recovery limits remain2 MiB/document,20 documents,20 MiB total, with bounded
  saved references. No real document or source origin was modified by this stage.

## Validation

Python3.12.10/PySide6/Qt6.9.3 in .venv. Each module ran in a separate serial
process with temporary HOME/settings/logs and offscreen Qt. No full MainWindow
startup fixtures, live providers or real user documents. Shared consumers use
lightweight real Qt containers, not mocked font/filter implementations.

Guard: system RAM85%, tree RSS600 MiB, wall180s, core dumps disabled. Pytest20s
includes setup/teardown. Only the validation process group can be killed by the
guard; no other worker/service is targeted. Command pattern:

```sh
.venv/bin/python /tmp/clarify_guard.py .venv/bin/python -m pytest MODULE -q \\
  --timeout=20 --timeout-method=thread -o timeout_func_only=false
```

| Module | Passed | Seconds | Peak tree RSS MiB |
| --- | ---: | ---: | ---: |
| test_file_explorer_presentation | 43 | 8.16 | 214.6 |
| test_file_explorer_enriched_conditions | 67 | 5.51 | 211.6 |
| test_file_explorer_conditions | 60 | 3.92 | 199.2 |
| test_file_explorer_multi_query | 70 | 8.68 | 210.4 |
| test_file_explorer_cross_line | 48 | 5.48 | 208.9 |
| test_file_explorer_target_scope | 69 | 7.56 | 209.3 |
| test_file_explorer_lifecycle | 36 | 7.57 | 211.7 |
| test_file_explorer | 35 | 0.44 | 76.0 |
| test_file_explorer_replace | 33 | 3.78 | 204.2 |
| test_file_explorer_content_scope | 6 | 3.46 | 183.1 |
| test_file_explorer_regex_coherence | 5 | 3.50 | 197.9 |
| test_file_explorer_incremental_search | 5 | 3.43 | 201.5 |
| test_file_explorer_top_options_and_globs | 4 | 3.57 | 204.9 |
| test_file_explorer_advanced_size_filters | 7 | 3.73 | 207.9 |
| test_file_explorer_table_refresh | 2 | 3.49 | 199.7 |
| test_multi_query | 10 | 0.13 | 62.2 |
| test_scope_feature | 3 | 0.21 | 71.0 |
| test_advanced_conditions_checkboxes | 8 | 0.23 | 71.3 |
| test_ai_advanced_conditions | 21 | 0.34 | 71.3 |
| test_phase4_conditions_logic_operator | 10 | 0.26 | 73.1 |
| test_editor_recovery | 39 | 0.94 | 80.7 |
| gui/test_editor_recovery_lifecycle | 53 | 13.58 | 214.8 |
| gui/test_editor_layout | 20 | 5.27 | 242.1 |
| gui/test_editor_dock | 67 | 7.88 | 204.7 |

Editor dock used -k 'not converter_switch'. **721 distinct focused cases passed**:
490 Explorer,52 shared/core,179 Editor;43 new. Earlier40-case repeats are not
counted again. First new run had39 passes and one actual FontChange regression;
handling both Qt font events fixed it. The final new module passed43 cases.

New cases cover initial/custom/shared/accessibility fonts, unchanged content/cursor
and fixed field heights, bounded/plain logs, tail retention, new-instance cleanup,
real worker errors/restart, stale/cancel/close diagnostics, pause/resume/cancel/close/
DeferredDelete without late log updates, existing File List consumer, enabled and
inactive drafts, old and invalid/oversized presets, QSettings/JSON and FE06 round-trip,
collapsed discoverability/retranslation, exact targets and both actual result views,
case normalization and relaxed/paused cache invalidation.

Pylint-E3 passed with jobs1/persistent=no, peak100.4 MiB. Initial normal run reported
six PySide6 dynamic-import false positives in the existing receiver imports.
Explicit extension inspection instead misidentified native Qt signals as ordinary
methods (peak382.2 MiB, exit2). Final normal analysis uses a local import-only
no-name-in-module annotation like the other Qt modules; no no-member suppression.
AST4 Python files, JSON2 catalogs and git diff --check passed. RAM44.0% at start,
45.4% before documentation. No native crash, timeout or guard abort in this stage.

## Limits And Closure

The historical FE05 combined214-case Qt process segfaulted at cross-line pause/
resume completion: signal11/exit139,210.7 MiB, no guard abort. **Root cause remains
UNRESOLVED.** Current isolated passes do not prove a fix, a leak-free process,
whole-suite/native desktop correctness or satisfaction of CI/security promotion gates.
No blind combined rerun, hosted CI, external provider call, push or main/develop change.

example.py remains untracked/unmodified (SHA-256
058053d87c818d699cde0f00d670bca0e1c6ad857caa9758ea6a556d7c64fcee).
Finite queue:0 pending,30 legacy items OUTSIDE SCOPE. No further continuation.

Monitoring was verified active with5 hooks/DB integrity/native queue and0.9.0;
doctor exit2 only for the previously failed reply-observer, not restarted.
Auto-start is false, so a finished idle worker is not reactivated by later hooks.
Only worker notebook-josue:codex:project=clarify-b09a84f1 and session
019ea8a0-6d60-7f03-90b9-c420603158d1 are authorized. Feature checkpoint ced3908
committed locally on the branch above. Then ai-presence --dry-run finish targeted
only that exact worker/session, exit0; status confirmed idle/current_task absent.
The CLI dry-run suppresses notifications, not the local finish database event;
no Discord/Telegram delivery occurred. Other workers retained their states and
services were not changed. No new native dispatch or retry was attempted.
