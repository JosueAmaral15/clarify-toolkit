# File Explorer Independent Multi-Query - 2026-09-28

## Scope And Checkpoint

Only FE-PAR-05 was implemented. Branch
`COM-a6d282af-6dff-466b-b6ac-0de83265ceb8` starts at `4263720`, the dispatch
journal following CE-REC-01 `d67a7d8`. Incoming FE05 marker confirms that prior
continuation was processed; it was not resent. FE01/02,03,04,07 and Editor header/
recovery remain preserved. No push or main/develop promotion; CI/security gates
are still unresolved. Untracked `example.py` was neither edited nor staged.

## Behavior And Bounds

- Existing Multi-query control now invokes independent compiled queries rather
  than searching the entire input as one string. Cross-line remains separate;
  combining the modes is rejected, and Replace remains unsupported.
- Reuses `split_multi_query`: strips each query line, ignores blanks and lines
  beginning with `#`, normalizes CRLF/CR, deduplicates repeated active queries
  in input order. Regex can escape a leading `#` when searching comments.
  Other `MultiQueryProcessor` consumers retain their existing fallback behavior.
- All active regexes for the requested Text/Binary/Both scope are validated
  before discovery; invalid or unsupported binary regex is an explicit error,
  never silently converted to a literal. Whole Word groups alternations.
- Text regexes run separately on target lines, with Unicode character columns.
  Binary preserves the existing line1/byte-offset contract, hex/ASCII snippets,
  and bytes-regex semantics (including explicit binary newline patterns).
  Results are ordered by line/start column; one location is emitted once.
  Different starts remain distinct even when ranges overlap. Input order breaks
  same-start ties. A single regex retains standard non-overlapping `finditer`.
- Input maximum64 KiB UTF-8 and128 active lines (duplicates count before dedup).
  GUI checks document character count before extracting an oversized query at
  operation start; core validates exact UTF-8 bytes and Unicode errors. Existing
  shared textChanged signaling is not a global input-memory cap.
- Content maximum4 MiB/file, read in bounded chunks with growth checks; explicit
  error instead of searching a truncated prefix. Text rejects invalid UTF-8/NUL.
  Reused condition content is also checked before searching. Classification
  still uses a bounded sample; late invalid Text content fails rather than
  being silently reclassified or searching the valid prefix.
- Up to10000 unique matches/file and50000/operation;50 operation errors.
  A lazy heap merges at most128 iterators, not unbounded per-query result arrays.
  Extra matches/errors produce visible partial diagnostics. Exact per-file
  budgets without extra matches are not flagged partial.
- Cooperative checkpoints during chunk reads, iterator initialization and merge
  preserve pause/resume/cancel behavior. Regex/OS calls already in progress have
  no internal deadline or forced interruption. Folder discovery retains its
  existing contract; this is not a new global discovery-memory ceiling.
- Exact File/Folder/Selected Results scopes, both result views, one operation
  per dock, close/deferred deletion cleanup and cache identity were reused.
  Mode/options/target changes invalidate; changed queries cannot reuse a cache
  with a different exact query. Partial/error/cancelled runs do not seed cache.
- CE recovery is untouched:2 MiB/document,20 documents,20 MiB aggregate and
  bounded reference restoration; no original file is overwritten by this stage.

## Validation Evidence

Serial isolated `.venv` Python3.12.10, PySide6/Qt6.9.3 offscreen processes with
temporary HOME/settings/logs. `/tmp/clarify_guard.py` polls system RAM85%, process
tree RSS600 MiB and wall180s, kills only its own validation process group, and
disables core dumps. Pytest20s includes fixture setup/teardown. No live providers,
real user documents or full MainWindow startup fixtures were used.

Common command (one module per process):

```sh
python /tmp/clarify_guard.py .venv/bin/python -m pytest MODULE -q \
  --timeout=20 --timeout-method=thread -o timeout_func_only=false
```

| Module | Passed | Pytest seconds | Peak tree RSS MiB |
| --- | ---: | ---: | ---: |
| tests/test_file_explorer_multi_query.py | 70 | 8.91 | 210.3 |
| tests/test_file_explorer_cross_line.py | 48 | 5.38 | 209.5 |
| tests/test_file_explorer_target_scope.py | 69 | 7.39 | 209.3 |
| tests/test_file_explorer_lifecycle.py | 36 | 7.65 | 211.7 |
| tests/test_file_explorer.py | 35 | 0.49 | 76.0 |
| tests/test_file_explorer_replace.py | 33 | 3.92 | 202.8 |
| tests/test_file_explorer_conditions.py | 60 | 3.74 | 198.6 |
| tests/test_file_explorer_content_scope.py | 6 | 3.57 | 182.8 |
| tests/test_file_explorer_regex_coherence.py | 5 | 3.56 | 197.0 |
| tests/test_file_explorer_incremental_search.py | 5 | 3.71 | 200.7 |
| tests/test_file_explorer_top_options_and_globs.py | 4 | 3.69 | 203.5 |
| tests/test_multi_query.py | 10 | 0.14 | 62.9 |
| tests/test_editor_recovery.py | 39 | 0.79 | 72.8 |
| tests/gui/test_editor_recovery_lifecycle.py | 53 | 12.69 | 214.1 |
| tests/gui/test_editor_layout.py | 20 | 5.33 | 241.9 |
| tests/gui/test_editor_dock.py, not converter_switch | 67 | 8.34 | 204.5 |

**560 distinct focused cases passed.** Editor excludes2 heavy converter-switch
fixtures. Earlier61/70 multi-query and48 cross-line isolated repeats are not
double-counted. Initial new test assumptions about method names, result keys,
query-cache invalidation, widget APIs and FIFO discovery were corrected before
these passing runs; their failed runs do not count as validation success.

Pylint-E on the3 production modules passed (exit0,391.2 MiB peak, one job,
persistent cache disabled), after pytest processes had ended. AST4 Python files,
JSON2 catalogs and `git diff --check` passed. RAM43.1% at final checks; no guard
was weakened. `example.py` SHA256 remains
`058053d87c818d699cde0f00d670bca0e1c6ad857caa9758ea6a556d7c64fcee`.

New cases cover validation before discovery/worker, UTF-8/query-count limits,
literal/regex/case/word matching, CR/LF, empty/repeated/overlapping/zero-width
queries, Unicode snippets, bytes scopes, file growth, handle closure, budget
union, late invalid content, partial/error cache behavior and prepared cancel.
Real Qt workers cover all target scopes and both views, incremental repeats,
pause/resume/cancellation while paused, close/deferred delete and no late batch
callback after closure. Central thread registry settles in those cases.

### Unresolved Combined Native Failure

A serial but combined process collected214 cases (then61 new multi-query,
48 cross-line,69 scopes,36 lifecycle). After the new tests passed, it segfaulted
during `test_real_worker_pause_at_block_read_then_resume_or_cancel` in
`tests/test_file_explorer_cross_line.py`, around Qt completion/logging callbacks.
Exit139 (signal11), peak210.7 MiB, guard reasonNone: not a demonstrated OOM or
guard timeout. Root cause is **unconfirmed**. No core dump or user-process kill.

The GUI modules were subsequently isolated in separate serial guarded processes;
all passed, including the affected cross-line module twice. This establishes
focused isolated results, **not** a fix or explanation for the combined crash.
It remains an integration/native stability risk. Do not blindly repeat the
combined run or claim leak-free/global GUI stability. If a native crash recurs
in isolated validation, stop automatic continuation and finish the exact worker.

## Monitoring And Remaining Queue

Doctor0.9.0 verifies5 hooks, database integrity, active monitor and native queue.
It exits2 only for the previously failed reply-observer; no restart was attempted.
Exact worker `notebook-josue:codex:project=clarify-b09a84f1` is active and hooks
refresh its status. Session `019ea8a0-6d60-7f03-90b9-c420603158d1` only.

Remaining **FE-PAR-06 and08**:2 finite items,32 overall including30 legacy items
excluded from this automation. Only one exact-session native continuation after
the validated local checkpoint; never retry uncertain dispatch. Finish the exact
worker when this finite queue completes or cannot continue safely. Isolated tests
do not clear CI/security, packaging, external coverage or native desktop UX gates.

## Continuation Journal

Validated FE05 checkpoint is `d924e4b` (9 scoped paths). Worktree then contained
only unchanged/untracked `example.py`; RAM43.2%, exact worker/hook active, no
previous exact-session queue process. Dry-run passed. Exactly one real native
continuation with delay15s/detached queue was called for
`CLARIFY_FE_PAR_CONTINUE_20260928_FE06`, the worker/session above. CLI exited0 with
`dispatch_started`; this is initiation, not proof of delivery or processing.
Never retry uncertainty. Next marker verifies this checkpoint plus this journal
before making a fresh COM-UUID branch. The continuation carries the unresolved
combined Qt crash and stop-on-isolated-crash/guard rule. Monitor remains active
only for FE06/08, with finish on finite completion or unsafe continuation.
