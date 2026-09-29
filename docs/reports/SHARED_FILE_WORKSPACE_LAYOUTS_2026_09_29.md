# Shared File Workspace And Layouts - Guarded Resume Completed

## Scope

User approved two new items, WS-MODE-01 and LAY-TABS-01, separate from the closed
FE-PAR queue and30 legacy items. Shared compact Search/Replace and advanced File
Explorer must retain target/query/options/results/selection; advanced filters remain
active with a visible summary. Repair registration and application-wide layouts.

Base627e9e5; branch COM-3e8d2f98-0024-4bec-9009-bc4fa830f809. Both new items are
complete after the explicitly authorized safe resume below, for a scoped local
commit. No push, promotion, native dispatch, provider call or real user document
operation. The original incomplete checkpoint and resource stop remain recorded.

## Implementation

- One FileExplorerDock and executor, not two synchronized copies. A shared mode
  selector above Directory Type changes presentation only. Existing filter,
  condition and preset widgets are hidden in compact mode without changing their
  effective values; a plain-text summary is limited to1024 characters.
- Standalone reusable SearchReplacePanel is retained for other consumers. Main
  workspace routes/UIBuilder use the single file workspace; separate Editing menu
  entry is removed. Old reopening paths map to the shared instance.
- Correct actual attribute registration (dock_editor/dock_file_explorer/etc.) and
  register lazy tabs/docks with stable IDs. Presets operate on tab-bar visibility,
  not visibility of pages inside QTabWidget; they do not close buffers. Compact
  can explicitly open only Editor if needed; startup layout restore does not
  automatically initialize unopened tools. Standard targets Editor/workspace/
  Rewriter already open; Advanced reveals open registered tabs.
- Custom snapshots retain tab order, logical visibility, active ID and workspace
  mode in existing QSettings, plus geometry/dock state. Legacy dock-only consumers
  and old search visibility keys have compatibility handling. Tab metadata bounds:
  128 records/64 KiB; invalid records rejected before UI mutations.
- Layout restore runs after tab restoration. Startup tab reconstruction must not
  overwrite its input snapshot; selection uses stable IDs with old-index fallback.
  Removed unconditional post-constructor1200x400 resize that overrode restored
  layouts; default size is set earlier. Lightweight Qt integration is validated;
  full application startup and interactive desktop E2E were intentionally excluded.

## Original Evidence And Resource Stop

Serial isolated .venv/offscreen validation with temporary HOME/settings/logs,
system RAM85%, tree RSS600 MiB, wall180s, pytest20s including fixtures. No full
MainWindow startup fixture; new tests use lightweight real Qt hosts and selected
MainWindow methods. Guard kills only its own validation process group.

| Module | Result | Seconds | Peak tree RSS MiB |
| --- | --- | ---: | ---: |
| tests/test_layout_manager.py | 14 passed | 1.19 | 83.9 |
| tests/test_tab_layouts.py | 20 passed | 5.88 | 235.9 |
| tests/test_shared_file_workspace.py | GUARD ABORT; no pytest pass summary | - | 125.8 |

The third process reached the **system RAM85% barrier**, was terminated by the
guard (signal15/guard exit125), and is not passing evidence. No isolated native
segfault was observed. The small process-tree peak does not establish what caused
system pressure, an application leak or an OOM. No unrelated process was stopped.
Initial system RAM72.1%; a subsequent snapshot was84.3% before the guard abort.

Automatic implementation/validation stopped at the barrier. No blind retry or
replacement run with weaker guards.34 distinct layout cases passed; workspace
tests, integrated regressions, screenshots and final static checks remain pending.
Historical FE05 combined Qt segfault remains unresolved; these layout passes do
not fix it or satisfy CI/security promotion gates.

## Resume Procedure Followed

Review the current diff first; preserve example.py and any new unrelated changes.
The exact monitor worker notebook-josue:codex:project=clarify-b09a84f1 remained
idle/current_task absent; no new worker, continuation or service change was made.
Authorized prior session019ea8a0-6d60-7f03-90b9-c420603158d1 was not dispatched to.

Resume only with safe memory headroom, keeping isolated one-GUI-module processes
and all guards. Start with tests/test_shared_file_workspace.py; fix ordinary test
failures, but stop on a native crash or guard barrier. Then validate layout/menu/
startup preference compatibility, both modes during operations, exact scopes/
cache/views, existing shared consumers and Editor recovery. Inspect optional Qt
captures before claiming visual correctness. Finish static/self-review checks and
commit locally only after the two new items are actually validated. No automatic
legacy work, push or promotion.

Remaining at the original checkpoint:2 new pending items +30 legacy =32 overall.
example.py unchanged:058053d87c818d699cde0f00d670bca0e1c6ad857caa9758ea6a556d7c64fcee.

## Authorized Resume And Final Evidence

The user closed applications and explicitly requested resumption. Fresh memory
verification showed approximately37.6% system use (later free output showed
2388MiB available of3799MiB). All original guards remained unchanged. Tests ran
serially with isolated temporary HOME/config/logs, one GUI module per process:

```bash
.venv/bin/python /tmp/clarify_guard.py .venv/bin/python -m pytest MODULE -q --timeout=20 --timeout-method=thread -o timeout_func_only=false
```

The guard checks system RAM85%, process-tree RSS600MiB and wall180s; fixture
timeouts are enabled. The guard script is a temporary validation runner, not a
new application service. Each row below has exit0 and guard reason=None.

| Module | Result | Seconds | Peak tree RSS MiB |
| --- | --- | ---: | ---: |
| tests/test_shared_file_workspace.py | 31 passed | 10.16 | 220.0 |
| tests/test_tab_layouts.py | 25 passed | 5.09 | 251.9 |
| tests/test_layout_manager.py | 14 passed | 0.96 | 85.2 |
| tests/gui/test_tools_menu_groups.py | 1 passed | 3.50 | 180.7 |
| tests/test_file_explorer_presentation.py | 43 passed | 8.39 | 213.8 |
| tests/test_file_explorer_internal_controls.py | 3 passed | 3.68 | 201.0 |
| tests/test_file_explorer_lifecycle.py | 36 passed | 7.91 | 211.9 |
| tests/test_file_explorer_enriched_conditions.py | 67 passed | 5.84 | 209.2 |
| tests/test_file_explorer_multi_query.py | 70 passed | 9.20 | 209.1 |
| tests/test_file_explorer_cross_line.py | 48 passed | 5.32 | 208.3 |
| tests/test_file_explorer_target_scope.py | 69 passed | 7.88 | 208.7 |
| tests/test_file_explorer_conditions.py | 60 passed | 4.01 | 199.2 |
| tests/test_file_explorer_replace.py | 33 passed | 4.23 | 203.1 |
| tests/test_file_explorer_incremental_search.py | 5 passed | 3.77 | 201.0 |
| tests/test_file_explorer_content_scope.py | 6 passed | 3.59 | 182.3 |
| tests/test_file_explorer_regex_coherence.py | 5 passed | 3.59 | 197.3 |
| tests/test_file_explorer_top_options_and_globs.py | 4 passed | 3.97 | 204.5 |
| tests/test_file_explorer_advanced_size_filters.py | 7 passed | 3.94 | 208.0 |
| tests/test_file_explorer_table_refresh.py | 2 passed | 3.60 | 199.3 |
| tests/test_file_explorer.py | 35 passed | 0.48 | 75.4 |
| tests/test_editor_recovery.py | 39 passed | 0.93 | 81.8 |
| tests/gui/test_editor_recovery_lifecycle.py | 53 passed | 13.69 | 212.8 |
| tests/gui/test_editor_dock.py | 67 passed, 2 deselected | 8.11 | 203.6 |

Total: **723 distinct focused tests,56 new**, across23 modules; repeated draft
runs are not added to this count. The2 converter_switch Editor cases were
explicitly deselected to avoid the existing full-MainWindow startup fixtures.
No resumed process hit a native crash or resource guard. These observations
are not a leak proof, complete-suite result, native Qt root-cause resolution
or CI/security gate clearance.

### Review Corrections

- Initial captures exposed the selector being clipped inside legacy horizontally
  scrolling controls. It now sits outside that scroll region, above Directory
  Type, with vertical exclusive mode buttons and palette-based checked styling.
  Button viewport geometry is tested at900/1200 pixels in light/dark themes,
  including horizontal scrolling.8 Qt captures are in
  /tmp/clarify-workspace-2026-09-29; four final representative captures were
  visually inspected across both modes, widths and themes. The legacy wide
  control rows still use explicit horizontal scrolling/splitter resizing;
  no hover expansion or wider control-layout redesign was introduced.
- Empty legacy open-tools lists no longer bypass fixed-tab selection restore.
  Insert uses the same identity-based route to reveal/reopen the existing
  instance and retain its buffer and registration. Tracked indices refresh
  from actual tab identities after closure, not stale pre-layout positions.
- Layout metadata validates UTF-8 byte bounds, active IDs and per-record shape
  before restoring UI. Hidden-tab initialization does not reveal layout-hidden
  tools. Existing dock-only API and old search visibility keys remain tested.
- Pylint initially reported Shiboken extension introspection and a pre-existing
  missing staticmethod on the touched factory's Placeholder Replacer helper.
  Used the existing direct Shiboken import pattern and added that decorator;
  a lightweight stub-dock test validates static calling and registration
  without initializing the real tool or provider.

### Static Checks And Preservation

- Guarded Pylint-E passed for8 production files, peak386.4MiB, exit0.
- AST parsing11 Python files and JSON parsing2 catalogs passed.
- Black check passed for the3 new files; git diff --check passed.
- Self-review: no second search state or worker, mode changes do not invalidate
  cache identity or broaden targets; shared SearchReplacePanel and its AI
  consumer remain intact. Existing presentation tests instantiate that panel
  and test the shared File List consumer. CE recovery/lifecycle tests preserve
  immediate-close buffers, quotas, original files and Save/Discard/Cancel.
- example.py retains the exact hash above and is excluded from staging.
  No unrelated applications, services or workers were stopped. The old monitor
  queue stays finished; no start/continuation/dispatch was issued for this work.
- Rollback is a revert of this scoped COM commit before any reviewed integration;
  permanent branches and remote state remain unchanged.

Current remaining work: **0 new items;30 legacy outside scope**. Full interactive
desktop/startup validation, historical FE05 native crash investigation and
CI/security promotion requirements remain open. No further task is started.
