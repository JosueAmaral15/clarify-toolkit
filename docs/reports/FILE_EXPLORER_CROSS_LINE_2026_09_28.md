# File Explorer: Cross-Line Draft And Resource Stop

Date: 2026-09-28
Branch: `COM-34c8502f-6eaf-416e-92e1-cd30adadbf3f`
Base: validated FE-PAR-03 checkpoint `d4551cb` plus dispatch journal `5e1750d`.
Scope: **FE-PAR-04 only** in the approved finite FE-PAR-01..08 batch.
Status: **draft, unvalidated, not completed; implementation is not committed**.
Previous [scope validation](FILE_EXPLORER_TARGET_SCOPES_2026_09_28.md) does not
validate the new working-tree changes.

## Orientation And Draft

The received unique FE04 marker confirms processing of the previous native
continuation. Checkpoint/journal were present; only unrelated `example.py` was
untracked before work. Current docs/shared APIs and branch policy were read.
The new COM branch was created from the authorized stacked checkpoint, not
main/develop. No push, promotion, provider or secret-file access.

The local draft contains:

- A separate Cross-line Block checkbox and `cross_line` option. The existing
  multi-query checkbox is labeled explicitly and mutually exclusive with block
  mode. Multi-query execution remains FE-PAR-05, not an implementation claim here.
  Options emit the existing cache invalidation signal; FE-PAR-03 target identity
  already incorporates all option values. The default remains old line matching.
- Pre-discovery query validation: nonempty text, at most 64 KiB UTF-8, valid
  regex, no combined multi-query, Text/ASCII only (Binary/Both rejected explicitly).
  Regex uses the existing Python engine with MULTILINE/DOTALL, case sensitivity
  and grouped word boundaries. No new dependency.
- Bounded 4 MiB file reads with 64 KiB chunks, size/growth checks and cooperative
  checkpoints. No unbounded `read_text` fallback in block mode. UTF-8 decoding/NUL
  errors are explicit. Cached condition content is size-checked before matching.
  Selected special files are rejected before content conditions or reads.
- LF/CRLF/CR normalization, character-based start lines/columns and bounded
  escaped snippets near the match rather than always the start of a long line.
  No per-character/line index array. Results remain existing SearchMatch objects.
- A 10000-match per-file budget and the remaining operation budget (50000)
  prevent overshoot. Limits/errors/cancellation mark partial results and remain
  visible in existing completion diagnostics; incomplete results cannot become
  an incremental cache. Errors stop at 50 with an explicit remaining-files notice.
- The UTF-8 sample classifier reads one extra byte and uses an incremental
  decoder to distinguish a split sample character from invalid EOF. This narrow
  correction also affects existing classification and therefore needs its old
  Text/Binary regressions as well as the new boundary cases.
- Core and dock reject replacement while cross-line mode is enabled, before
  confirmation/write, rather than silently using different replacement semantics.
  Existing replacement remains available with the new mode disabled.

These are **source intentions, not demonstrated working features**. The new
`tests/test_file_explorer_cross_line.py` includes normal/regex blocks, Unicode,
LF/CRLF, query/file bounds and growth, binary/invalid inputs, match/error budgets,
zero-width matches, mode round-trip, both views/target scopes, native worker
affinity, paused read cancellation/resumption, cache transition, diagnostics and
replacement rejection. It has not been collected or executed.

## Resource Evidence And Validation Limits

System RAM was 82.3% at orientation. Before any heavy run, five one-second
samples were 83.7, 83.9, 83.9, 83.9 and 83.9%. A separate bounded three-minute
watch sought five consecutive samples below 78%; it did not obtain headroom.
Samples rose from 84.5% to approximately 85-86% and ended at 85.7%.
Read-only process RSS inspection showed Firefox/content processes as the largest
consumers. No user process was killed, browser closed, cache dropped or service
restarted. This is ambient resource pressure, not evidence about draft leak safety.

**No pytest suite, runtime GUI check, screenshot or Pylint run was started in this
stage.** AST parsing of the initial draft and translation JSON parsing passed
before the final small guard/test edits; syntax alone does not validate imports,
behavior, the final draft or cleanup. No current test-count/pass claim applies.
The prior stage's 345 focused passes remain historical checkpoint evidence only.

The existing serial `/tmp/clarify_guard.py` was reread, not weakened. Limits remain
system RAM 85%, validation tree RSS 600 MiB, wall 180 seconds, core dumps disabled,
isolated HOME/settings/logs, Qt offscreen and OMP=1. Validation must not start
under current pressure merely to obtain a green result. Do not equate a guard
abort or collection-only result with a passing suite.

## Resume And Rollback

1. Obtain sustained RAM headroom first. Retain the current branch and inspect
   the worktree; drafts are uncommitted, so do not reset/clean/switch them away.
   Recheck unrelated edits and preserve `example.py`.
2. Review the final draft and execute the new cross-line module serially with
   the existing guard, `--timeout=20 --timeout-method=thread -o timeout_func_only=false`.
   Diagnose failures before broadening the test set.
3. Run the focused Explorer/lifecycle/target/content/regex/replacement regressions,
   then shared conditions, Editor layout/flows and ThreadManager compatibility in
   separate serial processes. Recheck headroom before each run, especially lint.
4. Run focused error lint, final AST/JSON/diff checks and inspect an offscreen
   capture of the new controls. Record exact evidence, repair regressions and
   commit implementation only after validation. The classifier change needs
   existing content-scope compatibility checks; shared widget APIs need review.
5. Update TASKS/history and resume monitoring explicitly when safe. Only after
   completing FE04 may one exact-session FE05 continuation be sent; never retry
   uncertain dispatch. FE05/06/08 and all 30 legacy items remain untouched.

If rollback is needed, review only this draft against `5e1750d`; retain prior
validated scope/lifecycle work and unrelated files. No rollback was performed.
Python regex/OS calls already in progress are still not forcibly interruptible;
byte/match limits and checkpoints do not provide a regex execution deadline.
Folder discovery retains its existing collection costs, not a global RAM ceiling.

## Monitoring Outcome

Doctor confirmed 0.9.0, integrity/schema, five hooks, native queue, current activity
and existing automation controls. Exit 2 remains the previously failed reply
observer; it was not restarted. With persistent resource pressure preventing safe
validation, the finite automation chain was stopped as authorized:

`ai-presence finish --worker notebook-josue:codex:project=clarify-b09a84f1 --protocol protocol2`

The real call returned exit 0 and `status=idle`. Other workers/services were not
stopped. No FE05 dry-run/dispatch or retry was made. Only a documentation stop
journal is committed; the feature draft remains uncommitted.

Remaining approved items: **FE-PAR-04 (in progress), 05, 06 and 08**. Four pending
plus 30 older out-of-scope items = **34 open**. No implementation-completion,
whole-suite/E2E, leak-free, native UX, CI/security or production-readiness claim.
