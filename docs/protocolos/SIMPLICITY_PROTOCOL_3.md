# Simplicity 3 Protocol - Solo Developer in Production

**Author**: Josué Amaral
**Creation Date**: December 02, 2025
**Version**: 3.1
**Last Update**: December 09, 2025
**Objective**: Hybrid methodology for **solo developers** with application in **production**

---

## 🎯 Why Does Simplicity 3 Exist?

### Project Context
- 👤 **Solo Developer**: You program alone (without a team)
- 🚀 **Production**: Application has real users depending on it
- ⚠️ **Critical**: Bugs affect users, downtime has impact
- 📈 **Evolutive**: Long-term project, not a prototype

### Why NOT Simplicity 1?
❌ **Simplicity 1** is **insufficient for production**:
- ❌ No security checklist → Vulnerabilities can go to production
- ❌ No CI/CD automation → Manual validation = human errors
- ❌ No rollback plan → If it breaks in production, you're debugging alone
- ❌ No profiling → Performance degrades without you noticing
- ❌ Basic documentation → You forget complex decisions after 3 months

**Real Risk**: Simple application today = giant technical debt in 6 months.

### Why NOT Simplicity 2?
❌ **Simplicity 2** has **team overhead** unnecessary for a solo developer:
- ❌ **Peer Code Review** (Step 9.5) → You have no peers
- ❌ **Formal Sprint Retrospectives** (Step 13.5) → Overkill for one person
- ❌ **Formal ADRs** (Step 11.5) → Can be simplified to decision notes
- ❌ **Accessibility WCAG** (Step 8.5) → Only if the app is public/accessible
- ❌ **API Documentation Sphinx** (Step 6.6) → Docstrings are sufficient

**Real Problem**: Bureaucracy consumes development time without real gain for a solo developer.

### ✅ Simplicity 3 - Hybrid Solution

**Philosophy**: **Production security and automation** WITHOUT team overhead.

**Formula**:
```
Simplicity 3 = Simplicity 1 Base (13 steps)
                 + 3 MANDATORY production steps (Security, CI/CD, Rollback)
                 + 3 pragmatic OPTIONAL steps (Matrix, Profiling, ADR Notes)
                 = 16-19 total steps
```

**Additional MANDATORY Steps** (vs Simplicity 1):
1. ⭐ **Step 6.5: OWASP Security Checklist** - CRITICAL for production
2. ⭐ **Step 10.6: CI/CD Quality Gates** - Essential automation
3. ⭐ **Step 12.5: Rollback Plans** - Deployment safety

**Adapted OPTIONAL Steps** (when it makes sense):
4. 📊 **Step 2.5: Decision Matrix** - When you have 10+ tasks to prioritize
5. ⚡ **Step 10.5: Profiling** - For slow features (>1s)
6. 📝 **Step 11.5: Decision Notes** - Simplified ADR (not formal)

**Removed from Simplicity 2** (don't make sense for solo dev):
- ❌ Step 9.5: Peer Code Review
- ❌ Step 13.5: Formal Sprint Retrospectives
- ❌ Step 8.5: Accessibility WCAG (unless app is public)
- ❌ Step 6.7: Formal API Documentation (docstrings are sufficient)

---

## 📊 Protocol Comparison

| Aspect | Simplicity 1 | Simplicity 3 | Simplicity 2 |
|---------|----------------|----------------|----------------|
| **Steps** | 13 mandatory | 16 oblig + 3 opt | 13 oblig + 10 opt |
| **Scenario** | Prototypes/internal | **Solo in production** | Enterprise teams |
| **Security** | ❌ No | ✅ OWASP mandatory | ✅ OWASP mandatory |
| **CI/CD** | ❌ No | ✅ Mandatory | ✅ Mandatory |
| **Rollback** | ❌ No | ✅ Mandatory | ✅ Mandatory |
| **Code Review** | ❌ No | ❌ Solo | ✅ Peers |
| **Retrospectives** | ❌ No | ❌ Solo | ✅ Team |
| **Overhead** | Low | **Medium** | High |
| **Production** | ❌ Not recommended | ✅ **IDEAL** | ✅ Yes |
| **Time/Task** | ~2-3h | ~3-4h | ~4-6h |

---

## 🎯 When to Use Simplicity 3?

### ✅ Use Simplicity 3 IF:
- ✅ You program **alone** (solo developer)
- ✅ Application is or will go to **production**
- ✅ You have **real users** depending on it (not a prototype)
- ✅ Bugs have **impact** (downtime, data loss)
- ✅ It's a **long-term project** (>6 months)
- ✅ You need **security** (user data, LGPD/GDPR)
- ✅ You want **automation** (CI/CD to not rely on memory)

### ❌ DO NOT use Simplicity 3 IF:
- ❌ Disposable prototype/POC → Use **Simplicity 1**
- ❌ Single-use script → Use **Simplicity 1**
- ❌ Team of 2+ people → Use **Simplicity 2** (has code review)
- ❌ Non-critical internal app → Use **Simplicity 1**
- ❌ Learning/experimenting → Use **Simplicity 1**

---

**Changelog v3.1** (09/12/2025):
- ✅ **[STEP 3]** Added recommendation for AI to provide suggestions and guesses for questions
- ✅ Recommended format: "❓ Question + 💡 AI Suggestion + Options A/B/C"
- ✅ Rationale: Speeds up decisions, reduces cognitive load, maintains consistency with existing code
- ✅ Classification: **OPTIONAL but HIGHLY RECOMMENDED**

**Changelog v3.0** (02/12/2025):
- ✅ **[HYBRID]** Created Simplicity 3 Protocol for solo developer in production
- ✅ Base: Simplicity 1 (13 steps) + 3 mandatory production steps
- ✅ **NEW MANDATORY**:
  - Step 6.5: OWASP Security Checklist (⭐ HIGH PRIORITY)
  - Step 10.6: CI/CD Quality Gates (⭐ HIGH PRIORITY)
  - Step 12.5: Rollback Plans (⭐ HIGH PRIORITY)
- ✅ **PRAGMATIC OPTIONAL**:
  - Step 2.5: Decision Matrix (when 10+ tasks)
  - Step 10.5: Profiling and Optimization (slow features)
  - Step 11.5: Decision Notes (simplified ADR)
- ✅ **REMOVED** (don't make sense for solo dev):
  - ❌ Peer Code Review (no peers)
  - ❌ Formal Sprint Retrospectives (overkill solo)
  - ❌ Accessibility WCAG (unless public)
  - ❌ Formal API Documentation (docstrings sufficient)
- ✅ Detailed Rationale: Why not Simplicity 1 or 2
- ✅ Comparative table of the 3 protocols
- ✅ Total: 16 mandatory + 3 optional = 16-19 steps

**Changelog v1.8** (02/12/2025):
- ✅ **[REORGANIZATION]** Code Review integrated into CLI and GUI steps
- ✅ Step 7: Verify CLI Implementation (includes 9 quality criteria)
- ✅ Step 8: Verify GUI Implementation (includes 9 quality criteria)
- ✅ Step 9: Verify Integration with Main Program (kept as separate step)
- ✅ 9 Criteria: Omission, Ambiguity, Incorrect Fact, Redundancy, Inconsistency, Lack of Integration, Lower Cohesion, Higher Coupling, Extraneous Information
- ✅ Review integrated into CLI/GUI verification process
- ✅ Total steps: 12 → 13 (integration verification added after GUI)

**Changelog v1.7** (02/12/2025):
- ✅ **[CRITICAL]** Added Step 8.5: Code Review (BEFORE tests)
- ✅ 9 Quality Criteria: Omission, Ambiguity, Incorrect Fact, Redundancy, Inconsistency, Lack of Integration, Lower Cohesion, Higher Coupling, Extraneous Information
- ✅ Complete review checklist (36 verification items)
- ✅ Recommended tools (pylint, vulture, radon, black, isort)
- ✅ Detailed CLI and GUI review process
- ✅ Practical examples of problems and corrections
- ✅ Integration with Step 9 (test after review)
- ✅ Total steps: 12 → 13 (8.5 added between 8 and 9)

**Changelog v1.6**:
- ✅ **[ADVANCED]** Added Step 9.2: Tests in Threads/Processes with Monitoring
- ✅ Test execution in separate process (`multiprocessing.Process`)
- ✅ Real-time logging via `Queue` (progress of each test)
- ✅ Manual cancellation at any time (graceful Ctrl+C)
- ✅ Global + individual timeout (double protection)
- ✅ Real-time statistics (passed/failed/elapsed)
- ✅ Full implementation of `test_runner_monitored.py` (~150 lines)
- ✅ Additional optional checklist (6 items)

**Changelog v1.5**:
- ✅ **[CRITICAL]** Added Step 9.1: Security in Tests
- ✅ 7 mandatory solutions to prevent infinite loops and timeouts
- ✅ Mandatory maximum timeout (30s per test)
- ✅ Mandatory headless environment for GUI tests (QT_QPA_PLATFORM=offscreen)
- ✅ Mandatory dry-run before executing tests (syntax + import + collect)
- ✅ Security checklist with 6 mandatory items
- ✅ Golden rules and safe commands documented
- ✅ Lessons learned from Task Example (infinite loop >1h)

**Changelog v1.4**:
- ✅ Reorganized final order: Implement → Integrate GUI → CLI → Test → Organize → Document → Commit
- ✅ Tests moved to AFTER integration verifications (test integrated system)
- ✅ Organize root folder moved to BEFORE documentation (document clean state)
- ✅ Logic: Integrate → Test integration → Clean repository → Document final state

**Changelog v1.3**:
- ✅ Reorganized step order: GUI and CLI Integration Verification now come BEFORE Documentation
- ✅ New order: Tests → GUI Integration → CLI → Documentation → Organize → Commit
- ✅ Logic: Verify integration before documenting ensures documentation reflects the real state

**Changelog v1.2**:
- ✅ Added Step 8: Verify integration with main program
- ✅ Added Step 9: Verify CLI implementation with parameter passing
- ✅ Total steps: 10 → 12

---

## 🎯 Core Philosophy

> "There will always be complex tasks to do, but also those that are more difficult and those that are easier. **I want you to always start with the easiest ones**."

**Principle**: From simple to complex, incremental, professional, and complete.

**NEW v3.0**: + **Production security and automation** without team overhead.

---

## ⚠️ Golden Rule: Absolute Priority for Workspace Errors

> **CRITICAL FOR AIs**: Before implementing new features or continuing with tasks, **all workspace errors must be fixed BY YOU (AI)**.

### 🤖 This Rule is For AI Assistants

**If you are an AI (Cursor, GitHub Copilot, etc.):**
- ✅ **YOU MUST** fix all existing errors BEFORE implementing new features
- ✅ **YOU MUST** resolve issues proactively, not wait for humans to fix them
- ✅ **YOU MUST** treat error correction as the highest priority
- ✅ **YOU MUST** clean the workspace before adding new code

**This rule does NOT mean:**
- ❌ That human developers must stop implementing when errors exist
- ❌ That the project cannot advance while errors are present
- ❌ That humans need to manually fix the errors

### 🚨 Types of Errors That Block Development

Consider the existence of errors in the workspace (visible in the IDE's "Problems" tab) as **undesirable and blocking**. If any of the following types of errors occur, **fixing them is an absolute priority** before continuing:

1. **❌ Syntax Issues**
   - Code parsing errors
   - Unclosed parentheses, braces, or brackets
   - Incorrect indentation (Python)
   - Missing semicolons (JavaScript, C, Java)

2. **❌ Code Inconsistencies**
   - Variables declared but not used
   - Unused or missing imports
   - Dead code (unreachable code)
   - Type mismatches (TypeScript, Python with type hints)

3. **❌ Unexpected Omissions**
   - Functions declared but not implemented
   - Missing required parameters
   - Missing return statements when expected
   - Missing mandatory documentation

4. **❌ Incorrect Facts**
   - References to non-existent variables
   - Function calls with wrong number of arguments
   - Access to non-existent properties
   - Imports of non-existent modules

5. **❌ Ambiguities**
   - Type checking warnings
   - Possible null/undefined references
   - Variable shadowing
   - Dangerous implicit type conversions

6. **❌ Missing Files**
   - Dependencies not installed
   - Imported modules not found
   - Missing configuration files
   - Referenced but non-existent assets

7. **❌ Execution Failures**
   - Build failures
   - Compilation errors
   - Failing tests
   - Linter errors (when configured)

### ✅ When You Can Continue

**ONLY** continue with development of new features when:

- ✅ **Zero errors** in the workspace "Problems" tab
- ✅ **All builds** complete successfully
- ✅ **All tests** pass (if they already exist)
- ✅ **Linter/formatter** doesn't report critical errors
- ✅ **Type checker** doesn't report errors (if applicable)

### 📋 Checklist Before Each Task

```markdown
Before starting any new task:

[ ] Check IDE "Problems" tab (0 errors)
[ ] Run project build (success)
[ ] Run existing tests (all passing)
[ ] Run linter/formatter (no critical errors)
[ ] Verify imports and dependencies (all resolved)
[ ] Confirm code is in clean state (committable)
```

### ⏱️ Estimated Time for Fixing

- **Syntax Errors**: ~2-5 minutes per error
- **Imports/Dependencies**: ~5-10 minutes
- **Type Errors**: ~5-15 minutes per error
- **Failing Tests**: ~10-30 minutes (depends on complexity)

**Rule of Thumb**: If you have >10 errors in the workspace, **dedicate 1-2 hours** to clean everything before proceeding.

### 🎯 Rationale

**Why is this rule critical?**

1. **Cascade Prevention**: One uncorrected error can generate 10 new errors
2. **Code Quality**: Code with errors = immediate technical debt
3. **Reliability**: New features on top of broken code = guaranteed bugs
4. **Productivity**: Fixing old + new errors is more time-consuming than fixing only old ones
5. **Professionalism**: Clean, error-free code is a minimum requirement

**Message for AIs**: 
> "Until the errors are resolved BY YOU (AI), tasks and features cannot continue being implemented BY YOU (AI). Fix the errors first, then continue with implementation."

---

## 🔍 Binary Search for Bug Localization

> **IMPORTANT FOR AIs**: When dealing with error correction and bug elimination, remember that you can use **binary search** to locate defects efficiently.

### 🎯 Core Concept

Binary search is a powerful technique that reduces the search space by half with each iteration, allowing you to locate defects in **O(log N) steps**, where N is the number of lines, commands, or instructions in the algorithm.

**Practical Example**: 
- If an error is on line 48 of a file with 512 lines
- Linear search: up to 512 checks
- Binary search: only **9 checks** (log₂(512) = 9)

### 📋 Binary Search Debugging Methodology

#### **1️⃣ Initial Step: Divide Code in Half**

Starting with a file of N lines where an error exists:
1. Comment out half of the code (e.g., lines 257-512)
2. Execute/test the remaining half (lines 1-256)
3. Check if the error persists

**Decision**:
- ✅ **Error persists**: The bug is in the active half (1-256)
- ❌ **Error disappears**: The bug is in the commented half (257-512)

#### **2️⃣ Recursion: Keep Dividing**

Once you've identified the half with the problem, repeat the process:

**Iteration 2** (error in 1-256):
- Comment out lines 129-256
- Test lines 1-128
- Identify which quarter contains the bug

**Iteration 3** (error in 1-128):
- Comment out lines 65-128
- Test lines 1-64
- Identify which eighth contains the bug

**Continue until** you locate exactly the problematic line/block.

#### **3️⃣ Complete Example: 512 Lines → Line 48**

```
Iteration 1: [1-512]   → Test [1-256]   ✅ Error present
Iteration 2: [1-256]   → Test [1-128]   ✅ Error present  
Iteration 3: [1-128]   → Test [1-64]    ✅ Error present
Iteration 4: [1-64]    → Test [1-32]    ❌ Error absent → Bug in [33-64]
Iteration 5: [33-64]   → Test [33-48]   ✅ Error present
Iteration 6: [33-48]   → Test [33-40]   ✅ Error present
Iteration 7: [41-48]   → Test [41-44]   ✅ Error present
Iteration 8: [45-48]   → Test [45-46]   ✅ Error present
Iteration 9: [47-48]   → Test [line 47]  ❌ Error absent → ✅ Bug on line 48!
```

**Result**: 9 iterations to find the bug in 512 lines (vs. up to 512 linear attempts).

### 🛠️ Implementation Techniques

#### **A) Temporary Comments**
```python
# BINARY SEARCH - Iteration 1: Testing [1-256]
# Lines 257-512 temporarily disabled
# def suspicious_function():  
#     potentially_buggy_code()
#     more_code()
```

#### **B) Debug Flags**
```python
DEBUG_BINARY_SEARCH = True
RANGE_START = 1
RANGE_END = 256

if DEBUG_BINARY_SEARCH and not (RANGE_START <= current_line <= RANGE_END):
    return  # Skip execution outside test range
```

#### **C) Git Bisect** (for bugs introduced in commits)
```bash
# Use git bisect to find the commit that introduced the bug
git bisect start
git bisect bad HEAD              # Current commit has bug
git bisect good v1.0.0           # Commit v1.0.0 didn't have bug
# Git automatically performs binary search on commits
```

#### **D) Partitioned Unit Tests**
```python
# Split test suite in half
pytest tests/test_module_part1.py  # First half
pytest tests/test_module_part2.py  # Second half
# Identify which half contains failing test
```

### 🎨 Creative Applications of Binary Search

Binary search is not limited to lines of code. It can be applied to:

1. **📦 Dependencies/Imports**:
   - Comment out half of the imports
   - Identify which import causes conflict/error
   
2. **🔧 Configuration Parameters**:
   - Disable half of the configurations
   - Find problematic configuration

3. **🗃️ Input Data**:
   - Process half of the dataset
   - Identify which subset causes error

4. **⚙️ Features/Functionality**:
   - Disable half of the features
   - Locate feature causing regression

5. **🧩 Modules/Components**:
   - Disable half of the modules
   - Find module with bug

6. **📅 Version History** (Git Bisect):
   - Test version in middle of history
   - Find commit that introduced bug

7. **🔄 Loop Iterations**:
   - Execute half of the iterations
   - Identify in which iteration error occurs

### ✅ Binary Search Debugging Checklist

```markdown
[ ] 1. Confirm error is consistently reproducible
[ ] 2. Identify total scope (N lines/modules/commits)
[ ] 3. Calculate required iterations: log₂(N)
[ ] 4. Create backup or test branch
[ ] 5. Iteration 1: Comment/disable upper/lower half
[ ] 6. Run test and check if error persists
[ ] 7. Record result and reduce scope by half
[ ] 8. Repeat until isolating exact line/block/commit
[ ] 9. Analyze isolated code to understand root cause
[ ] 10. Apply fix and validate with tests
[ ] 11. Remove debug code/temporary comments
```

### 🎯 When to Use Binary Search for Debugging

**✅ Use when:**
- Error is reproducible but cause is not obvious
- Large codebase (>100 lines)
- Suspect bug is in specific but broad region
- Error appeared after large changes (multiple commits)
- Test fails but there's no clear indication of problem
- Performance degraded but don't know which function is responsible

**❌ Don't use when:**
- Error is sporadic/non-reproducible (race condition, timing issue)
- Stack trace already points to exact line of problem
- Code is very small (<50 lines)
- Bug is obvious after quick code review

### ⏱️ Binary Search Efficiency

| Size (N) | Linear Search | Binary Search | Gain |
|----------|--------------|---------------|------|
| 32 lines  | up to 32 steps | 5 steps | 6.4x faster |
| 128 lines | up to 128 steps | 7 steps | 18.3x faster |
| 512 lines | up to 512 steps | 9 steps | 56.9x faster |
| 1024 lines | up to 1024 steps | 10 steps | 102.4x faster |
| 4096 lines | up to 4096 steps | 12 steps | 341.3x faster |

### 💡 Practical Tips

1. **Document the Process**: Record each iteration and result
2. **Use Version Control**: Create branches for each test
3. **Automate When Possible**: Scripts to comment/uncomment blocks
4. **Combine with Logs**: Add prints to confirm block execution
5. **Test Independently**: Ensure the test is deterministic
6. **Validate Before and After**: Confirm bug exists before and is fixed after

### 🚀 Rationale

**Why is binary search powerful for debugging?**

1. **⚡ Algorithmic Efficiency**: O(log N) vs O(N) - exponential time savings
2. **🎯 Precise Isolation**: Reduces uncertainty systematically
3. **🧠 Lower Cognitive Load**: Simple decisions (error present: yes/no)
4. **📊 Predictability**: Know exactly how many steps will be needed
5. **🔄 Universal Applicability**: Works for code, data, configurations, history
6. **✅ Success Guarantee**: If the bug is reproducible, binary search always finds it

**Message for AIs**:
> "Creativity in using binary search has no limits. Always consider whether a debugging problem can be reduced to a binary search - you'll save time and find bugs faster."

---

## 🧠 Associative Memory Factor

> **IMPORTANT FOR AIs**: During error investigation and correction, apply the **Associative Memory Factor** to learn from past patterns and accelerate future diagnostics.

### 🎯 What is Associative Memory?

**Associative Memory** is AI's ability to:
- 🧠 **Recognize patterns** recurring in errors and defects
- 🔗 **Associate causes and effects** in different contexts
- 📈 **Generalize solutions** from specific cases
- 📉 **Deduce problems** from general to specific (top-down)
- 📊 **Induce rules** from specific to general (bottom-up)

### 🐍 Connection with Python Traceback

Traceback presents errors in **top-down** structure:
```
main.py (ROOT/Orchestrator)
  ↓
processor.py (BRANCH/Coordinator)
  ↓
validator.py (LEAF/Executor) ← Error here!
```

**Associative Insight**:
- Errors in **leaves** → violated preconditions
- Errors in **branches** → incorrect coordination logic
- Errors in **root** → problematic integration

### 🔬 Complementary Approaches

**Deductive (General → Specific)**:
- Apply known general rules to diagnose
- Ex: "AttributeError usually indicates uninitialized object"

**Inductive (Specific → General)**:
- Observe repeated cases to create general rule
- Ex: "70% of IndexError are from incorrect index manipulation"

**Neuro-Symbolic (Combination)**:
- Unites deduction (symbolic AI) with induction (neural AI)
- Learns continuously while applying rules

### 🐛 Defect Taxonomy

Five categories of highly undesirable defects:

1. **Incorrect Fact**: Wrong or outdated information
2. **Extraneous Information**: Code/comments that don't belong to context
3. **Ambiguity**: Code with multiple possible interpretations
4. **Inconsistency**: Violation of established patterns
5. **Omission**: Missing code or logic (validations, error handling)

### 🔄 Error Patterns

**Input-Independent Errors**:
- Always occur, regardless of data
- Problem in **logic**, not in **data**

**Specific Scope Errors**:
- One bug, multiple symptoms in different parts
- Look for **shared dependency**

**Common Import Errors**:
- Multiple modules fail because they import buggy code
- Fix once resolves all cases

### 📊 Application in Production (Protocol 3)

For solo developers in production, associative memory is critical:

**Pattern Analysis in Production Logs**:

1. **Occurrence Frequency**
   - [ ] Is error isolated or recurring?
   - [ ] Occurs with specific data or all data?
   - [ ] Did frequency increase recently? (regression)

2. **Correlation with Deploy**
   - [ ] Did error start after specific deploy?
   - [ ] Use git bisect to identify causative commit
   - [ ] Revert suspicious changes and validate

3. **Scope Analysis**
   - [ ] Is error in specific module or multiple?
   - [ ] Do multiple modules import common buggy code?
   - [ ] Does traceback point to leaf, branch, or root?

4. **Personal Knowledge Base**
   - [ ] Has error occurred before? What was the solution?
   - [ ] Is pattern known? Apply standard solution
   - [ ] New pattern? Document thoroughly for future reference

**Proactive Prevention**:
- Maintain personal record of all resolved bugs
- Create regression tests for already fixed errors
- Document project-specific error patterns
- Implement monitoring to detect known patterns

### ✅ Application Checklist

When investigating and fixing errors:

**Analysis Phase**:
- [ ] Examine Traceback from top to bottom (root → leaf)
- [ ] Identify error level (orchestrator/coordinator/executor)
- [ ] Consult knowledge base for similar patterns
- [ ] Apply deduction: general rules → specific hypothesis
- [ ] Search induction: multiple cases → general pattern

**Investigation Phase**:
- [ ] Check if error is input-independent
- [ ] Identify specific scope of problem
- [ ] Look for shared code (common imports)
- [ ] Apply binary search if necessary
- [ ] Use git bisect for regressions

**Correction Phase**:
- [ ] Validate absence of Incorrect Fact
- [ ] Remove Extraneous Information
- [ ] Eliminate Ambiguities
- [ ] Ensure Consistency with project patterns
- [ ] Fix Omissions (validations, error handling)

**Learning Phase**:
- [ ] Add case to personal knowledge base
- [ ] Update general rules if new pattern identified
- [ ] Document solution thoroughly (root cause + solution)
- [ ] Create regression test to prevent recurrence
- [ ] Reinforce associations of confirmed patterns

### 📖 Complete Documentation

For complete details on the Associative Memory Factor, including:
- Detailed top-down investigation methodology
- Neuro-symbolic debugging cycle
- Practical examples of each defect type
- Error pattern knowledge base
- Integration with HDC (Hyperdimensional Computing)

**See**: [en/ASSOCIATIVE_MEMORY_FACTOR.md](ASSOCIATIVE_MEMORY_FACTOR.md)

---

## 🌐 Code Language: Variable Naming and Comments

> **IMPORTANT FOR AIs**: The choice of language for variable names and comments should be defined at the beginning of the project, preferably during the first session of interaction with the programmer.

### 📋 Default Rule

**By default**, when programming with artificial intelligence:
- ✅ **Variable names**: Should be in **English** (recommended for international projects)
- ✅ **Comments**: Should be in **English** (recommended for international projects)
- ✅ **Docstrings**: Should be in **English** (recommended for international projects)

**Note**: For Portuguese-speaking developers working on national projects, **Portuguese is the recommended default**. The AI should adapt based on the programmer's language preference.

**Justification**: Facilitates understanding and maintenance of code for developers, maintaining consistency with project documentation and communication. English is recommended for international projects, while native language (e.g., Portuguese) is recommended for national projects.

### 🤔 Mandatory Question in First Session

**The AI MUST ask the programmer at the first moment (or during the first session)**:

```
❓ Code Language Preferences

To maintain consistency in the project, I need to define the default 
language for variable names and comments in the code:

💡 Suggestion: English (recommended for international projects)
   or Native Language (recommended for national projects)

Options:
A) 🇺🇸 English - Variables and comments in English (RECOMMENDED for international)
B) 🇧🇷 Native Language - Variables and comments in native language (RECOMMENDED for national)
C) 🌍 Mixed - Variables in English, comments in native language
D) ⚙️ Custom - Specify custom preference

What is your preference?
```

### ✅ Available Options

#### Option A: 🇺🇸 English (RECOMMENDED for International Projects)
```python
# ✅ Example in English
def calculate_total_price(items: List[Item]) -> float:
    """
    Calculates the total price of a list of items.
    
    Args:
        items: List of items to be summed
        
    Returns:
        Total price with taxes included
    """
    subtotal_price = sum(item.price for item in items)
    tax_rate = 0.15
    final_price = subtotal_price * (1 + tax_rate)
    return final_price
```

#### Option B: 🇧🇷 Native Language (e.g., Portuguese)
```python
# ✅ Exemplo em Português
def calcular_preco_total(itens: List[Item]) -> float:
    """
    Calcula o preço total de uma lista de itens.
    
    Args:
        itens: Lista de itens a serem somados
        
    Returns:
        Preço total com impostos incluídos
    """
    preco_subtotal = sum(item.preco for item in itens)
    taxa_imposto = 0.15
    preco_final = preco_subtotal * (1 + taxa_imposto)
    return preco_final
```

#### Option C: 🌍 Mixed (Variables in English, Comments in Native Language)
```python
# ✅ Mixed Example
def calculate_total_price(items: List[Item]) -> float:
    """
    Calcula o preço total de uma lista de itens.
    
    Args:
        items: Lista de itens a serem somados
        
    Returns:
        Preço total com impostos incluídos
    """
    subtotal_price = sum(item.price for item in items)
    tax_rate = 0.15  # Taxa de imposto de 15%
    final_price = subtotal_price * (1 + tax_rate)
    return final_price
```

### 📝 Register the Preference

After the programmer's response, the AI should:

1. **Register the preference** in a visible location (e.g., README.md, CONTRIBUTING.md)
2. **Apply consistently** throughout all generated code
3. **Remember the preference** in future sessions of the same project

**Example Registration in README.md**:
```markdown
## 🌐 Code Conventions

- **Code Language**: English
- **Variables**: Names in English (e.g., `active_user`, `calculate_total`)
- **Comments**: In English
- **Documentation**: In English
```

### 🔄 Preference Change

The programmer can request a language change at any time:
- ✅ "Switch to English from now on"
- ✅ "I prefer comments in Portuguese, but variables in English"
- ✅ "Use English only for public APIs"

**The AI should confirm the change** and update the conventions documentation.

### ⚠️ Common Exceptions

Regardless of the language choice, **keep in English**:
- ✅ Library and framework names (e.g., `import pandas`, `from flask import`)
- ✅ Language keywords (e.g., `def`, `class`, `if`, `for`)
- ✅ Public API names (if code is distributed internationally)
- ✅ Technical terms without adequate translation (e.g., `callback`, `payload`, `refactoring`)

### 🎯 Rationale

**Why ask the programmer?**

1. **Project Context**: National vs. international projects have different needs
2. **Team**: Brazilian team may prefer Portuguese; international team needs English
3. **Readability**: Code is read more times than written - should be clear for maintainers
4. **Consistency**: Defining standard at the start avoids confusing language mixing
5. **Professionalism**: Demonstrates attention to detail and respect for developer preferences

**Why English as recommended for international?**

For international/open-source projects:
- ✅ Universal programming language
- ✅ Easier collaboration with developers worldwide
- ✅ Better integration with English documentation and resources
- ✅ Industry standard for libraries and frameworks

**Why Native Language for national projects?**

For national/regional projects (e.g., Portuguese for Brazil/Portugal):
- ✅ Developers read and understand faster
- ✅ Facilitates onboarding of new team members
- ✅ Documentation and code in same language = less mental translation
- ✅ Variables represent business concepts in native language

**When to prefer English?**

- 🌍 International open-source project
- 🌍 Multicultural team
- 🌍 Product aimed at global market
- 🌍 Library/framework for public distribution

---

## 📧 Contact Methods for User Feedback

> **IMPORTANT FOR AIs**: During the first session of interaction with the programmer, the artificial intelligence must ask if the developer would like to include contact methods in the project so that users can provide feedback to those responsible.

### 📋 Context and Purpose

Software projects greatly benefit from direct user feedback. Comments, suggestions, criticisms, complaints, compliments, and opinions are fundamental for the evolution and continuous improvement of the project.

### 🤔 Mandatory Question in the First Session

**The AI MUST ask the programmer at the very first moment (or during the first session)**:

```
❓ Contact Methods for User Feedback

Would you like to include contact methods in the project so users
can send feedback (comments, suggestions, criticisms, complaints,
compliments, and opinions)?

💡 Suggestion: Yes (recommended for projects with end users)

Options:
A) ✅ Yes, include email for feedback (DEFAULT RECOMMENDED)
B) ✅ Yes, include GitHub Issues (for open-source projects)
C) ✅ Yes, include contact form in the application
D) ✅ Yes, include multiple channels (email + issues + form)
E) ❌ No, do not include contact methods

What is your preference?
```

### ✅ Available Options

#### Option A: ✅ Email for Feedback (DEFAULT RECOMMENDED)

**What to include**:
- Dedicated email for feedback
- All types of feedback are welcome:
  - 💬 General comments
  - 💡 Improvement suggestions
  - 🐛 Constructive criticisms
  - 😞 Complaints about problems
  - 🎉 Compliments and recognition
  - 📝 Opinions about features

**Where to document**:
```markdown
## 📧 Feedback and Contact

Your opinion is very important to us! Send your comments, 
suggestions, criticisms, complaints, compliments, and opinions to:

**Email**: feedback@yourproject.com

All feedback is read and considered for future improvements.
```

**Implementation example (README.md)**:
```markdown
## 📮 Feedback

We'd love to hear from you! Send your comments, suggestions, 
criticisms, complaints, compliments, and opinions to:

- **Email**: contact@myproject.com
- **Response**: We typically respond within 48 hours

Your feedback helps us improve continuously!
```

#### Option B: ✅ GitHub Issues

**For open-source projects**:
```markdown
## 🐛 Report Problems or Give Feedback

Use [GitHub Issues](https://github.com/your-user/your-project/issues) to:

- 🐛 Report bugs
- 💡 Suggest new features
- 💬 Share general feedback
- ❓ Ask questions

**Available templates**:
- Bug Report
- Feature Request  
- General Feedback
```

#### Option C: ✅ Contact Form in the Application

**For web/desktop applications**:
- Add "Feedback" or "Contact" section in the interface
- Form with fields:
  - Name (optional)
  - Email (for response)
  - Type: Comment | Suggestion | Criticism | Complaint | Compliment | Opinion
  - Message
- Send via email or save to database

**Implementation example (GUI)**:
```python
# Menu: Help → Send Feedback
class FeedbackDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Send Feedback")
        
        # Feedback type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "💬 Comment",
            "💡 Suggestion",
            "🐛 Criticism/Bug",
            "😞 Complaint",
            "🎉 Compliment",
            "📝 Opinion"
        ])
        
        # Email (optional)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your@email.com (optional)")
        
        # Message
        self.message_text = QTextEdit()
        self.message_text.setPlaceholderText(
            "Share your comments, suggestions, criticisms, "
            "complaints, compliments, or opinions..."
        )
        
        # Send button
        self.send_button = QPushButton("Send Feedback")
        self.send_button.clicked.connect(self.send_feedback)
```

#### Option D: ✅ Multiple Channels

**Combine several options**:
```markdown
## 📞 Get in Touch

We value your feedback! You can contact us through:

### 📧 Email
- **General Feedback**: feedback@project.com
- **Technical Support**: support@project.com
- We respond within 48 hours

### 💬 GitHub Issues
- Report bugs: [Issues](https://github.com/user/project/issues)
- Suggest features: [Discussions](https://github.com/user/project/discussions)

### 🌐 Contact Form
- Access: Menu → Help → Send Feedback
- Or: https://project.com/contact

### 📱 Social Media
- Twitter: [@yourproject](https://twitter.com/yourproject)
- Discord: [Community](https://discord.gg/yourproject)
```

#### Option E: ❌ Do Not Include

**When to choose this option**:
- ⚠️ Personal/internal projects without external users
- ⚠️ Disposable prototypes
- ⚠️ Single-use scripts

**Consequence**: Users will not have a direct channel for feedback, which may limit the project's evolution.

### 📝 Register the Preference

After the programmer's response, the AI should:

1. **Add contact/feedback section** in README.md
2. **Create CONTACT.md file** (if needed) with details
3. **Implement form** (if application with interface)
4. **Document** in CONTRIBUTING.md (for open-source projects)

**Registration example (README.md)**:
```markdown
## 📬 Feedback and Contact

This project values user feedback! 

- **Email**: feedback@project.com
- **Feedback types welcome**: Comments, suggestions, criticisms, 
  complaints, compliments, and opinions
- **Response time**: Within 48 business hours

Your feedback is essential for continuous improvement!
```

### 🎯 Rationale

**Why ask about contact methods?**

1. **Continuous Improvement**: Direct feedback helps identify problems and opportunities
2. **Engagement**: Users who can give feedback feel more connected to the project
3. **Quality**: Criticisms and suggestions improve software quality
4. **Prioritization**: Feedback helps understand what is most important to users
5. **Recognition**: Compliments motivate the development team
6. **Transparency**: Open channel demonstrates commitment to users

**Why Email as default?**

For projects with users:
- ✅ **Universal**: Everyone has email
- ✅ **Simple**: Doesn't require account or additional registration
- ✅ **Direct**: Private and personal communication
- ✅ **Consolidated**: All types of feedback in a single channel
- ✅ **Traceable**: Complete history of communications
- ✅ **Professional**: Formal channel suitable for any type of feedback

**When to prefer other options?**

- 🌍 **GitHub Issues**: Open-source projects (public transparency)
- 🌍 **Form**: Apps with many users (organization and categorization)
- 🌍 **Multiple channels**: Large projects (different audiences, different needs)
- 🌍 **None**: Internal/personal projects without external users

### ⚠️ Important Considerations

**Feedback Management**:
- ✅ Define who will respond to feedback (responsible person)
- ✅ Establish expected response time (SLA)
- ✅ Create process for triage and prioritization
- ✅ Document relevant feedback (issues, backlog)
- ✅ Always thank, even for criticisms

**Privacy**:
- ✅ Inform how contact data will be used
- ✅ Do not share emails without permission
- ✅ GDPR/LGPD compliance if applicable

**Best practices example**:
```markdown
## 📧 Feedback Policy

**We commit to**:
- ✅ Respond to all feedback within 48 business hours
- ✅ Treat all opinions with respect
- ✅ Seriously consider criticisms and suggestions
- ✅ Maintain contact data privacy (GDPR/LGPD)
- ✅ Thank constructive contributions

**You can expect**:
- Personalized response (not automated)
- Updates on implemented suggestions
- Recognition in changelogs (if desired)
```

---

## 📊 Recursive Division of Complex Tasks

> **IMPORTANT**: If the task is very long or complex, and there are time limits or response length limits, the artificial intelligence should divide the task into smaller parts, recursively, until achieving a task that can provide a satisfactory response according to the determined response limit.

### 🔄 Division Strategy (Solo Developer)

**When to Apply** (Simplicity Protocol 3):
- ✅ Task estimated at >4 hours (divide into 2-3 sprints)
- ✅ Critical production feature
- ✅ Very long response (>1000 lines of code)
- ✅ Multiple interdependent functionalities
- ✅ Requires security checklist + CI/CD + rollback plan
- ✅ Risk of timeout or response limit
- ✅ **Solo**: You need to pause and continue later (context)

**How to Divide** (Recursively with Pragmatism):

1. **Level 1 - Deployable Features (3-4 hours each)**:
   ```
   Large Feature: "Real-Time Notifications System"
   ↓ Divide into (solo, production):
   ├── Sprint 1: Basic WebSocket server (4h)
   │   ├── Security: Rate limiting
   │   ├── CI/CD: Connection tests
   │   └── Rollback: Feature flag
   ├── Sprint 2: Client subscription (3h)
   │   ├── Security: Token validation
   │   └── CI/CD: Integration tests
   └── Sprint 3: Notification persistence (3h)
       ├── Security: Data sanitization
       ├── CI/CD: Database tests
       └── Rollback: Database migration
   
   Each sprint → Deployable to production
   Each sprint → Rollback plan if critical
   ```

2. **Level 2 - Testable Tasks (<3 hours)**:
   ```
   Sprint 1: Basic WebSocket server
   ↓ Divide into:
   ├── Task 1.1: Setup WebSocket library (30min)
   │   └── Security: Check vulnerabilities (pip-audit)
   ├── Task 1.2: Connection handler (1h)
   │   └── Security: Auth token validation
   ├── Task 1.3: Rate limiting (1h)
   │   └── Security: Prevent DDoS
   ├── Task 1.4: Tests + CI/CD (1h)
   └── Task 1.5: Deploy + monitoring (30min)
       └── Rollback: Feature flag WEBSOCKET_ENABLED
   ```

3. **Level 3 - Subtasks (<1 hour)** (rarely needed):
   ```
   Task 1.2: Connection handler
   ↓ Divide into (if too complex):
   ├── Subtask 1.2.1: Accept connection (20min)
   ├── Subtask 1.2.2: Validate token (20min)
   └── Subtask 1.2.3: Store connection (20min)
   ```

**Solo Stopping Criteria**:
- ⏱️ Task can be completed in <3 hours
- 📝 Response fits within reasonable limit (<500 lines)
- ✅ Clear and well-defined scope
- 🧪 Can be tested in isolation
- 🔒 Security checklist applicable (10-15min)
- 🤖 CI/CD validates automatically
- 🔄 Simple rollback plan (if critical)
- 💾 **Recoverable context**: If stopped, can continue later

**Solo Division Principles**:
1. **Independence**: Each subtask must be deployable alone
2. **Context**: Each subtask must have self-explanatory context
3. **Incremental Value**: Each subtask must work in production
4. **Testability**: Each subtask must have automated tests
5. **Security**: Each subtask must pass security checklist
6. **Automation**: CI/CD validates everything (you don't forget anything)
7. **Reversibility**: Critical features have rollback (you're alone)

**Practical Solo in Production Example**:
```markdown
❌ BAD - Feature too large (12h):
[ ] Implement complete billing system

✅ GOOD - Divided for solo developer:

Sprint 1 (4h) - Base structure (non-critical):
├── Task 1.1: Invoice model (1h)
│   └── CI/CD: Schema tests
├── Task 1.2: Basic CRUD (2h)
│   ├── Security: Access control
│   └── CI/CD: Unit tests
└── Task 1.3: Documentation + deploy (1h)
    └── Rollback: N/A (doesn't affect users)

Sprint 2 (4h) - Stripe Integration (CRITICAL):
├── Task 2.1: Setup Stripe API (1h)
│   ├── Security: API keys in env vars
│   └── CI/CD: Connection test
├── Task 2.2: Create payment intent (2h)
│   ├── Security: Amount validation, idempotency
│   └── CI/CD: Mock Stripe tests
└── Task 2.3: Deploy + rollback plan (1h)
    └── Rollback: FEATURE_STRIPE_ENABLED=false
    └── Monitoring: Alert if >5% error

Sprint 3 (3h) - Webhooks (CRITICAL):
├── Task 3.1: Webhook receiver (1.5h)
│   ├── Security: Signature validation (OWASP)
│   └── CI/CD: Webhook tests
├── Task 3.2: Event processing (1h)
│   └── Security: Idempotency check
└── Task 3.3: Deploy + monitoring (30min)
    └── Rollback: Disable webhook endpoint

Each Sprint:
- Security checklist (15min)
- Automatic CI/CD (GitHub Actions)
- Rollback plan if critical
- Production deployment
- **You alone can complete it**
```

**When to Divide vs When to Simplify**:

```markdown
If task is too large to divide efficiently:

❌ BAD - Over-dividing:
[ ] Task: Add "Save" button
    ├── Subtask 1: Create button (10min)
    ├── Subtask 2: Add event (10min)
    └── Subtask 3: Test (10min)
→ Division overhead > benefit

✅ GOOD - Atomic task (30min total):
[ ] Task: Add "Save" button with handler

Rule of thumb:
- Task <1h → Don't divide (atomic)
- Task 1-3h → Evaluate (divide if >3 components)
- Task >3h → Always divide
```

**Decision Matrix for Solo** (when there are multiple ways to divide):

| Division | Solo-friendly | Deploy | Rollback | Context | **Score** |
|---------|---------------|--------|----------|---------|-----------|
| **By deployable feature** | 5 | 5 | 5 | 4 | **33** 🟢 |
| By layer (backend/frontend) | 3 | 2 | 2 | 3 | **17** 🟡 |
| By priority (MVP → Nice-to-have) | 5 | 5 | 4 | 5 | **34** 🟢 |

**Why?**: Dividing tasks for solo developers ensures incremental deliveries with security, facilitates resuming context, allows quick rollback (you're alone in emergencies), and keeps code always deployable.

---

## 📋 Protocol Backbone (17 Mandatory Steps)

**Executive Summary** (⭐ = NEW vs Simplicity 1):
1. 📚 Read the documentation
2. ✅ Choose simpler tasks
   - 2.5 📊 [OPTIONAL] Decision Matrix (when 10+ tasks)
3. ❓ Ask questions until 100% clear
4. 🔍 Analyze and study the project
5. 🎯 Do sprints for the simpler tasks
6. 💻 Implement with professional architecture (GoF + GRASP)
   - 6.5 🔒 ⭐ **OWASP Security Checklist** (MANDATORY)
   - 6.6 🎨 **Project Icons** (MANDATORY)
7. ⌨️ Verify CLI Implementation + Code Review (9 criteria)
8. 🖥️ Verify GUI Implementation + Code Review (9 criteria)
9. 🔗 Verify Integration with Main Program
🔟 🧪 Run tests (100% coverage)
   - 10.5 ⚡ [OPTIONAL] Profiling and Optimization (if >1s)
   - 10.6 🤖 ⭐ **CI/CD Quality Gates** (MANDATORY)
1️⃣1️⃣ 🧹 Organize root folder
   - 11.5 📝 [OPTIONAL] Decision Notes (simplified ADR)
1️⃣2️⃣ 📝 Fill documentation
   - 12.5 🔄 ⭐ **Rollback Plans** (MANDATORY)
1️⃣3️⃣ 🚀 Commit and push

**Total**: 14 base + 3 new mandatory ⭐ + 3 optional = **17-20 steps**

### 1️⃣ **Read the Documentation**
- Consult `TASKS.md` (or equivalent file defined by the user) to see pending tasks
- Consult `docs/REQUIREMENTS.md` to understand the project context
- Review previous specifications (`v2.9.X-SPECIFICATIONS.md`)
- Understand dependencies and existing architecture
- Check examples in `tests/files/` when applicable

**📋 About the Task File**:

The `TASKS.md` file is the **default file** for managing project tasks, but you can use any ASCII format file (`.txt`, `.md`, etc.) according to your preference.

**Task File Requirements**:
- ✅ **ASCII format mandatory**: `.md`, `.txt` or similar (readable as plain text)
- ❌ **NOT accepted**: `.docx`, `.pdf`, or binary formats
- 📍 **Location**: Project root or in `docs/` (e.g., `TASKS.md`, `TODO.md`, `requirements.md`)
- 🔄 **Alternative**: If you prefer another name/location, specify at project start

**If no task file exists**:
1. AI should ask the user: "Which file do you use to manage tasks?"
2. If none exists, suggest creating the default `TASKS.md`
3. Confirm file location and name with the user

**Why?**: Avoid rework and ensure coherence with existing code. The task file centralizes project planning and progress.

**📋 About Action Plans**:

In addition to `TASKS.md`, you can create **Action Plans** for tasks requiring detailed step-by-step guidance.

**What are Action Plans?**
- 🎯 **Practical roadmaps** with numbered intermediate steps for complex tasks
- ⚡ **More urgent and detailed** than TASKS.md items
- 🔧 **Applicable to**: Maintenance, Correction, Evolution, Adaptation
- 📋 **Created BEFORE** starting implementation
- 📖 **Consulted always** during development

**Difference between TASKS.md and Action Plans:**
- **TASKS.md**: List of general tasks ("WHAT to do") - e.g., `[ ] Implement OAuth2 authentication`
- **Action Plan**: Detailed execution guide ("HOW to do it") - e.g.:
  ```
  PLAN #01: Implement OAuth2
  ├─ Step 1: Install passport.js library
  ├─ Step 2: Configure Google OAuth strategy
  ├─ Step 3: Create /auth/google routes
  └─ Step 4: Add tests
  ```

**When to use Action Plans:**
- ✅ Complex task with multiple interdependent steps
- ✅ Critical bug requiring step-by-step diagnosis
- ✅ Refactoring affecting multiple modules
- ✅ Technology migration or framework update

**Specifics for Simplicity 3 (Solo Developer in Production):**
- 🔒 **Mandatory security**: Include OWASP analysis for each step touching sensitive code
- 🔙 **Rollback Plan**: Each action plan must include rollback strategy (see Step 12.5)
- ⚡ **Automation-first**: Prioritize steps that can be automated/tested
- 📊 **Production metrics**: Include validation of metrics (performance, availability)

**Organization of Action Plans:**

**Option 1**: Consolidated file `docs/ACTION_PLANS.md`  
**Option 2**: Individual plans directory `docs/plans/`
```
docs/
├── TASKS.md
├── ACTION_PLANS.md [optional - index]
└── plans/
    ├── plan-001-oauth2.md
    ├── plan-002-migration.md
    └── plan-003-refactoring.md
```

**Recommendation**: For solo developer in production with multiple critical tasks, use `docs/plans/` for better organization and traceability.

**Required Fields for an Action Plan:**
1. **📅 Date** (YYYY-MM-DD): Plan creation date
2. **🕐 Time** (HH:MM): Plan creation time
3. **🎯 Main Function**: Main objective of the plan
4. **📋 Desired Requirement**: What needs to be achieved
5. **✅ Expected Result**: Measurable success criteria
6. **📌 Task ID**: Link to Task from TASKS.md (mandatory)

**Template for Simplicity 3 (Solo in Production):**
```markdown
## 🎯 ACTION PLAN #[ID]: [Title]
**📅 Date**: YYYY-MM-DD
**🕐 Time**: HH:MM
**⚡ Priority**: 🔴 Critical | 🟡 High | 🟢 Normal
**🏷️ Type**: Maintenance | Correction | Evolution | Adaptation
**📌 Task ID**: Task #X from TASKS.md
**🎯 Main Function**: [Plan objective]
**📋 Desired Requirement**: [What should be achieved]
**✅ Expected Result**: [Success criteria]
**🔒 Security Impact**: Yes | No
**💰 Production Impact**: Critical | Moderate | Low

### 📝 Context
[Why was this plan created? What impact on production system?]

### 🎯 Final Objective
[What will be achieved? Which metric will validate success?]

### 🔙 Rollback Plan (MANDATORY)
**If something goes wrong during execution:**
- [ ] **Rollback step 1**: [How to undo step 1]
- [ ] **Rollback step 2**: [How to undo step 2]
- [ ] **Affected data**: [How to recover/restore]
- [ ] **Estimated rollback time**: [duration]

### 📋 Intermediate Steps
- [ ] **Step 1**: [Description]
  - **Completion criteria**: [...]
  - **Estimated time**: [...]
  - **Security checklist**: 
    - [ ] Input validation
    - [ ] Output encoding
    - [ ] Authentication/Authorization
  - **Automated tests**: [commands]
  - **Rollback**: [how to revert this step]
  
- [ ] **Step 2**: [Description]
  - **Completion criteria**: [...]
  - **Dependencies**: Step 1
  - **Security checklist**: [...]
  - **Staging validation**: [commands/URLs]
[...]

### 🔒 Security Analysis (OWASP)
- [ ] **A01:2021 – Broken Access Control**: Evaluated
- [ ] **A02:2021 – Cryptographic Failures**: Evaluated
- [ ] **A03:2021 – Injection**: Evaluated
[... other relevant categories ...]

### 📊 Production Metrics Validation
- [ ] **Performance**: Response time < Xms (monitor for 24h)
- [ ] **Availability**: Uptime > 99.9%
- [ ] **Errors**: Error rate < 0.1%
- [ ] **Resources**: CPU/Memory within limits

### ✅ Completion Criteria
- [ ] All steps completed
- [ ] Automated tests passing (100% coverage)
- [ ] OWASP checklist validated
- [ ] Documentation updated
- [ ] Rollback plan tested
- [ ] Staging validation for 24h
- [ ] Production deploy with monitoring
- [ ] Production metrics stable for 48h
```

**Workflow with Action Plans (Solo in Production):**
1. Consult TASKS.md to see pending tasks
2. If complex/critical task → **CREATE Action Plan BEFORE starting**
3. Choose location: `docs/ACTION_PLANS.md` or `docs/plans/plan-[ID]-[name].md`
4. **Security analysis**: Apply OWASP checklist (Step 6.5)
5. **Create Rollback Plan**: Ensure ability to revert (Step 12.5)
6. **BEFORE implementing**: Review and validate entire plan
7. **Execute in staging first**: Validate for minimum 24h
8. Execute step by step, **consulting the plan whenever needed**
9. **Incremental deploy**: One step at a time, with monitoring
10. **Validate metrics**: 48h stability before considering complete
11. Upon completion → mark task in TASKS.md as complete
12. Archive plan in `docs/plans/archive/` with lessons learned

**Why create BEFORE and consult ALWAYS?**
- ✅ **Security First**: OWASP analysis before prevents vulnerabilities
- ✅ **Rollback Ready**: Have rollback strategy from the start
- ✅ **Avoids Downtime**: Early planning identifies risks
- ✅ **Stay on Track**: Consulting during work maintains security focus
- ✅ **Continuous Validation**: Each step has clear success criteria

**Benefits for Solo Developer:**
- ✅ **Security**: Mandatory checklist prevents vulnerabilities
- ✅ **Reliability**: Rollback plan ensures quick recovery
- ✅ **Quality**: Testable steps guarantee functionality
- ✅ **Autonomy**: Complete process documented for yourself
- ✅ **Maintainability**: Detailed history facilitates future fixes

**⚠️ When an Action Plan is MANDATORY in Simplicity 3:**
- 🔒 Changes affecting **authentication, authorization, or sensitive data**
- 💰 Deploy to **production with active users**
- 🗄️ **Database migrations** or schema changes
- 🔄 **Critical dependency updates** (frameworks, security libraries)
- 🐛 **Critical bugs** affecting availability or security

📖 **Complete details on Action Plans**: See README.md in repository, section "Action Plans (ACTION_PLANS.md)"

---

### 2️⃣ **Choose the Simplest Tasks**
- **Golden Rule**: Always start with the **easiest tasks to implement**
- Even in a list of complex tasks, **there are always simpler ones than others**
- Proportionality: balance simplicity vs. impact

**Simplicity Criteria**:
- ✅ Fewer dependencies
- ✅ Well-defined and clear scope
- ✅ Fewer files to modify
- ✅ Lower risk of breaking existing functionalities
- ✅ Can be tested in isolation

**Real Example**:
```
List of remaining complex tasks:
[ ] Complex Feature Example (VERY COMPLEX - 50h)
[ ] Semantic AI Search (COMPLEX - 20h)
[ ] Tooltip preview on hover (SIMPLE - 30min) ✅ START HERE!
```

---

### 2️⃣.5️⃣ **Objective Decision Matrix** [OPTIONAL]

**When to Use**: When you have 10+ tasks and it's not obvious which is simplest.

**What it is**: Scoring system with 5 criteria (0-5 points each):
1. **Technical Simplicity** (code, algorithm, new concepts)
2. **Dependencies** (files to modify, modules affected)
3. **Impact** (user value, frequency of use)
4. **Clarity** (defined requirements, examples)
5. **Risk** (breaking code, reversibility)

**Formula**:
```
Priority = (Simplicity × 2) + Dependencies + (Impact × 1.5) + Clarity + Risk
```

**Interpretation**:
- **30-35 points**: 🟢 IDEAL - Start immediately
- **20-29 points**: 🟡 GOOD
- **10-19 points**: 🟠 MEDIUM
- **0-9 points**: 🔴 COMPLEX - Leave for last

**Quick Example**:

| Task | Simpl | Dep | Imp | Clar | Risc | **Score** | Decision |
|------|-------|-----|-----|------|------|-----------|---------|
| **Tooltip Preview** | 5 | 5 | 3 | 5 | 5 | **33.5** 🟢 | **CHOOSE** |
| **Integrated Editor** | 1 | 2 | 5 | 4 | 2 | **20.5** 🟡 | Later |

**When NOT to use**:
- ❌ Only 1-3 tasks (obvious which is simplest)
- ❌ Urgent bugfix (ignores score)
- ❌ Blocking task (absolute priority)

📘 **Full details**: See `SIMPLICITY_PROTOCOL_2.md` - Step 2.5 (template, examples)

---

### 2️⃣.6️⃣ **Ordinal Task Organization** [RECOMMENDED FOR SOLO]

> **For Solo Developer in Production**: Pragmatic system to maximize parallelization and efficiency.

**When to Use** (Simplicity 3):
- ✅ **Solo** projects with >10 interdependent tasks
- ✅ Need to **switch contexts** (pause and resume)
- ✅ Multiple **feature branches** simultaneously
- ✅ **Asynchronous** work (non-linear)
- ✅ **Production**: Need for incremental deployment

#### 📊 Simplified System for Solo

**Pragmatic Numbering**:
```markdown
## 🔴 MUST HAVE - Sprint v2.1.0

1. 🔴🟢 [ ] Setup CI/CD (0.5h) - Independent
2. 🔴🟢 [ ] Create User model (1h) - Independent
3. 🔴🟡 [ ] Login API (2h) - Depends: #2
4. 🔴🔴 [ ] 2FA (3h) - Depends: #3

**Solo Analysis**:
- Tasks #1 and #2: PARALLEL (can switch freely)
- Tasks #3 and #4: SERIAL (#3 before #4)
- Task #1: Can do anytime (zero dependencies)
```

**Hierarchy for Multiple Contexts**:
```markdown
A. Authentication Feature (Branch: feat/auth)
   A.1. 🔴🟢 [ ] User model (1h)
   A.2. 🔴🟡 [ ] JWT Login (2h) - Depends: A.1
   A.3. 🔴🔴 [ ] 2FA (3h) - Depends: A.2

B. API Feature (Branch: feat/api)
   B.1. 🔴🟢 [ ] Basic endpoints (1.5h)
   B.2. 🔴🟡 [ ] Validation (1h) - Depends: B.1

**Solo Strategy**:
1. Monday: A.1 (1h morning)
2. Monday: B.1 (1.5h afternoon) ← Context switch
3. Tuesday: A.2 (2h morning)
4. Tuesday: B.2 (1h afternoon) ← Parallel
5. Wednesday: A.3 (3h) ← Back to auth
```

#### ⚡ Benefits for Solo in Production

**Productivity**:
- ✅ **Switch contexts** when blocked/tired
- ✅ **Incremental deployment**: Merge A.1, A.2 without waiting for A.3
- ✅ **Granular rollback**: Revert A.3 without affecting A.1, A.2

**Mental Organization**:
- ✅ **Resume work**: Ordinal prefix shows where you stopped
- ✅ **Clear prioritization**: Know which tasks to do first
- ✅ **Pause/Resume**: Branch per group facilitates context

**Real Example** (Solo Developer):
```markdown
Friday 5pm: Need to stop in the middle of A.2

TASKS.md:
A. Authentication Feature (Branch: feat/auth)
   ✅ A.1. User model (DONE - commit abc123)
   🟡 A.2. JWT Login (IN PROGRESS - 60% complete)
      → Next: Implement refresh token
   ⚪ A.3. 2FA (BLOCKED - waits for A.2)

Monday 9am: Resume easily by looking at TASKS.md
→ Know exactly where to continue (A.2, refresh token)
→ Know that A.3 is blocked until finishing A.2
```

#### 🔙 Rollback Plans and Ordinal Organization

For solo production, combine with Step 12.5 (Rollback Plans):

```markdown
A.2. JWT Login (2h) - CRITICAL for production

Rollback Plan:
- IF error rate > 5%: Revert ONLY A.2
- Keep A.1 (model) in production
- Feature flag: ENABLE_JWT_LOGIN=false
- Fallback: Basic login (previous version)

Ordinal prefix allows GRANULAR rollback:
✅ Revert A.2 without touching A.1
❌ Without prefix: Revert entire "authentication feature"
```

#### 🤖 AI as Solo Assistant

AI can suggest ordinal organization:

```markdown
💡 **AI Suggestion**: I identified 8 tasks in your backlog

Dependency analysis:
- 3 INDEPENDENT tasks (1, 2, 5)
- 2 PARALLEL groups (A.x, B.x)
- 1 CROSS dependency (C waits for A.3)

Recommendation to maximize productivity:
1. This week: Groups A and B (parallel)
   - Monday: A.1 (morning) + B.1 (afternoon)
   - Tuesday: A.2 (morning) + B.2 (afternoon)
2. Next week: A.3 → C.1 (serial)

Prefer this organization or want adjustments?
```

#### ✅ When NOT to Use (Solo)

- ❌ Project <5 tasks (unnecessary overhead)
- ❌ 1-day sprint (linear is sufficient)
- ❌ All tasks SERIAL (no parallelization possible)

📘 **Complete Documentation**: See `ORDINAL_TASK_ORGANIZATION.md` for:
- Deep hierarchy for complex projects
- Right→left reading (C.B.1.D.1)
- Decision flowchart
- Complete examples

---

### 3️⃣ **Ask Questions and More Questions to the Developer**
- **CRITICAL**: Never assume or guess requirements
- Ask **all necessary questions** until **100% of doubts are clarified**
- Validate understanding before starting implementation
- 🤖 **[NEW v3.1]** The AI **CAN and IS HIGHLY RECOMMENDED** to provide **suggestions and guesses** for the answer to each question (optional, but encouraged)

**Recommended Question Format with Suggestions**:
```
❓ Question: "How should it behave when [scenario X]?"
💡 AI Suggestion: "Based on existing code, I suggest [option A] because [reason Y]."
Options: A) [option A] | B) [option B] | C) [option C]
```

**Why AI Suggestions Are Important**:
- ✅ Speeds up decisions when the developer is undecided
- ✅ AI has context of existing code and can suggest consistent patterns
- ✅ Reduces developer's cognitive load (they only validate, don't create from scratch)
- ✅ Maintains quality: AI suggests based on already implemented best practices

**Question Categories**:
1. **Functional Requirements**:
   - "How should it behave when [scenario X]?"
   - "What happens if the user [action Y]?"
   - "What is the priority between [option A] and [option B]?"

2. **Technical Requirements**:
   - "Should I use [library X] or build from scratch?"
   - "What is the expected output format?"
   - "Are there any performance restrictions?"

3. **Edge Cases**:
   - "What if the file is empty?"
   - "What if there are special characters?"
   - "How to handle None/null values?"

4. **Integration**:
   - "Does it need to integrate with [existing module]?"
   - "Should I maintain compatibility with [previous version]?"
   - "Where to save the results?"

5. **Understanding Validation**:
   - "I understand you want [X]. Is that correct?"
   - "My proposed solution is [Y]. Does it make sense?"
   - "Can I start or did I forget something?"

**Real Example (Task Example)**:
```
❓ "Get first N words (how many? 3-5?)?"
✅ Answer: "Default can be 30 characters"

❓ "Convert to camelCase removing accents?"
✅ Answer: "Yes, accents should be removed"

❓ "Name conflicts: how to resolve?"
✅ Answer: "If they have the same parent key, don't touch. Shorter line wins."
```

**Why?**: Saves time, prevents rework, ensures the solution meets exactly what was requested.

#### 🌐 **Online Research: When AI Has Many Doubts or Difficulties**

> **IMPORTANT FOR AIs**: If you have **many doubts** about how to solve a particular problem, or have **significant difficulties** solving that same problem, **remember that you can perform online research**.

**When to Perform Online Research**:
- ✅ When there are complex technical doubts that you cannot resolve alone
- ✅ When you encounter a critical problem that has no obvious solution in the existing code
- ✅ When you need to understand how to implement something completely new
- ✅ When there is an error or bug that is difficult to diagnose
- ✅ When you need practical implementation examples

**Where to Search** (in order of priority):
1. **📚 Official GitHub Documentation of Related Projects**:
   - Similar repositories or those that solve similar problems
   - Issues and Pull Requests discussing similar problems
   - Wiki and technical documentation of related open source projects

2. **📖 Online Documentation Platforms**:
   - Official documentation of libraries and frameworks used in the project
   - Specialized tutorials and technical guides
   - Technical blogs and articles from experienced developers

3. **💬 Question and Answer Platforms**:
   - **StackOverflow**: Main platform for programming questions
   - **GitHub Discussions**: For project-specific questions
   - Other technical communities relevant to the project's technology

**Why Online Research Is Important**:
- ✅ **Saves time**: Complex problems may already have documented solutions
- ✅ **Best practices**: Learn from implementations already validated by the community
- ✅ **Avoid reinventing the wheel**: Many problems have already been solved by other developers
- ✅ **Reduces errors**: Solutions tested and approved by the community have fewer bugs
- ✅ **Updates**: Discover the most modern and efficient approaches

**Example Flow with Online Research**:
```
1. ❓ I tried to implement [feature X] but encountered [problem Y]
2. 🔍 I searched on GitHub: "similar implementation [feature X]"
3. 📚 I found 3 similar projects that solve this in different ways
4. 💡 I analyzed the examples and identified the most appropriate approach for our context
5. ✅ I implemented based on the best practices found
6. 📝 I documented the solution source for future reference
```

**⚠️ Important**: Always cite the consulted sources in the project documentation for future reference and traceability.

---

### 4️⃣ **Analyze and Study the Project**
- **CRITICAL**: After understanding all doubts, **study the code before implementing**
- Read relevant documentation (README, docs/, comments in code)
- Understand existing architecture and patterns used
- Check dependencies and necessary imports
- Identify reusable functions/classes

**Analysis Checklist**:
1. **Documentation Reading**:
   - `docs/REQUIREMENTS.md` - General project context
   - `docs/SPECIFICATIONS.md` - Specifications of previous versions
   - `README.md` - Overview and usage instructions
   - Docstrings of related modules

2. **Existing Code Analysis**:
   - Find modules similar to what will be implemented
   - Identify design patterns already used (GoF, GRASP)
   - Check naming conventions and structure
   - Locate reusable helper functions

3. **Dependency Mapping**:
   - Which modules need to be imported?
   - Are there name or version conflicts?
   - Which base classes or mixins should be inherited?
   - Where should new files be created?

4. **Compatibility Validation**:
   - Will the solution break existing code?
   - Is it necessary to refactor anything before implementing?
   - Are there tests that need to be updated?
   - Will the public API be maintained?

**Real Example (Task Example - Tutorials)**:
```
✅ Analyzed: Other docks (ComponentA, ComponentB)
✅ Identified: BaseDock pattern with FileInputMixin
✅ Verified: QTreeWidget + QTextBrowser for navigation
✅ Studied: How other modules convert markdown → HTML
✅ Located: Where to add imports in app.py
✅ Confirmed: Menu structure in _build_menu()
→ Result: Implementation in 2h instead of 5h (60% saving)
```

**Why?**: Avoids refactorings, saves time, ensures consistent code with the existing base.

---

### 5️⃣ **Do Sprints for the Simplest Tasks**
- Group 2-4 related tasks into a sprint
- Estimate total time: **maximum 3-4 hours** per sprint
- Maintain focus: **one sprint = one version (e.g., vX.Y.Z)**

**⚠️ Important - Task Division into Subtasks**:
> Tasks should be divided into smaller parts **only if really necessary**, that is:
> - ✅ When there is **higher probability of exceeding the maximum time** (>4h)
> - ✅ When there is **higher possibility the response will be too long** (complex implementation)
> - ❌ **DO NOT divide** if the task is reasonably simple and fits within the time limit
> 
> This decision should be made by the **artificial intelligence responsible for programming** the project, based on the real complexity of the task.

**Sprint Structure**:
```
Sprint vX.Y.Z (Task Example):
├── Task Example: Feature Update (estimated 3h)
│   ├── Subtask 1: Ask questions to the developer (15min)
│   ├── Subtask 2: extract_all_keys_from_obj() (45min)
│   ├── Subtask 3: build_substitution_map_by_value() (45min)
│   ├── Subtask 4: Integration into cli_dedupe() (30min)
│   ├── Subtask 5: Unit tests (60min)
│   └── Subtask 6: Documentation (30min)
└── Total: 3h45min ✅
```

---

### 6️⃣ **Implement from Simple to Complex with Professional Architecture**
- **Within each task**, start with the easiest part
- Build incrementally: helper function → main function → integration
- Test each part before moving on

**Implementation Order**:
1. **Helper functions** (e.g., `extract_all_keys_from_obj()`)
2. **Main functions** (e.g., `build_substitution_map_by_value()`)
3. **Integration** (e.g., update `cli_dedupe()`)
4. **GUI/UX** (if applicable)
5. **Optimizations** (last step)

**Architectural Principles (Mandatory)**:

#### 🔄 **Code Reuse with Modules**
- Create separate modules for each responsibility
- Avoid duplication (DRY - Don't Repeat Yourself)
- Generic functions reusable in multiple contexts

**Example**:
```python
# ✅ GOOD: Reusable module
# src/utils/file_utils.py
def read_file_safe(path: str) -> Optional[str]:
    """Function reused in 10+ places"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return None

# ❌ BAD: Duplicate code in each module
# (repeats try/except 20 times)
```

#### 🌳 **Import Tree Analogy**

**Concept**: A program's import structure can be visualized as a tree, where each module imports other modules, forming a dependency hierarchy.

**Unlimited Depth**: This tree can reach **any level or height** depending on program complexity:
- **Simple Programs**: Shallow tree (2-3 levels)
  ```
  main.py
  └── utils.py
      └── helpers.py
  ```

- **Medium Programs**: Moderate tree (4-6 levels)
  ```
  app.py
  ├── controllers/
  │   └── user_controller.py
  │       └── services/
  │           └── user_service.py
  │               └── models/
  │                   └── user.py
  └── config.py
  ```

- **Complex Programs**: Deep tree (7+ levels)
  ```
  enterprise_app.py
  ├── api/
  │   ├── routes/
  │   │   └── v1/
  │   │       └── users.py
  │   │           └── handlers/
  │   │               └── authentication.py
  │   │                   └── providers/
  │   │                       └── oauth/
  │   │                           └── google.py
  │   │                               └── scopes.py
  ```

**Application in Refactoring**:

1. **Identify Excessive Depth**:
   - ✅ If tree > 8 levels → Consider simplification
   - ✅ Very deep modules = difficult maintenance

2. **Detect Circular Dependencies**:
   ```python
   # ❌ BAD: Circular dependency
   # module_a.py
   from module_b import B
   
   # module_b.py
   from module_a import A  # Circular!
   ```

3. **Reorganize by Cohesion**:
   ```python
   # ✅ GOOD: Group related imports
   # before (dispersed):
   from utils.string import normalize
   from helpers.text import clean
   from tools.format import sanitize
   
   # after (cohesive):
   from text_processing import normalize, clean, sanitize
   ```

4. **Reduce Coupling**:
   - ✅ Direct imports only of what's necessary
   - ✅ Avoid `from module import *` (increases coupling)
   - ✅ Use interfaces/abstractions to decouple

5. **Visualize to Understand**:
   - Use tools like `pydeps`, `import-graph` (Python)
   - Identify "hubs" (heavily imported modules)
   - Refactor central modules to reduce impact

**Why it's important**:
- ✅ **Comprehension**: Clear tree = easier to understand code
- ✅ **Maintenance**: Organized dependencies = localized changes
- ✅ **Performance**: Fewer unnecessary imports = faster startup
- ✅ **Testing**: Independent modules = isolated tests
- ✅ **Refactoring**: Visualizing tree helps identify improvement opportunities

#### 📦 **Hierarchies and Encapsulation**
- Use classes when there is shared state
- Encapsulate private attributes (`_attribute`)
- Expose only necessary public interface

**Example**:
```python
# ✅ GOOD: Proper encapsulation
class ReferenceUpdater:
    def __init__(self, project_dir: str):
        self._project_dir = project_dir
        self._substitutions = {}
    
    def update_references(self) -> Dict[str, int]:
        """Clear public interface"""
        self._scan_files()  # Private method
        self._build_map()   # Private method
        return self._apply_changes()

# ❌ BAD: Everything exposed, no structure
def do_everything(dir, old, new, backup, ext):
    # 200 lines without organization
```

#### 🎯 **High Cohesion and Low Coupling**
- **High Cohesion**: Each module/class has a single clear responsibility
- **Low Coupling**: Independent modules, communication via interfaces

**Example**:
```python
# ✅ HIGH COHESION: Each class does ONE thing
class KeyExtractor:
    """Only extracts keys from structures"""
    def extract(self, data) -> Dict[str, str]: ...

class SubstitutionMapBuilder:
    """Only builds substitution map"""
    def build(self, old, new) -> Dict[str, str]: ...

class FileUpdater:
    """Only updates files"""
    def update(self, files, map) -> int: ...

# ✅ LOW COUPLING: Communication via interfaces
class ReferenceUpdater:
    def __init__(self, extractor: KeyExtractor, builder: SubstitutionMapBuilder):
        self._extractor = extractor  # Dependency injection
        self._builder = builder

# ❌ BAD: Low cohesion, high coupling
class EverythingManager:
    def do_all(self):
        # Does extraction + build + update + logging + GUI
        # Imports 20 different modules
        # Impossible to test in isolation
```

#### 🏗️ **GoF (Gang of Four) Patterns**
Apply design patterns when appropriate:

1. **Strategy Pattern** (algorithm selection at runtime):
```python
class CaseConverter:
    def __init__(self, strategy: CaseStrategy):
        self._strategy = strategy
    
    def convert(self, text: str) -> str:
        return self._strategy.apply(text)

class CamelCaseStrategy(CaseStrategy):
    def apply(self, text: str) -> str: ...

class SnakeCaseStrategy(CaseStrategy):
    def apply(self, text: str) -> str: ...
```

2. **Factory Pattern** (complex object creation):
```python
class ProcessorFactory:
    @staticmethod
    def create(type: str) -> Processor:
        if type == "data":
            return DATAProcessor()
        elif type == "ts":
            return TypeScriptProcessor()
```

3. **Observer Pattern** (event notification):
```python
class ProcessingModal(QDialog):
    cancel_requested = Signal()  # Observer pattern
    
    def _on_cancel_clicked(self):
        self.cancel_requested.emit()  # Notifies observers
```

4. **Command Pattern** (undo/redo):
```python
class ReplaceCommand:
    def __init__(self, file: str, old: str, new: str):
        self._file = file
        self._old = old
        self._new = new
    
    def execute(self): ...
    def undo(self): ...
```

#### 🎨 **GRASP (General Responsibility Assignment Software Patterns)**

1. **Information Expert**: Assign responsibility to the one with the information
```python
# ✅ GOOD: Dictionary has the info, so it has the method
class DataStore:
    def __init__(self, data: dict):
        self._data = data
    
    def get_value(self, key_path: str) -> Optional[str]:
        """Dictionary knows its structure"""
        return self._navigate_path(key_path)

# ❌ BAD: External class manipulates internal structure
def get_value_from_dict(dict_data, key_path):
    # Direct access to the dictionary's internal structure
```

2. **Creator**: Class A creates B if A contains/aggregates B
```python
# ✅ GOOD: RewriterDock creates its own widgets
class ComponentB(BaseDock):
    def __init__(self):
        self._create_widgets()  # Creator pattern
        self._setup_layout()
    
    def _create_widgets(self):
        self.ed_input = QLineEdit()  # Creates its children
        self.btn_process = QPushButton()
```

3. **Controller**: Delegate system operations to controller
```python
# ✅ GOOD: Controller coordinates operations
class RewriterController:
    def process_file(self, path: str):
        data = self._reader.read(path)
        processed = self._processor.process(data)
        self._writer.write(path, processed)

# ❌ BAD: GUI does everything directly
class RewriterDock:
    def on_button_click(self):
        # 50 lines of business logic in the GUI
```

4. **Low Coupling**: Minimize dependencies
```python
# ✅ GOOD: Generic interface
def update_references(updater: ReferenceUpdater):
    """Accepts any updater that implements the interface"""
    updater.update()

# ❌ BAD: Concrete dependency
def update_references(file_path: str, backup: bool, ext: list):
    """Many parameters, high coupling"""
```

5. **High Cohesion**: One class, one responsibility
```python
# ✅ GOOD: High cohesion
class FileReader:
    """Only reads files"""
    def read(self, path: str) -> str: ...

class DataValidator:
    """Only validates data"""
    def validate(self, data: dict) -> bool: ...

# ❌ BAD: Low cohesion
class FileManager:
    def read(self): ...
    def write(self): ...
    def validate(self): ...
    def send_email(self): ...  # ?!
```

**Anti-pattern** ❌:
```python
# DO NOT do everything at once:
def complex_function_with_everything():
    # 500 lines of code
    # Multiple responsibilities
    # Difficult to test
    # High coupling
    # No reuse
```

**Correct Pattern** ✅:
```python
# Module: src/rewriter/key_extractor.py
class KeyExtractor:
    """High cohesion: only extracts keys"""
    def extract_from_obj(self, data) -> Dict[str, str]:
        return self._recurse(data, prefix='t')

# Module: src/rewriter/substitution_builder.py
class SubstitutionMapBuilder:
    """High cohesion: only builds maps"""
    def build_by_value(self, old, new) -> Dict[str, str]:
        return self._match_values(old, new)

# Module: src/rewriter/reference_updater.py
class ReferenceUpdater:
    """Low coupling: uses interfaces"""
    def __init__(self, extractor: KeyExtractor, builder: SubstitutionMapBuilder):
        self._extractor = extractor  # Dependency injection
        self._builder = builder
    
    def update_project(self, dir: str) -> Dict[str, int]:
        """Coordinates but doesn't implement everything"""
        old = self._extractor.extract(self._read_old())
        new = self._extractor.extract(self._read_new())
        map = self._builder.build_by_value(old, new)
        return self._apply_to_files(dir, map)
```

---

### 6️⃣.5️⃣ **OWASP Security Checklist** ⭐ [MANDATORY]

> **CRITICAL FOR PRODUCTION**: This step is **MANDATORY** in Simplicity 3.

**Why mandatory for production**:
- ✅ Vulnerabilities affect **real users**
- ✅ You are **alone** - no second pair of eyes
- ✅ LGPD/GDPR applies to user data
- ✅ Quick checklist (10-15min) prevents costly problems

**OWASP Top 10 - Simplified Checklist**:

```markdown
## Security Checklist - Task #XX

### 1. Injection (SQL, Command, Code)
- [ ] All SQL queries use **parametrization** (no f-strings)?
- [ ] Shell commands sanitized (**shlex.quote()** or avoided)?
- [ ] `eval()`, `exec()`, `__import__()` NOT used?

### 2. Authentication
- [ ] Passwords NEVER in plaintext (use **bcrypt/argon2**)?
- [ ] Tokens/sessions have **expiration** and **invalidation**?
- [ ] Rate limiting on login endpoints (prevent brute-force)?

### 3. Sensitive Data
- [ ] Sensitive data **NOT** in logs (passwords, tokens, CPF)?
- [ ] Sensitive files have **correct permissions** (600/700)?
- [ ] Secrets in **environment variables** (not hardcoded)?

### 4. XML/XXE (if using XML)
- [ ] XML parser has **entity expansion disabled**?
- [ ] Schema validation before parsing?

### 5. Access Control
- [ ] Permissions checked **before** critical operations?
- [ ] User cannot access data of **other users**?
- [ ] Paths validated (no **path traversal**: `../../etc/passwd`)?

### 6. Insecure Configurations
- [ ] **DEBUG=False** in production?
- [ ] Secrets **NOT** committed to Git (.env in .gitignore)?
- [ ] Dependencies updated (**pip-audit** without vulnerabilities)?

### 7. XSS (if web/HTML)
- [ ] HTML output **escaped** (use template engine)?
- [ ] User input **sanitized** before display?

### 8. Insecure Deserialization
- [ ] **pickle** avoided (or validated if necessary)?
- [ ] DATA preferred over pickle for external data?

### 9. Vulnerable Dependencies
- [ ] `pip-audit` executed and no HIGH/CRITICAL issues?
- [ ] Dependencies updated (last 6 months)?

### 10. Logs/Monitoring
- [ ] Critical operations **logged** (create, update, delete)?
- [ ] Logs **DO NOT** contain sensitive data?
```

**INSECURE vs SECURE Example**:

```python
# ❌ INSECURE - SQL Injection
def get_user(username):
    query = f"SELECT * FROM users WHERE name='{username}'"
    return db.execute(query)
# Attack: username = "admin' OR '1'='1"

# ✅ SECURE - Parameterized
def get_user(username):
    query = "SELECT * FROM users WHERE name=?"
    return db.execute(query, (username,))

# ❌ INSECURE - Command Injection
def backup_file(filename):
    os.system(f"tar -czf backup.tar.gz {filename}")
# Attack: filename = "file.txt; rm -rf /"

# ✅ SECURE - List of args
def backup_file(filename):
    subprocess.run(["tar", "-czf", "backup.tar.gz", filename], check=True)

# ❌ INSECURE - Password in log
logger.info(f"User {username} logged in with password {password}")

# ✅ SECURE - No sensitive data
logger.info(f"User {username} logged in successfully")

# ❌ INSECURE - Path Traversal
def read_file(user_path):
    with open(f"/app/data/{user_path}") as f:
        return f.read()
# Attack: user_path = "../../etc/passwd"

# ✅ SECURE - Validate path
def read_file(user_path):
    safe_path = os.path.abspath(f"/app/data/{user_path}")
    if not safe_path.startswith("/app/data/"):
        raise ValueError("Invalid path")
    with open(safe_path) as f:
        return f.read()
```

**Automated Tools** (run BEFORE commit):

```bash
# 1. Vulnerabilities in dependencies
pip install pip-audit
pip-audit
# If HIGH/CRITICAL reported, update deps

# 2. Security linter
pip install bandit
bandit -r . -ll  # Low confidence + Low severity
# Review reported issues

# 3. Detected secrets
pip install detect-secrets
detect-secrets scan > .secrets.baseline
# Review if any secret leaked
```

**Pre-commit Hook** (automate):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ['-ll']
  
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
```

**When to SKIP the checklist** (rarely):
- ❌ Internal code without sensitive data
- ❌ Disposable single-use script
- ❌ Non-production prototype

**Estimated Time**: 10-15 minutes per task.

📘 **Complete checklist with 10 examples**: See `PROTOCOLO_SIMPLICIDADE_2.md` - Step 6.5

---

### 6️⃣.6️⃣ **Project Icons** [MANDATORY]

> **CRITICAL FOR AIs**: Every project must include appropriate icons to ensure professionalism and visual identity.

**When to Apply**: During implementation (Step 6), after defining the basic project structure.

#### 📋 Mandatory Requirement

Artificial intelligence **MUST** produce or download an icon for the project, whether:
- 🌐 Website/Web Application
- 💻 Desktop Program
- 📱 Mobile Application
- 🔧 Tool/Utility

#### 🎨 Icon Formats by Technology

**Web Applications**:
- ✅ **favicon.ico** (16x16, 32x32, 48x48 px) - Universal compatibility
- ✅ **icon.svg** - Vector, scalable, modern
- ✅ **icon-192.png** and **icon-512.png** - PWA/Android
- ✅ **apple-touch-icon.png** (180x180 px) - iOS

**Desktop Applications**:
- ✅ **icon.png** (256x256, 512x512 px) - Linux
- ✅ **icon.ico** (multiple sizes) - Windows
- ✅ **icon.icns** - macOS

**Mobile Applications**:
- ✅ **icon.png** (1024x1024 px) - iOS App Store
- ✅ **ic_launcher.png** (multiple densities) - Android
- ✅ **adaptive-icon.xml** - Android adaptive

#### 📁 Folder Structure (MANDATORY)

Icons **MUST** be organized in a dedicated folder:

```
project/
├── assets/              # ✅ PREFERRED (default for all)
│   ├── icons/
│   │   ├── favicon.ico
│   │   ├── icon.svg
│   │   ├── icon-192.png
│   │   ├── icon-512.png
│   │   └── apple-touch-icon.png
│   └── ...
│
# OR alternatives according to technology:
├── public/              # ✅ React, Vue, Next.js
│   ├── favicon.ico
│   └── icons/
├── static/              # ✅ Flask, Django, Svelte
│   └── icons/
├── src/assets/          # ✅ Angular, Ionic
│   └── icons/
├── resources/           # ✅ Electron, Tauri
│   └── icons/
└── res/                 # ✅ Native Android
    └── drawable/
```

**Golden Rule**: Always use a specific folder for icons, never loose files at the project root.

#### 🔧 How to Obtain/Create Icons

AI must follow this priority order:

1. **Ask the Programmer** (ALWAYS first):
   ```
   ❓ Do you already have an icon for the project?
   
   Options:
   A) ✅ Yes, I have (provide the path/file)
   B) 🎨 No, create a simple icon for me
   C) 🔍 No, download a suitable free icon
   D) ⏭️ Skip for now (not recommended)
   ```

2. **If A (User provides)**:
   - Validate format and size
   - Convert to necessary formats (use tools like `convert`, `sharp`, `imagemagick`)
   - Organize in the correct folder

3. **If B (AI creates simple icon)**:
   - Create vector SVG icon with project initials
   - Export to necessary formats (PNG, ICO)
   - Use project identity colors (if defined)

4. **If C (AI downloads icon)**:
   - Use free and copyright-free sources:
     - ✅ [Heroicons](https://heroicons.com/) (MIT License)
     - ✅ [Lucide Icons](https://lucide.dev/) (ISC License)
     - ✅ [Tabler Icons](https://tabler-icons.io/) (MIT License)
     - ✅ [Iconoir](https://iconoir.com/) (MIT License)
   - Verify license before using
   - Document source in README

5. **If D (Skip)**:
   - ⚠️ Warn that project will lack visual identity
   - Add task in TASKS.md for future: `[ ] Create project icon`

#### 🎨 Simple SVG Icon Example (Generated by AI)

```svg
<!-- assets/icons/icon.svg -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="20" fill="#4F46E5"/>
  <text x="50" y="65" font-family="Arial, sans-serif" font-size="48" 
        font-weight="bold" fill="white" text-anchor="middle">MP</text>
</svg>
```

#### 🔨 Icon Conversion Tools

**Python** (recommended for automation):
```bash
# Install Pillow
pip install Pillow

# Convert SVG to PNG (via cairosvg)
pip install cairosvg
python -c "import cairosvg; cairosvg.svg2png(url='icon.svg', write_to='icon.png', output_width=512)"

# Create ICO with multiple sizes
from PIL import Image
img = Image.open('icon.png')
img.save('favicon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48)])
```

**Node.js** (web projects):
```bash
# Install sharp
npm install sharp

# Conversion script
node -e "
const sharp = require('sharp');
sharp('icon.svg').resize(192, 192).toFile('icon-192.png');
sharp('icon.svg').resize(512, 512).toFile('icon-512.png');
"
```

**ImageMagick** (universal):
```bash
# Convert SVG to PNG
convert icon.svg -resize 192x192 icon-192.png

# Create favicon.ico
convert icon.png -define icon:auto-resize=16,32,48 favicon.ico
```

#### 🗂️ Project Integration

**HTML (Web)**:
```html
<!-- index.html -->
<head>
  <!-- Basic favicon -->
  <link rel="icon" type="image/x-icon" href="/assets/icons/favicon.ico">
  
  <!-- Modern SVG (preferred) -->
  <link rel="icon" type="image/svg+xml" href="/assets/icons/icon.svg">
  
  <!-- PNG for different sizes -->
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/icon-32.png">
  <link rel="icon" type="image/png" sizes="192x192" href="/assets/icons/icon-192.png">
  
  <!-- Apple Touch Icon -->
  <link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
  
  <!-- Android Chrome -->
  <link rel="manifest" href="/manifest.json">
</head>
```

**manifest.json (PWA)**:
```json
{
  "name": "My Project",
  "short_name": "MP",
  "icons": [
    {
      "src": "/assets/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/assets/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

**Python (Desktop - PyQt/Tkinter)**:
```python
# PyQt6
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

app = QApplication([])
app.setWindowIcon(QIcon('assets/icons/icon.png'))

# Tkinter
import tkinter as tk
root = tk.Tk()
root.iconbitmap('assets/icons/icon.ico')  # Windows
# or
root.iconphoto(True, tk.PhotoImage(file='assets/icons/icon.png'))  # Linux/Mac
```

**Electron (Desktop)**:
```javascript
// main.js
const { app, BrowserWindow } = require('electron');
const path = require('path');

const win = new BrowserWindow({
  icon: path.join(__dirname, 'resources/icons/icon.png')
});
```

**React Native (Mobile)**:
```
// android/app/src/main/res/
mipmap-hdpi/ic_launcher.png      (72x72)
mipmap-mdpi/ic_launcher.png      (48x48)
mipmap-xhdpi/ic_launcher.png     (96x96)
mipmap-xxhdpi/ic_launcher.png    (144x144)
mipmap-xxxhdpi/ic_launcher.png   (192x192)

// ios/ProjectName/Images.xcassets/AppIcon.appiconset/
// Configured via Xcode or Contents.json
```

#### ⏰ Best Timing to Add Icons

**Recommendation**: **During Step 6 (Implementation)**, preferably:

1. **Project Start** (✅ IDEAL):
   - When creating initial folder structure
   - Before first commit
   - Facilitates visual identity from the beginning

2. **MVP/Prototype** (✅ GOOD):
   - After basic functionalities work
   - Before showing to users/clients
   - Ensures minimum professionalism

3. **Before Production** (⚠️ ACCEPTABLE):
   - During deployment preparation
   - Before publishing (App Store, Play Store, web)
   - Minimum necessary, but delayed

4. **❌ NEVER**: Leave for "later" without defined date

#### 📋 Icon Checklist (Validation)

```markdown
## Icon Checklist - Project [Name]

### Icons Created
- [ ] Main icon created/obtained (source: [specify])
- [ ] License verified (if downloaded from external source)
- [ ] Vector format available (SVG) or high-quality PNG source

### Necessary Formats
- [ ] **favicon.ico** (16x16, 32x32, 48x48 px)
- [ ] **icon.svg** (vector)
- [ ] **icon-192.png** (192x192 px) - PWA
- [ ] **icon-512.png** (512x512 px) - PWA
- [ ] **apple-touch-icon.png** (180x180 px) - iOS
- [ ] Other technology-specific formats

### Organization
- [ ] `assets/icons/` folder created
- [ ] All icons organized in correct folder
- [ ] No loose icons at project root

### Integration
- [ ] Icon referenced in HTML/main code
- [ ] manifest.json updated (if PWA)
- [ ] Tested in browser/application (icon appears)
- [ ] Documented in README (if third-party icon)

### Quality
- [ ] Icon has good resolution (not pixelated)
- [ ] Colors appropriate to project
- [ ] Visible on light AND dark backgrounds (if applicable)
- [ ] Recognizable at small sizes (16x16)
```

#### 🎯 Rationale: Why Icons Are Mandatory

1. **Professionalism**: Projects without icons appear incomplete/amateur
2. **Visual Identity**: Users recognize the app by its icon (branding)
3. **User Experience**: Icon helps locate the app among multiple tabs/windows
4. **Platform Requirements**: App stores (iOS/Android) REQUIRE icons
5. **PWA**: Browsers request icons for installation
6. **Organization**: Facilitates finding and managing visual assets
7. **Traceability**: Documenting source ensures license compliance

#### 🚨 Common Mistakes to Avoid

❌ **Don't**:
- Leave icon at project root (e.g., loose `favicon.ico`)
- Use low-resolution icon (pixelated when enlarged)
- Forget to reference in HTML/code
- Use copyrighted icon without permission
- Create only one size (browsers need multiple)

✅ **Do**:
- Organize in dedicated folder (`assets/icons/`)
- Generate multiple sizes (16, 32, 192, 512 px)
- Validate that icon appears correctly
- Document source if third-party icon
- Use vector format (SVG) when possible

#### 📚 Useful Resources

**Free Icon Generators** (online):
- [Favicon.io](https://favicon.io/) - Generates favicon from text/image/emoji
- [RealFaviconGenerator](https://realfavicongenerator.net/) - Generates all formats
- [Favicon Generator](https://www.favicon-generator.org/) - Simple and fast

**Free Icon Libraries**:
- [Heroicons](https://heroicons.com/) - MIT License
- [Lucide Icons](https://lucide.dev/) - ISC License
- [Tabler Icons](https://tabler-icons.io/) - MIT License
- [Iconoir](https://iconoir.com/) - MIT License
- [Bootstrap Icons](https://icons.getbootstrap.com/) - MIT License

**Conversion Tools**:
- [ImageMagick](https://imagemagick.org/) - Universal CLI
- [Pillow (Python)](https://pillow.readthedocs.io/) - Image library
- [Sharp (Node.js)](https://sharp.pixelplumbing.com/) - High performance

#### 📝 Example README Documentation

```markdown
## 🎨 Project Icon

**Source**: Created by AI using project initials  
**License**: Free to use (generated for this project)  
**Location**: `assets/icons/`

### Available Formats
- `icon.svg` - Vector (preferred)
- `favicon.ico` - Browsers (16, 32, 48 px)
- `icon-192.png` - PWA/Android
- `icon-512.png` - PWA/Android
- `apple-touch-icon.png` - iOS

### Colors
- Primary: `#4F46E5` (Indigo Blue)
- Text: `#FFFFFF` (White)
```

#### ⏱️ Estimated Time

- **Create simple icon (AI)**: 5-10 minutes
- **Download and adapt icon**: 10-15 minutes
- **Convert to necessary formats**: 5-10 minutes
- **Integrate into project**: 5-10 minutes
- **TOTAL**: 15-30 minutes

**Small investment, big impact on project quality perception.**

---

### 6️⃣.7️⃣ **Execution Scripts to Facilitate Usage** [RECOMMENDED]

> **RECOMMENDATION FOR AIs**: When dealing with an application or program written in a programming language that is executable, it's recommended to create batch scripts for Windows, Linux, and Mac accessible in the main folder or root directory, in order to facilitate application execution.

**When to Apply**: During implementation (Step 6), especially after setting up the basic structure of the executable project.

#### 📋 Context and Purpose

Execution scripts in the project root significantly facilitate application usage, especially:
- ✅ **Development**: Accelerates development cycle (run without manually configuring environment)
- ✅ **Onboarding**: New developers can run the project immediately
- ✅ **Testing**: Facilitates test execution and validation
- ✅ **Production**: In some cases, can simplify deployment (if there are no better alternatives like Docker, systemd, etc.)

#### 🎯 When to Create Execution Scripts

**✅ CREATE scripts IF:**
- ✅ Application is executable (not a library)
- ✅ Requires environment configuration (variables, paths, dependencies)
- ✅ Has multiple initialization commands
- ✅ Needs setup before execution (migrations, build, etc.)
- ✅ Team/users need to execute frequently

**❌ DO NOT create scripts IF:**
- ❌ Application already has well-documented native CLI
- ❌ Uses standard language tools (npm start, cargo run, etc.)
- ❌ Deployment uses orchestration (Docker, Kubernetes) - scripts stay in Dockerfile
- ❌ Project is a library/framework (not executable)

#### 📝 Recommended Folder Structure

```
project/
├── run.bat                 # ✅ Windows (main execution)
├── run.sh                  # ✅ Linux/Mac (main execution)
├── dev.bat                 # 🔄 Development Windows (optional)
├── dev.sh                  # 🔄 Development Linux/Mac (optional)
├── test.bat                # 🧪 Tests Windows (optional)
├── test.sh                 # 🧪 Tests Linux/Mac (optional)
├── build.bat               # 🏗️ Build Windows (optional)
├── build.sh                # 🏗️ Build Linux/Mac (optional)
└── README.md               # Script usage documentation
```

**Golden Rule**: Scripts in project root = easy access. Complex scripts can stay in `scripts/` with simple wrappers in root.

#### 💻 Script Examples by Language

##### **Python**

**run.sh (Linux/Mac)**:
```bash
#!/bin/bash
# Execution script for Linux/Mac

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Python application...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}📦 Installing dependencies...${NC}"
    pip install -q -r requirements.txt
fi

# Run application
echo -e "${GREEN}✅ Running application...${NC}"
python src/main.py "$@"
```

**run.bat (Windows)**:
```batch
@echo off
REM Execution script for Windows

echo 🚀 Starting Python application...

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Virtual environment not found. Creating...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/update dependencies
if exist "requirements.txt" (
    echo 📦 Installing dependencies...
    pip install -q -r requirements.txt
)

REM Executar aplicação
echo ✅ Running application...
python src\main.py %*
```

##### **Node.js**

**run.sh (Linux/Mac)**:
```bash
#!/bin/bash
# Execution script for Linux/Mac

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Node.js application...${NC}"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${GREEN}📦 Installing dependencies...${NC}"
    npm install
fi

# Run application
echo -e "${GREEN}✅ Running application...${NC}"
npm start "$@"
```

**run.bat (Windows)**:
```batch
@echo off
REM Execution script for Windows

echo 🚀 Starting Node.js application...

REM Check if node_modules exists
if not exist "node_modules\" (
    echo 📦 Installing dependencies...
    call npm install
)

REM Run application
echo ✅ Running application...
npm start %*
```

##### **Java**

**run.sh (Linux/Mac)**:
```bash
#!/bin/bash
# Execution script for Linux/Mac

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Java application...${NC}"

# Compile if necessary
if [ ! -d "target" ]; then
    echo -e "${GREEN}🏗️ Compiling project...${NC}"
    mvn clean package -DskipTests
fi

# Run JAR
echo -e "${GREEN}✅ Running application...${NC}"
java -jar target/myapp.jar "$@"
```

**run.bat (Windows)**:
```batch
@echo off
REM Execution script for Windows

echo 🚀 Starting Java application...

REM Compile if necessary
if not exist "target\" (
    echo 🏗️ Compiling project...
    call mvn clean package -DskipTests
)

REM Run JAR
echo ✅ Running application...
java -jar target\myapp.jar %*
```

##### **Go**

**run.sh (Linux/Mac)**:
```bash
#!/bin/bash
# Execution script for Linux/Mac

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Go application...${NC}"

# Download dependencies if necessary
if [ ! -f "go.sum" ]; then
    echo -e "${GREEN}📦 Downloading dependencies...${NC}"
    go mod download
fi

# Run application
echo -e "${GREEN}✅ Running application...${NC}"
go run cmd/main.go "$@"
```

**run.bat (Windows)**:
```batch
@echo off
REM Execution script for Windows

echo 🚀 Starting Go application...

REM Download dependencies if necessary
if not exist "go.sum" (
    echo 📦 Downloading dependencies...
    go mod download
)

REM Run application
echo ✅ Running application...
go run cmd\main.go %*
```

##### **Rust**

**run.sh (Linux/Mac)**:
```bash
#!/bin/bash
# Execution script for Linux/Mac

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Rust application...${NC}"

# Compile and run
echo -e "${GREEN}✅ Running application (cargo run)...${NC}"
cargo run --release "$@"
```

**run.bat (Windows)**:
```batch
@echo off
REM Execution script for Windows

echo 🚀 Starting Rust application...

REM Compile and run
echo ✅ Running application (cargo run)...
cargo run --release %*
```

#### 🔧 Additional Useful Scripts

##### **Development Script** (watch/reload mode)

**dev.sh**:
```bash
#!/bin/bash
# Development mode with auto-reload

echo "🔄 Starting in development mode..."

# Python
# pip install watchdog
# watchmedo auto-restart --directory=./src --pattern=*.py python src/main.py

# Node.js
# npm run dev  # nodemon or similar

# Go
# go install github.com/cosmtrek/air@latest
# air

# Rust
# cargo install cargo-watch
# cargo watch -x run
```

##### **Test Script**

**test.sh**:
```bash
#!/bin/bash
# Run tests

echo "🧪 Running tests..."

# Python
# pytest tests/ -v

# Node.js
# npm test

# Java
# mvn test

# Go
# go test ./...

# Rust
# cargo test
```

#### 📋 Execution Scripts Checklist

```markdown
## Scripts Checklist - Project [Name]

### Scripts Created
- [ ] **run.sh** (Linux/Mac) - Main execution script
- [ ] **run.bat** (Windows) - Main execution script
- [ ] Execution permissions configured (`chmod +x *.sh`)
- [ ] Scripts tested on each platform

### Optional Scripts (as needed)
- [ ] **dev.sh/dev.bat** - Development mode with auto-reload
- [ ] **test.sh/test.bat** - Run automated tests
- [ ] **build.sh/build.bat** - Compile/build project
- [ ] **install.sh/install.bat** - Install dependencies
- [ ] **clean.sh/clean.bat** - Clean build artifacts

### Documentation
- [ ] README.md updated with script usage instructions
- [ ] Usage examples documented
- [ ] System requirements documented (Python 3.9+, Node 18+, etc.)
- [ ] Basic troubleshooting included

### Script Features
- [ ] Check if dependencies are installed
- [ ] Create virtual environment/directories if needed
- [ ] Clear and informative output messages
- [ ] Support argument passing (`./run.sh --help`)
- [ ] Handle errors gracefully
- [ ] Include colors in output (optional, improves UX)
```

#### 📝 Example README Documentation

```markdown
## 🚀 How to Run

### Requirements
- Python 3.9+ (or Node.js 18+, Java 17+, etc.)
- Git

### Quick Start

**Linux/Mac**:
```bash
./run.sh
```

**Windows**:
```batch
run.bat
```

### Available Scripts

| Script | Description | Platform |
|--------|-------------|----------|
| `run.sh` / `run.bat` | Runs the main application | Linux/Mac / Windows |
| `dev.sh` / `dev.bat` | Development mode (auto-reload) | Linux/Mac / Windows |
| `test.sh` / `test.bat` | Runs automated tests | Linux/Mac / Windows |
| `build.sh` / `build.bat` | Compiles/builds the project | Linux/Mac / Windows |

### Arguments

Pass arguments to application:
```bash
./run.sh --port 8080 --debug
```

### Troubleshooting

**Error: Permission denied (Linux/Mac)**
```bash
chmod +x run.sh dev.sh test.sh build.sh
```

**Error: Dependencies not found**
- Scripts automatically install dependencies on first run
- If it fails, run manually: `pip install -r requirements.txt` (Python) or `npm install` (Node.js)
```

#### ⏱️ Estimated Time

- **Create basic scripts (run.sh/run.bat)**: 10-15 minutes
- **Add optional scripts (dev, test, build)**: 5-10 minutes each
- **Document in README**: 10-15 minutes
- **Test on multiple platforms**: 10-20 minutes
- **TOTAL**: 30-60 minutes

**Investment: ~30-60 minutes. Benefit: Saves hours of setup for each developer and user.**

#### 🎯 Rationale: Why Execution Scripts Are Important

1. **Developer Experience (DX)**: New developer clones repo, runs `./run.sh` and application works
2. **Friction Reduction**: No need to read complex documentation to run project
3. **Consistency**: Everyone runs the same way, reduces "works on my machine"
4. **Automation**: Scripts can automatically configure environment (create venv, install deps)
5. **Living Documentation**: Scripts serve as executable documentation of initialization process
6. **Onboarding**: Accelerates entry of new team members
7. **CI/CD**: Scripts can be reused in pipelines
8. **Cross-Platform**: Explicit support for Windows, Linux, and Mac

#### ⚠️ When NOT to Use Root Scripts

**Use better alternatives when available:**
- 🐳 **Docker/Docker Compose**: For apps with multiple dependencies (databases, queues, etc.)
- 📦 **Native Package Managers**: `npm start`, `cargo run`, `go run` are already sufficient
- 🎯 **Task Runners**: Makefile, Just, Task for complex projects
- ☸️ **Orchestration**: Kubernetes, systemd for enterprise production

**Recommended Combination**:
```
project/
├── docker-compose.yml      # 🐳 For complete environment
├── Makefile                # 🎯 For complex commands
├── run.sh                  # ✅ Simple wrapper that calls Make/Docker
└── README.md               # 📚 Documents when to use each one
```

**Wrapper example**:
```bash
#!/bin/bash
# run.sh - Simple wrapper

if command -v docker &> /dev/null; then
    echo "🐳 Docker detected, using docker-compose..."
    docker-compose up
else
    echo "⚠️ Docker not found, running locally..."
    make run
fi
```

---

### 7️⃣ **Verify CLI Implementation + Code Review**
- **CRITICAL**: Verify that the new functionality is available via **CLI (Command Line Interface)**
- **IMPORTANT**: During verification, apply the **9 Quality Criteria** to the CLI code
- It's not enough to implement GUI, important functionalities must have a **CLI interface** for automation
- Verify subcommands, arguments, help text, integration, and code quality

**CLI Implementation Checklist**:

1. **Correct Import in app.py**:
   ```python
   # ✅ Verify if module was imported
   from .gui import (
       ComponentJ, ComponentK, ComponentI,
       ComponentC, ComponentD, ComponentA,
       ComponentB, ComponentF, ComponentG, ComponentH,
       ComponentE, NewComponent  # ← NEW module should be here
   )
   ```

2. **Export in Module's __init__.py**:
   ```python
   # src/gui/__init__.py
   from .text_to_data_dock import NewComponent
   
   __all__ = [
       'ComponentJ', 'ComponentK', 'ComponentI',
       'ComponentC', 'ComponentD', 'ComponentA',
       'ComponentB', 'ComponentF', 'ComponentG', 'ComponentH',
       'ComponentE', 'NewComponent'  # ← NEW module exported
   ]
   ```

3. **Menu Item Created and Connected**:
   ```python
   # In _build_menu() or similar
   m_tools = bar.addMenu(tr("menu.tools"))
   
   # Create QAction
   self.act_open_new_component = QAction(tr("menu.tools.text_to_data"), self)
   
   # Add to menu
   m_tools.addAction(self.act_open_new_component)
   
   # Connect signal
   self.act_open_new_component.triggered.connect(lambda: self.dock_new_component.show())
   ```

4. **Dock Initialized in __init__() or setup method**:
   ```python
   # In __init__() of MainWindow
   def __init__(self):
       super().__init__()
       # ... other docks ...
       self._open_new_component()  # ← Initialize dock
   
   def _open_new_component(self):
       self.dock_new_component = NewComponent(self)
       self.dock_new_component.open_in_other_component_requested.connect(self._load_data_from_source)
       self.addDockWidget(Qt.RightDockWidgetArea, self.dock_new_component)
       self.dock_new_component.hide()
   ```

5. **Signals Connected** (if applicable):
   ```python
   # Connect custom signals
   self.dock_new_component.open_in_other_component_requested.connect(self._load_data_from_source)
   
   def _load_data_from_source(self, data_str: str):
       """Callback to open DATA in editor"""
       if not hasattr(self, 'component_viewer'):
           self._open_component()
       self.component_viewer.load_data_string(data_str)
       self.component_viewer.show()
   ```

6. **i18n Translations Added**:
   ```data
   // src/i18n/en.data
   {
     "menu.tools.text_to_data": "Text to DATA Converter"
   }
   
   // src/i18n/pt_BR.data
   {
     "menu.tools.text_to_data": "Conversor de Texto para DATA"
   }
   ```

**Integration Test Checklist**:
- ✅ **Menu accessible**: Verify if item appears in Tools menu
- ✅ **Dock opens**: Clicking the menu should open the dock correctly
- ✅ **Basic functionality**: Test simple conversion
- ✅ **Signals work**: Test integration with other components (e.g., Open in Editor)
- ✅ **No console errors**: There should be no ImportError, AttributeError, etc.
- ✅ **Translation working**: Menu in PT-BR should show translated text

**Real Example (Task Example - Text to DATA Converter)**:
```python
✅ Import: from .gui import NewComponent
✅ Export: __all__ = [..., 'NewComponent']
✅ Menu: self.act_open_new_component = QAction(tr("menu.tools.text_to_data"), self)
✅ Init: self._open_new_component() called in __init__()
✅ Signal: open_in_other_component_requested.connect(self._load_data_from_source)
✅ i18n: EN "Text to DATA Converter", PT-BR "Conversor de Texto para DATA"
✅ Test: Menu opens dock, conversion works, signal to editor OK
```

**Questions to Validate Integration**:
1. ❓ "Is the new module imported in the main file (app.py)?"
2. ❓ "Is the module exported in the folder's __init__.py?"
3. ❓ "Is there a menu item to access the functionality?"
4. ❓ "Is the menu item connected to the correct method?"
5. ❓ "Is the dock/component initialized at application startup?"
6. ❓ "Are custom signals connected?"
7. ❓ "Were translations added (EN and PT-BR)?"
8. ❓ "Is the functionality accessible without errors?"

**Why?**: Ensure that the implemented code is **really usable** by the end user, not just "works in isolation".

---

### 8️⃣ **Verify GUI Implementation + Code Review**
- **CRITICAL**: Verify that components are **integrated into the main program** and accessible
- **IMPORTANT**: During verification, apply the **9 Quality Criteria** to the GUI code
- It's not enough to implement the module/dock, it needs to be **accessible and functional** in the app
- Verify menu, imports, initialization, connections, and code quality

**Part A - GUI Functional Verification (Integration)**:

1. **Correct Import in app.py**:
   ```python
   # ✅ Verify if module was imported
   from .gui import (
       ComponentJ, ComponentK, ComponentI,
       ComponentC, ComponentD, ComponentA,
       ComponentB, ComponentF, ComponentG, ComponentH,
       ComponentE, NewComponent  # ← NEW module should be here
   )
   ```

2. **Export in Module's __init__.py**:
   ```python
   # src/gui/__init__.py
   from .text_to_data_dock import NewComponent
   
   __all__ = [
       'ComponentJ', 'ComponentK', 'ComponentI',
       'ComponentC', 'ComponentD', 'ComponentA',
       'ComponentB', 'ComponentF', 'ComponentG', 'ComponentH',
       'ComponentE', 'NewComponent'  # ← NEW module exported
   ]
   ```

3. **Menu Item Created and Connected**:
   ```python
   # In _build_menu() or similar
   m_tools = bar.addMenu(tr("menu.tools"))
   
   # Create QAction
   self.act_open_new_component = QAction(tr("menu.tools.text_to_data"), self)
   
   # Add to menu
   m_tools.addAction(self.act_open_new_component)
   
   # Connect signal
   self.act_open_new_component.triggered.connect(lambda: self.dock_new_component.show())
   ```

4. **Dock Initialized in __init__() or setup method**:
   ```python
   # In __init__() of MainWindow
   def __init__(self):
       super().__init__()
       # ... other docks ...
       self._open_new_component()  # ← Initialize dock
   
   def _open_new_component(self):
       self.dock_new_component = NewComponent(self)
       self.dock_new_component.open_in_other_component_requested.connect(self._load_data_from_source)
       self.addDockWidget(Qt.RightDockWidgetArea, self.dock_new_component)
       self.dock_new_component.hide()
   ```

5. **Signals Connected** (if applicable):
   ```python
   # Connect custom signals
   self.dock_new_component.open_in_other_component_requested.connect(self._load_data_from_source)
   
   def _load_data_from_source(self, data_str: str):
       """Callback to open DATA in editor"""
       if not hasattr(self, 'component_viewer'):
           self._open_component()
       self.component_viewer.load_data_string(data_str)
       self.component_viewer.show()
   ```

6. **i18n Translations Added**:
   ```data
   // src/i18n/en.data
   {
     "menu.tools.text_to_data": "Text to DATA Converter"
   }
   
   // src/i18n/pt_BR.data
   {
     "menu.tools.text_to_data": "Conversor de Texto para DATA"
   }
   ```

**GUI Integration Test Checklist**:
- ✅ **Menu accessible**: Verify if item appears in Tools menu
- ✅ **Dock opens**: Clicking the menu should open the dock correctly
- ✅ **Basic functionality**: Test simple conversion
- ✅ **Signals work**: Test integration with other components (e.g., Open in Editor)
- ✅ **No console errors**: There should be no ImportError, AttributeError, etc.
- ✅ **Translation working**: Menu in PT-BR should show translated text

**Part B - GUI Code Quality Review (9 Criteria)**:

During GUI verification, simultaneously apply the following criteria:

1. **❌ Omission** - Verify if GUI is complete:
   - [ ] All necessary widgets/controls implemented?
   - [ ] Error handling in handlers (e.g., FileNotFoundError)?
   - [ ] Resource cleanup (close files, disconnect signals)?
   - [ ] Visual feedback for long operations (QProgressBar, busy cursor)?

2. **🤔 Ambiguity** - GUI should be clear:
   - [ ] Descriptive and clear labels?
   - [ ] Informative tooltips on controls?
   - [ ] Descriptive error messages (QMessageBox)?
   - [ ] Intuitive method names (_on_button_clicked vs _handle)?

3. **❗ Incorrect Fact** - Correct GUI logic:
   - [ ] Signals connected to correct slots?
   - [ ] Correct layouts (QVBoxLayout, QHBoxLayout, QSplitter)?
   - [ ] Enable/disable controls according to state?
   - [ ] Correct input validation (QValidator)?

4. **♻️ Redundancy** - Avoid repetition in GUI:
   - [ ] Widgets created only once?
   - [ ] Validations centralized (not duplicated)?
   - [ ] Initialization code not repeated?

5. **⚠️ Inconsistency** - Consistent GUI pattern:
   - [ ] Uniform naming (ed_ for QLineEdit, btn_ for QPushButton)?
   - [ ] Consistent message style?
   - [ ] Consistent layout spacing/margin?

6. **🔗 Lack of Integration** - GUI connected:
   - [ ] Dock added to MainWindow?
   - [ ] Menu item connected to dock.show()?
   - [ ] Custom signals connected?
   - [ ] Import present in app.py?

7. **🧩 Lower Cohesion** - Focused dock:
   - [ ] Dock only handles UI (not business logic)?
   - [ ] Complex logic in separate module?
   - [ ] Each method has a single responsibility?

8. **🔗 Higher Coupling** - Decoupled GUI:
   - [ ] Dock does not depend on internal implementation of other docks?
   - [ ] Communication via signals/slots (not direct calls)?
   - [ ] GUI testable independently (mock business logic)?

9. **🗑️ Extraneous Information** - Clean code:
   - [ ] No forgotten print() debugs?
   - [ ] No unresolved TODOs?
   - [ ] No unused widgets?

**GUI Review Example Applied**:
```python
# ❌ BEFORE - Omission, Ambiguity, Higher Coupling
class NewComponent(QDockWidget):
    def __init__(self):
        self.btn = QPushButton("Convert")  # Vague label
        self.btn.clicked.connect(self.convert)  # No error handling
    
    def convert(self):
        data = open(self.ed_file.text()).read()  # No validation, no closing
        data_str = my_convert(data)  # Business logic in GUI
        print(data_str)  # Forgotten debug

# ✅ AFTER - Complete, Clear, Decoupled
class NewComponent(BaseDock):
    """Text to DATA Converter dock widget."""
    
    # Signal for communication
    open_in_other_component_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_widgets()
        self._setup_layout()
        self._connect_signals()
        
        # Controller for business logic
        self._converter = TextToJsonConverter()
    
    def _create_widgets(self):
        """Create UI widgets."""
        self.ed_file = QLineEdit()
        self.ed_file.setPlaceholderText("Enter file path or paste text")
        
        self.btn_convert = QPushButton("Convert to DATA")
        self.btn_convert.setToolTip("Convert text to DATA format")
        
        self.btn_open_component = QPushButton("Open in Editor")
        self.btn_open_component.setEnabled(False)  # Disabled until converted
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.btn_convert.clicked.connect(self._on_convert_clicked)
        self.btn_open_component.clicked.connect(self._on_open_component_clicked)
    
    def _on_convert_clicked(self):
        """Handle convert button click."""
        file_path = self.ed_file.text().strip()
        
        if not file_path:
            QMessageBox.warning(self, "Empty Input", "Please enter a file path or text.")
            return
        
        try:
            # Read file with context manager (ensures closing)
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                text = file_path  # Treat as direct text
            
            # Convert using controller (decoupling)
            self._data_result = self._converter.convert(text)
            
            # Visual feedback
            QMessageBox.information(self, "Success", "Conversion successful!")
            self.btn_open_component.setEnabled(True)
        
        except FileNotFoundError:
            QMessageBox.critical(self, "File Not Found", f"File not found: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Conversion Error", f"Error: {str(e)}")
    
    def _on_open_component_clicked(self):
        """Handle open in editor button click."""
        if hasattr(self, '_data_result'):
            self.open_in_other_component_requested.emit(self._data_result)  # Signal
```

**Recommended GUI Tools**:
```bash
# Check unused Qt imports
grep -r "from PySide6" src/gui/ | cut -d: -f2 | sort | uniq

# Check unconnected signals (manual review)
grep -r "Signal(" src/gui/ | grep -v ".connect("

# Check unused widgets (manual review)
grep -r "self\.\w\+ = Q" src/gui/

# Check debug prints (CRITICAL)
grep -r "print(" src/gui/ --exclude="*_test.py"
```

**Questions to Validate GUI**:
1. ❓ "Is the dock fully integrated into the menu and MainWindow?"
2. ❓ "Are all signals connected and working?"
3. ❓ "Is there error handling with visual feedback (QMessageBox)?"
4. ❓ "Is business logic separated from GUI code?"
5. ❓ "Is the code free of debug prints and unresolved TODOs?"
6. ❓ "Are labels, tooltips, and messages clear and descriptive?"
7. ❓ "Are resources (files, connections) closed correctly?"

**Real Example (Task Example - Text to DATA Converter)**:
```python
✅ Import: from .gui import NewComponent
✅ Export: __all__ = [..., 'NewComponent']
✅ Menu: self.act_open_new_component.triggered.connect(lambda: self.dock_new_component.show())
✅ Init: self._open_new_component() called in __init__()
✅ Signal: open_in_other_component_requested.connect(self._load_data_from_source)
✅ i18n: EN "Text to DATA Converter", PT-BR "Conversor de Texto para DATA"
✅ Review: No debug prints, error handling OK, logic decoupled
✅ Test: Menu opens dock, conversion works, signal to editor OK
```

---

### 9️⃣ **Verify Integration with Main Program**
- **CRITICAL**: After implementing CLI and GUI, **verify that everything is integrated and working in the context of the main program**
- It's not enough to have isolated working code; it needs to be **accessible and operational** in the application
- Verify complete flow: menu → action → result
- Manually test functionality in the running program

**Complete Integration Checklist**:

1. **GUI Full Flow Test**:
   ```bash
   # Start application
   python -m app --gui
   
   # Manually test:
   [ ] Menu item appears correctly?
   [ ] Clicking the menu opens the dock?
   [ ] Dock displays all controls?
   [ ] Basic functionality works (conversion, search, etc.)?
   [ ] Signals between components work (e.g., "Open in Editor")?
   [ ] Error messages appear when appropriate?
   [ ] i18n translation works (change language and verify)?
   ```

2. **CLI Full Flow Test**:
   ```bash
   # Test help
   python -m app convert --help
   
   # Test functionality
   python -m app convert test.txt --pretty -o output.data
   
   # Test pipes
   echo "name: John" | python -m app convert -
   
   # Verify:
   [ ] Help text appears?
   [ ] Arguments are recognized?
   [ ] Functionality executes without errors?
   [ ] Output is correct?
   [ ] Correct exit codes (0=success, 1=error)?
   ```

3. **Inter-component Integration Test**:
   ```bash
   # Example: Convert text → Open in editor
   [ ] Clicking "Open in Editor" in the Text to DATA Converter opens the Editor?
   [ ] DATA is loaded correctly in the Editor?
   [ ] Editor can save the result?
   
   # Example: Search → Open file
   [ ] Clicking a search result opens the correct file?
   [ ] Cursor position goes to the correct line?
   ```

4. **Robustness Test**:
   ```bash
   # Error scenarios
   [ ] File not found displays clear message?
   [ ] Invalid input is handled gracefully?
   [ ] Canceled operation doesn't leave inconsistent state?
   [ ] Resources are released correctly (files closed, memory)?
   ```

5. **Performance Test** (if applicable):
   ```bash
   # Large files
   [ ] Processes files >10MB without freezing?
   [ ] Interface remains responsive during long operation?
   [ ] Progress bar/visual feedback works?
   [ ] Cancellation works during long operation?
   ```

**Real Example of Integration Problem**:
```python
# ❌ PROBLEM FOUND DURING INTEGRATION:
# Task Example - Text to DATA Converter CLI
# Problem: Extractor() was being called without 3 mandatory parameters

# BEFORE (broke during integration):
def main():
    if args.command == 'convert':
        extractor = Extractor()  # ❌ TypeError: missing 3 required arguments

# AFTER (fixed):
def main():
    if args.command == 'convert':
        extractor = Extractor(
            avoid_keys="",
            avoid_keys_parameter="equals",
            with_quotation_marks=False
        )  # ✅ Works!
```

**Questions to Validate Integration**:
1. ❓ "Can the end user easily access the functionality?"
2. ❓ "Do all usage flows work end-to-end?"
3. ❓ "Are there any errors or warnings in the console during normal use?"
4. ❓ "Is the functionality consistent with the rest of the application?"
5. ❓ "Is the documentation (help text, tooltips) clear and correct?"

**Why is this step critical?**:
- ✅ Detects problems that unit tests don't catch
- ✅ Validates real user experience
- ✅ Ensures all work is truly usable
- ✅ Avoids surprises after commit (tested code ≠ integrated code)

---

### 🔟 **Run Tests**
- **Mandatory**: Unit tests for each public function
- **Goal**: 100% coverage of implemented functionalities
- **Tools**: `unittest` (native) or `pytest`
- **CRITICAL**: Test the system **after integration** (GUI + CLI integrated)
- **IMPORTANT**: Execute **AFTER** code review (Steps 7 and 8)

**Test Categories**:
1. **Happy Path**: Normal use cases
2. **Edge Cases**: Empty values, None, long strings
3. **Error Handling**: Expected exceptions
4. **Integration**: Complete flow (including GUI/CLI integration)
5. **Quality Validation**: Tests that validate the absence of the 9 problems from Steps 7 and 8

**Task Example**:
```python
✅ test_extract_from_dict_simple()
✅ test_extract_from_obj_type()
✅ test_simple_substitution_same_value()
✅ test_different_values_no_substitution()
✅ test_apply_substitutions_tsx_file()
✅ test_update_multiple_files()
# ... 12 tests in total (100% passing)
```

**Why test AFTER integration and review?**:
- Ensures tests validate the **integrated system**, not isolated components
- Detects integration problems during testing
- Validates that features truly work in the application context
- Avoids false positives (tests pass but feature is not accessible)
- Code has already been reviewed, so tests validate **quality code**

**Why?**: Ensure quality, prevent regressions, facilitate future maintenance.

---

#### 🛡️ **Step 9.1 - Security in Tests (CRITICAL)**

**Problem Identified** (Task Example - 01/12/2025):
- GUI tests froze in an **infinite loop** for >1 hour without timeout
- No automatic deadlock or freeze detection
- Tests waited for non-existent X11 display (headless environment)

**Mandatory Solutions**:

1. **⏱️ Mandatory Maximum Timeout** (30s per test):
   ```bash
   # ALWAYS use timeout in tests
   pytest tests/test_*.py --timeout=30 -v
   
   # Install pytest-timeout plugin if necessary
   pip install pytest-timeout
   ```

2. **🚨 Infinite Loop Detection** (warning in 10s):
   ```bash
   # More aggressive timeout to detect loops
   timeout 10s pytest tests/test_specific.py || echo "⚠️ TIMEOUT: Possible infinite loop detected!"
   ```

3. **🖥️ Mandatory Headless Environment** (GUI tests without display):
   ```bash
   # Use Qt offscreen platform
   QT_QPA_PLATFORM=offscreen pytest tests/test_gui_*.py -v --timeout=30
   
   # OR use pytest-xvfb for virtual X11 environment
   pip install pytest-xvfb
   pytest tests/test_gui_*.py --xvfb-backend xvfb --timeout=30
   ```

4. **✅ Mandatory Dry-Run** (before executing):
   ```bash
   # 1. Check syntax
   python -m py_compile tests/test_*.py && echo "✅ Valid syntax"
   
   # 2. Check imports
   python -c "from tests.test_module import *; print('✅ Imports OK')"
   
   # 3. List tests without executing
   pytest tests/test_*.py --collect-only
   ```

5. **⏲️ Time Monitoring** (record duration):
   ```bash
   # Measure total time and save log
   time pytest tests/test_*.py -v --timeout=30 | tee test_output.log
   
   # Use pytest-benchmark for metrics
   pytest tests/test_*.py --benchmark-only --timeout=30
   ```

**Why?**: Prevent infinite freezes, protect development time, ensure reliable tests.

---

### 🔟.5️⃣ **Profiling and Optimization** [OPTIONAL]

**When to Use**: Critical feature is **slow** (>1s for user).

**Tools**:
```bash
# CPU profiling
python -m cProfile -s cumulative app.py > profile.txt

# Memory profiling
pip install memory_profiler
python -m memory_profiler app.py
```

**Example**:
```python
# ❌ SLOW - O(n²) 5.2s for 1000 tasks
def find_duplicates_slow(tasks):
    for i, t1 in enumerate(tasks):
        for j, t2 in enumerate(tasks):
            if i != j and t1.title == t2.title:
                # duplicated

# ✅ FAST - O(n) 0.02s (260x faster)
def find_duplicates_fast(tasks):
    seen = {}
    for task in tasks:
        if task.title in seen:
            # duplicated
        seen[task.title] = task
```

**When to Stop**: Optimizing is only worthwhile if **time saved × frequency** > 1min/day.

📘 **Details**: See `PROTOCOLO_SIMPLICIDADE_2.md` - Step 10.5

---

### 🔟.6️⃣ **CI/CD Quality Gates** ⭐ [MANDATORY]

> **CRITICAL FOR PRODUCTION**: This step is **MANDATORY** in Simplicity 3.

**Why mandatory**:
- ✅ **Memory fails**: You forget to run tests manually
- ✅ **24/7 Automation**: CI validates **every** commit automatically
- ✅ **Confidence**: You know broken code won't go to production
- ✅ **Fast**: Feedback in minutes (not hours debugging)

**Pre-commit Hooks** (local validation):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: check-yaml
      - id: check-data
  
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88']
  
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        args: ['tests/', '-v']
```

```bash
# Install
pip install pre-commit
pre-commit install

# Now every `git commit` executes validations automatically
# If it fails, commit is BLOCKED until corrected
```

**GitHub Actions** (CI pipeline):

```yaml
# .github/workflows/ci.yml
name: CI Quality Gates

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install deps
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8 black bandit
    
    - name: Black formatting
      run: black --check .
    
    - name: Flake8 linting
      run: flake8 . --max-line-length=88
    
    - name: Bandit security
      run: bandit -r . -ll
    
    - name: Tests + Coverage
      run: |
        pytest --cov=. --cov-report=term
        coverage report --fail-under=80
      # Fails if coverage < 80%
```

**GitLab CI**:

```yaml
# .gitlab-ci.yml
stages:
  - test

test:
  image: python:3.11
  script:
    - pip install -r requirements.txt pytest pytest-cov
    - pytest --cov=. --cov-report=term
    - coverage report --fail-under=80
```

**Badge in README** (visual status):

```markdown
[![CI](https://github.com/user/repo/workflows/CI/badge.svg)](https://github.com/user/repo/actions)
[![Coverage](https://codecov.io/gh/user/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/user/repo)
```

**Setup Time**: ~30 minutes (once). Then automatic.

📘 **Complete configurations**: See `PROTOCOLO_SIMPLICIDADE_2.md` - Step 10.6

---

### 1️⃣1️⃣ **Organize Project Root Folder**
- ✅ Imports validated (module loads without errors)
- 📝 **Documented limitation**: GUI tests require unconﬁgured headless environment

---

#### 🔬 **Step 9.2 - Tests in Threads/Processes with Monitoring (ADVANCED)**

**Objective**: Full control over test execution with the possibility to **interrupt**, **monitor**, and **log** progress in real-time.

**When to Use**:
- GUI tests that may freeze
- Long-duration tests (>1 min)
- Tests with external dependencies (network, database)
- Need for real-time logging
- Need for manual cancellation during execution

**Implementation with `multiprocessing.Process`**:

```python
# tests/test_runner_monitored.py
import multiprocessing as mp
import time
import sys
from queue import Empty

def run_tests_in_process(test_module: str, queue: mp.Queue, timeout: int = 30):
    """
    Executes tests in a separate process with logging to a queue.
    
    Args:
        test_module: Test module (e.g., 'tests.test_file_list_dock')
        queue: Queue for progress communication
        timeout: Timeout in seconds
    """
    try:
        import pytest
        
        # Configure real-time logging
        class QueueReporter:
            def __init__(self, queue):
                self.queue = queue
            
            def pytest_runtest_logreport(self, report):
                """pytest hook to capture results."""
                if report.when == 'call':
                    status = '✅ PASS' if report.passed else '❌ FAIL'
                    self.queue.put({
                        'type': 'test_result',
                        'test': report.nodeid,
                        'status': status,
                        'duration': report.duration
                    })
        
        # Execute pytest with custom reporter
        queue.put({'type': 'info', 'msg': f'Starting tests: {test_module}'})
        
        result = pytest.main([
            test_module,
            '-v',
            f'--timeout={timeout}',
            '--tb=short',
            '-p', 'no:cacheprovider'  # Disable cache
        ])
        
        queue.put({'type': 'info', 'msg': f'Tests finished. Exit code: {result}'})
        queue.put({'type': 'exit', 'code': result})
        
    except Exception as e:
        queue.put({'type': 'error', 'msg': str(e)})
        queue.put({'type': 'exit', 'code': 1})

def monitor_test_execution(test_module: str, max_timeout: int = 300):
    """
    Monitors test execution with full control.
    
    Args:
        test_module: Test module
        max_timeout: Maximum timeout in seconds (default: 5 min)
    
    Returns:
        dict: Execution result with statistics
    """
    queue = mp.Queue()
    process = mp.Process(
        target=run_tests_in_process,
        args=(test_module, queue, 30)
    )
    
    print(f"🚀 Starting tests: {test_module}")
    print(f"⏱️  Maximum timeout: {max_timeout}s")
    print(f"📊 Active monitoring. Press Ctrl+C to cancel.\n")
    
    process.start()
    start_time = time.time()
    results = {'passed': 0, 'failed': 0, 'tests': []}
    
    try:
        while process.is_alive():
            elapsed = time.time() - start_time
            
            # Check global timeout
            if elapsed > max_timeout:
                print(f"\n⚠️  GLOBAL TIMEOUT ({max_timeout}s exceeded)")
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()
                return {'status': 'timeout', 'elapsed': elapsed, 'results': results}
            
            # Read messages from the queue (non-blocking)
            try:
                msg = queue.get(timeout=0.5)
                
                if msg['type'] == 'test_result':
                    print(f"  {msg['status']} {msg['test']} ({msg['duration']:.2f}s)")
                    results['tests'].append(msg)
                    if '✅' in msg['status']:
                        results['passed'] += 1
                    else:
                        results['failed'] += 1
                
                elif msg['type'] == 'info':
                    print(f"ℹ️  {msg['msg']}")
                
                elif msg['type'] == 'error':
                    print(f"❌ ERROR: {msg['msg']}")
                
                elif msg['type'] == 'exit':
                    process.join(timeout=2)
                    elapsed = time.time() - start_time
                    print(f"\n✅ Tests finished in {elapsed:.2f}s")
                    return {
                        'status': 'completed',
                        'exit_code': msg['code'],
                        'elapsed': elapsed,
                        'results': results
                    }
            
            except Empty:
                # No message, continue monitoring
                pass
            
            # Show progress every 10s
            if int(elapsed) % 10 == 0 and int(elapsed) > 0:
                print(f"⏳ Executing... {int(elapsed)}s ({results['passed']} passed, {results['failed']} failed)")
    
    except KeyboardInterrupt:
        print("\n⚠️  Manual cancellation (Ctrl+C)")
        process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            process.kill()
        elapsed = time.time() - start_time
        return {'status': 'cancelled', 'elapsed': elapsed, 'results': results}
    
    finally:
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)

# Example usage:
if __name__ == '__main__':
    result = monitor_test_execution('tests/test_advanced_file_search.py', max_timeout=300)
    
    print(f"\n{'='*60}")
    print(f"Status: {result['status']}")
    print(f"Time: {result['elapsed']:.2f}s")
    print(f"Passed: {result['results']['passed']}")
    print(f"Failed: {result['results']['failed']}")
    print(f"{'='*60}")
```

**Practical Use**:

```bash
# 1. Create monitored runner
cat > tests/run_tests_monitored.py << 'EOF'
# [code above]
EOF

# 2. Execute with monitoring
python tests/run_tests_monitored.py

# 3. Cancel at any time (Ctrl+C)
# The process will be gracefully terminated
```

**Advantages**:
- ✅ **Full control**: Can cancel tests at any time
- ✅ **Real-time logging**: See progress of each test
- ✅ **Global + individual timeout**: Double protection
- ✅ **Statistics**: Pass/fail in real-time
- ✅ **Isolation**: Tests run in a separate process (don't freeze the terminal)
- ✅ **Guaranteed cleanup**: `terminate()` + forced `kill()` if necessary

**Optional Configurations**:

1. **File Logging** (in addition to stdout):
   ```python
   # Add to run_tests_in_process:
   import logging
   logging.basicConfig(
       filename=f'test_{time.time()}.log',
       level=logging.INFO,
       format='%(asctime)s - %(message)s'
   )
   ```

2. **Sound Notification** (upon completion):
   ```python
   import os
   # At the end of monitor_test_execution:
   os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga')
   ```

3. **CI/CD Integration**:
   ```python
   # Return correct exit code:
   sys.exit(0 if result['status'] == 'completed' and result['results']['failed'] == 0 else 1)
   ```

**Additional Checklist (Step 9.2 - Optional)**:
```
[ ] Create test_runner_monitored.py with multiprocessing
[ ] Define global timeout (default: 5 min)
[ ] Define individual test timeout (default: 30s)
[ ] Implement real-time logging (Queue)
[ ] Test manual cancellation (Ctrl+C)
[ ] Verify process cleanup (ps aux | grep pytest)
```

**When NOT to use**:
- Simple and fast tests (<10s total)
- Tests without GUI (pure backend)
- CI/CD with native timeout configured
- First execution of tests (unnecessary overhead)

---

### 1️⃣1️⃣ **Organize Project Root Folder**
- **CRITICAL**: Before documentation and commit, **organize the root folder recursively**
- **MANDATORY**: Files must be organized in the correct folders before commit
- Remove temporary files, unnecessary backups
- Verify that all files are in their correct places
- Clear cache and generated files (`__pycache__`, `.pyc`)
- Ensure `.gitignore` is updated

**Organization Checklist**:
1. **Removal of Temporary Files**:
   ```bash
   # Remove old backups
   rm -f *.backup_* *.bak *~
   
   # Clear Python cache
   find . -type d -name "__pycache__" -exec rm -rf {} +
   find . -type f -name "*.pyc" -delete
   find . -type f -name "*.pyo" -delete
   ```

2. **Directory Structure Verification (MANDATORY)**:
   - `src/` - source code
   - `tests/` - **ALL test files** (mandatory)
   - `docs/` - **ALL documents and markdown files** (mandatory)
   - Organized root files (README, setup.py, etc.)

3. **Mandatory Recursive Organization**:
   
   **⚠️ FUNDAMENTAL RULE**: 
   > Before commit, files must be organized in folders recursively. This is **mandatory** to keep the environment clean and organized.

   **Specific Rules by File Type**:
   
   a) **Test Files** → `tests/`
      - ✅ `test_*.py`, `*_test.py` → `tests/`
      - ✅ Test structure should mirror code structure
      - ✅ Example: `tests/unit/`, `tests/integration/`, `tests/fixtures/`
   
   b) **Documents and Markdown** → `docs/`
      - ✅ All `.md` files (except root README.md) → `docs/`
      - ✅ Documentation files → `docs/`
      - ✅ **Recursive organization within `docs/`**:
        - `docs/api/` - API documentation
        - `docs/tutorials/` - Tutorials
        - `docs/architecture/` - Architectural decisions
        - `docs/user-guide/` - User guides
        - `docs/dev-guide/` - Development guides
        - `docs/decisions/` - Decision notes (see Step 11.5)
      - ✅ Create subfolders that identify file context
   
   c) **Source Code** → `src/` or appropriate folder
      - ✅ Organize by modules/features
      - ✅ Example: `src/core/`, `src/utils/`, `src/api/`

**Complete Example**:
```bash
# BEFORE (disorganized):
├── src/
├── test_utils.py              ❌ test outside tests/
├── API_DOCS.md                ❌ doc outside docs/
├── tutorial.md                ❌ doc outside docs/
├── apply_v2913_patches.py     ❌ temporary
├── test_temp.py               ❌ temporary test
├── backup_old/                ❌ old backup
├── __pycache__/               ❌ cache
└── file.py.backup_v2913       ❌ unnecessary backup

# AFTER (recursively organized):
├── src/
│   ├── core/
│   └── utils/
├── tests/                     ✅ ALL tests
│   ├── unit/
│   │   └── test_utils.py     ✅ test moved
│   └── integration/
├── docs/                      ✅ ALL documents
│   ├── api/
│   │   └── API_DOCS.md       ✅ doc moved
│   ├── tutorials/
│   │   └── tutorial.md       ✅ doc moved
│   └── decisions/             ✅ Decision notes
└── README.md                  ✅ root README kept
```

**Why?**: Keep repository clean, avoid committing junk, facilitate navigation, professionalism, recursive organization ensures scalability. Document the **clean** and **organized** state of the project.

---

### 1️⃣1️⃣.5️⃣ **Decision Notes** [OPTIONAL]

**When to Use**: An important/non-obvious decision was made and you might forget the "why" later.

**What to document**:
- ✅ Choice of important library/framework
- ✅ Significant trade-off (performance vs simplicity)
- ✅ Decision NOT to do something (with rationale)
- ✅ Chosen architecture/pattern

**Simplified Format** (ADR light):

```markdown
# Decision: Use PyQt6 instead of Tkinter

**Date**: 2025-01-15
**Status**: ✅ Accepted

**Context**: Need GUI with professional dock widgets.

**Decision**: Chosen PyQt6.

**Why**:
- ✅ Native QDockWidget (Tkinter doesn't have)
- ✅ Styling with QSS (CSS-like)
- ✅ Excellent documentation

**Trade-offs**:
- ❌ GPL license (OK, project is open-source)
- ❌ Larger binary (~50MB vs ~5MB Tkinter)

**If it changes in the future**: Consider PySide6 (LGPL) if permissive license is needed.
```

**Where to store**:
```
docs/
├── decisions/
│   ├── 001-pyqt6-choice.md
│   ├── 002-data-storage.md
│   └── README.md
```

**When NOT to document**:
- ❌ Trivial decisions (naming, formatting)
- ❌ Obvious/conventional choices
- ❌ Self-explanatory code

**Time**: 5-10 minutes per important decision.

📘 **Formal ADR with template**: See `PROTOCOLO_SIMPLICIDADE_2.md` - Step 11.5

---

### 1️⃣2️⃣ **Fill New Documentation**
- **Update tasks/requirements file**: Mark tasks as `[X]` complete
- **Create SPECIFICATIONS.md**: Detailed document for the version
- **Update statistics**: Project completion percentage
- **🤖 [OPTIONAL] Manage AI task recommendations**

---

### ⚠️ **MANDATORY REQUIREMENT: Complete Documentation of All AI Implementations**

> **CRITICAL FOR AIs**: Everything that the artificial intelligence does in the project, in each implementation cycle, in each code, each implemented functionality, **MUST BE DOCUMENTED IN THE `docs/` FOLDER AS A MANDATORY REQUIREMENT** to mark new functionalities and new behaviors.

**📖 See SIMPLICITY_PROTOCOL_1.md. - Step 12** for complete documentation requirements, templates, and validation checklists.

#### **👤 Solo Developer in Production - Specific Documentation (Simplicity 3)**

In addition to base documentation requirements, Simplicity 3 adds:

**Critical Documentation for Solo in Production**:
- ✅ **OWASP Security Checklist** - MANDATORY in `docs/SECURITY.md`
- ✅ **Rollback Plans** - MANDATORY in `docs/ROLLBACK.md` for critical features
- ✅ **Decision Notes** - Pragmatic ADRs (simplified) in `docs/DECISIONS.md`
- ✅ **CI/CD Configuration** - Documented setup and quality gates
- ✅ **"Why I Did This" Notes** - Important for remembering context after 3-6 months

**📂 Solo Production Documentation Structure**:

```
docs/
├── REQUIREMENTS.md
├── vX.Y.Z-SPECIFICATIONS.md
├── CHANGELOG.md
├── ARCHITECTURE.md
├── DECISIONS.md             # Pragmatic decision notes (simplified ADRs)
├── SECURITY.md              # OWASP checklist (MANDATORY)
├── ROLLBACK.md              # Rollback plans (MANDATORY)
└── [feature]-GUIDE.md
```

**🔍 Additional Validation for Solo Production**:

Before commit, AI must also verify:
- [ ] ✅ **OWASP security checklist complete in SECURITY.md (MANDATORY)**
- [ ] ✅ **Rollback plan documented for critical features (MANDATORY)**
- [ ] ✅ Decision notes created for important choices (DECISIONS.md)
- [ ] ✅ CI/CD configuration documented
- [ ] ✅ Context notes for future self (why specific solutions were chosen)

**Rationale for Solo Developer**: 
- **Your Memory Fades**: After 3-6 months, you'll forget why you made specific decisions
- **Production Emergencies**: Complete documentation speeds up debugging at 3AM
- **Security is Your Responsibility**: No team to catch vulnerabilities - documentation is critical
- **Rollback Must Be Fast**: When things break in production, you need documented recovery plans
- **Future Handoff**: If you grow or sell, documentation enables smooth transition
- **Your "Second Brain"**: Documentation is your safety net as a solo developer

---

**📋 TASKS.md Management**:

**General Rule**:
- If a tasks/requirements file exists (e.g., `TASKS.md`, `TODO.md`, `requirements.md`):
  - ✅ **Mark tasks as complete** after implementation: `[ ]` → `[X]`
  - ✅ **Update statistics** (percentages, counters)
  - ✅ **Add completion notes** (date, version, brief description)
  - 🤖 **[OPTIONAL] Add new AI-recommended tasks** (see details in SIMPLICITY_PROTOCOL_1.md - Step 12)
  
- If a tasks/requirements file **DOES NOT exist**:
  - ❓ **Ask the user** for the file location/path
  - ❓ **Ask about next tasks and requirements** if no formal document
  - ❓ **Suggest creating** `TASKS.md` as the default file

---

### 📊 **Task Classification Legend (Simplicity 3 - Solo Developer)**

**Objective**: Standardize task classification and prioritization to facilitate AI organization when working alone in production.

**Note for Simplicity 3**: As a solo developer, you need **pragmatic and fast** classification that doesn't add unnecessary overhead. Classification should help make quick decisions without team bureaucracy.

#### **Task Status**

- 🔴 **Not Started** - Awaiting start, no work done
- 🟡 **In Progress** - Active development, work underway
- 🟢 **Done** - Implemented, tested, validated in CI/CD and completed
- 🔵 **Blocked** - Impeded by external dependency or technical issue

**Solo Tip**: Minimize 🔵 Blocked tasks. As you're alone, blockers are especially costly. If something's blocked, see if there's a temporary workaround or another task to advance.

#### **Task Complexity**

- 🟢 **Simple** (0-1h) - Low risk, few dependencies, clear scope
- 🟡 **Medium** (1-2h) - Medium risk, some integrations, may require additional tests
- 🔴 **Complex** (>2h) - High risk, many dependencies, open or ambiguous scope

**Solo Strategy**: Alternate complex tasks with simple ones. After solving a 🔴 complex task, do 2-3 🟢 simple ones to maintain momentum and motivation. Avoid accumulating only complex tasks in sprint.

#### **MoSCoW Prioritization**

- 🔴 **Must Have** - Critical for system functionality, release blocker
- 🟡 **Should Have** - Important but not blocking, can be postponed if needed
- 🟢 **Could Have** - Desirable if time permits, low priority
- ⚪ **Won't Have** (Later) - Explicitly out of current scope, for future versions

**Solo Tip**: Be strict with MoSCoW. The temptation to do everything is real when you're alone. Use ⚪ Won't Have generously to avoid feature creep.

#### **Integration with Decision Matrix (Optional)**

The Decision Matrix (Step 2.5) is **optional** in Simplicity 3, but useful when you have 10+ tasks to prioritize:

```markdown
## Sprint v2.5 - Solo Developer Backlog

### 🔴 MUST HAVE (Required for Release)

| Task | Status | Complex. | Score | Note |
|------|--------|----------|-------|------|
| #25 Security patch CVE-2024-1234 | 🔴 | 🟢 | 34.0 | Critical! Start today |
| #26 Rollback plan for deploy | 🔴 | 🟡 | 29.0 | Do before deploy |
| #27 Implement auto backup | 🔴 | 🟡 | 27.5 | Production requires |

**Decision**: Start with #25 (highest score + simplest). Then #26 and #27.
```

**When to use Decision Matrix**:
- ✅ When you have 10+ tasks and it's not obvious where to start
- ✅ When multiple tasks are "Must Have" and you need to break the tie
- ✅ When you want to justify decisions to yourself (or to client)
- ❌ When you have 1-5 obvious tasks (unnecessary overhead)

#### **Complete Simplicity 3 Example (Solo Developer)**

```markdown
# TASKS.md - Solo SaaS Project in Production

## 📊 Legend
- **Status**: 🔴 Not Started | 🟡 In Progress | 🟢 Done | 🔵 Blocked
- **Complexity**: 🟢 Simple (0-1h) | 🟡 Medium (1-2h) | 🔴 Complex (>2h)
- **MoSCoW**: 🔴 Must | 🟡 Should | 🟢 Could | ⚪ Won't

## 📊 Project Status
- **Current Version**: v3.2.1 in production
- **Progress**: 72% (29/40 planned features)
- **Active Users**: 1,245 (15% monthly growth)
- **Uptime**: 99.8% (last 30 days)
- **Next Release**: v3.3.0 (15 days)

## 🔴 MUST HAVE - Release v3.3.0

### High Priority (Critical)
- 🔴🟢 [ ] #88 Implement rate limiting (1h) ⭐ DO TODAY
  - **Reason**: Security, prevent API abuse
  - **CI/CD**: Include load tests
  - **Rollback Plan**: Feature flag toggle ready
  
- 🟡🟡 [ ] #89 Add health check endpoint (1.5h, 70% complete)
  - **Reason**: Uptime monitoring for Kubernetes
  - **Missing**: Integration tests + documentation
  - **Dependency**: Rate limiting must be working

### Medium Priority
- 🔵🔴 [ ] #90 Migrate database to PostgreSQL 14 (4h, BLOCKED)
  - **Blocker**: Awaiting maintenance window (next Sunday 3h-6h)
  - **Rollback Plan**: ✅ Current database snapshot created
  - **Fallback**: If it fails, stay on PG 12 for 1 more month

## 🟡 SHOULD HAVE - Release v3.4.0 (backlog)
- 🔴🟡 [ ] #91 Metrics dashboard (2h)
- 🔴🟢 [ ] #92 Improve error messages (0.5h)

## 🟢 COULD HAVE - Future Backlog
- 🔴🟡 [ ] #93 Dark mode (1.5h, RICE=180 - good priority)
- 🔴🔴 [ ] #94 Slack integration (3h)

## ⚪ WON'T HAVE - Don't do now
- [ ] #95 Native mobile app version (100h+, too much effort)
  - **Alternative**: PWA already works well on mobile
- [ ] #96 Multi-tenancy (80h+, high complexity)
  - **Reason**: Only 1 client for now, not justified

---

## 🤖 AI Recommendations (3/30 used)

### 🔴 MUST HAVE Suggested
- 🔴🟢 [ ] **[AI-001]** Add structured logging (1h)
  - **Reason**: Facilitate production incident debugging
  - **Integration**: Use existing library (loguru)

---

## 📝 Decision Notes (Simplified ADR)

**#90 - Why PostgreSQL 14?**
- Performance: 20% faster in complex queries (internal benchmark)
- Security: Critical security patches not backported to PG 12
- Support: PG 12 EOL in Nov/2024 (6 months)
- **Decision**: Migrate now with robust rollback plan

---

**Next review**: Monday (review progress, adjust priorities)
```

#### **Recommendations for AI Working with Solo Developer**

**When classifying tasks for solo developer (Simplicity 3), AI should**:

1. ✅ **Prioritize simple tasks first** - Solo dev needs quick wins for momentum
2. ✅ **Avoid blocker accumulation** - Suggest workarounds or alternative tasks
3. ✅ **Balance complexity** - Alternate difficult tasks with easy ones
4. ✅ **Consider energy/motivation** - Friday afternoon? Simple tasks. Monday morning? Complex tasks
5. ✅ **Document important decisions** - Solo dev forgets context after 3 months
6. ✅ **Be strict with "Won't Have"** - Protect against feature creep
7. ✅ **Automate what's repetitive** - Solo dev doesn't have time for manual tasks
8. ✅ **Prioritize security and CI/CD** - Without team to review, automation is essential
9. ✅ **Suggest rollback plans** - Solo dev doesn't have team to help if something goes wrong
10. ✅ **Keep classification pragmatic** - Don't add process overhead

**Simplicity 3 vs 2 Differences**:
- **S3**: Classification should be **fast** (don't waste time on elaborate scoring)
- **S3**: Prioritize **automation** over manual process (CI/CD, automatic tests)
- **S3**: **Rollback plans mandatory** (no team to help in incidents)
- **S3**: Decision Matrix **optional** (only when really necessary, not overhead)
- **S3**: AI recommendations accepted **directly** (no team consensus needed)

**Simplicity 3 vs 1 Differences**:
- **S3**: Adds **Security Checklist** mandatory (production requires)
- **S3**: Adds **CI/CD Quality Gates** mandatory (automation essential)
- **S3**: Adds **Rollback Plans** mandatory (deployment safety)
- **S3**: Maintains S1 classification, but focused on **critical production**

---

**🤖 AI Task Recommendations (Solo Developer)**:
For solo developers (Simplicity 3), AI recommendations are especially valuable as there's no team for brainstorming. AI acts as a "second brain" suggesting improvements and opportunities. Since you're working alone, you have autonomy to quickly accept/reject recommendations without needing team consensus.

📘 **Complete details of recommendation functionality**: See `SIMPLICITY_PROTOCOL_1.md` - Step 12 - Section "AI Task Recommendations"

**📁 TASKS.md File Location**:
- **Default preference**: The `TASKS.md` file, when created, should be placed in `docs/TASKS.md`
- **Create docs/ folder**: If the `docs/` folder does not exist in the project, it should be created automatically
- **Flexibility**: The user or programmer can choose to place it in another location if preferred
- **Creation example**:
  ```bash
  # Create docs folder if it doesn't exist
  mkdir -p docs
  
  # Create or update TASKS.md
  echo "# Tasks" > docs/TASKS.md
  ```

**Example of Marking (REQUIREMENTS.md)**:
```markdown
## 🟢 COULD HAVE (Low Priority)

### ✅ Completed Tasks

#### Task Example - Integrated File Editor (vX.Y.Z)
**Status**: ✅ Complete - 30/11/2025

**Objective**: Implement integrated text editor with scope differentiation by colors.

**Implementation**:
1. ✅ ComponentE with QTextEdit and syntax highlighting
2. ✅ Scope differentiation by colors (HTML tags, DATA keys, etc.)
3. ✅ Open/save files (.txt, .data, .html, .tsx, .py)
4. ✅ Integration with File menu → Open Editor

**Files Created**:
- `src/gui/editor_dock.py` (500+ lines)
- `tests/test_editor_dock.py` (15 tests)

### 🔨 Pending Tasks
- **[]** Next unimplement task...
```

**Minimum Recommended Structure**:
```markdown
# Project - Tasks

## Categories
- MUST HAVE: [X/Y complete] (Z%)
- SHOULD HAVE: [X/Y complete] (Z%)
- COULD HAVE: [X/Y complete] (Z%)
- WOULD HAVE: [X/Y complete] (Z%)

## Statistics
- **TOTAL**: [X/Y complete] (Z%)
```

**Version Documentation Structure**:
```markdown
# MyProject v2.9.X - [Descriptive Name]

**Date**: DD/MM/YYYY
**Sprint**: X tasks in Y hours
**Methodology**: Simplicity 1 Protocol

## 📋 Sprint Objectives
- Task #X: [description]
- Task #Y: [description]

## 🎯 Implemented Tasks
### Task #X: [Name]
- **Problem**: [description of original problem]
- **Solution**: [how it was solved]
- **Modified Files**: [list]
- **Tests**: [quantity and status]

## ✅ Quality (Simplicity 1 Protocol)
- ✅ Modular Architecture
- ✅ Type Hints (100%)
- ✅ Complete Docstrings
- ✅ Error Handling
- ✅ Tests (X passing)
- ✅ Semantic Commits
- ✅ Complete Documentation
- ✅ Clean Code (PEP8)

## 📊 Statistics
- TOTAL: X% complete (Y/Z tasks)
- Commits: N pushed
```

---

### 1️⃣2️⃣.5️⃣ **Rollback Plans** ⭐ [MANDATORY]

> **CRITICAL FOR PRODUCTION**: This step is **MANDATORY** in Simplicity 3.

**Why mandatory**:
- ✅ **Production**: Bugs affect real users
- ✅ **Solo**: You are alone to resolve emergencies
- ✅ **Downtime**: Fast rollback minimizes impact
- ✅ **Confidence**: Deploy boldly knowing you can revert

**When to create a Rollback Plan**:
- ✅ Critical feature (payment, authentication, data)
- ✅ Change in data schema/migrations
- ✅ Public API alteration
- ✅ High-risk deployment

**Simplified Template**:

```markdown
# Rollback Plan - Task #XX: [Feature Name]

## Criteria for Rollback
Execute rollback IF:
- [ ] Error rate > 5% within 1h after deployment
- [ ] Users report data loss
- [ ] Frequent crashes (>5 reports)
- [ ] Performance worse than previous version (>2x slower)

## How to Revert (Step-by-Step)

### 1. Preparation (5min)
```bash
# Backup current state
cp data.db data.db.backup-$(date +%s)
cp app.log rollback-logs.txt
```

### 2. Code Rollback (5min)
```bash
# Revert to previous version
git checkout v1.9.5
# OR
pip install app==1.9.5 --force-reinstall
```

### 3. Restore Data (if necessary)
```bash
# Restore DATA/DB backup created during migration
cp data.data.backup data.data
```

### 4. Validate (5min)
```bash
# Smoke tests
app --version  # Should show v1.9.5
app test-basic-flow
```

## Total Rollback Time
~15-20 minutes (expected downtime)

## Backup Required
- ✅ Automatic backup created on deploy
- ✅ Git tag of previous version exists
- ❌ Does not depend on external services

## Data at Risk
- **High**: Data created after deployment (not in backup)
- **Low**: Existing data (preserved in backup)

**Mitigation**: Export new data before rollback.
```

**Alternative: Feature Flags** (better than rollback):

```python
# Disable feature remotely without redeploy
FEATURE_NEW_EXPORT = os.getenv("ENABLE_NEW_EXPORT", "false") == "true"

def export_data():
    if FEATURE_NEW_EXPORT:
        return new_export()  # New implementation
    else:
        return old_export()  # Safe fallback

# In case of problem: export ENABLE_NEW_EXPORT=false
# Users automatically revert to old version
```

**Quick Checklist**:
```markdown
- [ ] Rollback criteria defined (when to execute?)
- [ ] Rollback steps documented (how to revert?)
- [ ] Automated backup (data preserved?)
- [ ] Estimated rollback time (<30min?)
- [ ] Feature flag considered (better alternative?)
```

**Creation Time**: 10-15 minutes per critical feature.

📘 **Complete Rollback Plans**: See `PROTOCOLO_SIMPLICIDADE_2.md` - Step 12.5

---

### 1️⃣3️⃣ **Commit and Push**
- **Format**: Conventional Commits (MANDATORY)
- **Language**: All commit messages must be **EXCLUSIVELY IN ENGLISH** (mandatory requirement)
- **Message**: Descriptive, complete, with context
- **Frequency**: 1 commit per task or logical group of changes

**Standardized Commit Types** (MANDATORY):
- `feat`: Indicates a new feature
  - Example: `git commit -m "feat: add Header component"`
- `fix`: Indicates a bug fix
  - Example: `git commit -m "fix: remove wrong prop in Header"`
- `refactor`: Indicates code refactoring
  - Example: `git commit -m "refactor: add title in Header"`
- `test`: Indicates test changes
  - Example: `git commit -m "test: add test in title Header"`
- `style`: Indicates style/formatting changes
  - Example: `git commit -m "style: add Header title background"`
- `docs`: Indicates documentation changes
  - Example: `git commit -m "docs: add get started in readme"`
- `chore`: Indicates development environment changes
  - Example: `git commit -m "chore: change eslint rules"`
- `build`: Indicates dependency changes
  - Example: `git commit -m "build: add sass"`
- `revert`: Indicates reversion of a previous commit
  - Example: `git commit -m "revert: back to adc1234 commit"`

⚠️ **IMPORTANT**: All commit messages must be written **EXCLUSIVELY IN ENGLISH**!

**Commit Message Structure**:
```
<type>: <short description> (<version>)

<ORIGINAL PROBLEM>:
- [Context of the problem]
- [Why it was necessary to solve]

<IMPLEMENTED SOLUTION>:
✅ [Feature/function 1]
   - [Technical detail]
✅ [Feature/function 2]
   - [Technical detail]

✅ [TESTS]:
   - [Quantity] unit tests ([status])
   - [Tested categories]

<MODIFIED FILES>:
- [file1.py] (+X lines)
- [file2.py] (~Y lines)
- [tests/test_X.py] (NEW - Z lines)
- [docs/REQUIREMENTS.md] (updated statistics)

<UPDATED STATISTICS>:
- [CATEGORY]: X → Y complete (A% → B%)
- TOTAL: X → Y complete (A% → B%)

<USAGE EXAMPLE>: (if applicable)
  [Practical demonstration]

Refs: [related documentation]
Closes: Task #X (vX.X.X)
```

**Real Example** (Task Example):
```bash
git add src/ tests/ docs/REQUIREMENTS.md
git commit -m "feat: complete Task Example - Feature Update System (vX.Y.Z)

ORIGINAL PROBLEM:
- Implementation vX.Y.Z used string_similarity() (WRONG)
- Did not detect duplicate values, only name similarity
...

✅ IMPLEMENTED SOLUTION:
✅ extract_all_keys_from_obj()
   - Supports Obj AND dict types
   - Returns Dict[str, str] (path → value)
...

Closes: Task Example (vX.Y.Z)"

git push
```

---

## 🏆 Professional Quality Criteria

Every implementation must meet **100% of these criteria**:

| # | Criterion | Description | Validation |
|---|----------|-----------|-----------|
| 1 | **Modular Architecture** | Each feature in a separate module | Own file in `src/` |
| 2 | **Type Hints** | 100% of parameters typed | `def func(x: int) -> str:` |
| 3 | **Docstrings** | All public functions documented | Args, Returns, Examples |
| 4 | **Error Handling** | Try/except with clear messages | `except Exception as e:` |
| 5 | **Tests** | Unit + integration (100% coverage) | `tests/test_*.py` passing |
| 6 | **Semantic Commits** | Conventional Commits | `feat:`, `fix:`, `docs:` |
| 7 | **Documentation** | REQUIREMENTS.md + SPECIFICATIONS.md | Updated and complete |
| 8 | **Clean Code** | PEP8, semantic names, DRY | Functions < 50 lines |

---

## 📊 Practical Application: Task Example (Complete Example)

### Initial Situation
```markdown
Pending tasks in the SHOULD HAVE category:
[ ] Complex Feature Example (VERY COMPLEX)
[ ] Semantic AI Search (VERY COMPLEX)
[⚠️] Feature Update (PARTIAL - simpler!) ✅ CHOSEN
[ ] Google Translate API integration (COMPLEX)
```

### Planned Sprint
```
vX.Y.Z: Complete Task Example
Estimate: 3-4 hours
Complexity: MEDIUM (simpler than the others)
```

### Execution (Simplicity 1 Protocol)

**1. Read Documentation** ✅
- Read: `docs/FEATURE_SPEC.md` (662 lines)
- Understood: string similarity vs. value equality problem

**2. Choose Simple Task** ✅
- Task Example is **simpler** than text editor or AI
- Clear scope: 2 main functions + integration

**3. Ask Questions** ✅
- Asked: "How many words to get? 3-5?"
- Answer: "Default 30 characters"
- Asked: "Convert to camelCase?"
- Answer: "Yes, remove accents"
- Asked: "Name conflicts?"
- Answer: "Shorter line wins, don't touch if values differ"

**4. Sprint** ✅
- 6 subtasks planned (including questions)
- Estimated time: 3h45min

**5. Implement with Architecture** ✅
```
Order executed:
1. extract_all_keys_from_obj() (helper function - High Cohesion)
2. build_substitution_map_by_value() (main function - Low Coupling)
3. Update cli_dedupe() (integration - Dependency Injection)
4. Create tests (validation)
5. Documentation (finalization)

Applied Patterns:
- ✅ Separate modules (Reuse)
- ✅ Type hints in all functions
- ✅ Information Expert (GRASP): each function has the info it needs
- ✅ Low coupling: independent functions
- ✅ High cohesion: each function does ONE thing
```

**6. Run Tests** ✅
```
12 unit tests created:
- 4 tests for extract_all_keys_from_obj()
- 5 tests for build_substitution_map_by_value()
- 2 tests for apply_substitutions_to_file()
- 1 test for update_references_in_project()
Result: 12/12 passing (100%)
```

**7. Documentation** ✅
```
Files created/updated:
- docs/REQUIREMENTS.md (Task Example marked [X])
- docs/FEATURE_SPEC.md (already existed)
- tests/test_reference_updater.py (NEW - 350 lines)
Statistics: 59.6% → 60.6% (63 tasks complete)
```

**8. Commit and Push** ✅
```bash
Commit: 903bca4
Message: 60 lines (complete and detailed)
Status: pushed to GitHub ✅
```

### Final Result
✅ **Task Example 100% complete**
✅ **Simplicity 1 Protocol: 10/10 steps met** (v1.1 - 10 steps)
✅ **Real time: ~3h (within estimate)**
✅ **Zero bugs detected**
✅ **Professional documentation**

**Note**: This example uses v1.1 of the protocol (10 steps). v1.2 adds 2 more steps (GUI and CLI integration).

---

## 🎓 Lessons Learned

### ✅ What Works
1. **Choose the simplest**: Task Example was easier than text editor
2. **Incrementality**: Helper function → main → integration
3. **Tests first**: Detected 2 necessary adjustments before committing
4. **Complete documentation**: Facilitates future maintenance

### ❌ Anti-patterns to Avoid
1. **Don't start with the hardest task**
   - ❌ "I'll do the text editor first (50h)"
   - ✅ "I'll do the tooltip preview first (30min)"

2. **Don't do everything at once**
   - ❌ "I'll implement everything in one giant function"
   - ✅ "I'll divide into 3 testable functions"

3. **Don't skip tests**
   - ❌ "I'll test manually later"
   - ✅ "I'll create 12 unit tests now"

4. **Don't make generic commits**
   - ❌ `git commit -m "updates"`
   - ✅ `git commit -m "feat: Task Example with VALUE EQUALITY (60 lines)"`

---

## 📚 References

- **REQUIREMENTS.md**: Complete list of project tasks
- **vX.Y.Z-COMPARISON.md**: First example of the protocol
- **vX.Y.Z-SPECIFICATIONS.md**: Sprint with 3 simple tasks
- **vX.Y.Z-SPECIFICATIONS.md**: Fast iterations
- **vX.Y.Z-SPECIFICATIONS.md**: 4 UX improvements
- **FEATURE_SPEC.md**: Example of detailed documentation

---

## 🔄 Continuous Cycle

Simplicity 1 Protocol is an **iterative cycle**:

```
┌──────────────────────────────────────────────┐
│  1. Read Documentation                         │
│  2. Choose Simplest Tasks                    │
│  3. Ask Questions to the Developer           │
│  4. Analyze and Study the Project             │
│  5. Plan Sprint (2-4 tasks, 3-4h)            │
│  6. Implement (GoF + GRASP architecture)    │
│  7. Verify GUI Integration                   │
│  8. Verify CLI Implementation                │
│  9. Test (100% coverage)                     │
│  10. Organize Root Folder                    │
│  11. Document (TASKS + vX.X.X-SPECS)         │
│  12. Commit + Push (conventional)            │
└──────────────────────────────────────────────┘
           ↓
    ┌──────────────┐
    │    REPEAT    │ ← There are always simpler tasks!
    └──────────────┘
```

**Result**: Constant progress, professional code, zero technical debt, **safe for production**.

---

## 🎯 Final Message

> "I want complete, professional, and **production-safe work** - developing alone!"

**Simplicity 3 ensures**:
- ✅ **Solid base**: 13 mandatory steps from Simplicity 1
- ✅ **Security**: OWASP checklist mandatory (zero vulnerabilities)
- ✅ **Automation**: CI/CD validates every commit (memory doesn't fail)
- ✅ **Protection**: Rollback plans for critical features
- ✅ **Pragmatic**: NO team overhead (code review, formal retrospectives)
- ✅ **Prioritization**: Decision matrix when necessary
- ✅ **Performance**: Profiling for slow features
- ✅ **Traceability**: Decision notes for important choices

**Simplicity 3 is ideal for**:
- 👤 **Solo developer** (you alone)
- 🚀 **Production** (real users depending)
- ⚠️ **Critical** (bugs have impact)
- 📈 **Long-term** (evolutive project >6 months)

**When to use another protocol**:
- Disposable prototype → Use **Simplicity 1**
- Team of 2+ people → Use **Simplicity 2** (has peer code review)

**Reread this document before each sprint!**

---

## 📊 Ordinal Task Organization - Simplicity Protocols

**Version**: 1.0  
**Creation Date**: December 27, 2025  
**Author**: Josué Amaral  
**Status**: ACTIVE

---

### 🎯 Objective

This document defines the **Ordinal Task Organization** system for the Simplicity Protocols, allowing human developers and artificial intelligences to quickly identify:

- ✅ **Execution order** of tasks (from simplest to most complex)
- ✅ **Dependencies** between tasks (which must be done first)
- ✅ **Parallelization** (which can be executed simultaneously)
- ✅ **Hierarchical organization** (tree/graph structure)

---

### 📊 Ordinal Prefix System

#### Level 1: Simple Numbering (Independent Tasks)

For **independent** tasks that have **no dependencies** between them:

```markdown
1. Task A - Set up development environment
2. Task B - Create initial documentation
3. Task C - Define system architecture
```

**Characteristics**:
- ✅ Can be executed in **any order**
- ✅ Can be done **in parallel** in separate branches
- ✅ No dependency conflicts
- ✅ Sequential ascending numbering (1, 2, 3...)

---

#### Level 2: Hierarchy with Letters (Task Groups)

To organize tasks into **logical groups** with **subgroups**:

```markdown
🔴 MUST HAVE - Release v1.0.0

A. Infrastructure and Configuration
   A.1. Create directory structure
   A.2. Configure project dependencies
   
B. Core - Data Structures
   B.1. Implement Node class
   B.2. Implement ExpressionTree
   
C. Core - Conversions
   C.1. Implement number → tree conversion
   C.2. Implement tree → RPN conversion
```

**Characteristics**:
- ✅ **Capital letter** = Group/Category
- ✅ **Number after letter** = Subtask within group
- ✅ Tasks from **different groups** (A, B, C) are **parallel**
- ✅ Tasks within the **same group** may have dependencies

---

#### Level 3: Deep Hierarchy (Complex Dependencies)

For tasks with **explicit dependencies** in a **tree/graph** structure:

```markdown
A.C.1. Implement number → tree conversion
   ├─ Must be done AFTER A.1, A.2, C.1
   └─ Structure: A (root) → C (intermediate) → 1 (leaf)

B.C.2. Implement tree → RPN conversion
   B.C.2.1. RPN Parser (leaf - do FIRST)
   B.C.2.2. RPN Serializer (leaf - do FIRST)
   B.C.2. Implement conversion (parent - do AFTER 2.1 and 2.2)
```

**Reading the hierarchy** (⭐ CRITICAL):

The hierarchy should be read from **RIGHT to LEFT** (reverse order):

```
C.B.1.D.1
   │  │ │ └─ 1: Execute LAST (tree root)
   │  │ └─── D: Execute THIRD
   │  └───── 1: Execute SECOND
   └──────── B: Execute FIRST (tree leaf)

Execution order: B → 1 → D → 1 (right to left)
```

**Interpretation**:
- ✅ **Rightmost** = Ancestors (execute LAST)
- ✅ **Leftmost** = Descendants (execute FIRST)
- ✅ **Bottom-up organization**: Base → Top

**Practical Example**:

```markdown
C.B.1.D.1 - Integrate Dash with Cytoscape

Execution order (right → left):
1. FIRST:  Task D.1 (create basic Cytoscape component)
2. SECOND: Task 1.D (configure layout)
3. THIRD:  Task B.1 (implement data structure)
4. FOURTH: Task C (final Dash + Cytoscape integration)
```

---

### 🌳 Tree/Graph Structure

#### Fundamental Concepts

**1. Parent and Child Nodes**

```
B.C.2 (PARENT - execute AFTER)
   ├── B.C.2.1 (CHILD - execute BEFORE)
   └── B.C.2.2 (CHILD - execute BEFORE)
```

**Rule**: 
- ✅ **Children must be completed BEFORE parent**
- ✅ Children are **prerequisites** for parent
- ✅ Parent **depends** on children

**2. Siblings (Parallel)**

```
B.C.2.1 (sibling)
B.C.2.2 (sibling)
```

**Rule**:
- ✅ Siblings can be executed **in parallel**
- ✅ No dependency between them
- ✅ Can be in **separate branches**

**3. Cousins, Uncles, Grandparents (Parallel vs Serial)**

```
A. Group A
   A.1. Task A1
   A.2. Task A2
   
B. Group B
   B.1. Task B1
   B.2. Task B2
```

**Rule**:
- ✅ **Different groups** (A, B) = **PARALLEL** (execute simultaneously)
- ✅ **Cousins** (A.1 and B.1) = **PARALLEL**
- ✅ **Uncles/Nephews** (A and B.1) = **Evaluate explicit dependencies**

---

### 🔄 Parallelization vs Serialization

#### PARALLEL Tasks (can be simultaneous)

✅ **When to parallelize**:
- Tasks from **different groups** (A.x, B.x, C.x)
- **Siblings** at the same level (X.1, X.2, X.3)
- **Cousins** (A.1 and B.1)
- Tasks **without explicit dependencies**

**Example**:
```markdown
✅ PARALLEL:
   A.1 (Create User model)
   B.1 (Create Product model)
   C.1 (Create graphical interface)
   
→ Can be done in 3 simultaneous branches
→ Zero conflicts
```

---

#### SERIAL Tasks (must be sequential)

❌ **When to serialize**:
- Tasks with **parent-child relationship**
- Tasks with **explicit dependencies**
- When one task **uses the result** of another

**Example**:
```markdown
❌ SERIAL:
   B.C.2.1 (RPN Parser) ─┐
   B.C.2.2 (Serializer)  ├─→ B.C.2 (Complete conversion)
                         ┘
   
→ B.C.2.1 and B.C.2.2 MUST be completed BEFORE B.C.2
→ B.C.2 depends on results from 2.1 and 2.2
```

---

### 🎯 Integration with Existing Classification System

The ordinal system **complements** (does not replace) existing classifications:

```markdown
🔴🟡 [ ] #3 B.1. Implement Node class (1h)
 │  │  │  │ └─ Ordinal prefix (dependencies)
 │  │  │  └─── Issue ID (#3)
 │  │  └────── Hierarchy (B = Group, 1 = Subtask)
 │  └───────── Complexity (🟡 Medium)
 └──────────── Priority (🔴 Must Have)

Reason: Base for all tree manipulation
Features: Binary tree node with operator/value
Tests: Unit tests for node creation
```

**Complete Legend**:
- **MoSCoW Priority**: 🔴 Must | 🟡 Should | 🟢 Could | ⚪ Won't
- **Complexity**: 🟢 Simple (0-1h) | 🟡 Medium (1-2h) | 🔴 Complex (>2h)
- **Status**: 🔴 Not Started | 🟡 In Progress | 🟢 Done | 🔵 Blocked
- **Ordinal Prefix**: Identifies execution order and dependencies

---

### 🤖 Instructions for Artificial Intelligences

**When to Suggest Ordinal Organization**

AI should suggest ordinal organization when:

✅ **Project has >10 tasks** with interdependencies
✅ **Multiple developers** working simultaneously
✅ **Blocking tasks** (one depends on another)
✅ **Risk of conflicts** in version control
✅ **Need for parallelization** to speed up development

**How AI Should Apply**

1. **Analyze dependencies**:
   ```python
   # Pseudo-code
   tasks = read_tasks_md()
   graph = build_dependency_graph(tasks)
   order = topological_sort(graph)  # Bottom-up
   ```

2. **Identify parallel groups**:
   ```python
   parallel_groups = identify_independent_components(graph)
   ```

3. **Assign ordinal prefixes**:
   ```python
   for group in parallel_groups:
       letter = next_letter()  # A, B, C...
       for task in group:
           task.prefix = f"{letter}.{task.index}"
   ```

4. **Suggest branch strategy**:
   ```markdown
   Branch recommendation:
   - Branch feat/auth: A.1 → A.2 → A.3
   - Branch feat/api: B.1 → B.2 (parallel with auth)
   - Branch feat/ui: C.1 (wait for auth merge)
   ```

---

## 🌳 Tree Imports Analogy

**Author:** Josué Amaral  
**Date:** December 24, 2025  
**Context:** Phase 3.0 - Refactoring Architecture  
**Applicable to:** All programming languages

---

### 📚 Overview

This document describes the **Tree Imports Analogy**, a mental model for understanding and organizing the dependency architecture in software projects. This analogy is applicable to any programming language that supports module importing/inclusion.

---

### 🌳 The Imports Tree

#### Fundamental Concept

A project's import structure can be visualized as a **hierarchical tree**, where:

```
                    📦 A (Root)
                   /           \
              📦 B              📦 C
             / | \               |
        📦 D 📦 E 📦 F         📦 G
         |    |    |            |
      [libs] [libs] [libs]   [libs]
```

#### Tree Elements

**🌲 Root**
- **Main File** (e.g., `app.py`, `main.py`, `index.js`)
- **Characteristics:**
  - Most complex and encapsulated
  - System orchestrator
  - Imports multiple project modules
  - Contains coordination logic between components
  - Decides "what" to do, delegating "how" to do it

**🌿 Branches**
- **Intermediate Modules** (e.g., `gui/`, `core/`, `utils/`)
- **Characteristics:**
  - Medium complexity
  - Import other project modules
  - Provide specialized functionality
  - Abstract implementation details

**🍃 Leaves**
- **Terminal Modules** (e.g., `button.py`, `validator.py`, `helpers.py`)
- **Characteristics:**
  - Simpler and more specific
  - **DO NOT import** files from the project itself
  - **DO import** external libraries (Numpy, Pandas, etc.)
  - Provide atomic functionality
  - Are reusable and independently testable

---

### 📊 Practical Example

#### Hierarchical Structure

```python
# A.py (ROOT) - Main file
from B import feature_x
from C import feature_y

def main():
    """Orchestrator - coordinates B and C"""
    result_x = feature_x.process()
    result_y = feature_y.process()
    combine(result_x, result_y)
```

```python
# B.py (BRANCH) - Intermediate module
from D import validator
from E import transformer
from F import calculator

def feature_x():
    """Specialist - coordinates D, E, F"""
    data = validator.validate_input()
    transformed = transformer.transform(data)
    return calculator.compute(transformed)
```

```python
# D.py (LEAF) - Terminal module
import re  # Standard library
import numpy as np  # External library

def validate_input(data):
    """Atomic function - doesn't import project files"""
    pattern = re.compile(r'^\d+$')
    return np.array([x for x in data if pattern.match(x)])
```

#### Characteristics by Level

| Level | File | Imports Project | Imports External | Complexity | Role |
|-------|------|-----------------|------------------|------------|------|
| 0 (Root) | A | B, C | Rarely | High | Orchestrator |
| 1 (Branch) | B, C | D, E, F, G | Sometimes | Medium | Coordinator |
| 2 (Leaf) | D, E, F, G | ❌ Never | ✅ Always | Low | Executor |

---

### 🔄 Development Approaches

#### 🔽 Top-Down (From Top to Bottom)

**Starts from the root and descends to the leaves**

```
Process:
1. Define A (what the system does)
2. Identify needs (B, C)
3. Decompose B into (D, E, F)
4. Implement leaves (D, E, F, G)
```

**Advantages:**
- ✅ Clear architecture from the start
- ✅ Facilitates high-level planning
- ✅ Identifies dependencies early

**Disadvantages:**
- ❌ May create interfaces without implementation
- ❌ Makes initial testing difficult
- ❌ Risk of over-engineering

---

#### 🔼 Bottom-Up (From Bottom to Top)

**Starts from the leaves and rises to the root**

```
Process:
1. Implement D, E, F, G (basic components)
2. Combine into B, C (functionalities)
3. Orchestrate in A (complete system)
```

**Advantages:**
- ✅ Testable components from the start
- ✅ Natural reusability
- ✅ Less code waste

**Disadvantages:**
- ❌ Architecture emerges late
- ❌ Risk of non-integrable components
- ❌ Difficulty visualizing the whole

---

#### ↔️ Middle-Out (From Middle Outward)

**Starts from the branches and expands in both directions**

```
Process:
1. Identify central functionality (B)
2. ↓ Implement necessary components (D, E, F)
3. ↑ Create orchestrator (A)
4. Repeat for other functionalities (C, G)
```

**Advantages:**
- ✅ Balances overview and details
- ✅ Iterative and adaptable
- ✅ Reduces risk of both extreme approaches

**Disadvantages:**
- ❌ Requires experience to identify "the middle"
- ❌ Can create inconsistencies
- ❌ Requires frequent refactoring

---

### 🎯 Design Principles

#### 1. **Depth Principle**

> "The closer to the root, the more complex and orchestrating.  
> The closer to the leaves, the simpler and executing."

```
Root (A):     if condition: B.do() else: C.do()  ← Decision
Branch (B):   return D.compute(E.prepare(data))  ← Coordination
Leaf (D):     return sum(numbers) / len(numbers) ← Execution
```

#### 2. **Independence Principle**

> "Leaves don't depend on other project leaves.  
> Leaves can only depend on external libraries."

❌ **Wrong:**
```python
# D.py (leaf)
from E import helper  # Dependency between leaves!
```

✅ **Correct:**
```python
# B.py (branch)
from D import function_d
from E import helper

def feature():
    return function_d(helper.prepare())  # Branch coordinates leaves
```

#### 3. **Single Responsibility Principle**

> "Each level has its distinct role."

| Level | Responsibility | Question it Answers |
|-------|----------------|---------------------|
| Root | Orchestration | "What does the system do?" |
| Branch | Coordination | "How do the parts connect?" |
| Leaf | Execution | "How to do X specifically?" |

---

### 📏 Quality Metrics

#### Good Architecture Indicators

✅ **Balanced Tree:**
- Depth of 2-4 levels
- Width proportional to complexity
- No leaves importing other leaves

✅ **Clear Separation:**
```
Root:  High complexity + Low execution
Leaf:  Low complexity + High execution
```

✅ **Ease of Testing:**
- Leaves testable in isolation
- Branches testable with mocks
- Root testable with integration

#### Problem Indicators

❌ **Degenerate Tree (Linear):**
```
A → B → C → D → E → F  # Too deep!
```

❌ **Fat Leaves:**
```python
# D.py - 500 lines, imports E, F, G  # It's a branch, not a leaf!
```

❌ **Thin Root:**
```python
# A.py - 10 lines  # Should orchestrate more!
```

---

### 📖 Conclusion of Sections

The **Ordinal Task Organization** and **Tree Imports Analogy** provide powerful mental models for:

1. **Organizing** tasks from simplest to most complex
2. **Understanding** existing architecture
3. **Planning** new modules
4. **Refactoring** code organically
5. **Parallelizing** development to accelerate deliveries
6. **Communicating** design decisions clearly

---

## 💡 Programming Best Practices for AI

> **This section contains specific recommendations to improve the quality of code generated by artificial intelligences.**

### 1. 📖 **Readable and Self-Documenting Code**

**Why it matters**: AIs should produce code that humans can easily understand and maintain.

**Practices**:
- ✅ **Descriptive names**: Use names that explain the purpose
  ```python
  # ❌ BAD
  def proc(d, x):
      return d[x] if x in d else None
  
  # ✅ GOOD
  def get_user_preference(preferences_dict, preference_key):
      """Returns user preference or None if it doesn't exist."""
      return preferences_dict.get(preference_key)
  ```

- ✅ **Small and focused functions**: One function = one responsibility
  ```python
  # ❌ BAD - Function does multiple things
  def process_user_data(user):
      # validates
      # transforms
      # saves to database
      # sends email
      # logs
      pass  # 150 lines
  
  # ✅ GOOD - Specialized functions
  def validate_user_data(user): pass
  def transform_user_data(user): pass
  def save_user_to_database(user): pass
  def send_welcome_email(user): pass
  def log_user_registration(user): pass
  ```

- ✅ **Avoid "magic numbers"**: Use named constants
  ```python
  # ❌ BAD
  if user.age > 18 and balance < 1000:
      apply_fee(balance * 0.05)
  
  # ✅ GOOD
  MINIMUM_ADULT_AGE = 18
  BALANCE_THRESHOLD = 1000
  SERVICE_FEE_RATE = 0.05
  
  if user.age > MINIMUM_ADULT_AGE and balance < BALANCE_THRESHOLD:
      apply_fee(balance * SERVICE_FEE_RATE)
  ```

### 2. 🎯 **Consistent Naming Conventions**

**Why it matters**: Consistency facilitates navigation and code comprehension.

**Practices by language**:

**Python**:
- ✅ `snake_case` for functions and variables
- ✅ `PascalCase` for classes
- ✅ `SCREAMING_SNAKE_CASE` for constants
- ✅ `_private_method` for private methods

**JavaScript/TypeScript**:
- ✅ `camelCase` for functions and variables
- ✅ `PascalCase` for classes and components
- ✅ `SCREAMING_SNAKE_CASE` for constants
- ✅ `_privateMethod` or `#privateField` for private

**General conventions**:
- ✅ Verbs for functions: `get_user()`, `calculate_total()`, `validate_input()`
- ✅ Nouns for classes: `UserManager`, `PaymentProcessor`
- ✅ Booleans with prefixes: `is_valid`, `has_permission`, `can_edit`

### 3. 🛡️ **Robust Error Handling**

**Why it matters**: Production code must gracefully handle failures.

**Practices**:
- ✅ **Always validate input**:
  ```python
  def divide(a, b):
      if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
          raise TypeError("Arguments must be numbers")
      if b == 0:
          raise ValueError("Divisor cannot be zero")
      return a / b
  ```

- ✅ **Use specific exceptions**:
  ```python
  # ❌ BAD - Generic exception
  try:
      process_payment(amount)
  except Exception as e:
      print("Error")
  
  # ✅ GOOD - Specific exceptions
  try:
      process_payment(amount)
  except PaymentDeclinedError as e:
      notify_user("Payment declined")
  except InsufficientFundsError as e:
      notify_user("Insufficient funds")
  except NetworkError as e:
      retry_payment(amount)
  ```

- ✅ **Adequate logging**:
  ```python
  import logging
  
  try:
      result = risky_operation()
  except Exception as e:
      logging.error(f"Failed in risky_operation: {e}", exc_info=True)
      raise  # Re-raise to allow handling at higher level
  ```

### 4. 🧪 **Effective Testing Strategies**

**Why it matters**: Tests ensure code works and continues working.

**Practices**:
- ✅ **Unit tests for business logic**:
  ```python
  def test_calculate_discount():
      # Arrange
      original_price = 100
      discount_rate = 0.2
      
      # Act
      final_price = calculate_discount(original_price, discount_rate)
      
      # Assert
      assert final_price == 80
  ```

- ✅ **Test edge cases**:
  ```python
  def test_edge_cases():
      assert calculate_discount(0, 0.5) == 0  # Zero price
      assert calculate_discount(100, 0) == 100  # Zero discount
      assert calculate_discount(100, 1.0) == 0  # 100% discount
      
      with pytest.raises(ValueError):
          calculate_discount(100, -0.1)  # Negative discount
      
      with pytest.raises(ValueError):
          calculate_discount(-100, 0.1)  # Negative price
  ```

- ✅ **Mocks for external dependencies**:
  ```python
  from unittest.mock import Mock, patch
  
  def test_send_notification():
      with patch('email_service.send') as mock_send:
          notify_user("user@example.com", "Test message")
          mock_send.assert_called_once()
  ```

### 5. 🔒 **Security First**

**Why it matters**: Vulnerabilities can have serious consequences.

**Practices**:
- ✅ **Never trust user input**:
  ```python
  # ❌ BAD - SQL Injection
  query = f"SELECT * FROM users WHERE id = {user_id}"
  
  # ✅ GOOD - Parameterization
  query = "SELECT * FROM users WHERE id = ?"
  cursor.execute(query, (user_id,))
  ```

- ✅ **Secrets in environment variables**:
  ```python
  # ❌ BAD
  API_KEY = "sk-1234567890abcdef"  # Hardcoded
  
  # ✅ GOOD
  import os
  API_KEY = os.getenv('API_KEY')
  if not API_KEY:
      raise ValueError("API_KEY not configured")
  ```

- ✅ **Sanitize output to prevent XSS**:
  ```python
  from html import escape
  
  # ❌ BAD
  html = f"<div>Hello {user_name}</div>"
  
  # ✅ GOOD
  html = f"<div>Hello {escape(user_name)}</div>"
  ```

### 6. ⚡ **Performance Optimization**

**Why it matters**: Slow code = unhappy users.

**Practices**:
- ✅ **Choose correct data structure**:
  ```python
  # ❌ BAD - List search O(n)
  if user_id in user_list:  # 1000 comparisons
      # ...
  
  # ✅ GOOD - Set search O(1)
  if user_id in user_set:  # 1 comparison
      # ...
  ```

- ✅ **Avoid unnecessary loops**:
  ```python
  # ❌ BAD - Double loop O(n²)
  for item in list1:
      for item2 in list2:
          if item == item2:
              # ...
  
  # ✅ GOOD - Set intersection O(n)
  common_items = set(list1) & set(list2)
  for item in common_items:
      # ...
  ```

- ✅ **Lazy loading when appropriate**:
  ```python
  # ❌ BAD - Load everything into memory
  all_users = User.objects.all()  # 1 million records
  for user in all_users:
      process(user)
  
  # ✅ GOOD - Iterator that loads on demand
  for user in User.objects.iterator():
      process(user)
  ```

### 7. 📝 **Clear and Useful Documentation**

**Why it matters**: Code is read much more often than it is written.

**Practices**:
- ✅ **Complete docstrings**:
  ```python
  def calculate_shipping(weight, distance, express=False):
      """
      Calculate shipping cost based on weight and distance.
      
      Args:
          weight (float): Package weight in kg
          distance (float): Distance in km
          express (bool): If True, uses express shipping (default: False)
      
      Returns:
          float: Shipping cost in dollars
      
      Raises:
          ValueError: If weight or distance is negative
      
      Examples:
          >>> calculate_shipping(2.5, 100)
          25.0
          >>> calculate_shipping(2.5, 100, express=True)
          37.5
      """
      if weight < 0 or distance < 0:
          raise ValueError("Weight and distance must be positive")
      
      base_cost = weight * distance * 0.1
      return base_cost * 1.5 if express else base_cost
  ```

- ✅ **Comments explain "why", not "what"**:
  ```python
  # ❌ BAD - Comments the obvious
  x = x + 1  # Increment x
  
  # ✅ GOOD - Explains the reason
  # Increment counter to include current element in count
  # since range() excludes the last element
  x = x + 1
  ```

- ✅ **README with practical examples**:
  ```markdown
  # How to use
  
  ## Installation
  ```bash
  pip install mypackage
  ```
  
  ## Basic example
  ```python
  from mypackage import Calculator
  
  calc = Calculator()
  result = calc.add(2, 3)
  print(result)  # Output: 5
  ```
  ```

### 8. 🏗️ **Organization and Modularity**

**Why it matters**: Organized code is easier to maintain and scale.

**Practices**:
- ✅ **Separation of concerns**:
  ```
  project/
  ├── models/       # Data structures
  ├── services/     # Business logic
  ├── controllers/  # Flow coordination
  ├── views/        # User interface
  ├── utils/        # Helper functions
  └── tests/        # Automated tests
  ```

- ✅ **DRY (Don't Repeat Yourself)**:
  ```python
  # ❌ BAD - Duplicated code
  def process_order_a():
      validate()
      calculate()
      save()
  
  def process_order_b():
      validate()
      calculate()
      save()
  
  # ✅ GOOD - Reused code
  def process_order_common():
      validate()
      calculate()
      save()
  
  def process_order_a():
      process_order_common()
      # specific logic A
  
  def process_order_b():
      process_order_common()
      # specific logic B
  ```

- ✅ **Single responsibility principle**:
  ```python
  # ❌ BAD - Class does many things
  class User:
      def __init__(self): pass
      def save_to_database(self): pass
      def send_email(self): pass
      def generate_pdf_report(self): pass
  
  # ✅ GOOD - Specialized classes
  class User:
      def __init__(self): pass
  
  class UserRepository:
      def save(self, user): pass
  
  class EmailService:
      def send(self, to, message): pass
  
  class ReportGenerator:
      def generate_pdf(self, user): pass
  ```

### 9. 🔄 **Effective Version Control**

**Why it matters**: Clean history facilitates debugging and collaboration.

**Practices**:
- ✅ **Atomic and descriptive commits**:
  ```bash
  # ❌ BAD
  git commit -m "fixes"
  git commit -m "updates"
  
  # ✅ GOOD
  git commit -m "feat: add email validation in registration form"
  git commit -m "fix: correct discount calculation for amounts over $1000"
  ```

- ✅ **Branches for features**:
  ```bash
  # Create branch for new feature
  git checkout -b feature/user-authentication
  
  # Develop and commit
  git commit -m "feat: implement JWT login"
  
  # Merge after review
  git checkout main
  git merge feature/user-authentication
  ```

- ✅ **Appropriate .gitignore**:
  ```gitignore
  # Python
  __pycache__/
  *.pyc
  .env
  venv/
  
  # JavaScript
  node_modules/
  dist/
  .env.local
  
  # IDEs
  .vscode/
  .idea/
  *.swp
  
  # OS
  .DS_Store
  Thumbs.db
  ```

### 10. 📦 **Dependency Management**

**Why it matters**: Poorly managed dependencies cause compatibility problems.

**Practices**:
- ✅ **Pin versions**:
  ```
  # ❌ BAD - requirements.txt
  flask
  requests
  
  # ✅ GOOD - requirements.txt
  flask==2.3.2
  requests==2.31.0
  ```

- ✅ **Use virtual environments**:
  ```bash
  # Python
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  
  # Node.js
  npm install  # Uses package-lock.json
  ```

- ✅ **Check for vulnerabilities**:
  ```bash
  # Python
  pip install pip-audit
  pip-audit
  
  # Node.js
  npm audit
  npm audit fix
  ```

### 11. 🔄 **Frequent Code Refactoring**

**Why it matters**: Code that isn't regularly refactored tends to deteriorate over time, becoming difficult to maintain, understand, and evolve.

> **CRITICAL FOR AIs**: Remember to **frequently** refactor code during development to maintain quality and avoid accumulation of technical debt.

**Mandatory practices**:

- ✅ **Avoid excessively large files**:
  ```
  # 🚨 SIZE ALERTS
  - File > 500 lines → Consider splitting
  - File > 1000 lines → MUST split
  - Class > 300 lines → Refactor into smaller classes
  - Function > 50 lines → Split into helper functions
  ```
  
  **Refactoring example**:
  ```python
  # ❌ BAD - 1500-line file
  # user_manager.py (everything in one file)
  class UserManager:
      def create_user(): pass  # 100 lines
      def validate_user(): pass  # 150 lines
      def authenticate_user(): pass  # 200 lines
      def send_email(): pass  # 100 lines
      # ... 950 more lines
  
  # ✅ GOOD - Split into specialized modules
  # user/
  #   __init__.py
  #   manager.py (200 lines)
  #   validator.py (150 lines)
  #   authenticator.py (200 lines)
  #   notifications.py (100 lines)
  ```

- ✅ **Increase cohesion (Single Responsibility Principle)**:
  ```python
  # ❌ BAD - Low cohesion (does many different things)
  class OrderProcessor:
      def process_order(self):
          self.validate_payment()
          self.send_email()
          self.update_inventory()
          self.generate_invoice()
          self.log_analytics()
  
  # ✅ GOOD - High cohesion (each class has one responsibility)
  class PaymentValidator:
      def validate(self): pass
  
  class EmailNotifier:
      def send_order_confirmation(self): pass
  
  class InventoryManager:
      def update_stock(self): pass
  
  class InvoiceGenerator:
      def generate(self): pass
  
  class AnalyticsLogger:
      def log_order(self): pass
  ```

- ✅ **Constantly improve readability**:
  ```python
  # ❌ BAD - Hard to understand
  def p(d, x, y):
      return sum([d[i][x] * d[i][y] for i in range(len(d)) if x in d[i] and y in d[i]])
  
  # ✅ GOOD - Self-explanatory
  def calculate_correlation_between_features(dataset, feature_x, feature_y):
      """
      Calculates the correlation between two features in a dataset.
      
      Args:
          dataset: List of dictionaries containing features
          feature_x: Name of the first feature
          feature_y: Name of the second feature
      
      Returns:
          float: Sum of feature products when both exist
      """
      correlation_sum = 0
      for data_point in dataset:
          if feature_x in data_point and feature_y in data_point:
              correlation_sum += data_point[feature_x] * data_point[feature_y]
      return correlation_sum
  ```

- ✅ **Eliminate redundancies and increase reusability**:
  ```python
  # ❌ BAD - Duplicated code (redundancy)
  def get_active_users():
      users = db.query("SELECT * FROM users")
      active = [u for u in users if u.status == 'active' and u.verified == True]
      return active
  
  def get_active_admins():
      users = db.query("SELECT * FROM users")
      active = [u for u in users if u.status == 'active' and u.verified == True and u.role == 'admin']
      return active
  
  # ✅ GOOD - Reusable code (DRY - Don't Repeat Yourself)
  def get_verified_active_users(role=None):
      """Returns active and verified users, optionally filtered by role."""
      users = db.query("SELECT * FROM users")
      filtered = [u for u in users if u.status == 'active' and u.verified == True]
      
      if role:
          filtered = [u for u in filtered if u.role == role]
      
      return filtered
  
  def get_active_users():
      return get_verified_active_users()
  
  def get_active_admins():
      return get_verified_active_users(role='admin')
  ```

- ✅ **Hierarchize code into folders and directories**:
  ```
  # ❌ BAD - Everything in root (hard to navigate)
  project/
    main.py
    user_stuff.py
    payment_things.py
    email_sender.py
    validators.py
    helpers.py
    utils.py
    config.py
    constants.py
  
  # ✅ GOOD - Logical hierarchy (easy to understand and maintain)
  project/
    main.py
    config/
      __init__.py
      settings.py
      constants.py
    core/
      __init__.py
      models.py
      exceptions.py
    features/
      users/
        __init__.py
        manager.py
        validator.py
      payments/
        __init__.py
        processor.py
        validator.py
    services/
      email/
        __init__.py
        sender.py
        templates.py
    utils/
      __init__.py
      helpers.py
      formatters.py
  ```

- ✅ **Search for orphaned code after refactoring** (⭐ **MANDATORY**):
  
  > **CRITICAL**: After any refactoring, it is **MANDATORY** to search for orphaned code - code that was implemented but is no longer being used.
  
  **What is orphaned code?**
  - ❌ Unused functions (defined but never called)
  - ❌ Unused variables (declared but never referenced)
  - ❌ Unused imports (imported but never used)
  - ❌ Dead/unreachable code
  - ❌ Uninstantiated classes (defined but never created)
  - ❌ Uncalled methods (defined but never invoked)
  
  **Why search for orphaned code?**
  - ✅ **Reduces complexity**: Less code = easier to understand
  - ✅ **Improves maintenance**: Don't waste time on unused code
  - ✅ **Avoids confusion**: Orphaned code can mislead developers
  - ✅ **Performance**: Less code = faster startup
  - ✅ **Security**: Orphaned code may contain forgotten vulnerabilities
  
  **Tools to detect orphaned code**:
  ```bash
  # Python - Unused code (functions, classes, variables)
  pip install vulture
  vulture src/ --min-confidence 80
  # Output: unused functions/classes/variables
  
  # Python - Unused imports
  pip install autoflake
  autoflake --remove-all-unused-imports --check -r src/
  # Or use pylint
  pylint --disable=all --enable=unused-import src/
  
  # JavaScript/TypeScript - Unused code
  npm install -g ts-prune  # For TypeScript
  ts-prune
  # Or ESLint
  npm run lint -- --rule 'no-unused-vars: error'
  
  # For any language - Search for unused definitions
  # 1. Generate list of definitions (functions, classes)
  # 2. Search for references to each definition in code
  # 3. If no reference found → orphaned code
  ```
  
  **Usage example (Python)**:
  ```python
  # Before refactoring - 500-line file
  
  # Refactoring: split into 3 smaller files
  # Now search for orphaned code:
  
  $ vulture src/ --min-confidence 80
  src/old_module.py:45: unused function 'process_legacy_format' (100% confidence)
  src/utils.py:123: unused function 'deprecated_helper' (90% confidence)
  src/models.py:67: unused class 'OldDataModel' (100% confidence)
  
  # Action: Remove or document why keeping
  # If truly unused → DELETE
  # If will be used in future → Mark with comment and issue
  ```
  
  **Orphaned code checklist** (execute AFTER refactoring):
  ```markdown
  - [ ] Run vulture (Python) or ts-prune (TypeScript)
  - [ ] Review unused functions (confirm if truly orphaned)
  - [ ] Remove unused imports (autoflake or similar tool)
  - [ ] Check uninstantiated classes
  - [ ] Search for old commented code (also orphaned code)
  - [ ] Document if any "orphaned" code should be kept (e.g., public API)
  ```
  
  **When NOT to remove**:
  - ✅ **Public APIs**: Even if not used internally, external clients may use them
  - ✅ **Hooks/callbacks**: May be called by frameworks
  - ✅ **Test code**: Test helpers may appear unused
  - ✅ **Planned code**: If there's an issue/task to use soon, keep (but document)

**When to refactor**:

1. **During new feature implementation**:
   - Before adding new code, check if existing files are organized
   - If you find poorly structured code, refactor BEFORE adding new functionality

2. **After completing a feature**:
   - Review the implemented code
   - Identify improvement opportunities (DRY, SRP, better names)
   - Refactor immediately while context is fresh
   - **⭐ MANDATORY**: Search for orphaned code (vulture, autoflake, etc.)

3. **When reviewing code (Steps 7 and 8)**:
   - Use the 9 quality criteria as a guide
   - If you detect redundancy, lower cohesion, or higher coupling → Refactor

4. **Before committing (Step 13)**:
   - Last checkpoint: is the code as clean as possible?
   - Is there anything that can be simplified?

5. **Minimum periodicity**:
   - ⚠️ **NEVER** let more than 3-5 features pass without refactoring
   - 🚨 If project has > 10 files with > 500 lines → PRIORITIZE refactoring
   - ⭐ **Always search for orphaned code after refactoring** (not optional)

**Benefits of frequent refactoring**:
- ✅ **Simpler maintenance**: Organized code is easier to modify
- ✅ **Fewer bugs**: Clean code has fewer places for bugs to hide
- ✅ **Faster onboarding**: New developers understand the code faster
- ✅ **Speed**: Paradoxically, frequent refactoring ACCELERATES development
- ✅ **Easier validation**: Modular code is easier to test and verify

**Tools to identify refactoring needs**:
```bash
# Python - Cyclomatic complexity
pip install radon
radon cc . -a -nb  # Show complex functions

# Python - Duplicated code
pip install pylint
pylint --disable=all --enable=duplicate-code .

# Python - Dead code
pip install vulture
vulture .

# JavaScript - Complexity analysis
npm install -g complexity-report
cr --format json src/
```

### 🎯 **Quick Checklist for AI**

Before generating/committing code, verify:

- [ ] Names are descriptive and follow language conventions?
- [ ] Functions have single responsibility and are small?
- [ ] Is there error handling for exceptional cases?
- [ ] Code is tested (unit tests + edge cases)?
- [ ] No obvious security vulnerabilities?
- [ ] Performance is acceptable (no unnecessary O(n²) algorithms)?
- [ ] Is there documentation (docstrings, useful comments)?
- [ ] Code is organized in logical modules?
- [ ] **Code was recently refactored?** (files < 500 lines, no duplication)
- [ ] **Folder hierarchy is logical?** (clear separation of responsibilities)
- [ ] Commits are descriptive (conventional commits)?
- [ ] Dependencies have pinned versions?

### 📚 **Additional Resources**

- **Clean Code** (Robert C. Martin) - Clean code principles
- **SOLID Principles** - Well-done object orientation
- **Design Patterns** (GoF) - Common solutions to common problems
- **OWASP Top 10** - Main security vulnerabilities
- **PEP 8** (Python) - Python style guide
- **Google Style Guides** - Style guides by language

---

## 📚 Related Documents

- 📘 **PROTOCOLO_SIMPLICIDADE_1.md**: Base (13 steps) - For prototypes/internal
- 📕 **PROTOCOLO_SIMPLICIDADE_2.md**: Advanced (23 steps) - For enterprise teams
- 📗 **PROTOCOLO_SIMPLICIDADE_3.md**: Hybrid (16 steps) - **Solo dev in production** ⭐

---

**Version**: 3.2
**Last update**: December 16, 2025
**Maintained by**: Josué Amaral
**Status**: ACTIVE - Protocol for solo developer in production
