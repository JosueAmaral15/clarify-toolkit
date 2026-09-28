# File Explorer: Validated Cross-Line Block Search

Date: 2026-09-28
Task: FE-PAR-04. Branch: `COM-34c8502f-6eaf-416e-92e1-cd30adadbf3f`.
Ancestry: FE03 `d4551cb`, dispatch journal `5e1750d`, resource-stop journal
`bdecb9a`, then header/task-organization checkpoint `136b44e`.
The [resource-stop report](FILE_EXPLORER_CROSS_LINE_2026_09_28.md) remains a
historical unvalidated snapshot. This report records the completed resumption.

## Delivered

Cross-line Block is an explicit option, separate and mutually exclusive with
Multi-query (execution of independent queries remains FE05). The default retains
line-by-line matching. File/Folder/Selected scopes and copied worker requests
remain unchanged. Search options enter the existing target cache signature;
mode changes invalidate the cache, including a prior empty match universe.

Block queries validate before folder discovery: nonempty text, at most 64 KiB
UTF-8, valid regex, no combined multi-query and Text/ASCII only. Binary/Both modes
fail explicitly. Literal blocks normalize LF/CRLF/CR. Regex uses the existing
Python engine with MULTILINE/DOTALL, case sensitivity and grouped whole-word
boundaries. There is no new dependency or regex execution-timeout claim.

Files are bounded at 4 MiB, read in at most 64 KiB chunks with cancellation/pause
checkpoints and a growth check (not prefix-search truncation). Cached condition
content is checked before matching. UTF-8/NUL/binary errors are visible; special
files are rejected before content conditions/read. The bounded sample classifier
now uses an incremental UTF-8 decoder and an extra byte to distinguish a sample
split from invalid EOF. Existing content-scope regressions passed after this fix.

Matches preserve character-based start line/column, normalized line breaks and
bounded escaped snippets near the match, including matches far along long lines.
No per-character/line offset array is allocated. Zero-width/EOF positions are
tested. Budgets are 10000 matches/file and the remaining 50000 matches/operation,
without overshoot. Partial limits/errors/cancellation are explicit; errors stop
at 50 with a remaining-files notice, and incomplete results never enter the
incremental cache. A file with exactly the budget and no extra matches is not
falsely marked partial. Both result views receive existing SearchMatch tuples.

Replacement is rejected in this mode in core and dock before confirmation/write,
rather than silently using different flags/newline semantics. Existing atomic
replacement remains available with Cross-line Block disabled.

## Validation

RAM was 43.1% at resumption; no process was closed or guard weakened. Runs were
serial, with isolated HOME/settings/logs, offscreen Qt, OMP=1, no core dumps,
20 s pytest timeouts including fixtures and the existing `/tmp/clarify_guard.py`.
Guard ceilings: system RAM85%, process-tree RSS600 MiB, wall180 s. No provider,
secret file or real user document was used; `example.py` remains excluded.

| Test Set | Passed | Duration | Peak Process-Tree RSS |
| --- | --- | --- | --- |
| Explorer regressions, scope/lifecycle and 48 new cross-line cases | 313 | 12.91 s | 243.7 MiB |
| Shared conditions, AND/OR, checkboxes and scopes | 52 | 0.58 s | 74.0 MiB |
| Editor layout/header/hidden files and Explorer-to-editor flows | 22 | 4.55 s | 247.1 MiB |
| ThreadManager compatibility (separate process) | 7 | 0.14 s | 65.8 MiB |

**394 distinct focused tests passed**, not whole-suite/E2E or production proof.
Initial cross-line-only run:48 passed,4.49 s,207.3 MiB. A fresh-process repeat of
cross-line/lifecycle:84 passed,7.68 s,213.6 MiB. That repeat includes the strengthened
cancellation assertion on the actual file handle being closed, not merely POSIX
unlink succeeding. Repeat cases are not counted twice in the distinct total.

New cases cover literal/regex blocks, anchors, case/word boundaries, Unicode and
sample boundaries, LF/CRLF/CR, query/file byte limits and growth, binary/invalid
inputs, zero-width matches, per-file/global/error budgets, copied exact targets,
both views, worker affinity, pause/resume/cancel at bounded read, option round-trip,
cache transitions, visible partial diagnostics and pre-write replacement rejection.
Shared lifecycle regressions retain close/deferred-delete/late-callback protection.

Focused four-module error lint (including Editor header changes) passed exit0,
peak417.6 MiB, jobs=1, persistent cache disabled and PySide6 dynamic support.
Final AST parsing of six changed Python files, both JSON catalogs and whitespace
checks passed. This is not global lint/coverage or a guarantee against all leaks.

An offscreen options capture was inspected: Cross-line Block is fully visible,
distinct from Multi-query and content type, with a multiline query. Capture peak
184.9 MiB. Other old wide rows remain horizontally scrollable. Editor header
captures are in its separate report; no native desktop/theme certification.

## Limits And Next Stage

Regex/OS calls already in progress remain cooperative only after returning;
there is no forced interruption or regex deadline. Directory discovery retains
its existing collection costs; these bounds are not a global application RAM cap.
The classifier remains a bounded heuristic; cross-line decoding checks the full
bounded UTF-8 input. No multi-file rollback, multi-query execution or enriched
conditions were added in this stage.

The user's latest request adds CE-REC-01, reusing the existing private bounded
recovery store to preserve latest Editor buffers on Editor/app closure and offer
safe restoration. Task organization/header24 were committed separately at136b44e.
Next is this recovery MUST before FE05/06/08, not an expansion into legacy tasks.
Current open count:34 (30 older out-of-scope + CE-REC-01 + FE05/06/08).

Monitor was explicitly restarted for this finite queue after the user's resumption.
Doctor confirms integrity/schema, five hooks, native queue and current controls;
only the known reply-observer service is failed (no restart/control change).
Commit locally after evidence; one exact-session native continuation may follow
for CE-REC-01, never retry uncertain dispatch. Finish when this finite queue ends
or cannot continue safely. No push/main/develop promotion with CI/security gates
still unresolved. Rollback must retain prior scoped lifecycle/header work and
unrelated files; review this stage's diff, do not reset the entire checkpoint.
