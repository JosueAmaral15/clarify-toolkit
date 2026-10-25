# Clarify Editor Tab Copy Path

## Scope

This stage implements only `CE-TAB-COPY-PATH-01` from checkpoint `cc94ab1` on
branch `COM-073bbbd8-29b7-4eec-b280-04092dca7ef6`. It adds safe path-copy
actions to the Clarify Editor file-tab menu without changing File Explorer,
APP-THREAD or the legacy backlog.

## Reproduction

Before the product edit, the guarded tab-menu regression failed with
`KeyError: 'copy_absolute'`: the clicked file tab exposed close, split and mode
actions but no path-copy commands. The isolated process exited normally with a
201.2 MiB peak tree RSS and no native crash or guard abort.

## Delivered Contract

- `Copy Absolute Path` and `Copy Relative Path` are bound to the clicked tab,
  not implicitly to the currently active tab.
- The tab menu and Explorer panel use the same canonical-root resolver. The
  relative value is derived from the resolved target only when it remains
  inside the canonical root.
- Untitled/recovered buffers, temporary notes, missing paths, external paths
  and paths whose symlink resolution escapes the root disable both actions.
  Tooltips, status tips and What Is This text expose the specific reason.
- Actions revalidate the tab and current Explorer root when triggered, so a
  file removed after menu construction cannot publish a stale path.
- `_copy_path` verifies that it runs on the QApplication thread before touching
  the clipboard. A real Python worker-thread regression proves rejection while
  preserving existing clipboard content.
- Existing labels are reused. Scoped reason strings were added to the English
  and Portuguese catalogs, matching the catalogs that already carry these
  Editor path actions; general i18n parity remains outside this stage.

## Validation

Every GUI module ran serially through `qt_lifecycle_probe.py`, with temporary
HOME, offscreen Qt, pytest timeout 20 seconds, wall limit 180 seconds, global
RAM guard 85 percent and process-tree RSS guard 600 MiB.

| Module | Result | Peak tree RSS |
| --- | ---: | ---: |
| `test_editor_tab_copy_path.py` | 5 passed | 204.2 MiB |
| `test_editor_priority_stage4_explorer.py` | 7 passed | 204.2 MiB |
| `test_editor_priority_stage4_tabs.py` | 8 passed | 208.6 MiB |
| `test_editor_priority_stage5_sessions.py` | 12 passed | 212.5 MiB |
| `test_editor_priority_stage5_notes.py` | 5 passed | 203.2 MiB |
| `test_editor_recovery_lifecycle.py` | 53 passed | 218.3 MiB |
| `test_editor_dock.py` | 69 passed | 227.6 MiB |
| `test_editor_recent_interactions.py` | 7 passed | 204.8 MiB |
| `test_editor_find_state_history.py` | 9 passed | 202.1 MiB |
| `test_editor_find_scope_negation.py` | 8 passed | 194.3 MiB |
| `test_editor_smart_home_visual.py` | 7 passed | 202.4 MiB |

The 190 distinct tests passed without a native crash, timeout or guard abort.
Python compilation, Pylint errors-only, Black on the new test and diagnostic
files, seven JSON parses and `git diff --check` passed. No provider, real user
document, dependency or default branch was changed. `example.py` remained
untracked and byte-identical.
