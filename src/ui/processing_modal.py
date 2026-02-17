#!/usr/bin/env python3
"""
processing_modal.py

Modal não-bloqueante para exibir progresso de processamento.
Permite minimizar/maximizar e continuar usando a aplicação.
"""
from typing import Optional

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel,
        QPushButton, QProgressBar, QWidget, QTextEdit
    )
    from PySide6.QtCore import Qt, QTimer, Signal
    from PySide6.QtGui import QFont
    from ..i18n.translator import tr, tooltip_tr
    _PYSIDE = True
except ImportError:
    _PYSIDE = False
    # Stubs for when PySide6 is not available
    # pylint: disable=too-few-public-methods,multiple-statements  # Stub classes
    class QDialog:
        """Stub QDialog."""
    class QVBoxLayout:
        """Stub QVBoxLayout."""
    class QHBoxLayout:
        """Stub QHBoxLayout."""
    class QLabel:
        """Stub QLabel."""
    class QPushButton:
        """Stub QPushButton."""
    class QProgressBar:
        """Stub QProgressBar."""
    class QWidget:
        """Stub QWidget."""
    class QTextEdit:
        """Stub QTextEdit."""
    class Qt:
        """Stub Qt."""
    class QTimer:
        """Stub QTimer."""
    class Signal:
        """Stub Signal."""
    class QFont:
        """Stub QFont."""


class ProcessingModal(QDialog):
    """
    Modal não-bloqueante para mostrar progresso de processamento.

    Features:
    - Não bloqueia a UI principal
    - Pode ser minimizado (reduz para barra de título)
    - Pode ser maximizado (mostra detalhes completos)
    - Mostra progresso com barra e percentual
    - Mostra mensagens de status
    - Botão para cancelar processamento
    - Sempre no topo (stays on top)
    """

    # Signal emitted when user clicks cancel
    cancel_requested = Signal()

    def __init__(self,
                 title: str = "Processing",
                 parent: Optional[QWidget] = None,
                 show_progress: bool = True,
                 show_cancel: bool = True):
        """
        Args:
            title: Título do modal
            parent: Widget pai
            show_progress: Se deve mostrar barra de progresso
            show_cancel: Se deve mostrar botão cancelar
        """
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(False)  # Non-blocking
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowStaysOnTopHint |  # Sempre no topo
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint
        )

        self._is_minimized = False
        self._show_progress = show_progress
        self._show_cancel = show_cancel

        self._setup_ui()
        self._apply_styles()

        # Timer for loading animation
        self._loading_timer = QTimer(self)
        self._loading_timer.timeout.connect(self._animate_loading)
        self._loading_dots = 0

        self.resize(500, 300)

    def _setup_ui(self):
        """Configura a interface do modal"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # === Header with title and buttons ===
        header = QHBoxLayout()

        self.lbl_title = QLabel("Processing...")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.lbl_title.setFont(font)
        header.addWidget(self.lbl_title)

        header.addStretch()

        # Minimize/maximize button
        self.btn_minimize = QPushButton("−")  # Minus symbol
        self.btn_minimize.setFixedSize(30, 30)
        self.btn_minimize.setToolTip(tooltip_tr("processing_modal.tooltip_minimize"))
        self.btn_minimize.clicked.connect(self.toggle_minimize)
        header.addWidget(self.btn_minimize)

        main_layout.addLayout(header)

        # === Content container (can be hidden) ===
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        # Status label with animation
        self.lbl_status = QLabel(tr("processing_modal.lbl_initializing"))
        self.lbl_status.setWordWrap(True)
        content_layout.addWidget(self.lbl_status)

        # Barra de progresso
        if self._show_progress:
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setTextVisible(True)
            content_layout.addWidget(self.progress_bar)

        # Log/details area (expandable)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        content_layout.addWidget(self.log_area)

        content_layout.addStretch()

        # === Footer with buttons ===
        footer = QHBoxLayout()
        footer.addStretch()

        if self._show_cancel:
            self.btn_cancel = QPushButton(tr("processing_modal.btn_cancel"))
            self.btn_cancel.clicked.connect(self._on_cancel_clicked)
            footer.addWidget(self.btn_cancel)

        content_layout.addLayout(footer)

        main_layout.addWidget(self.content_widget)

    def _apply_styles(self):
        """Aplica estilos CSS ao modal"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
            QLabel#title {
                color: #2c3e50;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton#minimize {
                background-color: #95a5a6;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#minimize:hover {
                background-color: #7f8c8d;
            }
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-family: monospace;
                font-size: 10pt;
            }
        """)

        self.btn_minimize.setObjectName("minimize")
        self.lbl_title.setObjectName("title")

    def toggle_minimize(self):
        """Alterna entre minimizado e maximizado"""
        self._is_minimized = not self._is_minimized

        if self._is_minimized:
            # Minimize: hide content
            self.content_widget.hide()
            self.btn_minimize.setText("□")  # Maximize symbol
            self.btn_minimize.setToolTip("Maximize")
            self.resize(500, 60)  # Minimum height
        else:
            # Maximize: show content
            self.content_widget.show()
            self.btn_minimize.setText("−")  # Minimize symbol
            self.btn_minimize.setToolTip("Minimize")
            self.resize(500, 300)

    def set_title(self, title: str):
        """Define o título do processamento"""
        self.lbl_title.setText(title)

    def set_status(self, message: str):
        """Define mensagem de status"""
        self.lbl_status.setText(message)
        self.log_message(f"[STATUS] {message}")

    def set_progress(self, value: int):
        """
        Define o progresso (0-100).
        Se value < 0, entra em modo indeterminado.
        """
        if not self._show_progress:
            return

        if value < 0:
            self.progress_bar.setRange(0, 0)  # Modo indeterminado
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(min(100, max(0, value)))

    def log_message(self, message: str):
        """Adiciona mensagem ao log"""
        self.log_area.append(message)
        # Auto-scroll para o final
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def start_loading_animation(self):
        """Inicia animação de loading (pontos piscando)"""
        self._loading_timer.start(500)  # 500ms

    def stop_loading_animation(self):
        """Para animação de loading"""
        self._loading_timer.stop()

    def _animate_loading(self):
        """Atualiza animação de loading"""
        self._loading_dots = (self._loading_dots + 1) % 4
        dots = "." * self._loading_dots
        base_text = self.lbl_status.text().rstrip(".")
        self.lbl_status.setText(f"{base_text}{dots}")

    def _on_cancel_clicked(self):
        """Callback quando botão cancelar é clicado"""
        self.cancel_requested.emit()
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setText("Canceling...")
        self.set_status("Cancellation requested, please wait...")

    def mark_completed(self, success: bool = True, message: str = ""):
        """
        Marca processamento como completo.

        Args:
            success: Se processamento foi bem-sucedido
            message: Mensagem final
        """
        self.stop_loading_animation()

        if success:
            self.set_title("✓ Completed")
            if not message:
                message = "Processing completed successfully!"
            self.set_status(message)
            if self._show_progress:
                self.progress_bar.setValue(100)
        else:
            self.set_title("✗ Failed")
            if not message:
                message = "Processing failed or was cancelled."
            self.set_status(message)

        # Replace cancel button with close
        if self._show_cancel and hasattr(self, 'btn_cancel'):
            self.btn_cancel.setText("Close")
            self.btn_cancel.setEnabled(True)
            self.btn_cancel.clicked.disconnect()
            self.btn_cancel.clicked.connect(self.accept)

    def closeEvent(self, event):  # pylint: disable=invalid-name  # Qt naming convention
        """Sobrescreve close event para emitir sinal de cancelamento"""
        if self._show_cancel and hasattr(self, 'btn_cancel'):
            if self.btn_cancel.text() != "Close":
                # Processing still active, emit cancellation
                self.cancel_requested.emit()
                event.ignore()  # Don't close yet
                return

        # Processing complete or cancel button doesn't exist
        self.stop_loading_animation()
        event.accept()


# pylint: disable=too-few-public-methods  # Minimal UI component
class MinimalProcessingModal(QDialog):
    """
    Versão minimalista do modal para operações rápidas.
    Apenas mostra spinner e mensagem, sem botões.
    """

    def __init__(self, message: str = "Processing...", parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setModal(False)
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint  # Sem bordas
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.lbl_message = QLabel(message)
        self.lbl_message.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        self.lbl_message.setFont(font)
        layout.addWidget(self.lbl_message)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        layout.addWidget(self.progress_bar)

        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
            QLabel {
                color: #2c3e50;
            }
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)

        self.resize(300, 100)

    def set_message(self, message: str):
        """Atualiza mensagem"""
        self.lbl_message.setText(message)
