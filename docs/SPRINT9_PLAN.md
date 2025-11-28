# Sprint 9 — v2.0.0: Plugin System, REST API, Cloud Sync

## Objetivo
Adicionar extensibilidade ao Clarify com sistema de plugins, expor funcionalidades via API REST e permitir sincronização de configurações/arquivos em nuvem.

## Roadmap
1. Sistema de Plugins
   - Carregamento dinâmico de módulos Python (pasta `src/plugins/`)
   - Interface base para plugins (PluginBase)
   - Menu de gerenciamento de plugins
   - Exemplo de plugin (ex: exportar JSON para CSV)
2. API REST
   - Servidor HTTP embutido (FastAPI ou Flask)
   - Endpoints: tradução, reescrita, arquivos recentes, status
   - Autenticação básica
3. Sincronização em Nuvem
   - Abstração para provedores (Google Drive, Dropbox, etc.)
   - Sincronização de configurações e arquivos recentes
   - UI para login e status de sincronização

## Tarefas
- [ ] Definir arquitetura de plugins e criar PluginBase
- [ ] Implementar carregador de plugins
- [ ] Criar exemplo de plugin
- [ ] Integrar menu de plugins na UI
- [ ] Adicionar servidor REST (FastAPI/Flask)
- [ ] Implementar endpoints principais
- [ ] Adicionar autenticação
- [ ] Criar abstração de cloud sync
- [ ] Implementar integração com ao menos um provedor
- [ ] UI para status/login de nuvem
- [ ] Testes automatizados para cada módulo

## Observações
- Plugins e API REST devem ser opcionais e seguros.
- Sincronização em nuvem pode ser expandida para múltiplos provedores.
