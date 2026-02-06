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

try:
    from PySide6.QtCore import QThread, QObject
    _PYSIDE = True
except ImportError:
    _PYSIDE = False
    class QThread:  # pylint: disable=too-few-public-methods  # Stub class
        """Stub QThread when PySide6 not available."""
    class QObject:  # pylint: disable=too-few-public-methods  # Stub class
        """Stub QObject when PySide6 not available."""


class FeatureType(Enum):
    """Tipos de features que podem usar processamento threaded"""
    SEARCH_REPLACE = "search_replace"
    INSERT = "insert"
    JSON_TRANSLATE = "json_translate"
    JSON_REWRITER = "json_rewriter"
    JSON_SEARCH = "json_search"
    CASE_CONVERTER = "case_converter"
    TEXT_EXTRACTOR = "text_extractor"
    PLACEHOLDER_REPLACER = "placeholder_replacer"
    AI_FILE_PROCESSOR = "ai_file_processor"


# pylint: disable=too-few-public-methods  # Data class
class ThreadInfo:
    """Informações sobre uma thread ativa"""
    def __init__(self,
                 thread: QThread,
                 worker: QObject,
                 feature: FeatureType,
                 cancel_callback: Optional[Callable] = None):
        self.thread = thread
        self.worker = worker
        self.feature = feature
        self.cancel_callback = cancel_callback
        self.is_running = True


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
                    cancel_callback: Optional[Callable] = None) -> bool:
        """
        Registra e inicia uma thread.

        Args:
            thread_id: Identificador único da thread
            thread: QThread object
            worker: Worker object que executa o processamento
            feature: Tipo de feature sendo executada
            cancel_callback: Função para cancelar processamento

        Returns:
            True se thread foi iniciada, False se feature já está rodando
        """
        if self._shutdown:
            return False

        # Try to acquire feature lock
        if not self._feature_locks[feature].acquire(blocking=False):
            return False  # Feature is already running

        try:
            # Register thread
            info = ThreadInfo(thread, worker, feature, cancel_callback)
            self._threads[thread_id] = info

            # Connect automatic cleanup
            thread.finished.connect(lambda: self._on_thread_finished(thread_id))

            return True
        except Exception:  # pylint: disable=broad-exception-caught  # Thread safety
            # If something goes wrong, release the lock
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
                print(f"[ThreadManager] Error canceling thread {thread_id}: {e}")

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

    def _on_thread_finished(self, thread_id: str):
        """Callback called when thread finishes"""
        if thread_id in self._threads:
            info = self._threads[thread_id]

            # Release feature lock
            try:
                self._feature_locks[info.feature].release()
            except Exception:  # pylint: disable=broad-exception-caught  # Cleanup robustness
                pass  # Lock already released

            # Remove thread from registry
            del self._threads[thread_id]

    def get_active_threads(self) -> Dict[FeatureType, int]:
        """Returns count of active threads per feature"""
        counts = {feature: 0 for feature in FeatureType}
        for info in self._threads.values():
            if info.is_running:
                counts[info.feature] += 1
        return counts

    def is_feature_running(self, feature: FeatureType) -> bool:
        """Checks if any thread of the feature is running"""
        for info in self._threads.values():
            if info.feature == feature and info.is_running:
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
            if info.is_running:
                # Cancel thread
                self.cancel_thread(thread_id)

                # Wait for finish
                if not info.thread.wait(timeout_ms):
                    all_finished = False
                    print(f"[ThreadManager] Warning: Thread {thread_id} did not finish in time")

        return all_finished

    def force_cleanup(self):
        """
        Força limpeza de todas as threads.
        Usado apenas em emergência.
        """
        for thread_id, info in list(self._threads.items()):
            try:
                if info.thread.isRunning():
                    info.thread.terminate()
                    info.thread.wait(1000)
            except Exception as e:  # pylint: disable=broad-exception-caught  # Cleanup robustness
                print(f"[ThreadManager] Error forcing cleanup of {thread_id}: {e}")

        self._threads.clear()

        # Libera todos os locks
        for lock in self._feature_locks.values():
            try:
                lock.release()
            except Exception:  # pylint: disable=broad-exception-caught  # Cleanup robustness
                pass

    def get_stats(self) -> dict:
        """Retorna estatísticas sobre threads"""
        return {
            "total_threads": len(self._threads),
            "running_threads": sum(1 for info in self._threads.values() if info.is_running),
            "by_feature": self.get_active_threads(),
            "shutdown_mode": self._shutdown
        }


# Singleton global
thread_manager = ThreadManager()
