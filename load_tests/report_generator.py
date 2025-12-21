"""
Report Generator - Geração de relatórios de testes de carga

Formata resultados de load tests em múltiplos formatos:
- Console (tabela formatada com box drawing)
- JSON (dados completos para análise)
- Markdown (relatório executivo para docs/)

Author: Josué Amaral
Date: 21/12/2024
"""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from .metrics_collector import LoadTestAnalysis


class ReportGenerator:
    """
    Gerador de relatórios de testes de carga em múltiplos formatos.
    
    Usage:
        analysis = collector.analyze("Batch Processing")
        
        # Console output
        ReportGenerator.to_console(analysis)
        
        # Save to JSON
        ReportGenerator.to_json(analysis, Path("results/test.json"))
        
        # Generate markdown report
        ReportGenerator.to_markdown(analysis, Path("docs/PERFORMANCE.md"))
    """
    
    @staticmethod
    def to_console(analysis: LoadTestAnalysis, show_details: bool = True):
        """
        Imprime relatório formatado no console com box drawing.
        
        Args:
            analysis: Resultado da análise
            show_details: Se True, mostra detalhes completos (latências, recursos)
        """
        # Header
        print()
        print("╔════════════════════════════════════════════════════════════════╗")
        print(f"║  LOAD TEST RESULTS - Clarify v2.9.82                           ║")
        print("╠════════════════════════════════════════════════════════════════╣")
        print(f"║  Scenario: {analysis.scenario_name:<49}║")
        print("╠════════════════════════════════════════════════════════════════╣")
        
        # Sumário de operações
        print(f"║  Total Operations:     {analysis.total_operations:<7} ops                        ║")
        print(f"║  Successful:           {analysis.successful_operations:<7} ops ({analysis.successful_operations/analysis.total_operations*100:.1f}%)                   ║")
        print(f"║  Failed:               {analysis.failed_operations:<7} ops ({analysis.error_rate*100:.1f}%)                   ║")
        print(f"║  Test Duration:        {analysis.test_duration:<7.1f} seconds                    ║")
        print("║                                                                ║")
        
        # Throughput
        print(f"║  Throughput:           {analysis.throughput_ops_per_sec:<7.2f} ops/sec                    ║")
        print(f"║  Throughput (MB):      {analysis.throughput_mb_per_sec:<7.2f} MB/sec                     ║")
        
        if show_details:
            print("║                                                                ║")
            print("║  Latency Distribution:                                         ║")
            print(f"║    Min:    {analysis.latency_min*1000:>7.0f} ms                                         ║")
            print(f"║    p50:    {analysis.latency_p50*1000:>7.0f} ms                                         ║")
            print(f"║    p95:    {analysis.latency_p95*1000:>7.0f} ms                                         ║")
            print(f"║    p99:    {analysis.latency_p99*1000:>7.0f} ms                                         ║")
            print(f"║    Max:    {analysis.latency_max*1000:>7.0f} ms                                         ║")
            print(f"║    Mean:   {analysis.latency_mean*1000:>7.0f} ms                                         ║")
            print("║                                                                ║")
            
            # Recursos do sistema
            print("║  System Resources:                                             ║")
            print(f"║    CPU (avg):      {analysis.cpu_percent_avg:>6.1f}%                                   ║")
            print(f"║    CPU (peak):     {analysis.cpu_percent_peak:>6.1f}%                                   ║")
            print(f"║    RAM (avg):      {analysis.memory_mb_avg:>7.1f} MB                                 ║")
            print(f"║    RAM (peak):     {analysis.memory_mb_peak:>7.1f} MB                                 ║")
            print(f"║    Disk I/O (avg): {analysis.disk_io_mb_per_sec_avg:>7.1f} MB/s                              ║")
            print("║                                                                ║")
        
        # Detecção de gargalos
        status_emoji = "✅" if not any([
            analysis.cpu_saturation_detected,
            analysis.memory_pressure_detected,
            analysis.io_bottleneck_detected,
            analysis.thrashing_detected
        ]) else "⚠️"
        
        print(f"║  Status: {status_emoji} {'PASS' if status_emoji == '✅' else 'WARNING'}                                                  ║")
        
        bottlenecks = []
        if analysis.cpu_saturation_detected:
            bottlenecks.append("CPU Saturation")
        if analysis.memory_pressure_detected:
            bottlenecks.append("Memory Pressure")
        if analysis.io_bottleneck_detected:
            bottlenecks.append("I/O Bottleneck")
        if analysis.thrashing_detected:
            bottlenecks.append("Thrashing")
        
        if bottlenecks:
            print(f"║  Bottlenecks: {', '.join(bottlenecks):<44}║")
        else:
            print("║  Bottlenecks: None detected                                    ║")
        
        print("╚════════════════════════════════════════════════════════════════╝")
        print()
    
    @staticmethod
    def to_json(analysis: LoadTestAnalysis, output_path: Path, indent: int = 2):
        """
        Salva análise completa em formato JSON.
        
        Args:
            analysis: Resultado da análise
            output_path: Caminho do arquivo de saída
            indent: Número de espaços para indentação (default: 2)
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "version": "2.9.82",
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis.to_dict()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        print(f"✅ Relatório JSON salvo em: {output_path}")
    
    @staticmethod
    def to_markdown(
        analysis: LoadTestAnalysis,
        output_path: Path,
        append: bool = True
    ):
        """
        Gera relatório executivo em Markdown.
        
        Args:
            analysis: Resultado da análise
            output_path: Caminho do arquivo de saída (ex: docs/PERFORMANCE.md)
            append: Se True, adiciona ao arquivo existente; se False, sobrescreve
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Se arquivo existe e append=True, lê conteúdo existente
        existing_content = ""
        if append and output_path.exists():
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # Gera novo conteúdo
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        new_content = f"""
## {analysis.scenario_name} - {timestamp}

**Test Duration**: {analysis.test_duration:.1f}s  
**Version**: v2.9.82

### Summary
- **Total Operations**: {analysis.total_operations} ops
- **Successful**: {analysis.successful_operations} ops ({analysis.successful_operations/analysis.total_operations*100:.1f}%)
- **Failed**: {analysis.failed_operations} ops ({analysis.error_rate*100:.1f}%)
- **Error Rate**: {analysis.error_rate*100:.2f}%

### Throughput
- **Operations**: {analysis.throughput_ops_per_sec:.2f} ops/sec
- **Data**: {analysis.throughput_mb_per_sec:.2f} MB/sec

### Latency Distribution

| Percentile | Latency (ms) |
|------------|--------------|
| Min        | {analysis.latency_min*1000:.0f}          |
| p50        | {analysis.latency_p50*1000:.0f}          |
| p95        | {analysis.latency_p95*1000:.0f}          |
| p99        | {analysis.latency_p99*1000:.0f}          |
| Max        | {analysis.latency_max*1000:.0f}          |
| Mean       | {analysis.latency_mean*1000:.0f}          |

### System Resources

- **CPU**: {analysis.cpu_percent_avg:.1f}% (avg), {analysis.cpu_percent_peak:.1f}% (peak)
- **RAM**: {analysis.memory_mb_avg:.1f}MB (avg), {analysis.memory_mb_peak:.1f}MB (peak)
- **Disk I/O**: {analysis.disk_io_mb_per_sec_avg:.1f} MB/s (avg)

### Bottleneck Detection

"""
        
        # Adiciona status de gargalos
        bottlenecks = []
        if analysis.cpu_saturation_detected:
            bottlenecks.append("- ⚠️ **CPU Saturation**: Detected (>95% sustained)")
        if analysis.memory_pressure_detected:
            bottlenecks.append("- ⚠️ **Memory Pressure**: Detected (>90% usage)")
        if analysis.io_bottleneck_detected:
            bottlenecks.append("- ⚠️ **I/O Bottleneck**: Detected (>200MB/s sustained)")
        if analysis.thrashing_detected:
            bottlenecks.append("- ⚠️ **Thrashing**: Detected (latency 2x baseline)")
        
        if bottlenecks:
            new_content += "\n".join(bottlenecks) + "\n"
        else:
            new_content += "- ✅ **No bottlenecks detected**\n"
        
        new_content += "\n---\n"
        
        # Combina conteúdo
        if append and existing_content:
            # Adiciona novo conteúdo no topo (após o título principal)
            if existing_content.startswith("# "):
                lines = existing_content.split("\n", 1)
                final_content = lines[0] + "\n" + new_content
                if len(lines) > 1:
                    final_content += "\n" + lines[1]
            else:
                final_content = new_content + "\n" + existing_content
        else:
            # Cria novo arquivo com cabeçalho
            final_content = f"""# Clarify - Performance Report

Auto-generated load test results for Clarify system.

**Last Updated**: {timestamp}

---
{new_content}
"""
        
        # Salva arquivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✅ Relatório Markdown salvo em: {output_path}")
    
    @staticmethod
    def to_summary(analysis: LoadTestAnalysis) -> str:
        """
        Gera sumário de uma linha para logging.
        
        Args:
            analysis: Resultado da análise
            
        Returns:
            String formatada com sumário
        """
        status = "✅" if analysis.error_rate == 0 else "⚠️"
        return (
            f"{status} {analysis.scenario_name}: "
            f"{analysis.throughput_ops_per_sec:.1f} ops/s | "
            f"p95={analysis.latency_p95*1000:.0f}ms | "
            f"CPU={analysis.cpu_percent_avg:.0f}% | "
            f"RAM={analysis.memory_mb_peak:.0f}MB"
        )
