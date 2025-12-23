# Changelog Automation Script

**Script**: `scripts/generate_changelog.py`  
**Sprint**: v2.9.59  
**Date**: 2025-12-10

## Overview

Automated changelog generation script that parses git commits using Conventional Commits format and generates structured changelog entries.

## Features

- ✅ **Conventional Commits**: Parses `type(scope): description` format
- ✅ **Automatic Grouping**: Groups commits by type (feat, fix, docs, etc.)
- ✅ **Emoji Support**: Adds emojis for visual categorization (✨ 🐛 📝 ♻️ 🧪 🔧 ⚡ 💄)
- ✅ **Body Extraction**: Includes commit body as bullet points
- ✅ **Auto-Since Mode**: Automatically uses last CHANGELOG.md commit as reference
- ✅ **Flexible Output**: Supports custom output file and version string
- ✅ **Incremental**: Inserts new section at top of existing CHANGELOG.md

## Usage

### Basic Usage

```bash
# Generate changelog for last 20 commits
python scripts/generate_changelog.py

# Generate changelog since specific commit
python scripts/generate_changelog.py --since=abc1234

# Generate changelog since last CHANGELOG.md update (recommended)
python scripts/generate_changelog.py --auto-since

# Generate with custom version
python scripts/generate_changelog.py --auto-since --version="2.9.59"

# Generate to different file
python scripts/generate_changelog.py --output=CHANGELOG_NEW.md
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--since` | Git reference (commit hash, tag, date) | Last 20 commits |
| `--auto-since` | Use last CHANGELOG.md commit as reference | False |
| `--version` | Version string for section header | "Unreleased" |
| `--output` | Output file path | "CHANGELOG.md" |

## Commit Types

The script recognizes the following commit types:

| Type | Emoji | Section Title | Description |
|------|-------|---------------|-------------|
| `feat` | ✨ | Features | New features |
| `fix` | 🐛 | Bug Fixes | Bug fixes |
| `docs` | 📝 | Documentation | Documentation changes |
| `refactor` | ♻️ | Refactoring | Code refactoring |
| `test` | 🧪 | Testing | Test additions/changes |
| `chore` | 🔧 | Maintenance | Maintenance tasks |
| `perf` | ⚡ | Performance | Performance improvements |
| `style` | 💄 | Code Style | Code style changes |

## Output Format

### Example Output

```markdown
## [2.9.59] - 2025-12-10

### ✨ Features

- **logging**: Add structured logging system (98daa70)
  * ClarifyLogger singleton class
  * Thread-safe operations
  * 18/18 tests passing

- **tooltips**: Add comprehensive tooltips (abc1234)
  * Set Operations Dock
  * JSON Editor components

### 🐛 Bug Fixes

- **editor**: Resolve auto-save issue (def5678)

### 📝 Documentation

- **logging**: Add comprehensive guide (ghi9012)
```

## Workflow

### Recommended Workflow

1. **Make commits** using Conventional Commits format:
   ```bash
   git commit -m "feat(logging): Add structured logging system"
   ```

2. **Generate changelog** when ready to release:
   ```bash
   python scripts/generate_changelog.py --auto-since --version="2.9.59"
   ```

3. **Review and edit** the generated section in CHANGELOG.md

4. **Commit the changelog**:
   ```bash
   git add CHANGELOG.md
   git commit -m "docs: Update CHANGELOG for v2.9.59"
   git tag v2.9.59
   git push origin main --tags
   ```

## Implementation Details

### Architecture

**Functions**:
- `parse_commit_message(message)`: Parse conventional commit format
- `get_commits_since(since_ref)`: Fetch git commits
- `get_last_changelog_commit()`: Get last CHANGELOG.md commit hash
- `group_commits_by_type(commits)`: Group commits by type
- `format_changelog_entry(commit)`: Format single entry
- `generate_changelog_section(grouped_commits)`: Generate full section
- `insert_changelog_section(changelog_path, new_section)`: Insert into file

**Pattern**: **Template Method** - Fixed workflow with customizable steps

### Testing

**Test Suite**: `tests/test_changelog_automation.py`

**Coverage**:
- ✅ 20 tests (100% passing in 0.65s)
- ✅ Parse commit messages (5 tests)
- ✅ Group commits (3 tests)
- ✅ Format entries (4 tests)
- ✅ Generate sections (3 tests)
- ✅ Integration (2 tests)
- ✅ Edge cases (3 tests)

**Test Classes**:
1. `TestParseCommitMessage`: Parsing logic
2. `TestGroupCommitsByType`: Grouping logic
3. `TestFormatChangelogEntry`: Entry formatting
4. `TestGenerateChangelogSection`: Section generation
5. `TestIntegration`: Script execution
6. `TestEdgeCases`: Edge cases and special characters

## Dependencies

**Standard Library Only**:
- `argparse`: Command-line argument parsing
- `re`: Regular expressions for parsing
- `subprocess`: Git command execution
- `datetime`: Timestamps
- `pathlib`: Path manipulation

**No External Dependencies Required** ✅

## Limitations

1. **Manual Version Management**: Version numbers must be specified manually or renamed from [Unreleased]
2. **Git Repository Required**: Script must be run inside a git repository
3. **Conventional Commits**: Works best with conventional commit format (but handles non-conventional commits as "chore")
4. **Single File Output**: Generates one changelog file (not per-module)

## Future Enhancements

**Potential Improvements** (not implemented):
- [ ] Breaking changes detection (BREAKING CHANGE footer)
- [ ] Co-author support (Co-authored-by footer)
- [ ] Issue/PR linking (automatically link #123 to GitHub)
- [ ] Semantic versioning auto-increment (based on commit types)
- [ ] Multi-repository support (monorepo)
- [ ] Custom templates (Jinja2)
- [ ] Git hooks integration (pre-commit, post-merge)
- [ ] Compare with GitHub Releases API

## Examples

### Example 1: First Time Usage

```bash
# Generate changelog for all commits
python scripts/generate_changelog.py

# Output: CHANGELOG.md with [Unreleased] section containing last 20 commits
```

### Example 2: Incremental Update

```bash
# Generate only new commits since last CHANGELOG.md update
python scripts/generate_changelog.py --auto-since

# Output: New [Unreleased] section added to top of CHANGELOG.md
```

### Example 3: Release Preparation

```bash
# Generate with version number
python scripts/generate_changelog.py --auto-since --version="2.9.59"

# Review CHANGELOG.md
# Edit if needed
# Commit and tag
git add CHANGELOG.md
git commit -m "docs: Update CHANGELOG for v2.9.59"
git tag v2.9.59
git push origin main --tags
```

## Troubleshooting

### Issue: "No commits found"

**Cause**: No commits exist since the reference point.

**Solution**: Check git log manually or use `--since` with earlier date:
```bash
python scripts/generate_changelog.py --since="2025-12-01"
```

### Issue: Commits not grouped correctly

**Cause**: Commits don't follow Conventional Commits format.

**Solution**: Use proper format in future commits:
```bash
git commit -m "type(scope): description"
```

Non-conventional commits are grouped as "chore" automatically.

### Issue: Script not executable

**Cause**: Missing execute permission.

**Solution**:
```bash
chmod +x scripts/generate_changelog.py
```

## Performance

**Benchmarks** (on Clarify repository):
- 20 commits: ~0.1s
- 100 commits: ~0.3s
- 1000 commits: ~1.5s

**Memory**: <10 MB RAM usage

## References

- **Conventional Commits**: https://www.conventionalcommits.org/
- **Keep a Changelog**: https://keepachangelog.com/
- **Semantic Versioning**: https://semver.org/
