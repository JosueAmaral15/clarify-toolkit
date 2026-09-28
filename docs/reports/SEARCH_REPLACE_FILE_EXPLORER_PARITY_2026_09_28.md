# Search/Replace And File Explorer Feature Review

Date: 2026-09-28. Scope: the active SearchReplacePanel imported by panels/__init__,
its worker/core helpers, FileExplorerDock, shared widgets, executor/worker,
ResultsTree, consumers, tests and current backlog. BACKUP/NEW panel files are
not active implementations. This is an inspection and recommendation, not a
feature implementation or a declaration that either full tool passes E2E tests.

## Inventory

| Search/Replace resource | File Explorer status | Decision |
| --- | --- | --- |
| Folder selection and browsing | Present, plus recent directories | No new feature |
| Is File / direct single-file input | Missing: dock rejects non-directory roots | Add explicit single-file scope |
| Extension filter enable/disable and extension list | Present in FileFilterPanel | Do not duplicate; consider visibility only |
| Include/exclude globs | Present in main directory section | No new feature |
| Filename/content/both queries | Present, with separate filename regex support | No new feature |
| Case Sensitive, Whole Word, Regex | Present globally | No new controls needed |
| Multiline input editor | Present | Input widget does not imply cross-line matching |
| Multiple independent queries | Checkbox present, executor ignores multi_query | Complete semantics, do not add duplicate checkbox |
| Search spanning newline boundaries | SearchWorker matches whole text; Explorer searches individual lines | Add bounded cross-line text search |
| Replace first per file / all occurrences | Controls/core present | Repair integration before expanding targets |
| Preserve Case | Checkbox and core present, dock does not pass its value | Wire existing option |
| Replacement applied to candidate file set | Explorer handlers use table selections only | Unify tree/table selection and explicit target scope |
| AND/OR dynamic conditions, add/remove/clear | Present, but execution differs in important cases | Repair shared condition semantics |
| Per-condition Case and Regex | Present, with incomplete execution paths | Repair rather than add controls |
| Per-condition Whole Word | Missing from ConditionsGrid | Add alongside shared evaluator |
| Starts With / Ends With condition operators | Missing from ConditionsGrid; shared Condition supports them | Add operator choices |
| Content scopes and scope parameter | Missing from ConditionsGrid | Add brackets/braces/parentheses/custom/tag/specific-tag scope UI |
| Progress and cancellation | Present via QProgressDialog and worker | Keep current equivalent |
| Pause/resume, shared progress manager / thread registration | SearchWorker supports pause; Explorer executor flags are not consumed by loops and UI has no pause | Add genuine cooperative pause and lifecycle integration |
| ProcessingModal with retained per-file logs | Explorer uses another progress dialog, plus history | Optional bounded log summary, not wholesale modal replacement |
| Sort results, position status | Present | No new feature |
| ResultsTree context actions | Same shared class in both | No port needed |
| Save results as TXT and operation history | Present | No new feature |
| Shared query/replacement editor font settings | Search panel setter is called by MainWindow; Explorer widgets have unused setters | Optional consistency improvement |
| Results expand when hovered | Explorer deliberately removed this behavior | Do not restore automatically |
| replace_requested signal / emit_replace_request | Used by AI Processor for its own generated results | Preserve shared capability; Explorer does not need to expose it merely for parity |
| request_preview signal | Declared but not emitted/connected in active panel | Not a working preview feature to port |

ResultsTree already shares Copy, Copy All Results/Content, JSON copy/export,
AI explanation preparation, folder map, file deletion/full-content replacement,
selection, Editor/open-and-switch, system open, location and properties actions.
These are not missing Search/Replace features in Explorer's tree view. Tree/table
consistency should be audited separately; the shared class is not proof that
every table action has equivalent behavior.

File Explorer additionally has browse mode, hidden/recursive/type filters,
size/date/depth filters, presets, table/tree switching, word wrap, statistics,
CSV export, incremental candidate filtering, bounded result snippets/match counts
and Text/ASCII/Binary/Both content search. Preserve these and their memory limits.

## Recommended Order

### First: Repair Existing Parity

1. **Replacement contract and Preserve Case.** Dock handlers omit preserve_case,
   call the executor synchronously, and expect success/replacements_made/error,
   while it returns replaced_count/files_modified/errors. The worker replace
   wrapper uses search_text/replace_text instead of the executor's argument names.
   Normalize the contract, handle partial failures, pass the existing checkbox,
   and use a cancelable background operation. Add UI-to-real-executor tests.
2. **Advanced-condition correctness.** Browse/early search use shared Condition;
   numeric UI names such as greater than are incompatible with its symbolic OPS.
   Late content conditions merely test match_count, ignoring their requested
   value/operator/options. Splitting early and late conditions also breaks mixed
   OR expressions. Reuse one canonical condition evaluator and typed operators;
   preserve complete AND/OR meaning and fail visibly on unsupported conditions.

These are existing-feature repairs, not justification for another copy of the UI.
Transactional backup/Undo/rollback is additional safety work already related to
LEG-24; neither tool's plain replacement path is a safe model to copy wholesale.

### Then: Complete Useful Search Capabilities

3. **Single-file scope.** Accept an explicitly selected file without scanning its
   siblings. A target scope control can cover Folder / File / Selected results.
   Use the current tree or table selection as appropriate. Replacing all results
   must require explicit choice/confirmation and preview, not silently expand
   from the current selection to the entire filesystem candidate set.
4. **True cross-line search.** Define a text-span mode independently from multiple
   queries. Preserve accurate line/column positions, cancellation, byte/match
   limits and regex safety; do not load arbitrary huge files just to gain parity.
5. **Multiple independent queries.** Connect the existing checkbox to explicit
   one-query-per-line behavior, blank/comment handling, validation and duplicate
   match policy. Reuse MultiQueryProcessor's useful semantics without copying its
   silent invalid-regex fallback. Retain query identity if users need grouped
   results; define replacement ordering/overlap before multi-query replacement.
6. **Condition scopes, Whole Word, Starts/Ends With.** Reuse Condition and scope
   helpers; add the missing controls and serialize them consistently into presets
   and executor requests. Do this after condition correctness, not before.
7. **Pause/resume and operation coordination.** Add cooperative checkpoints to
   enumeration/search and result emission, not just an unused flag. Cancellation
   must unblock a paused operation and closing the tool must release the worker.
   Integrate shared thread/progress coordination without duplicate dialogs or
   unbounded retained logs. Never pause mid-write without a safe transaction.

### Optional Polish

8. Propagate the shared monospace/font preferences to query/replacement editors.
   Consider making the existing extension-filter state more discoverable and
   adding bounded per-file completion logs. These are lower priority than the
   correctness fixes and actual missing capabilities.

Do not transfer hover expansion, unconditional batch overwrites, duplicate
results actions, a mandatory new modal, unused signals, or AI result-editing
behavior that belongs to the existing reusable SearchReplacePanel consumer.

## Evidence And Limitations

Seven disposable probes ran under offscreen Qt with temporary HOME/settings,
15-second per-test timeout, process-tree monitoring and the 85% system RAM guard.
All seven passed their diagnostic assertions in 4.70s; peak RSS 188.1 MiB.
Passing here means reproducing the stated behavior/gaps, not healthy product
tests. They confirmed:

- SearchWorker finds a literal alpha-newline-beta span; Explorer returns no match.
- Explorer multi_query=True does not search independent alpha/beta queries.
- A content condition contains absent still retains a needle result.
- Shared numeric Condition succeeds with > but not the UI's greater than.
- A matching content OR branch is lost when the early filename branch fails.
- Executor replacement output lacks the success/replacements_made keys the dock
  consumes (tested with no files; no user file modified).
- SearchReplacePanel's ordinary content-search launch raises AttributeError on
  its undeclared error signal path before worker startup.

Additional static findings: the source panel's multi-query path requires an
ed_query_multi attribute not created by its constructor; its current-progress
widget reference is not initialized in all paths. Thus advertised source features
are not all proven working. No full Search/Replace GUI run, live provider call,
filesystem-wide scan or destructive operation was performed. Tests used only
dummy temporary content. Diagnostic source remains outside the repository at
/tmp/test_clarify_feature_parity_20260928.py, not production code.

Source pointers: SearchReplacePanel lines 402/513/609/904; SearchWorker 73;
search_widgets ConditionsGrid 342 and get_options 216; FileExplorerDock 991/1618/
1709; executor 294/454/594/694; filters Condition 209; ResultsTree menu 737;
MainWindow font hook 337. Existing GUI integration tests often check widget/method
presence rather than these end-to-end contracts; new tests should exercise them.

The 2025 comparison and completion claims are historical, not current evidence.
This review creates recommendations only: TASKS.md still has **30 open items**,
and no new implementation requirements were silently added to that count. Existing
Editor header/hidden-file edits and example.py are preserved, with no commit,
push, merge, deletion or application source edits during this comparison.
