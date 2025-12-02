# CI/CD Setup Documentation

## Overview

This document describes the CI/CD Quality Gates setup for the Clarify project, specifically for the JSX Parameter Extractor feature.

## Tools Configured

### 1. Black (Code Formatter)
- **Purpose**: Automatic Python code formatting
- **Configuration**: `.pre-commit-config.yaml`, `pyproject.toml`
- **Line Length**: 120 characters
- **Usage**: `python -m black src/extractors/`

### 2. isort (Import Sorter)
- **Purpose**: Organize and sort Python imports
- **Configuration**: `pyproject.toml`
- **Profile**: black-compatible
- **Usage**: `python -m isort src/extractors/`

### 3. Pylint (Code Quality Linter)
- **Purpose**: Static code analysis and quality checks
- **Configuration**: `.pylintrc`, `pyproject.toml`
- **Threshold**: 9.0/10 minimum score
- **Disabled Checks**: C0111 (missing-docstring), C0103 (invalid-name), R0913 (too-many-arguments), etc.
- **Usage**: `python -m pylint src/extractors/ --rcfile=.pylintrc`

### 4. Pre-commit Hooks
- **Purpose**: Automatic quality checks before commits
- **Configuration**: `.pre-commit-config.yaml`
- **Installation**: 
  ```bash
  pip install pre-commit
  pre-commit install
  ```
- **Manual Run**: `pre-commit run --all-files`

## Local CI Script

### ci_quality_check.sh

A bash script that runs all quality gates locally before committing:

```bash
./ci_quality_check.sh
```

**Steps Executed:**
1. ✅ Black formatter check (auto-fix if needed)
2. ✅ isort import sorting (auto-fix if needed)
3. ✅ Pylint code quality (must score >= 9.0/10)
4. ✅ Python syntax validation
5. ✅ Functional tests (6 tests must pass)

**Exit Codes:**
- `0`: All quality gates passed
- `1`: One or more gates failed

## Quality Standards

### Code Formatting
- Line length: 120 characters
- Indentation: 4 spaces
- Quote style: Consistent (handled by Black)
- Trailing whitespace: Removed

### Import Organization
- Standard library imports first
- Third-party imports (PySide6)
- First-party imports (src.*)
- Local imports last

### Code Quality Metrics
- Pylint score: >= 9.0/10
- Maximum function arguments: 10
- Maximum class attributes: 15
- Maximum nested blocks: 6 (with warnings)

### Testing
- All 6 functional tests must pass
- Test coverage includes:
  - Attribute extraction
  - Standard tag filtering
  - String-only filtering
  - Case style conversions
  - Avoid-keys filtering
  - Text truncation

## Integration with Git

### Pre-commit Hooks (Optional)

To enable automatic checks before every commit:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

### Manual Workflow

If pre-commit hooks are not installed, run manually before committing:

```bash
# Run all quality checks
./ci_quality_check.sh

# If all pass, commit
git add .
git commit -m "feat(jsx-extractor): your message"
```

## Files Created/Modified

### Configuration Files
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `.pylintrc` - Pylint rules and settings
- `pyproject.toml` - Updated with tool configurations
- `ci_quality_check.sh` - Local CI script

### Quality Gate Results

**Current Status (December 2, 2025):**
- ✅ Black: 6 files formatted
- ✅ isort: 6 files sorted
- ✅ Pylint: Score 9.65/10
- ✅ Syntax: No errors
- ✅ Tests: 6/6 passed

## Troubleshooting

### Black Formatting Conflicts
If Black and Pylint disagree, Black takes precedence. Pylint's line-length check is disabled (C0301).

### Import Order Issues
Run `isort` with `--profile=black` to ensure compatibility with Black.

### Pylint Score Too Low
Review warnings with:
```bash
python -m pylint src/extractors/ --rcfile=.pylintrc
```

Common issues:
- Too many arguments: Consider using dataclasses or config objects
- Too many nested blocks: Extract helper functions
- Unused imports: Remove or use `# pylint: disable=unused-import`

## Future Enhancements

### GitHub Actions (Optional)
Create `.github/workflows/ci.yml` to run quality gates on every push:

```yaml
name: CI Quality Gates
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: ./ci_quality_check.sh
```

### Additional Tools (Optional)
- **mypy**: Type checking
- **pytest**: More comprehensive testing framework
- **coverage**: Code coverage reports
- **bandit**: Security linting

## References

- Black: https://black.readthedocs.io/
- isort: https://pycqa.github.io/isort/
- Pylint: https://pylint.readthedocs.io/
- Pre-commit: https://pre-commit.com/

## Maintenance

**Update Frequency:**
- Configuration files: As needed when adding new tools
- CI script: When adding new quality gates
- This documentation: When procedures change

**Responsible:** Development Team
**Last Updated:** December 2, 2025
