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
    class QThread: pass
    class QObject: pass


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
        if self._initialized:
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
        
        # Tenta adquirir lock da feature
        if not self._feature_locks[feature].acquire(blocking=False):
            return False  # Feature já está rodando
        
        try:
            # Registra thread
            info = ThreadInfo(thread, worker, feature, cancel_callback)
            self._threads[thread_id] = info
            
            # Conecta cleanup automático
            thread.finished.connect(lambda: self._on_thread_finished(thread_id))
            
            return True
        except Exception:
            # Se algo der errado, libera o lock
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
        
        # Chama callback de cancelamento se disponível
        if info.cancel_callback:
            try:
                info.cancel_callback()
            except Exception as e:
                print(f"[ThreadManager] Error canceling thread {thread_id}: {e}")
        
        # Marca como não rodando
        info.is_running = False
        
        # Thread será removida automaticamente quando terminar
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
        """Callback chamado quando thread termina"""
        if thread_id in self._threads:
            info = self._threads[thread_id]
            
            # Libera lock da feature
            try:
                self._feature_locks[info.feature].release()
            except Exception:
                pass  # Lock já foi liberado
            
            # Remove thread do registro
            del self._threads[thread_id]
    
    def get_active_threads(self) -> Dict[FeatureType, int]:
        """Retorna contagem de threads ativas por feature"""
        counts = {feature: 0 for feature in FeatureType}
        for info in self._threads.values():
            if info.is_running:
                counts[info.feature] += 1
        return counts
    
    def is_feature_running(self, feature: FeatureType) -> bool:
        """Verifica se alguma thread da feature está rodando"""
        for info in self._threads.values():
            if info.feature == feature and info.is_running:
                return True
        return False
    
    def wait_all_threads(self, timeout_ms: int = 5000) -> bool:
        """
        Aguarda término de todas as threads.
        Usado no fechamento da aplicação.
        
        Args:
            timeout_ms: Timeout em milissegundos para cada thread
        
        Returns:
            True se todas terminaram, False se houve timeout
        """
        self._shutdown = True
        
        all_finished = True
        for thread_id, info in list(self._threads.items()):
            if info.is_running:
                # Cancela thread
                self.cancel_thread(thread_id)
                
                # Aguarda término
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
            except Exception as e:
                print(f"[ThreadManager] Error forcing cleanup of {thread_id}: {e}")
        
        self._threads.clear()
        
        # Libera todos os locks
        for lock in self._feature_locks.values():
            try:
                lock.release()
            except Exception:
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
