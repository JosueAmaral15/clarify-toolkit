# File Explorer Priority Implementation - 2026-10-14

## Scope

This checkpoint completes only `FE-REFINE-01`. It does not start
`FE-MODE-I18N-01`, application-wide threading, TOON migration, plugins or the
legacy backlog.

## Audit

The executor already supported an explicit `candidate_paths` universe and the
dock already retained successful content-search paths. The missing product
contract was that this cache was applied implicitly. The existing implementation
also needed stronger invalidation for file type, filename query, content query,
include/exclude globs and advanced filters so that a late worker completion could
not restore stale candidates after the UI changed.

## Implementation

- Added a `Reuse previous results` checkbox to `Directory & Type`. It is off by
  default, persists only an explicit user choice and drops retained candidates
  when disabled.
- Added runtime labels, tooltip and completion statuses to all seven catalogs:
  English, Brazilian Portuguese, Spanish, French, German, Japanese and Chinese.
- A compatible reuse reports that previous results were refined. An incompatible
  or absent cache runs the normal full search and reports that fallback without
  promising an acceleration.
- Extended cache identity and immediate invalidation across target scope, paths,
  recursion, hidden-file mode, file revision, file type, filename pattern,
  content-document revision, search options, conditions, extensions, globs and
  advanced filters. The content revision avoids copying oversized query text
  before its existing bound check.
- Preserved the existing candidate-path executor, operation ownership,
  pause/cancel/close lifecycle, result views and search budgets.

## Validation

Final isolated Qt offscreen runs used a temporary HOME, one GUI module per
process, system RAM 85%, process-tree RSS 600 MiB, wall 180 s and pytest timeout
20 s guards:

- `tests/test_file_explorer_incremental_search.py`: 8 passed, peak 214.1 MiB.
- `tests/test_file_explorer_target_scope.py`: 69 passed, peak 212.8 MiB.
- `tests/test_file_explorer_multi_query.py`: 70 passed, peak 215.1 MiB.

The 147 distinct passing cases cover opt-in/persistence, all-language runtime
retranslation, candidate bounds, filter invalidation, exact target identity,
both result views and worker lifecycle. No passing run had a native Qt crash or
guard abort.

One earlier attempt was stopped at the global RAM barrier and was not counted.
During final validation, one stale-QSettings test assumption and one duplicate
oversized-query extraction were detected; the test now isolates its preference
and cache identity now uses `QTextDocument.revision()` instead of extracting the
query. Both affected modules were rerun completely.

Pylint error checks, Python compilation, parsing all seven JSON catalogs,
presence of all four new keys, `git diff --check` and the unrelated `example.py`
SHA-256 check passed.

## Workspace Mode Localization

`FE-MODE-I18N-01` was completed as a second bounded stage. The audit confirmed
that Compact and Advanced are presentation modes of one `FileExplorerDock`:
the compatibility Search/Replace action selects Compact without creating a
second panel, and it is no longer inserted in the Editing submenu. The tab and
window retain the translated File Explorer identity.

The workspace group and both mode names are now native translations in all seven
catalogs. Runtime retranslation updates button text, tooltip and accessible name.
An isolated 220 px regression verifies that the longest localized label fits
without replacing either functional tool name.

Guarded validation passed 42 distinct cases: one new seven-language runtime and
narrow-width case (208.2 MiB peak), 31 shared-workspace lifecycle/layout cases
(217.1 MiB peak), and 10 catalog lookup cases (186.5 MiB peak). No native crash,
timeout or resource-guard abort occurred.

## Remaining Priority Queue

The canonical backlog has 33 open tasks, three in the active priority queue:
`APP-THREAD-01`, `APP-TOON-PRIMARY-01` and `PLUGIN-WQXR-01`. No open
File Explorer-specific item remains in this priority queue.
