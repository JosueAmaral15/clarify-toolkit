# Code Study - Session 16: Important GUI Docks (Part 2)

**Date**: 2026-01-22  
**Programmer**: #4  
**Session Focus**: Medium-priority docks (JSON Rewriter, AI Processor, Set Operations)

---

## 📊 Session Statistics

**Files Studied**: 3 files (partial analysis)  
**Lines Studied**: ~1,500 LOC (focused reading)  
**Total Available**: 2,981 LOC (json_rewriter: 1,054, ai_processor: 1,193, set_operations: 734)  
**Time**: ~40 minutes  
**Coverage**: Architecture + key methods

---

## 📁 Files Analyzed

### 1. **src/gui/json_rewriter_dock.py** (1,054 LOC) ⭐ FEATURE-RICH

**Purpose**: Rewrite JSON/TS files with deduplication and formatting options

**Architecture**:
- Extends **BaseDock** (uses framework from Session 15)
- QGridLayout for compact option presentation
- QSettings for preference persistence
- **Accessibility support** (AccessibilityManager integration)

**Key Features** (18+ options!):

#### Input/Output
- Input file selection (.json, .ts, .tsx, .js, .jsx)
- Output file selection (optional - defaults to overwrite)
- "Is File" checkbox (file vs directory processing)

#### TypeScript Support
- `chk_from_ts` - Parse from TypeScript/JavaScript format
- `chk_ts_out` - Emit as TypeScript (`export default`)
- Preserves TypeScript format with `ts_process_full_preserving()`

#### Deduplication Options
- `chk_join` - Join duplicate keys into arrays
- `chk_elim` - Eliminate duplicates
- `chk_exclude_numeric` - Skip numeric keys from deduplication
- `chk_avoid_dup_child` - Avoid duplicate child keys
- `chk_remove_dup_consecutive` - Remove consecutive duplicates only
- `chk_remove_dup_all` - Remove all duplicates
- **Task #52**: `chk_remove_dup_objects` - Remove duplicate objects
  - `spin_dup_threshold` - Similarity threshold (50-100%)
  - `combo_dup_mode` - Remove vs Reference mode
  - `chk_include_dup_arrays` - Include arrays in deduplication

#### Array Operations
- `chk_convert_arrays` - Convert arrays to objects
- `chk_skip_no_siblings` - Skip items without siblings

#### Formatting
- `chk_nlb` - No blank lines
- `chk_normalize_escaping` - Normalize escape sequences
- `spin_indent` - Indentation level (-1 to 16, default: 2)
- `chk_skip_empty` - Skip empty values

#### Case Style Enforcement
- `chk_enforce_case` - Enforce consistent case style (default: enabled)
- `combo_case_style` - camelCase, PascalCase, snake_case, kebab-case
- `chk_validate_case` - Show validation dialog before processing
- **Validation flow**: Parse → Show warnings → User approves → Convert → Write

#### Reference Management (Sprint A v2.9.29)
- **Task #23**: `chk_update_refs` - Update orphaned references
  - `ed_project_dir` - Project directory for reference scanning
  - `btn_project_browse` - Browse for project directory
  - `chk_ref_backup` - Create backup before updating (default: enabled)
- `radio_delete_dups` - Delete duplicates mode (default)
- `radio_use_refs` - Use references mode
- `chk_resolve_refs` - Resolve references after processing
- **Sprint B Feature #4 v2.9.30**: `btn_configure_format` - Configure reference format
  - Reference format string (e.g., "$ref", "@ref")
  - Include line numbers in references
  - Use relative paths

#### Advanced Filtering (Sprint B Feature #1)
- `btn_advanced_filters` - Opens AdvancedFiltersDialog
- `chk_apply_all_types` - Apply filters to all file types
- `advanced_conditions` - Storage for Condition objects
- Integrates with `cli_dedupe()` via `advanced_conditions` parameter

**Key Methods**:

##### _rewrite() ⭐ MAIN EXECUTION (lines 524-738)
- **Validation**: Case validation dialog (if enabled)
- **Namespace construction**: Builds argparse.Namespace with 30+ options
- **Execution**: Calls `cli_dedupe()` from `src.core.cli_dedupe`
- **Returns**: output_text, substitution_map, removal_stats, detailed_stats
- **Task #23**: Updates orphaned references if enabled
  - Scans project directory recursively
  - Updates references using substitution_map
  - Creates backups if enabled
- **Task #52**: Handles duplicate object removal with similarity threshold
- **Sprint B Feature #3**: Displays detailed statistics (removal_stats)

##### _open_advanced_filters_dialog() (line 409)
- Opens modal dialog with Conditions UI
- Uses `get_conditions_from_ui()` utility
- Saves conditions to `self.advanced_conditions`
- Sets `self.advanced_filters_enabled` flag

##### _open_format_config_dialog() (line 310)
- Configure reference format ($ref, @ref, etc.)
- Include line numbers option
- Relative vs absolute paths
- Live preview with example
- Reset to defaults button

##### _load_preferences() / _save_preferences() (lines 738-825)
- QSettings persistence for 30+ options
- Saves: checkboxes, spinboxes, combos, advanced conditions
- Restores: last used configuration

**Design Patterns**:
- **Facade**: cli_dedupe wraps complex rewriter logic
- **Strategy**: Different deduplication modes (consecutive, all, objects)
- **Template Method**: BaseDock hooks
- **Memento**: QSettings for state persistence

**Integration Points**:
- ✅ **Filters** (Session 14): Condition class, filter_files_by_conditions()
- ✅ **Core**: cli_dedupe, rewriter module
- ✅ **Utilities**: format_removal_statistics, advanced_conditions
- ✅ **Accessibility**: AccessibilityManager integration

**Complexity**: This is one of the **most complex docks** (1,054 LOC, 30+ options)!

---

### 2. **src/gui/ai_processor_dock.py** (1,193 LOC) ⭐ AI INTEGRATION

**Purpose**: Process files with OpenAI ChatGPT, Google Gemini, Anthropic Claude, or Perplexity APIs

**Architecture**:
- Extends **StandardToolDock** (gets all mixins from base_dock!)
- **Splitter layout**: Resizable controls/results sections
- **Scroll areas**: For controls and multiple path entries
- **Worker thread**: AIProcessorWorker for async processing
- **Persistent stats**: Session + lifetime token/cost tracking

**Key Features**:

#### Provider Support (4 AI providers)
- **OpenAI ChatGPT**: GPT-4, GPT-3.5-turbo, etc.
- **Google Gemini**: gemini-pro, gemini-1.5-pro, etc.
- **Anthropic Claude**: claude-3-opus, claude-3-sonnet, etc.
- **Perplexity**: pplx-7b-online, pplx-70b-online, etc.

#### Model Selection
- `combo_provider` - Provider selection dropdown
- `combo_model` - Model selection (dynamic based on provider)
- `btn_refresh_models` - Refresh available models (calls API)
- **Model caching**: 24-hour cache in `~/.clarify_models_cache.json`

#### API Configuration
- `ed_api_key` - API key input (password field)
- `btn_verify` - Verify API key validity
- **Auto-detection**: Uses `has_openai_available()`, `has_gemini_available()`, etc.
- **Environment variables**: Checks OPENAI_API_KEY, GOOGLE_API_KEY, etc.

#### Prompt & Files
- `ed_prompt` - Multi-line prompt text editor
- **Template support**: `preview_template()`, `has_templates()`
- **Multiple paths**: Dynamic PathEntry widgets (add/remove)
- **Advanced conditions**: Filter files before processing
- **File discovery**: Recursive listing with filters

#### Processing Options
- Max tokens spinner
- Temperature spinner
- Batch size configuration
- Preserve code fences option
- **Interrupt support**: Escape key stops processing

#### Results & Statistics
- **Results display**: QTextEdit with search (Ctrl+F from ResultsOutputMixin)
- **Token tracking**: Session + lifetime statistics
- **Cost estimation**: Uses `estimate_cost()` function
- **Stats persistence**: `~/.clarify_ai_stats.json`
- **Auto fence removal**: Strips ```json, ```, etc. from responses

#### Advanced Features
- **Search/Replace in Results**: SearchReplacePanel integration
- **Insert in Prompt**: InsertPanel integration (line numbers + text/file modes)
- **History**: Save/load previous prompts
- **Export**: Save results to file
- **Store in Calculator**: Send results to Calculator dock (v2.9.98 signal)

**Key Methods**:

##### _process() ⭐ MAIN EXECUTION (line 707)
- Gets files from PathEntry widgets
- Applies advanced conditions
- Validates API key & prompt
- Estimates tokens & cost
- Creates AIProcessorWorker
- Starts async processing with progress updates

##### _refresh_models() (line 555)
- Calls provider-specific model listing (list_openai_models, etc.)
- Caches results for 24 hours
- Updates combo_model dropdown
- Shows error if API unavailable

##### _verify_key() (line 625)
- Creates provider client (OpenAIClient, GeminiClient, etc.)
- Tests connection
- Shows success/error message
- Validates API key format

##### _on_finished() (line 820)
- Receives responses from worker
- Removes code fences if enabled
- Updates token statistics
- Displays results
- Saves lifetime stats

##### _handle_replace_in_results() (line 859)
- Triggered by SearchReplacePanel
- Performs find/replace in results
- Updates display

##### _handle_insert_in_prompt() (line 901)
- Triggered by InsertPanel
- Inserts text/file content at line number
- Supports different insertion modes

##### _get_conditions() / _apply_advanced_conditions() (lines 982-1000)
- Collects Condition objects from UI
- Filters files using filter_files_by_conditions()
- Returns filtered list + removed count

**Design Patterns**:
- **Facade**: process_multiple_files wraps AI API calls
- **Strategy**: Different AI providers (OpenAI, Gemini, Claude, Perplexity)
- **Observer**: Qt signals for async progress
- **Worker Thread**: AIProcessorWorker prevents UI blocking
- **Singleton**: Statistics file shared across sessions
- **Template Method**: StandardToolDock inheritance

**Integration Points**:
- ✅ **Filters** (Session 14): Condition, filter_files_by_conditions()
- ✅ **AI Processor Core**: OpenAIClient, GeminiClient, etc.
- ✅ **Search/Replace** (Session 12): SearchReplacePanel, replace_in_text()
- ✅ **Insert**: InsertPanel, insert_at_line()
- ✅ **Widgets** (Session 13): PathEntry
- ✅ **Workers**: AIProcessorWorker for async execution
- ✅ **Calculator Dock** (signal): store_in_calculator_requested

**Complexity**: Very high (1,193 LOC, 4 AI providers, persistent stats, advanced filtering)!

---

### 3. **src/gui/set_operations_dock.py** (734 LOC) ⭐ MODULAR DESIGN

**Purpose**: JSON set operations (union, intersection, difference, symmetric difference)

**Architecture**:
- Extends **BaseDock**
- **Scroll area**: All controls in scrollable container
- **Modular widgets**: FileSelectionWidget, OperationOptionsWidget (from widgets/)
- **Executor pattern**: SetOperationExecutor handles logic
- **Exporter pattern**: ResultExporter handles output
- **History**: HistoryManager for operation history
- **Presets**: PresetsManager for saved configurations

**Key Features**:

#### File Selection
- **FileSelectionWidget**: Reusable file selector component
- JSON file filter (*.json)
- Supports multiple file selection

#### Operation Options
- **OperationOptionsWidget**: Reusable options panel
- Operations: Union, Intersection, Difference, Symmetric Difference
- Output format options
- Merge options

#### Action Buttons (12 buttons!)
- `btn_execute` - Execute operation
- `btn_save_preset` - Save current configuration
- `btn_clear` - Clear results
- `btn_save` - Save results to file
- `btn_export` - Export results (multiple formats)
- `btn_view_diff` - View diff visualization
- `btn_view_venn` - View Venn diagram
- `btn_merge` - Merge results
- `btn_store_calc` - Store in Calculator dock (v2.9.98 signal)
- `btn_batch` - Batch processing mode
- `btn_history` - View operation history
- `btn_presets` - Load saved presets

#### Results Display
- QTextEdit for results
- Statistics display
- Diff visualization support
- Venn diagram support

**Key Methods** (based on pattern):

##### _execute() (expected)
- Reads files via FileSelectionWidget
- Gets options from OperationOptionsWidget
- Calls SetOperationExecutor
- Displays results
- Updates history

##### _save_results() (expected)
- Uses ResultExporter
- Supports multiple formats (JSON, CSV, etc.)
- Save dialog integration

##### _view_diff() / _view_venn() (expected)
- Visualizations for set operations
- Diff: Show differences between sets
- Venn: Diagram of set relationships

##### _open_history() / _open_presets() (expected)
- Opens HistoryDialog or PresetsDialog
- Loads previous operation
- Applies preset configuration

**Design Patterns**:
- **Facade**: SetOperationExecutor wraps set logic
- **Strategy**: Different export formats (ResultExporter)
- **Memento**: History + Presets for state storage
- **Composite**: FileSelectionWidget + OperationOptionsWidget
- **Observer**: store_in_calculator_requested signal
- **Low Coupling**: Depends only on core set_operations logic (GRASP)

**Integration Points**:
- ✅ **Core** (Session 14): SetOperationExecutor, ResultExporter
- ✅ **Widgets**: FileSelectionWidget, OperationOptionsWidget
- ✅ **History**: HistoryManager, HistoryDialog
- ✅ **Presets**: PresetsManager, PresetsDialog
- ✅ **Calculator Dock** (signal): store_in_calculator_requested

**Code Quality**:
- Excellent modularity (widgets extracted to separate components)
- Clean separation of concerns (executor, exporter, history, presets)
- GRASP principles (Controller, Low Coupling)
- GoF patterns (Observer, Strategy, Facade, Memento)

---

## 🎯 Key Insights

### JSON Rewriter: Feature Density Champion

**json_rewriter_dock.py** is the **most feature-dense dock**:
- **30+ options** across 11 feature categories
- **3 major sprints** of features added (Sprint A, Sprint B Features 1-4)
- **Task integration**: Task #23 (orphaned refs), Task #52 (dup objects)
- **Advanced filtering**: Condition-based file filtering
- **Reference management**: Complex reference resolution system
- **Case validation**: Interactive validation dialog

**Trade-off**: Complexity vs Power. This dock is powerful but requires careful UX design.

### AI Processor: Multi-Provider Excellence

**ai_processor_dock.py** shows **excellent API abstraction**:
- **4 AI providers** with unified interface
- **Provider-agnostic design**: Switch providers without code changes
- **Intelligent caching**: 24-hour model cache reduces API calls
- **Cost tracking**: Session + lifetime statistics for budgeting
- **Resilient**: Handles API failures gracefully
- **Code fence removal**: Cleans LLM output automatically

**Pattern**: This is a **perfect example of Strategy pattern** - different providers, same interface!

### Set Operations: Modularity Masterclass

**set_operations_dock.py** demonstrates **excellent architecture**:
- **Reusable widgets**: FileSelectionWidget, OperationOptionsWidget extracted
- **Separation of concerns**: UI ← Executor ← Core Logic
- **History + Presets**: User experience enhancements
- **Signal-based integration**: Loosely coupled with Calculator dock
- **GRASP principles**: Controller, Low Coupling, High Cohesion

**Impact**: Adding new set operations or export formats is **trivial** due to modularity!

### Shared Patterns Across All Docks

**Common patterns observed**:
1. **BaseDock/StandardToolDock**: All docks inherit framework
2. **QSettings**: All use persistent preferences
3. **Tooltips**: All use tooltip_tr() for internationalization
4. **Worker threads**: Complex operations use async processing
5. **Scroll areas**: Large UIs use scrollable containers
6. **Modular widgets**: Reusable components extracted
7. **Accessibility**: AccessibilityManager integration

**Consistency**: This shows **excellent project architecture** with shared patterns!

---

## 📊 Updated Study Progress

**Session 16 Stats**:
- Files studied: 3 files (partial)
- LOC studied: ~1,500 LOC (focused reading)
- Total: json_rewriter (1,054), ai_processor (1,193), set_operations (734)

**Total Progress**:
- **Files**: 73/196 (37.2%)
- **LOC**: ~25,581/38,754 (66.0%)
- **Remaining**: 123 files (62.8%), ~13,173 LOC (34.0%)

**Milestone**: Crossed 2/3 mark! 66% code coverage achieved!

---

## 🚀 Next Steps

**Remaining Docks** (~9,500 LOC):
- calculator_dock.py (601 LOC)
- editor_dock.py (583 LOC) - Partial from Session 3
- json_search_dock.py (647 LOC) - Partial from Session 6
- comparison_dock.py, crypto_dock.py, encoding_dock.py, formatter_dock.py
- hash_dock.py, insert_dock.py, regex_dock.py, search_replace_dock.py
- template_dock.py, validator_dock.py, xpath_dock.py
- + more (~6,000 LOC)

**Options**:
- **A**: Continue dock studies (remaining docks)
- **B**: Complete Phase 4 implementation (10% remaining)
- **C**: Work on fixes/improvements (per user focus)

**Status**: Session 16 complete ✅  
**Key Finding**: All docks follow consistent patterns - framework is working beautifully!
