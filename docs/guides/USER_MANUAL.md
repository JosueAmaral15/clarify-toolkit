# Manual do Usuário — Clarify

## Índice
1. Introdução
2. Instalação
3. Primeiros Passos
4. Funcionalidades Principais
   - Tradução de JSON
   - Reescrita de JSON
   - Substituição de Placeholders
   - Gerenciamento de Arquivos Recentes
   - Preferências e Configurações Persistentes
   - Atalhos de Teclado
   - Barra de Status
5. Sistema de Plugins (v2.0.0+)
6. API REST (v2.0.0+)
7. Sincronização em Nuvem (v2.0.0+)
8. Dicas e Resolução de Problemas
9. Créditos e Licença

---

## 1. Introdução
O Clarify é uma aplicação desktop para manipulação, tradução e gerenciamento de arquivos JSON, com interface intuitiva baseada em docks modulares.

## 2. Instalação
- **Requisitos:** Python 3.9+, PySide6
- Instale via PyPI (em breve):
  ```bash
  pip install clarify-json
  ```
- Ou execute localmente:
  ```bash
  git clone <repo>
  cd clarify
  pip install -r requirements.txt
  python clarify.py
  ```

## 3. Primeiros Passos
- Abra o Clarify e carregue um arquivo JSON.
- Utilize os docks para traduzir, reescrever ou substituir placeholders.
- Salve e gerencie arquivos recentes pelo menu principal.

## 4. Funcionalidades Principais
### Tradução de JSON
- Traduza textos em arquivos JSON para múltiplos idiomas.
- Suporte a tradução automática e manual.

### Reescrita de JSON
- Reescreva chaves/valores conforme regras personalizadas.

### Substituição de Placeholders
- Substitua variáveis e marcadores em textos JSON.

### Gerenciamento de Arquivos Recentes
- Acesse rapidamente arquivos abertos recentemente.

### Preferências e Configurações Persistentes
- Tema, idioma, atalhos e preferências salvos automaticamente.

### Atalhos de Teclado
- **ENTER:** Pressione ENTER em qualquer campo de entrada para executar a ação principal do dock (tradução, busca, extração, etc.)
- **Ctrl+F:** Abra a caixa de busca em qualquer painel de resultados para localizar texto específico
- Consulte a lista completa de atalhos em Ajuda > Atalhos
- Personalize atalhos nas configurações

### Barra de Status
- Exibe dicas, progresso e status de operações.

### Recursos de Produtividade (v1.9.0+)
- **Execução Rápida:** Pressione ENTER em campos de entrada para executar ações sem usar o mouse
- **Busca em Resultados:** Use Ctrl+F para encontrar texto nos painéis de resultado
- **Parser Aprimorado:** GenericScopeParser reescrito com suporte a múltiplos padrões de atributos e expressões balanceadas

## 5. Sistema de Plugins (v2.0.0+)
- Permite extensão de funcionalidades via plugins Python.
- Instale plugins pelo menu ou manualmente na pasta `plugins/`.

## 6. API REST (v2.0.0+)
- Interface HTTP para automação e integração com outros sistemas.
- Documentação da API será fornecida na v2.0.0.

## 7. Sincronização em Nuvem (v2.0.0+)
- Sincronize configurações e arquivos recentes entre dispositivos.
- Suporte a provedores populares (Google Drive, Dropbox, etc.).

## 8. Dicas e Resolução de Problemas
- Consulte logs em `logs/clarify.log`.
- Para problemas de interface, reinicie o aplicativo.
- Dúvidas frequentes: [FAQ](#)

## 9. Créditos e Licença
- Desenvolvido por Josue Amaral e colaboradores.
- Licença MIT.
