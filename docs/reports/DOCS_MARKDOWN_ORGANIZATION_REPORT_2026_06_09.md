# Docs Markdown Organization Report - 2026-06-09

## Summary

First cleanup batch completed for loose Markdown files at the `docs/` root.

## Results

- Root Markdown before: 19 files
- Root Markdown after: 4 files
- Markdown count after cleanup: 815 files
- New planning document created: `docs/action-plans/cleanup/DOCS_MARKDOWN_ORGANIZATION_PLAN_2026_06_09.md`

## Root Files Preserved

The following files remain at `docs/` root because they are active operational entry points:

- `CURRENT_STATE.md`
- `INDEX.md`
- `README.md`
- `TASKS.md`

## Files Moved

| Previous path | New path |
| --- | --- |
| `docs/ACTION_PLAN_CRITICAL_TRANSLATION_BUGS_COM8.md` | `docs/action-plans/development/ACTION_PLAN_CRITICAL_TRANSLATION_BUGS_COM8.md` |
| `docs/ACTION_PLAN_HYPERLINK_FIX_COM8.md` | `docs/action-plans/development/ACTION_PLAN_HYPERLINK_FIX_COM8.md` |
| `docs/LIMIT_FEATURE_BUG_ACTION_PLAN_3.md` | `docs/action-plans/development/LIMIT_FEATURE_BUG_ACTION_PLAN_3.md` |
| `docs/ACTION_PLAN_RESTORE_ORPHANED_FEATURES_3.md` | `docs/action-plans/cleanup/ACTION_PLAN_RESTORE_ORPHANED_FEATURES_3.md` |
| `docs/CLEANUP_DECISION_AND_ACTION_PLAN_3.md` | `docs/action-plans/cleanup/CLEANUP_DECISION_AND_ACTION_PLAN_3.md` |
| `docs/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE1_3.md` | `docs/investigations/orphaned-code/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE1_3.md` |
| `docs/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE2_3.md` | `docs/investigations/orphaned-code/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE2_3.md` |
| `docs/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE3_3.md` | `docs/investigations/orphaned-code/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE3_3.md` |
| `docs/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE4_3.md` | `docs/investigations/orphaned-code/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE4_3.md` |
| `docs/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE5_FINAL_3.md` | `docs/investigations/orphaned-code/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE5_FINAL_3.md` |
| `docs/INVESTIGATION_COMPLETE_SUMMARY_3.md` | `docs/investigations/orphaned-code/INVESTIGATION_COMPLETE_SUMMARY_3.md` |
| `docs/ORPHANED_FEATURES_RESTORATION_SUMMARY_3.md` | `docs/investigations/orphaned-code/ORPHANED_FEATURES_RESTORATION_SUMMARY_3.md` |
| `docs/HYPERLINK_FIX_SUMMARY_COM8.md` | `docs/bugfixes/HYPERLINK_FIX_SUMMARY_COM8.md` |
| `docs/LIMIT_FIX_SUMMARY_3.md` | `docs/bugfixes/LIMIT_FIX_SUMMARY_3.md` |
| `docs/README_OLD.md` | `docs/archive/README_OLD.md` |

## Reference Updates

Updated direct references in current support documents:

- `docs/features/ADVANCED_CONVERTERS.md`
- `docs/bugfixes/HYPERLINK_FIX_SUMMARY_COM8.md`
- `docs/bugfixes/LIMIT_FIX_SUMMARY_3.md`
- `docs/action-plans/development/LIMIT_FEATURE_BUG_ACTION_PLAN_3.md`
- `docs/action-plans/cleanup/CLEANUP_DECISION_AND_ACTION_PLAN_3.md`
- `docs/investigations/orphaned-code/INVESTIGATION_COMPLETE_SUMMARY_3.md`
- `docs/investigations/orphaned-code/ORPHANED_FEATURES_RESTORATION_SUMMARY_3.md`
- `docs/investigations/orphaned-code/DEEP_ORPHANED_CODE_INVESTIGATION_PHASE5_FINAL_3.md`

Remaining filename-only references are either:

- within the same directory as the referenced file,
- in historical programmer/session records, or
- in this report/plan as movement history.

## Existing Worktree Notes

The worktree already contained modified files before this cleanup, including `docs/INDEX.md`, `docs/README.md`, API docs, guide docs, process docs, wiki docs, code, tests, and i18n JSON files. This cleanup avoided editing the active index files to avoid mixing with those pre-existing changes.

## Next Recommended Batch

1. Reconcile and update `docs/INDEX.md` and `docs/README.md` after the current modified versions are accepted.
2. Split the large `docs/reports/` directory into subdirectories:
   - `docs/reports/reading/`
   - `docs/reports/bugfixes/`
   - `docs/reports/validation/`
   - `docs/reports/architecture/`
3. Group COM8 translation-formatting documents under topic subdirectories in `docs/programmers/com8/` if that historical directory still needs cleanup.
