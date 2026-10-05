# CI Gate Restoration - 2026-10-05

## Scope

This checkpoint repairs the GitHub Actions definitions and local test collection
on `COM-1851754a-2bb0-46de-a084-0f1293011b33`. It does not promote `develop` or
`main`, prove a release, or resolve the historical Qt crash and legacy quality
debt by itself.

## Startup Failure

GitHub run `36336564902` ended as `startup_failure`, with no jobs or check runs.
The official actionlint 1.7.12 release identified
`peaceiris/actions-gh-pages@v3` as using a removed GitHub Actions runner. The docs
workflow now pins the full v4.1.0 commit
`84c30a85c19949d7eee79c4ff27748b70285e453`. Actionlint accepts all current YAML
workflows.

## Reproducibility Repairs

- CI, documentation and benchmarks install Python 3.12 dependencies from
  `poetry.lock` with Poetry 2.1.3 instead of unrelated ad hoc `pip install`
  commands. Poetry keyring access is disabled because the project uses no private
  repository credential.
- `psutil`, imported by runtime source and benchmarks, is now a direct runtime
  dependency and resolves to 7.2.2. The lock otherwise changed only its content
  hash and this package entry.
- Root `requirements-docs.txt` pins Sphinx 8.1.3, the Read the Docs theme 3.1.0
  and autodoc type hints 3.0.1.
- The benchmark PR trigger is reachable. PR results live in `$RUNNER_TEMP`, so
  checking out the base branch cannot delete them, and base dependencies are
  installed after that checkout.
- The security job exports exact versions from Poetry's TOML structure and runs
  `pip-audit --no-deps --disable-pip`; shell parsing cannot turn package
  constraints into redirections.

## Test Isolation

Automated collection previously imported historical executable diagnostics that
use live services, absolute user paths, writes or import-time `sys.exit()`. They
remain in the repository for explicit manual use, but `tests/conftest.py` excludes
37 such scripts and pytest skips `tests/manual`.

Collection now succeeds with 2,477 tests. The CI runner discovers 176 eligible
test modules and starts one pytest process per module, serially. Coverage is
appended across processes and the 80% threshold is enforced only after all
modules finish. This design limits cross-module Qt lifetime contamination and
reports native exits against the responsible module.

## Local Evidence

All Python and Qt commands used system RAM 85%, process-tree RSS 600 MiB and
wall-time 180 second guards where applicable.

| Check | Result | Resource evidence |
| --- | --- | --- |
| `poetry lock` and `poetry check --lock` | passed | 73.9 MiB lock peak |
| Lock synchronization | passed; psutil 7.1.3 to 7.2.2 | 107.9 MiB peak |
| `.venv/bin/python -m pip check` | no broken requirements | avoids stale pip launcher |
| Exact lock export | 97 unique pinned packages | structured TOML parser |
| Exact-lock `pip-audit` | no known vulnerabilities | 48.5 MiB peak |
| Workflow actionlint | all workflow files passed | actionlint 1.7.12 |
| New Python Black/isort/Pylint-E checks | passed | four files checked |
| Affected tests | 12 passed | 62.6 MiB peak |
| Full collection | 2,477 collected | 221.8 MiB peak |
| Serial runner smoke test | 4 passed, reports generated | 108.9 MiB peak |
| Sphinx HTML build | succeeded with 64 legacy warnings | 319.9 MiB peak |

The first isolated docs installation exposed a stale desktop keyring entry and
ended with code 1 at 563.3 MiB. Disabling Poetry keyring access made the retry
reproducible. The strict `-W` experiment correctly failed on 64 existing Sphinx
warnings, including removed API references, malformed docstrings and duplicate
objects. The normal build retains `--keep-going` and reports these warnings; they
are not represented as repaired documentation.

The historical `.venv/bin/pip` launcher still references an older checkout path
and exits before Python starts. The environment itself passes
`.venv/bin/python -m pip check`; workflows consistently use `python -m pip` and
do not depend on that stale generated launcher. Recreating `.venv` from the lock
remains preferable to editing generated entry points in place.

## Honest Limits And Remaining Gate

The old global `pylint src --fail-under=9.0` did not complete within 180 seconds
and reached about 422 MiB while reporting substantial legacy errors and PySide
import false positives. CI therefore performs compile checks plus Black, isort
and Pylint errors-only on changed source files. This is an incremental gate, not
proof that the repository has a global Pylint score of 9.

The full 176-module run was not duplicated locally because it is the remote CI
workload and the historical combined Qt crash requires isolation. The MUST stays
open until the published branch completes a hosted run, demonstrates actual
coverage at or above 80%, uploads Codecov successfully and passes the exact-lock
audit. A missing Codecov secret, account billing lock, coverage deficit or test
failure is a real external/non-pass result and must not be hidden by lowering the
gate.

## Hosted Run Evidence

Commit `5f4c81e` was pushed to the working branch and dispatched exactly once.
GitHub Actions run `37377505762` was accepted for the correct branch and SHA but
completed as `startup_failure` in about one second. The API reports zero jobs,
zero check runs and no downloadable logs, so no project command ran.

The repository reports Actions enabled with all actions allowed. The workflow is
active, and `gh workflow view --yaml --ref` returns content byte-for-byte equal
to the local file. These facts and actionlint exclude a stale push and the known
local syntax/runtime problem; they do not reveal the remaining pre-job cause.
The authenticated CLI lacks the additional `user` scope needed to read account
billing, and no token scope was changed. The earlier account/billing restriction
is consistent with this symptom but is not asserted as confirmed for this run.
No uncertain dispatch was retried.

The CI MUST therefore remains open. The next external action is to inspect or
repair the GitHub account Actions/billing status, then manually rerun this exact
commit once. Changing tests, coverage or dependency gates cannot repair a
failure that happens before jobs are created.
