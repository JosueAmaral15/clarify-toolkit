"""
Collapsible Section Widget with Smooth Animations (v2.9.117 - B.6)

A widget that provides expandable/collapsible sections with smooth height animations.
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=invalid-name  # Qt convention (setContent, setTitle, etc)
# pylint: disable=bare-except  # Animation exception handling

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PySide6.QtCore import QPropertyAnimation, QEasingCurve


class CollapsibleSection(QWidget):
    """
    A collapsible section widget with smooth animation.

    Features:
    - Click header to expand/collapse
    - Smooth height animation
    - Customizable header with icon/text
    - Remembers state

    Usage:
        section = CollapsibleSection("Filters")
        section.setContent(filter_panel)
        section.setCollapsed(True)  # Start collapsed
    """

    def __init__(self, title: str = "", parent=None):
        """
        Initialize collapsible section.

        Args:
            title: Section title text
            parent: Parent widget
        """
        super().__init__(parent)
        self._title = title
        self._is_collapsed = False
        self._content_widget = None
        self._animation_duration = 300  # ms

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header button
        self.header_button = QPushButton(self._title)
        self.header_button.setCheckable(True)
        self.header_button.setChecked(True)  # Expanded by default
        self.header_button.clicked.connect(self._toggle_collapsed)
        self.header_button.setObjectName("collapsible_header")
        self.main_layout.addWidget(self.header_button)

        # Content frame (for animation)
        self.content_frame = QFrame()
        self.content_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.content_frame.setObjectName("collapsible_content")

        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(8, 8, 8, 8)

        self.main_layout.addWidget(self.content_frame)

        # Setup animation
        self._animation = QPropertyAnimation(self.content_frame, b"maximumHeight")
        self._animation.setDuration(self._animation_duration)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def setContent(self, widget: QWidget):
        """
        Set the content widget for this section.

        Args:
            widget: Widget to display in the section
        """
        # Remove existing content
        if self._content_widget:
            self.content_layout.removeWidget(self._content_widget)

        self._content_widget = widget
        self.content_layout.addWidget(widget)

        # Update max height based on content
        if not self._is_collapsed:
            self.content_frame.setMaximumHeight(16777215)  # No limit when expanded

    def setTitle(self, title: str):
        """Set the section title."""
        self._title = title
        self.header_button.setText(title)

    def title(self) -> str:
        """Get the section title."""
        return self._title

    def setCollapsed(self, collapsed: bool):
        """
        Set collapsed state without animation.

        Args:
            collapsed: True to collapse, False to expand
        """
        self._is_collapsed = collapsed
        self.header_button.setChecked(not collapsed)

        if collapsed:
            self.content_frame.setMaximumHeight(0)
            self.content_frame.setVisible(False)
        else:
            self.content_frame.setMaximumHeight(16777215)
            self.content_frame.setVisible(True)

    def isCollapsed(self) -> bool:
        """Return whether the section is collapsed."""
        return self._is_collapsed

    def _toggle_collapsed(self):
        """Toggle collapsed state with animation."""
        self._is_collapsed = not self._is_collapsed

        if self._is_collapsed:
            # Collapsing: animate from current height to 0
            start_height = self.content_frame.height()
            self._animation.setStartValue(start_height)
            self._animation.setEndValue(0)
            self._animation.finished.connect(lambda: self.content_frame.setVisible(False))
        else:
            # Expanding: animate from 0 to content height
            self.content_frame.setVisible(True)
            self.content_frame.setMaximumHeight(16777215)
            content_height = self.content_frame.sizeHint().height()
            self.content_frame.setMaximumHeight(0)

            self._animation.setStartValue(0)
            self._animation.setEndValue(content_height)

            def on_finished():
                self.content_frame.setMaximumHeight(16777215)

            try:
                self._animation.finished.disconnect()
            except:
                pass
            self._animation.finished.connect(on_finished)

        self._animation.start()

    def setAnimationDuration(self, duration_ms: int):
        """Set animation duration in milliseconds."""
        self._animation_duration = duration_ms
        self._animation.setDuration(duration_ms)

    def setHeaderStyle(self, collapsed_color: str = "#3498db", expanded_color: str = "#2c3e50"):
        """
        Customize header colors.

        Args:
            collapsed_color: Background color when collapsed
            expanded_color: Background color when expanded
        """
        self.header_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {collapsed_color};
                color: white;
                text-align: left;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {collapsed_color};
                opacity: 0.8;
            }}
            QPushButton:checked {{
                background-color: {expanded_color};
            }}
        """)
