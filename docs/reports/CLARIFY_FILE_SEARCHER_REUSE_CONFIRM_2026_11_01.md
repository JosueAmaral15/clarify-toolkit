# File Searcher Replace Reuse Confirmation - 2026-11-01

## Scope

Implemented only `FE-REPLACE-REUSE-CONFIRM-01` from checkpoint `ed5bc2d`.
No public File Explorer rename, Editor work, provider integration or legacy
backlog item was started. `example.py` remained untracked and byte-identical.

## Reproduced gap

The previous Replace route showed one confirmation and immediately launched the
write worker. It did not run a read-only discovery preflight, display that
preview in the right result view, reject partial or stale previews, or offer an
explicit compatible-cache choice before the write confirmation.

## Delivered contract

- The initial translated confirmation reports the bounded query, replacement,
  exact scope, current file/match counts and cache compatibility.
- `Reuse Previous Results` remains unchecked by default. A checkbox is exposed
  only when directory, target signature, query and cached universe are
  compatible; an empty compatible search universe retains its existing cache
  semantics but is not offered as a useful replacement universe.
- Declining reuse or having no compatible cache performs complete discovery in
  the exact File, Folder or Selected Results scope. No sibling or outside-root
  expansion was added.
- Existing search workers populate Tree and Table as a read-only preflight.
  Empty, partial, cancelled, errored or over-budget previews block replacement.
- Query, options, replacement, scope and file revisions are checked after the
  preview. Revisions are checked again after the separate final confirmation,
  before the existing bounded atomic replacement worker starts.
- Closing or deleting a dock clears pending preflight state. A reproduced
  parent-delete settlement race was corrected in `ThreadManager`: a queued
  completion now safely releases a registration when Qt already deleted the
  native parentless thread object.

## Guarded validation

Each GUI module ran in a separate offscreen process with temporary `HOME` and
guards at system RAM 85%, process-tree RSS 600 MiB, wall 180 seconds and pytest
20 seconds including fixtures.

- replacement preflight/reuse confirmation: 7 passed;
- Search/Replace sections: 8 passed;
- replacement executor and dock: 33 passed;
- incremental cache: 8 passed;
- exact target scopes: 69 passed;
- File Explorer presentation: 43 passed;
- lifecycle and close cleanup: 36 passed;
- table refresh: 2 passed;
- top options/globs: 4 passed;
- workspace i18n: 1 passed;
- i18n expansion: 14 passed;
- translation catalog lookup: 10 passed;
- thread manager: 7 passed.

Total: 242 focused tests. Peak process-tree RSS was 216.3 MiB.

One intermediate legacy replacement test timed out because it left the target
scope implicit and opened an unmocked warning dialog; the probe reported
`abort_reason: null`. The test was corrected to its intended Selected Results
scope. A later lifecycle run exposed the deterministic deleted-`QThread`
settlement race described above; after the bounded fix, all 36 lifecycle tests
and all 7 ThreadManager tests passed. No native crash, RAM/RSS guard abort,
provider call or user-document access occurred.

Python compilation, four AST parses, all translation JSON parses, focused
Pylint error checks and `git diff --check` passed.
