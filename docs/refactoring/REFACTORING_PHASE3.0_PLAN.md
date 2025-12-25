# REFACTORING PHASE 3.0 - app.py (CRITICAL)

## 📊 STATUS: IN PROGRESS

## 🎯 OBJETIVO
Refatorar src/app.py (4533 linhas) - o arquivo MAIS CRÍTICO do projeto.
Meta: Reduzir para ~2000 linhas (-55%, ~2500 linhas)

## 📈 ANÁLISE ESTRUTURAL

### Estrutura do Arquivo:
```
Total de linhas: 4533 linhas
Funções standalone (module-level): 25 funções
Classe MainWindow: 2566 linhas (linhas 1851-4417)
  - Métodos: 107 métodos
  - __init__: ~130 linhas (linha 1852)
```

### Breakdown por Seção:

#### **1. Imports e Setup (linhas 1-200)**
- ~55 linhas de imports
- Imports de módulos organizados
- Imports condicionais (PySide6)
- Stub classes para CLI-only mode

#### **2. Funções Helper Module-Level (linhas 201-1850)**
Total: ~1650 linhas, 25 funções

**Grupo 1: JSON Translate Helpers (~400 linhas)**
- `_escape_variants_for_quotes()` - escape de quotes/apostrophes
- `_compile_value_union_regex()` - regex builder para dicionários
- `_apply_scoped_translation_tag_balanced()` - scope com tags HTML/JSX
- `mask_existing_placeholders()` / `unmask_existing_placeholders()` - proteção de placeholders
- `apply_scoped_translation()` - aplicação de transformações em scope
- `process_translate_file()` - processamento de arquivo individual
- `load_prefs()` / `save_prefs()` - carregamento/salvamento de preferências
- `apply_theme()` - aplicação de tema
- `load_translation_dict()` - carregamento de dicionário
- `flatten_dict_paths()` - flat de dicionário aninhado
- `translate_replace_texts()` - substituição de textos
- `read_translation_dict()` - leitura de dicionário

**Grupo 2: CLI Command Handlers (~400 linhas)**
- `cli_search()` - comando search CLI
- `cli_replace()` - comando replace CLI
- `cli_insert()` - comando insert CLI
- `cli_translate()` - comando translate CLI
- `cli_gtranslate()` - comando gtranslate CLI
- `cli_dedupe()` - comando dedupe CLI

**Grupo 3: CLI Utilities (~100 linhas)**
- `split_globs()` - split de padrões glob
- `parse_conditions()` - parsing de condições
- `build_file_list()` - construção de lista de arquivos

**Grupo 4: build_parser (~100 linhas)**
- `build_parser()` - argparse setup (linha 4417)

**Grupo 5: main function (~30 linhas)**
- `main()` - entry point (linha 4505)

#### **3. MainWindow Class (linhas 1851-4417)**
Total: 2566 linhas, 107 métodos

**Métodos principais identificados:**

**Setup e Initialization (~400 linhas)**
- `__init__()` - ~130 linhas (linha 1852)
- `_build_icon()` - ~26 linhas
- `_build_icon_fallback()` - ~27 linhas
- `_build_ui()` - ~53 linhas (linha 4348)
- `_build_menu()` - ? linhas
- `_restore_prefs()` - ~53 linhas (linha 4401)
- `_apply_saved_settings()` - ? linhas
- `_register_docks_with_layout_manager()` - ? linhas
- `_restore_tab_state()` - ? linhas
- `_initialize_all_tabs()` - ? linhas
- `_apply_accessibility()` - ? linhas
- `_auto_check_for_updates()` - ? linhas

**Dock Opening Methods (~15 métodos, ~200 linhas)**
- `_open_trans()` - ~6 linhas (linha 2035)
- `_open_rewrite()` - ~6 linhas (linha 2041)
- `_open_text_extractor()` - ~5 linhas (linha 2047)
- `_open_placeholder_replacer()` - ~5 linhas (linha 2052)
- `_open_ai_processor()` - ~5 linhas (linha 2057)
- `_open_json_search()` - ~5 linhas (linha 2062)
- `_open_case_converter()` - ~5 linhas (linha 2067)
- `_open_jsx_extractor()` - ~5 linhas (linha 2072)
- `_open_text_to_json()` - ~7 linhas (linha 2077)
- `_load_json_from_converter()` - ~6 linhas (linha 2084)
- `_open_file_list()` - ~5 linhas (linha 2091)
- `_open_history()` - ~? linhas
- ... (mais docks)

**Event Handlers (~1000 linhas?)**
- Translation handlers
- Theme handlers
- Menu action handlers
- Signal/slot connections
- Update checking
- ...

**Utilities (~500 linhas?)**
- Focus management
- Dock management
- State persistence
- ...

**closeEvent (~61 linhas)**
- `closeEvent()` - linha 4287

## 🎯 ESTRATÉGIA DE REFATORAÇÃO

### **Fase 3.0 - Overview e Preparação**
Esta fase documenta a análise e cria subfases para execução.

### **Fase 3.1 - CLI Module (PRIORIDADE ALTA)**
**Target**: Extrair comandos CLI para módulo separado
**Arquivos**:
- `src/cli/commands.py` - Comandos CLI (search, replace, insert, translate, gtranslate, dedupe)
- `src/cli/parser.py` - ArgumentParser setup
- `src/cli/utils.py` - Utilities CLI (split_globs, parse_conditions, build_file_list)

**Redução estimada**: ~530 linhas (-11.7%)
**Complexidade**: BAIXA (funções independentes, bem isoladas)
**ROI**: ALTO (grande redução, baixo risco)

### **Fase 3.2 - JSON Translate Helpers (PRIORIDADE ALTA)**
**Target**: Extrair helpers de tradução JSON
**Arquivos**:
- `src/translators/json_translate_helpers.py` - Funções de tradução

**Redução estimada**: ~400 linhas (-8.8%)
**Complexidade**: MÉDIA (funções relacionadas, algumas dependências)
**ROI**: ALTO (boa redução, médio risco)

### **Fase 3.3 - MainWindow: Dock Factory (PRIORIDADE ALTA)**
**Target**: Extrair métodos de criação de docks para factory
**Arquivos**:
- `src/gui/dock_factory.py` - Factory para criação de docks

**Redução estimada**: ~200 linhas (-4.4%)
**Complexidade**: BAIXA (métodos similares, padrão repetitivo)
**ROI**: MÉDIO (redução moderada, baixo risco)

### **Fase 3.4 - MainWindow: Menu Builder (PRIORIDADE ALTA)**
**Target**: Extrair _build_menu() para builder separado
**Arquivos**:
- `src/gui/menu_builder.py` - Construtor de menus

**Redução estimada**: ~150 linhas (-3.3%)
**Complexidade**: MÉDIA (muitas interações com MainWindow)
**ROI**: MÉDIO (redução moderada, médio risco)

### **Fase 3.5 - MainWindow: Settings Manager (PRIORIDADE MÉDIA)**
**Target**: Extrair lógica de settings/prefs
**Arquivos**:
- `src/gui/window_settings.py` - Gerenciamento de settings da janela

**Redução estimada**: ~150 linhas (-3.3%)
**Complexidade**: MÉDIA (estado compartilhado)
**ROI**: MÉDIO

### **Fase 3.6 - MainWindow: Event Handlers (PRIORIDADE BAIXA)**
**Target**: Extrair handlers para módulos de comportamento
**Arquivos**:
- `src/gui/event_handlers.py` - Event handlers genéricos

**Redução estimada**: ~300 linhas (-6.6%)
**Complexidade**: ALTA (muitas dependências cruzadas)
**ROI**: BAIXO-MÉDIO (redução boa, alto risco)

### **Fase 3.7 - MainWindow: Final Cleanup**
**Target**: Consolidação final e otimizações
**Redução estimada**: ~100 linhas (-2.2%)

## 📊 MÉTRICAS PROJETADAS

```
Estado Inicial:
├── Total: 4533 linhas
├── Module-level: 1650 linhas (25 funções)
└── MainWindow: 2566 linhas (107 métodos)

Após Fase 3.1 (CLI Module):
├── Total: ~4000 linhas (-533)
├── Module-level: ~1120 linhas
└── MainWindow: 2566 linhas

Após Fase 3.2 (JSON Translate):
├── Total: ~3600 linhas (-933)
├── Module-level: ~720 linhas
└── MainWindow: 2566 linhas

Após Fase 3.3 (Dock Factory):
├── Total: ~3400 linhas (-1133)
├── Module-level: ~720 linhas
└── MainWindow: ~2366 linhas

Após Fase 3.4 (Menu Builder):
├── Total: ~3250 linhas (-1283)
├── Module-level: ~720 linhas
└── MainWindow: ~2216 linhas

Após Fase 3.5 (Settings):
├── Total: ~3100 linhas (-1433)
├── Module-level: ~720 linhas
└── MainWindow: ~2066 linhas

Após Fase 3.6 (Event Handlers):
├── Total: ~2800 linhas (-1733)
├── Module-level: ~720 linhas
└── MainWindow: ~1766 linhas

Após Fase 3.7 (Final Cleanup):
├── Total: ~2700 linhas (-1833)
├── Module-level: ~720 linhas
└── MainWindow: ~1666 linhas

Meta Final: 2000-2500 linhas ✅
```

## 🔄 ORDEM DE EXECUÇÃO

1. ✅ **Fase 3.0**: Análise completa e planejamento (ATUAL)
2. 🎯 **Fase 3.1**: CLI Module (PRÓXIMA - ALTA PRIORIDADE)
3. 🎯 **Fase 3.2**: JSON Translate Helpers
4. 🎯 **Fase 3.3**: Dock Factory
5. 🎯 **Fase 3.4**: Menu Builder
6. 📋 **Fase 3.5**: Settings Manager
7. 📋 **Fase 3.6**: Event Handlers
8. 📋 **Fase 3.7**: Final Cleanup

## ⚠️ RISCOS E CONSIDERAÇÕES

### **Riscos Gerais**:
1. **Circular imports**: MainWindow importa muitos módulos, cuidado com ciclos
2. **Estado compartilhado**: Muitos métodos acessam self.app, self.settings, etc.
3. **Signal/slot connections**: Garantir que connections funcionem após refatoração
4. **Testes**: Arquivo crítico, testar extensivamente após cada fase

### **Mitigações**:
1. Usar injeção de dependência onde possível
2. Criar interfaces/protocolos para quebrar dependências
3. Testar cada fase isoladamente antes de prosseguir
4. Manter backups e commits frequentes

## 🎯 PRÓXIMOS PASSOS

1. Começar **Fase 3.1 - CLI Module**
2. Ler funções CLI (linhas ~900-1100)
3. Criar src/cli/commands.py
4. Extrair comandos um por um
5. Testar CLI após cada extração
6. Commit e beep

## 📝 NOTAS

- MainWindow tem 107 métodos - MUITO complexo
- __init__ tem ~130 linhas - pode ser reduzido
- Dock opening methods seguem padrão repetitivo - ideal para factory
- CLI commands são independentes - extração segura
- JSON translate helpers são relacionados - extrair como grupo

---

**Data de criação**: 2024-12-24  
**Status**: 📊 ANÁLISE COMPLETA  
**Próxima fase**: 🎯 Fase 3.1 - CLI Module
