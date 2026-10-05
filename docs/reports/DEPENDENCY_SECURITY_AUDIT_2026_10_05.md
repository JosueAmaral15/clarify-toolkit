# Dependency Security Audit - 2026-10-05

## Scope

This report covers the Python dependency lock on
`COM-61bd5563-4023-4060-adee-4c560bb1bcfe`, created from checkpoint `a6e699b`.
It does not promote `develop` or `main`, certify the full application, or replace
the still-broken CI/security promotion gates.

The GitHub Dependabot API reported 24 open alerts on the default branch:
1 critical, 12 high, 8 moderate and 3 low. Twenty-three applied to this COM lock.
The remaining default-branch alert is for `httplib2`, which is absent from the
current `poetry.lock`.

## Lock Remediation

| Package | Before | Locked after | Minimum fixed version used for review |
| --- | ---: | ---: | ---: |
| anyio | 4.12.1 | 4.15.1 | 4.14.2 |
| black | 26.1.0 | 26.10.0 | 26.3.1 |
| cryptography | 46.0.5 | 50.0.2 | 50.0.0 |
| idna | 3.11 | 3.20 | 3.15 |
| lxml | 6.0.2 | 6.1.3 | 6.1.0 |
| pyasn1 | 0.6.2 | 0.6.4 | 0.6.4 |
| Pygments | 2.19.2 | 2.21.0 | 2.20.0 |
| pytest | 9.0.2 | 9.1.1 | 9.0.3 |
| requests | 2.32.5 | 2.34.2 | 2.33.0 |
| urllib3 | 2.6.3 | 2.8.0 | 2.8.0 |
| uv | 0.10.3 | 0.12.23 | 0.11.15 |

The audit of the installed environment additionally identified vulnerable locked
transitives `click` and `virtualenv`. They were updated from 8.3.1 to 8.5.0 and
from 20.36.1 to 21.14.5. Resolving `virtualenv` also updated `filelock` to 4.0.12
and added its `python-discovery` 1.6.1 dependency. `typing-extensions` moved from
4.15.0 to 4.16.0 as required by the updated dependency graph.

The direct development floors now require `black>=26.3.1` and `pytest>=9.0.3`.
Other changes remain resolver-managed transitives rather than new direct project
dependencies.

## Audit Evidence

- `poetry check --lock`: passed.
- `poetry install -E dev --no-root --no-interaction --dry-run`: no pending
  operations after synchronization.
- `pip check`: no broken requirements.
- Structured threshold assertions passed for 13 reviewed locked packages;
  `httplib2` was confirmed absent from the lock.
- A requirements view generated with `tomllib` from all 96 exact lock entries was
  audited with `pip-audit --no-deps --disable-pip`: no known vulnerabilities.
- Lock synchronization peaked at 289 MiB process-tree RSS; the exact-lock audit
  peaked at 58 MiB. No live provider was contacted.

The existing `.venv` is intentionally not a clean lock-only environment. A full
path audit initially found 31 advisory rows in five packages. After the two
locked transitives were corrected, it found 22 rows in three remaining extras:
the environment's own `pip` 25.3, `httplib2` 0.31.2 and `starlette` 0.50.0.
`httplib2`/`starlette` are retained by extra, non-lock packages already installed
in this historical environment; forcing their removal or incompatible upgrade
was outside this change. One repeat attempt stopped at the RAM85.6% guard and was
not counted; a later run completed below the guard with 79 MiB peak RSS.

For release or CI evidence, create a clean environment from `poetry.lock` instead
of treating this historical `.venv` as reproducible.

## Compatibility Evidence

All modules ran serially, with offscreen Qt where applicable, temporary settings,
20-second pytest timeouts, 180-second wall limits, RAM85% and 600 MiB process-tree
RSS guards. GUI modules used separate processes.

| Area | Tests | Result | Peak RSS |
| --- | ---: | --- | ---: |
| Gemini clients and tutorial request cleanup, mocked SDK | 6 | passed | 127 MiB |
| Local Ollama dock contract | 1 | passed | 199 MiB |
| Translation catalogue lookup | 10 | passed | 186 MiB |
| I18n expansion | 14 | passed | 64 MiB |
| Update controller, excluding full MainWindow fixture | 3 | passed | 181 MiB |
| Plugin system | 16 | passed | 74.4 MiB |
| Tutorial localization | 3 | passed | 196.7 MiB |
| Document loader and DOCX table reconstruction | 11 | passed | 101 MiB |
| **Total** | **64** | **passed** | **199 MiB max** |

The DOCX module emitted five pre-existing `PytestReturnNotNoneWarning` warnings
because legacy tests return booleans instead of asserting. They are not test
failures, but should be cleaned separately. No native crash occurred.

## Remaining Gate

This branch supplies a locally audited remediation candidate. The MUST remains
open until the change is reviewed and integrated, a clean lock-only environment
is validated by restored CI, and GitHub confirms the default-branch alerts are
closed. The separate CI startup failure and historical Qt crash investigations
remain open.
