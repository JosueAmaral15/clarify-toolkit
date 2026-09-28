# File Explorer: Explicit Target Scope Stage

Date: 2026-09-28
Branch: `COM-f4922ddf-dee2-4de5-a53f-cfae7955af88`
Base: implementation checkpoint `54032ee`, followed by dispatch journal `932b41a`.
Scope: **FE-PAR-03**, with a regression-discovered FE-PAR-07 cleanup correction.
The [lifecycle report](FILE_EXPLORER_LIFECYCLE_2026_09_28.md) and
[first-stage report](FILE_EXPLORER_PARITY_IMPLEMENTATION_2026_09_28.md) retain
their historical evidence/counts; current pending state is in `docs/TASKS.md`.

## Delivered

- A target category selects Folder (compatible default), File, or Selected
  Results. File opens a file picker; Folder opens a directory picker. Selection
  scope disables the path, recent folders, recursion and hidden-discovery controls.
  Exact targets include explicitly chosen hidden paths, independent of discovery.
- File browse/search operates on that file alone even with recursion requested.
  Selected Results snapshots only represented paths in the active tree/table,
  deduplicated in order. Roots/group headings do not expand; selecting a directory
  lists only its metadata, never descendants. Content search/replacement skips
  directories. Missing selection reports an error rather than falling back to
  folder traversal. Selected paths may intentionally span different folders.
- Existing globs/type/size/conditions continue narrowing the target. Incremental
  candidates can only intersect explicit targets, including the empty intersection;
  they cannot introduce siblings or trigger an implicit rescan of the folder.
- Worker requests copy the scope/path snapshot before result clearing or dispatch.
  Both result views and browse/search run through the existing real Qt worker slot.
  Programmatic edits while paused do not change the in-flight operation.
- Cache identity includes scope, root, exact paths, recursion/hidden flags, search
  options and the single file's filesystem revision. Scope/path/options/selection
  changes invalidate it. Changed targets cannot restore an obsolete cache at
  settlement. File edits after an empty match set and Text-to-Binary changes are
  explicitly tested. This is not a new general folder watcher.
- File replacement requires the existing confirmation/preview and changes only
  the typed file, even if a sibling result is selected. Other scopes retain exact
  active-view selection, with Folder rejecting selected paths outside its root.
  No all-results fallback or multi-file Undo/rollback was added. Existing atomic
  replacement limits, metadata preservation and link/concurrent-edit rejection
  remain unchanged.
- Inputs reject empty/NUL/non-path values, ambiguous scope/path combinations,
  more than 1000 paths, paths over 4096 filesystem bytes, or over 1 MiB aggregate
  path bytes before target metadata work. Duplicate inputs count toward raw bounds
  before deduplication. Explicit metadata errors stop at 50 with a diagnostic.
  Leading/trailing spaces in a valid filename are preserved, not stripped.
- English/Portuguese labels retain stable item data after retranslation. The
  selection count has its own row. Target controls are left-aligned and their
  scroll viewport has a computed minimum width so the new selector is not clipped.
  Other existing wide rows retain horizontal scrolling; no global layout redesign.

## Cleanup Follow-Up

The combined regression run exposed a central registry entry left after deferred
dock deletion. All test bodies passed, but teardown failed; a bounded three-second
event-loop wait reproduced it, ruling out the original premature assertion.
The prior lambda completion callback could lose its Qt context when the
dock/thread was destroyed before queued cleanup.

ThreadManager now owns an independent QObject completion receiver with the
registration thread's affinity (GUI in Explorer). Its bound Qt slot removes the
entry and schedules its own deletion. Cleanup never mutates the registry directly
from an Explorer worker. Other feature-exclusive defaults and the non-PySide
fallback are preserved. Tests assert GUI affinity and destruction of these
receivers across ten operations; old ThreadManager compatibility tests pass.
This fixes a demonstrated lifecycle defect, not a claim of global leak freedom.

## Validation

Serial subprocesses used isolated HOME/settings/logs, Qt offscreen, OMP=1,
20-second pytest timeouts (including setup/teardown), and `/tmp/clarify_guard.py`.
The guard samples every 250 ms, kills only the validation process group if system
RAM reaches 85%, process-tree RSS exceeds 600 MiB, or wall time exceeds 180 seconds;
core dumps are disabled. RAM was checked before heavy runs. No parallel suites,
provider requests, secret reads, user-document writes or user-process kills.

| Final Test Set | Passed | Duration | Peak Process-Tree RSS |
| --- | --- | --- | --- |
| Explorer regressions, 69 new scope cases and 36 lifecycle cases | 265 | 13.07 s | 242.2 MiB |
| Shared conditions, AND/OR, checkboxes and scopes | 52 | 0.75 s | 73.1 MiB |
| Editor layout/header/hidden files and Explorer-to-editor flows | 21 | 4.90 s | 245.2 MiB |
| Existing ThreadManager compatibility | 7 | 0.16 s | 65.6 MiB |

**345 distinct focused tests passed**, not whole-project/E2E or production proof.
A separate fresh-process repeat of scope/lifecycle passed 105 cases (11.55 s,
213.8 MiB) before the final viewport-only correction; the final 265 run includes
the stronger viewport assertions and that correction. Earlier expected-filter
test failures used the wrong size-filter test payload and were corrected to the
existing API. Review also caught path stripping that could choose a different
file; browse/search/confirmed-replace regressions now cover exact space suffixes.

The first screenshot exposed viewport clipping missed by parent-widget bounds.
After the correction, a Portuguese offscreen capture was inspected: selector
and selection count are fully visible without overlap. Qt expanded the standalone
host to its existing minimum size (937x650 from a 900x650 request); this is not a
claim that the entire dock fits 640 pixels, nor native desktop/theme certification.
Capture process peak: 183.5 MiB. No real app startup/provider loading was needed.

Focused Pylint checks errors only, in the four changed production modules, with
jobs=1, persistent cache disabled, PySide6 extension support and dynamic
connect/disconnect members. AST parsing of six changed Python files, parsing
both translation JSON files, and diff whitespace checks are separate evidence.
All these checks passed; final Pylint exit 0, peak 388.1 MiB.
This is not global lint, whole-suite coverage or a new application memory ceiling.

## Limits, Review And Next Stage

Folder discovery retains its prior recursive/nonrecursive behavior and existing
collection costs. Explicit path bounds do not bound file contents or all possible
result sets. Cross-line input/result limits belong to FE-PAR-04. Pause/cancel still
await cooperative checkpoints; an in-progress regex/OS call or atomic commit is
not forcibly interrupted. Backend scope additions are optional keyword parameters;
legacy Folder consumers and shared API patterns remain available.

For rollback review, the target feature and independent registry receiver serve
different purposes: retain the validated receiver fix if reverting target UI/core
changes. Do not rewind the entire checkpoint or disturb unrelated work.

Monitor 0.9.0 remains active with current hooks. Doctor confirms integrity/schema,
five hooks, native queue and existing automation/native controls; its exit 2 is
the still-failed reply-observer service. No restart/control change/migration.
The received FE03 marker confirms processing of the preceding dispatch. Next
continuation must be one native call to the exact same worker/session, only after
local commit; uncertain dispatch is never retried. Detached initiation is not
delivery/processing proof, which must be verified at the next received marker.

Remaining approved tasks: **FE-PAR-04, 05, 06 and 08**, next cross-line search (04).
The **30 older backlog items are out of this automation scope**: 34 open total.
Finish ai-presence only when this finite batch completes or cannot safely continue.
No push/main/develop promotion while CI/security gates remain unresolved.
`example.py` and other unrelated edits are excluded and preserved.
