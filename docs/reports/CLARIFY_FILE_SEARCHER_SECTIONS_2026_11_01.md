# FE-SEARCH-REPLACE-SECTIONS-01 Evidence - 2026-11-01

## Scope

Implemented only `FE-SEARCH-REPLACE-SECTIONS-01` from checkpoint `5df3639` on
branch `COM-f4e804c5-81ba-4cee-8d30-2dad6169eedc`.

## Reproduced gaps

- Search inputs and destructive Replace controls shared one expanded section.
- Replace First and Replace All started enabled without a query or explicit
  result universe.
- No persistent bounded summary exposed the current file/match counts before
  the final replacement confirmation.

## Delivered contract

- Search and Replace are separate collapsible sections using the existing
  widgets and state. Replace starts collapsed in both Compact and Advanced
  presentations, without a duplicate query, replacement field or operation
  route.
- Replace actions remain disabled while another dock operation runs, while the
  query is empty or while no valid explicit file/selected-result universe is
  available.
- Existing single-file scope remains a valid one-file universe without sibling
  discovery. Folder and Selected Results scopes still require explicit visible
  result selection in the active Tree or Table view.
- The Replace section shows a bounded accessible count summary and a tooltip
  preview limited to five elided paths. Known match counts are shown only when
  every selected path belongs to the current search result identity.
- The same summary and bounded path preview appear in the existing final
  confirmation before the worker write route. This stage does not add preflight,
  implicit result reuse or any new write path.
- Runtime translation updates the new section/status and the reused
  `ReplacePanel` labels in all seven catalogs without replacing widget state.
- Exact scopes, result views, presets, cache identity/invalidation, pause,
  cancel, close, theme, compact sizing and default-off Reuse Previous Results
  behavior remain unchanged.

## Guarded validation

Each GUI module ran in a separate offscreen process with temporary HOME and
guards at system RAM 85%, process-tree RSS 600 MiB, wall 180 seconds and pytest
20 seconds including fixtures.

- `explorer-search-replace-sections`: 8 passed, peak 208.4 MiB.
- `explorer-presentation`: 43 passed, peak 216.7 MiB.
- `explorer-workspace-i18n`: 1 passed, peak 209.1 MiB.
- `explorer-target-scope`: 69 passed, peak 214.5 MiB.
- `explorer-replace`: 33 passed, peak 207.4 MiB.
- `explorer-incremental`: 8 passed, peak 214.9 MiB.
- `explorer-lifecycle`: 36 passed, peak 218.2 MiB.
- `explorer-table-refresh`: 2 passed, peak 202.5 MiB.
- `explorer-top-options`: 4 passed, peak 208.6 MiB.
- `i18n-expansion`: 14 passed, peak 65.4 MiB.
- `translation-catalog`: 10 passed, peak 186.4 MiB.
- Python compilation, four AST parses, seven translation JSON parses, focused
  Pylint-E and `git diff --check` passed.

No native crash, timeout, memory guard abort, provider call or user-document
operation occurred. `example.py` remains untracked and byte-identical at
SHA-256
`058053d87c818d699cde0f00d670bca0e1c6ad857caa9758ea6a556d7c64fcee`.
