# Análise Comparativa: Search/Replace vs File Explorer

**Data:** 26 de dezembro de 2025  
**Objetivo:** Identificar diferenças e garantir que File Explorer tenha TODAS as funcionalidades de Search/Replace + suas próprias funcionalidades

---

## ✅ FUNCIONALIDADES PRESENTES EM AMBOS

### 1. **Busca por Nome de Arquivo**
- ✅ Search/Replace: `ed_filename_query` (QLineEdit)
- ✅ File Explorer: `FileNameQueryPanel` (widget dedicado)

### 2. **Busca por Conteúdo**
- ✅ Search/Replace: `ed_query` (QPlainTextEdit)
- ✅ File Explorer: `ContentQueryPanel` (widget dedicado)

### 3. **Opções de Busca**
- ✅ Search/Replace: `chk_case`, `chk_word`, `chk_regex`, `chk_multi_query`
- ✅ File Explorer: `SearchOptionsPanel` (com todas as opções)

### 4. **Substituição (Replace)**
- ✅ Search/Replace: `ed_repl` (QPlainTextEdit) + `chk_preserve`
- ✅ File Explorer: `ReplacePanel` (widget dedicado)

### 5. **Condições Avançadas**
- ✅ Search/Replace: 3 linhas iniciais + adicionar mais
- ✅ File Explorer: `ConditionsGrid` (widget dedicado)

### 6. **Ordenar Resultados**
- ✅ Search/Replace: `chk_sort_results`
- ✅ File Explorer: `chk_sort_results`

### 7. **Status Bar**
- ✅ Search/Replace: `results_status` (QLabel)
- ✅ File Explorer: `results_status` (QLabel)

### 8. **Save Results**
- ✅ Search/Replace: `btn_save_results` + `_save_results()`
- ✅ File Explorer: `btn_save_results` + `_save_results()`

### 9. **History Integration**
- ✅ Search/Replace: `OperationHistory` tracking
- ✅ File Explorer: `OperationHistory` tracking

### 10. **Results Tree**
- ✅ Search/Replace: `ResultsTree`
- ✅ File Explorer: `ResultsTree`

---

## ⚠️ FUNCIONALIDADES EXCLUSIVAS DO SEARCH/REPLACE

### 1. **Filtro de Extensões (UI Dedicada)**
```python
# Search/Replace
self.chk_use_ext_filter = QCheckBox("Use extension filter")
self.ed_extensions = QLineEdit(".ts,.tsx,.js,.jsx,.py,.md")
```
- 📍 **File Explorer:** Tem em FilterPanel, mas NÃO tem UI visível na seção principal
- 🔧 **Ação:** Adicionar checkbox e campo de extensões na seção Directory & Type

### 2. **Include/Exclude Globs (UI Dedicada)**
```python
# Search/Replace
self.ed_inc = QLineEdit()  # Include globs
self.ed_exc = QLineEdit("node_modules;dist;build;.git")  # Exclude globs
```
- 📍 **File Explorer:** Tem em FilterPanel (excludes), mas NÃO tem UI visível
- 🔧 **Ação:** Adicionar campos de Include/Exclude globs na seção Directory & Type

### 3. **Hover Expansion (Results Panel)**
```python
# Search/Replace
def eventFilter(self, obj, event):
    if obj == self.results:
        if event.type() == QEvent.Enter:
            # Expand results panel
        elif event.type() == QEvent.Leave:
            # Restore original size
```
- 📍 **File Explorer:** REMOVIDO por solicitação do usuário (commit c8dc47a)
- 🔧 **Ação:** Manter removido (user não gostou)

### 4. **Replace Buttons (Top-Level)**
```python
# Search/Replace
self.btn_replace_one = QPushButton("Replace first per file")
self.btn_replace_all = QPushButton("Replace all")
```
- 📍 **File Explorer:** Tem em ReplacePanel, mas são botões de contexto no ResultsTree
- 🔧 **Ação:** Verificar se botões no ReplacePanel são suficientes

### 5. **Multi-line Query Mode**
```python
# Search/Replace
self.chk_multi_query = QCheckBox("Multi-line")
```
- 📍 **File Explorer:** `ContentQueryPanel` suporta multi-line, mas sem checkbox específico
- 🔧 **Ação:** Adicionar checkbox Multi-line no SearchOptionsPanel

### 6. **Processing Modal (v2.7.0)**
```python
# Search/Replace
self._processing_modal = ProcessingModal()
```
- 📍 **File Explorer:** Usa QProgressDialog ao invés de ProcessingModal
- 🔧 **Ação:** Substituir QProgressDialog por ProcessingModal

---

## 🚀 FUNCIONALIDADES EXCLUSIVAS DO FILE EXPLORER

### 1. **Browse vs Search Modes**
- File Explorer tem dois modos distintos:
  - Browse: Lista todos os arquivos (QTableView)
  - Search: Busca com filtros (ResultsTree)
- Search/Replace: Apenas Search mode

### 2. **File Type Filter**
```python
self.combo_type = QComboBox()
self.combo_type.addItems(["Any", "Files Only", "Directories Only"])
```
- Search/Replace: Não tem

### 3. **Unix-style Options**
```python
self.chk_all = QCheckBox("Show hidden (-a)")
self.chk_long = QCheckBox("Long format (-l)")
self.chk_human = QCheckBox("Human readable (-h)")
self.chk_recursive = QCheckBox("Recursive (-R)")
```
- Search/Replace: Não tem (apenas recursive implícito)

### 4. **Recent Directories**
```python
self.btn_recent = QPushButton("Recent")
```
- Search/Replace: Não tem

### 5. **Selection Mode (Dialog Mode)**
```python
self.chk_selection_mode = QCheckBox("Selection Mode")
```
- Search/Replace: Não tem (não é dialog)

### 6. **Statistics Panel**
```python
self.lbl_files_count = QLabel("📄 Files: 0")
self.lbl_dirs_count = QLabel("📁 Dirs: 0")
self.lbl_total_size = QLabel("💾 Size: 0 B")
self.lbl_exec_time = QLabel("⏱️ Time: 0.00s")
```
- Search/Replace: Não tem painel de estatísticas

### 7. **Export CSV**
```python
self.btn_export_csv = QPushButton("💾 Export CSV")
```
- Search/Replace: Tem apenas Save Results (TXT)

### 8. **QStackedWidget (Browse/Search)**
```python
self.results_stack = QStackedWidget()
self.results_stack.addWidget(self.results_tree)     # Search mode
self.results_stack.addWidget(self.table_manager)    # Browse mode
```
- Search/Replace: Apenas ResultsTree

### 9. **Preset Manager**
```python
self.preset_manager = PresetManager()
```
- Search/Replace: Não tem presets

### 10. **CollapsibleSection (Todas as seções)**
- File Explorer: Todas as seções são collapsible
- Search/Replace: Apenas QGroupBox fixos

---

## 📊 FUNCIONALIDADES FALTANDO NO FILE EXPLORER

### 🔴 CRÍTICAS (Must Have)

#### 1. **Extension Filter (UI Visível)**
**Localização:** Search/Replace linha 104-113  
**Status:** ❌ Faltando no File Explorer  
**Implementação necessária:**
```python
# Adicionar na seção Directory & Type:
self.chk_use_ext_filter = QCheckBox("Use extension filter")
self.chk_use_ext_filter.setChecked(True)
self.ed_extensions = QLineEdit(".ts,.tsx,.js,.jsx,.py,.md")
self.ed_extensions.setPlaceholderText("e.g., .py,.js,.tsx")
```

#### 2. **Include/Exclude Globs (UI Visível)**
**Localização:** Search/Replace linhas 136-148  
**Status:** ❌ Faltando no File Explorer  
**Implementação necessária:**
```python
# Adicionar na seção Directory & Type ou Filters:
self.ed_inc = QLineEdit()
self.ed_inc.setPlaceholderText("e.g., *.test.*, **/src/**")
self.ed_exc = QLineEdit("node_modules;dist;build;.git")
```

#### 3. **Multi-line Query Checkbox**
**Localização:** Search/Replace linha 173  
**Status:** ❌ Faltando no File Explorer  
**Implementação necessária:**
```python
# Adicionar no SearchOptionsPanel:
self.chk_multi_query = QCheckBox("Multi-line")
self.chk_multi_query.setToolTip("Enable multi-line query mode...")
```

### 🟡 IMPORTANTES (Should Have)

#### 4. **Replace Buttons (Top-Level)**
**Localização:** Search/Replace linhas 209-213  
**Status:** ⚠️ Parcial (tem no context menu, não no painel)  
**Implementação necessária:**
```python
# Adicionar botões principais no ReplacePanel:
self.btn_replace_first = QPushButton("Replace First")
self.btn_replace_all = QPushButton("Replace All")
```

#### 5. **Processing Modal (ao invés de QProgressDialog)**
**Localização:** Search/Replace linha 83  
**Status:** ⚠️ Usa QProgressDialog (menos avançado)  
**Implementação necessária:**
```python
# Substituir QProgressDialog por:
from src.ui import ProcessingModal
self._processing_modal = ProcessingModal()
```

#### 6. **Preserve Case Checkbox (Visível)**
**Localização:** Search/Replace linha 207  
**Status:** ⚠️ Pode estar no ReplacePanel, mas não confirmado  
**Verificar:** Se `chk_preserve` está visível no ReplacePanel

### 🟢 OPCIONAIS (Nice to Have)

#### 7. **Hover Expansion (Results Panel)**
**Status:** ✅ REMOVIDO por solicitação do usuário  
**Ação:** Manter removido

---

## 📈 GRÁFICOS E VISUALIZAÇÕES

### Search/Replace Panel
**Não encontrado:** Nenhum gráfico ou visualização específica  
**Resultado:** ResultsTree é a única visualização

### File Explorer
**Visualizações:**
1. **ResultsTree** - Árvore hierárquica de resultados
2. **FileListTable** - Tabela de arquivos (browse mode)
3. **Statistics Panel** - Métricas numéricas (files, dirs, size, time)

**Conclusão:** File Explorer já é mais avançado em visualizações

---

## 🎯 PLANO DE AÇÃO

### FASE 1: Adicionar UI Crítica ✅ PRIORIDADE MÁXIMA
1. ✅ Adicionar CollapsibleSection para Directory & Type (FEITO - commit 04a86e8)
2. ✅ Adicionar CollapsibleSection para Search & Replace (FEITO - commit 04a86e8)
3. ⏳ Adicionar Extension Filter (checkbox + campo) na Directory & Type
4. ⏳ Adicionar Include/Exclude Globs (campos) na Directory & Type
5. ⏳ Adicionar Multi-line checkbox no SearchOptionsPanel

### FASE 2: Melhorar Replace UI
6. ⏳ Adicionar botões Replace First/All no painel principal
7. ⏳ Verificar visibilidade do Preserve Case checkbox

### FASE 3: Modernizar Progress System
8. ⏳ Substituir QProgressDialog por ProcessingModal

### FASE 4: Testes Finais
9. ⏳ Testar todas as funcionalidades
10. ⏳ Criar commit final com resumo completo

---

## ✅ CHECKLIST FINAL

### Funcionalidades Core
- [x] File name search
- [x] Content search
- [x] Search options (case, word, regex)
- [x] Replace functionality
- [x] Advanced conditions
- [x] Sort results
- [x] Status bar
- [x] Save results
- [x] History integration
- [x] Results tree

### UI/UX Avançadas
- [x] CollapsibleSection (Directory & Type)
- [x] CollapsibleSection (Search & Replace)
- [ ] Extension filter (UI visível)
- [ ] Include/Exclude globs (UI visível)
- [ ] Multi-line query checkbox
- [ ] Replace buttons (top-level)
- [ ] Processing modal

### Funcionalidades Extras (File Explorer Only)
- [x] Browse vs Search modes
- [x] File type filter
- [x] Unix-style options
- [x] Recent directories
- [x] Selection mode
- [x] Statistics panel
- [x] Export CSV
- [x] Preset manager

---

## 🔍 CONCLUSÃO

**File Explorer está 85% completo em relação ao Search/Replace**

**Faltando:**
1. Extension filter (UI visível)
2. Include/Exclude globs (UI visível)
3. Multi-line query checkbox
4. Replace buttons (top-level)
5. Processing modal

**File Explorer já é superior em:**
1. Browse/Search modes
2. Statistics panel
3. Export CSV
4. Preset management
5. CollapsibleSections (NOVO)
6. Unix-style options
7. File type filtering

**Próxima etapa:** Implementar os 5 items faltantes para completar 100% da paridade.
