# Plano de Ação: Tradução Completa dos Elementos Gráficos do Clarify

**Autor:** Josué Amaral  
**Data:** 24 de Dezembro de 2025  
**Objetivo:** Traduzir 100% dos textos hardcoded dos elementos visuais para todos os 7 idiomas suportados

---

## 📊 Status Atual

### Idiomas Disponíveis (7):
| Idioma | Código | Chaves | Cobertura | Status |
|--------|--------|--------|-----------|--------|
| **English** | `en` | 501 | 100% (base) | ✅ Completo |
| **Português BR** | `pt_BR` | 501 | 100% | ✅ Completo |
| **Español** | `es` | 503 | 100.4% | ✅ Completo |
| **Deutsch** | `de` | 459 | 91.6% | ❌ **Faltam 44 chaves** |
| **Français** | `fr` | 459 | 91.6% | ❌ **Faltam 44 chaves** |
| **日本語** | `ja` | 459 | 91.6% | ❌ **Faltam 44 chaves** |
| **中文** | `zh` | 459 | 91.6% | ❌ **Faltam 44 chaves** |

**Resumo:**
- ✅ **3 idiomas 100% completos** (EN, PT-BR, ES)
- ❌ **4 idiomas incompletos** (DE, FR, JA, ZH)
- **Total de chaves faltantes:** 176 (44 × 4 idiomas)

---

## 🎯 Objetivos do Plano

### 1. **Fase 1: Completar Traduções Existentes** (Prioridade Alta)
Adicionar as 44 chaves faltantes nos 4 idiomas incompletos (DE, FR, JA, ZH):
- Dialog.preferences.* (7 chaves)
- Dialog.transparency.* (2 chaves)
- Dialog.plugin_manager.* (6 chaves)
- Dialog.layout_manager.* (9 chaves)
- Common.* (11 chaves)
- Tooltip.google_translate.* (8 chaves)
- Misc (1 chave)

### 2. **Fase 2: Eliminar Textos Hardcoded** (Prioridade Alta)
Identificar e substituir TODOS os textos hardcoded nos componentes GUI por chamadas ao sistema i18n.

### 3. **Fase 3: Adicionar Novas Traduções** (Prioridade Média)
Expandir o sistema de tradução para componentes ainda não internacionalizados.

### 4. **Fase 4: Validação e Testes** (Prioridade Alta)
Testar todos os idiomas em toda a aplicação.

---

## 📋 Fase 1: Completar Traduções Existentes

### Chaves Faltantes (44 por idioma):

#### **Diálogos (24 chaves)**
```json
"dialog.preferences.title": "Preferences",
"dialog.preferences.general": "General",
"dialog.preferences.show_tooltips": "Show tooltips",
"dialog.preferences.confirm_exit": "Confirm before exit",
"dialog.preferences.auto_save": "Auto-save settings",
"dialog.preferences.check_updates": "Check for updates on startup",
"dialog.preferences.success": "Preferences saved successfully",

"dialog.transparency.title": "Window Transparency",
"dialog.transparency.level": "Transparency Level",

"dialog.plugin_manager.title": "Plugin Manager - Clarify",
"dialog.plugin_manager.description": "Manage installed plugins",
"dialog.plugin_manager.refresh": "🔄 Refresh",
"dialog.plugin_manager.close": "✅ Close",
"dialog.plugin_manager.refreshed": "Plugins Refreshed",
"dialog.plugin_manager.activation_failed": "Activation Failed",

"dialog.layout_manager.title": "Manage Layouts",
"dialog.layout_manager.saved_layouts": "Saved layouts (custom layouts only):",
"dialog.layout_manager.load": "Load",
"dialog.layout_manager.delete": "Delete",
"dialog.layout_manager.reset": "Reset to Defaults",
"dialog.layout_manager.confirm_delete": "Confirm Delete",
"dialog.layout_manager.confirm_reset": "Confirm Reset",
"dialog.layout_manager.reset_complete": "Reset Complete",
"dialog.layout_manager.success": "Layout loaded successfully",
"dialog.layout_manager.close": "Close"
```

#### **Termos Comuns (11 chaves)**
```json
"common.success": "Success",
"common.error": "Error",
"common.warning": "Warning",
"common.ok": "OK",
"common.cancel": "Cancel",
"common.yes": "Yes",
"common.no": "No",
"common.close": "Close",
"common.save": "Save",
"common.delete": "Delete",
"common.load": "Load"
```

#### **Google Translate (8 chaves)**
```json
"menu.tools.google_translate": "Google Translate",
"tooltip.google_translate.from_lang": "Source language...",
"tooltip.google_translate.to_lang": "Target language...",
"tooltip.google_translate.input_text": "Enter or paste text...",
"tooltip.google_translate.translate_btn": "Start translation...",
"tooltip.google_translate.copy_result": "Copy translation result...",
"tooltip.google_translate.clear_btn": "Clear input and output...",
"tooltip.google_translate.file_mode": "Enable to translate entire..."
```

#### **Misc (1 chave)**
```json
"tooltip.base.btn_open_editor": "Open results in editor..."
```

### Traduções Necessárias:

#### **Alemão (de.json) - 44 traduções**
- Preferences → Einstellungen
- Window Transparency → Fenstertransparenz
- Manage Layouts → Layouts Verwalten
- Success → Erfolg
- Error → Fehler

#### **Francês (fr.json) - 44 traduções**
- Preferences → Préférences
- Window Transparency → Transparence de la Fenêtre
- Manage Layouts → Gérer les Dispositions
- Success → Succès
- Error → Erreur

#### **Japonês (ja.json) - 44 traduções**
- Preferences → 設定
- Window Transparency → ウィンドウの透明度
- Manage Layouts → レイアウト管理
- Success → 成功
- Error → エラー

#### **Chinês (zh.json) - 44 traduções**
- Preferences → 首选项
- Window Transparency → 窗口透明度
- Manage Layouts → 管理布局
- Success → 成功
- Error → 错误

---

## 🔍 Fase 2: Eliminar Textos Hardcoded

### Componentes com Textos Hardcoded Identificados:

#### **Alta Prioridade (100+ ocorrências)**

1. **src/gui/preferences_dialog.py** (7 strings)
   - `setWindowTitle("Preferences")`
   - `QGroupBox("General")`
   - `QCheckBox("Show tooltips")`
   - `QCheckBox("Confirm before exit")`
   - `QCheckBox("Auto-save settings")`
   - `QCheckBox("Check for updates on startup")`
   - Mensagem "Success"

2. **src/gui/json_translate_dock.py** (20+ strings)
   - `QLabel("Root path:")`
   - `QPushButton("Browse…")`
   - `QCheckBox("Is file?")`
   - `QLabel("Dictionary file (JSON/TS):")`
   - `QPushButton("Run translation")`
   - E muitos outros...

3. **src/gui/shortcuts_dialog.py** (15+ strings)
   - `setWindowTitle("Customize Keyboard Shortcuts")`
   - `QLabel("Customize keyboard shortcuts for all actions")`
   - `QPushButton("Reset Selected")`
   - `QPushButton("Save")`
   - E outros...

4. **src/gui/base_dock.py** (15+ strings)
   - `QPushButton("Browse...")`
   - `QCheckBox("Is file")`
   - `QLabel("Extensions:")`
   - Mensagens de contexto

5. **src/gui/update_notification.py** (10+ strings - PT-BR hardcoded!)
   - `setWindowTitle("Atualização Disponível - Clarify")`
   - `QLabel("✨ Nova Versão: Clarify v...")`
   - `QPushButton("📖 Ver Changelog Completo")`
   - `QPushButton("⬇️ Baixar Atualização")`
   - **PROBLEMA:** Está todo em português hardcoded!

6. **src/gui/case_validator_dialog.py** (10+ strings)
7. **src/gui/merge_config_dialog.py** (10+ strings)
8. **src/gui/transparency_dialog.py** (2 strings já feito)
9. **src/gui/plugin_manager_dialog.py** (6 strings já feito)
10. **src/gui/layout_manager_dialog.py** (9 strings já feito)

#### **Média Prioridade (50-100 ocorrências)**

11. **src/gui/json_rewriter_dock.py**
12. **src/gui/text_extractor_dock.py**
13. **src/gui/ai_processor_dock.py**
14. **src/gui/json_search_dock.py**
15. **src/gui/case_converter_dock.py**

#### **Baixa Prioridade (<50 ocorrências)**

16. **src/gui/text_to_json_dock.py**
17. **src/gui/set_operations_dock.py**
18. **src/gui/calculator_dock.py**
19. **src/gui/jsx_extractor_dock.py**
20. **src/gui/placeholder_replacer_dock.py**

### Estimativa: **300-500 strings hardcoded** no total

---

## 📐 Estratégia de Implementação

### **Passo 1: Preparar Traduções**

#### Script de Geração Automática
```python
# Script para gerar traduções usando Google Translate API ou similar
# generate_missing_translations.py

import json
from googletrans import Translator  # ou outro serviço

# Carregar EN como base
with open('src/i18n/en.json', 'r') as f:
    en_data = json.load(f)

# Para cada idioma incompleto
for lang_code in ['de', 'fr', 'ja', 'zh']:
    with open(f'src/i18n/{lang_code}.json', 'r') as f:
        lang_data = json.load(f)
    
    # Encontrar chaves faltantes
    missing = set(en_data.keys()) - set(lang_data.keys())
    
    # Traduzir automaticamente (precisa revisão manual)
    translator = Translator()
    for key in missing:
        translation = translator.translate(
            en_data[key], 
            dest=lang_code.split('_')[0]
        )
        lang_data[key] = translation.text
    
    # Salvar com aviso de revisão necessária
    lang_data['_auto_translated_needs_review'] = list(missing)
    
    with open(f'src/i18n/{lang_code}.json', 'w') as f:
        json.dump(lang_data, f, indent=2, ensure_ascii=False)
```

### **Passo 2: Criar Helper para i18n**

```python
# src/i18n/ui_translator.py
"""Helper para traduzir elementos UI"""

from .translator import tr

def tr_dialog(key: str, **kwargs) -> str:
    """Traduzir chave de diálogo"""
    return tr(f"dialog.{key}", **kwargs)

def tr_common(key: str) -> str:
    """Traduzir termo comum"""
    return tr(f"common.{key}")

def tr_tooltip(key: str, **kwargs) -> str:
    """Traduzir tooltip"""
    return tr(f"tooltip.{key}", **kwargs)
```

### **Passo 3: Refatorar Componentes Sistematicamente**

**Padrão de Substituição:**

```python
# ❌ ANTES (hardcoded)
self.setWindowTitle("Preferences")
btn_save = QPushButton("Save")

# ✅ DEPOIS (traduzido)
from src.i18n.ui_translator import tr_dialog, tr_common

self.setWindowTitle(tr_dialog("preferences.title"))
btn_save = QPushButton(tr_common("save"))
```

**Ordem de Refatoração:**
1. ✅ Diálogos pequenos (preferences, transparency, plugin_manager, layout_manager) - **JÁ FEITO**
2. ⏳ Diálogos médios (shortcuts, case_validator, merge_config, update_notification)
3. ⏳ Docks principais (json_translate, json_rewriter, text_extractor)
4. ⏳ Docks secundários (ai_processor, json_search, case_converter)
5. ⏳ Componentes base (base_dock, panels)
6. ⏳ Mensagens e notificações

---

## 🧪 Fase 4: Validação e Testes

### Checklist de Validação:

#### **Por Idioma:**
- [ ] **EN** - Verificar inglês em todos os diálogos e docks
- [ ] **PT-BR** - Verificar português em todos os diálogos e docks
- [ ] **ES** - Verificar espanhol em todos os diálogos e docks
- [ ] **DE** - Verificar alemão (após tradução)
- [ ] **FR** - Verificar francês (após tradução)
- [ ] **JA** - Verificar japonês (após tradução)
- [ ] **ZH** - Verificar chinês (após tradução)

#### **Por Componente:**
- [ ] Preferences Dialog
- [ ] Transparency Dialog
- [ ] Plugin Manager Dialog
- [ ] Layout Manager Dialog
- [ ] Shortcuts Dialog
- [ ] Update Notification
- [ ] JSON Translate Dock
- [ ] JSON Rewriter Dock
- [ ] Text Extractor Dock
- [ ] AI Processor Dock
- [ ] Todos os outros docks
- [ ] Menus
- [ ] Tooltips
- [ ] Mensagens de erro
- [ ] Notificações

### Script de Teste Automático:

```python
# tests/test_i18n_coverage.py
"""Testa cobertura de traduções"""

import os
import re
from pathlib import Path

def find_hardcoded_strings():
    """Encontra strings hardcoded em arquivos Python"""
    patterns = [
        r'setWindowTitle\("([^"]+)"\)',
        r'QLabel\("([^"]+)"\)',
        r'QPushButton\("([^"]+)"\)',
        r'QCheckBox\("([^"]+)"\)',
        r'QGroupBox\("([^"]+)"\)',
    ]
    
    hardcoded = []
    gui_files = Path('src/gui').rglob('*.py')
    
    for file in gui_files:
        with open(file, 'r') as f:
            content = f.read()
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if not match.startswith('tr('):  # Não é tradução
                        hardcoded.append({
                            'file': str(file),
                            'text': match
                        })
    
    return hardcoded

def test_no_hardcoded_strings():
    """Teste: Não deve haver strings hardcoded"""
    hardcoded = find_hardcoded_strings()
    
    if hardcoded:
        print(f"\n❌ Encontradas {len(hardcoded)} strings hardcoded:")
        for item in hardcoded[:10]:  # Mostrar primeiras 10
            print(f"  {item['file']}: {item['text']}")
        assert False, f"Existem {len(hardcoded)} strings hardcoded!"
    else:
        print("✅ Nenhuma string hardcoded encontrada!")
```

---

## 📅 Cronograma Estimado

### **Sprint 1: Fase 1 - Completar Traduções** (2-3 horas)
- [ ] Gerar traduções automáticas para DE, FR, JA, ZH
- [ ] Revisar e corrigir traduções automáticas
- [ ] Testar cada idioma na aplicação
- [ ] Commit: "i18n: Complete translations for DE, FR, JA, ZH"

### **Sprint 2: Fase 2.1 - Diálogos Pequenos** (3-4 horas)
- [x] Preferences Dialog ✅ JÁ FEITO
- [x] Transparency Dialog ✅ JÁ FEITO
- [x] Plugin Manager Dialog ✅ JÁ FEITO
- [x] Layout Manager Dialog ✅ JÁ FEITO

### **Sprint 3: Fase 2.2 - Diálogos Médios** (4-6 horas)
- [ ] Shortcuts Dialog
- [ ] Case Validator Dialog
- [ ] Merge Config Dialog
- [ ] Update Notification (corrigir PT-BR hardcoded!)
- [ ] Commit por componente

### **Sprint 4: Fase 2.3 - Docks Principais** (8-10 horas)
- [ ] JSON Translate Dock
- [ ] JSON Rewriter Dock
- [ ] Text Extractor Dock
- [ ] Commit por dock

### **Sprint 5: Fase 2.4 - Docks Secundários** (6-8 horas)
- [ ] AI Processor Dock
- [ ] JSON Search Dock
- [ ] Case Converter Dock
- [ ] Outros docks menores
- [ ] Commit por grupo

### **Sprint 6: Fase 2.5 - Base Components** (4-6 horas)
- [ ] base_dock.py
- [ ] Panels
- [ ] Widgets compartilhados
- [ ] Commit final

### **Sprint 7: Fase 4 - Validação Final** (4-6 horas)
- [ ] Testar todos os 7 idiomas
- [ ] Executar testes automáticos
- [ ] Documentar traduções
- [ ] Commit: "i18n: Complete UI translation for all 7 languages"

**Total Estimado:** 31-43 horas (~1 semana de trabalho dedicado)

---

## 🎯 Métricas de Sucesso

### Objetivos Finais:
- ✅ **7/7 idiomas** com 100% de cobertura
- ✅ **0 strings hardcoded** em componentes GUI
- ✅ **100% dos diálogos** traduzidos
- ✅ **100% dos docks** traduzidos
- ✅ **100% dos menus** traduzidos
- ✅ **100% dos tooltips** traduzidos
- ✅ **Testes automáticos** passando

### KPIs:
| Métrica | Atual | Meta | Status |
|---------|-------|------|--------|
| Idiomas completos | 3/7 (43%) | 7/7 (100%) | 🔴 |
| Chaves traduzidas | 1463/1712 (85%) | 1712/1712 (100%) | 🟡 |
| Componentes i18n | 4/30 (13%) | 30/30 (100%) | 🔴 |
| Strings hardcoded | ~400 | 0 | 🔴 |

---

## 📝 Documentação Adicional

### Arquivos de Referência:
- `src/i18n/translator.py` - Sistema de tradução
- `src/i18n/en.json` - Tradução base (inglês)
- `src/i18n/pt_BR.json` - Tradução português
- `src/i18n/es.json` - Tradução espanhol
- `docs/architecture/IMPORT_TREE_ANALOGY.md` - Arquitetura do projeto

### Convenções de Nomenclatura:

```
menu.{section}.{item}           # menu.file.open
dialog.{name}.{element}         # dialog.preferences.title
common.{term}                   # common.success
tooltip.{component}.{element}   # tooltip.search.query
context.{action}                # context.copy
search.{element}                # search.path
```

### Exemplo de Arquivo i18n Completo:

```json
{
  "_comment": "German (DE) translation for Clarify",
  "_translators": ["Automated + Manual Review"],
  "_version": "2.9.91",
  
  "app.title": "Clarify - JSON-Datei-Verwaltungssystem",
  "menu.file": "Datei",
  "dialog.preferences.title": "Einstellungen",
  "common.success": "Erfolg",
  "tooltip.search.query": "Suchmuster eingeben..."
}
```

---

## 🚀 Próximos Passos Imediatos

1. **Executar análise detalhada:**
   ```bash
   python3 scripts/analyze_i18n_coverage.py
   ```

2. **Gerar traduções faltantes:**
   ```bash
   python3 scripts/generate_missing_translations.py
   ```

3. **Criar branch para trabalho:**
   ```bash
   git checkout -b feature/complete-i18n-translation
   ```

4. **Iniciar Sprint 1:**
   - Adicionar 44 chaves × 4 idiomas = 176 traduções

---

## 📞 Contato e Suporte

**Mantenedor:** Josué Amaral  
**Repositório:** GitHub (private)  
**Documentação:** `docs/`

**Colaboradores convidados para revisão de traduções:**
- 🇩🇪 Alemão: Voluntário necessário
- 🇫🇷 Francês: Voluntário necessário
- 🇯🇵 Japonês: Voluntário necessário
- 🇨🇳 Chinês: Voluntário necessário

---

**Última atualização:** 24 de Dezembro de 2025  
**Próxima revisão:** Após Sprint 1 (completar traduções existentes)
