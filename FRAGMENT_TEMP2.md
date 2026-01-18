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

## 🤖 AI-Assisted Workflows (Optional)

**For projects using AI pair programming or automation:**

### AI-Assisted Merge

**Request AI to merge your branch (if supported by your tooling):**

```markdown
"Please merge my COM2-add-authentication branch into main after verifying:
- [ ] All tests pass
- [ ] No conflicts with main
- [ ] Files follow naming conventions
- [ ] Commit messages are descriptive"
```

**AI merge workflow:**
```bash
# AI performs these steps:

# 1. Switch to target branch
git checkout main

# 2. Merge source branch
git merge COM2-add-authentication

# 3. If conflicts, resolve intelligently or ask user

# 4. If no conflicts, push
git push origin main

# 5. Optionally delete merged branch
git branch -d COM2-add-authentication
git push origin --delete COM2-add-authentication
```

**Merge options:**
```bash
# Standard merge (preserves branch history)
git merge COM2-add-authentication

# No fast-forward (creates merge commit)
git merge --no-ff COM2-add-authentication

# Squash commits (single commit in main)
git merge --squash COM2-add-authentication
```

**AI pre-merge verification:**
1. ✅ Fetch latest main: `git fetch origin main`
2. ✅ Check for conflicts: `git merge --no-commit --no-ff origin/main`
3. ✅ Run tests (if available)
4. ✅ Verify file naming conventions
5. ✅ Check commit message quality
6. ✅ Confirm no debug statements

**AI MUST ask user for approval before executing merge.**

**Manual approval required for:**
- Breaking changes
- Large refactors (>500 lines)
- Production-critical code
- Database migrations
- Security-related changes

### AI Conflict Resolution Strategy

**When AI encounters conflicts, it can consider:**

1. **Code Quality:**
   - Linter scores (prefer higher scores)
   - Follows project patterns
   - Better error handling
   - More comprehensive tests

2. **Functionality:**
   - More complete implementation
   - Fewer bugs/edge cases
   - Better performance
   - Clearer code

3. **Recency:**
   - Latest main branch changes (usually preferred)
   - Unless older code is objectively better

4. **Context:**
   - Project conventions
   - Related code patterns
   - Documentation references

**AI MUST ask user when:**
- Both versions equally good
- Breaking changes involved
- Business logic differences
- Security implications
- Unclear which approach is better

---

## 📊 Verification Commands

**After completing workflow steps, verify success:**

### Check Branch Status
```bash
# Verify current branch
git branch --show-current
# Output: COM2-add-authentication

# List all branches
git branch -a

# Check if branch exists on remote
git ls-remote --heads origin COM2-add-authentication
```

### Verify Commits
```bash
# Count commits in your branch not in main
git rev-list --count main..COM2-add-authentication

# List commits with one-line summaries
git log --oneline main..COM2-add-authentication

# Show full commit details
git log main..COM2-add-authentication
```

### Check for Uncommitted Changes
```bash
# Verify working tree is clean
git status
# Output should be: "nothing to commit, working tree clean"

# Check for unstaged changes
git diff

# Check for staged changes
git diff --cached
```

### Verify Remote Sync
```bash
# Check if local branch is up-to-date with remote
git fetch origin
git status
# Output: "Your branch is up to date with 'origin/COM2-add-authentication'"

# Check if main is ahead of your branch
git fetch origin main
git log COM2-add-authentication..origin/main
# Empty output = you're up-to-date
```

### Verify Merge Success
```bash
# After merging to main, verify your commits are there
git checkout main
git log --oneline -10

# Verify file changes merged correctly
git diff HEAD~5..HEAD -- path/to/your/file

# Check that branch was deleted (after cleanup)
git branch -a | grep COM2-add-authentication
# Should return nothing if deleted
```

---

## 🎯 Benefits and Outcomes

**What you gain from this workflow:**

### 1. **Parallel Development** ✅
- Multiple programmers work simultaneously without stepping on each other
- No waiting for others to finish
- Branch isolation prevents interference

### 2. **Clean Repository** ✅
- File names describe content, not authorship
- Standard directory structure (no programmer folders)
- Easy to find files
- Professional appearance

### 3. **Git History Preservation** ✅
- Track who created/modified files via `git log`
- Understand why changes were made via commit messages
- Easy to revert specific changes if needed
- Blame/credit properly attributed

### 4. **Code Review Culture** ✅
- Pull requests enable peer review
- Catch bugs before merge
- Share knowledge across team
- Improve code quality

### 5. **Easy Rollback** ✅
- Can delete branch if experiment fails
- Revert merge if issues found
- Main branch stays stable
- Low-risk experimentation

### 6. **Conflict Resolution** ✅
- Conflicts happen in programmer's branch (not main)
- Easier to resolve (smaller scope)
- Main branch unaffected during resolution
- Learn git conflict resolution skills

### 7. **Documentation** ✅
- Commit messages document intent
- PR descriptions explain why
- Git history becomes project documentation
- Future developers understand decisions

---

## 🔒 Common Mistakes and Lessons Learned

**Learn from these common pitfalls:**

### Mistake 1: Working Directly on Main ❌

**What NOT to do:**
```bash
git checkout main
vim important_file.py
git commit -m "fix bug"
git push origin main  # ❌ WRONG
```

**Why it's bad:**
- No code review
- Breaks others' work immediately
- Can't easily revert
- No isolation for testing

**Correct approach:**
```bash
git checkout -b COM2-fix-bug
vim important_file.py
git commit -m "fix: resolve memory leak in auth module"
git push origin COM2-fix-bug
# Create PR, get review, then merge
```

---

### Mistake 2: Large, Infrequent Commits ❌

**What NOT to do:**
```bash
# Work for 2 weeks...
git add -A
git commit -m "various changes"  # ❌ WRONG
```

**Why it's bad:**
- Hard to review
- Hard to revert specific changes
- Loses granular history
- Difficult to find bugs

**Correct approach:**
```bash
# Commit after each logical change
git commit -m "feat: add user login endpoint"
# ... work more ...
git commit -m "test: add login endpoint tests"
# ... work more ...
git commit -m "docs: document authentication API"
```

---

### Mistake 3: Ignoring Conflicts ❌

**What NOT to do:**
```bash
git merge origin/main
# CONFLICT in file.py
git add file.py  # ❌ Without resolving!
git commit
```

**Why it's bad:**
- Code might not compile
- Introduces bugs
- Breaks functionality
- Wastes team time

**Correct approach:**
```bash
git merge origin/main
# CONFLICT in file.py

# Open file and resolve conflicts
vim file.py
# Remove markers, choose correct code

# Test that it works
npm test

# Then commit
git add file.py
git commit -m "merge: resolve conflicts with main"
```

---

### Mistake 4: Force Pushing to Main ❌

**What NOT to do:**
```bash
git push --force origin main  # ❌ CATASTROPHIC!
```

**Why it's bad:**
- **DESTROYS other people's work**
- Rewrites shared history
- Breaks everyone's local repos
- Can lose critical commits

**Correct approach:**
```bash
# Only force push YOUR branch if necessary
git push --force origin COM2-add-feature  # ⚠️ OK (your branch)

# NEVER force push main
# NEVER force push shared branches
```

---

### Mistake 5: Not Syncing with Main ❌

**What NOT to do:**
```bash
# Work on branch for 3 weeks without syncing
git checkout COM2-add-feature
# ... work work work ...
# Now merge to main
git checkout main
git merge COM2-add-feature  # ❌ HUGE CONFLICTS!
```

**Why it's bad:**
- Massive conflicts
- Hard to resolve
- Duplicated work
- Integration nightmares

**Correct approach:**
```bash
# Sync with main every 1-3 days
git checkout COM2-add-feature
git fetch origin main
git merge origin/main
# Resolve small conflicts as they appear

# When ready to merge, conflicts are minimal
```

---

### Mistake 6: Poor Commit Messages ❌

**What NOT to do:**
```bash
git commit -m "fix"  # ❌ What fix?
git commit -m "update"  # ❌ Update what?
git commit -m "wip"  # ❌ Not descriptive
```

**Why it's bad:**
- Future you won't understand
- Hard to find specific changes
- No context for reviewers
- Looks unprofessional

**Correct approach:**
```bash
git commit -m "fix: resolve null pointer exception in user login"
git commit -m "feat: add password reset functionality"
git commit -m "docs: update API documentation for new endpoints"
```

---

### Mistake 7: Forgetting to Delete Branches ❌

**What happens:**
```bash
git branch -a
# 50 old branches cluttering your repo!
```

**Why it's bad:**
- Hard to find active branches
- Wastes mental energy
- Looks messy
- Confuses new contributors

**Correct approach:**
```bash
# After merge, delete branch
git branch -d COM2-add-feature
git push origin --delete COM2-add-feature

# Periodically clean up
git fetch --prune
git branch -d $(git branch --merged | grep -v main)
```

---

### Real Incident Example: `.git/index.lock`

**Scenario:** During a git operation, an error occurred:
```
fatal: Unable to create '.git/index.lock': File exists
```

**Wrong response (don't do this):**
```bash
rm -f .git/index.lock  # ❌ Did this without asking
git add -A
git commit
```

**Why it was wrong:**
- Didn't investigate if git process was still running
- Removed system file without permission
- Could have corrupted repository
- Didn't explain risks

**Correct response:**
1. **STOP** - Don't immediately delete system files
2. **Investigate** - Check if git process is running: `ps aux | grep git`
3. **Inform user** - Explain the situation and risks
4. **Ask permission** - Request approval before removing lock file
5. **Document** - Explain what happened and why

**Lesson:** Always ask before risky operations, especially on shared repositories or system files.

---

## 📈 Success Metrics

**How to measure workflow success:**

### Team Health
- ✅ Merge conflicts < 10% of PRs
- ✅ PR review time < 24 hours
- ✅ All programmers can work simultaneously without blocking
- ✅ No "waiting for someone" delays

### Code Quality
- ✅ Test coverage maintained or improved
- ✅ Linter scores stable or improving
- ✅ Bug reports decreasing over time
- ✅ Code review finds issues before merge

### Git Hygiene
- ✅ Commit messages descriptive (can understand 6 months later)
- ✅ Branches short-lived (< 1 week average)
- ✅ Clean repository (< 10 active branches)
- ✅ No force pushes to main

### Knowledge Sharing
- ✅ PR discussions help team learn
- ✅ Git history documents decisions
- ✅ New team members can onboard via PR history
- ✅ Everyone understands the workflow

---

## 📝 Real Workflow Example

**Scenario:** Adding a user authentication feature

### Complete Flow

**Day 1: Start**
```bash
# 1. Create feature branch
git checkout main
git pull origin main
git checkout -b COM2-add-authentication

# 2. Implement basic login
vim src/auth/login.py
vim src/auth/jwt_utils.py

# 3. Commit
git add src/auth/
git commit -m "feat: add JWT login implementation"

# 4. Push to remote
git push -u origin COM2-add-authentication
```

**Day 2: Continue**
```bash
# 5. Add tests
vim tests/test_login.py

# 6. Commit
git add tests/
git commit -m "test: add login endpoint tests"

# 7. Sync with main (good practice)
git fetch origin main
git merge origin/main
# No conflicts

# 8. Push
git push origin COM2-add-authentication
```

**Day 3: Complete**
```bash
# 9. Add documentation
vim docs/API_AUTHENTICATION.md

# 10. Commit
git add docs/
git commit -m "docs: document authentication API"

# 11. Final sync
git fetch origin main
git merge origin/main

# 12. Push
git push origin COM2-add-authentication

# 13. Run pre-merge checklist
pytest tests/
pylint src/auth/
black src/auth/ --check

# 14. Create Pull Request
# Go to GitHub/GitLab
# Title: "Add JWT authentication system"
# Description: [detailed PR template filled out]
```

**Day 4: Review and Merge**
```bash
# 15. Address review comments
vim src/auth/login.py  # Fix requested changes
git add src/auth/login.py
git commit -m "refactor: improve error handling per review feedback"
git push origin COM2-add-authentication

# 16. After approval, merge (via web UI or CLI)
git checkout main
git merge COM2-add-authentication
git push origin main

# 17. Cleanup
git branch -d COM2-add-authentication
git push origin --delete COM2-add-authentication
```

**Result:**
- ✅ Feature implemented in 3 days
- ✅ 4 clear commits with good messages
- ✅ Tests and documentation included
- ✅ Code reviewed and approved
- ✅ Main branch stayed stable throughout
- ✅ Clean git history

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

**Avoid common mistakes:**
- ❌ Never work directly on main
- ❌ Never force push to shared branches
- ❌ Don't let branches get stale (sync often)
- ❌ Don't ignore merge conflicts
- ❌ Don't write vague commit messages

**Measure success:**
- Few merge conflicts
- Fast PR reviews
- Good code quality
- Clean git history
- Happy team

---

**Document Purpose**: Universal template for multi-programmer git workflows  
**Target Audience**: 2-12 programmer teams, open source, educational projects  
**Adapt**: Customize branch names, directories, commands for your stack  
**Questions**: Refer to [Git documentation](https://git-scm.com/doc) or ask your team lead

**Version**: 1.1 (2026-01-18)  
**License**: CC0 1.0 Universal (Public Domain) - Use freely!  
**Changelog**: v1.1 added AI workflows, verification commands, common mistakes, real example
