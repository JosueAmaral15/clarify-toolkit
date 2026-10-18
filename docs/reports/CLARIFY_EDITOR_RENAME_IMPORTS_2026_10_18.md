# Clarify Editor Rename Import Updates - 2026-10-18

## Scope

This report covers only `CE-RENAME-IMPORTS-01` from checkpoint `e1632c4`.
`APP-THREAD-01` and the legacy backlog were not changed.

The existing `src/rewriter/reference_updater.py` was audited before implementation.
It updates translation-key expressions such as `t.pages.contact` for JSON Rewriter;
its public consumers and tests do not model module imports. Reusing its regular
expressions for Editor renames would have introduced blind replacements, so its API
and consumers remain unchanged and were regression-tested.

## Delivered Contract

- File and folder renames retain the existing collision checks, tab path remapping,
  watcher baselines, folder sessions and bounded recovery checkpoints.
- Python `.py`/`.pyi` imports use `ast` plus `tokenize` source spans. Absolute and
  relative module paths are updated; strings are not searched or replaced.
- Single-line relative ESM imports/exports in `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`
  and `.cjs` use a comment/string/template-aware lexical guard. CommonJS `require`
  references are reported as ambiguous and are not changed.
- `from package import name` is reported when `name` may be either the renamed
  module or an exported symbol. Invalid module names, parse failures, non-UTF-8
  files, linked files and other unsupported cases are reported without claiming a
  complete correction.
- Analysis never leaves the canonical Explorer root or follows symlinks. Defaults
  are 20,000 directory entries, 2,000 supported files, 2 MiB per file, 32 MiB total,
  5,000 changes, 200 issues and 200 previewed changes.
- Modified open buffers are excluded. Clean affected tabs are reloaded after a
  confirmed update and their watcher baselines are refreshed.
- The preview is explicit and defaults to No. Writes use revision-bound atomic
  replacement. A partial failure rolls completed files back. The latest successful
  transaction can be undone from the Explorer context menu, unless a target changed
  afterward.
- UTF-8 BOM and original CRLF/LF bytes are preserved. No original is overwritten by
  the rename analysis itself, and no live provider or user document is used.

## Validation

All Qt modules ran serially in separate offscreen processes with temporary `HOME`,
system RAM guard 85%, process-tree RSS guard 600 MiB, wall guard 180 seconds and
pytest timeout 20 seconds.

| Validation | Result |
| --- | --- |
| New pure rename/reference tests | 13 passed |
| New Editor Qt integration tests | 7 passed |
| Explorer, tab, session, recovery, layout and dock-chrome regressions | 97 passed |
| Broad Editor module | 69 passed |
| Atomic-write and legacy reference-updater regressions | 15 passed |
| Total distinct tests | 201 passed |
| Peak process-tree RSS | 248.3 MiB |
| Native crash, timeout or guard abort | None |

The first new Qt integration run had five ordinary assertion/setup failures caused
by a test double that rejected a named argument and use of a `QPlainTextEdit`-only
method on `QTextEdit`. Production code did not crash; the test fixture was corrected
and all seven final integration tests passed.

`py_compile`, Pylint errors-only, `git diff --check`, seven-catalog JSON parsing and
presence checks for all 15 new translation keys passed. `example.py` remained
untracked and byte-identical at SHA-256
`058053d87c818d699cde0f00d670bca0e1c6ad857caa9758ea6a556d7c64fcee`.

## Remaining Queue

The canonical queue has 33 open items. The highest-priority previously open item is
`APP-THREAD-01`; it remains separate from this completed Editor stage.
