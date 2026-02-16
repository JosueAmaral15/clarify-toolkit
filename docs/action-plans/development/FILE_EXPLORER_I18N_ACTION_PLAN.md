# File Explorer i18n Action Plan
**Data:** 2026-01-04  
**Objetivo:** Completar 100% da tradução do File Explorer

## 📋 FASE 1: AUDITORIA COMPLETA

### Task 1.1: Identificar Strings Hardcoded
**Status:** 🔴 Pendente

**Arquivos a auditar:**
- [ ] `src/gui/panels/file_explorer_panel.py`
- [ ] `src/gui/panels/file_filter_panel.py`
- [ ] `src/gui/panels/file_explorer_table.py`
- [ ] `src/gui/panels/file_explorer_tree.py`
- [ ] `src/core/file_operations.py` (se aplicável)

**Método:**
```bash
# Procurar setText, setTitle, setLabel, setPlaceholderText com strings literais
grep -n 'setText\|setTitle\|setLabel\|setPlaceholderText\|setHeaderLabels' src/gui/panels/file_*.py | grep '"'
```

**Resultado esperado:** Lista completa de strings não traduzidas

---

### Task 1.2: Verificar Tooltips
**Status:** 🔴 Pendente

**Método:**
```bash
grep -n 'setToolTip' src/gui/panels/file_*.py | grep -v 'tooltip_tr\|tr('
```

**Resultado esperado:** Lista de tooltips sem i18n

---

### Task 1.3: Verificar Mensagens/Diálogos
**Status:** 🔴 Pendente

**Método:**
```bash
grep -n 'QMessageBox\|showMessage\|setWindowTitle' src/gui/panels/file_*.py | grep '"'
```

---

## 📋 FASE 2: CRIAÇÃO DE KEYS I18N

### Task 2.1: Adicionar Keys em en.json
**Status:** 🔴 Pendente

**Arquivo:** `config/locales/en.json`

**Estrutura esperada:**
```json
{
  "file_explorer": {
    "panel_title": "File Explorer",
    "filters": {
      "extensions_label": "Extensions",
      "use_extension_filter": "Use Extension Filter",
      ...
    },
    "table": {
      "column_name": "Name",
      "column_size": "Size",
      ...
    }
  }
}
```

---

### Task 2.2: Adicionar Traduções em pt_BR.json
**Status:** 🔴 Pendente

---

## 📋 FASE 3: IMPLEMENTAÇÃO

### Task 3.1: Substituir Strings Hardcoded
**Status:** 🔴 Pendente

**Para cada string identificada:**
1. Criar key i18n apropriada
2. Substituir `"texto"` por `tr("file_explorer.key")`
3. Adicionar import se necessário: `from ...utils.i18n import tr, tooltip_tr`

---

### Task 3.2: Teste Manual
**Status:** 🔴 Pendente

**Checklist:**
- [ ] Iniciar aplicação em inglês
- [ ] Verificar todos os labels
- [ ] Verificar todos os tooltips
- [ ] Trocar para português
- [ ] Verificar tradução completa
- [ ] Testar todos os botões e ações

---

## 📋 FASE 4: DOCUMENTAÇÃO

### Task 4.1: Atualizar Documentação
**Status:** 🔴 Pendente

- [ ] Documentar mudanças em CHANGELOG
- [ ] Atualizar I18N_COMPLETION_SUMMARY
- [ ] Registrar keys adicionadas

---

## 🎯 PROTOCOLO SIMPLICIDADE 3

### Etapa 1: Investigação ✅
- Criar este plano de ação

### Etapa 2: Planejamento
- Dividir em tasks pequenas e testáveis

### Etapa 3-7: Execução
- Executar cada task
- Testar antes de próxima
- Documentar

---

## 📊 PROGRESSO GERAL
- [x] Fase 1: Auditoria ✅ **COMPLETA**
- [x] Fase 2: Keys i18n ✅ **JÁ EXISTENTES**
- [x] Fase 3: Implementação ✅ **JÁ IMPLEMENTADO**
- [ ] Fase 4: Documentação

---

## ✅ RESULTADO DA AUDITORIA REAL (2026-01-04 18:00)

### ⚠️ AUDITORIA ANTERIOR ESTAVA **ERRADA** - NOVA INVESTIGAÇÃO HONESTA

### Strings Hardcoded Encontradas: **5+** ❌

#### 1. **CSV Headers NÃO traduzidos** ❌
**Arquivo:** `src/gui/widgets/file_list_table_manager.py:321`
```python
writer.writerow(["Name", "Size", "Modified", "Permissions", "Path"])
```

#### 2. **"Save Results" button** ❌
**Arquivos:**
- `src/gui/json_search_dock.py:147`
- `src/gui/ai_processor_dock.py:308`
- `src/gui/set_operations_dock.py:324`

#### 3. **"No File" warning** ❌
**Arquivo:** `src/gui/set_operations_dock.py:458`
```python
self.show_warning("No File", "No valid file selected to merge into.")
```

### 🔍 RESULTADO INVESTIGAÇÃO PROFUNDA (18:05):

#### ✅ STRINGS JÁ TRADUZIDAS (File Explorer):
- ✅ "Name", "Size", "Modified", "Permissions", "Path" - **linha 76-81 file_list_table_manager.py** (usando `tr("table_manager.header_*")`)
- ✅ "Quick Filter" - **linha 64** (usando `tr("table_manager.quick_filter")`)
- ✅ "Export CSV" / "Export to CSV" - **linha 559** file_explorer_dock.py (usando `tr("file_list.btn_export_csv")`)
- ✅ "Save Results" - **linha 552** (usando `tr("file_list.btn_save_results")`)

#### ❌ STRINGS HARDCODED ENCONTRADAS:

**1. CSV Export Headers (NÃO traduzidos):**  
`src/gui/widgets/file_list_table_manager.py:321`
```python
writer.writerow(["Name", "Size", "Modified", "Permissions", "Path"])
```
**Problema:** Headers da tabela usam `tr()` mas o CSV export usa strings hardcoded!

**2. "Save Results" em outros docks:**
- `src/gui/json_search_dock.py:147` - ❌ hardcoded
- `src/gui/ai_processor_dock.py:308` - ❌ hardcoded

**3. "No File" warning:**
- `src/gui/set_operations_dock.py:458` - ❌ hardcoded

**4. "Max Depth:" labels:**
- `src/gui/calculator_dock.py:73` - ❌ hardcoded
- `src/gui/operation_preview_dialog.py:175` - ❌ hardcoded
- `src/gui/recall_dialog.py:144` - ❌ hardcoded

**5. "Export CSV" em statistics:**
- `src/gui/statistics_dialog.py:77` - ❌ hardcoded
- `src/gui/statistics_dialog.py:236` - ❌ hardcoded (dialog title)

#### 🔍 STRINGS NÃO ENCONTRADAS (não existem no código File Explorer):
- ❌ "Include Globs" - não encontrado literalmente
- ❌ "No File Listed" - não encontrado
- ❌ "Options", "Case Sensitive", "Whole Word", "Preserve Case", "Extensions", "Modified After", "contains" - não são strings hardcoded, são nomes de variáveis/classes ou já traduzidos

### Conclusão:
🟡 **File Explorer Dock está ~95% traduzido**, mas **CSV export** e **outros docks** têm strings hardcoded.

**Próxima ação:** Corrigir 5 problemas identificados
