"""Clock, stopwatch, and countdown timer tool."""

from PySide6.QtCore import QElapsedTimer, QTime, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.i18n.translator import tr
from src.processing_feedback import notify_processing_completed


def _format_duration(total_seconds: int) -> str:
    hours, remainder = divmod(max(0, total_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class ClockDock(QWidget):
    """A bounded utility with clock, stopwatch, and countdown views."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ClockDock")
        self._stopwatch_elapsed_ms = 0
        self._stopwatch_clock = QElapsedTimer()
        self._remaining_seconds = 0
        self._build_ui()
        self._create_timers()
        self._update_clock()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        clock_page = QWidget()
        clock_layout = QVBoxLayout(clock_page)
        self.clock_label = QLabel()
        self.clock_label.setObjectName("clockDisplay")
        self.clock_label.setStyleSheet("font-size: 32px; font-weight: 600;")
        clock_layout.addStretch()
        clock_layout.addWidget(self.clock_label)
        clock_layout.addStretch()
        self.tabs.addTab(clock_page, tr("clock.clock", "Clock"))

        stopwatch_page = QWidget()
        stopwatch_layout = QVBoxLayout(stopwatch_page)
        self.stopwatch_label = QLabel("00:00:00.0")
        self.stopwatch_label.setStyleSheet("font-size: 28px; font-weight: 600;")
        stopwatch_layout.addWidget(self.stopwatch_label)
        stopwatch_buttons = QHBoxLayout()
        self.stopwatch_start_button = QPushButton(tr("clock.start", "Start"))
        self.stopwatch_pause_button = QPushButton(tr("clock.pause", "Pause"))
        self.stopwatch_reset_button = QPushButton(tr("clock.reset", "Reset"))
        self.stopwatch_start_button.clicked.connect(self._start_stopwatch)
        self.stopwatch_pause_button.clicked.connect(self._pause_stopwatch)
        self.stopwatch_reset_button.clicked.connect(self._reset_stopwatch)
        stopwatch_buttons.addWidget(self.stopwatch_start_button)
        stopwatch_buttons.addWidget(self.stopwatch_pause_button)
        stopwatch_buttons.addWidget(self.stopwatch_reset_button)
        stopwatch_layout.addLayout(stopwatch_buttons)
        stopwatch_layout.addStretch()
        self.tabs.addTab(stopwatch_page, tr("clock.stopwatch", "Stopwatch"))

        timer_page = QWidget()
        timer_layout = QVBoxLayout(timer_page)
        duration_row = QHBoxLayout()
        self.timer_minutes = QSpinBox()
        self.timer_minutes.setRange(0, 999)
        self.timer_minutes.setSuffix(" min")
        self.timer_seconds = QSpinBox()
        self.timer_seconds.setRange(0, 59)
        self.timer_seconds.setSuffix(" s")
        duration_row.addWidget(self.timer_minutes)
        duration_row.addWidget(self.timer_seconds)
        timer_layout.addLayout(duration_row)
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet("font-size: 28px; font-weight: 600;")
        timer_layout.addWidget(self.timer_label)
        timer_buttons = QHBoxLayout()
        self.timer_start_button = QPushButton(tr("clock.start", "Start"))
        self.timer_pause_button = QPushButton(tr("clock.pause", "Pause"))
        self.timer_reset_button = QPushButton(tr("clock.reset", "Reset"))
        self.timer_start_button.clicked.connect(self._start_countdown)
        self.timer_pause_button.clicked.connect(self._pause_countdown)
        self.timer_reset_button.clicked.connect(self._reset_countdown)
        timer_buttons.addWidget(self.timer_start_button)
        timer_buttons.addWidget(self.timer_pause_button)
        timer_buttons.addWidget(self.timer_reset_button)
        timer_layout.addLayout(timer_buttons)
        timer_layout.addStretch()
        self.tabs.addTab(timer_page, tr("clock.timer", "Timer"))

    def _create_timers(self):
        self._clock_timer = QTimer(self)
        self._clock_timer.setInterval(1000)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start()

        self._stopwatch_timer = QTimer(self)
        self._stopwatch_timer.setInterval(100)
        self._stopwatch_timer.timeout.connect(self._update_stopwatch)

        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._tick_countdown)

    def _update_clock(self):
        self.clock_label.setText(QTime.currentTime().toString("HH:mm:ss"))

    def _start_stopwatch(self):
        if not self._stopwatch_timer.isActive():
            self._stopwatch_clock.start()
            self._stopwatch_timer.start()

    def _pause_stopwatch(self):
        if self._stopwatch_timer.isActive():
            self._stopwatch_elapsed_ms += self._stopwatch_clock.elapsed()
            self._stopwatch_timer.stop()
            self._stopwatch_clock.invalidate()
            self._update_stopwatch()

    def _reset_stopwatch(self):
        self._stopwatch_timer.stop()
        self._stopwatch_clock.invalidate()
        self._stopwatch_elapsed_ms = 0
        self.stopwatch_label.setText("00:00:00.0")

    def _update_stopwatch(self):
        elapsed_ms = self._stopwatch_elapsed_ms
        if self._stopwatch_clock.isValid():
            elapsed_ms += self._stopwatch_clock.elapsed()
        seconds, tenths = divmod(elapsed_ms // 100, 10)
        self.stopwatch_label.setText(f"{_format_duration(seconds)}.{tenths}")

    def _start_countdown(self):
        if self._countdown_timer.isActive():
            return
        if self._remaining_seconds <= 0:
            self._remaining_seconds = (
                self.timer_minutes.value() * 60 + self.timer_seconds.value()
            )
        self._update_countdown_label()
        if self._remaining_seconds > 0:
            self._countdown_timer.start()

    def _pause_countdown(self):
        self._countdown_timer.stop()

    def _reset_countdown(self):
        self._countdown_timer.stop()
        self._remaining_seconds = 0
        self._update_countdown_label()

    def _tick_countdown(self):
        if self._remaining_seconds <= 0:
            self._countdown_timer.stop()
            return
        self._remaining_seconds -= 1
        self._update_countdown_label()
        if self._remaining_seconds == 0:
            self._countdown_timer.stop()
            notify_processing_completed()

    def _update_countdown_label(self):
        self.timer_label.setText(_format_duration(self._remaining_seconds))

    def closeEvent(self, event):
        self._clock_timer.stop()
        self._stopwatch_timer.stop()
        self._countdown_timer.stop()
        super().closeEvent(event)
