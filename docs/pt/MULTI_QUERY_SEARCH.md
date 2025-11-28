# Multi-Query Search (v2.8.0)

## Visão Geral

A funcionalidade de Multi-Query Search permite buscar por múltiplos padrões simultaneamente no Clarify. Cada linha do campo de busca representa uma query independente que é executada em paralelo.

## Como Usar

### Ativando o Modo Multi-Query

1. Na aba **Search/Replace**, localize o campo de busca
2. Marque a checkbox **"Multi-line"**
3. O campo de busca se transformará em uma área de texto multi-linha

### Sintaxe de Queries

Cada linha representa uma busca independente:

```
erro
warning
INFO
DEBUG
```

#### Comentários

Linhas começando com `#` são ignoradas:

```
# Buscar por logs de erro
error
critical
# warning - desabilitado temporariamente
```

#### Linhas Vazias

Linhas vazias são automaticamente ignoradas:

```
error


warning
```

### Usando Regex

Quando a opção **"Regex"** está marcada, cada linha pode conter uma expressão regular:

```
erro\d+
warning:\s+\w+
(ERROR|FATAL):\s+.*
\b[A-Z]{3,}\b
```

### Opções Adicionais

As opções de busca se aplicam a **todas** as queries:

- **Case Sensitive**: Todas as queries serão case-sensitive
- **Whole Word**: Todas as queries buscarão palavras inteiras
- **Regex**: Todas as queries serão tratadas como regex

## Exemplos Práticos

### Exemplo 1: Buscar Diferentes Níveis de Log

```
ERROR
WARNING
CRITICAL
FATAL
```

Encontrará todas as ocorrências desses níveis de log nos arquivos.

### Exemplo 2: Buscar Padrões Específicos com Regex

```
# Erros numerados
error-\d{3,}
# Warnings com contexto
warning:.*database
# Exceptions Java
Exception in thread
```

### Exemplo 3: Buscar Múltiplas Variáveis

```
user_id
username
user_email
user_name
userId
```

### Exemplo 4: Buscar Padrões de Data

```
\d{4}-\d{2}-\d{2}
\d{2}/\d{2}/\d{4}
\d{8}
```

## Limitações

1. **Máximo de caracteres por query**: 500 caracteres
2. **Deduplicação**: Se múltiplas queries encontrarem a mesma posição, apenas um match será retornado
3. **Performance**: Quanto mais queries, mais tempo levará a busca

## Comparação com Busca Single-Query

### Single-Query (Tradicional)
```
error|warning|info
```
- Usa uma única regex com alternation (`|`)
- Rápido para poucos padrões
- Difícil de manter com muitos padrões

### Multi-Query (v2.8.0)
```
error
warning
info
```
- Múltiplas queries independentes
- Fácil de adicionar/remover padrões
- Suporte a comentários
- Melhor organização

## Casos de Uso

### 1. Auditoria de Código

Buscar múltiplos padrões problemáticos:
```
# Código problemático
TODO
FIXME
XXX
HACK
# APIs deprecadas
deprecated_function
old_api_call
```

### 2. Análise de Logs

Buscar múltiplos níveis de severidade:
```
CRITICAL
ERROR
WARNING
# INFO - desabilitado para reduzir ruído
```

### 3. Busca de Configurações

Encontrar múltiplas configurações:
```
database_url
api_key
secret_key
password
token
```

### 4. Busca de Imports

Encontrar múltiplos imports em Python:
```
import os
import sys
from pathlib import Path
from typing import
```

## Performance

### Recomendações

1. **Use poucas queries quando possível** (1-10 é ideal)
2. **Desabilite regex se não precisar** (busca literal é mais rápida)
3. **Use whole-word quando apropriado** (reduz falsos positivos)
4. **Adicione comentários** para documentar suas queries

### Benchmarks Aproximados

| Queries | Arquivos | Tempo Aproximado |
|---------|----------|------------------|
| 1       | 1000     | ~2s              |
| 5       | 1000     | ~5s              |
| 10      | 1000     | ~10s             |
| 20      | 1000     | ~20s             |

*Nota: Tempos variam com tamanho dos arquivos e complexidade das regex*

## Troubleshooting

### Nenhum Resultado Encontrado

1. Verifique se há queries válidas (não apenas comentários)
2. Verifique se as opções Case/Word/Regex estão corretas
3. Teste cada query individualmente no modo single-query

### Query Muito Longa

Se receber erro "Query on line X is too long":
- Divida a query em múltiplas linhas
- Simplifique a expressão regular
- Limite: 500 caracteres por linha

### Resultados Duplicados

Se vir o mesmo resultado múltiplas vezes:
- É esperado quando múltiplas queries fazem match na mesma posição
- O sistema automaticamente deduplica baseado em (linha, coluna)

## Integração com Outras Features

### Replace com Multi-Query

⚠️ **Atenção**: Replace substitui **todas** as ocorrências encontradas por **todas** as queries pelo mesmo texto de substituição.

Exemplo:
```
Queries:
  error
  warning

Replace com: "LOG"

Resultado:
  "error occurred" → "LOG occurred"
  "warning here" → "LOG here"
```

### Filtros e Escopo

Multi-query funciona normalmente com:
- File filters (`*.py`, `*.txt`)
- Scope (replace within selection)
- Conditions (line number, file size, etc.)

## Ver Também

- [Search & Replace Guide](./SEARCH_REPLACE.md)
- [Regex Patterns](./REGEX_PATTERNS.md)
- [Performance Tips](./PERFORMANCE.md)
