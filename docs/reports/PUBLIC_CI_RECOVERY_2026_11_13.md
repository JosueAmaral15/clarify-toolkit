# Public CI Recovery - 2026-11-13

## Failure Reproduced

Pull request 19 reached the legacy `pytest tests/` command and failed before
running any test. Pytest imported `tests/com8/test_cli_direct_COM8.py`, which
uses an absolute personal document path, calls a live translation provider and
executes `sys.exit()` at import time. The incomplete workflow also installed
only PySide6 and pytest tools instead of the locked application dependencies.

After excluding that historical executable diagnostic, collection exposed an
invalid package import in `tests/test_smart_truncate_word_boundary_3.py`.
Correcting it allowed collection to continue and exposed an actual
`IndentationError` in `src/plugins/example_export_csv.py`. The stray unreachable
line was removed rather than hiding the source file from compilation.

## Repair

- CI installs application and test dependencies from `poetry.lock` with Poetry
  2.1.3 and validates lock consistency in a separate job.
- `tests/conftest.py` identifies historical executable diagnostics that remain
  available for explicit manual use but are not automated pytest modules.
- `tests/manual` is excluded through pytest's canonical `norecursedirs` option.
- `scripts/ci/run_tests_by_module.py` runs eligible modules serially in isolated
  processes while accumulating coverage. A native or Python failure is tied to
  its module instead of contaminating the remainder of one large Qt process.
- `psutil` is now a locked direct dependency because production source imports
  it at module load time.
- Static CI compiles all Python sources and checks only changed production
  Python files with Black, isort and Pylint errors-only. This does not claim
  that the legacy repository already satisfies a global formatting score.

## Local Evidence

- Focused runner policy: `1 passed`.
- Full collection: `1,533 tests collected` in 9.10 seconds; no collection error.
- Isolated runner smoke: `9 passed` across two separate modules.
- `compileall` for `src`, `tests` and `scripts/ci`: passed.
- Black, isort and Pylint errors-only on touched Python files: passed.
- `poetry check --lock`: passed; dry-run confirms all locked application and
  development dependencies, including odfpy and psutil.
- Workflow YAML parsed with the expected `test`, `static` and `lock` jobs.
- `git diff --check`: passed.
- Gitleaks Git history: 1,647 commits scanned, no findings.
- Gitleaks current tree: 56.25 MB scanned, no findings.

## Honest Limit

The complete 1,533-test workload was not duplicated locally. GitHub Actions is
the bounded integration environment for the serial suite. The canonical task
remains open until the published pull request proves dependency installation,
collection, module execution, coverage and artifact behavior. Any failing
module will be reported and repaired as a separate evidenced defect rather than
silenced or converted into a broad exclusion.
