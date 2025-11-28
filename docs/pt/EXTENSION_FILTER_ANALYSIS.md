# Análise: Onde Filtro de Extensões Faz Sentido

## ✅ FAZ SENTIDO (Processamento genérico de arquivos)

### 1. Search/Replace Panel
- **Por quê**: Processa qualquer tipo de arquivo de texto
- **Uso comum**: Buscar em `.py`, `.js`, `.tsx`, `.md`, etc.
- **Decisão**: ✅ **MANTER** filtro de extensões

### 2. Insert Panel
- **Por quê**: Insere texto em qualquer arquivo de texto
- **Uso comum**: Headers, footers, código em múltiplos tipos
- **Decisão**: ✅ **MANTER** filtro de extensões

### 3. Case Converter
- **Por quê**: Converte case em código de qualquer linguagem
- **Uso comum**: Processar `.js`, `.py`, `.tsx`, `.json`
- **Decisão**: ✅ **MANTER** filtro de extensões

### 4. AI File Processor
- **Por quê**: Processa múltiplos tipos de arquivo com IA
- **Uso comum**: Refatorar código, documentação, etc.
- **Decisão**: ✅ **MANTER** filtro de extensões

### 5. Placeholder Replacer
- **Por quê**: Substitui placeholders em HTML, JSX, templates
- **Uso comum**: Processar `.html`, `.jsx`, `.tsx`, `.md`
- **Decisão**: ✅ **MANTER** filtro de extensões

### 6. Text Extractor
- **Por quê**: Extrai texto de HTML/JSX de múltiplas extensões
- **Uso comum**: Processar `.html`, `.jsx`, `.tsx`
- **Decisão**: ✅ **MANTER** filtro de extensões

---

## ❌ NÃO FAZ SENTIDO (Específico para JSON/TS)

### 1. JSON Search
- **Por quê**: Trabalha APENAS com `.json`, `.ts`, `.tsx`, `.js`, `.jsx`
- **Extensões fixas**: Hardcoded no código
- **Decisão**: ❌ **REMOVER** filtro de extensões (redundante)

### 2. JSON Translate
- **Por quê**: Traduz arquivos JSON/TS com dicionário JSON/TS
- **Extensões fixas**: `.json`, `.ts`, `.tsx`, `.js`, `.jsx`
- **Decisão**: ❌ **REMOVER** filtro de extensões (redundante)

### 3. JSON Rewriter
- **Por quê**: Reescreve APENAS arquivos JSON/TS
- **Extensões fixas**: `.json`, `.ts`, `.tsx`, `.js`, `.jsx`
- **Decisão**: ❌ **REMOVER** filtro de extensões (redundante)

---

## 📊 Resumo de Decisões

| Módulo | Filtro Extensões | Motivo |
|--------|------------------|--------|
| Search/Replace | ✅ **MANTER** | Genérico |
| Insert | ✅ **MANTER** | Genérico |
| Case Converter | ✅ **MANTER** | Multi-linguagem |
| AI Processor | ✅ **MANTER** | Multi-tipo |
| Placeholder Replacer | ✅ **MANTER** | Templates diversos |
| Text Extractor | ✅ **MANTER** | HTML/JSX variados |
| JSON Search | ❌ **REMOVER** | Apenas JSON/TS |
| JSON Translate | ❌ **REMOVER** | Apenas JSON/TS |
| JSON Rewriter | ❌ **REMOVER** | Apenas JSON/TS |

---

## 🎯 Implementação

### Para Módulos Genéricos (Search/Replace, Insert)
```python
# Adicionar checkbox para habilitar/desabilitar
self.chk_use_ext_filter = QCheckBox("Use extension filter")
self.chk_use_ext_filter.setChecked(True)  # Default: enabled

# Só aplicar se checkbox marcado
if self.chk_use_ext_filter.isChecked() and extensions_text:
    # Aplicar filtro
else:
    # Pular filtro
```

### Para Módulos JSON (Search, Translate, Rewriter)
```python
# REMOVER completamente:
# - Campo ed_extensions
# - Label "Extensions:"
# - Lógica de parsing de extensões

# MANTER apenas:
# - Include globs (para patterns avançados)
# - Exclude globs (para node_modules, etc.)
```

---

## 🔄 Migração

### Antes (v2.9.0 - Incorreto)
```
JSON Search:
  Extensions: .json,.ts  ← REDUNDANTE
  Include globs: ...
```

### Depois (v2.9.1 - Correto)
```
JSON Search:
  [Sem campo Extensions - removido]
  Include globs: ...
```

### Search/Replace (mantém):
```
Search/Replace:
  [✓] Use extension filter
  Extensions: .py,.js,.tsx
  Include globs: ...
```
