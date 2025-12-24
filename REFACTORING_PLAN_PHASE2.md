# REFATORAÇÃO FASE 2 - DOCKS GRANDES
**Status**: EM ANDAMENTO
**Data**: 24/12/2024
**Versão**: v2.9.114 (continuação)

## 📋 Objetivo
Refatorar os 3 arquivos dock maiores para melhorar manutenibilidade:
- ai_processor_dock.py (1284 linhas)
- json_rewriter_dock.py (1229 linhas)
- set_operations_dock.py (1148 linhas)

**Total**: 3661 linhas → Meta: ~2500-2800 linhas (redução de ~25%)

---

## 🎯 Fase 2.1: AI Processor Dock (1284 linhas)

### Análise de Componentes
```
ai_processor_dock.py (1284 linhas):
├── PathEntry (64 linhas)              # Widget de entrada de path
├── AIProcessorWorker (47 linhas)      # Background worker
└── AIProcessorDock (1173 linhas)      # Dock principal (MUITO GRANDE)
    ├── _setup_ui() (343 linhas)       # Setup da interface
    ├── Statistics (100 linhas)        # Gestão de estatísticas
    ├── Models cache (70 linhas)       # Cache de modelos
    ├── Advanced conditions (150 linhas) # Filtros avançados
    └── Event handlers (510 linhas)    # Handlers diversos
```

### Estratégia de Extração

**2.1.1 - Extrair PathEntry para widgets/** ✅
- Classe: `PathEntry` (64 linhas)
- Destino: `src/gui/widgets/path_entry.py`
- Razão: Widget reutilizável

**2.1.2 - Extrair AIProcessorWorker para workers/**
- Classe: `AIProcessorWorker` (47 linhas)
- Destino: `src/gui/workers/ai_processor_worker.py`
- Razão: Worker específico de AI

**2.1.3 - Extrair gestão de estatísticas**
- Classes/métodos: Stats tracking (100 linhas)
- Destino: `src/gui/ai_processor/stats_manager.py`
- Conteúdo:
  - `_load_lifetime_stats_early()`
  - `_load_lifetime_stats()`
  - `_save_lifetime_stats()`
  - `_update_stats_display()`
  - `_strip_code_fences()`

**2.1.4 - Extrair gestão de modelos AI**
- Classes/métodos: Models cache (70 linhas)
- Destino: `src/gui/ai_processor/models_manager.py`
- Conteúdo:
  - `_load_models_cache()`
  - `_save_models_cache()`
  - `_refresh_models()`
  - `_on_provider_changed()`

**2.1.5 - Extrair advanced conditions UI**
- Classes/métodos: Conditions (150 linhas)
- Destino: `src/gui/ai_processor/conditions_ui.py`
- Conteúdo:
  - `_add_condition_row()`
  - `_clear_all_conditions()`
  - `_get_conditions()`
  - `_apply_advanced_conditions()`
  - `_save_advanced_conditions_preferences()`
  - `_load_advanced_conditions_preferences()`

**Meta Fase 2.1**: 1284 → ~850 linhas (redução de ~430 linhas - 33%)

---

## 🎯 Fase 2.2: JSON Rewriter Dock (1229 linhas)

### Análise de Componentes
```
json_rewriter_dock.py (1229 linhas):
├── JSONRewriterWorker (50 linhas)    # Background worker
└── JSONRewriterDock (1179 linhas)    # Dock principal
    ├── _setup_ui() (400 linhas)      # Setup da interface
    ├── Rules management (200 linhas)  # Gestão de regras
    ├── Preview (150 linhas)           # Sistema de preview
    └── Event handlers (429 linhas)    # Handlers diversos
```

### Estratégia de Extração

**2.2.1 - Extrair JSONRewriterWorker**
- Classe: `JSONRewriterWorker` (50 linhas)
- Destino: `src/gui/workers/json_rewriter_worker.py`

**2.2.2 - Extrair rules management**
- Métodos de gestão de regras (200 linhas)
- Destino: `src/gui/json_rewriter/rules_manager.py`

**2.2.3 - Extrair preview system**
- Preview panel e lógica (150 linhas)
- Destino: `src/gui/json_rewriter/preview_panel.py`

**Meta Fase 2.2**: 1229 → ~850 linhas (redução de ~380 linhas - 31%)

---

## 🎯 Fase 2.3: Set Operations Dock (1148 linhas)

### Análise de Componentes
```
set_operations_dock.py (1148 linhas):
├── SetOperationsWorker (45 linhas)   # Background worker
└── SetOperationsDock (1103 linhas)   # Dock principal
    ├── _setup_ui() (350 linhas)      # Setup da interface
    ├── Operations (200 linhas)        # Operações de conjunto
    ├── Venn diagram (150 linhas)      # Visualização
    └── Event handlers (403 linhas)    # Handlers diversos
```

### Estratégia de Extração

**2.3.1 - Extrair SetOperationsWorker**
- Classe: `SetOperationsWorker` (45 linhas)
- Destino: `src/gui/workers/set_operations_worker.py`

**2.3.2 - Extrair Venn diagram**
- Visualização Venn (150 linhas)
- Destino: `src/gui/set_operations/venn_widget.py`

**2.3.3 - Extrair operations logic**
- Lógica de operações (200 linhas)
- Destino: `src/gui/set_operations/operations_manager.py`

**Meta Fase 2.3**: 1148 → ~800 linhas (redução de ~350 linhas - 30%)

---

## 📊 Estatísticas Esperadas

### Antes
```
ai_processor_dock.py:     1284 linhas
json_rewriter_dock.py:    1229 linhas
set_operations_dock.py:   1148 linhas
─────────────────────────────────────
Total:                    3661 linhas
```

### Depois (Projetado)
```
ai_processor_dock.py:      ~850 linhas (-430, -33%)
json_rewriter_dock.py:     ~850 linhas (-380, -31%)
set_operations_dock.py:    ~800 linhas (-350, -30%)
─────────────────────────────────────
Total arquivos principais: 2500 linhas (-1161, -32%)

Novos módulos criados:    ~1200 linhas
```

### Benefícios
✅ Docks principais mais focados e gerenciáveis
✅ Workers isolados para melhor testabilidade
✅ Widgets reutilizáveis
✅ Managers especializados
✅ Melhor organização da arquitetura

---

## 🏗️ Nova Arquitetura

```
src/gui/
├── widgets/                 # Widgets reutilizáveis
│   └── path_entry.py       # PathEntry widget
│
├── workers/                 # Background workers
│   ├── ai_processor_worker.py
│   ├── json_rewriter_worker.py
│   └── set_operations_worker.py
│
├── ai_processor/           # Componentes AI Processor
│   ├── __init__.py
│   ├── stats_manager.py
│   ├── models_manager.py
│   └── conditions_ui.py
│
├── json_rewriter/          # Componentes JSON Rewriter
│   ├── __init__.py
│   ├── rules_manager.py
│   └── preview_panel.py
│
└── set_operations/         # Componentes Set Operations
    ├── __init__.py
    ├── venn_widget.py
    └── operations_manager.py
```

---

## 📝 Progresso

- [x] Fase 2.1: AI Processor Dock (PARCIAL - Componentes principais)
  - [x] 2.1.1: PathEntry extraction (64 linhas) - Commit 1a72509
  - [x] 2.1.2: AIProcessorWorker extraction (46 linhas) - Commit 24733eb
  - [~] 2.1.3-5: Mantidos no dock (stats, models, conditions)
    * Razão: Complexidade alta, dependências internas
    * Decisão: Focar em extrações mais impactantes

- [ ] Fase 2.2: JSON Rewriter Dock
  - [ ] 2.2.1: Worker extraction
  - [ ] 2.2.2: Rules manager extraction
  - [ ] 2.2.3: Preview panel extraction

- [ ] Fase 2.3: Set Operations Dock
  - [ ] 2.3.1: Worker extraction
  - [ ] 2.3.2: Venn widget extraction
  - [ ] 2.3.3: Operations manager extraction

---

## ⚠️ Considerações

1. **Testes**: Testar após cada extração
2. **Imports**: Atualizar todos os imports
3. **Dependências**: Verificar dependências circulares
4. **Backwards compatibility**: Manter compatibilidade
5. **Commits**: Commit após cada sub-fase completa
