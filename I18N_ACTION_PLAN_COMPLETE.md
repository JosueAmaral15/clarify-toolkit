# 📋 PLANO DE AÇÃO COMPLETO: CORREÇÃO 129 STRINGS i18n

**Data**: 02/01/2026  
**Duração Estimada**: 6-8 horas  
**Prioridade**: 🔴 ALTA (Solicitado pelo usuário - Opção A)  
**Estratégia**: Correção sistemática por categoria

---

## 📊 VISÃO GERAL

| Task | Categoria | Quantidade | Tempo | Prioridade |
|------|-----------|-----------|-------|-----------|
| **Task 1** | Tooltips | 48 | 2h | 🔴 CRÍTICA |
| **Task 2** | File Explorer (reportado) | 15 | 1h | 🔴 CRÍTICA |
| **Task 3** | QLabel | 35 | 1h | 🟡 ALTA |
| **Task 4** | QPushButton | 16 | 45min | 🟡 ALTA |
| **Task 5** | Table Headers | 10 | 45min | 🟡 ALTA |
| **Task 6** | QCheckBox | 10 | 30min | 🟢 MÉDIA |
| **Task 7** | Placeholders | 6 | 30min | 🟢 MÉDIA |
| **Task 8** | ComboBox | 4 | 20min | 🟢 BAIXA |
| **Task 9** | Testes Manuais | Todas | 1-2h | 🔴 CRÍTICA |
| **Task 10** | Documentação | - | 30min | 🟢 MÉDIA |
| **TOTAL** | **129 strings** | **8-10h** | - |

---

## 🎯 TASK 1: TOOLTIPS (48 STRINGS) - PRIORIDADE CRÍTICA

### Estimativa: 2 horas
### Status: ⏳ PENDENTE

### Arquivos Afetados (por prioridade):

#### 1.1. batch_dialog.py (11 tooltips)
**Arquivo**: `src/gui/batch_dialog.py`

| Linha | Código Atual | Chave JSON | Tradução PT |
|-------|--------------|-----------|-------------|
| 356 | `"Add a new step to the batch"` | `batch_dialog.tooltip_add_step` | `"Adicionar nova etapa ao lote"` |
| 361 | `"Edit the selected step"` | `batch_dialog.tooltip_edit_step` | `"Editar etapa selecionada"` |
| 366 | `"Delete the selected step from batch"` | `batch_dialog.tooltip_remove_step` | `"Remover etapa do lote"` |
| 375 | `"Save each step's result as separate JSON file..."` | `batch_dialog.tooltip_save_intermediate` | `"Salvar resultado de cada etapa..."` |
| 381 | `"Directory where intermediate JSON files will be saved"` | `batch_dialog.tooltip_output_folder` | `"Diretório para salvar JSONs intermediários"` |
| 384 | `"Select output directory for intermediate results"` | `batch_dialog.tooltip_browse_output` | `"Selecionar diretório de saída"` |
| 397 | `"Save batch definition to JSON file"` | `batch_dialog.tooltip_save_batch` | `"Salvar definição do lote"` |
| 402 | `"Load batch definition from JSON file"` | `batch_dialog.tooltip_load_batch` | `"Carregar definição do lote"` |
| 410 | `"Run all steps sequentially with result chaining..."` | `batch_dialog.tooltip_execute` | `"Executar todas as etapas..."` |
| 415 | `"Stop execution immediately (current step will complete)"` | `batch_dialog.tooltip_cancel` | `"Parar execução imediatamente"` |
| 421 | `"Close batch dialog without executing"` | `batch_dialog.tooltip_close` | `"Fechar sem executar"` |

**Ação**:
```python
# ANTES:
self.btn_add_step.setToolTip("Add a new step to the batch")

# DEPOIS:
self.btn_add_step.setToolTip(tooltip_tr("batch_dialog.tooltip_add_step"))
```

**Import necessário**: `from src.i18n.translator import tooltip_tr`

---

#### 1.2. panels/search_replace_panel_NEW.py (6 tooltips) - BACKUP FILE
**Arquivo**: `src/gui/panels/search_replace_panel_NEW.py`

⚠️ **NOTA**: Este é arquivo `_NEW.py` (pode ser versão de teste/backup)

| Linha | String | Chave | PT |
|-------|--------|-------|-----|
| 120 | `"Match case exactly (A ≠ a)"` | `search_replace.tooltip_case` | `"Diferenciar maiúsculas/minúsculas"` |
| 124 | `"Match whole words only..."` | `search_replace.tooltip_word` | `"Apenas palavras inteiras"` |
| 128 | `"Treat search text as regular expression"` | `search_replace.tooltip_regex` | `"Usar expressão regular"` |
| 151 | `"Number of replacements (0 = all occurrences)"` | `search_replace.tooltip_count` | `"Número de substituições"` |
| 161 | `"Execute replacement operation"` | `search_replace.tooltip_replace` | `"Executar substituição"` |
| 166 | `"Test regex pattern (shows compiled pattern)"` | `search_replace.tooltip_test` | `"Testar padrão regex"` |

**DECISÃO**: ⚠️ **SKIP** (arquivo backup) OU corrigir se for usado?

---

#### 1.3. panels/search_replace_panel_BACKUP.py (6 tooltips) - BACKUP FILE
**Arquivo**: `src/gui/panels/search_replace_panel_BACKUP.py`

⚠️ **DECISÃO**: **SKIP** (arquivo explicitamente backup)

---

#### 1.4. panels/insert_panel_BACKUP.py (6 tooltips) - BACKUP FILE
**Arquivo**: `src/gui/panels/insert_panel_BACKUP.py`

⚠️ **DECISÃO**: **SKIP** (arquivo backup)

---

#### 1.5. panels/search_replace_panel.py (2 tooltips) - ARQUIVO ATIVO
**Arquivo**: `src/gui/panels/search_replace_panel.py`

| Linha | String | Chave | PT |
|-------|--------|-------|-----|
| 427 | `"Use regular expression"` | `search_replace.tooltip_regex_cond` | `"Usar expressão regular"` |

**Ação**: Corrigir este (arquivo ativo)

---

#### 1.6. panels/insert_panel.py (5 tooltips) - ARQUIVO ATIVO
**Arquivo**: `src/gui/panels/insert_panel.py`

| Linha | String | Chave | PT |
|-------|--------|-------|-----|
| 215 | `"Clear all advanced condition fields"` | `insert_panel.tooltip_clear_cond` | `"Limpar todas as condições"` |
| 238 | `"Save all match results to a text file"` | `insert_panel.tooltip_save_results` | `"Salvar resultados em arquivo"` |
| 340 | `"Case sensitive"` | `insert_panel.tooltip_case` | `"Sensível a maiúsculas"` |
| 344 | `"Match whole word"` | `insert_panel.tooltip_word` | `"Palavra inteira"` |
| 348 | `"Use regular expression"` | `insert_panel.tooltip_regex` | `"Usar expressão regular"` |
| 354 | `"Remove this condition row"` | `insert_panel.tooltip_remove_cond` | `"Remover esta condição"` |

---

#### 1.7. Outros arquivos (10 tooltips)
**Diversos arquivos**:
- `operation_preview_dialog.py` (3 tooltips)
- `config_editor_dialog.py` (3 tooltips)
- `tutorial_assistant_dialog.py` (2 tooltips)
- `progress/progress_manager.py` (1 tooltip)
- `progress/progress_bar_widget.py` (2 tooltips)

---

### Subtarefas Task 1:

- [ ] **1.1**: Adicionar 48 chaves em `en.json` (categoria: tooltips)
- [ ] **1.2**: Traduzir 48 chaves em `pt_BR.json`
- [ ] **1.3**: Corrigir `batch_dialog.py` (11 tooltips) + import tooltip_tr
- [ ] **1.4**: Corrigir `search_replace_panel.py` (2 tooltips)
- [ ] **1.5**: Corrigir `insert_panel.py` (5 tooltips)
- [ ] **1.6**: Corrigir `operation_preview_dialog.py` (3 tooltips)
- [ ] **1.7**: Corrigir `config_editor_dialog.py` (3 tooltips)
- [ ] **1.8**: Corrigir `tutorial_assistant_dialog.py` (2 tooltips)
- [ ] **1.9**: Corrigir `progress/*.py` (3 tooltips)
- [ ] **1.10**: Black + isort todos os arquivos
- [ ] **1.11**: Commit: `fix(i18n): translate 48 tooltips across 9 files`

**Tempo**: 2 horas

---

## 🎯 TASK 2: FILE EXPLORER - STRINGS REPORTADAS PELO USUÁRIO

### Estimativa: 1 hora
### Status: ⏳ PENDENTE
### Prioridade: 🔴 CRÍTICA (reportado diretamente)

### 2.1. Investigação Manual (30 min)

**Strings reportadas mas NÃO encontradas no grep**:
1. ❓ **"Quick Filter"**
2. ❓ **"Save Results"**
3. ❓ **"Export CSV"**
4. ❓ **"Directory"**
5. ❓ **"Include Globs"**
6. ❓ **"File Name"**
7. ❓ **"Content Search"**
8. ❓ **"Replace with"**
9. ✅ **"Name"** (header) - JÁ TRADUZIDO (tr("table_manager.header_name"))
10. ✅ **"Size"** (header) - JÁ TRADUZIDO
11. ✅ **"Modified"** (header) - JÁ TRADUZIDO
12. ✅ **"Permissions"** (header) - JÁ TRADUZIDO
13. ✅ **"Path"** (header) - JÁ TRADUZIDO

**HIPÓTESE**: 5 headers JÁ estão traduzidos. Strings restantes podem estar em:
- Widgets criados em `file_explorer_dock.py` (não em file_list_table_manager)
- Campos de texto/labels inline
- Ou usuário testou versão antiga

**Ação**:
```bash
# Investigar file_explorer_dock.py manualmente
grep -n "Quick Filter\|Save Results\|Export CSV\|Directory\|Include Globs\|File Name\|Content Search\|Replace with" \
  src/gui/file_explorer_dock.py
```

---

### 2.2. Correções Identificadas

#### file_list_table_manager.py (Quick Filter)
**Linha ~60**: Verificar se "Quick Filter" está no QLineEdit placeholder

```python
# Procurar:
self.filter_edit.setPlaceholderText("Quick Filter")

# Substituir por:
self.filter_edit.setPlaceholderText(tr("file_list.placeholder_quick_filter"))
```

**Chave**: `file_list.placeholder_quick_filter: "Quick Filter"` (EN) → `"Filtro Rápido"` (PT)

---

### 2.3. Verificação de Traduções Existentes

**Verificar se chaves já existem**:
```bash
grep -r "col_name\|col_size\|col_modified\|col_permissions\|col_path" src/i18n/en.json
```

Se **NÃO existirem** em `en.json`, mas código usa `tr("table_manager.header_name")`:
- Adicionar chaves faltantes em `en.json`
- Adicionar traduções em `pt_BR.json`

---

### Subtarefas Task 2:

- [ ] **2.1**: Abrir `file_explorer_dock.py` e procurar visualmente strings
- [ ] **2.2**: Grep expandido: `setText\(`, `addWidget\(QLabel\(`, etc.
- [ ] **2.3**: Testar aplicação e anotar ONDE vê cada string
- [ ] **2.4**: Screenshot de cada string em inglês
- [ ] **2.5**: Adicionar chaves faltantes em `en.json`/`pt_BR.json`
- [ ] **2.6**: Corrigir cada ocorrência encontrada
- [ ] **2.7**: Black + isort
- [ ] **2.8**: Testar manualmente File Explorer (todas as seções)
- [ ] **2.9**: Commit: `fix(i18n): translate File Explorer remaining strings`

**Tempo**: 1 hora

---

## 🎯 TASK 3: QLABEL (35 STRINGS)

### Estimativa: 1 hora
### Status: ⏳ PENDENTE

### Arquivos Afetados:

#### 3.1. panels/search_replace_panel_NEW.py (4 QLabel) - BACKUP
**SKIP** (arquivo backup)

#### 3.2. panels/search_replace_panel_BACKUP.py (2 QLabel) - BACKUP
**SKIP**

#### 3.3. panels/insert_panel_BACKUP.py (4 QLabel) - BACKUP
**SKIP**

#### 3.4. Arquivos Ativos (25 QLabel restantes)

**Lista**:
- `set_operations_dock.py:158` - `QLabel("")` (vazio, OK)
- `ai_processor_dock.py:331,333` - `QLabel("💬")`, `QLabel("🌍")` (ícones, OK)
- `tutorial_assistant_dialog.py:91` - `QLabel("")` (vazio)
- `panels/search_replace_panel.py:275` - `QLabel("")` (status, vazio)
- `panels/insert_panel.py:247` - `QLabel("")` (status, vazio)
- `venn_diagram_dialog.py:185` - `QLabel("<i>Click a region to view keys and values</i>")` ⚠️
- `diff_viewer_dialog.py:135,139,143,147` - Legend labels ⚠️
- `google_translate_dock.py:206` - `QLabel("")` (vazio)
- `jsx_extractor_dock.py:229` - `QLabel("")` (vazio)
- `transparency_dialog.py:61,71` - `QLabel("0%")`, `QLabel("100%")` ⚠️
- `text_to_json_dock.py:280` - `QLabel("")` (vazio)
- `progress/progress_manager.py:36` - `QLabel("<b>Active Tasks (0)</b>")` ⚠️
- `progress/progress_bar_widget.py:94` - `QLabel("")` (vazio)
- `progress/progress_details_dialog.py:52` - `QLabel("<b>Processing Details:</b>")` ⚠️

**Labels a corrigir** (não-vazios, não-ícones):
1. `venn_diagram_dialog.py:185` - `"<i>Click a region to view keys and values</i>"`
2. `diff_viewer_dialog.py:135` - `" Only in A "`
3. `diff_viewer_dialog.py:139` - `" Only in B "`
4. `diff_viewer_dialog.py:143` - `" Common "`
5. `diff_viewer_dialog.py:147` - `" Modified "`
6. `transparency_dialog.py:61` - `"0%"`
7. `transparency_dialog.py:71` - `"100%"`
8. `progress/progress_manager.py:36` - `"<b>Active Tasks (0)</b>"`
9. `progress/progress_details_dialog.py:52` - `"<b>Processing Details:</b>"`

**Total real a corrigir**: 9 QLabel (não 35!)

---

### Subtarefas Task 3:

- [ ] **3.1**: Adicionar 9 chaves em `en.json`
- [ ] **3.2**: Traduzir 9 chaves em `pt_BR.json`
- [ ] **3.3**: Corrigir `venn_diagram_dialog.py` (1)
- [ ] **3.4**: Corrigir `diff_viewer_dialog.py` (4)
- [ ] **3.5**: Corrigir `transparency_dialog.py` (2)
- [ ] **3.6**: Corrigir `progress/*.py` (2)
- [ ] **3.7**: Black + isort
- [ ] **3.8**: Commit: `fix(i18n): translate 9 QLabel strings`

**Tempo**: 30 min (reduzido de 1h)

---

## 🎯 TASK 4: QPUSHBUTTON (16 STRINGS)

### Estimativa: 45 minutos
### Status: ⏳ PENDENTE

### Análise:

**Arquivos**:
- `tutorial_assistant_dialog.py:114,120` - `"👍"`, `"👎"` (emojis, OK)
- `panels/search_replace_panel.py:430` - `"✖"` (emoji, OK)
- `panels/search_replace_panel_NEW.py:160,165` - BACKUP (skip)
- `panels/search_replace_panel_BACKUP.py:143,148` - BACKUP (skip)
- `panels/insert_panel_BACKUP.py:131,136,141,151,156` - BACKUP (skip)
- `progress/progress_manager.py:41` - `"▼"` (emoji, OK)
- `progress/progress_bar_widget.py:59,67,74` - `"⏸"`, `"↗"`, `"✖"` (emojis, OK)

**TODOS SÃO EMOJIS** - Não precisam tradução!

**Ação**: ✅ **NENHUMA** (emojis são universais)

**Tempo**: 0 min (ignorar esta task)

---

## 🎯 TASK 5: TABLE HEADERS (10 STRINGS)

### Estimativa: 45 minutos
### Status: ⏳ PENDENTE

### Headers Sem tr():

| Arquivo | Linha | Headers | Ação |
|---------|-------|---------|------|
| `batch_dialog.py` | 344 | 7 columns | Corrigir |
| `results_tree.py` | 43 | `["Match"]` | Corrigir |
| `panels/results_tree.py` | 128 | `["Match"]` | Corrigir |
| `statistics_dialog.py` | 110 | 6 columns | Corrigir |
| `calculator_dock.py` | 131 | 8 columns | Corrigir |
| `plugin_manager_dialog.py` | 61 | 5 columns | Corrigir |
| `formula_dock.py` | 213 | `['Step', 'Expression']` | Corrigir |
| `shortcut_customizer.py` | 149 | ? columns | Corrigir |
| `shortcuts_dialog.py` | 86 | ? columns | Corrigir |

---

### 5.1. batch_dialog.py (7 headers)
**Linha 344-351**:
```python
# ANTES:
self.table_steps.setHorizontalHeaderLabels([
    "Step", "Operation", "Target", "Options", "Status", "Result", "Actions"
])

# DEPOIS:
self.table_steps.setHorizontalHeaderLabels([
    tr("batch_dialog.col_step"),
    tr("batch_dialog.col_operation"),
    tr("batch_dialog.col_target"),
    tr("batch_dialog.col_options"),
    tr("batch_dialog.col_status"),
    tr("batch_dialog.col_result"),
    tr("batch_dialog.col_actions")
])
```

**Chaves PT**:
```json
{
  "batch_dialog": {
    "col_step": "Etapa",
    "col_operation": "Operação",
    "col_target": "Alvo",
    "col_options": "Opções",
    "col_status": "Status",
    "col_result": "Resultado",
    "col_actions": "Ações"
  }
}
```

---

### 5.2. results_tree.py (1 header)
```python
# ANTES:
self.setHeaderLabels(["Match"])

# DEPOIS:
self.setHeaderLabels([tr("results_tree.col_match")])
```

---

### Subtarefas Task 5:

- [ ] **5.1**: Abrir cada arquivo e ver headers exatos
- [ ] **5.2**: Adicionar ~40 chaves de headers em `en.json`
- [ ] **5.3**: Traduzir em `pt_BR.json`
- [ ] **5.4**: Corrigir `batch_dialog.py`
- [ ] **5.5**: Corrigir `results_tree.py` (2 arquivos)
- [ ] **5.6**: Corrigir `statistics_dialog.py`
- [ ] **5.7**: Corrigir `calculator_dock.py`
- [ ] **5.8**: Corrigir `plugin_manager_dialog.py`
- [ ] **5.9**: Corrigir `formula_dock.py`
- [ ] **5.10**: Corrigir `shortcut_customizer.py`
- [ ] **5.11**: Corrigir `shortcuts_dialog.py`
- [ ] **5.12**: Black + isort
- [ ] **5.13**: Commit: `fix(i18n): translate table headers (40 columns across 9 files)`

**Tempo**: 45 min

---

## 🎯 TASK 6: QCHECKBOX (10 STRINGS)

### Estimativa: 30 minutos
### Status: ⏳ PENDENTE

### Checkboxes a Corrigir:

#### 6.1. widgets/file_filter_panel.py (2 checkboxes)
```python
# Linha 149-150
self.chk_exclude_git = QCheckBox(".git")
self.chk_exclude_pycache = QCheckBox("__pycache__")
```

**Decisão**: ⚠️ Labels técnicos (nomes de pastas) - **MANTER EM INGLÊS**?
- `.git` e `__pycache__` são nomes técnicos universais
- Traduzir label seria confuso: `QCheckBox(tr("file_filter.chk_git"))` → ".git" mesmo em PT

**Ação**: **SKIP** (termos técnicos)

---

#### 6.2. panels/search_replace_panel_NEW.py (4 checkboxes) - BACKUP
**SKIP** (arquivo backup)

#### 6.3. panels/search_replace_panel_BACKUP.py (4 checkboxes) - BACKUP
**SKIP**

---

### Resultado: 0 checkboxes a corrigir (todos são backup ou técnicos)

**Tempo**: 0 min (task cancelada)

---

## 🎯 TASK 7: PLACEHOLDERS (6 STRINGS)

### Estimativa: 30 minutos
### Status: ⏳ PENDENTE

### Análise:
```bash
cat audit_i18n/05_placeholder.txt
# (output pendente - precisa ver quais são)
```

**Ação**: Listar os 6 placeholders e corrigir

**Tempo**: 30 min

---

## 🎯 TASK 8: COMBOBOX (4 STRINGS)

### Estimativa: 20 minutos
### Status: ⏳ PENDENTE

### Análise:
```bash
cat audit_i18n/04_combobox.txt
# (output pendente)
```

**Ação**: Listar os 4 items de combobox e corrigir

**Tempo**: 20 min

---

## 🎯 TASK 9: TESTES MANUAIS

### Estimativa: 1-2 horas
### Status: ⏳ PENDENTE
### Prioridade: 🔴 CRÍTICA

### Checklist de Validação:

#### 9.1. File Explorer (30 min)
- [ ] Abrir File Explorer
- [ ] Verificar todas as seções (Directory, Search, Filters, Advanced, Presets)
- [ ] Verificar modo Table (colunas traduzidas)
- [ ] Verificar modo Tree (labels traduzidos)
- [ ] Testar troca EN ↔ PT
- [ ] Screenshot antes/depois

#### 9.2. Outros Docks (1h)
- [ ] Search/Replace Panel
- [ ] Insert Panel
- [ ] Batch Dialog
- [ ] Calculator
- [ ] Set Operations
- [ ] Todos os outros (15+ docks)

#### 9.3. Dialogs e Widgets (30 min)
- [ ] Venn Diagram
- [ ] Diff Viewer
- [ ] Statistics Dialog
- [ ] Progress bars
- [ ] Todos os tooltips (hover sobre botões)

---

## 🎯 TASK 10: DOCUMENTAÇÃO

### Estimativa: 30 minutos
### Status: ⏳ PENDENTE

### Deliverables:

- [ ] **10.1**: Atualizar `CHANGELOG.md`
- [ ] **10.2**: Criar `I18N_COMPLETION_REPORT.md`
- [ ] **10.3**: Screenshots antes/depois
- [ ] **10.4**: Atualizar `TASKS.md` (marcar Task 1.4 como completa)

---

## 📈 CRONOGRAMA SUGERIDO

### Dia 1 (4h):
- Task 1: Tooltips (2h)
- Task 2: File Explorer (1h)
- Task 3: QLabel (30min)
- Task 5: Table Headers (30min)

### Dia 2 (4h):
- Task 5 (continuar): Headers (15min)
- Task 7: Placeholders (30min)
- Task 8: ComboBox (20min)
- Task 9: Testes (2h)
- Task 10: Docs (30min)
- **Buffer**: 45min para imprevistos

---

## ✅ CRITÉRIOS DE SUCESSO

### Técnicos:
- [ ] Zero `grep "setToolTip(\"" | grep -v "tooltip_tr"` em src/gui/
- [ ] Zero `grep "QLabel(\"[^\"]\+\")" | grep -v "tr("` (exceto vazios/emojis)
- [ ] Zero `grep "setHorizontalHeaderLabels" | grep -v "tr("`
- [ ] `en.json` e `pt_BR.json` sincronizados (mesmas chaves)
- [ ] Black + isort + pylint passam

### Funcionais:
- [ ] Usuário confirma: "Agora está 100% traduzido"
- [ ] Todas as telas em PT quando idioma = PT-BR
- [ ] Todas as telas em EN quando idioma = EN
- [ ] Tooltips aparecem traduzidos

### Processo:
- [ ] Commits organizados (1 por task)
- [ ] Documentação completa
- [ ] Screenshots incluídos

---

## 🚀 INÍCIO DA EXECUÇÃO

**Aprovação do Usuário**: ⏳ AGUARDANDO  
**Próximo Passo**: Executar Task 1 (Tooltips) após aprovação

**Tempo Total Estimado**: 6-8 horas  
**Complexidade**: 🟡 MÉDIA (trabalho repetitivo mas sistemático)
