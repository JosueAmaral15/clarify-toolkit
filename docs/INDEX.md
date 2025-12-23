# 📚 Clarify Documentation Index

**Versão**: 2.9.111  
**Última atualização**: 23 de Dezembro de 2025

---

## 🗂️ Estrutura da Documentação

```
docs/
├── INDEX.md                    # Este arquivo (navegação principal)
├── README.md                   # Introdução à documentação
├── PROJECT_SUMMARY.md          # Executive summary do projeto
├── TASKS.md                    # Task tracking (histórico)
│
├── 📋 guides/                  # Guias de uso
│   ├── jsx-extractor-guide.md
│   ├── SHORTCUTS_CUSTOMIZATION.md
│   ├── TOOLTIP_GUIDELINES.md
│   └── ...
│
├── 📐 architecture/            # Documentação de arquitetura
│   └── (componentes, patterns, design)
│
├── 📝 specifications/          # Especificações de features
│   ├── v2.9/                  # Specs v2.9
│   │   ├── v2.9.108-SPECIFICATION.md
│   │   ├── v2.9.109-SPECIFICATION.md (Plugin System)
│   │   ├── v2.9.110-SPECIFICATION.md (Reusable Panels)
│   │   └── v2.9.111-SPECIFICATION.md (Regex Insert)
│   └── v2.10/                 # Specs v2.10
│       └── v2.10.0-PLANNING.md
│
├── 🚀 releases/               # Release notes e reports
│   ├── RELEASE_v2.9.109.md
│   └── FINAL_REPORT_v2.9.md
│
├── 📜 changelog/              # Changelog e automation
│   └── CHANGELOG_AUTOMATION.md
│
├── 🔧 processes/              # Processos de desenvolvimento
│   ├── CI_CD_SETUP.md
│   ├── ERROR_HANDLING.md
│   ├── LOGGING.md
│   └── TEST_LOOP_INFINITY_FIX.md
│
├── 🛡️ protocols/             # Protocolos e checklists
│   ├── PROTOCOL_CHECKLIST.md
│   └── protocolos/            # Protocolos detalhados
│
├── 🩹 patches/                # Patches e rollbacks
│   ├── insert_panel_integration.patch
│   ├── ROLLBACK.md
│   └── ROLLBACK_JSX_EXTRACTOR.md
│
├── 📖 tutorials/              # Tutoriais passo a passo
│
├── 📊 reports/                # Relatórios de análise
│
├── 🗺️ plans/                  # Planejamentos e roadmaps
│
├── 🏃 sprints/                # Documentação de sprints
│
├── 🌐 en/                     # Documentação em inglês
│
└── 🇧🇷 pt/                     # Documentação em português
```

---

## 🚀 Quick Start

### Para Novos Desenvolvedores
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Visão geral do projeto
2. [../README.md](../README.md) - Instruções de instalação
3. [../CONTRIBUTING.md](../CONTRIBUTING.md) - Como contribuir
4. [architecture/](architecture/) - Entender a arquitetura

### Para Usuários
1. [../README.md](../README.md) - Features e instalação
2. [guides/](guides/) - Guias de uso específicos
3. [tutorials/](tutorials/) - Tutoriais passo a passo

---

## 📝 Especificações por Versão

### v2.9 (Current - 100% Complete)

| Feature | Spec | LOC | Tests | Status |
|---------|------|-----|-------|--------|
| **Plugin System** | [v2.9.109](specifications/v2.9/v2.9.109-SPECIFICATION.md) | 800 | 15 | ✅ |
| **Reusable Panels** | [v2.9.110](specifications/v2.9/v2.9.110-SPECIFICATION.md) | 1,140 | 18 | ✅ |
| **Regex Insert** | [v2.9.111](specifications/v2.9/v2.9.111-SPECIFICATION.md) | 1,140 | 14 | ✅ |

**Release**: [RELEASE_v2.9.109.md](releases/RELEASE_v2.9.109.md)  
**Report**: [FINAL_REPORT_v2.9.md](releases/FINAL_REPORT_v2.9.md)

### v2.10 (Planned)

| Feature | Spec | Timeline | Priority |
|---------|------|----------|----------|
| **JSON Translation** | [v2.10.0-PLANNING](specifications/v2.10/v2.10.0-PLANNING.md) | 8h | SHOULD |
| **Reverse Conversion** | [v2.10.0-PLANNING](specifications/v2.10/v2.10.0-PLANNING.md) | 6h | SHOULD |
| **Schema Validation** | [v2.10.0-PLANNING](specifications/v2.10/v2.10.0-PLANNING.md) | 12h | SHOULD |

---

## 🔧 Processos de Desenvolvimento

### CI/CD
- [CI_CD_SETUP.md](processes/CI_CD_SETUP.md) - Configuração de CI/CD
- [../github/workflows/](../.github/workflows/) - GitHub Actions

### Error Handling
- [ERROR_HANDLING.md](processes/ERROR_HANDLING.md) - Estratégias de tratamento de erros
- [LOGGING.md](processes/LOGGING.md) - Sistema de logging

### Testing
- [TEST_LOOP_INFINITY_FIX.md](processes/TEST_LOOP_INFINITY_FIX.md) - Fix de loops infinitos
- [../tests/](../tests/) - Suite de testes

---

## 🛡️ Protocolos e Guidelines

### Development Protocols
- [PROTOCOL_CHECKLIST.md](protocols/PROTOCOL_CHECKLIST.md) - Checklist de desenvolvimento
- [protocolos/](protocolos/) - Protocolos detalhados

### UI/UX Guidelines
- [TOOLTIP_GUIDELINES.md](guides/TOOLTIP_GUIDELINES.md) - Diretrizes para tooltips
- [SHORTCUTS_CUSTOMIZATION.md](guides/SHORTCUTS_CUSTOMIZATION.md) - Customização de atalhos

---

## 📖 Guias Específicos

### Features
- [jsx-extractor-guide.md](guides/jsx-extractor-guide.md) - JSX Parameter Extractor
- [PROJECT_TEMPLATES.md](PROJECT_TEMPLATES.md) - Templates de projeto
- [RECIPES.md](RECIPES.md) - Recipes e exemplos

### Patches e Rollbacks
- [patches/insert_panel_integration.patch](patches/insert_panel_integration.patch) - Patch de integração
- [patches/ROLLBACK.md](patches/ROLLBACK.md) - Procedimentos de rollback

---

## 🌐 Documentação Multilíngue

### Português (pt/)
- Documentação completa em português brasileiro
- Guias, tutoriais e especificações

### English (en/)
- Complete English documentation
- Guides, tutorials and specifications

---

## 📊 Métricas do Projeto

| Métrica | Valor |
|---------|-------|
| **Versão** | 2.9.111 |
| **LOC** | 70,590+ |
| **Testes** | 91/94 (97%) |
| **Coverage** | 97% |
| **Commits** | 215+ |
| **Documentos** | 50+ |

Ver [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) para detalhes completos.

---

## 🔗 Links Rápidos

### Documentação Core
- [README](../README.md) - Página principal
- [CHANGELOG](../CHANGELOG.md) - Histórico de mudanças
- [CONTRIBUTING](../CONTRIBUTING.md) - Guia de contribuição
- [PROJECT_STRUCTURE](../PROJECT_STRUCTURE.md) - Estrutura do projeto
- [SECURITY](../SECURITY.md) - Política de segurança

### Repositório
- [GitHub](https://github.com/JosueAmaral15/clarify)
- [Issues](https://github.com/JosueAmaral15/clarify/issues)
- [Pull Requests](https://github.com/JosueAmaral15/clarify/pulls)

---

## 📝 Como Contribuir com a Documentação

1. **Estrutura**: Siga a organização de pastas acima
2. **Formato**: Use Markdown (.md)
3. **Templates**: Veja [PROJECT_TEMPLATES.md](PROJECT_TEMPLATES.md)
4. **Specs**: Especificações em `specifications/v{major}.{minor}/`
5. **Guias**: Guias práticos em `guides/`
6. **Traduções**: Adicione versões em `en/` ou `pt/`

### Checklist para Nova Documentação
- [ ] Arquivo nomeado corretamente (`kebab-case.md`)
- [ ] Header com título e data
- [ ] Índice (TOC) se >500 linhas
- [ ] Code blocks com syntax highlighting
- [ ] Links funcionais
- [ ] Exemplos práticos
- [ ] Atualizar INDEX.md (este arquivo)

---

## 🔍 Busca Rápida

### Por Categoria
- **Instalação**: [../README.md#instalação](../README.md)
- **Features**: [PROJECT_SUMMARY.md#major-features](PROJECT_SUMMARY.md)
- **API**: [api/](api/)
- **Arquitetura**: [architecture/](architecture/)
- **Testes**: [processes/](processes/)

### Por Versão
- **v2.9**: [specifications/v2.9/](specifications/v2.9/)
- **v2.10**: [specifications/v2.10/](specifications/v2.10/)

---

**Última atualização**: 2025-12-23  
**Mantido por**: Josue Amaral  
**Licença**: MIT
