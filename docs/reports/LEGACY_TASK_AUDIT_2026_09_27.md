# Legacy Task Audit - 2026-09-27

## Scope And Execution Plan

Review all 36 nonstandard markers in `docs/TASKS.md` in their original order.
Keep the original requirements, assign stable LEG identifiers, and distinguish
working implementations, partial work, duplicates, and historical headings.
Source inspection establishes implementation scope, not end-to-end correctness.

1. Inspect source, menu integration, persistence, and existing tests per marker.
2. Fix confirmed data-editing defects first: regex insertion order, error handling,
   undo preservation, and literal register substitution. Add regression tests.
3. Run bounded offline tests with temporary settings; include Editor layout tests.
4. Publish the 36-row evidence matrix and one canonical remaining-work queue.

No cloud credentials, network providers, model downloads, user files, commits, or
pushes are needed for this audit. Existing dirty changes must remain untouched.
Rollback means reverting only this audit's individual hunks, never the worktree.

## Result

The 36 markers represent **9 implemented items, 23 distinct open items,
3 duplicate requests, and 1 historical roadmap heading**. Open items include
partial implementations, validation, and large future features; they are not
23 confirmed broken features. Three environment checks and one newly recorded
Qt lifecycle investigation are separate: **27 canonical open entries in total**.
No original requirement was deleted.

The canonical open queue is in [TASKS.md](../TASKS.md). LEG identifiers follow
the original marker order, not priority. "Implemented" describes the original
scope supported by source and the focused checks below, not production readiness.

## Evidence Matrix

| ID | Status | Requirement, evidence, and remaining scope |
| --- | --- | --- |
| LEG-01 | Implemented; repaired | Regex capture registers and insertion are connected in [JsonEditorTab](../../src/gui/json_editor_tab.py) and [RegexInsertPanel](../../src/gui/panels/regex_insert_panel.py). Fixed root sibling order, lost Undo history, duplicate-key overwrites, broken exception handling, and recursive/partial register substitution. |
| LEG-02 | Partial | [InsertPanel](../../src/gui/panels/insert_panel.py) supports line insertion and first/last/all search occurrences. Group boundaries, explicit column placement and occurrence thresholds are not implemented by [insert_at_line](../../src/core/insert.py). |
| LEG-03 | Partial | [AdvancedExtractor](../../src/extractors/advanced_extractor.py) substitutes class names; [UnifiedTextToJsonDock](../../src/gui/unified_text_to_json_dock.py) exposes the option. A distinct class-name-differences mode is absent; comparison semantics need definition. |
| LEG-04 | Implemented | [EditorDock](../../src/gui/editor_dock.py) has File auto-save, document tabs, and explicit unsaved recovery through [UnsavedRecoveryStore](../../src/editor_recovery.py). Recovery is not a claim of automatic restoration of every clean tab. |
| LEG-05 | Planned | File Explorer has no image/video semantic index. Existing AI Processor/multimodal preflight is not CV search. Preserve natural-language queries, CLIP/provider choice, color/object/face/OCR/EXIF filters, previews, SQLite cache, bounded indexing, HEIC and video-frame support. |
| LEG-06 | Planned | [AI Processor](../../src/ai_processor/processor.py) reads bounded files but does not expose the requested chunk policy. Preserve optional byte/unit or count modes, model-token helper, and 1-99% capacity control. Google Translate's character chunker is not this feature. |
| LEG-07 | Partial | [Google Translate](../../src/gui/google_translate_dock.py), [format mapping](../../src/translation/format_mapper.py), PDF and notebook translation exist. Gemini-first quick text and rich-document translation with AI Processor chunking/output selection is not an equivalent completed workflow. Depends on LEG-06. |
| LEG-08 | Historical | Sprint-plan heading containing other tasks; it is not another deliverable. Its child requests are audited independently. |
| LEG-09 | Implemented | [CONTRIBUTING.md](../../CONTRIBUTING.md) covers conduct, reports, setup, style, tests and PRs. The unchecked entry duplicated a historical completion directly above it. |
| LEG-10 | Validation | Current [catalogs](../../src/i18n) pass key-parity/encoding checks. The old 90-keys-times-6 estimate is obsolete; it must not cause 540 duplicate translations. Review current English-identical UI strings in context and linguistic quality before claiming complete localization. |
| LEG-11 | Planned | No content/name-context file organizer was found in active source/menu paths. Requires preview, collision policy and reversible moves, not unattended relocation. |
| LEG-12 | Partial | [TOON adapter](../../src/converters/toon.py) and [converter factory](../../src/converters/factory.py) provide conversion/validation. A multi-file hierarchical JSON/TXT/TOON workspace with ID/hierarchy search, selective editing and merge remains distinct work. |
| LEG-13 | Planned | [JSON query parser](../../src/json_search/query_parser.py) is not a relational engine. Preserve SELECT, JOIN, aggregates and complex filters, plus JSON/TOON and NoSQL-style operations from LEG-30. |
| LEG-14 | Planned | Formula execution is not arbitrary Python sandboxing or block programming. Preserve both macro interfaces and scheduling. Resource isolation, filesystem/network permissions and cancellation must precede execution. Includes LEG-26. |
| LEG-15 | Planned | [cloud_sync.py](../../src/cloud_sync.py) contains only an abstract provider and DummyProvider. Drive/Dropbox/OneDrive, preset sharing, version diffs, comments and conflict handling are not implemented. |
| LEG-16 | Partial | [JsonEditorTab](../../src/gui/json_editor_tab.py) and EditorDock implement validation diagnostics, schema key completion and top-level missing-required-field fixes. Schema-based value suggestions remain; do not count key completion as value completion. |
| LEG-17 | Planned | No GraphQL query/mutation integration found. Preserve nested queries, aliases, fragments and mutations; read-only query implementation should precede writes. |
| LEG-18 | Planned | No Git client integration found in active tools. Preserve status/diff, commits, branches, conflict resolution, push and pull; external repository changes require explicit user actions. |
| LEG-19 | Partial | [tutorials](../../src/gui/tutorials_dock.py) and [TutorialAssistant](../../src/tutorial_assistant.py) exist. Adaptive usage-pattern suggestions, automation recipes and low-code guidance are not implemented; reuse the macro foundation from LEG-14. |
| LEG-20 | Implemented | Tutorial browser, Help menu wiring, and [tutorial index](../tutorials/index.json) exist. Tests verify every indexed tutorial file exists. This does not claim every feature has a tutorial. |
| LEG-21 | Partial | [ResultsTree](../../src/gui/panels/results_tree.py) can prepare bounded AI explanations of results. That does not implement semantic/natural-language cross-file retrieval like the requested AI search. |
| LEG-22 | Implemented; live unverified | [TutorialAssistantDialog](../../src/gui/tutorial_assistant_dialog.py), Help menu wiring and per-request Gemini clients exist. Mocked provider tests pass; live credentials/provider quality were not exercised. |
| LEG-23 | Planned | Python project/build metadata and launchers exist, but Linux app-manager distribution research and a reproducible installable artifact are not established by them. Compare target formats, build/install/uninstall and maintenance costs before publication. |
| LEG-24 | Partial | [CommandManager](../../src/core/command_manager.py) exists and MainWindow creates it, but no production execute_command call sites were found. Editor Undo/recovery does not provide application-wide transactional file undo. Failed undo/redo currently removes the command before success; multi-file rollback and byte-bounded history need attention. |
| LEG-25 | Planned | No Egg Cell Compactor/AI long-term change ledger exists. Define this format, losslessness, retention, privacy, storage budget and restore guarantees before implementation; retain the original intent rather than equating ECC with ordinary compression. |
| LEG-26 | Duplicate of LEG-14 | Python/block macros and composed application operations retained in LEG-14. |
| LEG-27 | Implemented; completed here | Search and Insert share [ResultsTree](../../src/gui/panels/results_tree.py). Added result activation through double-click/Enter to the existing open-and-switch action; directory/summary activation never opens every descendant. Single-click still selects. Feedback callbacks now use the label's Qt lifetime. |
| LEG-28 | Partial | [algorithm_analysis.py](../../src/algorithm_analysis.py) supplies bounded review prompts and Python AST context, not generation/compilation/transpilation. Define target Python/JS/React outputs and preview/validation without automatically executing generated code. |
| LEG-29 | Implemented | TOON conversion, detection, validation and JSON/BSON interoperability exist; adapter, file conversion, Unicode and GUI-format integration tests pass. This is not the larger LEG-12 workspace. |
| LEG-30 | Duplicate of LEG-13 | Retain JSON plus TOON and SQL/NoSQL-style operations in the canonical database request. |
| LEG-31 | Partial | [CalculatorMemory](../../src/calculator_memory.py) and operations support JSON slots/merge. Search-result tree accumulation, ordered concatenation, history and recall into ResultsTree are separate missing behaviors. |
| LEG-32 | Implemented; repaired | [VennDiagramDialog](../../src/gui/venn_diagram_dialog.py) supplies counts, interactive regions and value details. A constructor TypeError prevented opening on current PySide6; corrected italic font construction and added region-detail tests. |
| LEG-33 | Implemented; repaired | [DiffViewerDialog](../../src/gui/diff_viewer_dialog.py) supplies colored split views. Bidirectional raw scroll values made the end of longer documents unreachable; proportional synchronization with feedback blocked fixes this, with equal/unequal-length regressions. |
| LEG-34 | Partial | [FormulaDock](../../src/gui/formula_dock.py) and [FormulaManager](../../src/formula_manager.py) implement step editing, formula preview, execution and templates. A draggable file/operator canvas and live result preview remain absent. |
| LEG-35 | Partial | [CalculatorDock](../../src/gui/calculator_dock.py), RecallDialog and Set Operations wiring support five slots, Add, Recall and Clear. Content preview is in dialogs, not the requested inline side-panel preview for slots. |
| LEG-36 | Duplicate of LEG-35 | Same Calculator/Set Operations request. Its inline preview requirement stays in LEG-35, not a second task. |

## Verification

Final focused run: **315 passed in 24.28s**, with temporary home/settings and
offscreen Qt, a 180-second process limit and a 20-second per-test timeout covering
setup/teardown. No live provider calls, heavy downloads or whole-project suite
claim. The tested groups were:

- Regex registers/insertion: 20 existing + 13 new regression cases.
- Editor, layout and unsaved recovery: 69 + 6 + 5.
- Formula execution/templates, converters and GUI format integration: 19 + 43 + 16.
- Extractor, catalog structure and mocked Gemini clients: 29 + 14 + 6.
- Google Translate chunking: 20 (not AI Processor chunking).
- Legacy workflow checks, ResultsTree and isolated InsertPanel: 8 + 21 + 26.

The first combined run timed out on the custom exit dialog. The fixture now
mocks instance `exec()` as well as static dialogs. An intermediate 260-test retry
passed. Expanding to full-window InsertPanel fixtures then produced a native
segfault in `ThemeManager._apply_system_theme` while recreating MainWindow.
Deferred Qt deletions are now flushed; component tests use an actual isolated
InsertPanel instead of 26 full application startups. The final 315-test pass
does **not** establish that repeated full-window/theme cycling is fixed; this
has a separate MUST investigation in TASKS.md.

Failures were reproduced before the regex, Venn-constructor and unequal-scroll
fixes. Task consistency checks verify 36 unique original IDs, 23 matching open
legacy entries, 3 duplicates, and no surviving nonstandard unchecked markers.
`git diff --check` passes. Initial errors-only Pylint reported PySide6 dynamic
signal typing limitations (E1101/E1136); these are not runtime test failures.
The serial errors-only retry passed with E1101/E1136 explicitly excluded; it is
not an unrestricted lint pass. No generated core file was found in the repo root.

## Dependencies And Next Work

No user code contribution is needed to continue local work. Investigate the Qt
lifecycle failure first. LEG-24 (data-safe global undo) and LEG-06 (bounded
chunking) should precede features that multiply
file mutations or model requests. Cloud authentication, large model downloads,
publication, and live microphone/provider validation need user/environment setup.
LEG-03 comparison semantics and LEG-25's ECC format need focused clarification,
not invented implementations. Do not delete reusable modules to close markers.
