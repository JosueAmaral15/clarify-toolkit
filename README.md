# Clarify Toolkit

[![CI](https://github.com/JosueAmaral15/clarify-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/JosueAmaral15/clarify-toolkit/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython-6/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Clarify Toolkit is an open-source desktop application and command-line toolkit
for editing, searching, transforming, and structuring text, source code, and
JSON-like data. The desktop application is built with PySide6; reusable core
operations also power the command-line interface.

> **Project status:** Clarify Toolkit is under active development. Some tools
> and workflows are still being stabilized. See [the canonical task
> queue](docs/TASKS.md) and [the changelog](CHANGELOG.md) for current evidence
> instead of relying on historical feature or coverage claims.

## Main Capabilities

- **Clarify Editor:** multi-document text and source editor with file browsing,
  search and replace, split views, recovery, temporary notes, and configurable
  shortcuts.
- **File Searcher:** bounded file discovery, content search, filters, result
  views, previews, and guarded replacement workflows.
- **Text operations:** search, replace, insertion, case conversion, extraction,
  placeholder replacement, and format conversion.
- **Structured data tools:** JSON search, translation, rewriting,
  deduplication, set operations, and TypeScript/JavaScript object support.
- **Document and AI-assisted tools:** document loading and selected integrations
  with OpenAI, Google Gemini, and local Ollama-compatible services. Provider
  features require the user's own configuration and may send selected content
  to third-party services.
- **Internationalized interface:** runtime catalogs for English, Brazilian
  Portuguese, Spanish, French, German, Japanese, and Simplified Chinese.
- **CLI workflows:** scriptable search, replacement, insertion, dictionary
  translation, Google translation, and JSON/TypeScript rewriting.

The repository contains additional experimental and specialized tools. Their
presence does not imply that every workflow is release-ready; consult the task
queue and focused test evidence before depending on one in production.

## Requirements

- Python 3.12 or 3.13
- [Poetry 2](https://python-poetry.org/) for the reproducible development setup
- A graphical desktop session for the PySide6 application

The optional `excel` dependency group adds XLSX support through `openpyxl`.

## Installation

```bash
git clone https://github.com/JosueAmaral15/clarify-toolkit.git
cd clarify-toolkit
poetry install
```

Install the development dependency group when contributing:

```bash
poetry install -E dev
```

Install optional Excel support with:

```bash
poetry install -E excel
```

## Running the Application

Launch the desktop application from the repository root:

```bash
poetry run python -m src
```

Platform launchers are also available:

```text
clarify.sh       Linux and other Unix-like systems
clarify.command  macOS
clarify.bat      Windows
```

The launchers perform environment checks and may offer dependency setup. For a
controlled development run, prefer the Poetry command above.

## Command-Line Interface

The CLI uses the same package entry point. Available subcommands are `search`,
`replace`, `insert`, `translate`, `gtranslate`, and `dedupe`.

```bash
# Search recursively in Python files.
poetry run python -m src search ./src "SettingsManager" --include "*.py"

# Preview a replacement without writing files.
poetry run python -m src replace ./src old_name new_name --include "*.py" --dry-run

# Insert text below line 10.
poetry run python -m src insert ./notes.txt 10 "New line" --mode insert_below

# Rewrite JSON or TypeScript data to a separate file.
poetry run python -m src dedupe input.ts --join-keys --eliminate-duplicates -o output.ts
```

Use `--help` on the entry point or a subcommand for the current arguments:

```bash
poetry run python -m src --help
poetry run python -m src search --help
```

Replacement and insertion commands can modify many files. Use `--dry-run`, a
version-controlled working tree, and a reviewed target scope before writing.

## Development

The source is organized as a Python package:

```text
src/
  cli/          command parser and command handlers
  core/         search, replacement, insertion, and filtering contracts
  gui/          PySide6 windows, docks, panels, workers, and widgets
  i18n/         runtime translation catalogs
  rewriter/     structured-data parsing and rewriting
  translation/  translation services and models
  utils/        shared filesystem and text utilities
tests/          focused unit, GUI, lifecycle, and regression tests
docs/           user, developer, protocol, task, and evidence documentation
```

Run focused tests while developing:

```bash
poetry run pytest tests/test_module_name.py
```

Useful static checks include:

```bash
poetry check --lock
poetry run black --check src tests
poetry run isort --check-only src tests
poetry run pylint src
```

GUI tests should run offscreen and in isolated processes where documented. The
project has explicit RAM, process-tree RSS, wall-time, and pytest timeout guards;
follow the current protocol and task evidence rather than running the entire GUI
suite indiscriminately.

## Documentation

- [Documentation index](docs/README.md)
- [User wiki](docs/wiki/README.md)
- [Quick start guide](docs/wiki/quick-start-guide.md)
- [Feature overview](docs/wiki/features-overview.md)
- [Keyboard shortcuts](docs/wiki/keyboard-shortcuts.md)
- [Troubleshooting](docs/wiki/troubleshooting.md)
- [Project structure](docs/guides/PROJECT_STRUCTURE.md)
- [Canonical task queue](docs/TASKS.md)
- [English documentation](docs/en/README.md)
- [Brazilian Portuguese documentation](docs/pt/README.md)

English is the canonical language for the root README and maintained project
metadata. Localized documentation and translation catalogs remain part of the
project. The wider English-canonical audit is tracked in `docs/TASKS.md`.

## Security and Privacy

Report suspected vulnerabilities according to [SECURITY.md](SECURITY.md). Do
not open a public issue containing credentials, private documents, or sensitive
logs.

Clarify Toolkit primarily processes local files, but provider-backed AI and
translation features can transmit selected data to external services. Review
the active provider and its privacy terms before processing confidential
content. Keep API credentials out of source files, logs, command histories, and
commits.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Keep
changes scoped, preserve unrelated work, add proportionate tests, and document
validation limits. Historical reports under `docs/` are evidence snapshots and
may describe older architecture or results; do not silently rewrite them as if
they represented the current release.

## License

Clarify Toolkit is released under the [MIT License](LICENSE).

## Author

Created and maintained by [Josue Amaral](https://github.com/JosueAmaral15).
