"""
Test Runner Monitorado (Protocolo Simplicidade 1 v1.6 - Etapa 9.2)

Executa testes em processo separado com:
- Logging em tempo real
- Controle de timeout global + individual
- Cancelamento manual (Ctrl+C)
- Estatísticas em tempo real

Uso:
    python tests/test_runner_monitored.py tests/test_advanced_file_search.py

Autor: Josué Amaral
Data: 01/12/2025
"""

import multiprocessing as mp
import time
import sys
import os
from queue import Empty
from typing import Dict, Any


def run_tests_in_process(test_module: str, queue: mp.Queue, timeout: int = 30):
    """
    Executa testes em processo separado com logging para queue.
    
    Args:
        test_module: Módulo de teste (ex: 'tests/test_file_list_dock.py')
        queue: Queue para comunicação de progresso
        timeout: Timeout individual por teste em segundos
    """
    try:
        # Configurar ambiente headless para testes GUI
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        import pytest
        
        queue.put({'type': 'info', 'msg': f'🚀 Iniciando testes: {test_module}'})
        queue.put({'type': 'info', 'msg': f'⏱️  Timeout individual: {timeout}s por teste'})
        queue.put({'type': 'info', 'msg': f'🖥️  Ambiente: QT_QPA_PLATFORM=offscreen'})
        queue.put({'type': 'info', 'msg': ''})
        
        # Capturar resultados via pytest hooks
        class QueueReporter:
            def __init__(self, queue):
                self.queue = queue
                self.test_count = 0
            
            def pytest_runtest_logreport(self, report):
                """Hook para capturar resultados de cada teste."""
                if report.when == 'call':
                    self.test_count += 1
                    status = '✅ PASS' if report.passed else '❌ FAIL'
                    self.queue.put({
                        'type': 'test_result',
                        'test': report.nodeid,
                        'status': status,
                        'duration': report.duration,
                        'count': self.test_count
                    })
                    
                    # Reportar warnings
                    if hasattr(report, 'warnings') and report.warnings:
                        for warning in report.warnings:
                            self.queue.put({
                                'type': 'warning',
                                'msg': str(warning.message)
                            })
            
            def pytest_runtest_logstart(self, nodeid, location):
                """Hook para indicar início de teste."""
                self.queue.put({
                    'type': 'test_start',
                    'test': nodeid
                })
        
        # Registrar plugin
        reporter = QueueReporter(queue)
        
        # Executar pytest
        result = pytest.main([
            test_module,
            '-v',
            f'--timeout={timeout}',
            '--tb=short',
            '-p', 'no:cacheprovider',  # Desabilitar cache
            '--color=no',  # Desabilitar cores (queue é texto)
            '-W', 'ignore::DeprecationWarning'  # Ignorar deprecation warnings
        ], plugins=[reporter])
        
        queue.put({'type': 'info', 'msg': f'\n✅ Testes finalizados. Exit code: {result}'})
        queue.put({'type': 'exit', 'code': result})
        
    except Exception as e:
        queue.put({'type': 'error', 'msg': f'Erro fatal: {str(e)}'})
        import traceback
        queue.put({'type': 'error', 'msg': traceback.format_exc()})
        queue.put({'type': 'exit', 'code': 1})


def monitor_test_execution(test_module: str, max_timeout: int = 300, verbose: bool = True) -> Dict[str, Any]:
    """
    Monitora execução de testes com controle total.
    
    Args:
        test_module: Módulo de teste (caminho relativo ou absoluto)
        max_timeout: Timeout máximo global em segundos (padrão: 5 min)
        verbose: Mostrar output detalhado
    
    Returns:
        dict: Resultado da execução com estatísticas
            {
                'status': 'completed'|'timeout'|'cancelled'|'error',
                'exit_code': int (0 = sucesso),
                'elapsed': float (tempo em segundos),
                'results': {
                    'passed': int,
                    'failed': int,
                    'tests': list[dict]
                }
            }
    """
    queue = mp.Queue()
    process = mp.Process(
        target=run_tests_in_process,
        args=(test_module, queue, 30)
    )
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"🧪 TEST RUNNER MONITORADO (Protocolo Simplicidade 1 v1.6)")
        print(f"{'='*70}")
        print(f"📁 Módulo: {test_module}")
        print(f"⏱️  Timeout global: {max_timeout}s ({max_timeout/60:.1f} min)")
        print(f"🛡️  Proteções: Ctrl+C para cancelar | Timeout automático")
        print(f"{'='*70}\n")
    
    process.start()
    start_time = time.time()
    results = {'passed': 0, 'failed': 0, 'tests': []}
    last_progress_time = start_time
    
    try:
        while process.is_alive():
            elapsed = time.time() - start_time
            
            # Verificar timeout global
            if elapsed > max_timeout:
                if verbose:
                    print(f"\n⚠️  TIMEOUT GLOBAL: {max_timeout}s excedidos")
                    print(f"🛑 Terminando processo de testes...")
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    if verbose:
                        print(f"⚠️  Processo não respondeu, forçando kill...")
                    process.kill()
                    process.join(timeout=2)
                return {
                    'status': 'timeout',
                    'exit_code': 124,  # Código padrão de timeout
                    'elapsed': elapsed,
                    'results': results
                }
            
            # Ler mensagens da queue (não-bloqueante)
            try:
                msg = queue.get(timeout=0.5)
                
                if msg['type'] == 'test_start':
                    if verbose:
                        test_name = msg['test'].split('::')[-1]
                        print(f"  ⏳ Executando: {test_name}...", end='', flush=True)
                
                elif msg['type'] == 'test_result':
                    if verbose:
                        print(f"\r  {msg['status']} {msg['test'].split('::')[-1]} ({msg['duration']:.2f}s)")
                    results['tests'].append(msg)
                    if '✅' in msg['status']:
                        results['passed'] += 1
                    else:
                        results['failed'] += 1
                
                elif msg['type'] == 'info':
                    if verbose and msg['msg']:
                        print(msg['msg'])
                
                elif msg['type'] == 'warning':
                    if verbose:
                        print(f"  ⚠️  Warning: {msg['msg']}")
                
                elif msg['type'] == 'error':
                    if verbose:
                        print(f"  ❌ ERRO: {msg['msg']}")
                
                elif msg['type'] == 'exit':
                    process.join(timeout=2)
                    elapsed = time.time() - start_time
                    if verbose:
                        print(f"\n{'='*70}")
                        print(f"✅ Testes finalizados em {elapsed:.2f}s")
                        print(f"{'='*70}")
                    return {
                        'status': 'completed',
                        'exit_code': msg['code'],
                        'elapsed': elapsed,
                        'results': results
                    }
            
            except Empty:
                # Nenhuma mensagem, continuar monitorando
                pass
            
            # Mostrar progresso a cada 15s
            if verbose and elapsed - last_progress_time >= 15:
                print(f"\n⏳ Progresso: {int(elapsed)}s | ✅ {results['passed']} passed | ❌ {results['failed']} failed\n")
                last_progress_time = elapsed
    
    except KeyboardInterrupt:
        if verbose:
            print(f"\n\n⚠️  CANCELAMENTO MANUAL (Ctrl+C)")
            print(f"🛑 Terminando processo de testes...")
        process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            if verbose:
                print(f"⚠️  Processo não respondeu, forçando kill...")
            process.kill()
            process.join(timeout=2)
        elapsed = time.time() - start_time
        return {
            'status': 'cancelled',
            'exit_code': 130,  # Código padrão de SIGINT
            'elapsed': elapsed,
            'results': results
        }
    
    finally:
        # Garantir cleanup
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
            if process.is_alive():
                process.kill()


def main():
    """Ponto de entrada CLI."""
    if len(sys.argv) < 2:
        print("Uso: python test_runner_monitored.py <test_module> [timeout]")
        print("Exemplo: python test_runner_monitored.py tests/test_advanced_file_search.py 300")
        sys.exit(1)
    
    test_module = sys.argv[1]
    max_timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    
    # Verificar se arquivo existe
    if not os.path.exists(test_module):
        print(f"❌ Erro: Arquivo não encontrado: {test_module}")
        sys.exit(1)
    
    # Executar testes
    result = monitor_test_execution(test_module, max_timeout=max_timeout)
    
    # Resumo final
    print(f"\n{'='*70}")
    print(f"📊 RESUMO DA EXECUÇÃO")
    print(f"{'='*70}")
    print(f"Status: {result['status'].upper()}")
    print(f"Tempo total: {result['elapsed']:.2f}s ({result['elapsed']/60:.1f} min)")
    print(f"Exit code: {result['exit_code']}")
    print(f"")
    print(f"✅ Testes passados: {result['results']['passed']}")
    print(f"❌ Testes falhados: {result['results']['failed']}")
    print(f"📝 Total de testes: {len(result['results']['tests'])}")
    
    if result['results']['tests']:
        print(f"\n🔝 Testes mais lentos:")
        sorted_tests = sorted(result['results']['tests'], key=lambda x: x['duration'], reverse=True)[:5]
        for i, test in enumerate(sorted_tests, 1):
            test_name = test['test'].split('::')[-1]
            print(f"  {i}. {test_name}: {test['duration']:.2f}s")
    
    print(f"{'='*70}\n")
    
    # Exit code correto
    sys.exit(result['exit_code'])


if __name__ == '__main__':
    main()
