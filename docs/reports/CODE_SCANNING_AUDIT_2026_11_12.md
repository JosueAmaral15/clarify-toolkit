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

## Stage 3 - Spreadsheet Formula Injection

| Alert | CWE | Location | Classification | Remediation |
| --- | --- | --- | --- | --- |
| #2 | CWE-1236 | `src/export_manager.py` | Confirmed | Neutralize string keys and values only at the CSV/XLSX cell boundary; preserve numbers and raw JSON, YAML and TOML data. |
| #3 | CWE-1236 | `src/utils/file_finder.py` | Confirmed | Replace hand-built CSV quoting with `csv.writer` and neutralize attacker-controlled names and paths before writing cells. |
| #4 | CWE-1236 | `src/gui/statistics_dialog.py` | Confirmed | Neutralize visible table values when writing CSV and XLSX while leaving the source statistics and JSON export unchanged. |

The shared `neutralize_spreadsheet_cell` helper prefixes strings beginning with
`=`, `+`, `-`, `@`, tab or carriage return with an apostrophe. Safe strings and
non-text values are returned unchanged.

### Stage 3 Validation

- `tests/security/test_code_scanning_spreadsheets.py`: 10 passed. Coverage
  includes every dangerous prefix, safe and numeric values, real temporary CSV
  and JSON files, file-finder names, statistics exports and controlled XLSX
  workbook cells.
- The first collection attempt stopped before tests because optional `openpyxl`
  is not installed in `.venv`. The final test uses a minimal controlled workbook
  double for the XLSX write contract; no dependency was installed or network
  request made.
- Python compilation, Ruff, Pylint-E and `git diff --check` passed after removing
  one unused test import reported by Ruff.

No user file, provider, spreadsheet application or full GUI was opened. These
alerts remain open until reviewed integration and the default-branch scan.

## Stage 4 - Generated HTML And SVG Injection

| Alert | CWE | Location | Classification | Remediation |
| --- | --- | --- | --- | --- |
| #14 | CWE-79 | `src/diff_analyzer.py` | Confirmed | Escape untrusted file names, flattened JSON keys and serialized JSON values as HTML text before inserting them into the trusted diff-report template. |
| #20 | CWE-79 | `src/venn_diagram_generator.py` | Confirmed | Escape untrusted file names and other dynamic SVG text-node values while retaining the generator's fixed SVG elements and attributes. |

Both export APIs receive names or content derived from files selected by the
user. Before this stage, closing tags could leave their intended text nodes and
introduce active HTML or SVG elements. The correction is applied only at the
HTML/XML text serialization boundary; source dictionaries, Venn data and Qt
views remain unchanged.

### Stage 4 Validation

- `tests/security/test_code_scanning_xss.py`: 2 passed. Temporary exports cover
  script elements, event-handler payloads, closing `title`, `span`, `pre` and
  `text` tags, ampersands, source-data preservation and well-formed SVG parsing
  with no injected script node. Peak process-tree RSS was 63.2 MiB.
- Prior security regressions passed in separate isolated processes:
  `test_code_scanning_high.py` (11), `test_code_scanning_commands.py` (4) and
  `test_code_scanning_spreadsheets.py` (10).
- Python compilation, Ruff, Pylint-E and `git diff --check` passed.

No browser, provider, user document or full GUI was opened. The alerts remain
open until reviewed integration and the default-branch scan.

## Stage 5 - Compressed Document Amplification

| Alert | CWE | Location | Classification | Remediation |
| --- | --- | --- | --- | --- |
| #21 | CWE-409 | `src/translation/html_format_mapper.py` | Confirmed | Validate the complete ODT ZIP before ODF parser construction, then read custom `Pictures/` entries from the same validated stream. Retain the contained extraction contract from Stage 1. |
| #8 | CWE-409 | `src/translation/docx_html_mapper.py` | Confirmed | Validate the complete DOCX ZIP before python-docx constructs and materializes its package, then give the parser the same validated stream. |

The shared document-archive boundary limits entries to 4,096, each expanded
member to 64 MiB, total expanded and compressed bytes to 512 MiB, and the
per-member compression ratio to 200. Validation happens before either parser
loads XML parts or embedded media; reopening a path between validation and
parsing is avoided.

### Stage 5 Validation

- `tests/security/test_code_scanning_archives.py`: 10 passed. Generated
  temporary archives cover entry count, member size, total compressed and
  expanded size, compression ratio, parser-not-called behavior for ODT and DOCX
  bombs, the documented default limits, and successful translation of valid
  generated ODT and DOCX documents. Peak process-tree RSS was 87.4 MiB.
- `tests/security/test_code_scanning_high.py`: 11 passed, preserving the Stage 1
  ODT path, link and extraction protections. Peak process-tree RSS was 72.1 MiB.
- `tests/com8/test_html_format_mapper_COM8.py`: 5 passed with its required
  legacy `PYTHONPATH=src`. Peak process-tree RSS was 66.6 MiB.
- Python compilation, focused Ruff checks, Pylint-E and `git diff --check`
  passed. The broad legacy mapper retains pre-existing Ruff debt outside this
  change; syntax/error rules and all new code passed.

No provider, browser, user document or full GUI was used. These alerts remain
open until reviewed integration and the default-branch scan.

## Stage 6 - Project Template Output Containment

| Alert | CWE | Location | Classification | Remediation |
| --- | --- | --- | --- | --- |
| #17 | CWE-22 | `src/template_manager.py` | Confirmed | Build and validate the complete template output plan before creating the target root; reject absolute, parent, empty, control-containing, duplicate, conflicting and canonically escaping paths; write accepted text files through the existing atomic writer. |

Custom template JSON is loaded from the user template directory and previously
reached `target_dir / file_info["path"]` directly. The new preflight interprets
both slash styles consistently, resolves existing symlinks, requires every
target and existing ancestor to remain compatible with a regular file, and
detects file/directory collisions before any project output is created. If an
I/O failure occurs after preflight, the raised error states how many files were
completed and that partial output may remain.

### Stage 6 Validation

- `tests/security/test_code_scanning_template_paths.py`: 11 passed. Temporary
  templates cover POSIX and Windows traversal/absolute forms, empty and control
  paths, preflight ordering, symlink escape, existing-parent and planned-parent
  conflicts, valid nested paths, atomic-write use and explicit partial-failure
  reporting. Peak process-tree RSS was 63.8 MiB.
- `tests/test_template_manager.py`: 5 passed, preserving built-in lookup,
  categories and normal blank-project creation. The isolated guarded run peaked
  at 62.3 MiB; the module was rerun after the final preflight refinement.
- `tests/test_atomic_files.py`: 3 passed with peak process-tree RSS of 61.8 MiB.
- Python compilation, Ruff, Pylint-E and `git diff --check` passed.

No provider, browser, user document or full GUI was used. This alert remains
open until reviewed integration and the default-branch scan.

## Remaining Inventory

- 2 medium alerts not yet covered by a candidate correction: resource
  consumption and missing authentication.
- 6 low alerts not yet covered by a candidate correction: XML entity expansion,
  insecure temporary files and regular-expression complexity.

Each remaining alert stays open until its source and consumers have been
reviewed and focused evidence is recorded here. No alert is to be dismissed
merely because a work branch contains a candidate correction.
