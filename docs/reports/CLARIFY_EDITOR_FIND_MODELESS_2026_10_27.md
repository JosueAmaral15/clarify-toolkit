# Clarify Editor Modeless Find/Replace

## Scope

This stage implements only `CE-FIND-MODELESS-01` from checkpoint `fe9cc97` on
branch `COM-90f133b5-e40b-4b9b-a3c4-43fb6b8cf1ba`. It does not change AI
similarity search, File Explorer, application threading, TOON, WQXR or the
legacy backlog.

## Reproduction

Before the change, every Find or Find/Replace action constructed a new
`_EditorFindDialog`, called blocking `QDialog.exec()` and deleted it after the
nested event loop returned. An isolated regression intercepted `exec()` and
failed on that exact route. There was no lower-panel host, persisted
presentation mode or reusable workspace session.

## Delivered Contract

- One `_EditorFindDialog` instance belongs to each Editor workspace. Find and
  Find/Replace reuse it and change the visible controls instead of opening
  divergent sessions.
- The same widget moves between a lower docked panel and a floating modeless
  window. The selected mode and bounded floating geometry persist in the
  Editor's existing QSettings namespace.
- Selection prefill, query/replacement history, global match options, lexical
  and inverted scopes, line bounds, counters and Enter navigation keep their
  existing behavior. Switching tabs restores the private history of the new
  buffer; focusing a split retargets the same session to that active view.
- Closing the panel hides a reusable session. Closing the last document or the
  Editor disconnects document and translation signals, clears owner callbacks
  and schedules the widget for deletion, including when it is floating.
- All Find labels and the new dock/float command update on runtime language
  changes. The two new labels exist in all seven supported catalogs.

## Validation

All Qt modules ran serially, one GUI module per process, through
`qt_lifecycle_probe.py`. Each run used an isolated temporary HOME, offscreen
Qt, pytest timeout 20 seconds, wall limit 180 seconds, system RAM guard 85
percent and process-tree RSS guard 600 MiB.

| Module | Result | Peak tree RSS |
| --- | ---: | ---: |
| `test_editor_find_modeless.py` | 6 passed | 215.2 MiB |
| `test_editor_find_state_history.py` | 9 passed | 201.3 MiB |
| `test_editor_find_enter.py` | 9 passed | 198.7 MiB |
| `test_editor_find_scope_negation.py` | 8 passed | 192.3 MiB |
| `test_editor_recent_interactions.py` | 7 passed | 206.4 MiB |
| `test_editor_priority_stage3.py` | 8 passed | 198.5 MiB |
| `test_editor_find.py` | 18 passed | 71.0 MiB |
| `test_editor_dock.py` | 69 passed | 225.8 MiB |
| `test_editor_layout.py` | 20 passed | 249.2 MiB |
| `test_editor_quick_toolbar.py` | 8 passed | 226.4 MiB |
| `test_editor_status_info.py` | 9 passed | 212.9 MiB |
| `test_editor_recovery_reopen.py` | 5 passed | 207.2 MiB |
| `test_editor_temp_note_lifecycle.py` | 14 passed | 217.5 MiB |
| `test_editor_recovery_lifecycle.py` | 53 passed | 220.2 MiB |
| `test_editor_tab_copy_path.py` | 5 passed | 204.3 MiB |
| `test_editor_smart_home_visual.py` | 7 passed | 201.0 MiB |
| `test_translation_catalog_lookup.py` | 10 passed | 184.4 MiB |
| `test_i18n_expansion.py` | 14 passed | 64.7 MiB |

The 279 distinct tests passed without a native crash, timeout or resource-guard
abort. The initial pre-change regression failed only because the production
route invoked blocking `QDialog.exec()`, as intended by the reproduction.

Python compilation, seven JSON catalog parses, Pylint errors-only and
`git diff --check` passed. No provider, real user document, default branch or
dependency was changed. `example.py` stayed untracked and byte-identical.
