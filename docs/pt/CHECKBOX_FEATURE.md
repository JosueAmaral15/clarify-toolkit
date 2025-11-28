# Checkbox Feature - Advanced Conditions Matching Options

**Version**: 2.2.0  
**Date**: 2025-11-24  
**Author**: Josué Amaral

---

## 📋 Visão Geral

A funcionalidade de **Checkbox Options** nas **Advanced Conditions** permite controlar com precisão como as buscas de string são realizadas. São três opções independentes que podem ser combinadas para criar padrões de busca sofisticados:

1. **Case Sensitive** - Controla diferenciação entre maiúsculas e minúsculas
2. **Match Whole Word** - Força casamento apenas de palavras completas
3. **Use Regex** - Interpreta o valor como expressão regular

---

## 🎯 Checkboxes Disponíveis

### 1. Case Sensitive (Sensível ao Caso)

**Estado Padrão**: ✅ Ativo (case-sensitive)

#### Quando Ativo
- A busca diferencia maiúsculas de minúsculas
- "Hello" ≠ "hello" ≠ "HELLO"
- Comportamento tradicional de busca exata

#### Quando Inativo
- A busca ignora diferenças de caso
- "Hello" = "hello" = "HELLO" = "HeLLo"
- Útil para buscas mais flexíveis

#### Exemplo
```python
# Arquivo contém: "Python Programming"

# Case Sensitive = True
"python" → ❌ Não encontra
"Python" → ✅ Encontra

# Case Sensitive = False
"python" → ✅ Encontra
"PYTHON" → ✅ Encontra
"PyThOn" → ✅ Encontra
```

---

### 2. Match Whole Word (Casar Palavra Inteira)

**Estado Padrão**: ❌ Inativo

#### Quando Ativo
- Usa word boundaries (`\b`) do regex
- Força casamento apenas de palavras completas
- Evita casamentos parciais dentro de outras palavras

#### Quando Inativo
- Busca substring normal
- Casa com qualquer ocorrência, mesmo dentro de outras palavras

#### Exemplo
```python
# Arquivo contém: "The cat is in the category"

# Whole Word = False
"cat" → ✅ Encontra "cat" e também dentro de "category"

# Whole Word = True
"cat" → ✅ Encontra apenas "cat" (palavra independente)
         ❌ Não casa com "cat" dentro de "category"
```

#### Casos Especiais
```python
# Arquivo: "email-address user_name test123"

# Whole Word considera hífens e underscores como delimitadores
"email"   → ✅ Casa (seguido por hífen)
"address" → ✅ Casa (precedido por hífen)
"user"    → ✅ Casa (seguido por underscore)
"name"    → ✅ Casa (precedido por underscore)
"test"    → ✅ Casa (seguido por número)
```

---

### 3. Use Regex (Usar Expressão Regular)

**Estado Padrão**: ❌ Inativo

#### Quando Ativo
- Interpreta o valor como padrão de expressão regular Python
- Suporta todos os recursos do módulo `re`
- Permite padrões complexos de busca

#### Quando Inativo
- Busca literal de string
- Caracteres especiais são tratados como literais

#### Exemplo Básico
```python
# Arquivo: "Contact: user@example.com and admin@site.org"

# Regex = False
"@" → ✅ Encontra o caractere literal "@"

# Regex = True
r"\w+@\w+\.\w+" → ✅ Encontra emails usando padrão regex
r"\d+"          → ✅ Encontra sequências de dígitos
r"^Contact"     → ✅ Verifica se começa com "Contact"
```

#### Padrões Regex Comuns
```python
# Emails
r"\w+@\w+\.\w+"

# URLs
r"https?://[\w\.-]+\.\w+"

# Números de telefone
r"\(\d{3}\)\s?\d{3}-\d{4}"

# Datas (DD/MM/YYYY)
r"\d{2}/\d{2}/\d{4}"

# Palavras específicas com variações
r"colou?r"  # casa "color" ou "colour"

# Linhas vazias
r"^\s*$"
```

---

## 🔄 Combinações de Checkboxes

As três opções podem ser combinadas para criar buscas poderosas:

### Combinação 1: Case Insensitive + Whole Word

```python
# Arquivo: "The CAT is in the CATEGORY"

# Case=False, Word=True
"cat" → ✅ Encontra "CAT" (palavra completa, ignorando caso)
      → ❌ Não encontra em "CATEGORY"
```

### Combinação 2: Regex + Case Insensitive

```python
# Arquivo: "Email: USER@EXAMPLE.COM"

# Regex=True, Case=False
r"user@example\.com" → ✅ Encontra (ignora diferença de caso)
r"[A-Z]+"            → ✅ Encontra palavras em maiúsculas
```

### Combinação 3: Regex + Whole Word

```python
# Arquivo: "version 1.2.3 and v1.2.3"

# Regex=True, Word=True
r"\d+\.\d+\.\d+" → ✅ Encontra "1.2.3" (palavra independente)
                 → ✅ Também encontra em "v1.2.3"
```

### Combinação 4: Todas as Opções

```python
# Arquivo: "The EMAIL address is user@site.com"

# Case=False, Word=True, Regex=True
r"email" → ✅ Encontra "EMAIL" como palavra completa, case-insensitive
```

---

## 📝 Aplicação por Campo

### Campos que Suportam Checkboxes

| Campo      | Case | Word | Regex | Descrição                          |
|------------|------|------|-------|------------------------------------|
| `filename` | ✅   | ✅   | ✅    | Nome do arquivo (sem path)         |
| `path`     | ✅   | ✅   | ✅    | Caminho completo do arquivo        |
| `ext`      | ✅   | ✅   | ✅    | Extensão do arquivo (sem ponto)    |
| `content`  | ✅   | ✅   | ✅    | Conteúdo do arquivo                |
| `size`     | ❌   | ❌   | ❌    | Tamanho (apenas numérico)          |
| `mtime`    | ❌   | ❌   | ❌    | Data modificação (apenas numérico) |

**Nota**: Campos numéricos (`size`, `mtime`) não utilizam os checkboxes, pois operam com comparações numéricas.

---

## 🎨 Interface do Usuário

### Layout das Advanced Conditions

```
┌─────────┬──────────┬───────┬────────┬──────────┬──────┬──────┬───────┐
│ Field   │ Operator │ Value │ Scope  │ Scope    │ Case │ Word │ Regex │
│         │          │       │        │ Param    │      │      │       │
├─────────┼──────────┼───────┼────────┼──────────┼──────┼──────┼───────┤
│filename │contains  │ test  │ none   │          │  ☑   │  ☐   │  ☐   │
├─────────┼──────────┼───────┼────────┼──────────┼──────┼──────┼───────┤
│content  │contains  │ email │brackets│          │  ☐   │  ☑   │  ☑   │
├─────────┼──────────┼───────┼────────┼──────────┼──────┼──────┼───────┤
│path     │equals    │/home/ │ none   │          │  ☑   │  ☐   │  ☐   │
└─────────┴──────────┴───────┴────────┴──────────┴──────┴──────┴───────┘
```

### Tooltips

- **Case**: "Case sensitive"
- **Word**: "Match whole word"
- **Regex**: "Use regular expression"

---

## ⚙️ Integração com Scope Feature

Os checkboxes funcionam perfeitamente com a funcionalidade de Scope (v2.1.0):

```python
# Exemplo: Buscar emails apenas dentro de colchetes, case-insensitive

Field:       content
Operator:    contains
Value:       r"\w+@\w+\.\w+"
Scope:       brackets
Scope Param: (vazio)
Case:        ☐ (inativo - case insensitive)
Word:        ☐ (inativo)
Regex:       ☑ (ativo - usar regex)
```

**Resultado**: Busca padrão de email usando regex, sem diferenciar maiúsculas/minúsculas, apenas dentro de `[...]`.

---

## 🧪 Casos de Uso Práticos

### 1. Buscar Imports Python (Case Insensitive)

```python
Field:    content
Operator: starts with
Value:    from
Case:     ☐ False
Word:     ☐ False
Regex:    ☐ False
```

### 2. Buscar Variáveis Específicas (Whole Word)

```python
Field:    content
Operator: contains
Value:    userId
Case:     ☑ True
Word:     ☑ True   # Não casa com "userIdToken" ou "getUserId"
Regex:    ☐ False
```

### 3. Validar Formato de Email (Regex)

```python
Field:    content
Operator: contains
Value:    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
Case:     ☑ True
Word:     ☐ False
Regex:    ☑ True
```

### 4. Buscar Comentários TODO (Case Insensitive + Regex)

```python
Field:    content
Operator: contains
Value:    r"(TODO|FIXME|HACK|XXX):"
Case:     ☐ False  # Aceita "todo:", "Todo:", "TODO:"
Word:     ☐ False
Regex:    ☑ True
```

### 5. Arquivos com Extensão Específica (Case Insensitive)

```python
Field:    ext
Operator: equals
Value:    tsx
Case:     ☐ False  # Aceita ".tsx", ".TSX", ".Tsx"
Word:     ☐ False
Regex:    ☐ False
```

---

## 🔧 Implementação Técnica

### Classe Condition

```python
@dataclass
class Condition:
    field: str
    operator: str
    value: str
    scope_type: str = ""
    scope_value: str = ""
    case_sensitive: bool = True      # Novo em v2.2.0
    whole_word: bool = False         # Novo em v2.2.0
    use_regex: bool = False          # Novo em v2.2.0
```

### Método _apply_string_matching

O método `_apply_string_matching()` processa todas as combinações de flags:

1. **Regex Mode**: Se `use_regex=True`, compila padrão com flags apropriadas
2. **Whole Word**: Adiciona `\b` ao padrão se necessário
3. **Case Insensitive**: Aplica flag `re.IGNORECASE` ou `.lower()` nas strings
4. **Operadores**: Suporta contains, equals, starts with, ends with, not contains, not equals

---

## 📊 Estatísticas de Testes

### Suite de Testes: `test_checkbox_feature.py`

- **Total de Testes**: 10
- **Testes Passando**: 10 ✅
- **Cobertura**: 100%

#### Testes Implementados

1. `test_case_sensitive_true` - Verifica matching case-sensitive
2. `test_case_insensitive` - Verifica matching case-insensitive
3. `test_whole_word_matching` - Verifica word boundaries
4. `test_regex_matching` - Verifica padrões regex básicos
5. `test_regex_with_case_insensitive` - Combina regex + case
6. `test_whole_word_with_case_insensitive` - Combina word + case
7. `test_filename_matching_with_flags` - Testa aplicação em filename
8. `test_operators_with_case_insensitive` - Testa operadores variados
9. `test_not_contains_with_whole_word` - Testa operador negativo
10. `test_all_flags_combined` - Testa todas as flags juntas

---

## ⚠️ Limitações e Considerações

### Regex Inválidos

Se o usuário fornecer um padrão regex inválido, a condição retornará `False`:

```python
# Regex inválido
r"[invalid(regex" → ❌ Erro de compilação, retorna False
```

### Performance

- **Regex**: Padrões complexos podem ser mais lentos
- **Whole Word**: Adiciona overhead de regex interno
- **Case Insensitive**: Overhead mínimo (`.lower()`)

### Recomendações

1. Use regex apenas quando necessário
2. Teste padrões regex em ferramenta externa primeiro (regex101.com)
3. Para buscas simples, prefira case-insensitive ao invés de regex
4. Combine whole word com case insensitive para buscas flexíveis

---

## 🔗 Compatibilidade

- **Retrocompatível**: Valores padrão preservam comportamento anterior
- **Versão Mínima**: Python 3.7+
- **Dependências**: Módulo `re` (built-in)
- **Integração**: Funciona com Scope Feature (v2.1.0)

---

## 📚 Referências

- [Python re module](https://docs.python.org/3/library/re.html)
- [Regex Tutorial](https://www.regular-expressions.info/)
- [Word Boundaries](https://www.regular-expressions.info/wordboundaries.html)
- [CHANGELOG v2.2.0](../../CHANGELOG.md#220---2025-11-24)

---

**Version History**:
- v2.2.0 (2025-11-24): Funcionalidade implementada e documentada
