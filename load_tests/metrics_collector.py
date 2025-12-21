"""
Metrics Collector - Sistema de coleta e análise de métricas de performance

Coleta métricas do sistema (CPU, RAM, Disk I/O) e operações individuais
em tempo real durante testes de carga.

Author: Josué Amaral
Date: 21/12/2024
"""

import psutil
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from pathlib import Path
import statistics


@dataclass
class SystemMetrics:
    """Snapshot de métricas do sistema em um momento"""
    timestamp: float
    cpu_percent: float  # 0-100
    memory_mb: float
    memory_percent: float  # 0-100
    disk_io_read_mb: float
    disk_io_write_mb: float
    num_processes: int


@dataclass
class OperationMetrics:
    """Métricas de uma operação individual"""
    operation_type: str
    duration_seconds: float
    size_mb: float
    timestamp: float
    success: bool
    error_msg: Optional[str] = None


@dataclass
class LoadTestAnalysis:
    """Resultado da análise de um load test"""
    scenario_name: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    error_rate: float
    
    # Throughput
    throughput_ops_per_sec: float
    throughput_mb_per_sec: float
    
    # Latência (segundos)
    latency_min: float
    latency_max: float
    latency_mean: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    
    # Recursos do sistema (médias)
    cpu_percent_avg: float
    cpu_percent_peak: float
    memory_mb_avg: float
    memory_mb_peak: float
    disk_io_mb_per_sec_avg: float
    
    # Detecção de gargalos
    cpu_saturation_detected: bool = False
    memory_pressure_detected: bool = False
    io_bottleneck_detected: bool = False
    thrashing_detected: bool = False
    
    # Timestamps
    test_start: float = 0.0
    test_end: float = 0.0
    test_duration: float = 0.0
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return asdict(self)


class MetricsCollector:
    """
    Coletor de métricas em tempo real durante testes de carga.
    
    Usage:
        collector = MetricsCollector()
        collector.start()
        
        # Durante o teste
        collector.snapshot_system()
        collector.record_operation("batch_process", 0.145, 5.0, success=True)
        
        # Após o teste
        analysis = collector.analyze(scenario_name="Batch Processing")
    """
    
    def __init__(self):
        self.system_snapshots: List[SystemMetrics] = []
        self.operations: List[OperationMetrics] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # Baseline do sistema (antes do teste)
        self._baseline_cpu: Optional[float] = None
        self._baseline_memory: Optional[float] = None
        
        # Cached process handle
        self._process = psutil.Process()
    
    def start(self):
        """Inicia coleta de métricas e captura baseline"""
        self.start_time = time.time()
        
        # Captura baseline (aguarda 1s para estabilizar)
        time.sleep(0.5)
        baseline = self.snapshot_system()
        self._baseline_cpu = baseline.cpu_percent
        self._baseline_memory = baseline.memory_mb
    
    def stop(self):
        """Finaliza coleta de métricas"""
        self.end_time = time.time()
    
    def snapshot_system(self) -> SystemMetrics:
        """
        Captura snapshot do estado atual do sistema.
        
        Returns:
            SystemMetrics com valores atuais
        """
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_mb = memory.used / (1024 * 1024)
        memory_percent = memory.percent
        
        # Disk I/O (acumulado desde boot)
        disk_io = psutil.disk_io_counters()
        disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
        disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
        
        # Processos
        num_processes = len(psutil.pids())
        
        snapshot = SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            memory_percent=memory_percent,
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            num_processes=num_processes
        )
        
        self.system_snapshots.append(snapshot)
        return snapshot
    
    def record_operation(
        self,
        operation_type: str,
        duration_seconds: float,
        size_mb: float,
        success: bool = True,
        error_msg: Optional[str] = None
    ):
        """
        Registra métricas de uma operação individual.
        
        Args:
            operation_type: Tipo de operação (ex: "batch_process", "set_union")
            duration_seconds: Tempo de execução em segundos
            size_mb: Tamanho dos dados processados em MB
            success: Se a operação foi bem-sucedida
            error_msg: Mensagem de erro (se success=False)
        """
        operation = OperationMetrics(
            operation_type=operation_type,
            duration_seconds=duration_seconds,
            size_mb=size_mb,
            timestamp=time.time(),
            success=success,
            error_msg=error_msg
        )
        
        self.operations.append(operation)
    
    def analyze(self, scenario_name: str = "Load Test") -> LoadTestAnalysis:
        """
        Analisa as métricas coletadas e gera insights.
        
        Args:
            scenario_name: Nome do cenário testado
            
        Returns:
            LoadTestAnalysis com estatísticas e detecção de gargalos
        """
        if not self.operations:
            raise ValueError("Nenhuma operação registrada para análise")
        
        # Operações
        total_ops = len(self.operations)
        successful_ops = sum(1 for op in self.operations if op.success)
        failed_ops = total_ops - successful_ops
        error_rate = failed_ops / total_ops if total_ops > 0 else 0.0
        
        # Throughput
        test_duration = (self.end_time or time.time()) - (self.start_time or 0)
        throughput_ops = successful_ops / test_duration if test_duration > 0 else 0
        
        total_mb_processed = sum(op.size_mb for op in self.operations if op.success)
        throughput_mb = total_mb_processed / test_duration if test_duration > 0 else 0
        
        # Latências (apenas operações bem-sucedidas)
        successful_durations = [op.duration_seconds for op in self.operations if op.success]
        
        if successful_durations:
            latency_min = min(successful_durations)
            latency_max = max(successful_durations)
            latency_mean = statistics.mean(successful_durations)
            latency_p50 = self._percentile(successful_durations, 50)
            latency_p95 = self._percentile(successful_durations, 95)
            latency_p99 = self._percentile(successful_durations, 99)
        else:
            latency_min = latency_max = latency_mean = 0.0
            latency_p50 = latency_p95 = latency_p99 = 0.0
        
        # Recursos do sistema
        if self.system_snapshots:
            cpu_percents = [s.cpu_percent for s in self.system_snapshots]
            cpu_avg = statistics.mean(cpu_percents)
            cpu_peak = max(cpu_percents)
            
            memory_mbs = [s.memory_mb for s in self.system_snapshots]
            memory_avg = statistics.mean(memory_mbs)
            memory_peak = max(memory_mbs)
            
            # Disk I/O (diferença entre primeiro e último snapshot / tempo)
            if len(self.system_snapshots) >= 2:
                first = self.system_snapshots[0]
                last = self.system_snapshots[-1]
                time_delta = last.timestamp - first.timestamp
                
                read_delta = last.disk_io_read_mb - first.disk_io_read_mb
                write_delta = last.disk_io_write_mb - first.disk_io_write_mb
                disk_io_avg = (read_delta + write_delta) / time_delta if time_delta > 0 else 0
            else:
                disk_io_avg = 0.0
        else:
            cpu_avg = cpu_peak = 0.0
            memory_avg = memory_peak = 0.0
            disk_io_avg = 0.0
        
        # Detecção de gargalos
        cpu_saturation = self._detect_cpu_saturation()
        memory_pressure = self._detect_memory_pressure()
        io_bottleneck = self._detect_io_bottleneck()
        thrashing = self._detect_thrashing()
        
        return LoadTestAnalysis(
            scenario_name=scenario_name,
            total_operations=total_ops,
            successful_operations=successful_ops,
            failed_operations=failed_ops,
            error_rate=error_rate,
            throughput_ops_per_sec=throughput_ops,
            throughput_mb_per_sec=throughput_mb,
            latency_min=latency_min,
            latency_max=latency_max,
            latency_mean=latency_mean,
            latency_p50=latency_p50,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            cpu_percent_avg=cpu_avg,
            cpu_percent_peak=cpu_peak,
            memory_mb_avg=memory_avg,
            memory_mb_peak=memory_peak,
            disk_io_mb_per_sec_avg=disk_io_avg,
            cpu_saturation_detected=cpu_saturation,
            memory_pressure_detected=memory_pressure,
            io_bottleneck_detected=io_bottleneck,
            thrashing_detected=thrashing,
            test_start=self.start_time or 0.0,
            test_end=self.end_time or 0.0,
            test_duration=test_duration
        )
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calcula percentil de uma lista de valores"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _detect_cpu_saturation(self) -> bool:
        """
        Detecta saturação de CPU (>95% por >5s consecutivos).
        
        Returns:
            True se CPU saturation foi detectada
        """
        if len(self.system_snapshots) < 2:
            return False
        
        # Procura por janela de 5s com CPU > 95%
        threshold = 95.0
        window_duration = 5.0
        
        high_cpu_start = None
        for snapshot in self.system_snapshots:
            if snapshot.cpu_percent > threshold:
                if high_cpu_start is None:
                    high_cpu_start = snapshot.timestamp
                elif snapshot.timestamp - high_cpu_start >= window_duration:
                    return True
            else:
                high_cpu_start = None
        
        return False
    
    def _detect_memory_pressure(self) -> bool:
        """
        Detecta pressão de memória (>90% disponível).
        
        Returns:
            True se memory pressure foi detectada
        """
        if not self.system_snapshots:
            return False
        
        threshold = 90.0
        return any(s.memory_percent > threshold for s in self.system_snapshots)
    
    def _detect_io_bottleneck(self) -> bool:
        """
        Detecta gargalo de I/O (disk I/O > 200MB/s sustentado).
        
        Returns:
            True se I/O bottleneck foi detectado
        """
        if len(self.system_snapshots) < 2:
            return False
        
        # Threshold arbitrário: 200MB/s é considerado alto para I/O sustentado
        threshold_mb_per_sec = 200.0
        
        # Calcula taxa de I/O entre snapshots consecutivos
        for i in range(1, len(self.system_snapshots)):
            prev = self.system_snapshots[i-1]
            curr = self.system_snapshots[i]
            
            time_delta = curr.timestamp - prev.timestamp
            if time_delta <= 0:
                continue
            
            read_rate = (curr.disk_io_read_mb - prev.disk_io_read_mb) / time_delta
            write_rate = (curr.disk_io_write_mb - prev.disk_io_write_mb) / time_delta
            total_rate = read_rate + write_rate
            
            if total_rate > threshold_mb_per_sec:
                return True
        
        return False
    
    def _detect_thrashing(self) -> bool:
        """
        Detecta thrashing (latência crescendo e > 2x baseline).
        
        Returns:
            True se thrashing foi detectado
        """
        if len(self.operations) < 10:
            return False
        
        # Calcula latência média da primeira metade vs segunda metade
        mid = len(self.operations) // 2
        first_half = [op.duration_seconds for op in self.operations[:mid] if op.success]
        second_half = [op.duration_seconds for op in self.operations[mid:] if op.success]
        
        if not first_half or not second_half:
            return False
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        # Thrashing: segunda metade é 2x mais lenta
        return second_avg > (first_avg * 2.0)
