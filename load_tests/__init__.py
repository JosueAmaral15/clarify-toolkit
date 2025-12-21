"""
Load Testing System for Clarify

Sistema automatizado de testes de carga para identificar limites de performance
e gargalos em cenários de uso intensivo.

Complementa o sistema de benchmarks (v2.9.81) com testes de stress em
operações paralelas usando multiprocessing.

Author: Josué Amaral
Date: 21/12/2024
Version: 1.0.0
"""

__version__ = "1.0.0"

from .load_runner import LoadRunner, LoadConfig
from .scenarios import Scenarios
from .metrics_collector import MetricsCollector, SystemMetrics, OperationMetrics
from .report_generator import ReportGenerator

__all__ = [
    "LoadRunner",
    "LoadConfig",
    "Scenarios",
    "MetricsCollector",
    "SystemMetrics",
    "OperationMetrics",
    "ReportGenerator"
]
