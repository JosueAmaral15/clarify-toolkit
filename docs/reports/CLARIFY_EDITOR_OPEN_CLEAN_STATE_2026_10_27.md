# Clarify Editor Clean File-Open State

## Scope

This stage implements only `CE-OPEN-CLEAN-STATE-REGRESSION-01` from checkpoint
`42357c3` on branch `COM-1c5e398c-e4c0-4e73-8ef2-69fac8806235`. It does not
change Untitled numbering, read-only theming, Find highlighting, F2, File
Explorer, application threading, multi-window behavior or the legacy backlog.

## Reproduction

A temporary offscreen Editor opened the same bounded content as text and JSON.
Both tabs were initially clean. After the initial highlighter event settled,
the text tab changed to `is_modified=True` and displayed `sample.txt *`, while
`QTextDocument.isModified()` remained `False`; JSON remained clean.

The focused pre-change regression reproduced that exact state after 900 ms:
one failed test, peak tree RSS 201.9 MiB, no native crash and no resource-guard
abort.

## Root Cause And Fix

- `EditorTab(file_path)` installed a `SyntaxHighlighter` during construction.
  `load_file()` installed a second highlighter after resetting the dirty flag.
- The second highlighter's deferred character formatting emitted
  `QTextEdit.textChanged`. `_on_text_changed()` treated every such notification
  as a content edit even though the document modification flag was false.
- `_setup_highlighter()` now reuses the current highlighter when document and
  file type match, and safely detaches it before a genuine type change.
- Text and JSON dirty-state handlers now require
  `QTextDocument.isModified()`. Presentation-only formatting cannot mark a tab
  dirty, while keyboard/content edits still do.

No watcher, recovery, recent-file, Save/Discard/Cancel or tab-title API was
replaced. Failed UTF-8 reads still publish neither a tab nor a recent entry;
external disk changes remain a separate `[external]` state.

## Validation

Every Qt module ran serially in its own offscreen process through
`qt_lifecycle_probe.py`, with temporary HOME, pytest timeout 20 seconds, wall
limit 180 seconds, system RAM guard 85 percent and process-tree RSS guard
600 MiB.

| Module | Result | Peak tree RSS |
| --- | ---: | ---: |
| `test_editor_open_clean_state.py` | 10 passed | 210.1 MiB |
| `test_editor_dock.py` | 69 passed | 226.1 MiB |
| `test_editor_priority_stage1.py` | 6 passed | 210.4 MiB |
| `test_editor_priority_stage2.py` | 11 passed | 211.3 MiB |
| `test_editor_priority_stage4_tabs.py` | 8 passed | 211.6 MiB |
| `test_editor_priority_stage5_sessions.py` | 12 passed | 215.9 MiB |
| `test_editor_rename_imports.py` | 7 passed | 207.5 MiB |
| `test_editor_recovery_lifecycle.py` | 53 passed | 217.8 MiB |
| `test_editor_recovery_reopen.py` | 5 passed | 208.1 MiB |
| `test_editor_temp_note_lifecycle.py` | 14 passed | 217.8 MiB |
| `test_editor_priority_stage5_notes.py` | 5 passed | 204.1 MiB |
| `test_editor_status_info.py` | 9 passed | 211.7 MiB |
| `test_editor_quick_toolbar.py` | 8 passed | 226.7 MiB |
| `test_editor_layout.py` | 20 passed | 252.4 MiB |

The 237 distinct tests passed without native crash, timeout or guard abort.
They cover text/JSON open settlement, recent reuse, edit-only detachment, real
edits, invalid decoding, empty read-only splits, external changes and reload,
first Save As, folder sessions, rename, recovery, notes, status, toolbar and
layout.

Python compilation, focused Pylint errors-only, probe-key AST validation,
format checking of the new regression module and `git diff --check` passed. The
two touched product modules have broader pre-existing Black differences and
were not mechanically reformatted. No provider, real user document, default
branch or dependency was changed. `example.py` stayed untracked and
byte-identical.
