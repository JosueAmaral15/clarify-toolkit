#!/usr/bin/env python3
"""
thread_manager.py

Sistema centralizado de gerenciamento de threads para o Clarify.
Garante que threads não fiquem órfãs e previne execução simultânea
da mesma feature.
"""
import threading
from typing import Dict, Optional, Callable
from enum import Enum


from ..utils.logger import get_logger

logger = get_logger(__name__)

try:
    from PySide6.QtCore import QThread, QObject, Slot
    _PYSIDE = True
except ImportError:
    _PYSIDE = False
    class QThread:  # pylint: disable=too-few-public-methods  # Stub class
        """Stub QThread when PySide6 not available."""
    class QObject:  # pylint: disable=too-few-public-methods  # Stub class
        """Stub QObject when PySide6 not available."""


if _PYSIDE:
    class _ThreadFinishedReceiver(QObject):
        """GUI-owned completion survives destruction of the thread's former dock."""

        def __init__(self, manager, thread_id, completion_token):
            super().__init__()
            self.manager = manager
            self.thread_id = thread_id
            self.completion_token = completion_token

        @Slot()
        def finished(self):
            self.manager._on_thread_finished(self.thread_id, self.completion_token)


class FeatureType(Enum):
    """Tipos de features que podem usar processamento threaded"""
    SEARCH_REPLACE = "search_replace"
    FILE_EXPLORER = "file_explorer"
    INSERT = "insert"
    JSON_TRANSLATE = "json_translate"
    JSON_REWRITER = "json_rewriter"
    JSON_SEARCH = "json_search"
    CASE_CONVERTER = "case_converter"
    TEXT_EXTRACTOR = "text_extractor"
    PLACEHOLDER_REPLACER = "placeholder_replacer"
    AI_FILE_PROCESSOR = "ai_file_processor"
    TUTORIAL_ASSISTANT = "tutorial_assistant"
    GOOGLE_TRANSLATE = "google_translate"


# pylint: disable=too-few-public-methods  # Data class
class ThreadInfo:
    """Informações sobre uma thread ativa"""
    def __init__(self,
                 thread: QThread,
                 worker: QObject,
                 feature: FeatureType,
                 cancel_callback: Optional[Callable] = None,
                 exclusive: bool = True):
        self.thread = thread
        self.worker = worker
        self.feature = feature
        self.cancel_callback = cancel_callback
        self.is_running = True
        self.exclusive = exclusive
        self.finished_receiver = None
        self.completion_token = object()


class ThreadManager:
    """
    Singleton para gerenciar todas as threads da aplicação.

    Funcionalidades:
    - Rastreia todas as threads ativas por feature
    - Previne execução simultânea da mesma feature (locks)
    - Permite múltiplas features diferentes rodando em paralelo
    - Garante cleanup adequado ao fechar aplicação
    - Previne threads órfãs
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:  # pylint: disable=access-member-before-definition  # Set in __new__
            return

        self._initialized = True
        self._threads: Dict[str, ThreadInfo] = {}
        self._feature_locks: Dict[FeatureType, threading.Lock] = {
            feature: threading.Lock() for feature in FeatureType
        }
        self._shutdown = False

    def can_start_feature(self, feature: FeatureType) -> bool:
        """
        Verifica se uma feature pode ser iniciada.
        Retorna False se a feature já está em execução.
        """
        # Tenta adquirir o lock sem bloquear
        acquired = self._feature_locks[feature].acquire(blocking=False)
        if acquired:
            # Se conseguiu o lock, libera imediatamente (apenas checando)
            self._feature_locks[feature].release()
            return True
        return False

    # pylint: disable=too-many-positional-arguments  # Thread management requires all parameters
    def start_thread(self,
                    thread_id: str,
                    thread: QThread,
                    worker: QObject,
                    feature: FeatureType,
                    cancel_callback: Optional[Callable] = None,
                    *, exclusive: bool = True) -> bool:
        """
        Registra uma thread; o chamador inicia a execucao.

        Args:
            thread_id: Identificador único da thread
            thread: QThread object
            worker: Worker object que executa o processamento
            feature: Tipo de feature sendo executada
            cancel_callback: Função para cancelar processamento
            exclusive: Preserve the feature lock unless the caller owns its operation gate.

        Returns:
            True se thread foi iniciada, False se feature já está rodando
        """
        if self._shutdown:
            return False

        # Try to acquire feature lock
        if thread_id in self._threads:
            return False
        if exclusive and not self._feature_locks[feature].acquire(blocking=False):
            return False  # Feature is already running

        try:
            # Register thread
            info = ThreadInfo(thread, worker, feature, cancel_callback, exclusive)
            self._threads[thread_id] = info

            # Connect automatic cleanup
            if _PYSIDE:
                info.finished_receiver = _ThreadFinishedReceiver(
                    self, thread_id, info.completion_token
                )
                thread.finished.connect(info.finished_receiver.finished)
            else:
                thread.finished.connect(
                    lambda token=info.completion_token: self._on_thread_finished(thread_id, token)
                )

            return True
        except Exception:  # pylint: disable=broad-exception-caught  # Thread safety
            # If something goes wrong, release the lock
            failed = self._threads.pop(thread_id, None)
            if failed is not None and failed.finished_receiver is not None:
                failed.finished_receiver.deleteLater()
            if exclusive:
                self._feature_locks[feature].release()
            return False

    def cancel_thread(self, thread_id: str) -> bool:
        """
        Cancela uma thread específica.

        Returns:
            True se thread foi cancelada, False se não existe
        """
        if thread_id not in self._threads:
            return False

        info = self._threads[thread_id]

        # Call cancellation callback if available
        if info.cancel_callback:
            try:
                info.cancel_callback()
            except Exception as e:  # pylint: disable=broad-exception-caught  # Cleanup robustness
                logger.error(f"[ThreadManager] Error canceling thread {thread_id}: {e}")

        # Mark as not running
        info.is_running = False

        # Thread will be removed automatically when finished
        return True

    def cancel_feature(self, feature: FeatureType) -> int:
        """
        Cancela todas as threads de uma feature específica.

        Returns:
            Número de threads canceladas
        """
        count = 0
        for thread_id, info in list(self._threads.items()):
            if info.feature == feature and info.is_running:
                if self.cancel_thread(thread_id):
                    count += 1
        return count

    def _on_thread_finished(self, thread_id: str, completion_token=None):
        """Callback called when thread finishes"""
        if thread_id in self._threads:
            info = self._threads[thread_id]
            # A queued native completion can arrive after explicit settlement
            # and registration of another operation under the same public ID.
            if completion_token is not None and completion_token is not info.completion_token:
                return

            # Release feature lock
            try:
                if info.exclusive:
                    self._feature_locks[info.feature].release()
            except Exception:  # pylint: disable=broad-exception-caught  # Cleanup robustness
                pass  # Lock already released

            # Remove thread from registry
            del self._threads[thread_id]
            if info.finished_receiver is not None:
                info.finished_receiver.deleteLater()

    def get_active_threads(self) -> Dict[FeatureType, int]:
        """Returns count of active threads per feature"""
        counts = {feature: 0 for feature in FeatureType}
        for info in self._threads.values():
            if info.is_running or info.thread.isRunning():
                counts[info.feature] += 1
        return counts

    def is_feature_running(self, feature: FeatureType) -> bool:
        """Checks if any thread of the feature is running"""
        for info in self._threads.values():
            if info.feature == feature and (info.is_running or info.thread.isRunning()):
                return True
        return False

    def wait_all_threads(self, timeout_ms: int = 5000) -> bool:
        """
        Wait for all threads to finish.
        Used when closing the application.

        Args:
            timeout_ms: Timeout em milissegundos para cada thread

        Returns:
            True se todas terminaram, False se houve timeout
        """
        self._shutdown = True

        all_finished = True
        for thread_id, info in list(self._threads.items()):
            if info.is_running or info.thread.isRunning():
                # Cancel thread
                self.cancel_thread(thread_id)

                # Wait for finish
                if not info.thread.wait(timeout_ms):
                    all_finished = False
                    logger.error(f"[ThreadManager] Warning: Thread {thread_id} did not finish in time")

        if not all_finished:
            self._shutdown = False
        return all_finished

    def resume_registration(self):
        """A rejected application close must not permanently disable new work."""
        self._shutdown = False

    def force_cleanup(self):
        """
        Força limpeza de todas as threads.
        Usado apenas em emergência.
        """
        protected = {}
        cooperative_only = {
            FeatureType.FILE_EXPLORER,
            FeatureType.GOOGLE_TRANSLATE,
            FeatureType.INSERT,
            FeatureType.TEXT_EXTRACTOR,
        }
        for thread_id, info in list(self._threads.items()):
            try:
                if info.feature in cooperative_only and info.thread.isRunning():
                    self.cancel_thread(thread_id)
                    protected[thread_id] = info
                    continue
                if info.thread.isRunning():
                    info.thread.terminate()
                    info.thread.wait(1000)
            except Exception as e:  # pylint: disable=broad-exception-caught  # Cleanup robustness
                logger.error(f"[ThreadManager] Error forcing cleanup of {thread_id}: {e}")

        self._threads = protected

        # Libera todos os locks
        protected_features = {info.feature for info in protected.values() if info.exclusive}
        for feature, lock in self._feature_locks.items():
            if feature in protected_features:
                continue
            try:
                lock.release()
            except Exception:  # pylint: disable=broad-exception-caught  # Cleanup robustness
                pass

    def get_stats(self) -> dict:
        """Retorna estatísticas sobre threads"""
        return {
            "total_threads": len(self._threads),
            "running_threads": sum(1 for info in self._threads.values() if info.is_running or info.thread.isRunning()),
            "by_feature": self.get_active_threads(),
            "shutdown_mode": self._shutdown
        }


# Singleton global
thread_manager = ThreadManager()
