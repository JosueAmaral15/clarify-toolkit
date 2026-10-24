# Reconciliacao De Requisitos - 24/10/2026

## Escopo

Esta revisao mapeia integralmente os 45 apontamentos de
`docs/new-clarify-tasks2.txt` contra o roadmap, codigo e testes atuais. Ela
organiza requisitos; nao afirma que as novas funcionalidades foram entregues.

Resultado canonico:

- ponto de partida: 55 tarefas abertas;
- tarefas existentes ampliadas: 6 IDs;
- tarefas novas: 31;
- total atual: 86 tarefas abertas;
- documentos Markdown depois deste relatorio: 861;
- arquivos Markdown com pelo menos um `- [ ]`: 295.

## Evidencia Atual

- O crash de 21/10 registra `TypeError: options_changed() only accepts 0
  argument(s), 1 given!`. A assinatura atual do Find aceita `_checked`, mas isso
  nao prova qual conexao produziu o relatorio; foi criada investigacao propria.
- `TerminalDock` usa `QProcess` para um comando explicito, sem PTY ou shell
  interativo. O campo fica acima da saida e ha botoes Run/Stop.
- Information Structure oferece saida estrutural JSON; os exemplos externos de
  Cytoscape e `math-tree-expression` existem e precisam de auditoria de codigo e
  licenca antes de reutilizacao.
- Clock possui uma pagina Clock, um stopwatch e um timer; nao ha colecoes de
  alarmes, cronometros ou timers.
- O plugin `plugins/slack_notifications` existe e usa webhook Slack. A migracao
  para Discord nao deve preservar nomes, URLs ou payloads Slack por acidente.
- Lynx e integrado como renderizacao limitada via `lynx -dump`. Uma pagina que
  exige navegador moderno nao prova, sozinha, que o Lynx inteiro e inviavel.
- Calculator Memory Slots guarda cinco resultados JSON persistentes (A-E),
  estatisticas, comparacao e operacoes. Formula Builder ja possui steps, templates
  e executor, mas isso nao prova que o fluxo atual atende ao modelo mental do
  usuario.

## Mapeamento Integral

| Item | Decisao canonica |
| ---: | --- |
| 1 | Novo `CE-CODE-FOLDING-01`. |
| 2 | Novo `CE-FIND-STATE-HISTORY-01`, incluindo Clear e persistencia delimitada. |
| 3 | Novo `TERMINAL-UX-01`; terminal real depende de PTY/backend comprovado. |
| 4 | Novo `INFO-GRAPH-VIEW-01`, mantendo JSON e adicionando grafo alternavel. |
| 5 | Novo `CLOCK-MULTI-INSTANCE-01`. |
| 6 | Novo `EDITORIAL-RESULT-VIEW-01`, incluindo traducao e JSON/View. |
| 7 | Novo estudo `CE-UI-MATERIAL-STUDY-01`; PyQtMaterial nao foi adotado por suposicao. |
| 8 | Novo `UI-PLAYWRIGHT-ASSESSMENT-01`. |
| 9 | Novo `APP-TOOLS-INSERT-CATEGORY-01`. |
| 10 | Novo `CE-VOICE-PROGRAMMING-01`, com STT, RAG, LLM e confirmacao. |
| 11 | Novo `BOOLEAN-TRUTH-TABLE-VIEW-01`, preservando JSON alternavel. |
| 12 | Novo `LYNX-VIABILITY-01`; a mensagem sera reproduzida antes de decidir. |
| 13 | Novo `APP-TOOL-TAB-CLOSE-01`, com precedencia segura no Editor. |
| 14 | Novo `CALCULATOR-MEMORY-REVIEW-01`, dependente de definicao conjunta. |
| 15 | `LEG-34` ampliada para revisao conjunta e workflow sintetico. |
| 16 | Novo `CRASH-20261021-OPTIONS-SIGNAL-01`. |
| 17 | Novo `PLUGIN-DISCORD-NOTIFICATIONS-01`. |
| 18 | `APP-THREAD-01` ampliada; nao se cria uma thread permanente por botao. |
| 19 | Novo `APP-BRANDING-SPLASH-01`. |
| 20 | Mesmo `APP-BRANDING-SPLASH-01`, sem duplicar iconografia e splash. |
| 21 | Novo `APP-TOOLS-SHORTCUTS-01`. |
| 22 | `CE-MENU-SHORTCUTS-01` ampliada. |
| 23 | Novo `SET-OPERATIONS-VALIDATION-01`. |
| 24 | Novo `APP-RAG-CHATBOT-01`, reconciliado com os chats existentes. |
| 25 | Novo `APP-FEEDBACK-01`, condicionado a endpoint e privacidade. |
| 26 | Novo `APP-RESULT-PRESENTATION-AUDIT-01`; modificar outras tools exige aviso previo. |
| 27 | `CE-TEMP-NOTE-LIFECYCLE-01` ampliada para lista rolavel. |
| 28 | Novo `CE-PARAGRAPH-NAV-01`. |
| 29 | Incorporado em `CE-FIND-STATE-HISTORY-01`. |
| 30 | Atendido por esta especificacao detalhada e pelo roadmap. |
| 31 | `CE-FIND-ENTER-01` confirmado como Enter/Shift+Enter, uma acao por tecla. |
| 32 | Novo `CE-REDO-SHORTCUT-01`. |
| 33 | Incorporado em `CE-FIND-STATE-HISTORY-01`, com ancora no cursor e `n de m`. |
| 34 | Novo `CE-SYMBOL-BREADCRUMB-01`. |
| 35 | Novo `FE-COMPACT-ISOLATION-01`. |
| 36 | Novo `APP-JOB-CENTER-01` e ampliacao de `APP-THREAD-01`. |
| 37 | Novo `CE-FOLDER-SESSION-SWITCH-REGRESSION-01`; a entrega anterior sera provada. |
| 38 | `CE-MENU-SHORTCUTS-01` ampliada com Ctrl+H e conflito do Ctrl+R. |
| 39 | Incorporado em `CE-FIND-SCOPE-NEGATION-01`; semantica de inversao precisa ser definida. |
| 40 | `CE-FIND-MODELESS-01` ampliada para painel inferior ou janela modeless. |
| 41 | Incorporado em `CE-FIND-SCOPE-NEGATION-01` como Only Comments. |
| 42 | Incorporado em `CE-FIND-SCOPE-NEGATION-01` como regressao Regex. |
| 43 | Novo `CE-TAB-COPY-PATH-01`. |
| 44 | Incorporado em `APP-JOB-CENTER-01`. |
| 45 | Novo `CE-SMART-HOME-VISUAL-LINE-01`, distinto do Home logico ja entregue. |

## Definicoes Que Exigem Participacao Do Usuario

### Calculator Memory Slots

O comportamento atual e uma memoria persistente de cinco conjuntos JSON para
reusar resultados, comparar estatisticas e executar operacoes. Antes da
reformulacao, devem ser respondidas estas perguntas:

1. Os slots recebem somente Set Operations ou resultados de qualquer tool?
2. A memoria deve continuar em A-E, usar nomes livres ou ser uma lista limitada?
3. O conteudo deve sobreviver ao reinicio? Qual quota e politica de limpeza?
4. A tool deve calcular dados ou apenas guardar/encaminhar resultados?
5. Ela deve continuar separada ou integrar-se visualmente a Set Operations?

### Formula Builder

O codigo atual modela um pipeline de operacoes de conjunto com steps, entradas de
arquivo/resultado/slot e templates. Para corrigir o modelo, ainda e necessario
definir:

1. Formula significa expressao matematica visual ou pipeline de arquivos?
2. Quais fontes de entrada e operadores sao indispensaveis?
3. Resultados intermediarios devem ficar visiveis e editaveis?
4. Qual workflow concreto falha hoje e qual seria o resultado esperado?
5. O usuario prefere canvas por nos/arestas, expressao textual ou ambos?

## Fronteiras Tecnicas

- Widgets Qt e modelos permanecem na GUI thread; apenas IO e processamento
  thread-safe vao para workers. Background nao significa criar thread por clique.
- JSON continua disponivel quando funciona como contrato formal. Views graficas
  sao projecoes, nao substituicoes destrutivas do resultado.
- PyQtMaterial, NiceGUI, Flet, Cytoscape e Playwright exigem avaliacao de
  compatibilidade, licenca, memoria, empacotamento e manutencao antes de entrar no
  runtime principal.
- Nenhum webhook, provider, feedback ou documento do usuario sera enviado sem
  acao e consentimento explicitos.
