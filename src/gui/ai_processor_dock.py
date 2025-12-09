"""
AI Processor Dock Widget - Enhanced Version

Provides UI for processing files with OpenAI (ChatGPT) or Google Gemini APIs.

New features:
- Persistent token counter (session + lifetime statistics)
- Automatic code fence removal from responses (```json, ```, etc.)
- Enhanced result display with cleaned output
- Statistics tracking across sessions
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QGridLayout, QLabel, QLineEdit, QCheckBox, QSpinBox, 
    QComboBox, QTextEdit, QPushButton, QGroupBox, QHBoxLayout,
    QSplitter, QWidget, QVBoxLayout, QScrollArea, QFrame, QFileDialog,
    QMessageBox
)
from PySide6.QtCore import Qt, QSettings
from .base_dock import StandardToolDock, ProcessorWorkerBase
from src.ai_processor import (
    OpenAIClient, GeminiClient, ClaudeClient, PerplexityClient, AVAILABLE_MODELS, 
    count_tokens, estimate_cost, has_internet, is_openai_available, is_gemini_available, 
    is_claude_available, process_multiple_files, save_results, 
    list_files_recursive as ai_list_files, extract_between_markers,
    list_openai_models, list_gemini_models, list_claude_models, list_perplexity_models
)
from src.core.filters import Condition, filter_files_by_conditions
from src.utils.advanced_conditions import get_conditions_from_ui, apply_conditions_to_files


class PathEntry(QWidget):
    """Widget for a single path entry with browse and remove buttons."""
    
    def __init__(self, path_number, on_remove_callback, parent=None):
        super().__init__(parent)
        self.path_number = path_number
        self.on_remove_callback = on_remove_callback
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        
        # Path label
        self.lbl_path = QLabel(f"Path {path_number}:")
        self.lbl_path.setMinimumWidth(60)
        
        # Path input
        self.ed_path = QLineEdit()
        self.ed_path.setPlaceholderText("Enter file or directory path")
        self.ed_path.setToolTip("Path to file or directory to process with AI | Ctrl+Shift+A to open AI Processor")
        
        # Browse button
        self.btn_browse = QPushButton("Browse")
        self.btn_browse.setMaximumWidth(80)
        self.btn_browse.setToolTip("Browse for file or directory | Ctrl+O to open file dialog")
        self.btn_browse.clicked.connect(self._browse)
        
        # Is file checkbox
        self.chk_is_file = QCheckBox("File")
        self.chk_is_file.setToolTip("Check if selecting a file, uncheck for directory | Ctrl+Shift+A to open AI Processor")
        
        # Remove button (disabled for first path)
        self.btn_remove = QPushButton("✕")
        self.btn_remove.setMaximumWidth(30)
        self.btn_remove.setStyleSheet("QPushButton { color: red; font-weight: bold; }")
        self.btn_remove.clicked.connect(self._remove)
        self.btn_remove.setEnabled(path_number > 1)
        
        layout.addWidget(self.lbl_path)
        layout.addWidget(self.ed_path)
        layout.addWidget(self.btn_browse)
        layout.addWidget(self.chk_is_file)
        layout.addWidget(self.btn_remove)
    
    def _browse(self):
        """Browse for file or directory."""
        if self.chk_is_file.isChecked():
            path, _ = QFileDialog.getOpenFileName(self, "Select File")
        else:
            path = QFileDialog.getExistingDirectory(self, "Select Directory")
        
        if path:
            self.ed_path.setText(path)
    
    def _remove(self):
        """Remove this path entry."""
        if self.on_remove_callback:
            self.on_remove_callback(self)
    
    def get_path(self):
        """Get the path value."""
        return self.ed_path.text().strip()
    
    def is_file(self):
        """Check if marked as file."""
        return self.chk_is_file.isChecked()


class AIProcessorWorker(ProcessorWorkerBase):
    """Background worker for AI file processing."""
    
    def __init__(self, files, prompt, client, max_bytes, line_by_line,
                 scope_filter_enabled=False, scope_start="", scope_end="",
                 scope_start_regex=False, scope_start_case=False,
                 scope_end_regex=False, scope_end_case=False):
        super().__init__()
        self.files = files
        self.prompt = prompt
        self.client = client
        self.max_bytes = max_bytes
        self.line_by_line = line_by_line
        self.scope_filter_enabled = scope_filter_enabled
        self.scope_start = scope_start
        self.scope_end = scope_end
        self.scope_start_regex = scope_start_regex
        self.scope_start_case = scope_start_case
        self.scope_end_regex = scope_end_regex
        self.scope_end_case = scope_end_case
    
    def run(self):
        try:
            responses = process_multiple_files(
                self.files,
                self.prompt,
                self.client,
                self.max_bytes,
                self.line_by_line,
                progress_callback=lambda msg: self.emit_progress(msg),
                interrupt_check=lambda: self.check_interrupt(),
                scope_filter_enabled=self.scope_filter_enabled,
                scope_start=self.scope_start,
                scope_end=self.scope_end,
                scope_start_regex=self.scope_start_regex,
                scope_start_case=self.scope_start_case,
                scope_end_regex=self.scope_end_regex,
                scope_end_case=self.scope_end_case
            )
            self.emit_success(responses)
        except Exception as e:
            self.emit_error(str(e))


class AIProcessorDock(StandardToolDock):
    """Dock widget for AI file processor with enhanced features."""
    
    def __init__(self, parent=None):
        # Initialize attributes BEFORE calling super().__init__()
        # This prevents AttributeError when _setup_ui() calls _update_stats_display()
        self.worker = None
        self.last_responses = []
        
        # Session stats
        self.session_input_tokens = 0
        self.session_output_tokens = 0
        
        # Lifetime stats (persistent)
        self.stats_file = Path.home() / '.clarify_ai_stats.json'
        self.lifetime_stats = self._load_lifetime_stats_early()
        
        # Models cache (persistent for 24h)
        self.models_cache_file = Path.home() / '.clarify_models_cache.json'
        self.models_cache = self._load_models_cache()
        
        # Code fence removal option
        self.remove_fences = True
        
        # NOW call parent __init__ which triggers _setup_ui()
        super().__init__("AI File Processor", parent)
    
    def _setup_ui(self):
        """Setup UI components."""
        # Create splitter for resizable layout
        splitter = QSplitter(Qt.Vertical)
        
        # Top widget for controls with scroll
        scroll_controls = QScrollArea()
        scroll_controls.setWidgetResizable(True)
        scroll_controls.setFrameShape(QFrame.NoFrame)
        
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        
        grid = QGridLayout()
        
        # Provider selection
        grid.addWidget(QLabel("AI Provider:"), 0, 0)
        self.combo_provider = QComboBox()
        self.combo_provider.addItems([
            "OpenAI (ChatGPT)", 
            "Google Gemini", 
            "Anthropic Claude",
            "Perplexity"
        ])
        self.combo_provider.currentIndexChanged.connect(self._on_provider_changed)
        self.combo_provider.setToolTip("Choose your AI provider (requires API key) | Ctrl+Shift+A to open AI Processor")
        grid.addWidget(self.combo_provider, 0, 1, 1, 2)
        
        # Model selection
        grid.addWidget(QLabel("Model:"), 1, 0)
        self.combo_model = QComboBox()
        self.combo_model.setToolTip("AI model to use (different models have different costs and capabilities) | Ctrl+Shift+A to open AI Processor")
        grid.addWidget(self.combo_model, 1, 1, 1, 2)
        
        # Refresh models button
        self.btn_refresh_models = QPushButton("🔄")
        self.btn_refresh_models.setMaximumWidth(40)
        self.btn_refresh_models.setToolTip("Refresh models list from API | Ctrl+Shift+A to open AI Processor")
        self.btn_refresh_models.clicked.connect(self._refresh_models)
        grid.addWidget(self.btn_refresh_models, 1, 3)
        
        # API Key
        grid.addWidget(QLabel("API Key:"), 2, 0)
        self.ed_api_key = QLineEdit()
        self.ed_api_key.setEchoMode(QLineEdit.Password)
        self.ed_api_key.setPlaceholderText("Enter API key")
        self.ed_api_key.setToolTip("Your API key from the AI provider's dashboard (kept secure, never stored) | Ctrl+Shift+A to open AI Processor")
        self.btn_verify = QPushButton("Verify")
        self.btn_verify.clicked.connect(self._verify_key)
        self.btn_verify.setToolTip("Test if your API key is valid and working | Ctrl+Shift+A to open AI Processor")
        grid.addWidget(self.ed_api_key, 2, 1, 1, 3)
        grid.addWidget(self.btn_verify, 2, 4)
        
        # Prompt
        grid.addWidget(QLabel("Prompt:"), 3, 0)
        self.ed_prompt = QTextEdit()
        self.ed_prompt.setPlaceholderText("Enter instructions for AI (e.g., 'Analyze this code and suggest improvements')")
        self.ed_prompt.setToolTip("Enter AI processing instructions (one per line for line-by-line mode) | Ctrl+Shift+A to open AI Processor")
        self.ed_prompt.setMaximumHeight(100)
        grid.addWidget(self.ed_prompt, 3, 1, 1, 4)
        
        controls_layout.addLayout(grid)
        
        # Multiple paths section (in group box with scroll area)
        paths_group = QGroupBox("File Paths")
        paths_group_layout = QVBoxLayout()
        
        # Scroll area for path entries
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll.setFrameShape(QFrame.StyledPanel)
        
        paths_container = QWidget()
        self.paths_layout = QVBoxLayout(paths_container)
        self.paths_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll.setWidget(paths_container)
        paths_group_layout.addWidget(scroll)
        
        # Add path button
        btn_add_path = QPushButton("+ Add Path")
        btn_add_path.setToolTip("Add another file or directory path to process | Ctrl+Shift+A to open AI Processor")
        btn_add_path.clicked.connect(self._add_path_entry)
        btn_add_path.setMaximumWidth(120)
        paths_group_layout.addWidget(btn_add_path)
        
        paths_group.setLayout(paths_group_layout)
        controls_layout.addWidget(paths_group)
        
        # Initialize with first path entry
        self.path_entries = []
        self._add_path_entry()
        
        # Options grid
        options_grid = QGridLayout()
        
        self.chk_line_by_line = QCheckBox("Line-by-line mode")
        self.chk_line_by_line.setToolTip("Use each line of prompt for each file cyclically | Ctrl+Shift+A to open AI Processor")
        options_grid.addWidget(self.chk_line_by_line, 0, 0, 1, 2)
        
        lbl_max, self.spin_max_bytes = self.create_spinbox_input(
            "Max bytes:", 1000, 10000000, 1000000, 100000
        )
        self.spin_max_bytes.setToolTip("Maximum file size to process (bytes) | Ctrl+Shift+A to open AI Processor")
        options_grid.addWidget(lbl_max, 1, 0)
        options_grid.addWidget(self.spin_max_bytes, 1, 1)
        
        options_grid.addWidget(QLabel("Extensions:"), 1, 2)
        self.ed_extensions = QLineEdit()
        self.ed_extensions.setText(".txt,.py,.js,.ts,.jsx,.tsx")
        self.ed_extensions.setPlaceholderText("Comma-separated (e.g., .txt,.py)")
        self.ed_extensions.setToolTip("File extensions to process (comma-separated, e.g., .txt,.py,.js) | Ctrl+Shift+A to open AI Processor")
        options_grid.addWidget(self.ed_extensions, 1, 3, 1, 2)
        
        controls_layout.addLayout(options_grid)
        
        # Scope filter section
        scope_group = QGroupBox("Scope Filter")
        scope_layout = QGridLayout()
        
        self.chk_scope_enable = QCheckBox("Enable")
        self.chk_scope_enable.setToolTip("Extract only content between start/end markers | Ctrl+Shift+A to open AI Processor")
        scope_layout.addWidget(self.chk_scope_enable, 0, 0, 1, 2)
        
        scope_layout.addWidget(QLabel("Start:"), 1, 0)
        self.ed_scope_start = QLineEdit()
        self.ed_scope_start.setPlaceholderText("e.g., { or <div>")
        self.ed_scope_start.setToolTip("Starting marker to extract content from (e.g., '{' or '<div>') | Ctrl+Shift+A to open AI Processor")
        scope_layout.addWidget(self.ed_scope_start, 1, 1, 1, 2)
        
        self.chk_start_regex = QCheckBox("Regex")
        self.chk_start_regex.setToolTip("Treat start marker as regex pattern | Ctrl+Shift+A to open AI Processor")
        self.chk_start_case = QCheckBox("Case sensitive")
        self.chk_start_case.setToolTip("Case sensitive matching for start marker | Ctrl+Shift+A to open AI Processor")
        scope_layout.addWidget(self.chk_start_regex, 1, 3)
        scope_layout.addWidget(self.chk_start_case, 1, 4)
        
        scope_layout.addWidget(QLabel("End:"), 2, 0)
        self.ed_scope_end = QLineEdit()
        self.ed_scope_end.setPlaceholderText("e.g., } or </div>")
        self.ed_scope_end.setToolTip("Ending marker to extract content to (e.g., '}' or '</div>') | Ctrl+Shift+A to open AI Processor")
        scope_layout.addWidget(self.ed_scope_end, 2, 1, 1, 2)
        
        self.chk_end_regex = QCheckBox("Regex")
        self.chk_end_regex.setToolTip("Treat end marker as regex pattern | Ctrl+Shift+A to open AI Processor")
        self.chk_end_case = QCheckBox("Case sensitive")
        self.chk_end_case.setToolTip("Case sensitive matching for end marker | Ctrl+Shift+A to open AI Processor")
        scope_layout.addWidget(self.chk_end_regex, 2, 3)
        scope_layout.addWidget(self.chk_end_case, 2, 4)
        
        scope_group.setLayout(scope_layout)
        controls_layout.addWidget(scope_group)
        
        # Advanced Conditions section (Task #51 - v2.9.26)
        adv_cond_group = QGroupBox("Advanced File Filters (Optional)")
        adv_cond_group.setCheckable(True)
        adv_cond_group.setChecked(False)
        adv_cond_group.setToolTip("Filter files by filename, size, date, content patterns, etc. | Ctrl+Shift+A to open AI Processor")
        adv_cond_layout = QGridLayout()
        
        # Logic operator
        adv_cond_layout.addWidget(QLabel("Logic:"), 0, 0)
        self.combo_cond_logic = QComboBox()
        self.combo_cond_logic.addItems(["AND", "OR"])
        self.combo_cond_logic.setToolTip("AND: All conditions must match | OR: At least one must match | Ctrl+Shift+A to open AI Processor")
        adv_cond_layout.addWidget(self.combo_cond_logic, 0, 1, 1, 2)
        
        # Headers
        adv_cond_layout.addWidget(QLabel("Field"), 1, 0)
        adv_cond_layout.addWidget(QLabel("Operator"), 1, 1)
        adv_cond_layout.addWidget(QLabel("Value"), 1, 2)
        adv_cond_layout.addWidget(QLabel("Scope"), 1, 3)
        adv_cond_layout.addWidget(QLabel("Case"), 1, 4)
        adv_cond_layout.addWidget(QLabel("Regex"), 1, 5)
        
        # 3 condition rows (minimum)
        self.cond_rows = []
        for row in range(3):
            # Field combo
            combo_field = QComboBox()
            combo_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])
            combo_field.setToolTip("Select field to filter on | Ctrl+Shift+A to open AI Processor")
            
            # Operator combo
            combo_op = QComboBox()
            combo_op.addItems(["", "contains", "not contains", "equals", "not equals", 
                              "starts with", "ends with", ">", "<", ">=", "<="])
            combo_op.setToolTip("Select comparison operator | Ctrl+Shift+A to open AI Processor")
            
            # Value input
            ed_value = QLineEdit()
            ed_value.setPlaceholderText("Filter value")
            ed_value.setToolTip("Value to compare against (use regex if checkbox enabled) | Ctrl+Shift+A to open AI Processor")
            
            # Scope combo
            combo_scope = QComboBox()
            combo_scope.addItems(["none", "brackets", "braces", "parentheses", 
                                 "custom", "tag", "specific-tag", "hierarchical"])
            combo_scope.setToolTip("Scope for content field (e.g., only search within {} or tags) | Ctrl+Shift+A to open AI Processor")
            
            # Case sensitive checkbox
            chk_case = QCheckBox()
            chk_case.setChecked(True)
            chk_case.setToolTip("Case sensitive matching | Ctrl+Shift+A to open AI Processor")
            
            # Regex checkbox
            chk_regex = QCheckBox()
            chk_regex.setToolTip("Use value as regex pattern | Ctrl+Shift+A to open AI Processor")
            
            # Add to grid (row + 2 because of headers)
            grid_row = row + 2
            adv_cond_layout.addWidget(combo_field, grid_row, 0)
            adv_cond_layout.addWidget(combo_op, grid_row, 1)
            adv_cond_layout.addWidget(ed_value, grid_row, 2)
            adv_cond_layout.addWidget(combo_scope, grid_row, 3)
            adv_cond_layout.addWidget(chk_case, grid_row, 4)
            adv_cond_layout.addWidget(chk_regex, grid_row, 5)
            
            self.cond_rows.append((combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex))
        
        # Add buttons: Add Condition and Clear All (v2.9.40.3: store reference)
        self.buttons_layout_ref = QHBoxLayout()
        btn_add_cond = QPushButton("➕ Add Condition")
        btn_add_cond.setToolTip("Add more condition rows (no limit) | Ctrl+Shift+A to open AI Processor")
        btn_add_cond.clicked.connect(self._add_condition_row)
        self.buttons_layout_ref.addWidget(btn_add_cond)
        
        btn_clear_cond = QPushButton("🗑️ Clear All")
        btn_clear_cond.setToolTip("Clear all conditions | Ctrl+Shift+A to open AI Processor")
        btn_clear_cond.clicked.connect(self._clear_all_conditions)
        self.buttons_layout_ref.addWidget(btn_clear_cond)
        self.buttons_layout_ref.addStretch()
        
        adv_cond_layout.addLayout(self.buttons_layout_ref, 5, 0, 1, 6)  # Will be moved by _add_condition_row
        
        adv_cond_group.setLayout(adv_cond_layout)
        controls_layout.addWidget(adv_cond_group)
        
        # Store reference to group for enable/disable
        self.adv_cond_group = adv_cond_group
        self.adv_cond_grid = adv_cond_layout
        self.next_cond_row = 5  # Next available row after initial 3
        
        # Action buttons
        buttons = [
            ("Process", self._process),
            ("Interrupt", self._interrupt),
            ("Save Results", self._save_results),
            ("Clear", self._clear)
        ]
        btn_layout = self.create_action_buttons(buttons)
        self.btn_interrupt.setEnabled(False)
        
        # Add tooltips to action buttons (v2.9.48)
        self.btn_process.setToolTip("Process files with AI using specified settings | F5 to execute | Ctrl+Shift+A to open AI Processor")
        self.btn_interrupt.setToolTip("Interrupt current AI processing | Esc to cancel | Ctrl+Shift+A to open AI Processor")
        self.btn_save_results.setToolTip("Save AI processing results to file | Ctrl+Shift+A to open AI Processor")
        self.btn_clear.setToolTip("Clear all results and reset state | Ctrl+L | Ctrl+Shift+A to open AI Processor")
        
        controls_layout.addLayout(btn_layout)
        
        # Statistics panel
        stats_group = QGroupBox("Statistics")
        stats_layout = QGridLayout()
        
        self.lbl_session_stats = QLabel("Session: 0 in / 0 out | $0.00")
        self.lbl_session_stats.setToolTip("Current session token usage: input tokens / output tokens | Estimated cost | Ctrl+Shift+A to open AI Processor")
        self.lbl_lifetime_stats = QLabel("Lifetime: 0 in / 0 out | $0.00")
        self.lbl_lifetime_stats.setToolTip("Lifetime total token usage across all sessions | Estimated cumulative cost | Ctrl+Shift+A to open AI Processor")
        
        stats_layout.addWidget(QLabel("💬"), 0, 0)
        stats_layout.addWidget(self.lbl_session_stats, 0, 1)
        stats_layout.addWidget(QLabel("🌍"), 1, 0)
        stats_layout.addWidget(self.lbl_lifetime_stats, 1, 1)
        
        # Code fence removal option
        self.chk_remove_fences = QCheckBox("Remove code fences (```) from output")
        self.chk_remove_fences.setChecked(True)
        self.chk_remove_fences.setToolTip("Automatically strip ```json and ``` from responses | Ctrl+Shift+A to open AI Processor")
        stats_layout.addWidget(self.chk_remove_fences, 2, 0, 1, 2)
        
        stats_group.setLayout(stats_layout)
        controls_layout.addWidget(stats_group)
        
        # Set scroll widget and add to splitter
        scroll_controls.setWidget(controls_widget)
        splitter.addWidget(scroll_controls)
        
        # Results panel in bottom part of splitter
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        lbl_results, self.text_results = self.create_results_panel()
        results_layout.addWidget(lbl_results)
        results_layout.addWidget(self.text_results)
        
        # Open in Editor button (Task #6 - v2.9.19)
        editor_btn_layout = QHBoxLayout()
        self.add_open_in_editor_button(self.text_results, editor_btn_layout)
        results_layout.addLayout(editor_btn_layout)
        
        splitter.addWidget(results_widget)
        
        # Set initial splitter sizes (40% controls, 60% results)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        
        # Add splitter to main layout
        self.layout.addWidget(splitter)
        
        # Update stats display
        self._update_stats_display()
        
        # Initialize provider
        self._on_provider_changed()
        
        # Load advanced conditions preferences (Task #51 - v2.9.26)
        self._load_advanced_conditions_preferences()
    
    def _add_path_entry(self):
        """Add a new path entry."""
        path_number = len(self.path_entries) + 1
        entry = PathEntry(path_number, self._remove_path_entry, self)
        self.path_entries.append(entry)
        self.paths_layout.addWidget(entry)
    
    def _remove_path_entry(self, entry):
        """Remove a path entry."""
        if len(self.path_entries) <= 1:
            self.show_warning("Cannot Remove", "At least one path is required")
            return
        
        self.path_entries.remove(entry)
        entry.deleteLater()
        
        # Renumber remaining entries
        for i, e in enumerate(self.path_entries, 1):
            e.path_number = i
            e.lbl_path.setText(f"Path {i}:")
            e.btn_remove.setEnabled(i > 1)
    
    def _connect_signals(self):
        """Connect signals."""
        self._setup_enter_key_execution(self.ed_api_key, self.ed_extensions)
    
    def _load_models_cache(self):
        """Load models cache from file."""
        if not self.models_cache_file.exists():
            return {}
        
        try:
            with open(self.models_cache_file, 'r') as f:
                cache = json.load(f)
                # Validate cache age (24h expiry)
                if 'timestamp' in cache:
                    cached_time = datetime.fromisoformat(cache['timestamp'])
                    if datetime.now() - cached_time < timedelta(hours=24):
                        return cache.get('models', {})
                return {}
        except Exception:
            return {}
    
    def _save_models_cache(self, models_dict):
        """Save models cache to file."""
        try:
            cache = {
                'timestamp': datetime.now().isoformat(),
                'models': models_dict
            }
            with open(self.models_cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception:
            pass
    
    def _refresh_models(self):
        """Refresh models list from API."""
        api_key = self.ed_api_key.text().strip()
        if not api_key:
            self.show_warning("No API Key", "Please enter an API key first")
            return
        
        provider = self.combo_provider.currentText()
        self.show_info("Refreshing...", f"Fetching models from {provider}")
        
        try:
            if "OpenAI" in provider:
                models = list_openai_models(api_key)
                provider_key = 'openai'
            elif "Gemini" in provider:
                models = list_gemini_models(api_key)
                provider_key = 'gemini'
            elif "Claude" in provider:
                models = list_claude_models(api_key)
                provider_key = 'claude'
            elif "Perplexity" in provider:
                models = list_perplexity_models(api_key)
                provider_key = 'perplexity'
            else:
                return
            
            if models:
                # Update cache
                self.models_cache[provider_key] = models
                self._save_models_cache(self.models_cache)
                
                # Refresh UI
                self._on_provider_changed()
                self.show_info("Success", f"Found {len(models)} models")
            else:
                self.show_warning("No Models", "No models found. Check API key.")
        except Exception as e:
            self.show_error("Error", f"Failed to refresh models: {str(e)}")
    
    def _on_provider_changed(self):
        """Handle provider change."""
        provider = self.combo_provider.currentText()
        self.combo_model.clear()
        
        # Determine provider key
        if "OpenAI" in provider:
            provider_key = 'openai'
            if not is_openai_available():
                self.show_warning("SDK Missing", "OpenAI SDK not installed.\nRun: pip install openai")
        elif "Gemini" in provider:
            provider_key = 'gemini'
            if not is_gemini_available():
                self.show_warning("SDK Missing", "Gemini SDK not installed.\nRun: pip install google-generativeai")
        elif "Claude" in provider:
            provider_key = 'claude'
            if not is_claude_available():
                self.show_warning("SDK Missing", "Claude SDK not installed.\nRun: pip install anthropic")
        elif "Perplexity" in provider:
            provider_key = 'perplexity'
            if not is_openai_available():
                self.show_warning("SDK Missing", "OpenAI SDK not installed (required for Perplexity).\nRun: pip install openai")
        else:
            return
        
        # Load models from cache first, fallback to static list
        models = self.models_cache.get(provider_key, AVAILABLE_MODELS.get(provider_key, []))
        
        for model in models:
            self.combo_model.addItem(model['label'], model['name'])
    
    def _verify_key(self):
        """Verify API key."""
        api_key = self.ed_api_key.text().strip()
        if not api_key:
            self.show_warning("No Key", "Please enter an API key")
            return
        
        if not has_internet():
            self.show_warning("No Internet", "No internet connection detected")
            return
        
        provider = self.combo_provider.currentText()
        model_name = self.combo_model.currentData()
        
        try:
            if "OpenAI" in provider:
                client = OpenAIClient(api_key, model_name)
            elif "Gemini" in provider:
                client = GeminiClient(api_key, model_name)
            elif "Claude" in provider:
                client = ClaudeClient(api_key, model_name)
            elif "Perplexity" in provider:
                client = PerplexityClient(api_key, model_name)
            else:
                raise ValueError(f"Unknown provider: {provider}")
            
            ok, msg = client.verify_key()
            if ok:
                self.show_info("Success", msg)
            else:
                self.show_warning("Verification Failed", msg)
        except Exception as e:
            self.show_error("Error", f"Verification error: {str(e)}")
    
    def _get_client(self):
        """Get AI client."""
        api_key = self.ed_api_key.text().strip()
        if not api_key:
            raise ValueError("No API key provided")
        
        provider = self.combo_provider.currentText()
        model_name = self.combo_model.currentData()
        
        if "OpenAI" in provider:
            return OpenAIClient(api_key, model_name)
        elif "Gemini" in provider:
            return GeminiClient(api_key, model_name)
        elif "Claude" in provider:
            return ClaudeClient(api_key, model_name)
        elif "Perplexity" in provider:
            return PerplexityClient(api_key, model_name)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _get_files(self):
        """Get list of files to process from all path entries."""
        all_files = []
        ext_text = self.ed_extensions.text().strip()
        extensions = [e.strip() for e in ext_text.split(',') if e.strip()] if ext_text else []
        
        for entry in self.path_entries:
            path = entry.get_path()
            if not path:
                continue
            
            if entry.is_file():
                if not os.path.isfile(path):
                    raise ValueError(f"Not a file: {path}")
                all_files.append(path)
            else:
                if not os.path.isdir(path):
                    raise ValueError(f"Not a directory: {path}")
                
                dir_files = ai_list_files(path, extensions)
                if dir_files:
                    all_files.extend(dir_files)
        
        if not all_files:
            raise ValueError("No files found in any path")
        
        return all_files
    
    def _process(self):
        """Start processing."""
        try:
            prompt = self.ed_prompt.toPlainText().strip()
            if not prompt:
                self.show_warning("No Prompt", "Please enter a prompt")
                return
            
            client = self._get_client()
            files = self._get_files()
            
            # Apply advanced conditions BEFORE processing (Task #51 - v2.9.26)
            original_count = len(files)
            filtered_files, filtered_out = self._apply_advanced_conditions(files)
            
            # Check if any files remain after filtering
            if not filtered_files:
                self.show_warning(
                    "No Files Match Filters",
                    f"All {original_count} file(s) were filtered out by advanced conditions.\n"
                    "Please adjust your filters and try again."
                )
                return
            
            # Show feedback about filtering
            if filtered_out > 0:
                filter_msg = (
                    f"📊 Filtering: {len(filtered_files)} of {original_count} file(s) "
                    f"({filtered_out} filtered out)\n"
                )
            else:
                filter_msg = f"📊 Processing {len(filtered_files)} file(s) (no filters applied)\n"
            
            # Don't reset session stats - accumulate
            self.last_responses = []
            
            # Start worker with filtered files
            self.worker = AIProcessorWorker(
                filtered_files,  # Use filtered list instead of original
                prompt,
                client,
                self.spin_max_bytes.value(),
                self.chk_line_by_line.isChecked(),
                scope_filter_enabled=self.chk_scope_enable.isChecked(),
                scope_start=self.ed_scope_start.text().strip(),
                scope_end=self.ed_scope_end.text().strip(),
                scope_start_regex=self.chk_start_regex.isChecked(),
                scope_start_case=self.chk_start_case.isChecked(),
                scope_end_regex=self.chk_end_regex.isChecked(),
                scope_end_case=self.chk_end_case.isChecked()
            )
            self.worker.progress.connect(self._on_progress)
            self.worker.finished_ok.connect(self._on_finished)
            self.worker.failed.connect(self._on_failed)
            
            self.btn_process.setEnabled(False)
            self.btn_interrupt.setEnabled(True)
            self.clear_results(self.text_results)
            self.append_result(self.text_results, filter_msg)
            
            # Save preferences for next session
            self._save_advanced_conditions_preferences()
            
            self.worker.start()
            
        except Exception as e:
            self.show_error("Error", str(e))
    
    def _interrupt(self):
        """Interrupt processing."""
        if self.worker and self.worker.isRunning():
            self.worker.request_interrupt()
            self.append_result(self.text_results, "\n⚠️ Interrupt requested...")
    
    def _on_progress(self, msg):
        """Handle progress update with enhanced features."""
        if msg:
            # Remove code fences if option is enabled
            if self.chk_remove_fences.isChecked():
                cleaned_msg = self._strip_code_fences(msg)
                display_msg = cleaned_msg if cleaned_msg != msg else msg
            else:
                display_msg = msg
            
            self.append_result(self.text_results, display_msg)
            
            # Update token stats for actual responses (not status messages)
            if not msg.startswith('[') and not msg.startswith('✓') and not msg.startswith('Reading') and not msg.startswith('⚠'):
                model = self.combo_model.currentData() or 'gpt-4o'
                input_tok = count_tokens(self.ed_prompt.toPlainText(), model)
                output_tok = count_tokens(msg, model)
                
                # Update session stats
                self.session_input_tokens += input_tok
                self.session_output_tokens += output_tok
                
                # Update lifetime stats
                self.lifetime_stats['total_input_tokens'] += input_tok
                self.lifetime_stats['total_output_tokens'] += output_tok
                self.lifetime_stats['total_requests'] = self.lifetime_stats.get('total_requests', 0) + 1
                
                # Calculate costs
                session_cost = estimate_cost(self.session_input_tokens, self.session_output_tokens, model)
                lifetime_cost_increment = estimate_cost(input_tok, output_tok, model)
                self.lifetime_stats['total_cost'] = self.lifetime_stats.get('total_cost', 0.0) + lifetime_cost_increment
                
                # Update display
                self._update_stats_display()
                
                # Save lifetime stats periodically
                self._save_lifetime_stats()
    
    def _on_finished(self, responses):
        """Handle completion."""
        self.last_responses = responses
        self.append_result(self.text_results, f"\n✅ Processing complete! {len(responses)} response(s) received.")
        self.btn_process.setEnabled(True)
        self.btn_interrupt.setEnabled(False)
    
    def _on_failed(self, error):
        """Handle failure."""
        self.append_result(self.text_results, f"\n❌ Error: {error}")
        self.btn_process.setEnabled(True)
        self.btn_interrupt.setEnabled(False)
    
    def _save_results(self):
        """Save results to file."""
        if not self.last_responses:
            self.show_warning("No Results", "No results to save")
            return
        
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Save results", "",
            "Text files (*.txt);;All files (*)"
        )
        if path:
            try:
                save_results(self.last_responses, path, mode='write')
                self.show_info("Saved", f"Results saved to {path}")
            except Exception as e:
                self.show_error("Save Error", str(e))
    
    def _clear(self):
        """Clear results."""
        self.clear_results(self.text_results)
        self.last_responses = []
        self.session_input_tokens = 0
        self.session_output_tokens = 0
        self._update_stats_display()
    
    def _execute_action(self):
        """Execute the main action when ENTER is pressed."""
        self._process()
    
    # ==================== Advanced Conditions (Task #51 - v2.9.26) ====================
    
    def _add_condition_row(self):
        """Add a new condition row dynamically."""
        row_num = self.next_cond_row
        
        # Create widgets
        combo_field = QComboBox()
        combo_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])
        combo_field.setToolTip("Select field to filter on")
        
        combo_op = QComboBox()
        combo_op.addItems(["", "contains", "not contains", "equals", "not equals", 
                          "starts with", "ends with", ">", "<", ">=", "<="])
        combo_op.setToolTip("Select comparison operator")
        
        ed_value = QLineEdit()
        ed_value.setPlaceholderText("Filter value")
        
        combo_scope = QComboBox()
        combo_scope.addItems(["none", "brackets", "braces", "parentheses", 
                             "custom", "tag", "specific-tag", "hierarchical"])
        combo_scope.setToolTip("Scope for content field")
        
        chk_case = QCheckBox()
        chk_case.setChecked(True)
        chk_case.setToolTip("Case sensitive matching")
        
        chk_regex = QCheckBox()
        chk_regex.setToolTip("Use value as regex pattern")
        
        # Add to grid
        self.adv_cond_grid.addWidget(combo_field, row_num, 0)
        self.adv_cond_grid.addWidget(combo_op, row_num, 1)
        self.adv_cond_grid.addWidget(ed_value, row_num, 2)
        self.adv_cond_grid.addWidget(combo_scope, row_num, 3)
        self.adv_cond_grid.addWidget(chk_case, row_num, 4)
        self.adv_cond_grid.addWidget(chk_regex, row_num, 5)
        
        # Store reference
        self.cond_rows.append((combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex))
        
        # Increment next row
        self.next_cond_row += 1
        
        # Move buttons layout to new bottom position (v2.9.40.3)
        self.adv_cond_grid.removeItem(self.buttons_layout_ref)
        self.adv_cond_grid.addLayout(self.buttons_layout_ref, self.next_cond_row, 0, 1, 6)
    
    def _clear_all_conditions(self):
        """Clear all condition fields."""
        for combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex in self.cond_rows:
            combo_field.setCurrentIndex(0)
            combo_op.setCurrentIndex(0)
            ed_value.clear()
            combo_scope.setCurrentIndex(0)
            chk_case.setChecked(True)
            chk_regex.setChecked(False)
    
    def _get_conditions(self) -> list[Condition]:
        """
        Build list of Condition objects from UI.
        (Delegated to shared module for reusability)
        """
        return get_conditions_from_ui(self.cond_rows)
    
    def _apply_advanced_conditions(self, files: list[str]) -> tuple[list[str], int]:
        """
        Apply advanced conditions to file list.
        (Delegated to shared module for reusability)
        Returns: (filtered_files, num_filtered_out)
        """
        conditions = self._get_conditions()
        logic_op = self.combo_cond_logic.currentText()
        enabled = self.adv_cond_group.isChecked()
        
        return apply_conditions_to_files(files, conditions, logic_op, enabled)
    
    def _save_advanced_conditions_preferences(self):
        """Save advanced conditions state to QSettings."""
        settings = QSettings("Clarify", "AIProcessor")
        settings.setValue("adv_cond/enabled", self.adv_cond_group.isChecked())
        settings.setValue("adv_cond/logic", self.combo_cond_logic.currentText())
        
        # Save each condition row
        for i, (combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex) in enumerate(self.cond_rows):
            settings.setValue(f"adv_cond/row{i}/field", combo_field.currentText())
            settings.setValue(f"adv_cond/row{i}/operator", combo_op.currentText())
            settings.setValue(f"adv_cond/row{i}/value", ed_value.text())
            settings.setValue(f"adv_cond/row{i}/scope", combo_scope.currentText())
            settings.setValue(f"adv_cond/row{i}/case", chk_case.isChecked())
            settings.setValue(f"adv_cond/row{i}/regex", chk_regex.isChecked())
        
        settings.setValue("adv_cond/row_count", len(self.cond_rows))
    
    def _load_advanced_conditions_preferences(self):
        """Load advanced conditions state from QSettings."""
        settings = QSettings("Clarify", "AIProcessor")
        
        # Load enabled state
        enabled = settings.value("adv_cond/enabled", False, type=bool)
        self.adv_cond_group.setChecked(enabled)
        
        # Load logic operator
        logic = settings.value("adv_cond/logic", "AND", type=str)
        index = self.combo_cond_logic.findText(logic)
        if index >= 0:
            self.combo_cond_logic.setCurrentIndex(index)
        
        # Load condition rows
        row_count = settings.value("adv_cond/row_count", 0, type=int)
        for i in range(min(row_count, len(self.cond_rows))):
            combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex = self.cond_rows[i]
            
            field = settings.value(f"adv_cond/row{i}/field", "", type=str)
            operator = settings.value(f"adv_cond/row{i}/operator", "", type=str)
            value = settings.value(f"adv_cond/row{i}/value", "", type=str)
            scope = settings.value(f"adv_cond/row{i}/scope", "none", type=str)
            case = settings.value(f"adv_cond/row{i}/case", True, type=bool)
            regex = settings.value(f"adv_cond/row{i}/regex", False, type=bool)
            
            # Set values
            idx = combo_field.findText(field)
            if idx >= 0:
                combo_field.setCurrentIndex(idx)
            
            idx = combo_op.findText(operator)
            if idx >= 0:
                combo_op.setCurrentIndex(idx)
            
            ed_value.setText(value)
            
            idx = combo_scope.findText(scope)
            if idx >= 0:
                combo_scope.setCurrentIndex(idx)
            
            chk_case.setChecked(case)
            chk_regex.setChecked(regex)
    
    # ==================== Enhanced Features ====================
    
    def _load_lifetime_stats_early(self) -> dict:
        """Load lifetime statistics from file (early initialization)."""
        stats_file = Path.home() / '.clarify_ai_stats.json'
        try:
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_requests': 0,
            'total_cost': 0.0
        }
    
    def _load_lifetime_stats(self) -> dict:
        """Load lifetime statistics from file."""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_requests': 0,
            'total_cost': 0.0
        }
    
    def _save_lifetime_stats(self):
        """Save lifetime statistics to file."""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.lifetime_stats, f, indent=2)
        except Exception as e:
            print(f"Failed to save stats: {e}")
    
    def _update_stats_display(self):
        """Update statistics labels."""
        # Session stats
        session_cost = estimate_cost(
            self.session_input_tokens,
            self.session_output_tokens,
            self.combo_model.currentData() if self.combo_model.currentData() else 'gpt-4o'
        )
        self.lbl_session_stats.setText(
            f"Session: {self.session_input_tokens:,} in / {self.session_output_tokens:,} out | ${session_cost:.6f}"
        )
        
        # Lifetime stats
        lifetime_cost = self.lifetime_stats.get('total_cost', 0.0)
        self.lbl_lifetime_stats.setText(
            f"Lifetime: {self.lifetime_stats['total_input_tokens']:,} in / "
            f"{self.lifetime_stats['total_output_tokens']:,} out | ${lifetime_cost:.6f}"
        )
    
    def _strip_code_fences(self, text: str) -> str:
        """
        Remove code fences from text (improved with non-greedy matching).
        Handles patterns like:
        - ```json ... ```
        - ```python ... ```
        - ``` ... ```
        - Nested fences (improved)
        """
        if not text:
            return text
        
        stripped = text.strip()
        
        # Remove surrounding fences with optional language identifier (non-greedy)
        # Pattern: ```[language]\n content \n```
        pattern = r'^```[\w]*?\n(.+?)\n```$'
        match = re.match(pattern, stripped, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Remove inline fence blocks (non-greedy to handle nested cases)
        # This will match from the first ``` to the nearest closing ```
        text = re.sub(r'```[\w]*?\n(.+?)\n```', r'\1', stripped, flags=re.DOTALL)
        
        return text.strip()
