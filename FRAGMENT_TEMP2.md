# Multi-Programmer Git Workflow Guide

**Purpose**: Branch-based workflow for multiple developers working in parallel  
**Audience**: Open source projects, small teams, educational projects  
**Last Updated**: 2026-01-18  
**Version**: 1.0

---

## 📋 Overview

This document provides a comprehensive git workflow strategy for **projects with multiple programmers** working simultaneously on documentation, features, or refactoring.

### Key Principles

1. **Isolation**: Each programmer works in their own branch
2. **Standardization**: No programmer suffixes in file names
3. **Clarity**: Standard directory structure (no programmer-specific folders)
4. **Traceability**: All changes tracked through git branches
5. **Collaboration**: Pull requests enable code review before merge

### Benefits

- ✅ **No conflicts** - Multiple programmers work simultaneously
- ✅ **Clean naming** - Files describe content, not authorship
- ✅ **Standard structure** - Single directory tree for all
- ✅ **Git history** - Track ownership via branches and commits
- ✅ **Code review** - PR workflow before merging to main

---

## 🌿 Branch Naming Strategies

The workflow supports **TWO branch patterns** depending on your project needs:

### **Pattern 1: COM-UUID** (Maximum Traceability)

**Format**: `COM-[UUID]`  
**Example**: `COM-a5e531b2-5d4f-a827-b3c8-24a52b27f281`

**When to use:**
- AI-generated branches
- Need unique identification
- Automated workflows
- Short-lived task branches

**Generate:**
```bash
# Linux/Mac
git checkout -b COM-$(uuidgen | tr '[:upper:]' '[:lower:]')

# Python (cross-platform)
git checkout -b COM-$(python -c "import uuid; print(uuid.uuid4())")
```

**Pros**: Unique, no conflicts, automated  
**Cons**: Not human-readable

---

### **Pattern 2: COM<N>-feature** (Recommended Default) ⭐

**Format**: `COM<N>-<feature-name>`  
**Examples**: 
- `COM2-fix-authentication`
- `COM5-add-user-profile`
- `COM12-refactor-database`

**When to use:**
- Most development work (RECOMMENDED)
- Feature development
- Bug fixes
- Refactoring tasks

**Create:**
```bash
# Feature
git checkout -b COM2-add-search-filter

# Bug fix
git checkout -b COM2-fix-memory-leak

# Refactor
git checkout -b COM5-refactor-api-client
```

**Pros**: Human-readable, clear purpose, easy management  
**Cons**: Need descriptive naming

---

### **Pattern 3: COM<N>** (Persistent Workspace) [Optional]

**Format**: `COM<N>`  
**Examples**: `COM2`, `COM9`, `COM12`

**When to use:**
- Documentation work spanning multiple sessions
- Study/learning phases
- General personal workspace
- Don't want branch-per-task overhead

**Create:**
```bash
git checkout -b COM2
```

**Pros**: Simple, one branch for all work  
**Cons**: Can become cluttered, less granular history

---

## 🎯 Quick Pattern Selection Guide

| Scenario | Pattern | Example |
|----------|---------|---------|
| AI creating branch | Pattern 1 | `COM-[UUID]` |
| Fixing specific bug | Pattern 2 ⭐ | `COM2-fix-auth` |
| Adding feature | Pattern 2 ⭐ | `COM5-user-profile` |
| Documentation work | Pattern 2 or 3 | `COM2-update-docs` or `COM2` |
| Refactoring | Pattern 2 ⭐ | `COM12-refactor-api` |

**Recommendation**: Use **Pattern 2** (COM<N>-feature) for most work!

---

## 📁 File Naming and Directory Standards

### File Naming Rules

**Standard Format** (NO programmer suffixes):
```
<DESCRIPTION>.<extension>
```

**Examples**:
- ✅ `USER_GUIDE.md` (correct)
- ✅ `api_client.py` (correct)
- ✅ `database_schema.sql` (correct)
- ❌ `USER_GUIDE_2.md` (wrong - has programmer suffix)
- ❌ `api_client_programmer5.py` (wrong)

**Exception**: Only add suffixes when **naming conflicts** exist and both versions must be preserved.

### Directory Structure

**Standard Locations** (no programmer-specific folders):

| Content Type | Suggested Location | Example |
|--------------|-------------------|---------|
| Documentation | `docs/` | `docs/USER_GUIDE.md` |
| Source code | `src/` or `lib/` | `src/api_client.py` |
| Tests | `tests/` or `test/` | `tests/test_api_client.py` |
| Configuration | `config/` or root | `config/database.yml` |
| Scripts | `scripts/` | `scripts/deploy.sh` |

**Avoid** (programmer-specific folders):
- ❌ `docs/programmer_1/`
- ❌ `src/COM2/`
- ❌ Any per-programmer subdirectories

**Why?** Git branches already separate programmer work. No need for folder isolation.

---

## 🔄 Complete Workflow

### Step 1: Create Your Branch

**First time** - create your branch (choose pattern):

```bash
# Pattern 1: UUID (AI-generated)
git checkout -b COM-$(uuidgen | tr '[:upper:]' '[:lower:]')

# Pattern 2: Feature (RECOMMENDED)
git checkout -b COM2-add-authentication

# Pattern 3: Workspace (optional)
git checkout -b COM2
```

**Verify:**
```bash
git branch
# Output: * COM2-add-authentication
```

---

### Step 2: Make Changes

Work normally in your branch:

```bash
# Edit files
vim src/auth.py
vim docs/AUTH_GUIDE.md

# Check status
git status

# View changes
git diff
```

---

### Step 3: Commit Regularly

**Commit format**: `<type>: <description>`

```bash
# Stage changes
git add src/auth.py docs/AUTH_GUIDE.md

# Commit with descriptive message
git commit -m "feat: add JWT authentication system"

# More commits as you work
git commit -m "docs: update authentication guide"
git commit -m "test: add auth integration tests"
```

**Commit types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance
- `style:` - Formatting

---

### Step 4: Push to Remote

```bash
# Push your branch
git push origin COM2-add-authentication

# First time push (set upstream)
git push -u origin COM2-add-authentication
```

---

### Step 5: Keep Branch Updated

**Sync with main regularly** to avoid large conflicts:

```bash
# Get latest main
git fetch origin main

# Merge main into your branch
git merge origin/main

# Or rebase (cleaner history)
git rebase origin/main

# Resolve conflicts if any
# ... edit files ...
git add <resolved_files>
git commit
```

---

### Step 6: Create Pull Request

**When feature is ready:**

1. Push latest changes: `git push origin COM2-add-authentication`
2. Go to your repository on GitHub/GitLab/Bitbucket
3. Click "Create Pull Request" or "Merge Request"
4. Fill in:
   - **Title**: Clear feature description
   - **Description**: What changed, why, how to test
   - **Reviewers**: Assign team members (if applicable)

**Example PR description:**
```markdown
## Summary
Added JWT authentication system for API endpoints

## Changes
- Implemented JWT token generation and validation
- Added middleware for protected routes
- Updated API documentation

## Testing
- All existing tests pass
- Added 15 new authentication tests
- Manual testing completed

## Checklist
- [x] Tests pass
- [x] Documentation updated
- [x] No breaking changes
```

---

### Step 7: After Merge - Cleanup

**Once merged to main:**

```bash
# Switch to main
git checkout main

# Pull merged changes
git pull origin main

# Delete local branch (optional)
git branch -d COM2-add-authentication

# Delete remote branch (optional)
git push origin --delete COM2-add-authentication
```

---

## ⚙️ Handling Merge Conflicts

**If your PR has conflicts with main:**

```bash
# On your branch
git fetch origin main
git merge origin/main

# Git will show conflicts:
# CONFLICT (content): Merge conflict in src/auth.py

# Open conflicted files
vim src/auth.py

# Look for conflict markers:
# <<<<<<< HEAD
# Your changes
# =======
# Main branch changes
# >>>>>>> origin/main

# Edit to resolve conflict (keep what's needed)

# Stage resolved files
git add src/auth.py

# Complete merge
git commit -m "merge: resolve conflicts with main"

# Push updated branch
git push origin COM2-add-authentication
```

**Common conflict scenarios:**
- Same file edited in main and your branch
- File renamed in main but edited in your branch
- File deleted in main but modified in your branch

---

## 💾 Saving Unfinished Work (git stash)

**Need to switch branches with uncommitted changes?**

```bash
# Save work temporarily
git stash save "WIP: implementing user authentication"

# Switch to another branch
git checkout main

# Later, return to your branch
git checkout COM2-add-authentication

# Restore stashed work
git stash pop
```

**Advanced stash:**
```bash
# List all stashes
git stash list

# Apply specific stash (keep in stash list)
git stash apply stash@{0}

# Drop specific stash
git stash drop stash@{0}

# Clear all stashes
git stash clear
```

---

## 📝 File Ownership and Attribution

**Track who created/modified files:**

```bash
# See full file history
git log --follow <filename>

# See line-by-line authors
git blame <filename>

# See who last modified
git log -1 <filename>

# See file changes with diffs
git log -p --follow <filename>
```

**Quick lookup:**
- Files in `origin/COM2` branch = Programmer #2's work
- Files in `main` = Merged code (check `git log` for author)

**Why this matters:**
- Questions about code → Know who to ask
- Bug investigation → Trace to original author
- Code review → Understand context
- Credit → Proper attribution

---

## ✅ Pre-Merge Checklist

**Before creating PR, verify:**

### 1. Tests
- [ ] All existing tests pass
- [ ] New tests added for new features
- [ ] Manual testing completed
- [ ] Edge cases covered

**Commands:**
```bash
# Python
pytest tests/

# JavaScript
npm test

# Go
go test ./...

# Ruby
rspec spec/
```

### 2. Code Quality
- [ ] Linter passes (no warnings)
- [ ] Formatter applied
- [ ] No debug statements (console.log, print, etc.)
- [ ] No commented-out code

**Commands:**
```bash
# Python
pylint src/
black src/ --check

# JavaScript
npm run lint
prettier --check src/

# Go
golint ./...
gofmt -d .

# Ruby
rubocop
```

### 3. Documentation
- [ ] README updated (if API changes)
- [ ] Code comments for complex logic
- [ ] CHANGELOG updated
- [ ] API documentation current

### 4. Git Hygiene
- [ ] Commit messages descriptive
- [ ] Branch up-to-date with main
- [ ] No unnecessary files (.env, .DS_Store, etc.)
- [ ] Sensitive data removed

**Verification:**
```bash
# Check commits
git log --oneline COM2-add-auth ^main

# Check for unwanted files
git status
git ls-files | grep -E "\.env|\.DS_Store|node_modules"

# Verify sync with main
git fetch origin main
git log COM2-add-auth..origin/main
```

---

## 🚨 Emergency Commands

### Abort Merge
```bash
git merge --abort
```

### Undo Last Commit (Keep Changes)
```bash
git reset --soft HEAD~1
```

### Undo Last Commit (Discard Changes) ⚠️
```bash
git reset --hard HEAD~1
```

### Restore Deleted File
```bash
git checkout HEAD -- <filename>
```

### Discard All Local Changes ⚠️
```bash
git reset --hard HEAD
```

### Force Push (Careful!) ⚠️
```bash
# Only on YOUR branch, NEVER on main
git push --force origin COM2-add-auth
```

---

## 📊 Useful Git Commands

### Branch Management
```bash
# List all branches
git branch -a

# Switch branch
git checkout <branch>

# Create and switch
git checkout -b <new-branch>

# Delete branch
git branch -d <branch>

# Rename current branch
git branch -m <new-name>
```

### Viewing Changes
```bash
# See what changed
git diff

# See staged changes
git diff --cached

# See file names only
git diff --name-only

# Compare branches
git diff main..COM2-add-auth
```

### History and Attribution
```bash
# View commit history
git log

# Compact view
git log --oneline

# With file changes
git log --stat

# Graphical view
git log --graph --oneline --all

# Find who wrote code
git blame <filename>

# Track file renames
git log --follow <filename>
```

### Remote Operations
```bash
# View remotes
git remote -v

# Fetch latest
git fetch origin

# Pull and merge
git pull origin main

# Push branch
git push origin <branch>

# Delete remote branch
git push origin --delete <branch>
```

---

## 🔒 Best Practices

### 1. Commit Often
- Small, focused commits are better than large ones
- Makes code review easier
- Easier to revert if needed

### 2. Write Good Commit Messages
**Format:**
```
<type>: <short summary> (50 chars max)

<detailed description if needed>
<explain why, not what>

<footer with issue references>
Fixes #123
```

**Example:**
```
feat: add JWT authentication middleware

Implemented token-based authentication to secure API endpoints.
Tokens expire after 24 hours and include user role information.

Tested with 15 integration tests covering:
- Token generation
- Token validation
- Expired token handling
- Invalid token handling

Fixes #45
```

### 3. Keep Branches Short-Lived
- Merge to main frequently (daily or every few days)
- Long-lived branches = more conflicts
- Use feature flags if need to hide incomplete features

### 4. Review Your Own Code First
Before creating PR:
```bash
# Review all your changes
git diff main..COM2-add-auth

# Check specific files
git diff main..COM2-add-auth -- src/auth.py
```

### 5. Communicate
- Comment on PRs with context
- Ask questions if code is unclear
- Explain design decisions
- Request specific feedback

### 6. Never Force Push to Main ⚠️
```bash
# NEVER do this:
git push --force origin main  # ❌ DANGEROUS

# Only force push YOUR branch if needed:
git push --force origin COM2-add-auth  # ⚠️ Use carefully
```

### 7. Use .gitignore
**Essential entries:**
```gitignore
# Dependencies
node_modules/
vendor/
__pycache__/

# Environment
.env
.env.local
*.secret

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Build outputs
dist/
build/
*.pyc
```

---

## 🎓 Learning Resources

### Official Git Documentation
- [Git Book](https://git-scm.com/book/en/v2) - Comprehensive guide
- [Git Cheat Sheet](https://training.github.com/downloads/github-git-cheat-sheet.pdf)
- [Git Workflows](https://www.atlassian.com/git/tutorials/comparing-workflows)

### Branching Strategies
- Feature Branch Workflow (recommended for this guide)
- Gitflow Workflow (for release management)
- Trunk-Based Development (for rapid deployment)

### Pull Request Best Practices
- [GitHub PR Guide](https://docs.github.com/en/pull-requests)
- [Google Code Review Guidelines](https://google.github.io/eng-practices/review/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 🛠️ Adaptation for Your Project

This guide is **template**. Adapt it:

### Project-Specific Customization

1. **Branch naming**: Adjust pattern to match your conventions
   - Add project prefix: `PROJ-COM2-feature`
   - Use issue numbers: `COM2-fix-issue-123`

2. **Directory structure**: Match your project layout
   ```
   your-project/
   ├── src/          # Your source location
   ├── docs/         # Your docs location
   ├── tests/        # Your tests location
   └── ...
   ```

3. **Testing commands**: Update for your stack
   ```bash
   # Add your specific test commands
   npm run test:unit
   npm run test:e2e
   make test
   cargo test
   ```

4. **Linting/formatting**: Use your tools
   ```bash
   # Your linters
   npm run lint
   cargo clippy
   mix format --check-formatted
   ```

5. **CI/CD integration**: Reference your pipelines
   - GitHub Actions
   - GitLab CI
   - Jenkins
   - CircleCI

---

## 📖 Quick Reference Card

### Daily Workflow
```bash
# 1. Switch to your branch
git checkout COM2-add-feature

# 2. Make changes
vim src/file.py

# 3. Stage and commit
git add -A
git commit -m "feat: implement feature X"

# 4. Push
git push origin COM2-add-feature
```

### Sync with Main
```bash
git fetch origin main
git merge origin/main
```

### Create PR
1. Push branch
2. Go to repository web interface
3. Click "Create Pull Request"
4. Fill description
5. Request review

### After Merge
```bash
git checkout main
git pull origin main
git branch -d COM2-add-feature
```

---

## 🎯 Summary

**Key Takeaways:**

1. **Use branches** - One per programmer or per feature
2. **Standard naming** - No programmer suffixes in files
3. **Standard structure** - No programmer folders
4. **Commit often** - Small, focused commits
5. **Sync regularly** - Merge main into your branch frequently
6. **Code review** - Always use pull requests
7. **Git tracks ownership** - Use `git log` and `git blame`

**Recommended workflow:**
- **Pattern 2 (COM<N>-feature)** for branches
- **Standard naming** for files and folders
- **Regular commits** with clear messages
- **Pull requests** for code review
- **Branch cleanup** after merge

---

**Document Purpose**: General template for multi-programmer git workflows  
**Adapt**: Customize for your project's needs  
**Questions**: Refer to [Git documentation](https://git-scm.com/doc)

**Version**: 1.0 (2026-01-18)  
**License**: CC0 1.0 Universal (Public Domain) - Use freely!
