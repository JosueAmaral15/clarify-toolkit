# Clarify Editor Find State And History

## Scope

This stage implements only `CE-FIND-STATE-HISTORY-01` from checkpoint
`67d9dee` on branch `COM-6ea25995-c3b8-4193-bab8-8724358cebd8`. It does not
change the separate modeless-panel, scope-negation, AI-search, File Explorer or
application-thread tasks.

## Reproduction

Before the change, the Find/Replace dialog had no Clear action or query and
replacement history. Closing and reopening lost both values. Moving the editor
cursor left `current_match_index` at `-1` and displayed only the total match
count instead of the nearest `n of m`. The dock also constructed the dialog over
the primary editor even when its split view was active.

## Delivered Contract

- Each open file or untitled buffer has a private in-memory identity and up to
  five most-recent query/replacement pairs. Each value is limited to 4096
  characters. The dock retains at most twenty buffer histories using bounded
  least-recently-used eviction.
- Closing a file removes only its history; closing the Editor clears all Find
  histories. Queries and replacements are never written to QSettings, document
  recovery snapshots or folder sessions.
- Clear removes the current query, replacement, matches and buffer history. It
  intentionally retains Case Sensitive, Whole Word, Regex, lexical scope and
  start/end line values.
- Reopening Find/Replace and moving the cursor calculate the nearest result and
  update `n of m` without navigating, selecting or replacing text. Find uses the
  active split when applicable.
- Previous Values is available only when the dialog was not initialized from an
  editor selection. A Find-only use preserves the replacement previously paired
  with the same query.
- The three new labels are translated in all seven supported catalogs.

## Validation

All Qt modules ran serially through `qt_lifecycle_probe.py`, with an isolated
temporary HOME, offscreen Qt, pytest timeout 20 seconds, wall limit 180 seconds,
RAM guard 85 percent and process-tree RSS guard 600 MiB.

| Module | Result | Peak tree RSS |
| --- | ---: | ---: |
| `test_editor_find_state_history.py` | 9 passed | 201.2 MiB |
| `test_editor_priority_stage3.py` | 8 passed | 199.3 MiB |
| `test_editor_recent_interactions.py` | 7 passed | 205.6 MiB |
| `test_editor_dock.py` | 69 passed | 226.7 MiB |
| `test_editor_priority_stage4_tabs.py` | 8 passed | 208.4 MiB |
| `test_editor_priority_stage5_sessions.py` | 6 passed | 205.8 MiB |

The 107 distinct tests passed without a native crash or resource-guard abort.
An initial focused run found one test-fixture issue: the QTextEdit convenience
constructor normalized multiline input. The fixture was changed to
`setPlainText`; no product defect was hidden by that correction.

Python compilation, JSON parsing for all seven catalogs, Pylint errors-only,
scoped Black checks and `git diff --check` passed. No provider, real user
document, default branch or dependency was changed. `example.py` stayed
untracked and byte-identical.
