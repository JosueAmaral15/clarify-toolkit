"""
Unit Tests para Load Testing System

Testa componentes do sistema de load testing:
- MetricsCollector (coleta e análise)
- ReportGenerator (formatação)
- Scenarios (geração de corpus)
- LoadRunner (engine básico)

Author: Josué Amaral
Date: 21/12/2024
"""

import pytest
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import multiprocessing

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from load_tests.metrics_collector import (
    MetricsCollector,
    SystemMetrics,
    OperationMetrics,
    LoadTestAnalysis
)
from load_tests.report_generator import ReportGenerator
from load_tests.scenarios import Scenarios
from load_tests.load_runner import LoadRunner, LoadConfig, Worker


class TestMetricsCollector:
    """Testes para MetricsCollector"""
    
    def test_snapshot_system_metrics(self):
        """Testa captura de snapshot do sistema"""
        collector = MetricsCollector()
        
        snapshot = collector.snapshot_system()
        
        assert isinstance(snapshot, SystemMetrics)
        assert snapshot.cpu_percent >= 0
        assert snapshot.memory_mb > 0
        assert snapshot.memory_percent >= 0
        assert snapshot.num_processes > 0
    
    def test_record_operation(self):
        """Testa registro de operações"""
        collector = MetricsCollector()
        
        collector.record_operation(
            operation_type="test_op",
            duration_seconds=0.5,
            size_mb=10.0,
            success=True
        )
        
        assert len(collector.operations) == 1
        op = collector.operations[0]
        assert op.operation_type == "test_op"
        assert op.duration_seconds == 0.5
        assert op.size_mb == 10.0
        assert op.success is True
    
    def test_analyze_with_operations(self):
        """Testa análise de métricas coletadas"""
        collector = MetricsCollector()
        collector.start_time = time.time() - 10.0
        collector.end_time = time.time()
        
        # Adiciona operações mock
        for i in range(10):
            collector.record_operation(
                operation_type="test_op",
                duration_seconds=0.1 + (i * 0.01),
                size_mb=1.0,
                success=True
            )
        
        # Adiciona snapshots mock
        for i in range(5):
            collector.system_snapshots.append(
                SystemMetrics(
                    timestamp=time.time(),
                    cpu_percent=50.0 + i,
                    memory_mb=1000.0 + (i * 100),
                    memory_percent=60.0,
                    disk_io_read_mb=100.0,
                    disk_io_write_mb=50.0,
                    num_processes=100
                )
            )
        
        analysis = collector.analyze("Test Scenario")
        
        assert isinstance(analysis, LoadTestAnalysis)
        assert analysis.scenario_name == "Test Scenario"
        assert analysis.total_operations == 10
        assert analysis.successful_operations == 10
        assert analysis.failed_operations == 0
        assert analysis.error_rate == 0.0
        assert analysis.throughput_ops_per_sec > 0
        assert analysis.latency_min > 0
        assert analysis.latency_max > 0
    
    def test_percentile_calculation(self):
        """Testa cálculo de percentis"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        
        p50 = MetricsCollector._percentile(data, 50)
        p95 = MetricsCollector._percentile(data, 95)
        
        assert 5.0 <= p50 <= 6.0
        assert 9.0 <= p95 <= 10.0
    
    def test_detect_cpu_saturation(self):
        """Testa detecção de saturação de CPU"""
        collector = MetricsCollector()
        
        # Simula CPU alta por >5s
        base_time = time.time()
        for i in range(12):  # 12 snapshots x 0.5s = 6s
            collector.system_snapshots.append(
                SystemMetrics(
                    timestamp=base_time + (i * 0.5),
                    cpu_percent=96.0,
                    memory_mb=1000.0,
                    memory_percent=60.0,
                    disk_io_read_mb=100.0,
                    disk_io_write_mb=50.0,
                    num_processes=100
                )
            )
        
        assert collector._detect_cpu_saturation() is True
    
    def test_detect_memory_pressure(self):
        """Testa detecção de pressão de memória"""
        collector = MetricsCollector()
        
        # Simula memória alta (>90%)
        collector.system_snapshots.append(
            SystemMetrics(
                timestamp=time.time(),
                cpu_percent=50.0,
                memory_mb=8000.0,
                memory_percent=92.0,
                disk_io_read_mb=100.0,
                disk_io_write_mb=50.0,
                num_processes=100
            )
        )
        
        assert collector._detect_memory_pressure() is True


class TestReportGenerator:
    """Testes para ReportGenerator"""
    
    def test_to_console_output(self, capsys):
        """Testa saída formatada no console"""
        analysis = LoadTestAnalysis(
            scenario_name="Test Scenario",
            total_operations=100,
            successful_operations=95,
            failed_operations=5,
            error_rate=0.05,
            throughput_ops_per_sec=50.0,
            throughput_mb_per_sec=100.0,
            latency_min=0.01,
            latency_max=0.5,
            latency_mean=0.1,
            latency_p50=0.09,
            latency_p95=0.3,
            latency_p99=0.4,
            cpu_percent_avg=70.0,
            cpu_percent_peak=85.0,
            memory_mb_avg=2000.0,
            memory_mb_peak=2500.0,
            disk_io_mb_per_sec_avg=50.0,
            test_duration=10.0
        )
        
        ReportGenerator.to_console(analysis, show_details=False)
        
        captured = capsys.readouterr()
        assert "LOAD TEST RESULTS" in captured.out
        assert "Test Scenario" in captured.out
        assert "100" in captured.out  # total operations
    
    def test_to_json_creates_file(self, tmp_path):
        """Testa criação de arquivo JSON"""
        analysis = LoadTestAnalysis(
            scenario_name="Test",
            total_operations=10,
            successful_operations=10,
            failed_operations=0,
            error_rate=0.0,
            throughput_ops_per_sec=50.0,
            throughput_mb_per_sec=100.0,
            latency_min=0.01,
            latency_max=0.1,
            latency_mean=0.05,
            latency_p50=0.05,
            latency_p95=0.08,
            latency_p99=0.09,
            cpu_percent_avg=50.0,
            cpu_percent_peak=60.0,
            memory_mb_avg=1000.0,
            memory_mb_peak=1200.0,
            disk_io_mb_per_sec_avg=30.0,
            test_duration=5.0
        )
        
        output_path = tmp_path / "test_results.json"
        ReportGenerator.to_json(analysis, output_path)
        
        assert output_path.exists()
        
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        assert "version" in data
        assert "analysis" in data
        assert data["analysis"]["scenario_name"] == "Test"
    
    def test_to_summary_format(self):
        """Testa geração de sumário de uma linha"""
        analysis = LoadTestAnalysis(
            scenario_name="Test",
            total_operations=10,
            successful_operations=10,
            failed_operations=0,
            error_rate=0.0,
            throughput_ops_per_sec=50.0,
            throughput_mb_per_sec=100.0,
            latency_min=0.01,
            latency_max=0.1,
            latency_mean=0.05,
            latency_p50=0.05,
            latency_p95=0.08,
            latency_p99=0.09,
            cpu_percent_avg=50.0,
            cpu_percent_peak=60.0,
            memory_mb_avg=1000.0,
            memory_mb_peak=1200.0,
            disk_io_mb_per_sec_avg=30.0,
            test_duration=5.0
        )
        
        summary = ReportGenerator.to_summary(analysis)
        
        assert "Test" in summary
        assert "50.0 ops/s" in summary
        assert "p95=" in summary
        assert "CPU=" in summary


class TestScenarios:
    """Testes para Scenarios"""
    
    def test_generate_test_corpus_creates_files(self, tmp_path):
        """Testa geração de corpus de arquivos"""
        files = Scenarios.generate_test_corpus(
            size_mb=0.5,  # 500KB total
            num_files=5,
            output_dir=tmp_path
        )
        
        assert len(files) <= 5  # Pode ser menos se atingir target antes
        assert all(f.exists() for f in files)
        assert all(f.suffix == ".json" for f in files)
        
        # Verifica que são JSONs válidos
        for file in files:
            with open(file, 'r') as f:
                data = json.load(f)
            assert "items" in data
            assert "count" in data
    
    def test_generate_json_content_structure(self):
        """Testa estrutura do JSON gerado"""
        data = Scenarios._generate_json_content(target_size_kb=10)
        
        assert "version" in data
        assert "items" in data
        assert "count" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0
        
        # Verifica estrutura de um item
        item = data["items"][0]
        assert "id" in item
        assert "name" in item
        assert "value" in item
        assert "category" in item
        assert "tags" in item
        assert "metadata" in item
    
    def test_batch_processing_scenario_executes(self):
        """Testa execução do cenário batch processing"""
        # Usa apenas 5 files para teste rápido
        results = Scenarios.batch_file_processing(num_files=5)
        
        assert len(results) == 5
        
        for success, duration, size_mb in results:
            assert isinstance(success, bool)
            assert isinstance(duration, float)
            assert isinstance(size_mb, float)
            assert duration >= 0
            assert size_mb > 0
    
    def test_set_operations_scenario_executes(self):
        """Testa execução do cenário set operations"""
        # Usa apenas 3 files para teste rápido
        results = Scenarios.set_operations_stress(num_files=3, operation="union")
        
        assert len(results) == 1  # Retorna 1 resultado (operação única)
        
        success, duration, size_mb = results[0]
        assert isinstance(success, bool)
        assert isinstance(duration, float)
        assert isinstance(size_mb, float)


class TestLoadRunner:
    """Testes para LoadRunner (básicos, sem execução completa)"""
    
    def test_load_config_creation(self):
        """Testa criação de configuração"""
        config = LoadConfig(
            num_workers=8,
            warmup_duration=5.0,
            rampup_duration=10.0,
            sustain_duration=30.0,
            cooldown_duration=5.0
        )
        
        assert config.num_workers == 8
        assert config.warmup_duration == 5.0
        assert config.rampup_duration == 10.0
        assert config.sustain_duration == 30.0
        assert config.cooldown_duration == 5.0
    
    def test_load_runner_initialization(self):
        """Testa inicialização do LoadRunner"""
        config = LoadConfig(num_workers=2)
        runner = LoadRunner(config)
        
        assert runner.config == config
        assert runner.workers == []
        assert runner.task_queue is None
        assert runner.metrics_collector is None
    
    def test_worker_creation(self):
        """Testa criação de Worker process"""
        task_queue = multiprocessing.Queue()
        metrics_queue = multiprocessing.Queue()
        stop_event = multiprocessing.Event()
        
        worker = Worker(
            worker_id=0,
            task_queue=task_queue,
            metrics_queue=metrics_queue,
            stop_event=stop_event
        )
        
        assert worker.worker_id == 0
        assert worker.task_queue == task_queue
        assert worker.metrics_queue == metrics_queue
        assert worker.stop_event == stop_event


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
