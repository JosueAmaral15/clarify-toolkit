"""
AI Processor Dock Widget - Enhanced Version

Provides UI for processing files with OpenAI (ChatGPT) or Google Gemini APIs.

New features:
- Persistent token counter (session + lifetime statistics)
- Automatic code fence removal from responses (```json, ```, etc.)
- Enhanced result display with cleaned output
- Statistics tracking across sessions
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=broad-exception-caught  # GUI robustness
# pylint: disable=import-outside-toplevel  # Lazy Qt imports
# pylint: disable=logging-fstring-interpolation  # F-strings clearer


import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

from PySide6.QtWidgets import (
    QGridLayout, QLabel, QLineEdit, QCheckBox,
    QComboBox, QTextEdit, QPushButton, QGroupBox, QHBoxLayout,
    QSplitter, QWidget, QVBoxLayout, QScrollArea, QFrame, QFileDialog,
    QMessageBox
)
from PySide6.QtCore import Qt, QSettings, QTimer

from src.ai_processor import (
    OpenAIClient, GeminiClient, ClaudeClient, PerplexityClient, OllamaClient, AVAILABLE_MODELS,
    count_tokens, estimate_cost, has_internet, is_openai_available, is_gemini_available,
    is_claude_available,
    list_files_recursive as ai_list_files,
    list_openai_models, list_gemini_models, list_claude_models, list_perplexity_models,
    list_ollama_models,
    preview_template, has_templates
)
from src.core.filters import Condition
from src.core.search_replace import SearchOptions
from src.gui.panels import SearchReplacePanel, InsertPanel
from src.gui.widgets import PathEntry
from src.gui.workers import (
    AIConditionRequest,
    AIFileDiscoveryPlan,
    AIPathTarget,
    AIProcessorWorker,
    AIPromptInsertPlan,
    AIPromptInsertWorker,
    AIResultReplacePlan,
    AIResultReplaceWorker,
    AIResultSavePlan,
    AIResultSaveWorker,
    MAX_AI_PROMPT_BYTES,
    MAX_AI_RESULT_TEXT_CHARS,
)
from src.i18n.translator import tr, tooltip_tr
from src.utils.advanced_conditions import get_conditions_from_ui, apply_conditions_to_files
from src.utils.logger import get_logger

from .base_dock import StandardToolDock

logger = get_logger(__name__)
_UNSET = object()


class AIProcessorDock(StandardToolDock):
    """Dock widget for AI file processor with enhanced features."""

    def __init__(self, parent=None):
        # Initialize attributes BEFORE calling super().__init__()
        # This prevents AttributeError when _setup_ui() calls _update_stats_display()
        self.worker = None
        self._worker_generation = 0
        self._worker_thread_id = f"ai-processor-{id(self)}"
        self._pending_worker_result = _UNSET
        self._pending_worker_error = None
        self._result_replace_worker = None
        self._result_replace_generation = 0
        self._result_replace_thread_id = f"ai-processor-result-replace-{id(self)}"
        self._pending_result_replace = _UNSET
        self._pending_result_replace_error = None
        self._prompt_insert_worker = None
        self._prompt_insert_generation = 0
        self._prompt_insert_thread_id = f"ai-processor-prompt-insert-{id(self)}"
        self._pending_prompt_insert = _UNSET
        self._pending_prompt_insert_error = None
        self._result_save_worker = None
        self._result_save_generation = 0
        self._result_save_thread_id = f"ai-processor-result-save-{id(self)}"
        self._pending_result_save = _UNSET
        self._pending_result_save_error = None
        self._cancel_requested = False
        self._discard_worker_callbacks = False
        self._close_action = None
        self._close_retry_timer = None
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
        self._close_retry_timer = QTimer(self)
        self._close_retry_timer.setSingleShot(True)
        self._close_retry_timer.setInterval(25)
        self._close_retry_timer.timeout.connect(self._retry_deferred_close)

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
        grid.addWidget(QLabel(tr("ai_processor.lbl_provider")), 0, 0)
        self.combo_provider = QComboBox()
        self.combo_provider.addItems([
            "OpenAI (ChatGPT)",
            "Google Gemini",
            "Anthropic Claude",
            "Perplexity",
            "Ollama (Local)",
        ])
        self.combo_provider.currentIndexChanged.connect(self._on_provider_changed)
        self.combo_provider.setToolTip(tooltip_tr("ai_processor.tooltip_provider"))
        grid.addWidget(self.combo_provider, 0, 1, 1, 2)

        # Model selection
        grid.addWidget(QLabel(tr("ai_processor.lbl_model")), 1, 0)
        self.combo_model = QComboBox()
        self.combo_model.setToolTip(tooltip_tr("ai_processor.tooltip_model"))
        grid.addWidget(self.combo_model, 1, 1, 1, 2)

        # Refresh models button
        self.btn_refresh_models = QPushButton(tr("ai_processor.btn_refresh"))
        self.btn_refresh_models.setMaximumWidth(40)
        self.btn_refresh_models.setToolTip(tooltip_tr("ai_processor.tooltip_refresh_models"))
        self.btn_refresh_models.clicked.connect(self._refresh_models)
        grid.addWidget(self.btn_refresh_models, 1, 3)

        # API Key
        grid.addWidget(QLabel(tr("ai_processor.lbl_api_key")), 2, 0)
        self.ed_api_key = QLineEdit()
        self.ed_api_key.setEchoMode(QLineEdit.Password)
        self.ed_api_key.setPlaceholderText(tr("ai_processor.placeholder_api_key"))
        self.ed_api_key.setToolTip(tooltip_tr("ai_processor.tooltip_api_key"))
        self.btn_verify = QPushButton(tr("ai_processor.btn_verify"))
        self.btn_verify.clicked.connect(self._verify_key)
        self.btn_verify.setToolTip(tooltip_tr("ai_processor.tooltip_verify"))
        grid.addWidget(self.ed_api_key, 2, 1, 1, 3)
        grid.addWidget(self.btn_verify, 2, 4)

        # Prompt
        grid.addWidget(QLabel(tr("ai_processor.lbl_prompt")), 3, 0)
        self.ed_prompt = QTextEdit()
        self.ed_prompt.setPlaceholderText(tr("ai_processor.placeholder_prompt"))
        self.ed_prompt.setToolTip(tooltip_tr("ai_processor.tooltip_prompt"))
        self.ed_prompt.setMaximumHeight(100)
        grid.addWidget(self.ed_prompt, 3, 1, 1, 4)

        controls_layout.addLayout(grid)

        # Multiple paths section (in group box with scroll area)
        paths_group = QGroupBox(tr("ai_processor.group_paths"))
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
        btn_add_path = QPushButton(tr("ai_processor.btn_add_path"))
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

        self.chk_line_by_line = QCheckBox(tr("ai_processor.chk_line_by_line"))
        self.chk_line_by_line.setToolTip(tooltip_tr("ai_processor.tooltip_line_by_line"))
        options_grid.addWidget(self.chk_line_by_line, 0, 0, 1, 2)

        lbl_max, self.spin_max_bytes = self.create_spinbox_input(
            "Max bytes:", 1000, 10000000, 1000000, 100000
        )
        self.spin_max_bytes.setToolTip(tooltip_tr("ai_processor.tooltip_max_bytes"))
        options_grid.addWidget(lbl_max, 1, 0)
        options_grid.addWidget(self.spin_max_bytes, 1, 1)

        options_grid.addWidget(QLabel(tr("ai_processor.lbl_extensions")), 1, 2)
        self.ed_extensions = QLineEdit()
        self.ed_extensions.setText(".txt,.py,.js,.ts,.jsx,.tsx")
        self.ed_extensions.setPlaceholderText(tr("ai_processor.placeholder_extensions"))
        self.ed_extensions.setToolTip(tooltip_tr("ai_processor.tooltip_extensions"))
        options_grid.addWidget(self.ed_extensions, 1, 3, 1, 2)

        controls_layout.addLayout(options_grid)

        # Scope filter section
        scope_group = QGroupBox(tr("ai_processor.group_scope"))
        scope_layout = QGridLayout()

        self.chk_scope_enable = QCheckBox(tr("ai_processor.chk_enable"))
        self.chk_scope_enable.setToolTip(tooltip_tr("ai_processor.tooltip_scope_enable"))
        scope_layout.addWidget(self.chk_scope_enable, 0, 0, 1, 2)

        scope_layout.addWidget(QLabel(tr("ai_processor.lbl_start")), 1, 0)
        self.ed_scope_start = QLineEdit()
        self.ed_scope_start.setPlaceholderText(tr("ai_processor.placeholder_start"))
        self.ed_scope_start.setToolTip(tooltip_tr("ai_processor.tooltip_scope_start"))
        scope_layout.addWidget(self.ed_scope_start, 1, 1, 1, 2)

        self.chk_start_regex = QCheckBox(tr("ai_processor.chk_regex"))
        self.chk_start_regex.setToolTip(tooltip_tr("ai_processor.tooltip_start_regex"))
        self.chk_start_case = QCheckBox(tr("ai_processor.chk_case_sensitive"))
        self.chk_start_case.setToolTip(tooltip_tr("ai_processor.tooltip_start_case"))
        scope_layout.addWidget(self.chk_start_regex, 1, 3)
        scope_layout.addWidget(self.chk_start_case, 1, 4)

        scope_layout.addWidget(QLabel(tr("ai_processor.lbl_end")), 2, 0)
        self.ed_scope_end = QLineEdit()
        self.ed_scope_end.setPlaceholderText(tr("ai_processor.placeholder_end"))
        self.ed_scope_end.setToolTip(tooltip_tr("ai_processor.tooltip_scope_end"))
        scope_layout.addWidget(self.ed_scope_end, 2, 1, 1, 2)

        self.chk_end_regex = QCheckBox(tr("ai_processor.chk_regex"))
        self.chk_end_regex.setToolTip(tooltip_tr("ai_processor.tooltip_end_regex"))
        self.chk_end_case = QCheckBox(tr("ai_processor.chk_case_sensitive"))
        self.chk_end_case.setToolTip(tooltip_tr("ai_processor.tooltip_end_case"))
        scope_layout.addWidget(self.chk_end_regex, 2, 3)
        scope_layout.addWidget(self.chk_end_case, 2, 4)

        scope_group.setLayout(scope_layout)
        controls_layout.addWidget(scope_group)

        # Advanced Conditions section (Task #51 - v2.9.26)
        adv_cond_group = QGroupBox(tr("ai_processor.group_advanced"))
        adv_cond_group.setCheckable(True)
        adv_cond_group.setChecked(False)
        adv_cond_layout = QGridLayout()

        # Logic operator
        adv_cond_layout.addWidget(QLabel(tr("ai_processor.lbl_logic")), 0, 0)
        self.combo_cond_logic = QComboBox()
        self.combo_cond_logic.addItems(["AND", "OR"])
        self.combo_cond_logic.setToolTip(tooltip_tr("ai_processor.tooltip_cond_logic"))
        adv_cond_layout.addWidget(self.combo_cond_logic, 0, 1, 1, 2)

        # Headers
        adv_cond_layout.addWidget(QLabel(tr("ai_processor.lbl_field")), 1, 0)
        adv_cond_layout.addWidget(QLabel(tr("ai_processor.lbl_operator")), 1, 1)
        adv_cond_layout.addWidget(QLabel(tr("ai_processor.lbl_value")), 1, 2)
        adv_cond_layout.addWidget(QLabel(tr("ai_processor.lbl_scope")), 1, 3)
        adv_cond_layout.addWidget(QLabel(tr("ai_processor.lbl_case")), 1, 4)
        adv_cond_layout.addWidget(QLabel(tr("ai_processor.lbl_regex")), 1, 5)

        # 3 condition rows (minimum)
        self.cond_rows = []
        for row in range(3):
            # Field combo
            combo_field = QComboBox()
            combo_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])
            # Operator combo
            combo_op = QComboBox()
            combo_op.addItems(["", "contains", "not contains", "equals", "not equals",
                              "starts with", "ends with", ">", "<", ">=", "<="])
            # Value input
            ed_value = QLineEdit()
            ed_value.setPlaceholderText(tr("ai_processor.placeholder_filter_value"))
            ed_value.setToolTip(tooltip_tr("ai_processor.tooltip_cond_value"))

            # Scope combo
            combo_scope = QComboBox()
            combo_scope.addItems(["none", "brackets", "braces", "parentheses",
                                 "custom", "tag", "specific-tag", "hierarchical"])
            combo_scope.setToolTip(tooltip_tr("ai_processor.tooltip_cond_scope"))

            # Case sensitive checkbox
            chk_case = QCheckBox()
            chk_case.setChecked(True)
            # Regex checkbox
            chk_regex = QCheckBox()
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
        btn_add_cond = QPushButton(tr("ai_processor.btn_add_condition"))
        btn_add_cond.setToolTip(tooltip_tr("ai_processor.tooltip_add_cond"))
        btn_add_cond.clicked.connect(self._add_condition_row)
        self.buttons_layout_ref.addWidget(btn_add_cond)

        btn_clear_cond = QPushButton(tr("ai_processor.btn_clear_conditions"))
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
        self.btn_process.setToolTip(tooltip_tr("ai_processor.tooltip_process"))
        self.btn_interrupt.setToolTip(tooltip_tr("ai_processor.tooltip_interrupt"))
        self.btn_save_results.setToolTip(tooltip_tr("ai_processor.tooltip_save_results"))
        self.btn_clear.setToolTip(tooltip_tr("ai_processor.tooltip_clear"))

        controls_layout.addLayout(btn_layout)

        # Statistics panel
        stats_group = QGroupBox(tr("ai_processor.group_stats"))
        stats_layout = QGridLayout()

        self.lbl_session_stats = QLabel(tr("ai_processor.lbl_session_stats"))
        self.lbl_session_stats.setToolTip(tooltip_tr("ai_processor.tooltip_session_stats"))
        self.lbl_lifetime_stats = QLabel(tr("ai_processor.lbl_lifetime_stats"))
        self.lbl_lifetime_stats.setToolTip(tooltip_tr("ai_processor.tooltip_lifetime_stats"))

        stats_layout.addWidget(QLabel("💬"), 0, 0)
        stats_layout.addWidget(self.lbl_session_stats, 0, 1)
        stats_layout.addWidget(QLabel("🌍"), 1, 0)
        stats_layout.addWidget(self.lbl_lifetime_stats, 1, 1)

        # Code fence removal option
        self.chk_remove_fences = QCheckBox(tr("ai_processor.chk_remove_fences"))
        self.chk_remove_fences.setChecked(True)
        self.chk_remove_fences.setToolTip(tooltip_tr("ai_processor.tooltip_remove_fences"))
        stats_layout.addWidget(self.chk_remove_fences, 2, 0, 1, 2)

        # Template variables option (v2.9.79 - Dynamic Templates)
        self.chk_enable_templates = QCheckBox(tr("ai_processor.chk_templates"))
        self.chk_enable_templates.setChecked(False)
        self.chk_enable_templates.setToolTip(
            "Enable dynamic variables in prompts:\n"
            "• {{count}} - File index (0-based)\n"
            "• {{count+N}} - Arithmetic (e.g., {{count+1}} for 1-based)\n"
            "• {{filename}} - Current file name\n"
            "• {{filepath}} - Full file path\n"
            "• {{total}} - Total number of files\n\n"
            "Example: 'Process chapter {{count+1}} of {{total}}: {{filename}}'\n"
            "→ 'Process chapter 1 of 10: chapter1.txt' (for first file)"
        )
        stats_layout.addWidget(self.chk_enable_templates, 3, 0, 1, 2)

        # Template preview button
        self.btn_preview_template = QPushButton(tr("ai_processor.btn_preview"))
        self.btn_preview_template.setToolTip(tooltip_tr("ai_processor.tooltip_preview_template"))
        self.btn_preview_template.clicked.connect(self._preview_template)
        self.btn_preview_template.setMaximumWidth(100)
        stats_layout.addWidget(self.btn_preview_template, 4, 0, 1, 2)

        stats_group.setLayout(stats_layout)
        controls_layout.addWidget(stats_group)

        # Search/Replace Panel (v2.9.110 - Re-enabled with emit methods)
        search_replace_group = QGroupBox(tr("ai_processor.group_search_replace"))
        search_replace_layout = QVBoxLayout()
        self.search_replace_panel = SearchReplacePanel(self, "ai_processor_search_replace")
        self.search_replace_panel.replace_requested.connect(self._handle_replace_in_results)
        search_replace_layout.addWidget(self.search_replace_panel)

        # Add button to trigger replace signal
        self.btn_replace_results = QPushButton(tr("ai_processor.btn_apply_replace"))
        self.btn_replace_results.setToolTip(tooltip_tr("ai_processor.tooltip_replace_results"))
        self.btn_replace_results.clicked.connect(self.search_replace_panel.emit_replace_request)
        search_replace_layout.addWidget(self.btn_replace_results)

        search_replace_group.setLayout(search_replace_layout)
        controls_layout.addWidget(search_replace_group)

        # Insert Panel (v2.9.110 - Re-enabled with emit methods)
        insert_group = QGroupBox(tr("ai_processor.group_insert"))
        insert_layout = QVBoxLayout()
        self.insert_panel = InsertPanel(self, "ai_processor_insert")
        self.insert_panel.insert_requested.connect(self._handle_insert_in_prompt)
        insert_layout.addWidget(self.insert_panel)

        # Add button to trigger insert signal
        self.btn_insert_prompt = QPushButton(tr("ai_processor.btn_apply_insert"))
        self.btn_insert_prompt.setToolTip(tooltip_tr("ai_processor.tooltip_insert_prompt"))
        self.btn_insert_prompt.clicked.connect(self.insert_panel.emit_insert_request)
        insert_layout.addWidget(self.btn_insert_prompt)

        insert_group.setLayout(insert_layout)
        controls_layout.addWidget(insert_group)

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

        # Apply tooltips (v2.9.71)
        self._apply_tooltips()

        # Update stats display
        self._update_stats_display()

        # Initialize provider
        self._on_provider_changed()

        # Load advanced conditions preferences (Task #51 - v2.9.26)
        self._load_advanced_conditions_preferences()

    def _apply_tooltips(self) -> None:
        """Apply internationalized tooltips (v2.9.71)."""
        # Path entries (will be applied to each PathEntry dynamically)
        for path_entry in self.path_entries:
            path_entry.ed_path.setToolTip(tooltip_tr("ai_processor.ed_path"))
            path_entry.btn_browse.setToolTip(tooltip_tr("ai_processor.btn_browse"))
            path_entry.chk_is_file.setToolTip(tooltip_tr("ai_processor.chk_is_file"))

        # AI Configuration
        self.combo_provider.setToolTip(tooltip_tr("ai_processor.combo_provider"))
        self.combo_model.setToolTip(tooltip_tr("ai_processor.combo_model"))
        self.btn_refresh_models.setToolTip(tooltip_tr("ai_processor.btn_refresh_models"))
        self.ed_api_key.setToolTip(tooltip_tr("ai_processor.ed_api_key"))
        self.btn_verify.setToolTip(tooltip_tr("ai_processor.btn_verify"))
        self.ed_prompt.setToolTip(tooltip_tr("ai_processor.ed_prompt"))

        # Processing Options
        self.chk_line_by_line.setToolTip(tooltip_tr("ai_processor.chk_line_by_line"))
        self.spin_max_bytes.setToolTip(tooltip_tr("ai_processor.spin_max_bytes"))
        self.ed_extensions.setToolTip(tooltip_tr("ai_processor.ed_extensions"))

        # Scope Extraction
        self.chk_scope_enable.setToolTip(tooltip_tr("ai_processor.chk_scope_enable"))
        self.ed_scope_start.setToolTip(tooltip_tr("ai_processor.ed_scope_start"))
        self.chk_start_regex.setToolTip(tooltip_tr("ai_processor.chk_start_regex"))
        self.chk_start_case.setToolTip(tooltip_tr("ai_processor.chk_start_case"))
        self.ed_scope_end.setToolTip(tooltip_tr("ai_processor.ed_scope_end"))
        self.chk_end_regex.setToolTip(tooltip_tr("ai_processor.chk_end_regex"))
        self.chk_end_case.setToolTip(tooltip_tr("ai_processor.chk_end_case"))

        # Advanced Conditions
        self.combo_cond_logic.setToolTip(tooltip_tr("ai_processor.combo_cond_logic"))

        # Action Buttons
        self.btn_process.setToolTip(tooltip_tr("ai_processor.btn_process"))
        self.btn_interrupt.setToolTip(tooltip_tr("ai_processor.btn_interrupt"))
        self.btn_save_results.setToolTip(tooltip_tr("ai_processor.btn_save_results"))
        self.btn_clear.setToolTip(tooltip_tr("ai_processor.btn_clear"))

        # Statistics
        self.lbl_session_stats.setToolTip(tooltip_tr("ai_processor.lbl_session_stats"))
        self.lbl_lifetime_stats.setToolTip(tooltip_tr("ai_processor.lbl_lifetime_stats"))

        # Output Options
        self.chk_remove_fences.setToolTip(tooltip_tr("ai_processor.chk_remove_fences"))

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

    def prepare_file_explorer_explanation(
        self,
        prompt: str,
        file_paths: List[str],
        max_bytes: int,
    ) -> int:
        """Prepare AI Processor to explain File Searcher results without processing."""
        needed_entries = max(1, len(file_paths))
        while len(self.path_entries) < needed_entries:
            self._add_path_entry()

        while len(self.path_entries) > needed_entries:
            entry = self.path_entries[-1]
            self.path_entries.remove(entry)
            entry.deleteLater()

        for index, entry in enumerate(self.path_entries):
            path = file_paths[index] if index < len(file_paths) else ""
            entry.ed_path.setText(path)
            entry.chk_is_file.setChecked(bool(path))
            entry.btn_remove.setEnabled(index > 0)
            entry.path_number = index + 1
            entry.lbl_path.setText(f"Path {index + 1}:")

        self.ed_prompt.setPlainText(prompt)
        self.spin_max_bytes.setValue(max_bytes)
        self.chk_line_by_line.setChecked(False)
        self.clear_results(self.text_results)
        self.append_result(
            self.text_results,
            (
                "Prepared from File Searcher. Review the prompt, provider, model, "
                "API key and max bytes before clicking Process."
            ),
        )
        return len(file_paths)

    def _connect_signals(self):
        """Connect signals."""
        self._setup_enter_key_execution(self.ed_api_key, self.ed_extensions)
        self._setup_escape_key_interrupt()
        self._setup_escape_key_interrupt()

    def _setup_escape_key_interrupt(self):
        """Setup Esc key to interrupt AI processing (v2.9.50.1)."""
        # pylint: disable=reimported,redefined-outer-name  # Lazy import for Qt components
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QShortcut, QKeySequence

        shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        shortcut.activated.connect(self._interrupt)

    def _load_models_cache(self):
        """Load models cache from file."""
        if not self.models_cache_file.exists():
            return {}

        try:
            with open(self.models_cache_file, 'r', encoding='utf-8') as f:
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
            with open(self.models_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2)
        except Exception:
            pass

    def _refresh_models(self):
        """Refresh models list from API."""
        api_key = self.ed_api_key.text().strip()
        provider = self.combo_provider.currentText()
        if "Ollama" not in provider and not api_key:
            self.show_warning("No API Key", "Please enter an API key first")
            return

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
            elif "Ollama" in provider:
                models = list_ollama_models()
                provider_key = 'ollama'
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
                self.show_warning("SDK Missing", "Gemini SDK not installed.\nRun: pip install google-genai")
        elif "Claude" in provider:
            provider_key = 'claude'
            if not is_claude_available():
                self.show_warning("SDK Missing", "Claude SDK not installed.\nRun: pip install anthropic")
        elif "Perplexity" in provider:
            provider_key = 'perplexity'
            if not is_openai_available():
                self.show_warning(
                    "SDK Missing",
                    "OpenAI SDK not installed (required for Perplexity).\nRun: pip install openai"
                )
        elif "Ollama" in provider:
            provider_key = 'ollama'
        else:
            return

        is_local = provider_key == "ollama"
        self.ed_api_key.setEnabled(not is_local)
        self.btn_verify.setText("Verify Service" if is_local else tr("ai_processor.btn_verify"))

        # Load models from cache first, fallback to static list
        models = self.models_cache.get(provider_key, AVAILABLE_MODELS.get(provider_key, []))

        for model in models:
            self.combo_model.addItem(model['label'], model['name'])

    def _verify_key(self):
        """Verify API key."""
        api_key = self.ed_api_key.text().strip()
        provider = self.combo_provider.currentText()
        if "Ollama" not in provider and not api_key:
            self.show_warning("No Key", "Please enter an API key")
            return

        if "Ollama" not in provider and not has_internet():
            self.show_warning("No Internet", "No internet connection detected")
            return

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
            elif "Ollama" in provider:
                client = OllamaClient(None, model_name)
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
        provider = self.combo_provider.currentText()
        if "Ollama" not in provider and not api_key:
            raise ValueError("No API key provided")

        model_name = self.combo_model.currentData()

        if "OpenAI" in provider:
            return OpenAIClient(api_key, model_name)
        elif "Gemini" in provider:
            return GeminiClient(api_key, model_name)
        elif "Claude" in provider:
            return ClaudeClient(api_key, model_name)
        elif "Perplexity" in provider:
            return PerplexityClient(api_key, model_name)
        elif "Ollama" in provider:
            return OllamaClient(None, model_name)
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

    def _snapshot_processing_plan(self):
        """Capture bounded discovery/filter state without performing file IO."""
        targets = tuple(
            AIPathTarget(entry.get_path(), entry.is_file())
            for entry in self.path_entries
            if entry.get_path()
        )
        ext_text = self.ed_extensions.text().strip()
        extensions = tuple(
            extension.strip()
            for extension in ext_text.split(",")
            if extension.strip()
        )
        filtering_enabled = self.adv_cond_group.isChecked()
        conditions = (
            tuple(
                AIConditionRequest.from_condition(condition)
                for condition in self._get_conditions()
            )
            if filtering_enabled
            else ()
        )
        return AIFileDiscoveryPlan(
            targets=targets,
            extensions=extensions,
            conditions=conditions,
            logic_operator=self.combo_cond_logic.currentText().upper(),
            filtering_enabled=filtering_enabled,
        )

    def _process(self):
        """Start processing."""
        if self._processing_running():
            return
        try:
            prompt = self.ed_prompt.toPlainText().strip()
            if not prompt:
                self.show_warning("No Prompt", "Please enter a prompt")
                return

            client = self._get_client()
            discovery_plan = self._snapshot_processing_plan()

            # Don't reset session stats - accumulate
            self.last_responses = []

            # Start worker with filtered files
            worker = AIProcessorWorker(
                discovery_plan,
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
                scope_end_case=self.chk_end_case.isChecked(),
                template_enabled=self.chk_enable_templates.isChecked()
            )
            self._worker_generation += 1
            generation = self._worker_generation
            self.worker = worker
            self._pending_worker_result = _UNSET
            self._pending_worker_error = None
            self._cancel_requested = False
            self._discard_worker_callbacks = False
            worker.progress.connect(
                lambda message, current=generation: self._on_worker_progress(
                    current, message
                )
            )
            worker.finished_ok.connect(
                lambda result, current=generation: self._store_worker_result(
                    current, result
                )
            )
            worker.failed.connect(
                lambda error, current=generation: self._store_worker_error(
                    current, error
                )
            )

            from src.ui import FeatureType, thread_manager

            if not thread_manager.start_thread(
                self._worker_thread_id,
                worker,
                worker,
                FeatureType.AI_FILE_PROCESSOR,
                worker.request_interrupt,
                exclusive=False,
            ):
                self.worker = None
                self.show_error("Error", "Cannot start AI processing during shutdown")
                return
            worker.finished.connect(
                lambda current=generation, finished_worker=worker: self._on_worker_finished(
                    current, finished_worker
                )
            )

            self.btn_process.setEnabled(False)
            self.btn_interrupt.setEnabled(True)
            self.btn_replace_results.setEnabled(False)
            self.btn_insert_prompt.setEnabled(False)
            self.btn_save_results.setEnabled(False)
            self.clear_results(self.text_results)
            self.append_result(self.text_results, "[Preparation] Starting file discovery...")

            # Save preferences for next session
            self._save_advanced_conditions_preferences()

            worker.start()

        except Exception as e:
            self.show_error("Error", str(e))

    def _interrupt(self):
        """Interrupt processing."""
        if self.worker and self.worker.isRunning():
            self._cancel_requested = True
            self.worker.request_interrupt()
            self.append_result(self.text_results, "\n⚠️ Interrupt requested...")
        elif self._result_replace_worker and self._result_replace_worker.isRunning():
            self._cancel_requested = True
            self._result_replace_worker.request_interrupt()
        elif self._prompt_insert_worker and self._prompt_insert_worker.isRunning():
            self._cancel_requested = True
            self._prompt_insert_worker.request_interrupt()
        elif self._result_save_worker and self._result_save_worker.isRunning():
            self._cancel_requested = True
            self._result_save_worker.request_interrupt()

    def _processing_running(self):
        return any(
            worker is not None
            for worker in (
                self.worker,
                self._result_replace_worker,
                self._prompt_insert_worker,
                self._result_save_worker,
            )
        )

    def _embedded_operation_running(self):
        return any(
            panel.has_active_operation()
            for panel in (self.search_replace_panel, self.insert_panel)
        )

    def _operation_running(self):
        return self._processing_running() or self._embedded_operation_running()

    def _on_worker_progress(self, generation, message):
        if (
            generation != self._worker_generation
            or self._discard_worker_callbacks
            or self._cancel_requested
        ):
            return
        self._on_progress(message)

    def _store_worker_result(self, generation, responses):
        if generation == self._worker_generation:
            self._pending_worker_result = responses

    def _store_worker_error(self, generation, error):
        if generation == self._worker_generation:
            self._pending_worker_error = error

    def _on_worker_finished(self, generation, worker):
        if generation != self._worker_generation or worker is not self.worker:
            worker.deleteLater()
            return

        result = self._pending_worker_result
        error = self._pending_worker_error
        cancelled = self._cancel_requested
        discard = self._discard_worker_callbacks
        self.worker = None
        self._pending_worker_result = _UNSET
        self._pending_worker_error = None
        self.btn_process.setEnabled(True)
        self.btn_interrupt.setEnabled(False)
        self.btn_replace_results.setEnabled(True)
        self.btn_insert_prompt.setEnabled(True)
        self.btn_save_results.setEnabled(True)
        worker.deleteLater()

        if not discard:
            if error is not None:
                self._on_failed(error)
            elif cancelled:
                self.append_result(self.text_results, "\n⚠️ Processing interrupted.")
            elif result is not _UNSET:
                self._on_finished(result)
            else:
                self._on_failed("AI processing ended without a result")

        self._cancel_requested = False
        if self._close_action is not None:
            self._schedule_close_retry()

    def _store_result_replace(self, generation, result):
        if generation == self._result_replace_generation:
            self._pending_result_replace = result

    def _store_result_replace_error(self, generation, error):
        if generation == self._result_replace_generation:
            self._pending_result_replace_error = error

    def _on_result_replace_finished(self, generation, worker, query):
        if (
            generation != self._result_replace_generation
            or worker is not self._result_replace_worker
        ):
            worker.deleteLater()
            return

        result = self._pending_result_replace
        error = self._pending_result_replace_error
        cancelled = self._cancel_requested
        discard = self._discard_worker_callbacks
        self._result_replace_worker = None
        self._pending_result_replace = _UNSET
        self._pending_result_replace_error = None
        self.btn_process.setEnabled(True)
        self.btn_interrupt.setEnabled(False)
        self.btn_replace_results.setEnabled(True)
        self.btn_insert_prompt.setEnabled(True)
        self.btn_save_results.setEnabled(True)
        worker.deleteLater()

        if not discard:
            if error is not None:
                self.show_error("Replace Error", f"Error during replacement:\n\n{error}")
            elif cancelled:
                self.append_result(self.text_results, "\n⚠️ Replacement cancelled.")
            elif result is _UNSET:
                self.show_error("Replace Error", "Replacement ended without a result")
            else:
                new_content, replaced = result
                self.text_results.setPlainText(new_content)
                query_preview = query if len(query) <= 80 else f"{query[:77]}..."
                self.show_info(
                    "Replace Complete",
                    f"Replaced {replaced} occurrence(s) of '{query_preview}'",
                )

        self._cancel_requested = False
        if self._close_action is not None:
            self._schedule_close_retry()

    def _store_prompt_insert(self, generation, result):
        if generation == self._prompt_insert_generation:
            self._pending_prompt_insert = result

    def _store_prompt_insert_error(self, generation, error):
        if generation == self._prompt_insert_generation:
            self._pending_prompt_insert_error = error

    def _on_prompt_insert_finished(self, generation, worker, line_no, mode):
        if (
            generation != self._prompt_insert_generation
            or worker is not self._prompt_insert_worker
        ):
            worker.deleteLater()
            return

        result = self._pending_prompt_insert
        error = self._pending_prompt_insert_error
        cancelled = self._cancel_requested
        discard = self._discard_worker_callbacks
        self._prompt_insert_worker = None
        self._pending_prompt_insert = _UNSET
        self._pending_prompt_insert_error = None
        self.btn_process.setEnabled(True)
        self.btn_interrupt.setEnabled(False)
        self.btn_replace_results.setEnabled(True)
        self.btn_insert_prompt.setEnabled(True)
        self.btn_save_results.setEnabled(True)
        worker.deleteLater()

        if not discard:
            if error is not None:
                self.show_error("Insert Error", f"Error during insertion:\n\n{error}")
            elif cancelled:
                self.show_info("Insert Cancelled", "Prompt insertion was cancelled.")
            elif result is _UNSET:
                self.show_error("Insert Error", "Insertion ended without a result")
            else:
                self.ed_prompt.setPlainText(result)
                self.show_info(
                    "Insert Complete",
                    f"Inserted text at line {line_no} using {mode} mode",
                )

        self._cancel_requested = False
        if self._close_action is not None:
            self._schedule_close_retry()

    def _store_result_save(self, generation, output_path):
        if generation == self._result_save_generation:
            self._pending_result_save = output_path

    def _store_result_save_error(self, generation, error):
        if generation == self._result_save_generation:
            self._pending_result_save_error = error

    def _on_result_save_finished(self, generation, worker):
        if (
            generation != self._result_save_generation
            or worker is not self._result_save_worker
        ):
            worker.deleteLater()
            return

        output_path = self._pending_result_save
        error = self._pending_result_save_error
        cancelled = self._cancel_requested
        discard = self._discard_worker_callbacks
        self._result_save_worker = None
        self._pending_result_save = _UNSET
        self._pending_result_save_error = None
        self.btn_process.setEnabled(True)
        self.btn_interrupt.setEnabled(False)
        self.btn_replace_results.setEnabled(True)
        self.btn_insert_prompt.setEnabled(True)
        self.btn_save_results.setEnabled(True)
        worker.deleteLater()

        if not discard:
            if error is not None:
                self.show_error("Save Error", error)
            elif output_path is not _UNSET:
                self.show_info("Saved", f"Results saved to {output_path}")
            elif cancelled:
                self.show_info("Save Cancelled", "Result saving was cancelled.")
            else:
                self.show_error("Save Error", "Result saving ended without a result")

        self._cancel_requested = False
        if self._close_action is not None:
            self._schedule_close_retry()

    def _request_operation_shutdown(self):
        if self.worker is not None:
            self._cancel_requested = True
            self.worker.request_interrupt()
        if self._result_replace_worker is not None:
            self._cancel_requested = True
            self._result_replace_worker.request_interrupt()
        if self._prompt_insert_worker is not None:
            self._cancel_requested = True
            self._prompt_insert_worker.request_interrupt()
        if self._result_save_worker is not None:
            self._cancel_requested = True
            self._result_save_worker.request_interrupt()
        self.search_replace_panel.request_parent_shutdown()
        self.insert_panel.request_parent_shutdown()

    def _schedule_close_retry(self):
        if self._close_retry_timer is not None and not self._close_retry_timer.isActive():
            self._close_retry_timer.start()

    def _retry_deferred_close(self):
        if self._operation_running():
            self._schedule_close_retry()
            return
        action = self._close_action
        self._close_action = None
        self._discard_worker_callbacks = False
        if action is None:
            return
        name, target = action
        if name == "tab":
            index = target.tabs.indexOf(self)
            if index >= 0:
                target._close_tab(index)
        else:
            target.close()

    def request_tab_close(self):
        """Defer tab removal until parent and embedded operations settle."""
        if not self._operation_running():
            QTimer.singleShot(0, self.deleteLater)
            return True
        host = self.window()
        if hasattr(host, "tabs") and hasattr(host, "_close_tab"):
            self._close_action = ("tab", host)
        else:
            self._close_action = ("close", self)
        self._discard_worker_callbacks = True
        self._request_operation_shutdown()
        self._schedule_close_retry()
        return False

    def closeEvent(self, event):
        """Wait for cooperative settlement before destroying the dock."""
        if self._operation_running():
            self._close_action = ("close", self)
            self._discard_worker_callbacks = True
            self._request_operation_shutdown()
            self._schedule_close_retry()
            event.ignore()
            return
        if self._close_retry_timer is not None:
            self._close_retry_timer.stop()
        super().closeEvent(event)

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
            if not msg.startswith('[') and not msg.startswith('✓') \
                    and not msg.startswith('Reading') and not msg.startswith('⚠'):
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
        self.notify_processing_completed()

    def _on_failed(self, error):
        """Handle failure."""
        self.append_result(self.text_results, f"\n❌ Error: {error}")
        self.btn_process.setEnabled(True)
        self.btn_interrupt.setEnabled(False)

    def _save_results(self):
        """Save results to file."""
        if self._operation_running():
            self.show_warning(
                "Operation Running",
                "Wait for the current AI Processor operation to finish or cancel it.",
            )
            return
        if not self.last_responses:
            self.show_warning("No Results", "No results to save")
            return

        # pylint: disable=reimported,redefined-outer-name  # Lazy import
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Save results", "",
            "Text files (*.txt);;All files (*)"
        )
        if path:
            try:
                plan = AIResultSavePlan(tuple(self.last_responses), path)
                worker = AIResultSaveWorker(plan)
                self._result_save_generation += 1
                generation = self._result_save_generation
                self._result_save_worker = worker
                self._pending_result_save = _UNSET
                self._pending_result_save_error = None
                self._cancel_requested = False
                self._discard_worker_callbacks = False
                worker.finished_ok.connect(
                    lambda output_path, current=generation: self._store_result_save(
                        current, output_path
                    )
                )
                worker.failed.connect(
                    lambda error, current=generation: self._store_result_save_error(
                        current, error
                    )
                )
                worker.finished.connect(
                    lambda current=generation, finished_worker=worker: (
                        self._on_result_save_finished(current, finished_worker)
                    )
                )

                from src.ui import FeatureType, thread_manager

                if not thread_manager.start_thread(
                    self._result_save_thread_id,
                    worker,
                    worker,
                    FeatureType.AI_FILE_PROCESSOR,
                    worker.request_interrupt,
                    exclusive=False,
                ):
                    self._result_save_worker = None
                    worker.deleteLater()
                    self.show_error(
                        "Save Error",
                        "Cannot save results during application shutdown",
                    )
                    return

                self.btn_process.setEnabled(False)
                self.btn_interrupt.setEnabled(True)
                self.btn_replace_results.setEnabled(False)
                self.btn_insert_prompt.setEnabled(False)
                self.btn_save_results.setEnabled(False)
                worker.start()
            except (TypeError, ValueError, UnicodeError) as exc:
                self.show_error("Save Error", str(exc))

    def _clear(self):
        """Clear results."""
        self.clear_results(self.text_results)
        self.last_responses = []
        self.session_input_tokens = 0
        self.session_output_tokens = 0
        self._update_stats_display()

    def _handle_replace_in_results(self, file_name_query, file_content_query, replacement,
                                   options, preserve_case, count):
        """
        Handle search/replace in results text (v2.9.110).

        Pattern: Command (GoF)
        Args:
            file_name_query: File name search pattern (not used in text results)
            file_content_query: File content search text
            replacement: Replacement text
            options: SearchOptions (case_sensitive, whole_word, regex)
            preserve_case: Preserve case pattern
            count: Number of replacements (0 = all)
        """
        if self._operation_running():
            self.show_warning(
                "Operation Running",
                "Wait for the current AI Processor operation to finish or cancel it.",
            )
            return

        needle = file_content_query if file_content_query else file_name_query
        document = self.text_results.document()
        if document.isEmpty():
            self.show_warning("No Results", "No results to process. Run AI processor first.")
            return
        if max(0, document.characterCount() - 1) > MAX_AI_RESULT_TEXT_CHARS:
            self.show_error(
                "Replace Error",
                "Result text exceeds the 4 MiB character safety limit",
            )
            return

        try:
            if not isinstance(options, SearchOptions):
                raise TypeError("Replacement options must be SearchOptions")
            plan = AIResultReplacePlan(
                content=self.text_results.toPlainText(),
                query=needle,
                replacement=replacement,
                case_sensitive=options.case_sensitive,
                whole_word=options.whole_word,
                use_regex=options.regex,
                preserve_case=preserve_case,
                count=count or 0,
            )
            worker = AIResultReplaceWorker(plan)
            self._result_replace_generation += 1
            generation = self._result_replace_generation
            self._result_replace_worker = worker
            self._pending_result_replace = _UNSET
            self._pending_result_replace_error = None
            self._cancel_requested = False
            self._discard_worker_callbacks = False
            worker.finished_ok.connect(
                lambda result, current=generation: self._store_result_replace(
                    current, result
                )
            )
            worker.failed.connect(
                lambda error, current=generation: self._store_result_replace_error(
                    current, error
                )
            )
            worker.finished.connect(
                lambda current=generation, finished_worker=worker, query=needle: (
                    self._on_result_replace_finished(
                        current, finished_worker, query
                    )
                )
            )

            from src.ui import FeatureType, thread_manager

            if not thread_manager.start_thread(
                self._result_replace_thread_id,
                worker,
                worker,
                FeatureType.AI_FILE_PROCESSOR,
                worker.request_interrupt,
                exclusive=False,
            ):
                self._result_replace_worker = None
                worker.deleteLater()
                self.show_error(
                    "Replace Error",
                    "Cannot start replacement during application shutdown",
                )
                return

            self.btn_process.setEnabled(False)
            self.btn_interrupt.setEnabled(True)
            self.btn_replace_results.setEnabled(False)
            self.btn_insert_prompt.setEnabled(False)
            self.btn_save_results.setEnabled(False)
            worker.start()

        except (TypeError, ValueError, UnicodeError) as exc:
            self.show_error("Replace Error", f"Error during replacement:\n\n{exc}")

    def _handle_insert_in_prompt(self, line_no, text, mode):
        """
        Handle insert in prompt text (v2.9.110).

        Pattern: Command (GoF)
        Args:
            line_no: Target line number (1-based)
            text: Text to insert
            mode: Insertion mode (LEFT, RIGHT, REPLACE, INSERT_ABOVE, INSERT_BELOW)
        """
        if self._operation_running():
            self.show_warning(
                "Operation Running",
                "Wait for the current AI Processor operation to finish or cancel it.",
            )
            return

        document = self.ed_prompt.document()
        if max(0, document.characterCount() - 1) > MAX_AI_PROMPT_BYTES:
            self.show_error(
                "Insert Error",
                "Prompt text exceeds the 4 MiB character safety limit",
            )
            return

        try:
            plan = AIPromptInsertPlan(
                content=self.ed_prompt.toPlainText(),
                line_no=line_no,
                text=text,
                mode=mode,
            )
            worker = AIPromptInsertWorker(plan)
            self._prompt_insert_generation += 1
            generation = self._prompt_insert_generation
            self._prompt_insert_worker = worker
            self._pending_prompt_insert = _UNSET
            self._pending_prompt_insert_error = None
            self._cancel_requested = False
            self._discard_worker_callbacks = False
            worker.finished_ok.connect(
                lambda result, current=generation: self._store_prompt_insert(
                    current, result
                )
            )
            worker.failed.connect(
                lambda error, current=generation: self._store_prompt_insert_error(
                    current, error
                )
            )
            worker.finished.connect(
                lambda current=generation, finished_worker=worker: (
                    self._on_prompt_insert_finished(
                        current, finished_worker, line_no, mode
                    )
                )
            )

            from src.ui import FeatureType, thread_manager

            if not thread_manager.start_thread(
                self._prompt_insert_thread_id,
                worker,
                worker,
                FeatureType.AI_FILE_PROCESSOR,
                worker.request_interrupt,
                exclusive=False,
            ):
                self._prompt_insert_worker = None
                worker.deleteLater()
                self.show_error(
                    "Insert Error",
                    "Cannot start insertion during application shutdown",
                )
                return

            self.btn_process.setEnabled(False)
            self.btn_interrupt.setEnabled(True)
            self.btn_replace_results.setEnabled(False)
            self.btn_insert_prompt.setEnabled(False)
            self.btn_save_results.setEnabled(False)
            worker.start()

        except (TypeError, ValueError, UnicodeError) as exc:
            self.show_error("Insert Error", f"Error during insertion:\n\n{exc}")

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
        combo_op = QComboBox()
        combo_op.addItems(["", "contains", "not contains", "equals", "not equals",
                          "starts with", "ends with", ">", "<", ">=", "<="])
        ed_value = QLineEdit()
        ed_value.setPlaceholderText(tr("ai_processor.placeholder_filter_value"))

        combo_scope = QComboBox()
        combo_scope.addItems(["none", "brackets", "braces", "parentheses",
                             "custom", "tag", "specific-tag", "hierarchical"])
        chk_case = QCheckBox()
        chk_case.setChecked(True)
        chk_regex = QCheckBox()
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
                with open(stats_file, 'r', encoding='utf-8') as f:
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
                with open(self.stats_file, 'r', encoding='utf-8') as f:
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
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.lifetime_stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

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

        return text

    def _preview_template(self):
        """Preview template rendering for first file (v2.9.79)."""
        prompt = self.ed_prompt.toPlainText().strip()

        if not prompt:
            self.show_warning("No Prompt", "Please enter a prompt to preview")
            return

        if not self.chk_enable_templates.isChecked():
            QMessageBox.information(
                self,
                tr("ai_processor.msg_templates_disabled_title"),
                tr("ai_processor.msg_templates_disabled")
            )
            return

        if not has_templates(prompt):
            QMessageBox.information(
                self,
                tr("ai_processor.msg_no_templates_title"),
                tr("ai_processor.msg_no_templates")
            )
            return

        # Get files to determine total count
        try:
            files = self._get_files()
            total_files = len(files)
        except Exception:
            total_files = 5  # Default for preview

        # Generate preview
        preview_text = preview_template(prompt, total_files)

        # Show in message box
        QMessageBox.information(
            self,
            tr("ai_processor.msg_template_preview_title"),
            tr("ai_processor.msg_template_preview").format(
                prompt=prompt,
                separator='='*50,
                preview=preview_text,
                total=total_files
            )
        ).strip()
