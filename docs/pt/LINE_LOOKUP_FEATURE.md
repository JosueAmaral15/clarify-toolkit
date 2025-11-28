# Line Lookup Feature - Insert Panel

**Version**: 2.3.0  
**Date**: 2025-11-24  
**Author**: Josué Amaral

---

## 📋 Visão Geral

A funcionalidade de **Line Lookup** no **Insert Panel** permite inserir texto em arquivos baseado em padrões de busca ao invés de números de linha estáticos. Isso torna a inserção dinâmica e adaptável a arquivos que mudam frequentemente.

### Problema Resolvido

**Antes (v2.2.0)**:
- Necessário saber o número exato da linha
- Inserções quebravam quando arquivo mudava
- Impossível inserir em múltiplas linhas similares

**Agora (v2.3.0)**:
- Busca padrões para encontrar linhas automaticamente
- Inserções funcionam mesmo com arquivos modificados
- Suporta inserção em múltiplas linhas de uma vez

---

## 🎯 Modos de Operação

### Modo 1: Manual (Tradicional)

Quando o campo **Search query** está **vazio**:

```
Search query: [                    ] (vazio)
Line number:  [42                  ] ← Usado
```

- Usa o número de linha do spin box
- Comportamento clássico preservado
- Ideal quando você sabe exatamente a linha

### Modo 2: Lookup (Novo)

Quando o campo **Search query** contém **texto**:

```
Search query: [def calculate        ] ← Usado para buscar
Line number:  [42                  ] (ignorado)
```

- Busca o padrão nas linhas do arquivo
- Ignora o número de linha manual
- Insere nas linhas encontradas

---

## ⚙️ Opções de Busca

### 1. Case Sensitive

**Quando Ativo** (☑):
- "Function" ≠ "function" ≠ "FUNCTION"
- Busca exata respeitando maiúsculas/minúsculas

**Quando Inativo** (☐):
- "Function" = "function" = "FUNCTION"
- Busca case-insensitive

### 2. Whole Word

**Quando Ativo** (☑):
- Usa word boundaries (`\b`)
- "test" casa com "test" mas não com "testing"

**Quando Inativo** (☐):
- Busca substring
- "test" casa com "test", "testing", "contest"

### 3. Regex

**Quando Ativo** (☑):
- Interpreta query como regex
- Suporta padrões complexos: `^import.*from`, `\d+`, etc.

**Quando Inativo** (☐):
- Busca literal de string
- Caracteres especiais são tratados como literais

---

## 📍 Occurrence Modes

### First (Primeira Ocorrência)

Insere **apenas** na **primeira linha** que casa com o padrão.

```python
# Arquivo:
import os
import sys
import re

# Query: "import"
# Occurrence: First
# Result: Insere apenas na linha 1 (import os)
```

### Last (Última Ocorrência)

Insere **apenas** na **última linha** que casa com o padrão.

```python
# Arquivo:
import os
import sys
import re

# Query: "import"
# Occurrence: Last
# Result: Insere apenas na linha 3 (import re)
```

### All (Todas as Ocorrências)

Insere em **todas as linhas** que casam com o padrão.

```python
# Arquivo:
import os
import sys
import re

# Query: "import"
# Occurrence: All
# Result: Insere nas linhas 1, 2 e 3
```

**Nota**: Quando usar "All", as inserções são processadas de baixo para cima para evitar mudanças nos números de linha.

---

## 🎨 Interface do Usuário

### Layout Completo

```
┌─────────────────────────────────────────────────────┐
│ Root path: [/path/to/files          ] [Browse...]   │
│ ☐ Is File?                                           │
│ Include globs: [*.ts;*.tsx;*.js;*.jsx;*.py;*.md]   │
│ Exclude globs: [node_modules;dist;build;.git]      │
├─────────────────────────────────────────────────────┤
│ ╔═══════════════════════════════════════════════╗  │
│ ║ Line Lookup (optional - leave empty for line) ║  │
│ ╠═══════════════════════════════════════════════╣  │
│ ║ Search query: [___________________________]   ║  │
│ ║ ☑ Case sensitive ☐ Whole word ☐ Regex        ║  │
│ ║ Occurrence: [First ▼]                         ║  │
│ ╚═══════════════════════════════════════════════╝  │
├─────────────────────────────────────────────────────┤
│ Line number (1-based): [1      ]                    │
│ (Manual - used only if search query is empty)       │
├─────────────────────────────────────────────────────┤
│ Insert text:                                         │
│ ┌─────────────────────────────────────────────┐    │
│ │ Text to insert here...                       │    │
│ └─────────────────────────────────────────────┘    │
│ Mode: [INSERT_ABOVE ▼]                              │
└─────────────────────────────────────────────────────┘
```

---

## 🧪 Casos de Uso Práticos

### Caso 1: Adicionar Comentário Antes de Funções

**Objetivo**: Inserir docstring antes de todas as funções Python

```python
Query:        "def "
Case:         ☑ (sensitive)
Word:         ☐
Regex:        ☐
Occurrence:   All
Mode:         INSERT_ABOVE
Insert text:  """Function documentation."""
```

**Antes**:
```python
def calculate(x, y):
    return x + y

def process(data):
    return data * 2
```

**Depois**:
```python
"""Function documentation."""
def calculate(x, y):
    return x + y

"""Function documentation."""
def process(data):
    return data * 2
```

---

### Caso 2: Adicionar Import Após Último Import

**Objetivo**: Adicionar novo import após o último import existente

```python
Query:        "^import "
Case:         ☑
Word:         ☐
Regex:        ☑ (ativo)
Occurrence:   Last
Mode:         INSERT_BELOW
Insert text:  import newmodule
```

**Antes**:
```python
import os
import sys
import re

def main():
    pass
```

**Depois**:
```python
import os
import sys
import re
import newmodule

def main():
    pass
```

---

### Caso 3: Adicionar Tag ao Final de Linhas TODO

**Objetivo**: Adicionar prioridade em todos os TODOs

```python
Query:        "TODO"
Case:         ☐ (insensitive - aceita TODO, todo, Todo)
Word:         ☑ (whole word - não casa com TODONE)
Regex:        ☐
Occurrence:   All
Mode:         RIGHT
Insert text:   // PRIORITY: HIGH
```

**Antes**:
```python
# TODO: Fix this bug
def process():
    pass

# TODO: Refactor code
def cleanup():
    pass
```

**Depois**:
```python
# TODO: Fix this bug // PRIORITY: HIGH
def process():
    pass

# TODO: Refactor code // PRIORITY: HIGH
def cleanup():
    pass
```

---

### Caso 4: Inserir Comentário em Linhas com Regex

**Objetivo**: Comentar linhas que contêm números de versão

```python
Query:        "version.*\d+\.\d+\.\d+"
Case:         ☐
Word:         ☐
Regex:        ☑ (ativo)
Occurrence:   All
Mode:         LEFT
Insert text:  # 
```

**Antes**:
```python
app_version = "1.2.3"
api_version = "2.0.1"
name = "MyApp"
```

**Depois**:
```python
# app_version = "1.2.3"
# api_version = "2.0.1"
name = "MyApp"
```

---

### Caso 5: Adicionar Logging em Funções Específicas

**Objetivo**: Adicionar logging apenas em funções "process"

```python
Query:        "def process"
Case:         ☑
Word:         ☑ (não casa com "def process_data")
Regex:        ☐
Occurrence:   All
Mode:         INSERT_BELOW
Insert text:      logger.info("Function called")
```

**Antes**:
```python
def process():
    return True

def process_data():
    return False

def process():
    return None
```

**Depois**:
```python
def process():
    logger.info("Function called")
    return True

def process_data():
    return False

def process():
    logger.info("Function called")
    return None
```

---

## 📊 Mensagem de Confirmação

Após aplicar inserções, uma mensagem informativa é exibida:

### Exemplo 1: Modo Lookup com Matches

```
Modified files: 5
Skipped files (no match): 2

Used search query: 'def calculate'
Occurrence mode: First
```

### Exemplo 2: Modo Lookup com All

```
Modified files: 12
Skipped files (no match): 0

Used search query: 'TODO'
Occurrence mode: All
```

### Exemplo 3: Modo Manual

```
Modified files: 8
Skipped files (no match): 0

Used line number: 42
```

---

## 🔧 Implementação Técnica

### Método _find_line_by_query()

```python
def _find_line_by_query(self, text: str, query: str) -> List[int]:
    """
    Find line numbers matching the query.
    Returns list of 1-based line numbers.
    """
    if not query:
        return []
    
    case_sensitive = self.chk_lookup_case.isChecked()
    whole_word = self.chk_lookup_word.isChecked()
    use_regex = self.chk_lookup_regex.isChecked()
    
    lines = text.splitlines()
    matches = []
    
    for i, line in enumerate(lines, start=1):
        if self._line_matches_query(line, query, case_sensitive, 
                                     whole_word, use_regex):
            matches.append(i)
    
    return matches
```

### Método _line_matches_query()

```python
def _line_matches_query(self, line: str, query: str, case_sensitive: bool, 
                         whole_word: bool, use_regex: bool) -> bool:
    """
    Check if a line matches the query with given options.
    """
    try:
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = query
            if whole_word:
                pattern = r'\b' + pattern + r'\b'
            return bool(re.search(pattern, line, flags))
        else:
            search_line = line if case_sensitive else line.lower()
            search_query = query if case_sensitive else query.lower()
            
            if whole_word:
                pattern = r'\b' + re.escape(search_query) + r'\b'
                flags = 0 if case_sensitive else re.IGNORECASE
                return bool(re.search(pattern, line, flags))
            else:
                return search_query in search_line
    except re.error:
        return False
```

### Lógica de Aplicação

```python
def _apply(self):
    query = self.ed_query.text().strip()
    manual_line = self.spin_line.value()
    
    for p in self._files():
        old = read_text(p)
        
        # Determine line numbers
        if query:
            line_matches = self._find_line_by_query(old, query)
            if not line_matches:
                skipped += 1
                continue
            
            if occurrence == "First":
                target_lines = [line_matches[0]]
            elif occurrence == "Last":
                target_lines = [line_matches[-1]]
            else:  # "All"
                target_lines = line_matches
        else:
            target_lines = [manual_line]
        
        # Apply insertions (bottom to top for All mode)
        new = old
        for line in sorted(target_lines, reverse=True):
            new = insert_at_line(new, line, insert_text, mode)
        
        if new != old:
            write_text(p, new)
            count += 1
```

---

## 📈 Estatísticas de Testes

### Suite: `test_line_lookup_feature.py`

- **Total de Testes**: 10
- **Testes Passando**: 10 ✅
- **Cobertura**: 100%

#### Testes Implementados

1. `test_find_line_case_sensitive` - Busca case-sensitive
2. `test_find_line_case_insensitive` - Busca case-insensitive
3. `test_find_line_whole_word` - Busca whole word
4. `test_find_line_regex` - Busca com regex
5. `test_insert_at_first_occurrence` - Inserção na primeira ocorrência
6. `test_insert_at_last_occurrence` - Inserção na última ocorrência
7. `test_insert_at_all_occurrences` - Inserção em todas ocorrências
8. `test_no_match_skips_file` - Arquivo sem match é ignorado
9. `test_regex_with_whole_word` - Regex com whole word
10. `test_multiline_insertion` - Inserção de múltiplas linhas

---

## ⚠️ Considerações e Limitações

### Performance

- Busca em arquivos grandes pode ser lenta
- Modo "All" com muitos matches processa múltiplas inserções
- Regex complexos aumentam tempo de processamento

### Recomendações

1. **Use padrões específicos**: Evite padrões muito genéricos que casem com muitas linhas
2. **Teste em poucos arquivos primeiro**: Valide query antes de aplicar em muitos arquivos
3. **Prefira Whole Word**: Reduz falsos positivos
4. **Valide regex externamente**: Use regex101.com para testar padrões complexos

### Comportamento com Occurrence "All"

Quando usar "All":
- Inserções são processadas de **baixo para cima** (linha maior para menor)
- Isso evita mudanças nos números de linha durante processamento
- Garante que todas as inserções sejam feitas nas linhas corretas

### Arquivos Sem Match

- Arquivos onde nenhuma linha casa com a query são **ignorados**
- Contados como "skipped" na mensagem final
- Não geram erro, apenas não são modificados

---

## 🔗 Compatibilidade

- **Retrocompatível**: Modo manual preservado 100%
- **Integração**: Funciona com Advanced Conditions (v2.1.0)
- **Versão Mínima**: Python 3.7+
- **Dependências**: Módulo `re` (built-in)

---

## 📚 Exemplos Avançados

### Exemplo: Adicionar Type Hints

```python
Query:        "def \w+\(.*\):"
Case:         ☑
Word:         ☐
Regex:        ☑
Occurrence:   All
Mode:         REPLACE
Insert text:  def function_name(param: str) -> None:
```

### Exemplo: Comentar Prints de Debug

```python
Query:        "^\s*print\("
Case:         ☐
Word:         ☐
Regex:        ☑
Occurrence:   All
Mode:         LEFT
Insert text:  # DEBUG: 
```

### Exemplo: Adicionar Try-Except

```python
Query:        "with open\("
Case:         ☑
Word:         ☐
Regex:        ☑
Occurrence:   First
Mode:         INSERT_ABOVE
Insert text:  try:
```

---

## 📖 Referências

- [Python re module](https://docs.python.org/3/library/re.html)
- [CHANGELOG v2.3.0](../../CHANGELOG.md#230---2025-11-24)
- [Insert Modes](../INSERT_MODES.md)
- [Advanced Conditions](../ADVANCED_CONDITIONS.md)

---

**Version History**:
- v2.3.0 (2025-11-24): Feature implementada e documentada
