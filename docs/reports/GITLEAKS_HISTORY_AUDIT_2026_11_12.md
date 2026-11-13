# Gitleaks History Audit - 2026-11-12

## Scope

- Repository history scanned: 1,621 commits, approximately 33.07 MB.
- Scanner: Gitleaks 8.30.1, Git history mode, fully redacted report.
- No secret values are reproduced in this report.

## Classification

The initial scan reported seven findings:

- One `dropbox-api-token` match in `docs/STEP_1_0_READING_LOG.md`. The matched
  text is ordinary roadmap prose containing `Dropbox etc`; it is not a token.
- Six `generic-api-key` matches in five protocol-document locations. Every
  location is an explicitly labelled bad/insecure code example that uses the
  same fictional `sk-...` value. One location is present in two historical
  commits and therefore produced two findings.

All seven findings are false positives. The review found no evidence that any of
the matched values grants access to a provider or account. No credential
rotation or history rewrite is warranted by these findings.

## Remediation

- Added the seven exact fingerprints to `.gitleaksignore`; the allowlist does
  not suppress new matches in the same files or rules. Two current-tree aliases
  for the same reviewed content are also fingerprint-specific.
- Added the local `audit-gitleaks.json` output to `.gitignore` so a redacted or
  non-redacted local report cannot be committed accidentally.
- Preserved the historical protocol examples and original Git history.

## Verification

The complete command was rerun after the narrow allowlist was added:

```bash
gitleaks git . --redact --report-format json --report-path <temporary-report> --timeout 180
```

Result: exit code `0`, 1,621 commits scanned, zero unreviewed findings. The
temporary report contained an empty JSON array.

A separate current-directory scan initially rediscovered the same fictional
API-key example and Dropbox prose under their reorganized paths. After adding
those two exact current-tree fingerprints, the directory scan also returned
zero unreviewed findings.

This result closes only the reviewed Gitleaks findings. It does not replace
dependency, CI, privacy or release-readiness review.
