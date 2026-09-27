# Docs Markdown Organization Plan - 2026-06-09

## Scope

Organize Markdown files under `docs/` without changing source code, binary fixtures, generated files, or operational documentation content.

## Current State

- Markdown files under `docs/`: 814
- Markdown files currently loose at `docs/` root: 19
- Pre-existing modified documentation files are present in the worktree; this cleanup avoids editing those files directly.

## Root Files To Keep

These files remain at `docs/` root because they are active entry points or operational references:

- `CURRENT_STATE.md`
- `INDEX.md`
- `README.md`
- `TASKS.md`

## First Batch: Root Markdown Cleanup

Move root-level historical/action/report Markdown into existing documentation categories:

| Current path | Target path | Reason |
| --- | --- | --- |
| `docs/ACTION_PLAN_CRITICAL_TRANSLATION_BUGS_COM8.md` | `docs/action-plans/development/ACTION_PLAN_CRITICAL_TRANSLATION_BUGS_COM8.md` | Translation bug action plan |
| `docs/ACTION_PLAN_HYPERLINK_FIX_COM8.md` | `docs/action-plans/development/ACTION_PLAN_HYPERLINK_FIX_COM8.md` | Hyperlink fix action plan |
| `docs/LIMIT_FEATURE_BUG_ACTION_PLAN_3.md` | `docs/action-plans/development/LIMIT_FEATURE_BUG_ACTION_PLAN_3.md` | Limit bug action plan |
| `docs/ACTION_PLAN_RESTORE_ORPHANED_FEATURES_3.md` | `docs/action-plans/cleanup/ACTION_PLAN_RESTORE_ORPHANED_FEATURES_3.md` | Orphaned feature restoration plan |
| `docs/CLEANUP_DECISION_AND_ACTION_PLAN_3.md` | `docs/action-plans/cleanup/CLEANUP_DECISION_AND_ACTION_PLAN_3.md` | Orphaned converter cleanup decision |
| `docs/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE1_3.md` | `docs/investigations/orphaned-code/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE1_3.md` | Orphaned code investigation phase |
| `docs/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE2_3.md` | `docs/investigations/orphaned-code/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE2_3.md` | Orphaned code investigation phase |
| `docs/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE3_3.md` | `docs/investigations/orphaned-code/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE3_3.md` | Orphaned code investigation phase |
| `docs/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE4_3.md` | `docs/investigations/orphaned-code/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE4_3.md` | Orphaned code investigation phase |
| `docs/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE5_FINAL_3.md` | `docs/investigations/orphaned-code/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE5_FINAL_3.md` | Orphaned code investigation final report |
| `docs/INVESTIGATION_COMPLETE_SUMMARY_3.md` | `docs/investigations/orphaned-code/INVESTIGATION_COMPLETE_SUMMARY_3.md` | Orphaned code completion summary |
| `docs/ORPHANED_FEATURES_RESTORATION_SUMMARY_3.md` | `docs/investigations/orphaned-code/ORPHANED_FEATURES_RESTORATION_SUMMARY_3.md` | Orphaned feature restoration summary |
| `docs/HYPERLINK_FIX_SUMMARY_COM8.md` | `docs/bugfixes/HYPERLINK_FIX_SUMMARY_COM8.md` | Hyperlink preservation fix summary |
| `docs/LIMIT_FIX_SUMMARY_3.md` | `docs/bugfixes/LIMIT_FIX_SUMMARY_3.md` | Limit bug fix summary |
| `docs/README_OLD.md` | `docs/archive/README_OLD.md` | Historical README backup |

## Follow-Up Batches

1. Deduplicate report/session/study reading summaries.
2. Group programmer-specific COM8 translation-formatting documents by topic.
3. Split `reports/` into high-level reports, reading reports, bug reports, and validation reports if needed.
4. Update `docs/INDEX.md` and `docs/README.md` after the worktree's existing edits are reconciled.

## Validation

After movement:

- Confirm only active root Markdown remains.
- Search for references to moved file names.
- Create a movement report with the final mapping.
