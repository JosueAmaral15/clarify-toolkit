# Revisão de Código - Text to JSON Converter
**Data**: 02/12/2025  
**Arquivo**: `add/main.py`  
**Protocolo**: Simplicidade 1 v1.7 - Etapa 8.5

## Resumo Executivo
- **Total de Problemas Encontrados**: A determinar durante revisão
- **Severidade Alta**: A determinar
- **Severidade Média**: A determinar
- **Severidade Baixa**: A determinar

---

## 1. Omissão ❌

### 1.1 Validação de Entrada
- [ ] **PROBLEMA**: Falta validação se `paths` está vazio em `_run()`
  - **Linha**: ~1715
  - **Código Atual**: `if not paths:` apenas mostra warning
  - **Impacto**: Usuário pode tentar executar sem paths válidos
  - **Status**: ✅ OK - Validação existe

### 1.2 Tratamento de Erro
- [ ] **PROBLEMA**: Exceções genéricas em múltiplos lugares
  - **Linha**: ~1790 (`except Exception as e:`)
  - **Impacto**: Erro específico não é identificado
  - **Correção Sugerida**: Capturar exceções específicas (IOError, ValueError, etc)
  - **Status**: ⚠️ REVISAR

### 1.3 Cleanup de Recursos
- [ ] **PROBLEMA**: Arquivos podem não ser fechados em caso de exceção
  - **Linha**: ~1300-1350 (método `run()` de Extractor)
  - **Impacto**: File descriptors podem vazar
  - **Correção Sugerida**: Usar `with open()` sempre
  - **Status**: ✅ OK - Já usa `with open()`

### 1.4 Documentação
- [x] **PROBLEMA**: Docstrings incompletas ou ausentes
  - **Linha**: Várias classes e métodos
  - **Impacto**: Dificulta manutenção
  - **Correção Sugerida**: Adicionar docstrings com Args, Returns, Raises
  - **Status**: ⚠️ MELHORAR

---

## 2. Ambiguidade 🤔

### 2.1 Nomes de Variáveis
- [x] **PROBLEMA**: Variável `s` genérica em múltiplos lugares
  - **Linha**: ~130 (`def normalize_token(s: str, ...)`)
  - **Impacto**: Reduz legibilidade
  - **Correção Sugerida**: Renomear para `text` ou `token_str`
  - **Status**: ⚠️ MELHORAR

### 2.2 Magic Numbers
- [x] **PROBLEMA**: Número mágico `500` sem constante
  - **Linha**: ~798 (`tail = text[mstart.end(): mstart.end()+500]`)
  - **Impacto**: Não fica claro o propósito
  - **Correção Sugerida**: `ATTR_SCAN_WINDOW = 500`
  - **Status**: ⚠️ MELHORAR

- [x] **PROBLEMA**: Número mágico `50` em preview
  - **Linha**: ~1779 (`if len(matches) >= 50:`)
  - **Impacto**: Não fica claro o limite
  - **Correção Sugerida**: `MAX_PREVIEW_MATCHES = 50`
  - **Status**: ⚠️ MELHORAR

### 2.3 Lógica Complexa
- [x] **PROBLEMA**: Método `_custom_find_matching_close_span` muito complexo
  - **Linha**: ~265-370
  - **Impacto**: Difícil de entender e manter
  - **Correção Sugerida**: Quebrar em métodos menores
  - **Status**: ⚠️ MELHORAR

---

## 3. Fato Incorreto ❗

### 3.1 Operadores Lógicos
- [ ] **PROBLEMA**: Verificação em `check_value_if_it_is_just_string`
  - **Linha**: ~1137 (verifica `\?\s{0,3}\(`)
  - **Impacto**: Pode não detectar todos os casos
  - **Correção Sugerida**: Revisar regex
  - **Status**: 🔍 INVESTIGAR

### 3.2 Comparações
- [ ] **PROBLEMA**: Verificação `if n <= 0 or len(text) <= n:`
  - **Linha**: ~105
  - **Impacto**: `n == 0` deveria retornar string vazia?
  - **Correção Sugerida**: Clarificar comportamento esperado
  - **Status**: 🔍 INVESTIGAR

---

## 4. Redundância ♻️

### 4.1 Código Duplicado
- [x] **PROBLEMA**: Padrão de iteração de paths duplicado
  - **Linha**: ~1760-1790 (loop `for path, is_file in paths:`)
  - **Impacto**: Manutenção duplicada
  - **Correção Sugerida**: Extrair método `_process_single_path()`
  - **Status**: ⚠️ MELHORAR

### 4.2 Imports Não Utilizados
- [ ] **PROBLEMA**: Verificar imports não usados
  - **Correção Sugerida**: Executar `pylint --disable=all --enable=unused-import`
  - **Status**: 🔍 VERIFICAR

### 4.3 Variáveis Não Usadas
- [ ] **PROBLEMA**: Verificar variáveis criadas mas não usadas
  - **Correção Sugerida**: Executar `vulture add/main.py`
  - **Status**: 🔍 VERIFICAR

### 4.4 Debug Prints
- [x] **PROBLEMA**: Múltiplos `#print()` comentados
  - **Linha**: ~80, 82, 149, 159, 166, etc
  - **Impacto**: Poluição visual
  - **Correção Sugerida**: Remover ou converter para logging
  - **Status**: ❌ REMOVER

---

## 5. Inconsistência ⚠️

### 5.1 Nomenclatura
- [x] **PROBLEMA**: Mistura de `camelCase` e `snake_case`
  - **Linha**: Vários lugares (ex: `check_value_if_it_is_just_string` vs `ATTR_DQ_RE`)
  - **Impacto**: Falta de padrão
  - **Correção Sugerida**: Padronizar tudo para `snake_case` (Python PEP8)
  - **Status**: ✅ OK - Python usa snake_case para métodos

### 5.2 Formatação
- [ ] **PROBLEMA**: Espaçamento inconsistente
  - **Correção Sugerida**: Executar `black add/main.py`
  - **Status**: 🔍 EXECUTAR

### 5.3 Tratamento de Erro
- [x] **PROBLEMA**: Alguns lugares usam `try/except`, outros não
  - **Linha**: Vários métodos
  - **Impacto**: Comportamento inconsistente
  - **Correção Sugerida**: Padronizar tratamento de erro
  - **Status**: ⚠️ PADRONIZAR

---

## 6. Falta de Integração 🔗

### 6.1 CLI Subcomando
- [x] **PROBLEMA**: CLI funciona standalone mas não integrado ao Clarify
  - **Linha**: `if __name__ == "__main__":`
  - **Impacto**: Não está disponível via `clarify text2json`
  - **Correção Sugerida**: Adicionar ao `main.py` do Clarify
  - **Status**: ⚠️ INTEGRAR

### 6.2 Botões GUI
- [ ] **PROBLEMA**: Verificar se todos os botões têm handlers
  - **Linha**: ~1520-1540 (botões Run e Save)
  - **Status**: ✅ OK - Conectados corretamente

### 6.3 Imports
- [ ] **PROBLEMA**: Módulo não importado em `__init__.py`
  - **Linha**: N/A (arquivo standalone)
  - **Correção Sugerida**: Adicionar ao package structure
  - **Status**: ⚠️ ESTRUTURAR

---

## 7. Menor Coesão 🧩

### 7.1 Classe `Extractor`
- [x] **PROBLEMA**: Classe faz muitas coisas (parse, normalize, filter, merge, export)
  - **Linha**: ~870-1350
  - **Impacto**: Dificulta testes e manutenção
  - **Correção Sugerida**: Separar em classes menores
    - `TextParser` (parse JSX/generic)
    - `PathNormalizer` (normalize tokens)
    - `JSONBuilder` (build JSON structure)
    - `ResultExporter` (export to different formats)
  - **Status**: ⚠️ REFATORAR (Opcional - funciona mas não é ideal)

### 7.2 Método `process_text`
- [x] **PROBLEMA**: Método faz parsing + filtering + building
  - **Linha**: ~1150-1240
  - **Impacto**: Método muito longo (~90 linhas)
  - **Correção Sugerida**: Quebrar em submétodos
  - **Status**: ⚠️ QUEBRAR (Opcional)

---

## 8. Maior Acoplamento 🔗

### 8.1 Dependências
- [ ] **PROBLEMA**: `MainWindow` acessa diretamente `Extractor`
  - **Linha**: ~1735-1760
  - **Impacto**: Dificulta testes unitários
  - **Correção Sugerida**: Interface/abstração entre GUI e lógica
  - **Status**: ⚠️ MELHORAR (Opcional - aceitável para ferramenta pequena)

### 8.2 Imports Circulares
- [ ] **PROBLEMA**: Verificar imports circulares
  - **Correção Sugerida**: Não há outros módulos ainda
  - **Status**: ✅ OK - Arquivo standalone

---

## 9. Informação Estranha 🗑️

### 9.1 Debug Prints
- [x] **PROBLEMA**: Múltiplos `#print(...)` comentados
  - **Linha**: ~80, 82, 149, 159, 166, 233, 253, etc (20+ ocorrências)
  - **Impacto**: Poluição de código
  - **Correção Sugerida**: Remover todos
  - **Status**: ❌ CRÍTICO - REMOVER

### 9.2 Código Comentado
- [ ] **PROBLEMA**: Verificar código comentado sem justificativa
  - **Linha**: Vários `#` sem razão clara
  - **Correção Sugerida**: Remover ou justificar
  - **Status**: 🔍 VERIFICAR

### 9.3 TODOs
- [x] **PROBLEMA**: TODOs na docstring do topo
  - **Linha**: ~32-35
  - **Impacto**: Funcionalidades incompletas documentadas?
  - **Correção Sugerida**: Resolver ou mover para TASKS.md
  - **Status**: ⚠️ DOCUMENTAR

### 9.4 Comentários Desatualizados
- [ ] **PROBLEMA**: Comentários podem estar desatualizados
  - **Linha**: A revisar durante testes
  - **Status**: 🔍 VERIFICAR DURANTE TESTES

---

## Priorização de Correções

### 🔴 **CRÍTICO (Fazer Agora)**
1. ❌ Remover todos os debug prints comentados (~20+ ocorrências)
2. ⚠️ Adicionar constantes para magic numbers (500, 50, etc)
3. ⚠️ Melhorar tratamento de exceções específicas

### 🟡 **IMPORTANTE (Fazer Logo)**
4. ⚠️ Integrar CLI ao sistema Clarify principal
5. ⚠️ Adicionar docstrings completas
6. ⚠️ Renomear variáveis ambíguas (`s`, `t`, etc)

### 🟢 **DESEJÁVEL (Fazer Quando Possível)**
7. ⚠️ Refatorar classe `Extractor` (separar responsabilidades)
8. ⚠️ Quebrar método `process_text` em submétodos
9. ⚠️ Executar formatador automático (black + isort)

---

## Ações Imediatas

### Etapa 1: Limpeza Crítica
```bash
# Remover debug prints comentados
sed -i '/^\s*#print(/d' add/main.py

# Formatação automática
black add/main.py
isort add/main.py

# Verificar imports não usados
pylint --disable=all --enable=unused-import add/main.py
```

### Etapa 2: Constantes
```python
# Adicionar no topo após imports
# ----------------------------- Constants -------------------------------------

ATTR_SCAN_WINDOW_SIZE = 500  # Characters to scan for attributes after tag
MAX_PREVIEW_MATCHES = 50     # Maximum matches to show in scope preview
MAX_SCROLL_HEIGHT = 150      # Maximum height for paths scroll area
SPLITTER_SIZES = [400, 600]  # Default splitter sizes (40% controls, 60% results)
```

### Etapa 3: Testes
- Testar CLI com arquivo de exemplo
- Testar GUI com múltiplos paths
- Verificar preview de scope
- Validar outputs JSON

---

## Status Final
- [ ] **Revisão Completa**: Em progresso
- [ ] **Correções Aplicadas**: Pendente
- [ ] **Testes Executados**: Pendente
- [ ] **Documentação Atualizada**: Pendente
- [ ] **Pronto para Commit**: Não

**Próximo Passo**: Aplicar correções críticas e executar testes.
