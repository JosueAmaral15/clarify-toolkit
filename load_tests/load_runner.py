"""
Load Runner - Engine principal de testes de carga

Gerencia execução de cenários de teste com multiprocessing,
coleta métricas em tempo real e detecta gargalos de performance.

Author: Josué Amaral
Date: 21/12/2024
"""

import time
import multiprocessing
from multiprocessing import Process, Queue, Event
from dataclasses import dataclass
from typing import Callable, List, Any, Optional
from pathlib import Path

from .metrics_collector import MetricsCollector, LoadTestAnalysis
from .report_generator import ReportGenerator


@dataclass
class LoadConfig:
    """
    Configuração de um teste de carga.
    
    Attributes:
        num_workers: Número de processos paralelos
        warmup_duration: Duração da fase de aquecimento (segundos)
        rampup_duration: Duração da fase de ramp-up (segundos)
        sustain_duration: Duração da fase de carga máxima (segundos)
        cooldown_duration: Duração da fase de cooldown (segundos)
        metrics_interval: Intervalo entre snapshots de métricas (segundos)
    """
    num_workers: int = 4
    warmup_duration: float = 5.0
    rampup_duration: float = 10.0
    sustain_duration: float = 30.0
    cooldown_duration: float = 5.0
    metrics_interval: float = 0.5


class Worker(Process):
    """
    Processo de trabalho que executa operações em paralelo.
    
    Recebe tarefas via Queue, executa, e reporta métricas via Queue.
    """
    
    def __init__(
        self,
        worker_id: int,
        task_queue: Queue,
        metrics_queue: Queue,
        stop_event: Event
    ):
        super().__init__()
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.metrics_queue = metrics_queue
        self.stop_event = stop_event
    
    def run(self):
        """Loop principal do worker"""
        while not self.stop_event.is_set():
            try:
                # Tenta pegar tarefa (timeout 0.1s para checar stop_event)
                task = self.task_queue.get(timeout=0.1)
                
                if task is None:  # Sentinel value para parar
                    break
                
                operation_type, func, args, kwargs = task
                
                # Executa operação
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error_msg = None
                except Exception as e:
                    result = None
                    success = False
                    error_msg = str(e)
                
                duration = time.time() - start_time
                
                # Reporta métricas
                # Estima tamanho (se resultado for lista de tuplas com size_mb)
                size_mb = 0.0
                if isinstance(result, list) and result:
                    if isinstance(result[0], tuple) and len(result[0]) >= 3:
                        size_mb = sum(r[2] for r in result if len(r) >= 3)
                
                self.metrics_queue.put({
                    "worker_id": self.worker_id,
                    "operation_type": operation_type,
                    "duration": duration,
                    "size_mb": size_mb,
                    "success": success,
                    "error_msg": error_msg
                })
            
            except multiprocessing.queues.Empty:
                continue
            except Exception as e:
                # Erro crítico no worker
                self.metrics_queue.put({
                    "worker_id": self.worker_id,
                    "operation_type": "worker_error",
                    "duration": 0.0,
                    "size_mb": 0.0,
                    "success": False,
                    "error_msg": f"Worker critical error: {str(e)}"
                })
                break


class LoadRunner:
    """
    Engine principal para execução de testes de carga.
    
    Gerencia workers em multiprocessing, distribui tarefas, coleta métricas
    em tempo real e gera relatórios.
    
    Usage:
        config = LoadConfig(num_workers=8)
        runner = LoadRunner(config)
        
        analysis = runner.run_scenario(
            scenario_func=Scenarios.batch_file_processing,
            scenario_name="Batch Processing",
            scenario_args={"num_files": 1000}
        )
        
        ReportGenerator.to_console(analysis)
    """
    
    def __init__(self, config: LoadConfig):
        self.config = config
        self.workers: List[Worker] = []
        self.task_queue: Optional[Queue] = None
        self.metrics_queue: Optional[Queue] = None
        self.stop_event: Optional[Event] = None
        self.metrics_collector: Optional[MetricsCollector] = None
    
    def run_scenario(
        self,
        scenario_func: Callable,
        scenario_name: str,
        scenario_args: dict = None,
        show_progress: bool = True
    ) -> LoadTestAnalysis:
        """
        Executa cenário de teste completo com todas as fases.
        
        Fases:
        1. Warmup (10% carga)
        2. Ramp-up (10→100% carga gradual)
        3. Sustain (100% carga constante)
        4. Cooldown (100→0% carga gradual)
        
        Args:
            scenario_func: Função do cenário (ex: Scenarios.batch_file_processing)
            scenario_name: Nome do cenário (para relatório)
            scenario_args: Argumentos para passar ao cenário
            show_progress: Se True, mostra progresso em tempo real
            
        Returns:
            LoadTestAnalysis com resultados completos
        """
        if scenario_args is None:
            scenario_args = {}
        
        print(f"\n🚀 Iniciando Load Test: {scenario_name}")
        print(f"   Workers: {self.config.num_workers}")
        print(f"   Warmup: {self.config.warmup_duration}s")
        print(f"   Ramp-up: {self.config.rampup_duration}s")
        print(f"   Sustain: {self.config.sustain_duration}s")
        print(f"   Cooldown: {self.config.cooldown_duration}s")
        print()
        
        # Inicializa recursos
        self._setup()
        
        try:
            # Fase 1: Warmup
            if show_progress:
                print("📊 Fase 1/4: Warmup (10% carga)...")
            self._warmup_phase(scenario_func, scenario_args)
            
            # Fase 2: Ramp-up
            if show_progress:
                print("📈 Fase 2/4: Ramp-up (10→100% carga)...")
            self._rampup_phase(scenario_func, scenario_args)
            
            # Fase 3: Sustain
            if show_progress:
                print("💪 Fase 3/4: Sustain (100% carga constante)...")
            self._sustain_phase(scenario_func, scenario_args)
            
            # Fase 4: Cooldown
            if show_progress:
                print("🔽 Fase 4/4: Cooldown (100→0% carga)...")
            self._cooldown_phase()
            
            # Finaliza coleta
            self.metrics_collector.stop()
            
            # Processa métricas restantes na queue
            self._drain_metrics_queue()
            
            # Analisa resultados
            if show_progress:
                print("\n📊 Analisando resultados...")
            
            analysis = self.metrics_collector.analyze(scenario_name=scenario_name)
            
            return analysis
        
        finally:
            self._cleanup()
    
    def _setup(self):
        """Inicializa queues, workers e metrics collector"""
        # Queues
        self.task_queue = Queue()
        self.metrics_queue = Queue()
        self.stop_event = Event()
        
        # Metrics collector
        self.metrics_collector = MetricsCollector()
        self.metrics_collector.start()
        
        # Workers
        self.workers = []
        for i in range(self.config.num_workers):
            worker = Worker(
                worker_id=i,
                task_queue=self.task_queue,
                metrics_queue=self.metrics_queue,
                stop_event=self.stop_event
            )
            worker.start()
            self.workers.append(worker)
    
    def _cleanup(self):
        """Finaliza workers e limpa recursos"""
        # Sinaliza workers para parar
        self.stop_event.set()
        
        # Envia sentinel values
        for _ in self.workers:
            self.task_queue.put(None)
        
        # Aguarda workers terminarem (timeout 5s)
        for worker in self.workers:
            worker.join(timeout=5.0)
            if worker.is_alive():
                worker.terminate()
        
        self.workers = []
    
    def _warmup_phase(self, scenario_func: Callable, scenario_args: dict):
        """Fase de aquecimento (10% da carga)"""
        num_tasks = max(1, self.config.num_workers // 10)
        duration = self.config.warmup_duration
        
        self._execute_phase(scenario_func, scenario_args, num_tasks, duration)
    
    def _rampup_phase(self, scenario_func: Callable, scenario_args: dict):
        """Fase de ramp-up (aumenta carga gradualmente 10→100%)"""
        duration = self.config.rampup_duration
        steps = 10  # 10 incrementos
        step_duration = duration / steps
        
        for step in range(1, steps + 1):
            load_percent = step * 10  # 10%, 20%, ..., 100%
            num_tasks = max(1, (self.config.num_workers * load_percent) // 100)
            
            self._execute_phase(scenario_func, scenario_args, num_tasks, step_duration)
    
    def _sustain_phase(self, scenario_func: Callable, scenario_args: dict):
        """Fase de carga máxima (100% sustentado)"""
        num_tasks = self.config.num_workers
        duration = self.config.sustain_duration
        
        self._execute_phase(scenario_func, scenario_args, num_tasks, duration)
    
    def _cooldown_phase(self):
        """Fase de cooldown (reduz carga gradualmente)"""
        # Apenas aguarda e coleta métricas, sem adicionar novas tarefas
        start = time.time()
        while time.time() - start < self.config.cooldown_duration:
            self.metrics_collector.snapshot_system()
            time.sleep(self.config.metrics_interval)
    
    def _execute_phase(
        self,
        scenario_func: Callable,
        scenario_args: dict,
        num_tasks: int,
        duration: float
    ):
        """
        Executa uma fase do teste, enviando tarefas e coletando métricas.
        
        Args:
            scenario_func: Função do cenário
            scenario_args: Argumentos do cenário
            num_tasks: Número de tarefas paralelas
            duration: Duração da fase (segundos)
        """
        phase_start = time.time()
        
        # Envia tarefas iniciais
        for _ in range(num_tasks):
            self.task_queue.put((
                scenario_func.__name__,
                scenario_func,
                [],
                scenario_args
            ))
        
        # Loop da fase
        while time.time() - phase_start < duration:
            # Coleta snapshot de sistema
            self.metrics_collector.snapshot_system()
            
            # Processa métricas de operações completadas
            self._drain_metrics_queue(block=False)
            
            # Aguarda intervalo
            time.sleep(self.config.metrics_interval)
            
            # Adiciona mais tarefas se workers estiverem ociosos
            # (mantém carga constante)
            if self.task_queue.qsize() < num_tasks:
                for _ in range(num_tasks - self.task_queue.qsize()):
                    self.task_queue.put((
                        scenario_func.__name__,
                        scenario_func,
                        [],
                        scenario_args
                    ))
    
    def _drain_metrics_queue(self, block: bool = True):
        """
        Processa todas as métricas na queue.
        
        Args:
            block: Se True, bloqueia até processar todas; se False, processa
                   apenas as disponíveis
        """
        while True:
            try:
                timeout = None if block else 0.01
                metrics = self.metrics_queue.get(timeout=timeout)
                
                # Registra operação no collector
                self.metrics_collector.record_operation(
                    operation_type=metrics["operation_type"],
                    duration_seconds=metrics["duration"],
                    size_mb=metrics["size_mb"],
                    success=metrics["success"],
                    error_msg=metrics.get("error_msg")
                )
            
            except multiprocessing.queues.Empty:
                break
