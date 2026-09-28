# File Explorer Enriched Conditions - 2026-09-28

## Scope And Checkpoint

Only FE-PAR-06, on `COM-9c8a0ddf-ec84-47cd-a00d-f718bf01f720`, freshly created
from `6c4ae07` (FE06 dispatch journal after FE05 checkpoint `d924e4b`). Incoming
marker confirms processing; prior dispatch was not resent. No push, main/develop
promotion or CI/security bypass. `example.py` and unrelated work are preserved.

## Changes

- ConditionsGrid now exposes Starts With/Ends With, per-condition Whole Word,
  content scope and parameter. Compact stacked rows avoid adding all controls to
  one wide strip. Stable field/operator data is preserved, including numeric
  aliases and legacy `regex` operator/`use_regex` mappings.
- Whole Word retains shared semantics for Contains/Not Contains; disabled for
  operators where the shared matcher does not use it. Scope/parameter apply only
  to content. Switching fields disables irrelevant controls without destroying
  their local values. Brackets/braces/parentheses/custom/tag/specific-tag and the
  existing hierarchical API reuse `Condition` and `extract_scope_content`.
- `set_conditions` validates first, restores all options and AND/OR, and emits
  only the completed expression. Empty UI rows remain inactive as before.
- Explorer presets retain the existing flat filter keys and add `conditions`
  and `logic_operator`. QSettings and JSON use the existing PresetManager.
  Filter-only legacy presets restore no conditions/AND, clearing any previous
  expression. Bad condition data is rejected before either panel is changed;
  validation errors are shown instead of a misleading successful load.
- Effective regex is validated with the same grouping/end anchors used during
  matching. Unknown/invalid scope, incomplete custom delimiters, missing tag/
  hierarchical parameters, malformed scope regex and unsupported multi-capture
  extraction are explicit errors. GUI validates before worker launch; core also
  validates mappings. Valid legacy direct `Condition` consumers remain supported.
- Limits:128 condition entries;64 KiB UTF-8 per value/scope parameter. Preset
  values are validated before widget restoration; editors have bounded character
  capacity and core additionally checks bytes. Existing4 MiB content-reader
  limit/cache remains. Optional `max_chars` scope-output bound prevents repeated
  hierarchical includes from expanding output beyond source character count in
  Explorer. Exceeding it propagates an explicit per-file error, not a false claim
  of complete filtering. Consumers omitting that keyword retain their behavior.
- Condition changes invalidate incremental cache; expression and AND/OR are part
  of target/cache identity. Changing conditions while paused cannot repopulate an
  obsolete universe on completion. File/Folder/Selected Results, both views,
  multi-query/cross-line separation, budgets and safe worker lifecycle are reused.
- Editor recovery is untouched:2 MiB/document,20 documents,20 MiB aggregate and
  bounded saved-reference restoration. This stage does not write document files.

## Validation

`.venv` Python3.12.10/PySide6/Qt6.9.3. Each module ran in a separate serial
offscreen process with temporary HOME/settings/logs and `/tmp/clarify_guard.py`:
system RAM85%, tree RSS600 MiB, wall180s, no core dumps. Only that validation
process group can be terminated by the guard. Pytest20s includes fixtures.
No providers, user documents or full MainWindow startup fixtures.

```sh
python /tmp/clarify_guard.py .venv/bin/python -m pytest MODULE -q \
  --timeout=20 --timeout-method=thread -o timeout_func_only=false
```

| Module | Passed | Seconds | Peak tree RSS MiB |
| --- | ---: | ---: | ---: |
| test_file_explorer_enriched_conditions | 67 | 5.57 | 209.9 |
| test_file_explorer_conditions | 60 | 4.02 | 198.2 |
| test_file_explorer_multi_query | 70 | 8.78 | 212.4 |
| test_file_explorer_cross_line | 48 | 5.25 | 209.8 |
| test_file_explorer_target_scope | 69 | 7.24 | 209.1 |
| test_file_explorer_lifecycle | 36 | 7.46 | 214.2 |
| test_file_explorer | 35 | 0.48 | 75.7 |
| test_file_explorer_replace | 33 | 3.89 | 204.1 |
| test_file_explorer_content_scope | 6 | 3.47 | 183.0 |
| test_file_explorer_regex_coherence | 5 | 3.49 | 196.9 |
| test_file_explorer_incremental_search | 5 | 3.69 | 200.9 |
| test_file_explorer_top_options_and_globs | 4 | 3.76 | 203.9 |
| test_multi_query | 10 | 0.14 | 62.7 |
| test_scope_feature | 3 | 0.23 | 70.8 |
| test_advanced_conditions_checkboxes | 8 | 0.22 | 71.0 |
| test_ai_advanced_conditions | 21 | 0.32 | 71.3 |
| test_phase4_conditions_logic_operator | 10 | 0.27 | 73.1 |
| test_editor_recovery | 39 | 0.82 | 63.9 |
| gui/test_editor_recovery_lifecycle | 53 | 12.43 | 215.6 |
| gui/test_editor_layout | 20 | 4.96 | 241.9 |
| gui/test_editor_dock, not converter_switch | 67 | 7.80 | 204.6 |

Module names are under `tests/` with the `.py` suffix. Pylint-E on5 production
modules passed after pytest ended (one job, no persistent cache, final exit0 and
391.3 MiB peak). AST6 Python files, JSON2 catalogs and `git diff --check` passed.
RAM started43.2%; all runs retained the guards unchanged.

**669 distinct focused cases passed**,67 new. Earlier62/66 new-test runs and60
condition repeat are not double-counted. The first new run had61 passes and one
incorrect expectation about the disabled extension filter; the test was corrected
to check restored text without implementing FE08 early. No native crash, timeout
or memory-guard abort occurred during this stage's validations.

New cases exercise every scope, shared extraction reuse, operator/word/case/regex
semantics, strict errors, UTF-8/count/output bounds, legacy defaults and aliases,
Qt enabled states/one completed restore signal,450/900px layout, invalid presets
without panel mutation, actual QSettings and JSON condition round-trip, exact
targets and both views with real workers, empty cache followed by relaxed
conditions, condition edits while paused/resume/cancel/close, and pre-launch errors.

Other consumer regressions are focused shared-core evidence, not their complete
tool UIs. Full MainWindow Search/Replace fixtures were deliberately not run;
Editor excludes2 converter-switch fixtures. Extension-filter presentation/state
belongs to FE08, not a claim that all existing filter-preset issues are resolved.

## Risks And Remaining Queue

The FE05 combined214-case Qt segfault remains **unresolved**. Isolated passing
modules do not explain or fix it, establish native desktop UX or certify no leaks.
Do not repeat that combined run blindly. Stop continuation and finish the exact
worker if an isolated native crash or resource guard barrier recurs. Filesystem
and regex calls in progress have no production internal deadline; checkpoints
remain cooperative. Existing shared extraction semantics are not a full XML parser.

Monitor0.9.0/hook active; doctor confirms5 hooks, integrity and native queue,
exit2 only for the previously failed reply-observer, not restarted. Exact worker
`notebook-josue:codex:project=clarify-b09a84f1`, session
`019ea8a0-6d60-7f03-90b9-c420603158d1` only. No other worker was changed.
`example.py` SHA256 unchanged:
`058053d87c818d699cde0f00d670bca0e1c6ad857caa9758ea6a556d7c64fcee`.

Remaining **FE-PAR-08 only** (1 finite,31 overall including30 legacy excluded).
One exact-session native continuation after validated local commit, never retry
uncertain dispatch; finish the worker on finite completion or unsafe continuation.
