# Clarify Performance Benchmarks 🚀

Sistema de benchmarking automatizado para medir performance das operações principais do Clarify.

## 📊 O que é medido?

- **Tempo de execução** (segundos)
- **Uso de memória** (MB)
- **CPU** (%)

## 🎯 Operações Benchmarked

### 1. Converters (TOON/BSON)
- JSON → TOON conversion
- JSON → BSON → JSON roundtrip
- Diferentes tamanhos: 1MB, 5MB, 10MB

### 2. Set Operations
- Union de JSONs
- Intersection
- Difference
- Symmetric difference

### 3. JSON Rewriter
- Add keys
- Remove keys
- Rename keys
- Transformações complexas

### 4. JSON Search
- Flatten objects
- Project indexing
- Search operations

### 5. Text Extractor
- HTML parsing
- JSX extraction
- Generic extraction

## 🚀 Uso

### Executar todos os benchmarks

```bash
python -m benchmarks
```

### Executar com tamanhos customizados

```bash
python -m benchmarks --sizes 1,5,10
```

### Executar operações específicas

```bash
# Apenas converters
python -m benchmarks --operations converter

# Apenas set operations
python -m benchmarks --operations set

# Múltiplas operações
python -m benchmarks --operations converter,set
```

### Ajustar número de runs

```bash
# 5 runs por benchmark (mais preciso, mais lento)
python -m benchmarks --runs 5

# Sem warmup (mais rápido, menos preciso)
python -m benchmarks --no-warmup
```

### Salvar resultados em arquivo customizado

```bash
python -m benchmarks --output results/benchmark_$(date +%Y%m%d).json
```

## 📈 Interpretando Resultados

### Exemplo de output:

```
🏁 Clarify Performance Benchmarks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Platform: Linux-6.8.0-49-generic-x86_64
Python: 3.12.4
Date: 2025-12-25 14:30:00

Running benchmarks...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ json_to_toon_1MB          0.125s  12.3MB  45%
✓ set_union_5MB             0.450s  28.7MB  72%
✓ rewriter_add_keys_1MB     0.089s   8.9MB  38%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Results saved to: benchmarks/results.json
```

### Métricas:

- **< 0.1s**: Excelente ⚡
- **0.1s - 0.5s**: Bom ✅
- **0.5s - 1.0s**: Aceitável ⚠️
- **> 1.0s**: Lento 🐌

### Uso de memória:

- **< 10MB**: Baixo 🟢
- **10-50MB**: Moderado 🟡
- **> 50MB**: Alto 🔴

## 🔧 Arquitetura

```
benchmarks/
├── __init__.py              # Package marker
├── __main__.py              # Entry point (python -m benchmarks)
├── benchmark_runner.py      # Core engine (metrics collection)
├── generators.py            # Test data generators
├── run.py                   # CLI interface
└── results.json            # Latest results
```

### Componentes:

#### 1. BenchmarkRunner
Engine principal que:
- Registra benchmarks
- Executa múltiplas runs
- Coleta métricas (time, memory, CPU)
- Faz warmup opcional
- Calcula médias

#### 2. Generators
Funções para gerar dados de teste:
- `generate_json_data(size_mb)` - JSON aleatório com tamanho específico
- `generate_nested_json(depth)` - JSON aninhado
- `generate_array_with_duplicates(size)` - Arrays com duplicatas
- `generate_html_content(size_kb)` - HTML para extração

#### 3. CLI Runner
Interface de linha de comando com:
- Seleção de operações
- Configuração de tamanhos
- Controle de runs
- Export de resultados

## 📦 Adicionando Novos Benchmarks

### Exemplo simples:

```python
from benchmarks.benchmark_runner import BenchmarkRunner
from benchmarks.generators import generate_json_data

runner = BenchmarkRunner(num_runs=3)

# Registrar benchmark
runner.register(
    name="my_operation_1MB",
    func=my_function,
    args=(data,),
    size_label="1MB"
)

# Executar
runner.run_all()
results = runner.get_results()
```

### Exemplo complexo com setup:

```python
def setup_my_benchmarks(runner: BenchmarkRunner, sizes: List[float]):
    """Register custom benchmarks."""
    for size_mb in sizes:
        data = generate_json_data(size_mb)
        
        runner.register(
            name=f"my_operation_{int(size_mb)}MB",
            func=my_complex_operation,
            args=(data,),
            kwargs={'option': True},
            size_label=f"{size_mb}MB"
        )
```

### Adicionar ao run.py:

```python
# Em run.py, função main()
if args.operations in ['all', 'my_operation']:
    setup_my_benchmarks(runner, sizes)
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow

Benchmarks são executados automaticamente:
- **Push em main**: Benchmarks rápidos (1MB)
- **Semanalmente**: Benchmarks completos (1MB, 5MB, 10MB)
- **Pull Requests**: Comparação de performance

### Workflow file: `.github/workflows/benchmarks.yml`

```yaml
name: Performance Benchmarks

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * 0'  # Domingo às 2am
  workflow_dispatch:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e .
      - run: python -m benchmarks --sizes 1,5
      - uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: benchmarks/results.json
```

## 📊 Tracking Performance Over Time

### Salvar resultados históricos:

```bash
# Criar diretório para histórico
mkdir -p benchmarks/history

# Executar e salvar com timestamp
python -m benchmarks --output benchmarks/history/results_$(date +%Y%m%d_%H%M%S).json
```

### Comparar resultados:

```python
import json

# Carregar dois resultados
with open('benchmarks/history/results_20251220.json') as f:
    old = json.load(f)
    
with open('benchmarks/results.json') as f:
    new = json.load(f)

# Comparar tempos
for benchmark in new['results']:
    name = benchmark['name']
    old_time = next(b['avg_time'] for b in old['results'] if b['name'] == name)
    new_time = benchmark['avg_time']
    
    diff = ((new_time - old_time) / old_time) * 100
    print(f"{name}: {diff:+.1f}%")
```

## 🎯 Best Practices

### 1. Run Multiple Times
```bash
# 5 runs para mais precisão
python -m benchmarks --runs 5
```

### 2. Warmup é Importante
- Primeira execução sempre é mais lenta (cache, JIT)
- Sempre faça warmup (padrão está ativado)

### 3. Isolar Ambiente
```bash
# Fechar outros programas
# Executar em máquina dedicada para CI/CD
# Evitar executar durante uso pesado do sistema
```

### 4. Tamanhos Representativos
- **1MB**: Arquivos pequenos típicos
- **5MB**: Arquivos médios
- **10MB**: Arquivos grandes

### 5. Monitorar Regressões
```bash
# Definir thresholds
# Alertar se performance cair > 10%
# Bloquear PRs com regressões significativas
```

## 🐛 Troubleshooting

### "Module not found" errors

```bash
# Instalar Clarify em modo dev
pip install -e .

# Ou adicionar ao PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH
```

### Benchmarks muito lentos

```bash
# Reduzir tamanhos
python -m benchmarks --sizes 0.5,1

# Reduzir runs
python -m benchmarks --runs 1 --no-warmup
```

### Resultados inconsistentes

```bash
# Aumentar runs
python -m benchmarks --runs 10

# Verificar se há processos concorrentes
htop  # ou top
```

## 📚 Recursos Adicionais

### Dependências:
- `psutil` - Métricas de CPU/memória
- `tracemalloc` - Rastreamento de memória Python

### Documentação relacionada:
- [PERFORMANCE.md](../docs/PERFORMANCE.md) - Guia de otimização
- [TESTING.md](../docs/TESTING.md) - Guia de testes
- [CI_CD_SETUP.md](../docs/CI_CD_SETUP.md) - Setup de CI/CD

## 📝 Changelog

### v2.9.115 (Sprint 3 - 2025-12-25)
- ✅ README.md completo com documentação
- ✅ GitHub Actions workflow para CI/CD
- ✅ Cenários específicos para features principais
- ✅ Integração completa com sistema de testes

### v2.9.83 (2024-12-21)
- Sistema de benchmarking inicial
- Support para converters, set ops, rewriter
- CLI interface com argparse

### v2.9.81 (2024-12-21)
- BenchmarkRunner engine
- Generators para test data
- Métricas de time/memory/CPU

## 🤝 Contribuindo

Para adicionar novos benchmarks:

1. Criar gerador em `generators.py` (se necessário)
2. Adicionar setup function em `run.py`
3. Registrar na função `main()`
4. Testar: `python -m benchmarks --operations my_operation`
5. Documentar neste README

## 📄 Licença

Same as Clarify project license.
