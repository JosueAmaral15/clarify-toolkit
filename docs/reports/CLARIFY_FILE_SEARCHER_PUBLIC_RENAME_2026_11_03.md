# File Searcher Public Rename Evidence

## Scope

`FE-RENAME-FILE-SEARCHER-01` changes only the public product name from
**File Explorer** to **File Searcher**. It does not rename the Clarify Editor
Explorer, Python classes/modules, `file_explorer` tool and operation IDs,
persisted workspace/preset keys, the `clarify.file_explorer.results` format, or
the compatible `open_file_list` shortcut key.

## Reproduction

The initial focused regression failed on the existing English
`file_list.progress_title` value (`File Explorer`). The audit also found the old
public name in menu/status/tab labels, progress and busy messages, operation
history, the F1 shortcut action, AI explanation prompts, Information Structure
handoff text and the user manual.

The first post-change run exposed one test-only error: an assertion searched
for the English word `Explorer` while the active test language was Chinese. The
assertion was corrected to switch explicitly to English and verify the Clarify
Editor filesystem Explorer text remained unchanged. No product defect or native
failure was involved.

## Implementation

- All seven catalogs now expose localized File Searcher names for the tool,
  status, progress, busy state and history operations.
- Menu, tab, detached/dialog title and runtime language changes use the same
  existing translation keys.
- Shortcut customization and the generated F1 reference reuse the persisted
  `open_file_list` key and now display File Searcher. The effective default
  remains `Ctrl+Shift+L`.
- AI explanation and Information Structure handoffs use the new public name.
- The user manual distinguishes File Searcher from the Clarify Editor Explorer.
- Compatibility identifiers, settings and worker/lifecycle paths are unchanged.

## Validation

The guarded probe ran each GUI module in its own offscreen process with a
temporary HOME, 85% system-RAM guard, 600 MiB process-tree RSS guard, 180-second
wall limit and 20-second pytest timeout.

158 distinct focused tests passed:

- 3 public-rename/catalog/compatibility tests;
- 1 workspace runtime-i18n test;
- 18 live menu/tab/F1 tests;
- 10 shortcut-reference tests;
- 25 tab-layout/workspace-restore tests;
- 8 Search/Replace section tests;
- 7 replacement preflight/cache-confirmation tests;
- 10 translation-catalog tests;
- 14 i18n-expansion tests;
- 26 shortcut-manager tests;
- 36 File Searcher lifecycle tests.

Peak process-tree RSS was 254.9 MiB. There was no SIGSEGV, native Qt crash,
guard abort, provider access or user-document access.

Static validation passed for 11 changed Python files and all seven catalogs:
Python compilation, AST parsing, JSON parsing, Pylint error-only and
`git diff --check`.

## Compatibility Audit

Workspace/layout restoration still addresses `file_explorer`; existing settings
continue under the `FileExplorer` QSettings application name. Presets, cached
results, exact target scopes, Tree/Table state, replacement preflight and worker
ownership were not migrated or duplicated. Remaining source occurrences of
“File Explorer” are internal comments/docstrings or intentionally refer to the
Clarify Editor filesystem Explorer or the operating-system file manager.
