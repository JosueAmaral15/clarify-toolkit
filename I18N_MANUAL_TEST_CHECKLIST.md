# 🧪 TASK 9: MANUAL TESTING CHECKLIST
**Generated**: 2026-01-02
**Tester**: User (Josué)
**Language**: PT-BR
**Goal**: Verify ALL i18n translations work correctly in GUI

---

## ✅ PRE-TEST VALIDATION (Automated)

### 1. JSON Files Integrity
- [ ] en.json loads without errors
- [ ] pt_BR.json loads without errors
- [ ] All keys in en.json have pt_BR counterpart
- [ ] No duplicate keys found

### 2. Code Validation
- [ ] No hardcoded tooltips in active files
- [ ] No hardcoded QLabels in active files
- [ ] No hardcoded headers in active files
- [ ] No hardcoded placeholders in active files
- [ ] No hardcoded ComboBox items in active files

---

## 📋 GUI MANUAL TESTS

### TASK 1: TOOLTIPS (26 items) - Priority: HIGH

#### Batch Dialog (11 tooltips)
**How to test**: Menu > Tools > Batch Operations
- [ ] Hover "Add Step" button → Shows tooltip in PT-BR
- [ ] Hover "Edit Step" button → Shows tooltip in PT-BR
- [ ] Hover "Remove Step" button → Shows tooltip in PT-BR
- [ ] Hover "Save Intermediate" checkbox → Shows tooltip in PT-BR
- [ ] Hover "Output Folder" field → Shows tooltip in PT-BR
- [ ] Hover "Browse Output" button → Shows tooltip in PT-BR
- [ ] Hover "Save Batch" button → Shows tooltip in PT-BR
- [ ] Hover "Load Batch" button → Shows tooltip in PT-BR
- [ ] Hover "Execute" button → Shows tooltip in PT-BR
- [ ] Hover "Cancel Exec" button → Shows tooltip in PT-BR
- [ ] Hover "Close" button → Shows tooltip in PT-BR

#### Operation Preview Dialog (3 tooltips)
**How to test**: Execute any operation > Preview result
- [ ] Hover "Memory Slot" dropdown → Shows tooltip in PT-BR
- [ ] Hover "Store" button → Shows tooltip in PT-BR
- [ ] Hover "Discard" button → Shows tooltip in PT-BR

#### Tutorial Assistant (2 tooltips)
**How to test**: Help > Tutorial Assistant
- [ ] Hover thumbs-up button → Shows "Resposta útil"
- [ ] Hover thumbs-down button → Shows "Resposta não útil"

#### Insert Panel (6 tooltips)
**How to test**: Tools > Insert Text
- [ ] Hover "Clear Conditions" button → PT-BR
- [ ] Hover "Save Results" button → PT-BR
- [ ] Hover "Case Sensitive" checkbox → PT-BR
- [ ] Hover "Whole Word" checkbox → PT-BR
- [ ] Hover "Regex" checkbox → PT-BR
- [ ] Hover "Remove Condition" button → PT-BR

#### Progress Manager (3 tooltips)
**How to test**: Execute long operation (e.g., File Explorer search)
- [ ] Hover "Toggle" button → PT-BR
- [ ] Hover "Pause" button → PT-BR
- [ ] Hover "Resume" button → PT-BR

---

### TASK 3: QLABELS (10 items) - Priority: MEDIUM

#### Venn Diagram Dialog (1 label)
**How to test**: Tools > Set Operations > Venn Diagram
- [ ] See instruction text in PT-BR: "Clique em uma região..."

#### Diff Viewer Dialog (4 labels)
**How to test**: Tools > Diff Viewer
- [ ] Legend shows "Apenas em A" (not "Only in A")
- [ ] Legend shows "Apenas em B" (not "Only in B")
- [ ] Legend shows "Comum" (not "Common")
- [ ] Legend shows "Modificado" (not "Modified")

#### Transparency Dialog (2 labels)
**How to test**: View > Transparency
- [ ] Min label shows "0%"
- [ ] Max label shows "100%"

#### Progress Dialogs (3 labels)
**How to test**: Execute operation with progress
- [ ] Progress Manager header: "Tarefas Ativas (N)"
- [ ] Progress Details header: "Detalhes do Processamento:"
- [ ] Update notification: "Nova Versão Disponível!"

---

### TASK 5: TABLE HEADERS (21 items) - Priority: HIGH

#### Batch Dialog Table (7 headers)
**How to test**: Tools > Batch Operations > Add steps
- [ ] Column 1: "#" (OK, number)
- [ ] Column 2: "Descrição" (not "Description")
- [ ] Column 3: "Operação" (not "Operation")
- [ ] Column 4: "Arquivo A" (not "File A")
- [ ] Column 5: "Arquivo B" (not "File B")
- [ ] Column 6: "Modo" (not "Mode")
- [ ] Column 7: "Status" (OK, same in both)

#### Statistics Dialog (6 headers)
**How to test**: Tools > Statistics (if available)
- [ ] "Tipo de Operação" (not "Operation Type")
- [ ] "Chave Original" (not "Original Key")
- [ ] "Chave Mantida" (not "Kept Key")
- [ ] "Similaridade %" (not "Similarity %")
- [ ] "Números de Linha" (not "Line Numbers")
- [ ] "Contagem" (not "Count")

#### Shortcut Customizer (5 headers)
**How to test**: Settings > Customize Shortcuts
- [ ] "Ação" (not "Action")
- [ ] "Descrição" (not "Description")
- [ ] "Padrão" (not "Default")
- [ ] "Personalizado" (not "Custom")
- [ ] "Status" (OK, same)

#### Results Tree (1 header)
**How to test**: Execute search with matches
- [ ] Header shows "Correspondência" (not "Match")

#### Formula Dock (2 headers)
**How to test**: Tools > Formula Calculator
- [ ] "Etapa" (not "Step")
- [ ] "Expressão" (not "Expression")

---

### TASK 7: PLACEHOLDERS (88 items) - Priority: LOW
**Note**: Already 100% translated. Spot check recommended.

#### File Explorer (spot check 5)
**How to test**: Tools > File Explorer
- [ ] Directory field placeholder in PT-BR
- [ ] File name field placeholder in PT-BR
- [ ] Content search field placeholder in PT-BR
- [ ] Replace field placeholder in PT-BR
- [ ] Include globs field placeholder in PT-BR

---

### TASK 8: COMBOBOX (4 items) - Priority: MEDIUM

#### Operation Preview (1 item)
**How to test**: Execute operation when NO slots available
- [ ] Dropdown shows "(Nenhum slot disponível)"

#### History Dialog (1 item)
**How to test**: Open history when empty
- [ ] List shows "(Nenhuma operação no histórico)"

#### Presets Dialog (1 item)
**How to test**: Open presets when empty
- [ ] List shows "(Nenhuma predefinição salva)"

#### Google Translate (1 item)
**How to test**: Tools > Google Translate
- [ ] Language dropdown has "Detectar automaticamente"

---

## 🐛 FILE EXPLORER SPECIFIC TESTS (User Reported Issues)

### Advanced Filters
**How to test**: File Explorer > Enable Advanced Filters
- [ ] Size max filter WORKS (< 30 KB filters correctly)
- [ ] Size min filter WORKS
- [ ] Extension filter WORKS
- [ ] Date modified filter WORKS
- [ ] All conditions apply BEFORE content search (early optimization)

### Table View
**How to test**: File Explorer > View: Table (files)
- [ ] "Quick Filter" label translated to PT-BR
- [ ] Column "Name" → "Nome"
- [ ] Column "Size" → "Tamanho"
- [ ] Column "Modified" → "Modificado"
- [ ] Column "Permissions" → "Permissões"
- [ ] Column "Path" → "Caminho"
- [ ] Button "Save Results" → "Salvar Resultados"
- [ ] Button "Export CSV" → "Exportar CSV"

### Filter Panel
**How to test**: File Explorer > Filters section
- [ ] "Directory" label → "Diretório"
- [ ] "Include Globs" label in PT-BR
- [ ] "File Name" label → "Nome do Arquivo"
- [ ] "Content Search" label → "Busca de Conteúdo"
- [ ] "Replace with" label → "Substituir por"

### Search/Replace Tool
**How to test**: Tools > Search/Replace
- [ ] Tool appears in menu context
- [ ] All GUI elements visible and translated
- [ ] Functionality works correctly

---

## ✅ POST-TEST VALIDATION

### Regression Tests
- [ ] NO crashes during testing
- [ ] NO missing translations (empty strings)
- [ ] NO mixed language (EN + PT in same screen)
- [ ] Tooltips appear within 1 second of hover
- [ ] All buttons remain clickable after i18n
- [ ] No layout issues (text overflow, cut-off)

### Performance
- [ ] Application startup time < 5 seconds
- [ ] Switching language doesn't require restart
- [ ] No memory leaks during testing session

---

## 📊 TEST SUMMARY

**Total Test Items**: ~100
**Critical Items**: 26 tooltips + 21 headers + 4 combobox = 51
**Medium Priority**: 10 QLabels + File Explorer = ~20
**Low Priority**: 88 placeholders (spot check) = ~10

**Estimated Time**: 1-2 hours
**Pass Criteria**: ≥95% items pass (≤5 failures acceptable)

---

## 📝 RESULTS (To be filled by tester)

**Date Tested**: _______________
**Time Spent**: _______________
**Items Passed**: ___ / 100
**Items Failed**: ___
**Critical Bugs**: ___
**Notes**:
