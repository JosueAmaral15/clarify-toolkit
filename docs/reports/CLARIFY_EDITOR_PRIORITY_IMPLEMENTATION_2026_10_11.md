# Clarify Editor Priority Implementation - 2026-10-11

## Objective

Complete the open priority tasks owned by Clarify Editor before starting File
Explorer work. Preserve existing recovery, external-file detection, shared tool
consumers, user files and the unrelated untracked `example.py`.

## Audited State

- `CE-FIRST-SAVE-01`: basic Save As clears `is_modified`, but the complete
  transition (path identity, external state, recovery, recents and failure cases)
  lacks focused regression coverage and atomicity is inconsistent between tabs.
- `CE-INDENT-01`: menu actions exist, but `Tab` and `Shift+Tab` do not implement
  the requested editor behavior or a persisted tab/spaces preference.
- `CE-RECENT-01`: `recent_files` is memory-only; no recent folder list, menus,
  persistence, stale-path pruning or clear action exists.
- `CE-OPEN-PATH-01`: no text-path action exists. `open_file_path()` is the shared
  API and must remain the only file-opening implementation.
- `CE-FIND-01`: basic Case/Whole Word/Regex controls exist. Previous, current/total
  count, state persistence, line bounds and string/variable modes are absent.
- `CE-EXPLORER-CONTEXT-01`: the Editor Explorer has no context menu.
- `CE-TAB-CONTEXT-01`: the tab menu only toggles edit-only mode. The tab bar is
  already movable, but bulk close and split contracts are absent.
- `CE-TAB-SYNC-01`: tab activation does not reveal the corresponding Explorer item
  and moved-tab order is not persisted.
- `CE-FOLDER-SESSION-01`: folder-specific tab references/order/active tab are not
  persisted or restored.
- `CE-TEMP-NOTES-01`: emergency recovery exists, but there is no user-managed
  persistent temporary-note store or UI.

`APP-TOON-PRIMARY-01` is a cross-application migration, not an Editor-only feature.
It follows functional Editor completion as its own architecture stage.

## Stages

1. **File state and keyboard editing**
   - Complete first-save settlement and atomic text writes.
   - Implement Tab/Shift+Tab with persisted tab/spaces width preferences.
   - Validate text and JSON tabs, cancellation, IO failure, recovery and watchers.
2. **Opening and recents**
   - Persist bounded recent files/folders with stale-entry pruning and clear menus.
   - Add Open by Path using `open_file_path()` with explicit path validation.
3. **Find**
   - One bounded matcher contract for next/previous/count/replace.
   - Persist options, add line range and string/variable scope without GUI blocking.
4. **Explorer and tab workflows**
   - Context menus, absolute/relative paths, safe rename/delete/new/reveal/analyze.
   - Bulk-close contracts, split ownership, tab-to-tree sync and reorder persistence.
5. **Folder sessions and temporary notes**
   - Bounded folder reference sessions integrated with recovery.
   - Private atomic note storage, manual delete by default and optional retention.

## Safety And Validation

- Use only temporary HOME and temporary files in tests; never modify user documents.
- Keep Qt widgets/models on the GUI thread. No worker is added without measured
  blocking IO or processing.
- Run offscreen, serial, one GUI module per process, with RAM 85%, tree RSS 600 MiB,
  wall 180 s and pytest timeout 20 s guards.
- Commit each validated stage on the current COM branch. A failed native Qt process,
  guard abort or unresolved data-loss regression stops the stage without masking it.
- Rollback is one stage commit at a time; no main/develop promotion is part of this
  implementation run.

## Stage 1 Result - Complete

Implemented `CE-FIRST-SAVE-01` and `CE-INDENT-01`.

- Added a shared atomic UTF-8 writer for new/existing regular files. It rejects
  symbolic/hard links, preserves bounded metadata and detects replacement races.
- Successful Save/Save As now settles path identity, dirty/document state,
  edit-only mode, auto-save timer, watcher baseline, recovery snapshot, recents,
  title and menu state only after the write succeeds.
- Tab and Shift+Tab now operate inside text and JSON editors with persisted tabs
  versus spaces and width 1-8. Other modifiers and read-only editors retain Qt
  behavior; line selections and undo remain coherent.

Distinct passing cases: 203 (5 new stage regressions, 3 atomic-file tests, 67
EditorDock, 16 edit-only, 53 recovery lifecycle, 20 layout and 39 recovery-store).
Peak observed test-tree RSS was 242.9 MiB. No native Qt crash occurred.

Two resource/test events are retained honestly:

- One run was stopped before collection at global RAM 85.1%, and one recovery run
  was stopped at global RAM 85.0%; both later completed from the beginning.
- The first layout run passed 19/20 and timed out waiting for one hidden `.env`
  model row. That exact case passed in isolation and the full 20-case module then
  passed. This is an existing asynchronous-model flake, not proof it is fixed.

Compile/AST, two JSON catalogs, Pylint error checks and `git diff --check` passed.
Black was applied only to the new isolated files because pre-existing modified
modules are not globally Black-clean and broad formatting would add unrelated churn.

## Stage 2 Result - Complete

Implemented `CE-RECENT-01` and `CE-OPEN-PATH-01`.

- File now contains separate recent-file and recent-folder submenus. Both retain
  at most 10 normalized paths in Editor QSettings, deduplicate by most recent use,
  prune missing entries and clear independently without storing file content.
- The existing graphical Open action and the new Open by Path action converge on
  `open_file_path()`. Existing tabs are reused by normalized path identity.
- Typed paths accept absolute values, values relative to the current Explorer root,
  home expansion, spaces and Unicode without shell interpretation. Validation is
  bounded to 4096 path characters and 16 MiB files and reports empty, missing,
  directory, symbolic-link, irregular-file, unreadable and stat failures.

Distinct complete passing cases: 98 (11 new Stage 2 regressions, 67 EditorDock and
20 Editor layout). Peak observed tree RSS was 246.5 MiB; no native Qt crash occurred.
Compile, two JSON catalog parses, Pylint error checks and `git diff --check` passed.

Resource limitation retained honestly: two EditorDock/recovery attempts were
stopped by the system-RAM 85% guard while unrelated npm/Next/Playwright processes
from another workspace were active. The first EditorDock retry later passed all 67
cases. The recovery retry reached 18/53 before a global 85.3% stop with its own tree
at 212.1 MiB; it is not counted as pass evidence. The same 53-case recovery module
passed in Stage 1 before this Stage 2 menu/opening change.
