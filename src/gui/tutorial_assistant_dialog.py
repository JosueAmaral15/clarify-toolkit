"""
Tutorial Assistant Dialog

Non-modal chat dialog for AI-powered tutorial assistance.
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=no-member  # SettingsManager dynamic attributes
# pylint: disable=invalid-name  # Qt method name convention

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QVBoxLayout
)

from src.i18n.translator import tr, tooltip_tr
from ..settings_manager import SettingsManager
from ..tutorial_assistant import get_assistant


class AssistantWorker(QThread):
    """Worker thread for AI assistant to avoid blocking UI."""

    response_ready = Signal(str, bool)

    def __init__(self, assistant, query: str):
        super().__init__()
        self.assistant = assistant
        self.query = query

    def run(self):
        """Execute query in background."""
        response, success = self.assistant.ask(self.query)
        self.response_ready.emit(response, success)


class TutorialAssistantDialog(QDialog):
    """
    Non-modal dialog for tutorial assistance.

    Features:
    - Chat-like interface
    - Session conversation history
    - Thumbs up/down feedback
    - Typing indicator
    - Keyboard shortcuts (Enter to send, Esc to close)
    """

    def __init__(self, parent=None, api_key: str = None):
        super().__init__(parent)
        self.assistant = get_assistant(api_key=api_key)
        self.settings = SettingsManager()
        self.worker = None

        # Feedback counters
        self.thumbs_up_count = self.settings.get_value("tutorial_assistant/thumbs_up", 0, int)
        self.thumbs_down_count = self.settings.get_value("tutorial_assistant/thumbs_down", 0, int)

        self._init_ui()
        self._check_availability()

    def _init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle(tr("tutorial_assistant.window_title"))
        self.setMinimumSize(600, 500)

        # Non-modal
        self.setModal(False)

        # Main layout
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(tr("tutorial_assistant.header"))
        header.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Segoe UI", 10))
        self.chat_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
        """
        )
        layout.addWidget(self.chat_display)

        # Status label (typing indicator)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        layout.addWidget(self.status_label)

        # Input area
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(tr("tutorial_assistant.placeholder_question"))
        self.input_field.setFont(QFont("Segoe UI", 10))
        self.input_field.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton(tr("tutorial_assistant.btn_send"))
        self.send_button.clicked.connect(self._send_message)
        self.send_button.setMinimumWidth(80)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Feedback and actions
        actions_layout = QHBoxLayout()

        self.thumbs_up_button = QPushButton("👍")
        self.thumbs_up_button.setToolTip(tooltip_tr("tutorial_assistant.tooltip_thumbs_up"))
        self.thumbs_up_button.clicked.connect(self._thumbs_up)
        self.thumbs_up_button.setMaximumWidth(50)
        actions_layout.addWidget(self.thumbs_up_button)

        self.thumbs_down_button = QPushButton("👎")
        self.thumbs_down_button.setToolTip(tooltip_tr("tutorial_assistant.tooltip_thumbs_down"))
        self.thumbs_down_button.clicked.connect(self._thumbs_down)
        self.thumbs_down_button.setMaximumWidth(50)
        actions_layout.addWidget(self.thumbs_down_button)

        actions_layout.addStretch()

        self.clear_button = QPushButton(tr("tutorial_assistant.btn_clear"))
        self.clear_button.clicked.connect(self._clear_chat)
        actions_layout.addWidget(self.clear_button)

        self.close_button = QPushButton(tr("tutorial_assistant.btn_close"))
        self.close_button.clicked.connect(self.close)
        actions_layout.addWidget(self.close_button)

        layout.addLayout(actions_layout)

        # Feedback stats label
        self.stats_label = QLabel(self._get_stats_text())
        self.stats_label.setStyleSheet("color: #999; font-size: 9pt; padding: 5px;")
        layout.addWidget(self.stats_label)

    def _check_availability(self):
        """Check if assistant is available."""
        if not self.assistant.is_available():
            self._add_system_message(
                "⚠️ Tutorial assistant is not available. "
                "Please configure a Google Gemini API key in Settings."
            )
            self.input_field.setEnabled(False)
            self.send_button.setEnabled(False)
        else:
            self._add_system_message(
                "✅ Tutorial assistant ready! Ask me about JSON translation, "
                "search & replace, JSON rewriting, or any other Clarify feature."
            )

    def _add_system_message(self, message: str):
        """Add system message to chat."""
        self.chat_display.append(f"<div style='color: #666; font-style: italic;'>{message}</div><br>")
        self._scroll_to_bottom()

    def _add_user_message(self, message: str):
        """Add user message to chat."""
        escaped = message.replace("<", "&lt;").replace(">", "&gt;")
        self.chat_display.append(
            f"<div style='background-color: #e3f2fd; padding: 8px; border-radius: 5px; margin: 5px 0;'>"
            f"<strong>You:</strong> {escaped}</div>"
        )
        self._scroll_to_bottom()

    def _add_assistant_message(self, message: str, success: bool = True):
        """Add assistant message to chat."""
        color = "#c8e6c9" if success else "#ffcdd2"
        escaped = message.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        self.chat_display.append(
            f"<div style='background-color: {color}; padding: 8px; border-radius: 5px; margin: 5px 0;'>"
            f"<strong>Assistant:</strong><br>{escaped}</div><br>"
        )
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """Scroll chat to bottom."""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)

    def _send_message(self):
        """Send user message to assistant."""
        query = self.input_field.text().strip()
        if not query:
            return

        # Add user message
        self._add_user_message(query)
        self.input_field.clear()

        # Show typing indicator
        self.status_label.setText("💭 AI is thinking...")
        self.send_button.setEnabled(False)
        self.input_field.setEnabled(False)

        # Start worker thread
        self.worker = AssistantWorker(self.assistant, query)
        self.worker.response_ready.connect(self._handle_response)
        self.worker.start()

    def _handle_response(self, response: str, success: bool):
        """Handle assistant response."""
        # Clear typing indicator
        self.status_label.setText("")
        self.send_button.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

        # Add assistant message
        self._add_assistant_message(response, success)

    def _thumbs_up(self):
        """Record positive feedback."""
        self.thumbs_up_count += 1
        self.settings.set_value("tutorial_assistant/thumbs_up", self.thumbs_up_count)
        self.stats_label.setText(self._get_stats_text())
        self._add_system_message("Thank you for the feedback! 👍")

    def _thumbs_down(self):
        """Record negative feedback."""
        self.thumbs_down_count += 1
        self.settings.set_value("tutorial_assistant/thumbs_down", self.thumbs_down_count)
        self.stats_label.setText(self._get_stats_text())
        self._add_system_message("Thank you for the feedback. We'll work to improve! 👎")

    def _clear_chat(self):
        """Clear chat history."""
        self.chat_display.clear()
        self.assistant.reset_conversation()
        self._add_system_message("Chat cleared. Feel free to ask a new question!")

    def _get_stats_text(self) -> str:
        """Get feedback stats text."""
        return f"Feedback: 👍 {self.thumbs_up_count} | 👎 {self.thumbs_down_count}"

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
