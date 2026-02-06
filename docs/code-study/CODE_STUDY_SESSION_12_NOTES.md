# Code Study - Session 12: Phase 4 Core Components

**Date**: 2026-01-22  
**Programmer**: #4  
**Session Focus**: Files directly relevant to v2.9.116 Phase 4 implementation

---

## 📊 Session Statistics

**Files Studied**: 5 files  
**Lines of Code**: 2,076 LOC  
**Time**: ~45 minutes  
**Coverage**: Core Phase 4 components

---

## 📁 Files Analyzed

### 1. **src/gui/widgets/search_widgets.py** (476 LOC) ⭐ CRITICAL

**Purpose**: Reusable search/replace widgets extracted for File Explorer integration

**Key Components**:

#### FileNameQueryPanel (lines 28-80)
- Simple filename pattern input with regex support
- Signals: `pattern_changed`, `clear_requested`
- Methods: `get_pattern()`, `set_pattern()`, `clear()`
- **Usage in Phase 4**: Section 2 (Search & Replace)

#### ContentQueryPanel (lines 82-127)
- Multi-line text editor for content search
- Signal: `query_changed`
- Max height: 80px
- Methods: `get_query()`, `set_query()`, `set_font()`, `clear()`
- **Usage in Phase 4**: Section 2 (Search & Replace)

#### SearchOptionsPanel (lines 129-194)
- Checkboxes for: case-sensitive, whole-word, regex, **multi-query**
- Signal: `options_changed` (emits dict)
- Methods: `get_options()`, `set_options()`
- **CRITICAL**: `multi_query` checkbox enables multi-line search mode
- **Usage in Phase 4**: Section 2 options

#### ReplacePanel (lines 196-273)
- Text editor + preserve case checkbox + action buttons
- Signals: `replace_first_requested`, `replace_all_requested`
- Methods: `get_replacement()`, `get_preserve_case()`, `set_buttons_enabled()`
- **Usage in Phase 4**: Section 2 (Replace operations)

#### ConditionsGrid (lines 275-476) ⭐ MOST COMPLEX
- **Dynamic** condition rows (add/remove)
- **Fields**: filename, path, ext, size, mtime, content
- **Operators**: equals, not equals, contains, not contains, >, <, >=, <=, regex
- **Logic**: AND/OR combo box
- **Options**: case-sensitive, regex (enabled only for text fields)
- Signal: `conditions_changed` (emits list of dicts)
- Methods: 
  - `add_condition_row()` - creates new row widget
  - `get_conditions()` - returns list of condition dicts
  - `get_logic_operator()` - returns "AND" or "OR"
  - `clear_conditions()` - removes all rows
- **IMPORTANT**: Uses `currentData()` for technical field names (not translated text)
- **Usage in Phase 4**: Section 4 (Advanced Conditions)

**Design Patterns**:
- Signal/Slot communication
- Composite pattern (ConditionsGrid contains multiple rows)
- Dynamic UI generation

**Phase 4 Integration**:
- All 5 widgets are **already created** in Phase 3
- Phase 4 must: connect their signals to File Explorer handlers
- **No new widgets needed** - just wire existing ones!

---

### 2. **src/core/file_explorer_executor.py** (683 LOC) ⭐ CRITICAL

**Purpose**: Unified executor merging Browse + Search + Replace operations

**Key Classes**:

#### SearchMatch (lines 34-48)
- Dataclass storing match info: line, col, snippet
- **Memory Optimization** (v2.9.120): 
  - Snippet truncated to 200 chars max
  - context_before/after deprecated (3x memory reduction)

#### SearchResult (lines 50-57)
- Container: file_info, matches list, match_count
- Used by execute_search() to return results

#### UnifiedFileExplorerExecutor (lines 59-680) ⭐ MAIN CLASS

**Signals**:
- `progress(str)` - current file being processed
- `progress_detailed(int, int, str)` - current, total, message
- `done(dict)` - final results {files, stats}
- `error(str)` - error messages

**Methods**:

##### execute_browse() (lines 101-179)
- **Purpose**: List files with filters (no search)
- **Steps**:
  1. Use FileListExecutor.list_files()
  2. Apply type filter (files/dirs/any)
  3. Apply include/exclude globs
  4. Return SearchResult objects (empty matches)
- **Returns**: `{files: List[SearchResult], stats: dict}`

##### execute_search() (lines 181-354) ⭐ COMPLEX
- **Purpose**: Search by filename pattern AND/OR content
- **Steps**:
  1. Call execute_browse() to get base file list
  2. **OPTIMIZATION**: Apply non-content conditions EARLY (before I/O)
     - Separate conditions: early (size/ext/date) vs late (content)
     - Filters out files before reading content (huge performance gain!)
  3. Apply filename pattern filter (fnmatch)
  4. Read files and search content (_search_in_text)
  5. Apply content-based conditions LATE (after reading)
  6. Calculate statistics
- **Memory Protection** (v2.9.120):
  - MAX_TOTAL_MATCHES = 50,000 (global limit across all files)
  - MAX_MATCHES_PER_FILE = 10,000
  - Stops search if limits exceeded
- **Returns**: `{files: List[SearchResult], stats: dict}`

##### execute_replace() (lines 356-410)
- **Purpose**: Replace search query with replacement text
- **Args**: files (SearchResult list), search_query, replacement, preserve_case, replace_all, options
- **Steps**:
  1. Read file content
  2. Call _replace_in_text()
  3. Write modified content back
  4. Track: replaced_count, files_modified, errors
- **Returns**: `{replaced_count, files_modified, errors}`

##### _search_in_text() (lines 412-491) ⭐ CORE ALGORITHM
- **Purpose**: Search for query in text, return SearchMatch list
- **Features**:
  - Regex support with DoS protection (OWASP A03)
  - Case sensitivity option
  - Whole word matching
  - Line-by-line processing
  - Match count limits (10,000/file)
  - Error recovery (catches regex errors, continues)
- **Security**: Prevents ReDoS attacks with MAX_MATCHES_PER_FILE

##### _replace_in_text() (lines 493-554)
- **Purpose**: Replace query with replacement in text
- **Features**:
  - Regex support with DoS protection
  - Whole word matching
  - Preserve case option (_replace_preserve_case)
  - Replace first vs all
  - **BUG FIX** (v2.9.117): Escape backslashes in non-regex mode
- **Returns**: (new_text, count)

##### _replace_preserve_case() (lines 556-595)
- **Purpose**: Replace while preserving original case pattern
- **Logic**: 
  - ALL CAPS → replacement.upper()
  - all lowercase → replacement.lower()
  - First Upper → Capitalize first letter only
- **Used by**: _replace_in_text() when preserve_case=True

##### _apply_conditions() (lines 597-637)
- **Purpose**: Filter SearchResult list by advanced conditions
- **Logic**: AND (all match) vs OR (any match)
- **Used by**: execute_search() for LATE content conditions

##### _check_condition() (lines 639-680)
- **Purpose**: Check if single SearchResult matches condition
- **Supports**: filename, path, ext, size, mtime, content fields
- **Operators**: =, !=, contains, >, <, >=, <=

**Design Patterns**:
- Template Method (execute_* methods follow same structure)
- Strategy (different search/replace strategies)
- Observer (Qt signals for progress tracking)

**OWASP Security**:
- A03: Regex DoS prevention (MAX_MATCHES limits)
- Input validation (try/except on regex compile)
- Error recovery (continue on regex errors)

**Phase 4 Integration**:
- **Already integrated** in Phase 3!
- File Explorer already uses execute_browse() and execute_search()
- Phase 4 just needs to: ensure all widget signals connect correctly

---

### 3. **src/gui/widgets/collapsible_section.py** (182 LOC)

**Purpose**: Expandable/collapsible sections with smooth animations

**Key Features**:
- Click header to expand/collapse
- Smooth height animation (300ms, InOutQuad easing)
- Remembers state
- Customizable header colors

**Methods**:
- `setContent(widget)` - set content widget
- `setCollapsed(bool)` - set state without animation
- `setTitle(str)` - update header text
- `_toggle_collapsed()` - animate expand/collapse

**Phase 4 Usage**:
- Sections 3, 4, 5 are collapsible
- Sections 1, 2 always expanded

---

### 4. **src/gui/widgets/file_filter_panel.py** (392 LOC)

**Purpose**: UI panel for setting file filters (include/exclude globs, min/max size, dates)

**NOT STUDIED IN DETAIL** - Already exists, Phase 4 just reuses it in Section 3

---

### 5. **src/core/filters.py** (343 LOC)

**Purpose**: Advanced file filtering with conditions

**Key Components**:

#### Condition dataclass (lines 208-309)
- **Fields**: field, operator, value, scope_type, scope_value, case_sensitive, whole_word, use_regex
- **Methods**:
  - `_apply_string_matching()` - handles regex, case, whole word
  - `matches(path)` - check if file matches condition
- **Supported Fields**: filename, path, ext, size, mtime, content
- **Scope Types**: none, brackets, braces, parentheses, custom, tag, specific-tag, hierarchical

#### filter_files_by_conditions() (lines 312-343)
- **Purpose**: Filter file list by multiple conditions
- **Logic**: AND (all match) vs OR (any match)
- **Used by**: UnifiedFileExplorerExecutor.execute_search() for early filtering

#### Hierarchical Filtering (lines 25-204)
- **Purpose**: Extract content from HTML/XML with include/exclude rules
- **Syntax**: "include div#test1, exclude #test2, include #test3"
- **Functions**:
  - `parse_hierarchical_ranges()` - parse syntax
  - `apply_hierarchical_filter()` - apply rules
  - `extract_scope_content()` - extract based on scope type

**Phase 4 Integration**:
- ConditionsGrid widget creates Condition objects
- UnifiedFileExplorerExecutor uses filter_files_by_conditions() for early optimization
- **Early vs Late** separation critical for performance!

---

## 🎯 Key Insights for Phase 4

### What I Now Understand:

1. **Phase 4 Structure is Clear**:
   - TASKS.md line 118-123 defines EXACTLY what to do
   - Task 4.1: Implement unified search pipeline (1h)
   - Task 4.2: Unit tests for new components (30 min)

2. **All Components Already Exist**:
   - ✅ Widgets: search_widgets.py (Phase 3 created)
   - ✅ Executor: file_explorer_executor.py (Phase 2 created)
   - ✅ Filters: filters.py (existing)
   - ✅ UI: collapsible_section.py (existing)

3. **Phase 4 Actual Work**:
   - **NOT creating new code** - all components exist!
   - **IS connecting signals** - wire widgets to executor
   - **IS refactoring** - move widgets into correct sections
   - **IS testing** - unit tests for integration

4. **Unified Pipeline Already Works**:
   - execute_browse() - list files
   - execute_search() - search content
   - execute_replace() - replace text
   - All 3 methods already implemented and tested!

5. **Advanced Conditions Work**:
   - Early filtering (size/ext/date) = BEFORE content read
   - Late filtering (content) = AFTER content read
   - Huge performance optimization already implemented!

6. **Memory Optimizations Active**:
   - MAX_TOTAL_MATCHES = 50,000
   - MAX_SNIPPET_LENGTH = 200 chars
   - Prevents UI freezing on large searches

### Phase 4 Is Really About:

1. **Signal Connections** (TASKS.md lines 104-110):
   - FileNameQueryPanel.pattern_changed → trigger search
   - ContentQueryPanel.query_changed → update search params
   - SearchOptionsPanel.options_changed → update options
   - ReplacePanel.replace_first/all_requested → execute replace
   - ConditionsGrid.conditions_changed → filter results

2. **UI Layout** (TASKS.md lines 89-103):
   - Move existing widgets into 5 sections
   - Section 1: Directory & Type (always expanded)
   - Section 2: Search & Replace (always expanded) ← ADD search_widgets here
   - Section 3: Filters (collapsible) ← existing FileFilterPanel
   - Section 4: Advanced Conditions (collapsible) ← ADD ConditionsGrid here
   - Section 5: Presets (collapsible) ← existing PresetManager

3. **Executor Integration** (TASKS.md lines 111-116):
   - Replace FileListExecutor calls with UnifiedFileExplorerExecutor
   - Connect progress signals
   - Implement pause/cancel handlers

---

## 🔍 What Phase 4 is NOT:

- ❌ NOT creating search algorithm (already exists in _search_in_text)
- ❌ NOT creating replace logic (already exists in _replace_in_text)
- ❌ NOT creating condition filtering (already exists in filters.py)
- ❌ NOT creating widgets (already created in Phase 3)
- ❌ NOT creating executor (already created in Phase 2)

**Phase 4 is UI INTEGRATION, not algorithm implementation!**

---

## 🚀 Next Steps

Now that I understand Phase 4 clearly, I can:

1. **Option A**: Continue studying more code (Phase 5: Plugin system, Phase 6: Remaining files)
2. **Option B**: Ask user if I should work on fixes/improvements (per their focus)
3. **Option C**: Prepare for Phase 4 implementation (once user green-lights it)

**Current Understanding**: 100% clear on what Phase 4 needs to do  
**Blocker**: User wants fixes/improvements first, not new features

---

## 📊 Updated Study Progress

**Total Files Studied**: 52 files (47 previous + 5 this session)  
**Total LOC Studied**: 19,408 LOC (17,332 previous + 2,076 this session)  
**Code Coverage**: 26.5% of files (52/196), 50.1% of LOC (19,408/38,754)  
**Remaining**: 144 files, 19,346 LOC (49.9%)

---

**Status**: Session 12 complete ✅  
**Next**: Await user guidance on fixes/improvements or continue study
