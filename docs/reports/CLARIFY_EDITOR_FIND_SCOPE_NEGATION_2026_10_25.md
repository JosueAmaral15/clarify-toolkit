# Clarify Editor Find Scope And Negation

## Scope

This stage implements only `CE-FIND-SCOPE-NEGATION-01` from checkpoint
`203275e` on branch `COM-e83ad129-559d-4be4-952e-50b05d3904e7`. The user chose
Line as the default inverted-search unit and requested Token and Interval as
explicit alternatives.

## Reproduction

Before editing, `FindOptions` rejected the `inverted` argument, the valid regex
`^(?!\s*def).*` raised `regular expression must not match empty text`, and a
Python `comments` scope returned no result without exposing a UI option.

## Delivered Contract

- Inverted Search is opt-in. Its unit selector is enabled only while inversion
  is active and defaults safely to Line when settings are missing or invalid.
- Line returns nonempty in-scope lines with no positive match. Token returns
  Unicode word tokens with no overlapping positive match. Interval returns
  maximal contiguous groups of nonmatching lines; it never generates every
  character gap between matches.
- Start/end line bounds, Case Sensitive, Whole Word and lexical scopes are
  applied before inversion. Unknown file types retain the existing explicit
  scope-fallback signal.
- Only Comments uses Python tokenization and a bounded JS/TS/JSON5 scanner that
  skips quoted strings. Standard JSON has no comment scope and therefore
  returns no comment matches rather than searching all text.
- Regex mode uses multiline anchors. Valid expressions that can also produce
  empty matches remain usable, but empty spans are omitted. Invalid regexes
  report an error without cursor movement.
- Replace and Replace All are explicitly disabled during inverted search,
  because replacing an entire line, token or interval would be ambiguous and
  potentially destructive. Ordinary replacement behavior is unchanged.
- Text, query, result-count and time budgets remain enforced. Inverted search
  fails explicitly if positive discovery is truncated, rather than deriving an
  incorrect complement.
- New controls and status text are translated in all seven catalogs. Clear
  retains scope, inversion unit and line bounds under the existing options
  contract.

## Validation

Every module ran serially through `qt_lifecycle_probe.py`, with temporary HOME,
offscreen Qt, pytest timeout 20 seconds, wall limit 180 seconds, global RAM
guard 85 percent and process-tree RSS guard 600 MiB.

| Module | Result | Peak tree RSS |
| --- | ---: | ---: |
| `test_editor_find.py` | 18 passed | 70.6 MiB |
| `test_editor_find_scope_negation.py` | 8 passed | 193.7 MiB |
| `test_editor_priority_stage3.py` | 8 passed | 199.9 MiB |
| `test_editor_find_state_history.py` | 9 passed | 201.8 MiB |
| `test_editor_recent_interactions.py` | 7 passed | 206.1 MiB |
| `test_editor_dock.py` | 69 passed | 227.2 MiB |

The 119 distinct tests passed without a native crash, timeout or guard abort.
The first pure run found only two expected JS fixture offsets one column too
high; correcting those expected values required no product-code change.

Python compilation, Pylint errors-only, scoped Black checks, seven JSON parses
and `git diff --check` passed. No provider, real user document, dependency or
default branch was changed. `example.py` remained untracked and byte-identical.
