"""
Tutorials Dock Widget

Provides UI for browsing and viewing Clarify tutorials with markdown rendering.

Author: Josué Amaral
Date: November 30, 2025
Version: v2.9.15
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules


import json
import html
import re
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, Signal, Slot, QUrl
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
    QTreeWidgetItem, QTextBrowser, QSplitter, QLineEdit, QPushButton,
    QLabel, QMessageBox
)

from src.i18n.translator import get_translator, tooltip_tr, tr


class TutorialsDock(QDockWidget):
    """
    Dock widget for browsing and viewing Clarify tutorials.

    Features:
    - Tree navigation (Beginner/Developers → Basic/Advanced)
    - Markdown rendering with QTextBrowser
    - Search functionality
    - Quick Start guide access
    - Integration ready for AI Chatbot
    """

    tutorial_opened = Signal(str)  # Emits tutorial file path

    def __init__(self, parent=None):
        super().__init__("📚 Tutorials", parent)

        # Paths
        self.docs_path = Path(__file__).parent.parent.parent / "docs"
        self.tutorials_path = self.docs_path / "tutorials"
        self.index_path = self.tutorials_path / "index.json"

        # Data
        self.tutorials_index: Dict = {}
        self.current_tutorial: Optional[str] = None
        self._view_state = "welcome"
        self._status_state = "ready"
        self._search_query = ""
        self._search_matches: List[Dict] = []

        # UI
        self._setup_ui()
        self._load_index()
        self._populate_tree()

        # Signals
        self._connect_signals()

        # Apply tooltips
        self._apply_tooltips()
        get_translator().languageChanged.connect(self.retranslateUi)
        self.retranslateUi()

    @Slot()
    def retranslateUi(self):  # pylint: disable=invalid-name
        """Refresh chrome and current results without replacing the selected item."""
        self.setWindowTitle(tr("menu.help.tutorials"))
        self.search_input.setPlaceholderText(tr("tutorials.placeholder_search"))
        self.btn_search.setText(tr("tutorials.btn_search"))
        self.btn_quick_start.setText(tr("tutorials.btn_quick_start"))
        self.btn_ai_assistant.setText(tr("tutorials.btn_ai_assistant"))
        self.tree.setHeaderLabel(tr("tutorials.browse"))
        for key, item in self._category_items:
            item.setText(0, tr(f"tutorials.category_{key}"))
        for item, tutorial in self._tutorial_items:
            item.setText(0, f"📄 {self._entry_text(tutorial, 'title')}")
            item.setToolTip(0, self._entry_tooltip(tutorial))
        self._apply_tooltips()
        if self._view_state == "welcome":
            self._show_welcome()
        elif self._view_state == "search":
            self._render_search_results()
        elif self._view_state == "tutorial":
            self._update_tutorial_title()
        if self._status_state == "loaded":
            self.status_label.setText(tr("tutorials.status_loaded").format(count=len(self.tutorials_index.get("tutorials", []))))
        elif self._status_state == "index_missing":
            self.status_label.setText(tr("tutorials.status_index_not_found"))
        elif self._status_state == "enter_keywords":
            self.status_label.setText(tr("tutorials.status_enter_keywords"))
        elif self._status_state == "file_error":
            self.status_label.setText(tr("tutorials.file_not_found").format(file=self._error_path))
        elif self._status_state == "load_error":
            self.status_label.setText(tr("tutorials.load_error_title"))
        elif self._status_state == "open_error":
            self.status_label.setText(tr("tutorials.open_error_title"))
        elif self._status_state == "search":
            self._update_search_status()
        elif self._status_state == "ready":
            self.status_label.setText(tr("tutorials.status_ready"))

    @staticmethod
    def _entry_text(tutorial: Dict, field: str) -> str:
        fallback = tutorial.get(field, "")
        return tr(f"tutorials.entry.{tutorial.get('id', '')}.{field}", fallback)

    def _entry_tooltip(self, tutorial: Dict) -> str:
        duration = tutorial.get("estimated_time", "")
        match = re.fullmatch(r"(\d+) minutes?", duration)
        if match:
            duration = tr("tutorials.duration_minutes").format(count=match.group(1))
        difficulty = tutorial.get("difficulty", "easy")
        difficulty = tr(f"tutorials.difficulty_{difficulty}", difficulty)
        return f"{self._entry_text(tutorial, 'description')}\n\n⏱️ {duration}\n🎯 {difficulty}"

    def _setup_ui(self):
        """Setup UI components."""
        main_widget = QWidget()
        self.setWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # === Search Bar ===
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("tutorials.placeholder_search"))
        self.btn_search = QPushButton(tr("tutorials.btn_search"))
        self.btn_quick_start = QPushButton(tr("tutorials.btn_quick_start"))
        self.btn_ai_assistant = QPushButton(tr("tutorials.btn_ai_assistant"))

        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_quick_start)
        search_layout.addWidget(self.btn_ai_assistant)
        layout.addLayout(search_layout)

        # === Splitter: Tree + Browser ===
        splitter = QSplitter(Qt.Horizontal)

        # Left: Tree Navigation
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(tr("tutorials.browse"))
        self.tree.setMaximumWidth(300)
        splitter.addWidget(self.tree)

        # Right: Markdown Browser
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        browser_layout.setContentsMargins(0, 0, 0, 0)

        # Tutorial title label
        self.title_label = QLabel(tr("tutorials.title_welcome"))
        self.title_label.setWordWrap(True)
        browser_layout.addWidget(self.title_label)

        # Text browser for markdown
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)  # Open external links in system browser
        self.browser.setOpenLinks(False)  # Handle internal links ourselves
        browser_layout.addWidget(self.browser)

        splitter.addWidget(browser_widget)
        splitter.setStretchFactor(1, 1)  # Browser takes more space

        layout.addWidget(splitter)

        # === Status Bar ===
        status_layout = QHBoxLayout()
        self.status_label = QLabel(tr("tutorials.status_ready"))
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)

        # Load welcome message
        self._show_welcome()

    def _apply_tooltips(self):
        """Apply internationalized tooltips to all widgets."""
        # Search Bar
        self.search_input.setToolTip(tooltip_tr("tutorials.search_input"))
        self.btn_search.setToolTip(tooltip_tr("tutorials.btn_search"))
        self.btn_quick_start.setToolTip(tooltip_tr("tutorials.btn_quick_start"))
        self.btn_ai_assistant.setToolTip(tr("menu.tooltip_ai_assistant"))

        # Tree Navigation
        self.tree.setToolTip(tooltip_tr("tutorials.tree"))

        # Browser Section
        self.title_label.setToolTip(tooltip_tr("tutorials.title_label"))
        self.browser.setToolTip(tooltip_tr("tutorials.browser"))

        # Status Bar
        self.status_label.setToolTip(tooltip_tr("tutorials.status_label"))

    def _connect_signals(self):
        """Connect signals to slots."""
        self.tree.itemClicked.connect(self._on_tree_item_clicked)
        self.btn_search.clicked.connect(self._perform_search)
        self.btn_quick_start.clicked.connect(self._open_quick_start)
        self.btn_ai_assistant.clicked.connect(self._open_ai_assistant)
        self.browser.anchorClicked.connect(self._on_link_clicked)
        self._setup_enter_key()

    def _setup_enter_key(self):
        """Setup Enter key to execute search (v2.9.52)."""
        self.search_input.returnPressed.connect(self._perform_search)

    def _load_index(self):
        """Load tutorials index from index.json."""
        if not self.index_path.exists():
            self._status_state = "index_missing"
            self.status_label.setText(tr("tutorials.status_index_not_found"))
            return

        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                self.tutorials_index = json.load(f)
            self._status_state = "loaded"
            self.status_label.setText(tr("tutorials.status_loaded").format(count=len(self.tutorials_index.get('tutorials', []))))
        except Exception as e:  # pylint: disable=broad-exception-caught  # UI robustness
            self._status_state = "load_error"
            self.status_label.setText(tr("tutorials.load_error_title"))
            QMessageBox.warning(
                self, tr("tutorials.load_error_title"),
                tr("tutorials.load_error").format(error=str(e))
            )

    def _populate_tree(self):
        """Populate tree widget with tutorial structure."""
        self.tree.clear()
        self._tutorial_items = []

        # Root items
        beginner_root = QTreeWidgetItem(self.tree, [tr("tutorials.category_beginner")])
        developers_root = QTreeWidgetItem(self.tree, [tr("tutorials.category_developers")])

        # Beginner → Basic/Advanced
        beginner_basic = QTreeWidgetItem(beginner_root, [tr("tutorials.category_basic")])
        beginner_advanced = QTreeWidgetItem(beginner_root, [tr("tutorials.category_advanced")])

        # Developers → Basic/Advanced
        dev_basic = QTreeWidgetItem(developers_root, [tr("tutorials.category_basic")])
        dev_advanced = QTreeWidgetItem(developers_root, [tr("tutorials.category_advanced")])
        self._category_items = [("beginner", beginner_root), ("developers", developers_root),
                                ("basic", beginner_basic), ("advanced", beginner_advanced),
                                ("basic", dev_basic), ("advanced", dev_advanced)]

        # Add tutorials from index
        tutorials = self.tutorials_index.get("tutorials", [])

        for tutorial in tutorials:
            category = tutorial.get("category", "")
            file_path = tutorial.get("file", "")

            # Create item with metadata
            item = QTreeWidgetItem([f"📄 {self._entry_text(tutorial, 'title')}"])
            item.setData(0, Qt.UserRole, file_path)  # Store file path
            item.setToolTip(0, self._entry_tooltip(tutorial))
            self._tutorial_items.append((item, tutorial))

            # Add to appropriate parent
            if "beginner/basic" in category:
                beginner_basic.addChild(item)
            elif "beginner/advanced" in category:
                beginner_advanced.addChild(item)
            elif "developers/basic" in category:
                dev_basic.addChild(item)
            elif "developers/advanced" in category:
                dev_advanced.addChild(item)

        # Expand all by default
        self.tree.expandAll()

    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):  # pylint: disable=unused-argument  # Qt signal
        """Handle tree item click."""
        file_path = item.data(0, Qt.UserRole)

        if file_path:
            # It's a tutorial file
            self._open_tutorial(file_path)
        else:
            # It's a category folder - just expand/collapse
            item.setExpanded(not item.isExpanded())

    def _open_tutorial(self, relative_path: str):
        """Open and display a tutorial markdown file."""
        full_path = self.tutorials_path / relative_path

        if not full_path.exists():
            self._status_state = "file_error"
            self._error_path = relative_path
            self.status_label.setText(tr("tutorials.file_not_found").format(file=relative_path))
            QMessageBox.warning(
                self, tr("tutorials.file_not_found_title"),
                tr("tutorials.file_not_found").format(file=full_path)
            )
            return

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Convert markdown to HTML (simple approach)
            html_content = self._markdown_to_html(markdown_content)

            # Display in browser
            self.browser.setHtml(html_content)

            # Update title
            # Update status
            self.current_tutorial = str(full_path)
            self._view_state = "tutorial"
            self._status_state = "tutorial"
            self._update_tutorial_title()
            self.status_label.setText(f"📄 {full_path.name}")

            # Emit signal
            self.tutorial_opened.emit(str(full_path))

        except Exception as e:  # pylint: disable=broad-exception-caught  # UI robustness
            self._status_state = "open_error"
            self.status_label.setText(tr("tutorials.open_error_title"))
            QMessageBox.critical(
                self, tr("tutorials.open_error_title"),
                tr("tutorials.open_error").format(error=str(e))
            )

    def _update_tutorial_title(self):
        if self.current_tutorial is None:
            return
        name = Path(self.current_tutorial).name
        tutorial = next((item for item in self.tutorials_index.get("tutorials", [])
                         if Path(item.get("file", "")).name == name), None)
        title = (self._entry_text(tutorial, "title") if tutorial is not None
                 else Path(name).stem.replace('-', ' ').title())
        self.title_label.setText(f"<h3>📖 {html.escape(title)}</h3>")

    def _markdown_to_html(self, markdown: str) -> str:
        """
        Convert markdown to HTML (basic implementation).

        For production, consider using a library like `markdown` or `mistune`.
        This is a minimal implementation for MVP.
        """
        html = markdown

        # Strip YAML frontmatter
        html = re.sub(r'^---\n.*?\n---\n', '', html, flags=re.DOTALL)

        # Headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)

        # Bold/Italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Code blocks
        html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

        # Lists
        html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)

        # Paragraphs (basic)
        lines = html.split('\n')
        processed_lines = []
        in_pre = False
        for line in lines:
            if '<pre>' in line:
                in_pre = True
            elif '</pre>' in line:
                in_pre = False
            elif line.strip() and not in_pre and not any(tag in line for tag in ['<h', '<ul', '<li', '<code']):
                processed_lines.append(f'<p>{line}</p>')
            else:
                processed_lines.append(line)
        html = '\n'.join(processed_lines)

        # Wrap in HTML document with styling
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                        Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                h3 {{ color: #7f8c8d; }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }}
                pre {{
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                pre code {{ background-color: transparent; color: #ecf0f1; }}
                a {{ color: #3498db; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                ul {{ margin-left: 20px; }}
                li {{ margin: 5px 0; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #3498db; color: white; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """

        return styled_html

    def _show_welcome(self):
        """Show welcome message."""
        self.browser.setHtml(f"""
            <h1>{tr('tutorials.welcome_heading')}</h1>
            <p>{tr('tutorials.welcome_intro')}</p>
            <h2>{tr('tutorials.welcome_quick_title')}</h2>
            <p>{tr('tutorials.welcome_quick_body')}</p>
            <h2>{tr('tutorials.welcome_beginner_title')}</h2>
            <p>{tr('tutorials.welcome_beginner_body')}</p>
            <ul>
                <li>{tr('tutorials.welcome_feature_translate')}</li>
                <li>{tr('tutorials.welcome_feature_search')}</li>
                <li>{tr('tutorials.welcome_feature_rewriter')}</li>
            </ul>
            <h2>{tr('tutorials.welcome_developer_title')}</h2>
            <p>{tr('tutorials.welcome_developer_body')}</p>
            <p>{tr('tutorials.welcome_help_body')}</p>
        """)

    def _open_quick_start(self):
        """Open Quick Start guide."""
        quickstart_path = "quickstart.md"
        self._open_tutorial(quickstart_path)

    def _open_ai_assistant(self):
        """Open AI Tutorial Assistant dialog (v2.9.92)."""
        # pylint: disable=import-outside-toplevel  # Lazy imports
        from .tutorial_assistant_dialog import TutorialAssistantDialog
        from ..settings_manager import get_settings
        from shiboken6 import isValid

        # Get Gemini API key from settings
        settings = get_settings()
        api_key = settings.get('ai_processor/gemini_api_key', '')

        dialog = getattr(self, '_tutorial_assistant_dialog', None)
        if dialog is None or not isValid(dialog):
            dialog = TutorialAssistantDialog(self, api_key=api_key)
            self._tutorial_assistant_dialog = dialog
        dialog.show()

    def _perform_search(self):
        """Search tutorials by keywords."""
        query = self.search_input.text().strip()

        if not query:
            self._status_state = "enter_keywords"
            self.status_label.setText(tr("tutorials.status_enter_keywords"))
            return

        # Search in tutorials index
        tutorials = self.tutorials_index.get("tutorials", [])
        matches = []

        needle = query.casefold()
        for tutorial in tutorials:
            title = f"{tutorial.get('title', '')} {self._entry_text(tutorial, 'title')}".casefold()
            description = f"{tutorial.get('description', '')} {self._entry_text(tutorial, 'description')}".casefold()
            keywords = [kw.casefold() for kw in tutorial.get("keywords", [])]

            if needle in title or needle in description or any(needle in kw for kw in keywords):
                matches.append(tutorial)

        self._search_query = query
        self._search_matches = matches
        self._view_state = "search"
        self._status_state = "search"
        self._render_search_results()

    def _update_search_status(self):
        if self._search_matches:
            self.status_label.setText(tr("tutorials.search_status").format(
                count=len(self._search_matches), query=self._search_query))
        else:
            self.status_label.setText(tr("tutorials.no_results_status").format(query=self._search_query))

    def _render_search_results(self):
        self._update_search_status()
        count = len(self._search_matches)
        self.title_label.setText(tr("tutorials.search_title").format(count=count))
        if count:
            self.browser.setHtml(self._generate_search_results_html(self._search_query, self._search_matches))
        else:
            self.browser.setHtml(
                f"<h2>{tr('tutorials.no_results_title').format(query=html.escape(self._search_query))}</h2>"
                f"<p>{tr('tutorials.no_results_hint')}</p>")

    def _generate_search_results_html(self, query: str, matches: List[Dict]) -> str:
        """Generate HTML for search results."""
        results_items = ""
        for tutorial in matches:
            title = html.escape(self._entry_text(tutorial, "title"))
            description = html.escape(self._entry_text(tutorial, "description"))
            file_path = tutorial.get("file", "")
            difficulty = tutorial.get("difficulty", "easy")
            time = tutorial.get("estimated_time", "")
            difficulty = tr(f"tutorials.difficulty_{difficulty}", difficulty)
            duration = re.fullmatch(r"(\d+) minutes?", time)
            if duration:
                time = tr("tutorials.duration_minutes").format(count=duration.group(1))

            results_items += f"""
            <div class="result-card">
                <h3><a href="{html.escape(file_path, quote=True)}">{title}</a></h3>
                <p>{description}</p>
                <p><small>⏱️ {html.escape(time)} | 🎯 {html.escape(difficulty)}</small></p>
            </div>
            """

        summary_key = "tutorials.search_summary_one" if len(matches) == 1 else "tutorials.search_summary_many"
        return (f"<h2>{tr('tutorials.search_heading').format(query=html.escape(query))}</h2>"
                f"<p>{tr(summary_key).format(count=len(matches))}</p>{results_items}")

    def _on_link_clicked(self, url: QUrl):
        """Handle internal link clicks."""
        link = url.toString()

        # If it's a relative tutorial link, open it
        if link.endswith('.md'):
            self._open_tutorial(link)
        else:
            # External link - already handled by setOpenExternalLinks
            pass
