# Clarify Editor Folder Session Switch

## Scope

This stage implements only `CE-FOLDER-SESSION-SWITCH-REGRESSION-01` from
checkpoint `4118b96` on branch
`COM-355494f1-aadf-4ce5-91d1-bc033af5ff7a`. All reproduction and validation
used temporary roots, settings and files.

## Reproduction

Before the product fix, the guarded A to B regression left both A tabs visible
after B became the Explorer root: the assertion expected zero tabs and observed
two. Six preceding session tests passed, the process exited normally and peak
tree RSS was 208.6 MiB. Source audit also confirmed that a failed recovery
checkpoint did not stop `_set_explorer_root`; the root change continued after
the failure was reported.

## Delivered Contract

- File-backed tabs are assigned to the canonical Explorer root that owned them
  when they were opened or restored. Files outside that root are not silently
  claimed by the workspace.
- Closing or switching a folder checkpoints and stores its bounded session,
  detaches only tabs owned by that root and retains their recovery snapshots.
  A checkpoint or session-write failure aborts before the root or tabs change.
- Reopening a root restores its tab order, active tab, shared split orientation
  and dirty in-memory contents. No tab owned by A remains visible in B.
- Dirty snapshots take precedence over disk references. Clean references reuse
  their recovery identity when the source revision still matches, preventing a
  new reference from being accumulated on every switch.
- Removed or unreadable origins are skipped and reported. Recovery-list IO
  failures are reported without deleting the stored snapshot files.
- Detaching stops tab timers, releases watcher registrations, clears only the
  detached buffers' private Find history and never invokes individual-tab
  discard behavior. Save/Discard/Cancel, temporary notes, Find and Home
  behavior remain unchanged.

## Validation

Every GUI module ran serially through `qt_lifecycle_probe.py`, with temporary
HOME, offscreen Qt, pytest timeout 20 seconds, wall limit 180 seconds, global
RAM guard 85 percent and process-tree RSS guard 600 MiB.

| Module | Result | Peak tree RSS |
| --- | ---: | ---: |
| `test_editor_priority_stage5_sessions.py` | 12 passed | 213.2 MiB |
| `test_editor_priority_stage1.py` | 6 passed | 209.2 MiB |
| `test_editor_priority_stage4_tabs.py` | 8 passed | 208.8 MiB |
| `test_editor_priority_stage5_notes.py` | 5 passed | 203.2 MiB |
| `test_editor_recovery_lifecycle.py` | 53 passed | 218.4 MiB |
| `test_editor_recent_interactions.py` | 7 passed | 206.8 MiB |
| `test_editor_find_state_history.py` | 9 passed | 202.0 MiB |
| `test_editor_find_scope_negation.py` | 8 passed | 193.9 MiB |
| `test_editor_smart_home_visual.py` | 7 passed | 202.0 MiB |
| `test_editor_dock.py` | 69 passed | 227.2 MiB |

The 184 distinct tests passed without a native crash, timeout or guard abort.
Python compilation, Pylint errors-only and `git diff --check` passed before the
documentation update. No provider, real user document, dependency or default
branch was changed. `example.py` remained untracked and byte-identical.
