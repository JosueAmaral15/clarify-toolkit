# Clarify Editor Dense Untitled Names

## Scope

This stage implements only `CE-UNTITLED-DENSE-NAMES-01` from checkpoint
`dc6b7c0` on branch `COM-f2ce947a-7674-40b4-8bb3-64169750d06c`. It does not
change read-only theming, Find highlighting, the temporary-note toolbar, F2,
File Explorer, application threading, multi-window behavior or legacy work.

## Reproduction

The pre-change Editor created `Untitled`, `Untitled-2` and `Untitled-3` from a
monotonic historical counter. Closing the second tab left `Untitled` and
`Untitled-3`; moving tabs also moved their stale labels instead of deriving
names from current visual order. The guarded regression failed on this exact
state at 201.1 MiB peak tree RSS, without a native crash or guard abort.

## Root Cause And Fix

- `_new_file()` incremented `untitled_counter` for the lifetime of the dock and
  replaced each tab instance's `get_tab_title()` with a closure containing that
  historical number.
- The counter and method override were removed. `_prepare_tab_for_dock()` now
  gives every tab a private UUID in `_clarify_buffer_identity`; this identity
  does not change when the visible name, position or backing changes.
- `_renumber_untitled_tabs()` derives only the mutable display label from the
  current order of unnamed tabs. File paths, explicit generated names and
  temporary-note titles are excluded from this sequence.
- Renumbering runs after structural transitions: create, close, reorder,
  successful Save As, temporary-note adoption, file conversion and folder-tab
  detachment. The split header is refreshed without replacing its shared
  document or changing focus.
- Recovery snapshots with historical names such as `Untitled-17` are restored
  as unnamed buffers and join the dense sequence. Their snapshot IDs and
  content remain unchanged. Named recovery, generated JSON/text and notes keep
  their explicit titles.

Find history retains its existing private identity, and recovery snapshots
retain their existing IDs. Neither subsystem uses the mutable display label as
a key. Dirty markers continue to follow actual document modification state.

## Validation

Every Qt module ran serially in its own offscreen process through
`qt_lifecycle_probe.py`, with temporary HOME, pytest timeout 20 seconds, wall
limit 180 seconds, system RAM guard 85 percent and process-tree RSS guard
600 MiB.

| Module | Result | Peak tree RSS |
| --- | ---: | ---: |
| `test_editor_untitled_dense_names.py` | 8 passed | 214.8 MiB |
| `test_edit_only_mode.py` | 16 passed | 213.9 MiB |
| `test_editor_dock.py` | 69 passed | 228.0 MiB |
| `test_editor_open_clean_state.py` | 10 passed | 210.3 MiB |
| `test_editor_priority_stage1.py` | 6 passed | 211.2 MiB |
| `test_editor_priority_stage2.py` | 11 passed | 212.5 MiB |
| `test_editor_priority_stage3.py` | 8 passed | 200.9 MiB |
| `test_editor_priority_stage4_tabs.py` | 8 passed | 211.7 MiB |
| `test_editor_priority_stage5_sessions.py` | 12 passed | 217.1 MiB |
| `test_editor_recovery_lifecycle.py` | 53 passed | 219.4 MiB |
| `test_editor_recovery_reopen.py` | 5 passed | 209.0 MiB |
| `test_editor_recovery.py` | 39 passed | 63.7 MiB |
| `test_editor_temp_note_lifecycle.py` | 14 passed | 219.0 MiB |
| `test_editor_priority_stage5_notes.py` | 5 passed | 205.1 MiB |
| `test_editor_find_state_history.py` | 9 passed | 203.0 MiB |
| `test_editor_find_modeless.py` | 6 passed | 216.8 MiB |
| `test_editor_status_info.py` | 9 passed | 214.5 MiB |
| `test_editor_layout.py` | 20 passed | 255.2 MiB |
| `test_editor_quick_toolbar.py` | 8 passed | 228.5 MiB |
| `test_editor_menu_shortcuts.py` | 8 passed | 216.5 MiB |
| `test_editor_recent_interactions.py` | 7 passed | 208.5 MiB |
| `test_editor_tab_copy_path.py` | 5 passed | 205.9 MiB |
| `test_editor_redo_shortcuts.py` | 6 passed | 210.1 MiB |

The 342 distinct tests passed without native crash, timeout or guard abort.
They cover dense create/close/reorder behavior, stable identities, dirty
markers, Save As, temporary notes, legacy recovery, splits, folder sessions,
Find history, recent files, path actions, toolbar, shortcuts and clean opens.

Python compilation, focused Pylint errors-only, Black for the new regression,
probe-key AST validation, canonical task-ID validation and `git diff --check`
passed. No provider, real user document, default branch or dependency changed.
`example.py` stayed untracked and byte-identical.
