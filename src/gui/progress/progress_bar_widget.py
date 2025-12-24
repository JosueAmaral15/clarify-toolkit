"""
Individual progress bar widget with controls.
Extracted from app.py (v2.9.114).
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton
)
from PySide6.QtCore import Signal

from .progress_details_dialog import ProgressDetailsDialog


class ProgressBarWidget(QWidget):
    """
    Individual progress bar widget with:
    - Task name label
    - Progress bar
    - Status label (current file/action)
    - Statistics label (speed, ETA) - NEW v2.5.0+
    - Expand button (↗)
    - Close button (✖)
    - Pause button (⏸) - NEW v2.5.0+
    """
    # Signals
    expand_requested = Signal(str)  # task_id
    close_requested = Signal(str)   # task_id
    cancel_requested = Signal(str)  # task_id
    pause_requested = Signal(str, bool)  # task_id, is_paused - NEW v2.5.0+
    
    def __init__(self, task_id: str, task_name: str, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.task_name = task_name
        self.details_dialog = None
        
        # Time tracking (NEW - v2.5.0+)
        self.start_time = datetime.now()
        self.is_paused = False
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # Top row: task name + buttons
        top_layout = QHBoxLayout()
        
        self.name_label = QLabel(f"<b>{task_name}</b>")
        top_layout.addWidget(self.name_label)
        
        top_layout.addStretch()
        
        # Pause button (NEW - v2.5.0+)
        self.btn_pause = QPushButton("⏸")
        self.btn_pause.setFixedSize(25, 25)
        self.btn_pause.setCheckable(True)
        self.btn_pause.setToolTip("Pause/Resume task")
        self.btn_pause.clicked.connect(self._on_pause_clicked)
        top_layout.addWidget(self.btn_pause)
        
        # Expand button
        self.btn_expand = QPushButton("↗")
        self.btn_expand.setFixedSize(25, 25)
        self.btn_expand.setToolTip("Expand to detailed view")
        self.btn_expand.clicked.connect(self._on_expand_clicked)
        top_layout.addWidget(self.btn_expand)
        
        # Close button
        self.btn_close = QPushButton("✖")
        self.btn_close.setFixedSize(25, 25)
        self.btn_close.setToolTip("Close progress bar")
        self.btn_close.clicked.connect(self._on_close_clicked)
        top_layout.addWidget(self.btn_close)
        
        layout.addLayout(top_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Status label (current action)
        self.status_label = QLabel("Starting...")
        self.status_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.status_label)
        
        # Statistics label (NEW - v2.5.0+)
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #888; font-size: 9px;")
        layout.addWidget(self.stats_label)
        
        # Add border
        self.setStyleSheet("""
            ProgressBarWidget {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f9f9f9;
            }
        """)
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Update progress bar, status, and statistics (v2.5.0+)."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        
        # Calculate statistics (NEW - v2.5.0+)
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if current > 0 and elapsed > 0:
            speed = current / elapsed
            remaining = total - current
            eta_seconds = remaining / speed if speed > 0 else 0
            
            # Format statistics
            if eta_seconds < 60:
                eta_str = f"{int(eta_seconds)}s"
            elif eta_seconds < 3600:
                eta_str = f"{int(eta_seconds / 60)}m"
            else:
                eta_str = f"{int(eta_seconds / 3600)}h"
            
            speed_str = f"{speed:.1f}/s" if speed >= 1 else f"{speed*60:.1f}/min"
            self.stats_label.setText(f"Speed: {speed_str} | ETA: {eta_str}")
        
        if message:
            # Truncate long paths
            if len(message) > 60:
                message = "..." + message[-57:]
            self.status_label.setText(message)
        
        # Update details dialog if open
        if self.details_dialog and self.details_dialog.isVisible():
            self.details_dialog.update_progress(current, total, message)
    
    def add_log(self, message: str):
        """Add log entry to details dialog if open."""
        if self.details_dialog and self.details_dialog.isVisible():
            self.details_dialog.add_log(message)
    
    def set_complete(self, success: bool = True):
        """Mark task as complete and show notification (v2.5.0+)."""
        self.progress_bar.setValue(self.progress_bar.maximum())
        if success:
            self.status_label.setText("✓ Completed")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self._show_notification("Task Complete", f"{self.task_name} finished successfully")
        else:
            self.status_label.setText("✖ Failed")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self._show_notification("Task Failed", f"{self.task_name} failed or was cancelled")
    
    def _show_notification(self, title: str, message: str):
        """Show desktop notification (v2.5.0+)."""
        try:
            # Try using plyer for cross-platform notifications
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="Clarify",
                timeout=5
            )
        except ImportError:
            # Fallback: use system notification if available
            try:
                import subprocess
                import platform
                system = platform.system()
                if system == "Linux":
                    subprocess.run(["notify-send", title, message], check=False)
                elif system == "Darwin":  # macOS
                    subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}"'], check=False)
                # Windows would use win10toast, but skipping for now
            except Exception:
                pass  # Notifications not available, silently continue
    
    def _on_pause_clicked(self):
        """Handle pause button clicked (v2.5.0+)."""
        self.is_paused = self.btn_pause.isChecked()
        if self.is_paused:
            self.btn_pause.setText("▶")
            self.btn_pause.setToolTip("Resume task")
            self.status_label.setText("⏸ Paused")
        else:
            self.btn_pause.setText("⏸")
            self.btn_pause.setToolTip("Pause task")
        
        self.pause_requested.emit(self.task_id, self.is_paused)
    
    def _on_expand_clicked(self):
        """Show detailed progress dialog."""
        if not self.details_dialog:
            self.details_dialog = ProgressDetailsDialog(self.task_name, self)
            self.details_dialog.rejected.connect(lambda: self.cancel_requested.emit(self.task_id))
        
        # Update dialog with current state
        current = self.progress_bar.value()
        total = self.progress_bar.maximum()
        self.details_dialog.update_progress(current, total, self.status_label.text())
        
        self.details_dialog.show()
        self.details_dialog.raise_()
        self.details_dialog.activateWindow()
    
    def _on_close_clicked(self):
        """Request to close this progress bar."""
        self.close_requested.emit(self.task_id)
