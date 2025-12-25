# Sprint 2 - Análise: add/main.py Advanced Extractor

**Data:** 2025-12-25  
**Arquivo:** `add/main.py` (1.745 linhas)  
**Status:** Parcialmente extraído

---

## 📊 Mapeamento: O que já foi integrado

### ✅ 1. JSXParser Class (Básico)
**Localização atual:** `src/extractors/jsx_parser.py`  
**Linhas:** ~200 linhas  
**Status:** INTEGRADO PARCIALMENTE

**O que já existe:**
- Parsing básico de tags JSX `<Tag ...>`
- Detecção de self-closing `<Tag />`
- Extração de atributos `key="value"`
- Stack de tags para hierarquia

**O que FALTA do add/main.py:**
- ❌ `is_attribute_mode` - modo para extrair só atributos vs conteúdo
- ❌ `no_standard` - filtrar tags HTML padrão
- ❌ `_custom_find_matching_close_span()` - algoritmo robusto de matching
- ❌ `_extract_non_tag_items()` - extrair texto entre tags
- ❌ `_strip_tag_tokens()` - limpar tokens de tags
- ❌ `_read_balanced_brace_expr()` - ler expressões JSX balanceadas

---

### ✅ 2. GenericScopeParser Class (Básico)
**Localização atual:** `src/extractors/generic_parser.py`  
**Linhas:** ~100 linhas  
**Status:** INTEGRADO PARCIALMENTE

**O que já existe:**
- Parser genérico com regex start/end
- Extração de conteúdo entre delimitadores

**O que FALTA do add/main.py:**
- ❌ `match_all` - extrair todos os parâmetros sem filtro
- ❌ Melhor handling de scopes aninhados

---

### ✅ 3. Normalization Utils
**Localização atual:** `src/utils/normalization.py`  
**Linhas:** ~50 linhas  
**Status:** INTEGRADO PARCIALMENTE

**O que já existe:**
- `normalize_token()` - snake_case, camelCase, PascalCase, kebab-case
- Conversão para uppercase

**O que FALTA do add/main.py:**
- ❌ `smart_truncate()` - truncar com avoid_cut (boundary)
- ❌ `strip_code_fences()` - remover ```code fences```
- ❌ `kept_prefix()` - algoritmo de drop standard HTML tags

---

### ✅ 4. JSXExtractorDock (GUI Básica)
**Localização atual:** `src/gui/jsx_extractor_dock.py`  
**Linhas:** ~300 linhas  
**Status:** GUI BÁSICA INTEGRADA

**O que já existe:**
- Input para file/directory
- Botão Extract
- Output preview
- Save JSON

**O que FALTA do add/main.py:**
- ❌ Checkboxes avançados:
  - `is_attribute_mode` - extrair atributo vs conteúdo
  - `add_value` - incluir valor normalizado no path
  - `add_key` - incluir chave no path
  - `only_string` - aceitar apenas strings literais
  - `drop_standard` - remover tags HTML padrão
  - `emit_nested` - gerar JSON aninhado vs flat
- ❌ Opções de normalização:
  - Case style dropdown (snake/camel/pascal/kebab)
  - Uppercase checkbox
  - Limit input + avoid_cut checkbox
- ❌ Preview avançado com filtros
- ❌ Context menu (Copy, Export, Add to JSON)
- ❌ Painel de paths separado
- ❌ Algoritmo de remoção de hierarquia numérica

---

## 🔍 Classes e Funções NUNCA Integradas

### 1. Extractor Class (Core Business Logic)
**Linhas:** 825-1343 (518 linhas!)  
**Métodos:**

#### Construtor
```python
def __init__(
    self, param_name: str, mode: str,
    case_style: str = "snake",
    limit: Optional[str] = "all",
    avoid_cut: bool = True,
    to_upper: bool = False,
    drop_standard: bool = False,
    add_value: bool = False,
    add_key: bool = False,
    start_regex: Optional[str] = None,
    end_regex: Optional[str] = None,
    emit_nested: bool = True,
    is_attribute_mode: bool = False,
    only_string: bool = False,
    depth_offset: int = 0,
    avoid_keys: Optional[List[str]] = None
)
```

**⭐ Métodos Críticos Não Integrados:**

1. **`find_paths_to_key()`** - Buscar todos os paths que levam a uma chave
2. **`get_subtree_at_path()`** - Obter subárvore em path específico
3. **`build_tree_from_path()`** - Construir árvore de dict a partir de path
4. **`merge_dicts()`** - Merge profundo de dicts
5. **`prune_to_key()`** - Podar árvore para manter apenas paths até key
6. **`remove_key()`** - Remover key de estrutura
7. **`remove_key_with_collapse()`** - Remover key e colapsar hierarquia numérica ⭐⭐⭐
8. **`check_value_if_it_is_just_string()`** - Validar se valor é string literal
9. **`process_text()`** - Processar texto e gerar paths + JSON
10. **`json_to_js_literal()`** - Converter JSON para literal JS
11. **`_nearest_kept_ancestor_tokens()`** - Encontrar ancestral não-standard mais próximo
12. **`_record_text_bucket()`** - Gravar path com bucket de valores

---

### 2. MainWindow Class (GUI Completa)
**Linhas:** 1395-1683 (288 linhas)  
**Métodos:**

1. **`_build_ui()`** - Construir interface completa ⭐⭐⭐
   - 11 checkboxes (add_value, add_key, only_string, etc.)
   - 5 dropdowns (mode, case style, etc.)
   - 2 text inputs (start/end regex)
   - 3 text edits (paths, output, errors)
   - Context menu
   - Layout complexo

2. **`avoid_keys_option_changed()`** - Handler para avoid_keys
3. **`_should_filter_line()`** - Filtrar linhas no output
4. **`_copy_all()`** - Copiar resultado para clipboard
5. **`_toggle_generic_fields()`** - Mostrar/esconder campos generic mode
6. **`_browse()`** - Dialog de seleção file/directory
7. **`_run()`** - Executar extração (core logic)
8. **`_save_outputs()`** - Salvar paths e JSON

---

### 3. Utils Functions Não Integradas

1. **`kept_prefix()`** - Algoritmo de drop standard tags
2. **`smart_truncate()`** - Truncar com avoid_cut
3. **`strip_code_fences()`** - Remover triple backticks
4. **`insert_nested()`** - Inserir em dict aninhado

---

## 🎯 Priorização de Features para Integração

### 🔥 CRÍTICO (Deve integrar):

1. **`remove_key_with_collapse()`** ⭐⭐⭐⭐⭐
   - Algoritmo para remover hierarquia numérica
   - Mencionado explicitamente no plano
   - 35 linhas de lógica complexa

2. **`check_value_if_it_is_just_string()`** ⭐⭐⭐⭐
   - Validar se valor é string literal (not expression)
   - Usado em `only_string` mode
   - 44 linhas com regex complexo

3. **`process_text()`** ⭐⭐⭐⭐
   - Core logic de processamento
   - 89 linhas
   - Orquestra JSXParser/GenericParser + Extractor

4. **Checkboxes avançados na GUI** ⭐⭐⭐
   - `add_value`, `add_key`, `only_string`, `is_attribute_mode`
   - Mencionados no plano

---

### ⚠️ IMPORTANTE (Bom ter):

5. **`find_paths_to_key()` + `prune_to_key()`** ⭐⭐
   - Buscar e podar árvore por chave
   - Útil para "avoid keys" feature

6. **Context Menu** ⭐⭐
   - Reaproveitado de outro software
   - Copy, Export, Add to JSON, etc.

7. **Preview avançado com filtros** ⭐⭐
   - Separar paths de output
   - Filtrar linhas

---

### 💡 NICE TO HAVE (Pode adiar):

8. **`json_to_js_literal()`**
   - Converter JSON para JS literal
   - Feature avançada

9. **`smart_truncate()` com avoid_cut**
   - Truncar no boundary de palavra
   - Refinamento

---

## 📋 Plano de Integração Revisado

### Fase 1: Core Business Logic (4h)
**Objetivo:** Integrar classe Extractor completa

**Tarefa 1.1:** Criar `src/extractors/advanced_extractor.py`
- Extrair classe `Extractor` completa de add/main.py
- Incluir todos os 12 métodos principais
- Especialmente `remove_key_with_collapse()` e `check_value_if_it_is_just_string()`
- **Tempo:** 2h

**Tarefa 1.2:** Integrar utils avançados
- `kept_prefix()`, `smart_truncate()`, `strip_code_fences()`, `insert_nested()`
- Criar `src/utils/extraction_utils.py`
- **Tempo:** 1h

**Tarefa 1.3:** Atualizar JSXParser e GenericParser
- Adicionar `is_attribute_mode`, `no_standard`, `match_all`
- Adicionar métodos avançados faltantes
- **Tempo:** 1h

---

### Fase 2: GUI Avançada (3h)
**Objetivo:** Criar AdvancedExtractorDock com todas features

**Tarefa 2.1:** Criar layout completo
- 11 checkboxes avançados
- Dropdowns de case style
- Inputs de regex
- 3 painéis (paths, output, errors)
- **Tempo:** 1.5h

**Tarefa 2.2:** Implementar lógica de execução
- `_run()` method usando AdvancedExtractor
- `_save_outputs()` para paths e JSON
- `_toggle_generic_fields()` para mostrar/esconder
- **Tempo:** 1h

**Tarefa 2.3:** Integrar context menu
- Copy, Copy All, Export, Add to JSON
- Reaproveitado de outro software
- **Tempo:** 30min

---

### Fase 3: Testes (1h)
**Objetivo:** Garantir funcionamento de todas features

**Tarefa 3.1:** Criar `tests/test_advanced_extractor.py`
- Testar `remove_key_with_collapse()`
- Testar `check_value_if_it_is_just_string()`
- Testar `process_text()` com vários modos
- **Tempo:** 45min

**Tarefa 3.2:** Teste de integração GUI
- Testar JSX mode com todas opções
- Testar Generic mode
- Validar output JSON
- **Tempo:** 15min

---

## 📊 Estatísticas

| Item | Linhas no add/main.py | Status Atual | Prioridade |
|------|----------------------|--------------|------------|
| JSXParser (avançado) | ~400 | 50% integrado | 🔥 CRÍTICO |
| GenericParser (avançado) | ~100 | 40% integrado | ⚠️ IMPORTANTE |
| Extractor class | ~518 | 0% integrado | 🔥 CRÍTICO |
| Utils avançados | ~100 | 30% integrado | ⚠️ IMPORTANTE |
| MainWindow GUI | ~288 | 20% integrado | 🔥 CRÍTICO |
| **TOTAL** | **~1.406** | **25% integrado** | - |

**Código órfão restante:** ~1.056 linhas (~75% ainda não integrado)

---

## ✅ Próximos Passos

1. ✅ Criar este documento de análise
2. 🔄 Tarefa 1.1: Extrair classe Extractor → `advanced_extractor.py`
3. ⏭️ Tarefa 1.2: Criar `extraction_utils.py`
4. ⏭️ Tarefa 1.3: Atualizar parsers existentes
5. ⏭️ Fase 2: GUI avançada
6. ⏭️ Fase 3: Testes

**Tempo estimado total:** 8 horas  
**Complexidade:** 🔥🔥🔥 ALTA (código complexo, muitas features)
