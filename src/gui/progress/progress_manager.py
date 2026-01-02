"""
Progress manager widget for displaying multiple progress bars.
Extracted from app.py (v2.9.114).
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea
from PySide6.QtCore import Qt

from .progress_bar_widget import ProgressBarWidget


class ProgressManager(QWidget):
    """
    Manager widget that displays multiple progress bars at the bottom of the window.
    Features:
    - Scrollable area for multiple progress bars
    - Auto-hide when no active tasks
    - Can be expanded/collapsed
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_tasks = {}  # task_id -> ProgressBarWidget

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header (collapsible)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 2, 5, 2)

        self.header_label = QLabel("<b>Active Tasks (0)</b>")
        header_layout.addWidget(self.header_label)

        header_layout.addStretch()

        self.btn_toggle = QPushButton("▼")
        self.btn_toggle.setFixedSize(20, 20)
        self.btn_toggle.setToolTip(tooltip_tr("progress_manager.tooltip_toggle"))
        self.btn_toggle.clicked.connect(self._toggle_visibility)
        header_layout.addWidget(self.btn_toggle)

        layout.addLayout(header_layout)

        # Scroll area for progress bars
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(250)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Container for progress bars
        self.bars_container = QWidget()
        self.bars_layout = QVBoxLayout(self.bars_container)
        self.bars_layout.setSpacing(5)
        self.bars_layout.setContentsMargins(5, 5, 5, 5)
        self.bars_layout.addStretch()

        self.scroll_area.setWidget(self.bars_container)
        layout.addWidget(self.scroll_area)

        # Initially hidden
        self.hide()

    def add_task(self, task_id: str, task_name: str) -> ProgressBarWidget:
        """Add a new task and return its progress bar widget."""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]

        progress_widget = ProgressBarWidget(task_id, task_name, self)
        progress_widget.close_requested.connect(self._on_task_close_requested)
        progress_widget.cancel_requested.connect(self._on_task_cancel_requested)

        # Insert before stretch
        self.bars_layout.insertWidget(self.bars_layout.count() - 1, progress_widget)

        self.active_tasks[task_id] = progress_widget
        self._update_header()
        self.show()

        return progress_widget

    def remove_task(self, task_id: str):
        """Remove a completed or cancelled task."""
        if task_id not in self.active_tasks:
            return

        widget = self.active_tasks.pop(task_id)
        self.bars_layout.removeWidget(widget)
        widget.deleteLater()

        self._update_header()

        # Hide if no more tasks
        if not self.active_tasks:
            self.hide()

    def get_task_widget(self, task_id: str) -> ProgressBarWidget:
        """Get progress widget for a specific task."""
        return self.active_tasks.get(task_id)

    def _update_header(self):
        """Update header label with task count."""
        count = len(self.active_tasks)
        self.header_label.setText(f"<b>Active Tasks ({count})</b>")

    def _toggle_visibility(self):
        """Toggle scroll area visibility."""
        visible = self.scroll_area.isVisible()
        self.scroll_area.setVisible(not visible)
        self.btn_toggle.setText("▲" if not visible else "▼")

    def _on_task_close_requested(self, task_id: str):
        """Handle close button clicked on a progress bar."""
        self.remove_task(task_id)

    def _on_task_cancel_requested(self, task_id: str):
        """Handle cancel request from details dialog."""
        # Emit signal to cancel the actual task
        # This will be connected to worker.cancel() by the panel
        widget = self.get_task_widget(task_id)
        if widget:
            widget.set_complete(success=False)
            # Actual cancellation is handled by the panel that created the task
