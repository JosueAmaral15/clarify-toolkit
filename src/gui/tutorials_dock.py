"""
Tutorials Dock Widget

Provides UI for browsing and viewing Clarify tutorials with markdown rendering.

Author: Josué Amaral
Date: November 30, 2025
Version: v2.9.15
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
    QTreeWidgetItem, QTextBrowser, QSplitter, QLineEdit, QPushButton,
    QLabel, QMessageBox
)
from PySide6.QtGui import QFont, QIcon

from src.i18n.translator import tooltip_tr


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
        
        # UI
        self._setup_ui()
        self._load_index()
        self._populate_tree()
        
        # Signals
        self._connect_signals()
        
        # Apply tooltips
        self._apply_tooltips()
    
    def _setup_ui(self):
        """Setup UI components."""
        main_widget = QWidget()
        self.setWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # === Search Bar ===
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search tutorials...")
        self.btn_search = QPushButton("Search")
        self.btn_quick_start = QPushButton("⚡ Quick Start")
        self.btn_ai_assistant = QPushButton("💬 Ask AI")
        
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_quick_start)
        search_layout.addWidget(self.btn_ai_assistant)
        layout.addLayout(search_layout)
        
        # === Splitter: Tree + Browser ===
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Tree Navigation
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("📂 Browse Tutorials")
        self.tree.setMaximumWidth(300)
        splitter.addWidget(self.tree)
        
        # Right: Markdown Browser
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tutorial title label
        self.title_label = QLabel("<h3>Welcome to Clarify Tutorials</h3>")
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
        self.status_label = QLabel("Ready")
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
            self.status_label.setText("⚠️ index.json not found")
            return
        
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                self.tutorials_index = json.load(f)
            self.status_label.setText(f"✓ Loaded {len(self.tutorials_index.get('tutorials', []))} tutorials")
        except Exception as e:
            self.status_label.setText(f"✗ Error loading index: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load tutorials index:\n{str(e)}")
    
    def _populate_tree(self):
        """Populate tree widget with tutorial structure."""
        self.tree.clear()
        
        # Root items
        beginner_root = QTreeWidgetItem(self.tree, ["👶 Beginner"])
        developers_root = QTreeWidgetItem(self.tree, ["💻 Developers"])
        
        # Beginner → Basic/Advanced
        beginner_basic = QTreeWidgetItem(beginner_root, ["📖 Basic"])
        beginner_advanced = QTreeWidgetItem(beginner_root, ["🔥 Advanced"])
        
        # Developers → Basic/Advanced
        dev_basic = QTreeWidgetItem(developers_root, ["📖 Basic"])
        dev_advanced = QTreeWidgetItem(developers_root, ["🔥 Advanced"])
        
        # Add tutorials from index
        tutorials = self.tutorials_index.get("tutorials", [])
        
        for tutorial in tutorials:
            category = tutorial.get("category", "")
            title = tutorial.get("title", "Untitled")
            file_path = tutorial.get("file", "")
            difficulty = tutorial.get("difficulty", "easy")
            time = tutorial.get("estimated_time", "")
            
            # Create item with metadata
            item = QTreeWidgetItem([f"📄 {title}"])
            item.setData(0, Qt.UserRole, file_path)  # Store file path
            item.setToolTip(0, f"{tutorial.get('description', '')}\n\n⏱️ {time}\n🎯 {difficulty}")
            
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
    
    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
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
            self.status_label.setText(f"✗ File not found: {relative_path}")
            QMessageBox.warning(self, "File Not Found", f"Tutorial file not found:\n{full_path}")
            return
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Convert markdown to HTML (simple approach)
            html_content = self._markdown_to_html(markdown_content)
            
            # Display in browser
            self.browser.setHtml(html_content)
            
            # Update title
            tutorial_name = full_path.stem.replace('-', ' ').title()
            self.title_label.setText(f"<h3>📖 {tutorial_name}</h3>")
            
            # Update status
            self.current_tutorial = str(full_path)
            self.status_label.setText(f"📄 {full_path.name}")
            
            # Emit signal
            self.tutorial_opened.emit(str(full_path))
            
        except Exception as e:
            self.status_label.setText(f"✗ Error opening tutorial")
            QMessageBox.critical(self, "Error", f"Failed to open tutorial:\n{str(e)}")
    
    def _markdown_to_html(self, markdown: str) -> str:
        """
        Convert markdown to HTML (basic implementation).
        
        For production, consider using a library like `markdown` or `mistune`.
        This is a minimal implementation for MVP.
        """
        import re
        
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
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; line-height: 1.6; padding: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                h3 {{ color: #7f8c8d; }}
                code {{ background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
                pre {{ background-color: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }}
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
        welcome_html = """
        <html>
        <head>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; padding: 30px; }
                h1 { color: #3498db; }
                .card { background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0; }
                .emoji { font-size: 24px; }
            </style>
        </head>
        <body>
            <h1>📚 Welcome to Clarify Tutorials</h1>
            <p>Learn how to use Clarify's powerful features with step-by-step guides.</p>
            
            <div class="card">
                <h3 class="emoji">🚀 Quick Start</h3>
                <p>New to Clarify? Click <strong>"⚡ Quick Start"</strong> button above for a 5-minute introduction.</p>
            </div>
            
            <div class="card">
                <h3 class="emoji">👶 Beginner Tutorials</h3>
                <p>Step-by-step guides with visual instructions:</p>
                <ul>
                    <li>JSON Translate - Extract text from code</li>
                    <li>Search & Replace - Find and replace across files</li>
                    <li>JSON Rewriter - Transform JSON structures</li>
                </ul>
            </div>
            
            <div class="card">
                <h3 class="emoji">💻 Developer Tutorials</h3>
                <p>Technical documentation with algorithms and APIs (Coming Soon)</p>
            </div>
            
            <hr style="margin: 30px 0;">
            
            <p><strong>Need Help?</strong> Use the integrated <strong>AI Assistant</strong> (Help → AI Assistant) for real-time answers.</p>
        </body>
        </html>
        """
        self.browser.setHtml(welcome_html)
    
    def _open_quick_start(self):
        """Open Quick Start guide."""
        quickstart_path = "quickstart.md"
        self._open_tutorial(quickstart_path)
    
    def _open_ai_assistant(self):
        """Open AI Tutorial Assistant dialog (v2.9.92)."""
        from .tutorial_assistant_dialog import TutorialAssistantDialog
        from ..settings_manager import SettingsManager
        
        # Get Gemini API key from settings
        settings = SettingsManager()
        api_key = settings.get_value('ai_processor/gemini_api_key', '')
        
        dialog = TutorialAssistantDialog(self, api_key=api_key)
        dialog.show()
    
    def _perform_search(self):
        """Search tutorials by keywords."""
        query = self.search_input.text().strip().lower()
        
        if not query:
            self.status_label.setText("⚠️ Enter search keywords")
            return
        
        # Search in tutorials index
        tutorials = self.tutorials_index.get("tutorials", [])
        matches = []
        
        for tutorial in tutorials:
            title = tutorial.get("title", "").lower()
            description = tutorial.get("description", "").lower()
            keywords = [kw.lower() for kw in tutorial.get("keywords", [])]
            
            if query in title or query in description or any(query in kw for kw in keywords):
                matches.append(tutorial)
        
        if matches:
            # Show results
            results_html = self._generate_search_results_html(query, matches)
            self.browser.setHtml(results_html)
            self.title_label.setText(f"<h3>🔍 Search Results: {len(matches)} found</h3>")
            self.status_label.setText(f"✓ Found {len(matches)} results for '{query}'")
        else:
            self.status_label.setText(f"✗ No results for '{query}'")
            self.browser.setHtml(f"<html><body><h2>No results found for '{query}'</h2><p>Try different keywords.</p></body></html>")
    
    def _generate_search_results_html(self, query: str, matches: List[Dict]) -> str:
        """Generate HTML for search results."""
        results_items = ""
        for tutorial in matches:
            title = tutorial.get("title", "Untitled")
            description = tutorial.get("description", "")
            file_path = tutorial.get("file", "")
            difficulty = tutorial.get("difficulty", "easy")
            time = tutorial.get("estimated_time", "")
            
            results_items += f"""
            <div class="result-card">
                <h3><a href="{file_path}">{title}</a></h3>
                <p>{description}</p>
                <p><small>⏱️ {time} | 🎯 {difficulty}</small></p>
            </div>
            """
        
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; padding: 20px; }}
                h2 {{ color: #2c3e50; }}
                .result-card {{ background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 15px 0; }}
                .result-card a {{ color: #3498db; text-decoration: none; font-weight: bold; }}
                .result-card a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h2>🔍 Search Results for "{query}"</h2>
            <p>Found {len(matches)} tutorial(s):</p>
            {results_items}
        </body>
        </html>
        """
    
    def _on_link_clicked(self, url: QUrl):
        """Handle internal link clicks."""
        link = url.toString()
        
        # If it's a relative tutorial link, open it
        if link.endswith('.md'):
            self._open_tutorial(link)
        else:
            # External link - already handled by setOpenExternalLinks
            pass
