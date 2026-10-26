# Clarify Editor Find Enter

## Scope

This stage implements only `CE-FIND-ENTER-01` from checkpoint `b215e81` on
branch `COM-7688039c-8b9b-4fc0-98a2-deaa51f8186c`. It changes only keyboard
routing inside `_EditorFindDialog` and does not add AI search, File Explorer,
APP-THREAD or i18n work.

## Reproduction

Before the product edit, one Return key press in the Find query field selected
the second match (`current_match_index == 1`) instead of the first (`0`). Qt
delivered both the `QLineEdit.returnPressed` connection and the dialog's default
Find Next button. The isolated failing process exited normally at 195.6 MiB
peak tree RSS, without a native crash or guard abort.

## Delivered Contract

- Return and Enter in the Find query field invoke exactly one Find Next.
  Keypad Enter follows the same route while its keypad modifier is ignored for
  navigation direction.
- Shift+Return and Shift+Enter invoke exactly one Find Previous. Control, Alt
  or Meta combinations are not captured.
- Auto-repeat Return/Enter events with either direction are consumed without
  triggering additional navigation.
- The global Shift+Enter button shortcut, default Find Next button and duplicate
  `returnPressed` signal route were removed. Find buttons remain directly
  clickable, with dialog buttons no longer becoming implicit defaults.
- Replace input, start/end line controls and the editor document retain native
  Enter behavior. Invalid regexes continue reporting an error without moving
  the editor cursor.
- Existing matching, n-of-m status, circular navigation, state/history,
  Case Sensitive, Whole Word, Regex, lexical/inverted scopes, splits and
  recovery contracts remain unchanged.

## Validation

Every GUI module ran serially through `qt_lifecycle_probe.py`, with temporary
HOME, offscreen Qt, pytest timeout 20 seconds, wall limit 180 seconds, global
RAM guard 85 percent and process-tree RSS guard 600 MiB.

| Module | Result | Peak tree RSS |
| --- | ---: | ---: |
| `test_editor_find_enter.py` | 9 passed | 198.5 MiB |
| `test_editor_find.py` | 18 passed | 71.5 MiB |
| `test_editor_find_state_history.py` | 9 passed | 201.6 MiB |
| `test_editor_find_scope_negation.py` | 8 passed | 193.9 MiB |
| `test_editor_priority_stage3.py` | 8 passed | 200.0 MiB |
| `test_editor_recent_interactions.py` | 7 passed | 206.2 MiB |
| `test_editor_smart_home_visual.py` | 7 passed | 202.0 MiB |
| `test_editor_recovery_lifecycle.py` | 53 passed | 218.1 MiB |
| `test_editor_dock.py` | 69 passed | 227.3 MiB |

The 188 distinct tests passed without a native crash, timeout or guard abort.
Python compilation, Pylint errors-only, Black on the new test and diagnostic
files, and `git diff --check` passed. No provider, real user document,
dependency, translation catalog or default branch was changed. `example.py`
remained untracked and byte-identical.
