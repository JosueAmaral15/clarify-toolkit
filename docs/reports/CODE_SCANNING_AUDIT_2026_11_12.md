# Code Scanning Audit - 12 November 2026

## Scope

GitHub Code Scanning reports 22 open alerts on `main`: 2 high, 13 medium and
7 low. This audit treats the API result as an inventory, not as proof that each
alert is exploitable. Findings are classified and remediated in bounded stages;
GitHub closure requires reviewed default-branch integration and a subsequent
scan.

## Stage 1 - High Severity

| Alert | CWE | Location | Classification | Remediation |
| --- | --- | --- | --- | --- |
| #1 | CWE-89 | `plugins/export_to_postgresql/main.py` | Confirmed | Compose table identifiers with `psycopg2.sql.Identifier`; keep JSON values parameterized; reject empty, control-containing and overlong identifiers. |
| #11 | CWE-22 | `src/translation/html_format_mapper.py` | Confirmed | Replace unrestricted `extractall()` with contained, regular-file-only extraction and bounded entries, member bytes, total bytes and compression ratio. |

The bounded ODT extraction also directly addresses medium alert #7, which
reports unbounded entry count, uncompressed size and compression ratio at the
same operation. It does not close unrelated XML parser or archive-reading
findings.

## Stage 1 Validation

- `tests/security/test_code_scanning_high.py`: 11 passed. Coverage includes a
  malicious SQL identifier, invalid identifier boundaries, contained regular
  ODT members, traversal and absolute paths, Windows separators, symbolic links
  and excessive compression.
- `tests/test_plugin_system.py`: 16 passed.
- `tests/com8/test_html_format_mapper_COM8.py`: 5 passed with its required
  legacy `PYTHONPATH=src`; the first collection without that path failed before
  running tests because the module imports the legacy top-level `translation`
  package.
- Python compilation and `git diff --check` passed. Pylint-E reported only the
  plugin's existing PySide6 introspection false positives and two existing
  undefined `logger` references outside this diff; a run suppressing only those
  known categories passed.

No live database, provider, user document or full GUI startup was used. GitHub
alerts remain open until this branch is reviewed, integrated and scanned on
`main`.

## Stage 2 - Command Injection

| Alert | CWE | Location | Classification | Remediation |
| --- | --- | --- | --- | --- |
| #15 | CWE-78 | `src/gui/results_tree.py` | Confirmed | Replace Windows `cmd /c start` and all platform command launchers with `QDesktopServices.openUrl(QUrl.fromLocalFile(...))`. Apply the same contract to the active `src/gui/panels/results_tree.py` consumer while retaining the compatibility widget. |
| #10 | CWE-78 | `.github/workflows/benchmarks.yml` | Confirmed | Convert free-form size and run dispatch fields to enumerated choices; pass all dispatch values through step environment variables and quote each argument rather than interpolating expressions into shell source. |
| #19 | CWE-78 | `src/gui/progress/progress_bar_widget.py` | Confirmed | Keep the AppleScript program immutable and pass the title and message as separate `argv` values after `--`; keep Linux notification values as separate arguments as well. |

### Stage 2 Validation

- `tests/security/test_code_scanning_commands.py`: 4 passed. The tests preserve
  shell metacharacters as local-URL data, forbid `cmd /c start` in both result
  tree implementations, prove that notification data is absent from the
  AppleScript program, and parse the workflow to verify choice inputs and quoted
  environment arguments.
- `tests/test_results_tree_unicode_hierarchy.py`: 21 passed.
- `tests/test_progress_system.py`: 18 passed.
- `tests/test_benchmarks.py`: 10 passed.
- Python compilation, workflow YAML parsing and `git diff --check` passed.
  Pylint-E reported only its known inability to introspect the dynamic PySide6
  `QUrl` and `QDesktopServices` exports; suppressing only `no-name-in-module`
  produced a clean result.

No desktop command, notification provider, benchmark workflow, user file or
full GUI was launched. The findings remain open until reviewed integration and
the default-branch scan.

## Remaining Inventory

- 10 medium alerts not yet covered by a candidate correction: resource
  consumption, compressed-data amplification, XSS, path traversal, missing
  authentication and CSV formula injection.
- 6 low alerts not yet covered by a candidate correction: XML entity expansion,
  insecure temporary files and regular-expression complexity.

Each remaining alert stays open until its source and consumers have been
reviewed and focused evidence is recorded here. No alert is to be dismissed
merely because a work branch contains a candidate correction.
