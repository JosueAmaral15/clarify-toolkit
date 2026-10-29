# Clarify Editor Read-Only Theme

## Scope

This stage implements only `CE-READONLY-THEME-01` from checkpoint `aab693f` on
branch `COM-ccf0b7a8-dad8-4f6e-874d-66e9bc4cb690`. It does not change Find
highlighting, the temporary-note toolbar, Explorer F2, File Explorer,
application threading, multi-window behavior or legacy work.

## Reproduction

The isolated regression enabled the Dark theme and created a text tab in
Edit-Only mode. Before the fix, `EditorTab._update_visual_indicators()` applied
`background-color: #FFF8DC` and `color: #000000` directly to `QTextEdit`.
The regression failed on the fixed background declaration at 195.1 MiB peak
tree RSS, without a native crash or guard abort.

## Root Cause And Fix

- The local Edit-Only QSS owned the editor background and foreground, so it
  overrode the application palette in Dark, Light and System themes.
- The Edit-Only visual rule now owns only its gold border. Background,
  foreground, selection and cursor colors remain controlled by the active
  application theme.
- Text and JSON tabs expose the mode through the `clarifyEditOnly` dynamic
  property and a translated accessible description. Runtime language changes
  refresh that description through the existing Editor retranslation path.
- Edit-Only remains the existing editable sandbox state; it is not silently
  converted into Qt read-only mode. Actual `QTextEdit.setReadOnly(True)` views
  remain non-editable and follow runtime theme changes.
- JSON validation keeps its existing border-only diagnostic style. Syntax
  highlighting, content, selection, undo state, Find extra selections and
  shared split documents are not replaced during mode changes.

## Validation

Every Qt module ran serially in its own offscreen process through
`qt_lifecycle_probe.py`, with temporary HOME, pytest timeout 20 seconds, wall
limit 180 seconds, system RAM guard 85 percent and process-tree RSS guard
600 MiB.

| Module | Result | Peak tree RSS |
| --- | ---: | ---: |
| `test_editor_readonly_theme.py` | 7 passed | 207.0 MiB |
| `test_edit_only_mode.py` | 16 passed | 214.3 MiB |
| `test_theme_manager.py` | 14 passed | 68.1 MiB |
| `test_editor_dock.py` | 69 passed | 227.4 MiB |
| `test_editor_open_clean_state.py` | 10 passed | 211.1 MiB |
| `test_editor_untitled_dense_names.py` | 8 passed | 214.9 MiB |
| `test_editor_layout.py` | 20 passed | 255.9 MiB |
| `test_editor_status_info.py` | 9 passed | 215.1 MiB |
| `test_editor_recovery_reopen.py` | 5 passed | 209.7 MiB |
| `test_editor_temp_note_lifecycle.py` | 14 passed | 219.7 MiB |
| `test_editor_find_modeless.py` | 6 passed | 217.8 MiB |
| `test_editor_priority_stage4_tabs.py` | 8 passed | 211.8 MiB |

The 186 distinct tests passed without native crash, timeout or guard abort.
Focused Pylint errors-only, Python compilation and `git diff --check` passed.
The new regression was Black-formatted. Existing source files were not
mechanically reformatted because their current repository style differs from
Black and broad churn is outside this stage. No provider, real user document,
default branch or dependency changed. `example.py` stayed untracked and
byte-identical.
