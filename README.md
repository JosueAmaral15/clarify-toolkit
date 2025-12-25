# Clarify - Advanced Text Processing & JSON Manipulation System

[![CI](https://github.com/JosueAmaral15/clarify/actions/workflows/ci.yml/badge.svg)](https://github.com/JosueAmaral15/clarify/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/JosueAmaral15/clarify/branch/main/graph/badge.svg)](https://codecov.io/gh/JosueAmaral15/clarify)
[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)](htmlcov/index.html)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.10.1+-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pylint](https://img.shields.io/badge/pylint-9.0+-green.svg)](https://pylint.pycqa.org/)
[![i18n](https://img.shields.io/badge/i18n-7%20languages-blue.svg)](src/i18n/)
[![v2.9](https://img.shields.io/badge/version-2.9.111-blue.svg)](CHANGELOG.md)

## 📋 Descrição

**Clarify** é um sistema completo e modular para processamento de texto e manipulação de JSON, com interface gráfica (GUI) moderna e linha de comando (CLI) poderosa.

### ✨ Versão 2.9.111 - 100% Feature Complete! 🎉
- ✅ **100% COULD HAVE tasks** implementadas (36/36)
- 🔌 **Plugin System** (v2.9.109) - Extensível e modular
- 🎨 **Search/Replace & Insert Panels** (v2.9.110) - Componentes reutilizáveis
- 🎯 **Regex Insert + Memory Register** (v2.9.111) - Captura e reutilização de valores
- 📊 **70,000+ LOC** com arquitetura limpa
- ✅ **97% test coverage** (91/94 testes passing)
- 🚀 **212+ commits** de desenvolvimento iterativo

### 🔥 Destaques v2.9

#### 🔌 Plugin System (v2.9.109)
- **Arquitetura extensível**: Carregamento dinâmico de plugins
- **Hot reload**: Atualiza plugins sem restart
- **2 plugins incluídos**: PostgreSQL Export, Slack Notifications
- **Plugin API**: Base classes e lifecycle hooks
- **Testes**: 15 testes unitários, 100% passing

#### 🎨 Reusable Panels (v2.9.110)
- **SearchReplacePanel**: Busca/substituição modular (280 LOC)
- **InsertPanel**: Inserção de texto modular (220 LOC)
- **AI Processor Integration**: Panels embarcados no AI dock
- **JSON Editor Integration**: Panels no editor principal
- **18 testes**: 100% passing

#### 🎯 Regex Insert + Memory Register (v2.9.111)
- **Memory Register System**: Captura regex com grupos $0-$99
- **RegexInsertPanel**: Workflow 2-step (Capture → Insert)
- **JSON Editor Integration**: Inserção path-based (Inside/Before/After)
- **Smart value parsing**: JSON, number, boolean, null, string
- **14 testes**: MemoryRegister + Panel + Integration

## 🎯 Funcionalidades Principais

### 🔍 Busca e Substituição
- Busca case-sensitive, whole-word, regex
- Substituição com preservação de capitalização
- Filtros avançados por extensão, tamanho, data, conteúdo

### 📝 Inserção de Texto
- 5 modos de inserção (esquerda, direita, substituir, acima, abaixo)
- Inserção condicional baseada em conteúdo
- Filtros avançados com operadores relacionais

### 🔧 JSON Rewriter
- Deduplicação de pares chave-valor
- Join de chaves duplicadas
- Eliminação global de duplicatas
- Suporte para TypeScript/JavaScript objects
- **✅ BUG FIX**: Correção crítica de perda de dados (tipo Obj agora suportado)

### 🌐 JSON Translator
- Tradução de textos usando dicionário JSON/TS
- Suporte para scopes customizados (JSX, string literals)
- Modo reverso (objetos → texto)
- Proteção de placeholders existentes
- Root name configurável

### 🆕 Ferramentas Modulares (v1.0.0)

#### 🔤 Case Converter
- **Conversão entre 4 estilos**: camelCase, PascalCase, snake_case, kebab-case
- Processamento de arquivo único ou diretório recursivo
- Filtro por extensões (.js, .ts, .jsx, .tsx, etc.)
- Suporte para JSON puro e TypeScript/JavaScript objects
- Threading para processamento em background

#### 🔎 JSON Search
- **Busca avançada** em arquivos JSON e TypeScript
- Suporta `export default`, `export const` e object literals
- Busca por chave, valor ou ambos
- Case-sensitive, whole-word e regex
- Indexação inteligente com dot-path notation
- Suporte para arquivos grandes (>10MB)

#### 🎯 JSX Parameter Extractor (NEW in v2.9.0)
- **Extração inteligente de parâmetros** de arquivos JSX/TSX/React
- **Dual-mode selection**: JSX Extractor (file-based) ou Text Converter (text-based)
- **2 modos de parsing**: Attribute mode (key="value") e Tag-content mode (inner text)
- **Path + "Is file?" checkbox**: Seleciona arquivo único ou diretório recursivo
- **Filtros avançados**: 
  - `only_strings`: Filtra apenas strings literais (sem expressões `{var}`)
  - `avoid_keys`: Exclui chaves específicas (ex: className, data-testid)
  - `no_standard`: Remove tags HTML padrão (div, span, p) do output
- **Normalização configurável**: 
  - 4 case styles (snake_case, camelCase, PascalCase, kebab-case)
  - Smart truncation com limit + avoid_cut (word boundary awareness)
  - Uppercase option
- **Output hierárquico JSON**: Estrutura aninhada reflete componente tree
- **Segurança**: Path traversal prevention, file extension validation
- **Extensions filter**: .tsx, .jsx, .js, .ts (customizável)
- **Generic mode**: Delimitadores regex customizados para outros formatos
- Ver documentação completa em [docs/jsx-extractor-guide.md](docs/jsx-extractor-guide.md)

#### 📄 Text Extractor (LEGACY)
- **Modo texto básico**: Conversão simples de texto para JSON
- Use o **JSX Parameter Extractor** para extração de arquivos React/JSX
- Interface de seleção: escolha entre JSX Extractor ou Text Converter

#### 🤖 AI Processor (ENHANCED)
- **Integração com OpenAI** (ChatGPT) e Google Gemini
- **Token counter persistente**: session + lifetime statistics
- **Code fence removal**: Strip automático de \`\`\`json e \`\`\`
- Estatísticas salvas em `~/.clarify_ai_stats.json`
- Monitoramento de custos em tempo real
- Processamento de múltiplos arquivos
- Line-by-line mode para prompts cíclicos

#### 🔄 Placeholder Replacer
- Substituição em lote de placeholders (ex: `{t.key}`)
- Suporte para JSON, CSV e mappings customizados
- Processamento recursivo de diretórios
- Backup automático opcional
- Validation e error reporting

#### 🌐 JSON Translator
- Tradução de textos usando dicionário JSON/TS
- **Scope delimiters** configuráveis via regex
- **Exclusion patterns** para proteger código
- Root variable customizável (default: `t`)
- Modo reverso: `{t.path}` → texto original
- Don't override existing translations
- Backup automático

#### 🔧 JSON Rewriter
- Deduplicação de pares chave-valor
- Join de chaves duplicadas
- Eliminação global de duplicatas
- Suporte para TypeScript/JavaScript objects
- Configuração de indentação (-1 a 16)
- Output: JSON puro ou TS export
- Preserva hierarquia de tags
- Remove duplicatas automaticamente
- Ignora scripts, estilos e comentários
- Suporte para className como chaves opcionais
- Output em JSON ou TypeScript (export default)

#### 🔄 Placeholder Replacer
- Substituição em lote de placeholders (ex: {t.pages.home.title})
- Suporte para arquivos de mapeamento JSON ou CSV
- Estratégia longest-match-first (evita colisões)
- Filtro de escopo com regex (start/end markers)
- Criação automática de backups
- Modo preview (dry-run) antes de aplicar

#### 🤖 AI File Processor
- Integração com OpenAI (ChatGPT) e Google Gemini
- Processamento em lote de arquivos com IA
- Contagem de tokens e estimativa de custo
- Modo line-by-line (prompt diferente por arquivo)
- Limite de bytes configurável por arquivo
- Interrupção de processamento em tempo real
- Salvamento de resultados em arquivo único
- Suporte para múltiplas extensões de arquivo

## � Documentação

### 📚 User Manual (Wiki)

Complete documentation for users:

- **[📖 Wiki Home](docs/wiki/README.md)** - Documentation index and navigation
- **[🚀 Quick Start Guide](docs/wiki/quick-start-guide.md)** - 5-minute tutorial to get started
- **[📋 Features Overview](docs/wiki/features-overview.md)** - Complete feature documentation
- **[❓ FAQ](docs/wiki/faq.md)** - Frequently asked questions
- **[🔧 Troubleshooting](docs/wiki/troubleshooting.md)** - Common problems and solutions
- **[⌨️ Keyboard Shortcuts](docs/wiki/keyboard-shortcuts.md)** - Complete shortcut reference

### 👨‍💻 Developer Documentation

For contributors and developers:

- **[📚 API Documentation](https://josueamaral15.github.io/clarify/)** - Complete API reference (Sphinx)
- **[🤝 Contributing Guide](CONTRIBUTING.md)** - How to contribute to Clarify
- **[📝 Changelog](CHANGELOG.md)** - Version history and changes
- **[📋 Project Structure](PROJECT_STRUCTURE.md)** - Codebase organization
- **[🎯 Tasks & Roadmap](docs/TASKS.md)** - Development tasks and priorities

---

## �📁 Estrutura do Projeto

```
clarify/
├── 📄 clarify.py              # ⭐ Ponto de entrada principal (USE ESTE)
├── 📄 main.py                 # Script de teste/validação modular
│
├── 📁 src/                    # 🆕 Todo código fonte organizado aqui
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # Entry point para: python -m src
│   ├── app.py                # Aplicação completa GUI+CLI (~2,700 linhas)
│   │
│   ├── 📁 core/              # ✅ Funcionalidades principais
│   │   ├── search_replace.py    # Busca e substituição
│   │   ├── insert.py            # Inserção de texto
│   │   └── filters.py           # Filtros avançados
│   │
│   ├── 📁 utils/             # ✅ Utilitários
│   │   ├── file_utils.py        # Operações de arquivo
│   │   ├── text_utils.py        # Processamento de texto
│   │   └── ts_utils.py          # TypeScript/JavaScript
│   │
│   ├── 📁 rewriter/          # ✅ JSON Rewriter
│   │   ├── types.py             # Tipos (Obj, JSONNode)
│   │   ├── rewriter.py          # ⭐ BUG FIX APLICADO
│   │   ├── ts_parser.py         # Parser TS/JS
│   │   ├── operations.py        # Dedupe, join, eliminate
│   │   └── serializer.py        # Serialização
│   │
│   ├── 📁 translators/       # 🚧 JSON Translator (futuro)
│   ├── 📁 ui/                # 🚧 GUI components (futuro)
│   └── 📁 cli/               # 🚧 CLI commands (futuro)
│
├── 📁 docs/                   # 📚 Documentação organizada
│   ├── README.md             # Índice bilíngue
│   ├── REORGANIZATION.md     # Detalhes da reorganização v2.1.0
│   ├── LAUNCHERS.md          # Documentação dos launchers GUI
│   │
│   ├── 📁 architecture/      # Documentação de arquitetura
│   │   ├── ARCHITECTURE.md       # Explicação dos entry points
│   │   ├── ARCHITECTURE_DIAGRAM.txt  # Diagrama visual
│   │   └── STRUCTURE.txt         # Estrutura completa do projeto
│   │
│   ├── 📁 reports/           # Relatórios de análise
│   │   ├── BUG_FIX_REPORT.md     # Correções de bugs documentação (EN)
│   │   ├── BUG_FIX_REPORT_PT.md  # Correções de bugs documentação (PT)
│   │   ├── CODE_BUG_REPORT.md    # Análise de bugs no código (EN)
│   │   └── CODE_BUG_REPORT_PT.md # Análise de bugs no código (PT)
│   │
│   ├── 📁 archive/           # Documentação histórica
│   │   ├── LANGUAGE_FIX.md       # Log da correção de idiomas
│   │   └── project_structure.txt # Estrutura antiga (referência)
│   │
│   ├── 📁 en/                # Documentação em inglês
│   │   ├── README.md             # Navegação
│   │   └── TASKS.md              # Roadmap de desenvolvimento
│   │
│   └── 📁 pt/                # Documentação em português
│       ├── README.md
│       ├── CODE_REVIEW_DETAILED.md
│       ├── CODE_REVIEW_FINAL.md
│       ├── MIGRATION_COMPLETE.md
│       ├── MIGRATION_FINAL_STATUS.md
│       ├── MIGRATION_CHECKLIST.md
│       ├── REORGANIZATION_STATUS.md
│       ├── RENAMING.md
│       └── REVIEW_REPORT.md
│
├── 📁 tests/                  # 🆕 Testes unitários (futuro)
│
├── 📁 archive/                # 🆕 Arquivos históricos
│   ├── backup/               # Backups antigos do código
│   └── old/                  # Versões antigas do projeto
│
├── 📄 clarify_gui.sh         # Launcher script para Linux/Mac
├── 📄 clarify_gui.bat        # Launcher script para Windows
│
├── pyproject.toml            # Poetry configuration
├── poetry.lock               # Dependency lock
└── README.md                 # Este arquivo
```

## 🚀 Como Usar

### Instalação

```bash
git clone https://github.com/JosueAmaral15/clarify.git
cd clarify
pip install PySide6  # Necessário para GUI
```

#### 📦 Dependências Opcionais

O Clarify tem algumas features que requerem bibliotecas adicionais:

**Excel Export** (Exportar estatísticas para .xlsx):
```bash
pip install openpyxl>=3.1.0
```

Se `openpyxl` não estiver instalado, ao tentar exportar para Excel você verá:
> ⚠️ Excel export requires 'openpyxl' package. Install with: pip install openpyxl

**Instalação completa** (todas as dependências):
```bash
pip install -r requirements.txt  # Todas as bibliotecas principais + opcionais
```

### 🖥️ Modo GUI (Recomendado)

```bash
python clarify.py            # Método direto
# OU
python -m src                # Executar como módulo Python
```

### 💻 Modo CLI

```bash
# Busca
python clarify.py search ./src --query "foo" --include "*.ts;*.tsx"

# Substituição
python clarify.py replace ./src --query "foo" --replacement "bar" --all

# Inserção
python clarify.py insert ./src --line 1 --text "HEADER" --mode insert_above

# JSON Translator
python clarify.py translate ./web --dictionary dict.ts --root-name t

# JSON Rewriter (com bug fix)
python clarify.py dedupe en.ts --join-keys --eliminate-duplicates -o en2.ts
```

### 🧪 Validar Arquitetura Modular

```bash
python main.py test
# ✅ src.core.SearchOptions, src.core.InsertMode, src.core.Condition
# ✅ src.utils.walk_files, src.utils.read_text
# ✅ src.rewriter.Obj, src.rewriter.dedupe, src.rewriter.sanitize_keys_and_values
```

### 📚 Uso Programático (Módulos Organizados)

```python
import sys
sys.path.insert(0, '/caminho/para/clarify')

# Busca e substituição
from src.core import SearchOptions, replace_in_text
opts = SearchOptions(case_sensitive=True)
pattern = opts.compile("antigo")
novo, count = replace_in_text(texto, pattern, "novo")

# Inserção
from src.core import InsertMode, insert_at_line
novo_texto = insert_at_line(texto, line_no=10, text="Nova linha", mode=InsertMode.INSERT_ABOVE)

# Filtros avançados
from src.core import Condition, filter_files_by_conditions
from src.utils import walk_files
cond = Condition("content", "contains", "React")
files = list(walk_files("./src"))
filtered = filter_files_by_conditions(files, [cond])

# JSON Rewriter (COM BUG FIX)
from src.rewriter import (
    parse_json_preserving_duplicates_text,
    sanitize_keys_and_values,
    dedupe, join_keys, eliminate_duplicates
)

data = parse_json_preserving_duplicates_text(json_text)
data = sanitize_keys_and_values(data)  # ⭐ Bug fix aplicado aqui
data = join_keys(data)
data = dedupe(data)
final = eliminate_duplicates(data)
```

## 🐛 Bug Fix Crítico Aplicado

**Problema**: JSON Rewriter perdia dados ao processar estruturas `Obj` (lista de tuplas chave-valor).

**Solução**: Adicionado suporte para tipo `Obj` na função `sanitize_keys_and_values()` em `rewriter/rewriter.py`.

**Localização do Fix**:
```python
# rewriter/rewriter.py, linhas ~40-55
def walk(v):
    if isinstance(v, Obj):  # ⭐ CORREÇÃO CRÍTICA
        out = Obj()
        for k, x in v:
            nk = clean_key(k)
            if nk is None:
                continue
            vx = walk(x)
            if drop_empty_values and isinstance(vx, str) and not vx.strip():
                continue
            out.append((nk, vx))
        return out
    # ... continua com dict e list
```

## 📊 Status da Reorganização

### ✅ Reorganização Completa (v2.1.0)
- **src/** - Todo código fonte organizado em um pacote Python
- **src/core/** - 4 arquivos, ~260 linhas (SearchOptions, InsertMode, Condition, filtros)
- **src/utils/** - 4 arquivos, ~270 linhas (file_utils, text_utils, ts_utils)
- **src/rewriter/** - 6 arquivos, ~690 linhas (tipos, parser, operações, serializer + bug fix)
- **src/app.py** - Aplicação completa GUI+CLI (~2,700 linhas)
- **docs/** - Documentação organizada por idioma (en/, pt/)
- **archive/** - Backups e versões antigas arquivados

### 🚧 Planejado para Futuras Versões
- **src/translators/** - Extrair JSON Translator do app.py
- **src/ui/** - Extrair componentes GUI do app.py
- **src/cli/** - Extrair comandos CLI do app.py
- **tests/** - Adicionar testes unitários

## ⚠️ Importante

**Para uso completo, utilize `python clarify.py`** - ponto de entrada principal.

**Alternativa**: `python -m src` - executar como módulo Python.

**Para validação modular, use `python main.py test`** - valida arquitetura modular.

**Arquivo principal**: `src/app.py` contém toda a aplicação GUI+CLI (~2,700 linhas).

## 🧪 Validação

```bash
# Validar arquitetura modular
python main.py test

# Executar aplicação completa
python clarify.py

# Executar como módulo Python
python -m src

# Ver ajuda CLI
python clarify.py --help
```

## 📚 Documentação Adicional

### 📖 Documentação em Inglês (docs/en/)
- **TASKS.md** - Development roadmap (MoSCoW priorities)
- **CODE_REVIEW_FINAL.md** - Executive code review summary
- **CODE_REVIEW_DETAILED.md** - Comprehensive code analysis
- **MIGRATION_COMPLETE.md** - Complete migration history
- **RENAMING.md** - File renaming documentation
- **REORGANIZATION_STATUS.md** - Module organization status

### 📖 Documentação em Português (docs/pt/)
- Em desenvolvimento - contribuições bem-vindas!

### 🔗 Acesso Rápido
- **docs/README.md** - Índice bilíngue de toda documentação
- **docs/ORPHANED_CODE_INTEGRATION_PLAN.md** - Plano de integração de código órfão (25h de features prontas!)

### 🛠️ Desenvolvimento e Planos
- **docs/refactoring/** - Histórico completo de refatorações (14 arquivos)
- **docs/ORPHANED_CODE_INTEGRATION_PLAN.md** - Plano detalhado para integrar ~2.500 linhas de código implementado mas não utilizado
  - 7 itens identificados (MinimalProcessingModal, ManualCheckDialog, Advanced Extractor, etc.)
  - Roadmap de 3 sprints (3 semanas)
  - 5 novas features + 3 ferramentas de desenvolvimento melhoradas
- **scripts/refactor_app.py** - Ferramenta automatizada de refatoração
- **tests/test_docks_factory.py** - Teste de integração DockFactory
- **load_tests/** - Sistema completo de load testing (a integrar)
- **benchmarks/** - Sistema de benchmarks de performance (a integrar)

## 👤 Autor

**Josué Amaral**  
GitHub: [@JosueAmaral15](https://github.com/JosueAmaral15)  
Data: 2025/10/01

## 📄 Licença

MIT License

---

## 💡 Dica

Para melhor experiência:
- **GUI (Launcher)**: Clique duplo em `clarify_gui.bat` (Windows) ou `clarify_gui.sh` (Linux/Mac)
- **GUI (Python)**: `python clarify.py` ou `python -m src` (interface completa)
- **CLI**: `python clarify.py <comando>` (linha de comando)
- **Validação**: `python main.py test` (validar arquitetura modular)
- **Documentação**: `docs/README.md` (índice bilíngue)

### 🚀 Launchers GUI
Criados scripts de conveniência para iniciar a GUI com um clique:
- **Windows**: `clarify_gui.bat` - Double-click para executar
- **Linux/Mac**: `clarify_gui.sh` - Double-click ou `./clarify_gui.sh`
- Ambos verificam dependências e oferecem instalar PySide6 se necessário
- Ver [LAUNCHERS.md](LAUNCHERS.md) para detalhes

## 📝 Changelog v2.1.0 (2025-11-23)

### 🎉 Reorganização Completa
- ✅ Todo código movido para `src/` (arquitetura modular padrão Python)
- ✅ Código movido para `src/app.py` (clareza e consistência)
- ✅ Criado `src/__init__.py` e `src/__main__.py` (suporte a `python -m src`)
- ✅ Documentação organizada por idioma: `docs/en/` e `docs/pt/`
- ✅ Arquivos históricos movidos para `archive/` (backup/, old/)
- ✅ Imports atualizados: `from src.core import ...`
- ✅ Lazy loading de PySide6 (CLI funciona sem GUI)
- ✅ Estrutura pronta para testes unitários em `tests/`

### 🔧 Melhorias Técnicas
- Suporte a execução como módulo: `python -m src`
- Validação de arquitetura: `python main.py test`
- Imports relativos no `src/app.py`
- Classes GUI condicionadas a `_PYSIDE`

### 📚 Documentação
- README.md atualizado com nova estrutura
- Documentação bilíngue (docs/en/, docs/pt/)
- Changelog desta versão

⭐ **Dê uma estrela se este projeto foi útil!**
