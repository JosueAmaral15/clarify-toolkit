# 📚 Exemplos Detalhados de Traduções Pendentes

**Complemento de:** [REMAINING_TRANSLATIONS.md](REMAINING_TRANSLATIONS.md)  
**Data:** 2025-12-30

---

## 🔴 FASE 33: Botões com Emojis (Prioridade Alta)

### recall_dialog.py (3 botões)

#### Localização: Linhas 100-112
```python
# 🔴 ANTES (hardcoded):
self.btn_export = QPushButton("📤 Export to File")
self.btn_copy = QPushButton("📋 Copy to Clipboard")
self.btn_send = QPushButton("🔄 Send to Set Operations")

# ✅ DEPOIS (traduzido):
self.btn_export = QPushButton(f"📤 {tr('recall_dialog.btn_export')}")
self.btn_copy = QPushButton(f"📋 {tr('recall_dialog.btn_copy')}")
self.btn_send = QPushButton(f"🔄 {tr('recall_dialog.btn_send')}")
```

#### JSON (pt_BR.json):
```json
"recall_dialog.btn_export": "Exportar para Arquivo",
"recall_dialog.btn_copy": "Copiar para Área de Transferência",
"recall_dialog.btn_send": "Enviar para Operações de Conjunto"
```

---

### plugin_manager_dialog.py (2 botões)

#### Localização: Linhas 81-83
```python
# 🔴 ANTES:
btn_refresh = QPushButton("🔄 Refresh")
btn_close = QPushButton("✅ Close")

# ✅ DEPOIS:
btn_refresh = QPushButton(f"🔄 {tr('plugin_manager.btn_refresh')}")
btn_close = QPushButton(f"✅ {tr('plugin_manager.btn_close')}")
```

#### JSON:
```json
"plugin_manager.btn_refresh": "Atualizar",
"plugin_manager.btn_close": "Fechar"
```

---

### diff_viewer_dialog.py (1 botão)

#### Localização: Linha 192
```python
# 🔴 ANTES:
self.btn_export = QPushButton("📤 Export HTML")

# ✅ DEPOIS:
self.btn_export = QPushButton(f"📤 {tr('diff_viewer.btn_export')}")
```

#### JSON:
```json
"diff_viewer.btn_export": "Exportar HTML"
```

---

### venn_diagram_dialog.py (1 botão)

#### Localização: Linha 214
```python
# 🔴 ANTES:
btn_export_svg = QPushButton("💾 Export SVG")

# ✅ DEPOIS:
btn_export_svg = QPushButton(f"💾 {tr('venn_diagram.btn_export_svg')}")
```

#### JSON:
```json
"venn_diagram.btn_export_svg": "Exportar SVG"
```

---

### progress/progress_bar_widget.py (3 botões)

#### Localização: Linhas 58, 66, 73
```python
# 🔴 ANTES:
self.btn_pause = QPushButton("⏸")
self.btn_expand = QPushButton("↗")
self.btn_close = QPushButton("✖")

# ✅ DEPOIS:
self.btn_pause = QPushButton("⏸")  # Apenas emoji - não traduz texto
self.btn_expand = QPushButton("↗")  # Apenas emoji - não traduz texto
self.btn_close = QPushButton("✖")   # Apenas emoji - não traduz texto

# Mas adicionar tooltips traduzidos:
self.btn_pause.setToolTip(tooltip_tr("progress_bar.tooltip_pause"))
self.btn_expand.setToolTip(tooltip_tr("progress_bar.tooltip_expand"))
self.btn_close.setToolTip(tooltip_tr("progress_bar.tooltip_close"))
```

**Nota:** Estes botões têm APENAS emoji, sem texto. A tradução vai nos tooltips!

---

### progress/progress_details_dialog.py (2 botões)

#### Localização: Linhas 68, 72
```python
# 🔴 ANTES:
self.btn_pause = QPushButton("⏸ Pause")
self.btn_cancel = QPushButton("✖ Cancel Task")

# ✅ DEPOIS:
self.btn_pause = QPushButton(f"⏸ {tr('progress_details.btn_pause')}")
self.btn_cancel = QPushButton(f"✖ {tr('progress_details.btn_cancel')}")
```

#### JSON:
```json
"progress_details.btn_pause": "Pausar",
"progress_details.btn_cancel": "Cancelar Tarefa"
```

---

### update_notification_dialog.py (1 botão)

#### Localização: Linha 89
```python
# 🔴 ANTES:
self.btn_download = QPushButton("📥 Download Update")

# ✅ DEPOIS:
self.btn_download = QPushButton(f"📥 {tr('update_notification.btn_download')}")
```

#### JSON:
```json
"update_notification.btn_download": "Baixar Atualização"
```

---

### panels/search_replace_panel.py (1 botão)

#### Localização: Linha 447
```python
# 🔴 ANTES:
btn_remove = QPushButton("✖")

# ✅ DEPOIS:
btn_remove = QPushButton("✖")  # Apenas emoji
# Adicionar tooltip:
btn_remove.setToolTip(tooltip_tr("search_replace.tooltip_remove_condition"))
```

---

## 🟡 FASE 34: Placeholders

### batch_dialog.py (3 exemplos)

#### Localização: Linhas 85, 116, 378
```python
# 🔴 ANTES:
self.ed_file_a.setPlaceholderText("Path to File A (if from file)")
self.ed_file_b.setPlaceholderText("Path to File B")
self.ed_output_folder.setPlaceholderText("Output folder (if saving intermediate)")

# ✅ DEPOIS:
self.ed_file_a.setPlaceholderText(tr("batch_dialog.placeholder_file_a"))
self.ed_file_b.setPlaceholderText(tr("batch_dialog.placeholder_file_b"))
self.ed_output_folder.setPlaceholderText(tr("batch_dialog.placeholder_output"))
```

#### JSON:
```json
"batch_dialog.placeholder_file_a": "Caminho para o Arquivo A (se de arquivo)",
"batch_dialog.placeholder_file_b": "Caminho para o Arquivo B",
"batch_dialog.placeholder_output": "Pasta de saída (se salvando intermediários)"
```

---

### tutorial_assistant_dialog.py

#### Localização: Linha 99
```python
# 🔴 ANTES:
self.input_field.setPlaceholderText("Type your question here...")

# ✅ DEPOIS:
self.input_field.setPlaceholderText(tr("tutorial_assistant.placeholder_question"))
```

#### JSON:
```json
"tutorial_assistant.placeholder_question": "Digite sua pergunta aqui..."
```

---

### advanced_extractor_dock.py (2 exemplos)

#### Localização: Linhas 158, 273
```python
# 🔴 ANTES:
self.extensions_edit.setPlaceholderText(".tsx .jsx .js")
self.avoid_keys_edit.setPlaceholderText("div, span, test")

# ✅ DEPOIS:
self.extensions_edit.setPlaceholderText(tr("advanced_extractor.placeholder_extensions"))
self.avoid_keys_edit.setPlaceholderText(tr("advanced_extractor.placeholder_avoid_keys"))
```

#### JSON:
```json
"advanced_extractor.placeholder_extensions": ".tsx .jsx .js",
"advanced_extractor.placeholder_avoid_keys": "div, span, test"
```

---

### panels/search_replace_panel.py (5 exemplos)

#### Localização: Linhas 113, 132, 150, 161, 433
```python
# 🔴 ANTES:
self.ed_extensions.setPlaceholderText("e.g., .py,.js,.tsx (leave empty for all)")
self.ed_inc.setPlaceholderText("e.g., *.test.*, **/src/** (leave empty for all)")
self.ed_filename_query.setPlaceholderText("Search in file names (e.g., test_*.py)")
self.ed_query.setPlaceholderText("Search in file contents")
ed_scope_val.setPlaceholderText("e.g., 'begin,end' or 'div'")

# ✅ DEPOIS:
self.ed_extensions.setPlaceholderText(tr("search_replace.placeholder_extensions"))
self.ed_inc.setPlaceholderText(tr("search_replace.placeholder_include"))
self.ed_filename_query.setPlaceholderText(tr("search_replace.placeholder_filename"))
self.ed_query.setPlaceholderText(tr("search_replace.placeholder_content"))
ed_scope_val.setPlaceholderText(tr("search_replace.placeholder_scope"))
```

#### JSON:
```json
"search_replace.placeholder_extensions": "ex: .py,.js,.tsx (vazio para todos)",
"search_replace.placeholder_include": "ex: *.test.*, **/src/** (vazio para todos)",
"search_replace.placeholder_filename": "Buscar em nomes de arquivo (ex: test_*.py)",
"search_replace.placeholder_content": "Buscar no conteúdo dos arquivos",
"search_replace.placeholder_scope": "ex: 'inicio,fim' ou 'div'"
```

---

## 🟡 FASE 35: QGroupBox + Tabs

### diff_viewer_dialog.py (2 QGroupBox)

#### Localização: Linhas 158, 169
```python
# 🔴 ANTES (com variável):
left_panel = QGroupBox(f"File A: {self.file_a_name}")
right_panel = QGroupBox(f"File B: {self.file_b_name}")

# ✅ DEPOIS:
left_panel = QGroupBox(tr("diff_viewer.group_file_a").format(name=self.file_a_name))
right_panel = QGroupBox(tr("diff_viewer.group_file_b").format(name=self.file_b_name))
```

#### JSON:
```json
"diff_viewer.group_file_a": "Arquivo A: {name}",
"diff_viewer.group_file_b": "Arquivo B: {name}"
```

---

### ui_builder.py (2 tabs)

#### Localização: Linhas 95-96
```python
# 🔴 ANTES:
main_window.tabs.addTab(main_window.tab_search, "Search / Replace")
main_window.tabs.addTab(main_window.tab_insert, "Insert")

# ✅ DEPOIS:
main_window.tabs.addTab(main_window.tab_search, tr("main.tab_search"))
main_window.tabs.addTab(main_window.tab_insert, tr("main.tab_insert"))
```

#### JSON:
```json
"main.tab_search": "Buscar / Substituir",
"main.tab_insert": "Inserir"
```

---

### jsx_extractor_dock.py (2 tabs)

#### Localização: Linhas 225-226
```python
# 🔴 ANTES:
self.tabs.addTab(self.out_paths, "Paths")
self.tabs.addTab(self.out_json, "JSON")

# ✅ DEPOIS:
self.tabs.addTab(self.out_paths, tr("jsx_extractor.tab_paths"))
self.tabs.addTab(self.out_json, tr("jsx_extractor.tab_json"))
```

#### JSON:
```json
"jsx_extractor.tab_paths": "Caminhos",
"jsx_extractor.tab_json": "JSON"
```

---

## 🟢 FASE 36+: setText() - Casos Especiais

### Tipos JSON (json_tree_widget.py) - NÃO TRADUZIR

#### Localização: Linhas 121-165
```python
# ❌ NÃO TRADUZIR - São tipos técnicos JSON:
item.setText(2, "Object")
item.setText(2, "Array")
item.setText(2, "String")
item.setText(2, "Boolean")
item.setText(2, "Number")
item.setText(2, "Null")
```

**Motivo:** Tipos JSON são internacionalmente reconhecidos em inglês.

---

### Labels Dinâmicos - TRADUZIR COM .format()

#### recall_dialog.py (Linha 70)
```python
# 🔴 ANTES:
timestamp_label = QLabel(f"Stored: {self.timestamp}")

# ✅ DEPOIS:
timestamp_label = QLabel(tr("recall_dialog.lbl_stored").format(timestamp=self.timestamp))
```

#### JSON:
```json
"recall_dialog.lbl_stored": "Armazenado: {timestamp}"
```

---

#### calculator_dock.py (Linha 44)
```python
# 🔴 ANTES:
title = QLabel(f"Comparison: Slot {slot1} vs Slot {slot2}")

# ✅ DEPOIS:
title = QLabel(tr("calculator.lbl_comparison").format(slot1=slot1, slot2=slot2))
```

#### JSON:
```json
"calculator.lbl_comparison": "Comparação: Slot {slot1} vs Slot {slot2}"
```

---

## 🟢 FASE 41+: Tooltips

### batch_dialog.py (Exemplos)

#### Localização: Linhas 59, 68, 70, 75
```python
# 🔴 ANTES:
self.ed_description.setToolTip("Human-readable description for this step (optional)")
self.radio_file_a_file.setToolTip("Use a JSON file from disk as input")
self.radio_file_a_previous.setToolTip("Use the result from the previous step as input")

# ✅ DEPOIS:
self.ed_description.setToolTip(tooltip_tr("batch_dialog.tooltip_description"))
self.radio_file_a_file.setToolTip(tooltip_tr("batch_dialog.tooltip_file_input"))
self.radio_file_a_previous.setToolTip(tooltip_tr("batch_dialog.tooltip_previous_input"))
```

**Nota:** Usar `tooltip_tr()` para tooltips!

#### JSON:
```json
"batch_dialog.tooltip_description": "Descrição legível para este passo (opcional)",
"batch_dialog.tooltip_file_input": "Usar um arquivo JSON do disco como entrada",
"batch_dialog.tooltip_previous_input": "Usar o resultado do passo anterior como entrada"
```

---

## 🟢 FASE 45+: QMessageBox

### Padrão Geral

#### Simples (sem variáveis)
```python
# 🔴 ANTES:
QMessageBox.information(self, "Success", "Operation completed successfully!")

# ✅ DEPOIS:
QMessageBox.information(
    self,
    tr("common.msg_title_success"),
    tr("operation.msg_completed")
)
```

#### Com variáveis
```python
# 🔴 ANTES:
QMessageBox.warning(self, "Validation Error", f"File A not found: {file_path}")

# ✅ DEPOIS:
QMessageBox.warning(
    self,
    tr("common.msg_title_validation_error"),
    tr("batch.msg_file_not_found").format(file=file_path)
)
```

#### Com botões personalizados
```python
# 🔴 ANTES:
reply = QMessageBox.question(
    self,
    "Confirm",
    "Are you sure?",
    QMessageBox.Yes | QMessageBox.No
)

# ✅ DEPOIS:
reply = QMessageBox.question(
    self,
    tr("common.msg_title_confirm"),
    tr("common.msg_are_you_sure"),
    QMessageBox.Yes | QMessageBox.No
)
# Nota: Textos dos botões Yes/No são traduzidos automaticamente pelo Qt
```

---

## ⚙️ Padrões de Keys para JSON

### Estrutura Recomendada:
```
{componente}.{elemento}_{descrição}
```

### Exemplos:
- **Botões:** `recall_dialog.btn_export`
- **Labels:** `recall_dialog.lbl_stored`
- **Placeholders:** `batch_dialog.placeholder_file_a`
- **Tooltips:** `batch_dialog.tooltip_description`
- **GroupBox:** `diff_viewer.group_file_a`
- **Tabs:** `main.tab_search`
- **QMessageBox Títulos:** `common.msg_title_success`
- **QMessageBox Textos:** `operation.msg_completed`
- **Window Titles:** `recall_dialog.window_title`

### Categorias Comuns:
- `common.*` - Strings usadas em múltiplos componentes
- `{dock_name}.*` - Específicas de um dock
- `{dialog_name}.*` - Específicas de um dialog
- `{widget_name}.*` - Específicas de um widget

---

## 🎓 Checklist para Nova Tradução

### Antes de traduzir:
- [ ] Identificar arquivo e linha exata
- [ ] Verificar se string tem variáveis (usar .format())
- [ ] Verificar se é texto técnico (pode não traduzir)
- [ ] Verificar imports necessários (tr, tooltip_tr)
- [ ] Escolher key apropriada no JSON

### Durante tradução:
- [ ] Adicionar ao pt_BR.json primeiro
- [ ] Adicionar aos outros 6 idiomas
- [ ] Atualizar código Python
- [ ] Manter emojis fora das traduções (no código)
- [ ] Usar .format() para variáveis, não f-strings

### Após tradução:
- [ ] Validar todos os 7 JSONs
- [ ] Verificar erros de sintaxe Python
- [ ] Testar visualmente se possível
- [ ] Commit estruturado
- [ ] Push para GitHub

---

## 🚀 Script Helper para Busca

```bash
#!/bin/bash
# find_untranslated.sh - Buscar strings não traduzidas

COMPONENT=$1
CATEGORY=$2

case $CATEGORY in
  "button")
    grep -rn "QPushButton.*[\"']" src/gui/$COMPONENT*.py | grep -v "tr("
    ;;
  "placeholder")
    grep -rn "setPlaceholderText" src/gui/$COMPONENT*.py | grep -v "tr("
    ;;
  "tooltip")
    grep -rn "setToolTip" src/gui/$COMPONENT*.py | grep -v "tooltip_tr"
    ;;
  "label")
    grep -rn "QLabel.*[\"']" src/gui/$COMPONENT*.py | grep -v "tr("
    ;;
  *)
    echo "Uso: ./find_untranslated.sh <component> <button|placeholder|tooltip|label>"
    ;;
esac
```

**Uso:**
```bash
chmod +x find_untranslated.sh
./find_untranslated.sh recall_dialog button
./find_untranslated.sh batch_dialog placeholder
```

---

*Documento de referência para traduções - Clarify v2.9.114*  
*Última atualização: 2025-12-30*
