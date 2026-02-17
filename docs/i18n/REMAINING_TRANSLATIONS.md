# 📋 Levantamento de Traduções Restantes - Clarify

**Data:** 2025-12-30  
**Versão:** v2.9.114  
**Fase Atual:** 33 (após Fase 32 - Window Titles)

---

## 📊 Resumo Executivo

| Categoria | Quantidade | Prioridade | Dificuldade |
|-----------|------------|------------|-------------|
| **Botões com Emojis** | 14 | 🔴 Alta | ⭐ Fácil |
| **Placeholders** | 19 | 🟡 Média | ⭐ Fácil |
| **QGroupBox** | 2 | 🟡 Média | ⭐ Fácil |
| **Tabs (addTab)** | 4 | 🟡 Média | ⭐ Fácil |
| **QLabel** | 6 | 🟢 Baixa | ⭐ Fácil |
| **setText()** | 40 | 🟢 Baixa | ⭐⭐ Médio |
| **Tooltips** | 214 | 🟢 Baixa | ⭐⭐ Médio |
| **QMessageBox** | ~171 | 🟢 Baixa | ⭐⭐⭐ Difícil |
| **TOTAL** | **~470** | - | - |
| **Em 7 línguas** | **~3.290** | - | - |

---

## 🎯 Priorização Recomendada

### Fase 33: Botões com Emojis (14 strings × 7 = 98 traduções) 🔴 PRIORIDADE ALTA
**Justificativa:** Alto impacto visual, fácil implementação, já está planejada.

**Arquivos afetados:**
- `recall_dialog.py` (3 botões)
- `plugin_manager_dialog.py` (2 botões)
- `diff_viewer_dialog.py` (1 botão)
- `venn_diagram_dialog.py` (1 botão)
- `progress/progress_bar_widget.py` (3 botões)
- `progress/progress_details_dialog.py` (2 botões)
- `update_notification_dialog.py` (1 botão)
- `panels/search_replace_panel.py` (1 botão)

**Padrão de implementação:**
```python
# Antes:
QPushButton("📤 Export to File")

# Depois:
QPushButton(f"📤 {tr('recall_dialog.btn_export')}")
```

---

### Fase 34: Placeholders (19 strings × 7 = 133 traduções) 🟡 MÉDIA
**Justificativa:** Aparecem quando campos estão vazios, melhoram UX.

**Principais arquivos:**
- `batch_dialog.py` (3 placeholders)
- `error_report_dialog.py` (3 placeholders)
- `tutorial_assistant_dialog.py` (1 placeholder)
- `advanced_extractor_dock.py` (2 placeholders)
- `panels/search_replace_panel.py` (5 placeholders)

**Padrão:**
```python
# Antes:
ed.setPlaceholderText("Type your question here...")

# Depois:
ed.setPlaceholderText(tr("tutorial_assistant.placeholder_question"))
```

---

### Fase 35: QGroupBox + Tabs (6 strings × 7 = 42 traduções) 🟡 MÉDIA
**Justificativa:** Agrupamentos visuais importantes.

**QGroupBox (2):**
- `diff_viewer_dialog.py`: "File A: {name}" e "File B: {name}"

**Tabs (4):**
- `ui_builder.py`: "Search / Replace", "Insert"
- `jsx_extractor_dock.py`: "Paths", "JSON"

---

### Fase 36-40: QLabel e setText() (~46 strings × 7 = 322 traduções) 🟢 BAIXA
**Justificativa:** Muitos são dinâmicos com f-strings, requerem análise cuidadosa.

**Tipos encontrados:**
1. **Labels dinâmicos:** `f"Stored: {timestamp}"` - Requerem .format()
2. **Labels de tipo:** "Object", "Array", "String", "Boolean", "Number", "Null"
3. **Labels de status:** Diversos em setText()

**Desafio:** Muitos setText() são usados para valores dinâmicos (paths, números, etc.) que não devem ser traduzidos. Requer análise caso a caso.

---

### Fase 41+: Tooltips (214 strings × 7 = 1.498 traduções) 🟢 BAIXA
**Justificativa:** Grande volume, mas menor prioridade (aparecem apenas no hover).

**Principais concentrações:**
- `batch_dialog.py`: ~20 tooltips
- Diversos widgets e docks

**Padrão:**
```python
# Antes:
widget.setToolTip("Human-readable description")

# Depois:
widget.setToolTip(tooltip_tr("batch_dialog.tooltip_description"))
```

**Nota:** Usar `tooltip_tr()` ao invés de `tr()` para tooltips.

---

### Fase 45+: QMessageBox (~171 ocorrências) 🟢 BAIXA - DESAFIADOR
**Justificativa:** Grande volume, requer análise contextual profunda, muitas mensagens dinâmicas.

**Tipos de mensagens:**
1. **Títulos (title):** "Error", "Warning", "Success", "Confirmation"
2. **Mensagens (text):** Textos explicativos variados
3. **Botões personalizados:** Quando usam StandardButton

**Desafios:**
- Muitas mensagens com formatação dinâmica (f-strings)
- Contexto importante para tradução adequada
- Alguns já podem usar tr() - requer verificação cuidadosa

**Recomendação:** Fazer por arquivo/dock, não tudo de uma vez.

---

## 📁 Arquivos com Mais Strings Não Traduzidas

| Arquivo | Categoria Principal | Est. Strings |
|---------|---------------------|--------------|
| `batch_dialog.py` | Tooltips, Placeholders, QMessageBox | ~35 |
| `panels/search_replace_panel.py` | Placeholders, Botões | ~8 |
| `error_report_dialog.py` | Placeholders, QMessageBox | ~6 |
| `google_translate_dock.py` | setText(), QMessageBox | ~15 |
| `tutorials_dock.py` | setText(), QMessageBox | ~10 |
| Diversos progress widgets | Botões emoji, setText() | ~8 |

---

## 🚫 Elementos que NÃO Devem Ser Traduzidos

### 1. Valores Técnicos/Programáticos
```python
# ❌ NÃO traduzir:
item.setText(2, "Object")  # Tipo JSON - mantém em inglês
self.ed_root_var.setText("t")  # Valor padrão técnico
```

### 2. Formatação HTML/CSS
```python
# ❌ NÃO traduzir (HTML):
QLabel("<b>Bold text</b>")  # Mantém tags HTML
label.setStyleSheet("color: red;")  # CSS
```

### 3. Valores Dinâmicos Puros
```python
# ❌ NÃO traduzir se for apenas número/path/valor:
label.setText(str(count))  # Número
label.setText(file_path)  # Caminho de arquivo
label.setText(json_value)  # Valor do JSON
```

### 4. Strings de Debug/Log
```python
# ❌ NÃO traduzir logs internos:
print(f"Debug: {value}")  # Log de desenvolvimento
```

---

## ✅ Boas Práticas Identificadas

### 1. Botões com Emoji
- ✅ **Manter emoji:** `f"📤 {tr('key')}"`
- ❌ **Não incluir emoji no JSON:** `"btn_export": "Export to File"` (sem emoji)

### 2. Strings com Variáveis
```python
# ✅ Usar .format() ao invés de f-string:
tr("recall_dialog.window_title").format(slot_name=slot_name)

# JSON:
"window_title": "Recall Slot {slot_name}"
```

### 3. Ordem de Adição aos JSONs
1. `pt_BR.json` primeiro (tradução manual)
2. Outros 6 idiomas em paralelo (multi_replace)
3. Validar todos os JSONs com `python3 -m json.tool`

### 4. Imports Necessários
```python
from src.i18n.translator import tr  # Para textos
from src.i18n.translator import tooltip_tr  # Para tooltips
```

---

## 📈 Estimativa de Esforço por Fase

| Fase | Categoria | Strings | Traduções | Arquivos | Tempo Est. |
|------|-----------|---------|-----------|----------|------------|
| 33 | Botões Emoji | 14 | 98 | 8 | 30 min |
| 34 | Placeholders | 19 | 133 | 7 | 45 min |
| 35 | GroupBox+Tabs | 6 | 42 | 3 | 20 min |
| 36-40 | QLabel+setText | 46 | 322 | 10 | 2h |
| 41-44 | Tooltips | 214 | 1.498 | 20+ | 4h |
| 45+ | QMessageBox | 171 | 1.197 | 25+ | 6h |
| **TOTAL** | - | **470** | **3.290** | - | **~13h** |

---

## 🎯 Roadmap de Traduções

### ✅ Concluído (Fases 1-32)
- [x] Fase 1-22: Diversos widgets e docks (447 strings)
- [x] Fase 23: match_panel, search_replace_panel (42 strings)
- [x] Fase 24-25: ai_processor, json_rewriter, calculator (16 strings)
- [x] Fase 26: file_selection, file_filter, path_entry (5 strings)
- [x] Fase 27: layout_manager, recall, transparency (9 strings)
- [x] Fase 28: tutorial_assistant, plugin_manager, diff_viewer, venn (10 strings)
- [x] Fase 29: update_notification (8 strings)
- [x] Fase 30: venn, progress widgets (5 strings)
- [x] Fase 31: operation_options, json_search (6 strings)
- [x] **Fase 32: Window Titles (15 strings)** ← ÚLTIMA CONCLUÍDA
- **Total concluído: 578 strings = 4.046 traduções**

### 🔄 Próximas Fases (33-50)
- [ ] **Fase 33: Botões com Emojis** (14 strings) ← PRÓXIMA
- [ ] Fase 34: Placeholders (19 strings)
- [ ] Fase 35: QGroupBox + Tabs (6 strings)
- [ ] Fases 36-40: QLabel + setText (46 strings)
- [ ] Fases 41-44: Tooltips (214 strings)
- [ ] Fases 45-50: QMessageBox (171 strings)

### 📊 Progresso Geral
```
Concluído:   578 strings ████████████░░░░░░░░ 55%
Pendente:    470 strings ░░░░░░░░░░░░░░░░░░░░ 45%
Total:     1.048 strings ████████████████████ 100%

Traduções concluídas: 4.046 / 7.336 (55%)
```

---

## 🔍 Observações Importantes

### Arquivos BACKUP e NEW
**Decisão:** Excluir de traduções  
**Motivo:** São versões antigas/experimentais que serão eventualmente removidas.

Arquivos identificados:
- `panels/search_replace_panel_BACKUP.py`
- `panels/search_replace_panel_NEW.py`
- `panels/insert_panel_BACKUP.py`

### Strings em Comentários
Algumas strings aparecem em comentários docstrings. Essas **não** devem ser traduzidas, pois são documentação interna para desenvolvedores.

### QMessageBox - Verificação Necessária
A contagem de ~171 QMessageBox pode incluir alguns que já usam `tr()`. É necessário revisar arquivo por arquivo.

---

## 📝 Template para Próximas Fases

```markdown
## Fase XX: [Nome da Categoria]

**Strings identificadas:** X
**Traduções totais:** X × 7 = Y
**Arquivos afetados:** Z

### Arquivos:
1. arquivo1.py (N strings)
2. arquivo2.py (N strings)

### Padrão de implementação:
[Exemplo de código]

### Commits:
- Adicionar strings aos 7 JSONs
- Atualizar código Python
- Validar JSONs
- Commit: "feat(i18n): Fase XX - [Descrição]"
```

---

## 🎓 Lições Aprendidas (Fases 1-32)

### ✅ O que funcionou bem:
1. **Fases pequenas:** 5-15 strings por fase = commits gerenciáveis
2. **Validação automática:** `python3 -m json.tool` para cada JSON
3. **multi_replace_string_in_file:** Editar múltiplos arquivos em paralelo
4. **Padrão de keys:** `component.element_description` (ex: `recall_dialog.btn_export`)
5. **Commit estruturado:** Mensagem descritiva com lista de arquivos

### ⚠️ Desafios encontrados:
1. **Imports mal formatados:** Requerem correção (ex: file_selection_widget.py)
2. **Whitespace exato:** oldString precisa ter espaçamento perfeito
3. **Variáveis em strings:** Requer .format() ao invés de f-strings
4. **Contexto das strings:** Algumas requerem leitura do código para entender uso

### 🔧 Melhorias para próximas fases:
1. **Pré-análise:** Verificar imports antes de editar
2. **Agrupamento lógico:** Agrupar strings do mesmo arquivo na mesma fase
3. **Teste visual:** Se possível, testar interface após traduções
4. **Documentação:** Manter este documento atualizado após cada fase

---

## 📌 Comandos Úteis

### Buscar strings não traduzidas:
```bash
# Botões com emoji:
grep -rn 'QPushButton.*["'"'"'][🔄📤📥✅❌]' src/gui/ --include="*.py" | grep -v "tr("

# Placeholders:
grep -rn 'setPlaceholderText' src/gui/ --include="*.py" | grep -v "tr("

# Tooltips:
grep -rn '\.setToolTip.*["'"'"']' src/gui/ --include="*.py" | grep -v "tooltip_tr"

# QMessageBox:
grep -rn 'QMessageBox\.' src/gui/ --include="*.py" | grep -E "(information|warning|critical|question)"
```

### Validar JSONs:
```bash
for lang in pt_BR en de es fr ja zh; do
  python3 -m json.tool "src/i18n/$lang.json" > /dev/null && echo "✓ $lang.json" || echo "✗ $lang.json"
done
```

### Contar strings em arquivo específico:
```bash
grep -n 'QPushButton.*["'"'"']' src/gui/recall_dialog.py | grep -v "tr(" | wc -l
```

---

## 📞 Contato e Manutenção

**Documento mantido por:** Josué Amaral  
**Última atualização:** 2025-12-30  
**Próxima revisão:** Após Fase 35

**Nota:** Este documento deve ser atualizado após cada 3-5 fases concluídas para refletir o progresso e ajustar estimativas.

---

## 🏁 Meta Final

**Objetivo:** 100% de strings traduzidas na interface GUI  
**Estimativa de conclusão:** ~13 horas de trabalho (470 strings restantes)  
**Impacto:** Interface totalmente multilíngue em 7 idiomas  
**Benefício:** Acessibilidade global, experiência profissional para todos os usuários

**Status atual:** 578/1.048 strings (55%) ✅  
**Próximo milestone:** 650/1.048 strings (62%) após Fases 33-35

---

*Documento gerado automaticamente em 2025-12-30*  
*Clarify v2.9.114 - Sistema de Gerenciamento de Arquivos JSON*
