# Clarify Editor Smart Home On Visual Lines

## Scope

This stage implements only `CE-SMART-HOME-VISUAL-LINE-01` from checkpoint
`094c65c` on branch `COM-951ed0bf-7198-48c4-97c7-124fff0dea05`.
`CE-FIND-SCOPE-NEGATION-01` remains outside scope pending the user's definition
of the inverted-search unit. No File Explorer, APP-THREAD, i18n or legacy task
was started.

## Reproduction

The previous implementation calculated Home targets from the entire logical
QTextBlock. In the isolated reproduction, the cursor was on the second wrapped
visual line, whose block-relative start was column 21. Pressing Home targeted
column 4, the first nonblank character of the logical paragraph, and therefore
jumped to a different visual line.

## Delivered Contract

- The current visual range comes from
  `QTextBlock.layout().lineForTextPosition()`. All offsets are clamped to the
  current block; the previous logical-line behavior is retained as a fallback
  when Qt has not produced layout lines yet.
- Home toggles between the current visual-line start and its first nonblank
  space/tab character. A visual segment containing only whitespace stays at its
  own start instead of crossing into the next segment.
- Shift+Home uses the same destinations while retaining the existing anchor.
  Read-only views still permit cursor movement.
- The calculation reads the live layout on every key press, so resize and zoom
  changes are respected. Primary and split views keep independent cursors over
  their shared document.
- Cursor movement does not modify document text, revision or undo availability.

## Validation

All Qt modules ran serially through `qt_lifecycle_probe.py`, using temporary
HOME, offscreen Qt, pytest timeout 20 seconds, wall limit 180 seconds, global
RAM guard 85 percent and process-tree RSS guard 600 MiB.

| Module | Result | Peak tree RSS |
| --- | ---: | ---: |
| `test_editor_smart_home_visual.py` | 7 passed | 201.8 MiB |
| `test_editor_recent_interactions.py` | 7 passed | 205.7 MiB |
| `test_editor_priority_stage4_tabs.py` | 8 passed | 208.4 MiB |
| `test_editor_redo_shortcuts.py` | 6 passed | 207.0 MiB |
| `test_editor_dock.py` | 69 passed | 225.6 MiB |

The 97 distinct tests passed without a native crash, timeout or guard abort in
the authorized resumed run. The earlier attempt was stopped before pytest
output because global RAM reached 85 percent; its test tree used 110.4 MiB and
was not counted as evidence. After the user authorized resumption at 35.2
percent RAM, the first focused run exposed a test-fixture assumption: two tabs
wrapped at 150 px. Giving that explicitly unwrapped compatibility case a 500 px
viewport corrected the fixture; the product behavior was retained and all
tests passed.

Python compilation, Pylint errors-only, scoped Black checks and
`git diff --check` passed. No provider, real user document, dependency or
default branch was changed. `example.py` remained untracked and byte-identical.
