# Clarify Editor External Reload

## Scope

This stage completes only `CE-EXTERNAL-RELOAD-UX-01` from checkpoint `ec833fa`
on branch `COM-df4374fe-207f-405b-86ec-6c93872b1afb`. It does not implement
Find escapes, language override, File Searcher, Clock or other backlog items.

## Reproduction

Temporary files proved two gaps before product edits. External-change status
remained hard-coded in English after switching to Portuguese, and no bounded
stable-revision reader existed. The audit also found a TOCTOU window: the old
path read the file and then collected a potentially newer path signature, so a
concurrent replacement could make older text appear current.

## Contract And Fix

- The file watcher only marks `[external]` or `[missing]`, pauses auto-save and
  enables the explicit reload action. It never replaces editor text.
- Dirty buffers require confirmation before reload. Refusal, read/decode error,
  oversize input or a revision change leaves the editor buffer untouched.
- The bounded binary reader compares path and descriptor metadata before and
  after reading, then revalidates before and immediately after application.
- Text and JSON tabs apply the already-read revision instead of reopening the
  path. UTF-8 BOM and the first LF, CRLF or CR convention are retained for a
  subsequent atomic save. Other encodings remain explicitly unsupported.
- Cursor and selection positions are restored within the new document bounds.
  A user-authorized reload establishes a clean baseline and intentionally
  clears the previous document undo stack; a post-apply disk change leaves the
  tab marked external.
- All user-facing external-change and reload messages now use the seven runtime
  translation catalogs and expose the warning through accessible status text.

## Validation

Each Qt module ran serially in its own offscreen process with temporary HOME,
pytest timeout 20 seconds, wall limit 180 seconds, system RAM guard 85 percent
and process-tree RSS guard 600 MiB.

| Module | Result | Peak tree RSS |
| --- | ---: | ---: |
| `test_editor_external_reload.py` | 11 passed | 210.4 MiB |
| `test_editor_dock.py` external/reload subset | 3 passed | 205.0 MiB |
| `test_editor_open_clean_state.py` | 10 passed | 213.3 MiB |
| `test_unified_text_to_json_editor_switch.py` | 2 passed | 202.8 MiB |
| `test_editor_recovery_reopen.py` | 5 passed | 212.0 MiB |

The 31 distinct tests passed. One added CRLF test initially exposed ambiguous
`\r` versus `\r\n` detection; the implementation was corrected and the complete
focused module reran successfully. No native crash, timeout or guard abort
occurred.

Focused Pylint-E rated 10.00/10. Four AST parses, seven JSON parses, parity of
all 18 new translation keys and `git diff --check` passed. No provider, real
user document, default branch or dependency was changed. `example.py` remained
untracked and byte-identical.
