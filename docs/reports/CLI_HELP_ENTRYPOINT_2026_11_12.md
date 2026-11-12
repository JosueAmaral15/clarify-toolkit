# CLI Help Entry-Point Repair - 2026-11-12

## Reproduced Defect

`python -m src --help` bypassed `argparse`, initialized `MainWindow`, activated
plugins and remained alive until the process was explicitly stopped. The same
routing defect allowed invalid top-level options to enter the graphical path.

The cause was the entry point's decision to invoke the parser only when the
first argument was one of six known subcommand names.

## Correction

All explicit arguments now pass through the canonical parser:

- `-h` and `--help` print top-level help and exit successfully.
- Invalid top-level options report an argument error and exit with status 2.
- CLI subcommands continue to invoke their registered handlers.
- `--gui` cannot be combined with a CLI subcommand.
- No arguments, or standalone `--gui`, retain graphical startup behavior.

Qt receives a clean application argument list after Clarify has consumed
`--gui`, preventing the application-only option from leaking into Qt parsing.

## Validation

`tests/test_cli_entrypoint.py` contains five isolated regressions. Four invoke
the package through a real subprocess with ten-second timeouts and assert that
the MainWindow initialization message is absent. The fifth checks that the
no-argument path still selects GUI behavior when PySide6 is unavailable.

The focused module passed with five tests. Python compilation, Pylint error-only
analysis and `git diff --check` also passed. No provider or user document was
used, and no full GUI session was started during final validation.
