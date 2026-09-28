# File Explorer Parity: First Implementation Stage

Date: 2026-09-28
Branch: `COM-7bf189e1-fee8-410b-9929-bf58e6d8d2ca`
Scope: approved FE-PAR-01..08; this checkpoint completes **01 and 02**, not the batch.

## Delivered

- Replacement uses the visible tree/table selection only, deduplicated and never
  silently expanded to all results. First/All require confirmation with bounded
  query/replacement/path previews. The Qt-bound worker slot runs off the GUI thread.
- Dock/worker/executor share a compatible result contract: success, cancellation,
  replacement counts, modified files and errors. Original `replaced_count` remains.
  Partial results are reported honestly; history keeps counts, not file text.
- Preserve Case works with deletion, literals/backslashes, numbered/named regex
  backreferences and zero-width matches. Whole Word groups regex alternatives.
- Per-file atomic writes preserve CRLF, ownership/group, permissions and supported
  extended attributes. Reject symlinks/hard links, oversized inputs/output and
  files whose identity/revision changed during the operation; failed writes leave
  the original and clean temporary files. This is not multi-file rollback.
- Replacement limits: 4 MiB input/output/query/replacement, 1000 selected files,
  10000 matches per file and 50 recorded errors. Error-limit stops are explicit.
- Conditions normalize older numeric/operator aliases and validate before use.
  Browse/search use the complete AND/OR expression with real content values,
  options and scopes, not the main query match count. OR is order independent
  when metadata matches but content cannot be read as text.
- Content-condition reads are bounded to 4 MiB and cached per file. Invalid
  conditions fail closed with diagnostics; completion errors are bounded and
  visible in status/tooltips. Failed operations do not retain incremental caches.
- Shared Condition matching fixes regex Ends With/Whole Word grouping and accepts
  extensions with/without a leading dot. Shared filtering lazily reads content
  once, preserving OR metadata matches when a read fails. Other tools remain.
- Retained prior Editor folder-label/hidden-file changes. Retesting exposed lazy
  model loading invalidating the tree root; the root is rebound to the current
  folder without changing sidebar visibility or following stale load paths.

## Validation

All final runs used separate subprocesses, temporary HOME/settings/logs, Qt
offscreen, 20-second test timeouts and the local resource guard. No real user
documents, credentials, providers or applications were changed by testing.

| Final Run | Result | Time | Peak Process-Tree RSS |
| --- | --- | --- | --- |
| Explorer replacement/conditions + existing browse/search/binary/filter/cache/progress regressions | 160 passed | 6.93 s | 232.0 MiB |
| Shared AI conditions, AND/OR, checkboxes and scopes | 52 passed | 0.93 s | 71.5 MiB |
| Editor layout/header/hidden files/root rebinding and Explorer flows | 21 passed | 6.35 s | 242.4 MiB |
| Repeat Editor run, fresh process | 21 passed | 6.26 s | 243.8 MiB |
| Focused Pylint errors, six changed production modules, serial | exit 0 | bounded | 385.1 MiB |

There are **233 distinct tests** across the three final test sets; the repeated
Editor run is not counted twice. New tests prove actual replacement thread
affinity, active-view selection, confirmation cancellation, partial cancellation,
invalid regex/backreferences, limits, atomic failure/conflicts, links/metadata,
numeric aliases, content predicates/options, mixed OR and compatibility.
AST parsing and `git diff --check` passed. Pylint uses PySide6 extension support
and `--generated-members=connect`; the initial attempt produced only dynamic Qt
`connect` false positives. This is not whole-project lint or full-suite/E2E proof.

Earlier failures were investigated: one incorrect regex expectation in a new
test was corrected; an Editor root race was repaired. The first root-rebind
patch misplaced the visibility call; layout tests caught it and it was restored.
One broader test attempt was stopped before collection because system RAM
reached 85%. After five stable samples below 80%, validation resumed. Limits:
85% system RAM, 600 MiB validation process tree, 180 seconds wall time. No user
process was killed, and an interrupted attempt is not counted as a pass.

## Continuation And Remaining Work

AI Presence Monitor 0.9.0 was started once for this project using Protocol 2.
Database integrity/schema, native Codex queue and five hooks are available;
hooks show real current activity. Strict doctor returned an error because the
reply-observer service is failed. No service restart, migration, control change,
GUI input or secret-file access was performed. Direct native continuation does
not use that reply observer. Dry-run targets the exact current session and worker;
a detached dispatch is preliminary, not proof of processed input.

Next: **FE-PAR-07**, covering cooperative pause/resume, cancellation during pause,
safe application close, coordinated workers and late-callback cleanup, with real
thread/lifecycle tests. Then explicit targets (03), cross-line blocks (04),
independent queries (05), enriched conditions/presets (06) and presentation (08).
There are **six approved parity items and 30 earlier backlog items open**, total
36. Do not automatically expand continuation to the legacy backlog.

Limitations: multi-query replacement is explicitly rejected; ordinary text search
still needs bounded reads in FE-PAR-04. Python `re` has no hard per-match timeout;
cooperative cancellation does not interrupt a pathological match. Global Undo,
backup and transactional multi-file rollback remain LEG-24. CI/security/branch
protection/PR integration and the broader Qt lifecycle investigation remain open.
No push, main/develop merge or release claim accompanies this local checkpoint.
The unrelated `example.py` is excluded.
