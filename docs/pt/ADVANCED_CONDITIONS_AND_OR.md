# Operadores AND/OR em Condições Avançadas

## Visão Geral

O Clarify suporta operadores lógicos **AND** e **OR** para combinar múltiplas condições avançadas, permitindo filtros mais flexíveis e poderosos.

## Funcionalidade

### Operador AND (Conjunção)
- **Comportamento**: Todas as condições devem corresponder
- **Uso**: Quando você quer arquivos que atendem TODOS os critérios simultaneamente
- **Padrão**: AND é o operador padrão se nenhum for especificado
- **Lógica**: `condition1 AND condition2 AND condition3` = todas verdadeiras

### Operador OR (Disjunção)
- **Comportamento**: Pelo menos uma condição deve corresponder
- **Uso**: Quando você quer arquivos que atendem QUALQUER critério
- **Lógica**: `condition1 OR condition2 OR condition3` = pelo menos uma verdadeira

## Interface do Usuário

### Localização
O seletor de operador lógico está localizado no topo da seção de Condições Avançadas:

```
┌─────────────────────────────────────────────────────────┐
│ Logic: [AND ▼]  ← Dropdown para selecionar operador     │
├─────────────────────────────────────────────────────────┤
│ Field    │ Operator │ Value │ Scope │ Case │ Word │ ... │
│ filename │ contains │ test  │ none  │  ☑   │  ☐   │ ... │
│ ext      │ equals   │ py    │ none  │  ☑   │  ☐   │ ... │
└─────────────────────────────────────────────────────────┘
```

### Tooltip
Ao passar o mouse sobre o dropdown:
```
AND: All conditions must match
OR: At least one condition must match
```

## Exemplos Práticos

### Exemplo 1: AND - Todos os critérios
**Objetivo**: Encontrar arquivos Python de teste

**Configuração**:
```
Logic: AND
- filename contains "test"
- ext equals "py"
```

**Resultado**: Somente arquivos que:
- Têm "test" no nome **E**
- São arquivos `.py`

**Arquivos correspondentes**:
- ✅ `test_utils.py` (contém "test" E é .py)
- ✅ `test_models.py` (contém "test" E é .py)
- ❌ `utils.py` (é .py mas NÃO contém "test")
- ❌ `test_data.json` (contém "test" mas NÃO é .py)

### Exemplo 2: OR - Qualquer critério
**Objetivo**: Encontrar arquivos Python OU arquivos de teste

**Configuração**:
```
Logic: OR
- filename contains "test"
- ext equals "py"
```

**Resultado**: Arquivos que:
- Têm "test" no nome **OU**
- São arquivos `.py` **OU**
- Ambos

**Arquivos correspondentes**:
- ✅ `test_utils.py` (contém "test" E é .py)
- ✅ `utils.py` (é .py)
- ✅ `test_data.json` (contém "test")
- ✅ `main.py` (é .py)
- ❌ `data.json` (nem .py nem contém "test")

### Exemplo 3: AND com conteúdo
**Objetivo**: Arquivos Python que importam específico módulo

**Configuração**:
```
Logic: AND
- ext equals "py"
- content contains "import numpy"
- filename not_contains "test"
```

**Resultado**: Arquivos que:
- São `.py` **E**
- Contêm "import numpy" **E**
- NÃO têm "test" no nome

### Exemplo 4: OR para múltiplas extensões
**Objetivo**: Encontrar todos arquivos de imagem

**Configuração**:
```
Logic: OR
- ext equals "png"
- ext equals "jpg"
- ext equals "gif"
```

**Resultado**: Qualquer arquivo com extensão .png, .jpg ou .gif

## Tabela Verdade

### AND (Conjunção)
| Condição 1 | Condição 2 | Resultado |
|------------|------------|-----------|
| ✅ Match   | ✅ Match   | ✅ INCLUDE |
| ✅ Match   | ❌ No Match | ❌ EXCLUDE |
| ❌ No Match | ✅ Match   | ❌ EXCLUDE |
| ❌ No Match | ❌ No Match | ❌ EXCLUDE |

### OR (Disjunção)
| Condição 1 | Condição 2 | Resultado |
|------------|------------|-----------|
| ✅ Match   | ✅ Match   | ✅ INCLUDE |
| ✅ Match   | ❌ No Match | ✅ INCLUDE |
| ❌ No Match | ✅ Match   | ✅ INCLUDE |
| ❌ No Match | ❌ No Match | ❌ EXCLUDE |

## Combinação com Checkboxes

Os operadores AND/OR funcionam perfeitamente com as opções de checkbox:

**Exemplo**: Busca case-sensitive com múltiplas condições
```
Logic: AND
- filename contains "Test" [Case: ☑] [Word: ☐] [Regex: ☐]
- ext equals "py" [Case: ☑] [Word: ☐] [Regex: ☐]
- content contains "class.*Test" [Case: ☐] [Word: ☐] [Regex: ☑]
```

## Implementação Técnica

### Backend (filters.py)
```python
def filter_files_by_conditions(
    files: Iterable[str], 
    conds: Sequence[Condition], 
    logic_operator: str = "AND"
) -> List[str]:
    if logic_operator == "OR":
        # Disjunção: pelo menos uma condição deve corresponder
        ok = any(c.matches(p) for c in conds)
    else:
        # Conjunção: todas as condições devem corresponder (padrão)
        ok = all(c.matches(p) for c in conds)
```

### Frontend (app.py)
```python
# Criação do dropdown
self.combo_logic_op = QComboBox()
self.combo_logic_op.addItems(["AND", "OR"])
self.combo_logic_op.setToolTip("AND: All conditions must match\nOR: At least one condition must match")

# Conexão para atualização ao vivo (Insert Panel)
self.combo_logic_op.currentTextChanged.connect(self._schedule_live_refresh)

# Obtenção do operador selecionado
def _conds(self) -> tuple[List[Condition], str]:
    # ... coleta condições ...
    logic_op = self.combo_logic_op.currentText()
    return out, logic_op

# Aplicação do filtro
conds, logic_op = self._conds()
filtered = filter_files_by_conditions(files, conds, logic_op)
```

## Casos de Uso

### 1. Desenvolvimento Web
**Encontrar todos os componentes React ou Vue**:
```
Logic: OR
- filename contains "Component"
- filename contains "View"
- ext equals "jsx"
- ext equals "vue"
```

### 2. Análise de Dados
**Scripts Python que usam pandas mas não são testes**:
```
Logic: AND
- ext equals "py"
- content contains "import pandas"
- filename not_contains "test"
```

### 3. Documentação
**Documentos em português ou inglês**:
```
Logic: OR
- filename contains "pt-br"
- filename contains "en-us"
- filename contains "README"
```

### 4. Build System
**Arquivos de configuração críticos**:
```
Logic: OR
- filename equals "package.json"
- filename equals "tsconfig.json"
- filename equals "pyproject.toml"
- filename equals "Dockerfile"
```

## Testes

O recurso foi validado com 10 testes abrangentes:

1. ✅ `test_and_operator_all_match` - AND com todas condições correspondendo
2. ✅ `test_and_operator_one_fails` - AND com uma condição falhando
3. ✅ `test_or_operator_one_matches` - OR com uma condição correspondendo
4. ✅ `test_or_operator_all_match` - OR com todas condições correspondendo
5. ✅ `test_or_operator_none_match` - OR com nenhuma condição correspondendo
6. ✅ `test_multiple_files_and_operator` - AND com múltiplos arquivos
7. ✅ `test_multiple_files_or_operator` - OR com múltiplos arquivos
8. ✅ `test_default_operator_is_and` - Operador padrão é AND
9. ✅ `test_with_content_condition_and` - AND com condição de conteúdo
10. ✅ `test_with_content_condition_or` - OR com condição de conteúdo

## Disponibilidade

✅ **Search/Replace Panel**: Sim  
✅ **Insert Panel**: Sim  
✅ **Live Preview**: Sim (Insert Panel atualiza em tempo real)  
✅ **Performance**: Otimizado com avaliação curto-circuito  

## Versão

- Implementado em: v2.6.0
- Arquivo: `src/core/filters.py`, `src/app.py`
- Testes: `tests/test_and_or_operators.py`
