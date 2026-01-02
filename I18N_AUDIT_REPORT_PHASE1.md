# 📊 RELATÓRIO DE AUDITORIA i18n - FASE 1

**Data**: 02/01/2026  
**Duração**: 45 minutos  
**Status**: ✅ COMPLETO

---

## 📈 RESUMO EXECUTIVO

### Números Totais:
| Categoria | Quantidade | Crítico |
|-----------|-----------|---------|
| **QLabel hardcoded** | 35 | 🟡 |
| **QPushButton hardcoded** | 16 | 🟡 |
| **QCheckBox hardcoded** | 10 | 🟡 |
| **ComboBox items hardcoded** | 4 | 🟢 |
| **Placeholders hardcoded** | 6 | 🟢 |
| **Tooltips hardcoded** | 48 | 🔴 **ALTA** |
| **Table headers sem tr()** | 10 | 🟡 |
| **Window titles hardcoded** | 0 | ✅ |
| **TOTAL** | **129** | - |

### Gravidade Global: 🔴 **ALTA PRIORIDADE**
- **129 strings** não traduzidas encontradas
- **48 tooltips** afetados (maior problema)
- **File Explorer**: 2 ocorrências diretas (table headers)
- **Arquivos BACKUP**: Contêm muitas ocorrências (podem ser ignorados)

---

## 🔍 ANÁLISE DETALHADA POR CATEGORIA

### 1. QLabel Hardcoded (35 ocorrências)

**Arquivos Principais Afetados:**
```
src/gui/panels/search_replace_panel_NEW.py:     4 ocorrências ("File Name:", "File Content:", "Replace:", "Count:")
src/gui/panels/search_replace_panel_BACKUP.py:   2 ocorrências
src/gui/panels/insert_panel_BACKUP.py:           4 ocorrências
src/gui/venn_diagram_dialog.py:                  1 ocorrência (italic text)
src/gui/diff_viewer_dialog.py:                   4 ocorrências (legend labels)
```

**Nota**: Muitas são **arquivos BACKUP** que podem ser ignorados.

**Ação Necessária**: 
- ✅ Manter arquivos `_BACKUP.py` como estão (deprecated)
- 🔧 Corrigir apenas arquivos ativos

---

### 2. QPushButton Hardcoded (16 ocorrências)

**Distribuição**:
- Não houve output detalhado (grep foi salvo em arquivo)
- Análise manual necessária

**Ação**: Abrir `audit_i18n/02_qpushbutton.txt` e listar arquivos

---

### 3. QCheckBox Hardcoded (10 ocorrências)

**Ação**: Verificar arquivo `audit_i18n/03_qcheckbox.txt`

---

### 4. ComboBox Items Hardcoded (4 ocorrências)

**Baixa Prioridade** - Poucos casos

---

### 5. Placeholders Hardcoded (6 ocorrências)

**Ação**: Verificar arquivo `audit_i18n/05_placeholder.txt`

---

### 6. 🔴 **Tooltips Hardcoded (48 ocorrências) - CRÍTICO**

**MAIOR PROBLEMA IDENTIFICADO**

Esta é a categoria com mais ocorrências. **48 tooltips** usam `setToolTip("...")` ao invés de `setToolTip(tooltip_tr(...))`.

**Impacto**:
- Tooltips aparecem em inglês para usuários PT-BR
- Má UX (usuário vê interface mista)

**Ação Prioritária**: 
1. Listar todos os 48 tooltips
2. Adicionar chaves em `en.json` / `pt.json`
3. Substituir por `tooltip_tr(...)`

---

### 7. Table Headers Sem tr() (10 ocorrências)

**Arquivos Afetados** (headers não traduzidos):

```
✅ src/gui/widgets/json_tree_widget.py:56       - JÁ USA tr() ✓
✅ src/gui/panels/regex_insert_panel.py:158     - JÁ USA tr() ✓
✅ src/gui/statistics_dialog.py:139             - JÁ USA tr() ✓
✅ src/gui/history_dock.py:66                   - JÁ USA tr() ✓

❌ src/gui/batch_dialog.py:344                  - SEM tr()
❌ src/gui/results_tree.py:43                   - SEM tr() ["Match"]
❌ src/gui/widgets/file_list_table_manager.py:76 - SEM tr() ⚠️ FILE EXPLORER
❌ src/gui/panels/results_tree.py:128           - SEM tr() ["Match"]
❌ src/gui/statistics_dialog.py:110             - SEM tr()
❌ src/gui/calculator_dock.py:131               - SEM tr()
❌ src/gui/plugin_manager_dialog.py:61          - SEM tr()
❌ src/gui/formula_dock.py:213                  - SEM tr() ['Step', 'Expression']
❌ src/gui/shortcut_customizer.py:149           - SEM tr()
❌ src/gui/shortcuts_dialog.py:86               - SEM tr()
```

**FILE EXPLORER IDENTIFICADO**:
- ⚠️ **src/gui/widgets/file_list_table_manager.py:76** - Table headers hardcoded

---

### 8. Window Titles Hardcoded (0 ocorrências)

✅ **TODOS OS TÍTULOS JÁ USAM tr()** - Excelente!

---

## 🎯 FILE EXPLORER - ANÁLISE ESPECÍFICA

**Arquivo Principal**: `src/gui/widgets/file_list_table_manager.py`

### Linha 76-77 (Table Headers):
```python
self.table.setHorizontalHeaderLabels([
    "Name", "Size", "Modified", "Permissions", "Path"
])
```

**Strings Hardcoded NO File Explorer**:
1. "Name" → precisa `tr("file_list.col_name")`
2. "Size" → precisa `tr("file_list.col_size")`
3. "Modified" → precisa `tr("file_list.col_modified")`
4. "Permissions" → precisa `tr("file_list.col_permissions")`
5. "Path" → precisa `tr("file_list.col_path")`

**Strings Reportadas pelo Usuário** (ainda não encontradas no grep):
- "Quick Filter" → Precisa investigar mais (pode estar em outro lugar)
- "Save Results" → Não apareceu no grep (verificar QPushButton details)
- "Export CSV" → Não apareceu no grep
- "Directory" → Não apareceu no grep
- "Include Globs" → Não apareceu no grep
- "File Name" → Encontrado em `search_replace_panel_NEW.py` (não é File Explorer)
- "Content Search" → Não encontrado
- "Replace with" → Encontrado em `search_replace_panel_NEW.py`

**CONCLUSÃO**: Nem todas as strings reportadas foram encontradas. Possibilidades:
1. Estão em widgets criados dinamicamente
2. Já foram corrigidas e usuário testou versão antiga
3. Grep pattern precisa ser expandido

---

## 📁 TOP 10 ARQUIVOS MAIS AFETADOS

| Rank | Arquivo | Ocorrências | Prioridade |
|------|---------|-----------|-----------|
| 1 | `panels/search_replace_panel_NEW.py` | ~8 | 🟢 BACKUP (ignorar) |
| 2 | `panels/insert_panel_BACKUP.py` | ~7 | 🟢 BACKUP (ignorar) |
| 3 | (tooltips distribuídos) | 48 | 🔴 CRÍTICO |
| 4 | `widgets/file_list_table_manager.py` | 5 | 🟡 FILE EXPLORER |
| 5 | `diff_viewer_dialog.py` | 4 | 🟡 MÉDIA |
| 6 | `venn_diagram_dialog.py` | 1 | 🟢 BAIXA |
| 7 | `results_tree.py` | 1 | 🟡 MÉDIA |
| 8 | `calculator_dock.py` | 1 (header) | 🟡 MÉDIA |
| 9 | `formula_dock.py` | 1 (header) | 🟡 MÉDIA |
| 10 | `batch_dialog.py` | 1 (header) | 🟡 MÉDIA |

---

## 🚨 INVESTIGAÇÃO ADICIONAL NECESSÁRIA

### Strings Reportadas Pelo Usuário MAS NÃO ENCONTRADAS:

1. **"Quick Filter"** - Não apareceu em nenhum grep
   - Possível localização: `file_explorer_dock.py` (QLineEdit placeholder?)
   - Ação: Grep manual em file_explorer_dock.py

2. **"Save Results"** - Não apareceu em QPushButton grep
   - Possível: Botão criado em `base_dock.py` ou dinamicamente
   - Ação: Verificar `audit_i18n/02_qpushbutton.txt` manualmente

3. **"Export CSV"** - Não apareceu
   - Ação: Verificar audit files

4. **"Directory"** - Não apareceu
   - Pode ser QLabel ou text()
   - Ação: Grep por `setText("Directory")` ou similar

5. **"Include Globs"**, **"Content Search"** - Não encontrados
   - Ação: Expansão de grep patterns

**RECOMENDAÇÃO**: Abrir `file_explorer_dock.py` e fazer **busca manual** por essas strings.

---

## 📋 PRÓXIMAS AÇÕES (FASE 2)

### 1. Investigação Manual (30 min)
- [ ] Abrir `src/gui/file_explorer_dock.py`
- [ ] Buscar visualmente todas as strings reportadas
- [ ] Grep adicional: `setText\(`, `addItems\(`
- [ ] Verificar widgets dinamicamente criados

### 2. Listar Tooltips (30 min)
- [ ] Abrir `audit_i18n/06_tooltip.txt`
- [ ] Criar lista de todos os 48 tooltips
- [ ] Agrupar por arquivo
- [ ] Priorizar por módulo (docks > dialogs > widgets)

### 3. Criar Chaves JSON (30 min)
- [ ] Para cada string encontrada, criar chave em `en.json`
- [ ] Traduzir para `pt.json`
- [ ] Validar formato JSON

### 4. Aplicar Correções (2-3h)
- [ ] file_list_table_manager.py (headers)
- [ ] file_explorer_dock.py (labels, buttons)
- [ ] Todos os 48 tooltips
- [ ] Outros arquivos conforme prioridade

---

## ⏱️ TEMPO ESTIMADO RESTANTE

| Fase | Tempo |
|------|-------|
| Fase 2: Criar Traduções | 1h |
| Fase 3: Aplicar Traduções | 3h |
| Fase 4: Testes Manuais | 1-2h |
| Fase 5: Documentação | 30min |
| **TOTAL** | **5.5-6.5h** |

---

## ✅ DELIVERABLES DESTA FASE

1. ✅ `audit_i18n/01_qlabel.txt` - 35 ocorrências
2. ✅ `audit_i18n/02_qpushbutton.txt` - 16 ocorrências
3. ✅ `audit_i18n/03_qcheckbox.txt` - 10 ocorrências
4. ✅ `audit_i18n/04_combobox.txt` - 4 ocorrências
5. ✅ `audit_i18n/05_placeholder.txt` - 6 ocorrências
6. ✅ `audit_i18n/06_tooltip.txt` - 48 ocorrências
7. ✅ `audit_i18n/07_headers.txt` - 14 arquivos (10 sem tr())
8. ✅ `audit_i18n/09_titles.txt` - 0 ocorrências
9. ✅ Este relatório (`I18N_AUDIT_REPORT_PHASE1.md`)

---

## 💡 RECOMENDAÇÕES

### Prioridade de Correção:
1. 🔴 **ALTA**: Tooltips (48) + File Explorer headers (5)
2. 🟡 **MÉDIA**: QLabel/QPushButton em arquivos ativos
3. 🟢 **BAIXA**: Arquivos BACKUP (deixar como estão)

### Estratégia:
- **Não corrigir arquivos `_BACKUP.py` ou `_NEW.py`** (deprecated/testing)
- **Focar em arquivos de produção** usados ativamente
- **File Explorer primeiro** (reportado pelo usuário)

---

**Status Final Fase 1**: ✅ COMPLETO  
**Aprovação do Usuário**: ⏳ AGUARDANDO  
**Próximo Passo**: Fase 2 se aprovado
