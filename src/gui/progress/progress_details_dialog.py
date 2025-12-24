"""
Progress details dialog showing expanded information.
Extracted from app.py (v2.9.114).
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QTextEdit, QPushButton
)


class ProgressDetailsDialog(QDialog):
    """
    Expanded dialog showing detailed progress information.
    Shown when user clicks the expand button on a progress bar.
    Enhanced with time estimation and statistics (v2.5.0+).
    """
    def __init__(self, task_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Progress Details - {task_name}")
        self.setModal(False)
        self.resize(600, 450)
        
        # Time tracking
        self.start_time = datetime.now()
        self.last_update_time = self.start_time
        
        layout = QVBoxLayout(self)
        
        # Task name label
        name_label = QLabel(f"<h3>{task_name}</h3>")
        layout.addWidget(name_label)
        
        # Progress bar (larger)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(30)
        layout.addWidget(self.progress_bar)
        
        # Status label with time estimation
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)
        
        # Statistics label (NEW - v2.5.0+)
        self.stats_label = QLabel("Speed: calculating...")
        self.stats_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.stats_label)
        
        # Details text (log area)
        details_label = QLabel("<b>Processing Details:</b>")
        layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumBlockCount(1000)  # Limit log size
        layout.addWidget(self.details_text)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_minimize = QPushButton("↓ Minimize to Bar")
        self.btn_minimize.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_minimize)
        
        # Pause/Resume button (NEW - v2.5.0+)
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_pause.setCheckable(True)
        btn_layout.addWidget(self.btn_pause)
        
        self.btn_cancel = QPushButton("✖ Cancel Task")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Update progress bar, status, and statistics (v2.5.0+)."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        
        percent = (current / total * 100) if total > 0 else 0
        status = f"Progress: {current}/{total} ({percent:.1f}%)"
        
        # Calculate time estimation (NEW - v2.5.0+)
        now = datetime.now()
        elapsed = (now - self.start_time).total_seconds()
        
        if current > 0 and total > 0:
            # Calculate ETA
            speed = current / elapsed if elapsed > 0 else 0
            remaining = total - current
            eta_seconds = remaining / speed if speed > 0 else 0
            
            # Format time strings
            def format_time(seconds):
                if seconds < 60:
                    return f"{int(seconds)}s"
                elif seconds < 3600:
                    return f"{int(seconds / 60)}m {int(seconds % 60)}s"
                else:
                    hours = int(seconds / 3600)
                    minutes = int((seconds % 3600) / 60)
                    return f"{hours}h {minutes}m"
            
            elapsed_str = format_time(elapsed)
            eta_str = format_time(eta_seconds) if eta_seconds > 0 else "calculating..."
            
            status += f" | Elapsed: {elapsed_str} | ETA: {eta_str}"
            
            # Update statistics label
            speed_str = f"{speed:.2f} files/sec" if speed >= 1 else f"{speed*60:.1f} files/min"
            self.stats_label.setText(f"Speed: {speed_str} | Total time: {elapsed_str}")
        
        if message:
            status += f"\n{message}"
        
        self.status_label.setText(status)
        self.last_update_time = now
    
    def add_log(self, message: str):
        """Add a log entry to details text."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.details_text.append(f"[{timestamp}] {message}")
