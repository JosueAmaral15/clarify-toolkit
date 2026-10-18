# Reconciliacao De Requisitos - 18/10/2026

## Escopo

Esta revisao fez duas verificacoes diferentes:

1. Mapeamento integral da lista fornecida pelo usuario contra `docs/TASKS.md`,
   codigo e testes atuais.
2. Varredura estrutural de toda a pasta `docs/` para localizar marcadores
   Markdown ainda abertos.

A segunda verificacao nao e uma auditoria semantica conclusiva de cada frase dos
859 arquivos Markdown. Ela encontrou 295 arquivos com pelo menos um marcador
`- [ ]`; a maioria esta em planos, relatorios, sessoes e estudos historicos. O
roadmap canonico continua sendo `docs/TASKS.md`, e a nova tarefa
`DOCS-HISTORICAL-CHECKBOX-AUDIT-01` exige classificar cada marcador antes de
promove-lo.

## Resultado Canonico

- Ponto de partida: 41 tarefas abertas.
- Tarefas existentes ampliadas: `APP-THREAD-01`, `CE-FIND-ENTER-01`,
  `CE-TEMP-NOTE-LIFECYCLE-01` e `LEG-23`.
- Novas tarefas: 14.
- Total depois da reconciliacao: 55 tarefas abertas.
- Nenhuma tarefa historica foi reaberta somente porque apareceu em outro arquivo.

## Requisitos Atuais

| Requisito | Decisao |
| --- | --- |
| Save/Ctrl+S mantem nota temporaria; Save As converte em arquivo | Ampliado em `CE-TEMP-NOTE-LIFECYCLE-01`. A exclusao da nota ocorre somente depois da escrita atomica bem-sucedida. |
| Atalhos para File, Edit e View | Novo `CE-MENU-SHORTCUTS-01`. O codigo atual possui comandos sem shortcut e o registro global nao cobre todas as acoes locais. |
| Preservar indentacao ao colar entre arquivos | Novo `CE-PASTE-INDENT-01`. O paste atual delega diretamente ao Qt, mas nao existe regressao que prove tabs, espacos mistos, multiline e undo. |
| Tab em texto selecionado ignora a preferencia Spaces | Novo `CE-INDENT-SELECTION-REGRESSION-01`. O core usa `_indent_unit()`, mas o teste existente atribui a propriedade diretamente e nao prova QAction, QSettings, reabertura ou troca de guia. |
| Enter duplica Find Next | Ampliado em `CE-FIND-ENTER-01`. O painel atual combina botao default e `returnPressed`, duas rotas para a mesma tecla. |
| Find por similaridade com IA | Novo `CE-FIND-AI-SIMILARITY-01`, opt-in, limitado e distinto de busca exata/regex. |
| Processamentos nao podem bloquear a GUI | Ampliado em `APP-THREAD-01` com inventario e prova de afinidade. Operacoes caras recebem worker; criar uma thread permanente para cada botao sem trabalho caro foi rejeitado por seguranca Qt e consumo de memoria. |
| Observar nomes de classes e imports | Novo `CE-CLASS-IMPORT-OBSERVER-01`, reutilizando atualizador de referencias e AST, inicialmente para Python. A verificacao ocorre somente ao sair da linha alterada, salvar ou sair do Editor; nao durante a digitacao incompleta. |

## Lista Historica Fornecida

### Entregue E Mantido Fechado

- **Extrator:** os quatro estados `key/value`, incluindo FAQ fixture e modos
  `Key + value`, `Key only`, `Value only` e `Neither`, estao registrados como
  entregues.
- **File Explorer:** refresh da tabela, refinamento do universo anterior,
  limpeza de resultados vazios, remocao da redundancia Regex, progresso limitado,
  copy all, delete seguro, replace por arquivo, JSON de resultados e explicacao
  assistida estao registrados como entregues.
- **Google Translate:** multiplas tags, Open and Switch to Editor, recentes,
  historico, JSON, IPYNB, PDF e traducao inversa estao registrados como entregues.
- **Digital Text Content Repairer:** deteccao de idioma, ortografia/gramatica,
  categorias de defeitos e pre-validacao ABNT possuem fundacao entregue.
- **Information Structure:** mapa de pasta, grafo de banco, arvore AST de codigo,
  organizacao hierarquica, grafo de funcoes/complexidade, referencias cientificas
  e transformacoes visuais possuem fatias entregues e limitadas.
- **Tools gerais:** categorias, feedback sonoro, abas internas, terminal, Find no
  Format Converter, tabela verdade/Quine-McCluskey, Lynx, Ollama/LLaVA, operacoes
  multiformato, identidade Clarify Toolkit, voz para programacao, analise de
  algoritmos, Open in Editor/Switch, Explorer lateral e Clock estao registrados.
- **Clarify Editor:** line numbers, recovery de 24 horas configuravel, Explorer,
  Tab/Shift+Tab, tabs/espacos, abas arrastaveis, splits, abertura por caminho,
  selecao inicial no Find, recentes, sessao de pasta, menus de contexto e atalhos
  principais ja possuem entregas documentadas.
- **CLI:** `src/cli/parser.py` ja oferece search, replace, insert, translate,
  gtranslate e dedupe, integrado ao entrypoint `python -m src`; portanto nao foi
  criada uma segunda tarefa de CLI.
- **LLM basico:** AI Processor ja apresenta providers/modelos explicitos. O novo
  cadastro diferencia um agente configurado de um provider simples.

### Parcial Ou Pendente

- **Chrome/acoplamento:** os controles internos enganosos foram removidos, mas o
  toggle real permanece em `TOOL-DOCK-TOGGLE-01`.
- **Editor inspirado em nano/Xed/Notepad/Notepad++:** existe uma base ampla, mas
  os contratos recentes continuam nas tarefas de toolbar, status, atalhos,
  Find modeless e F1.
- **Revisao editorial mais profunda:** a fundacao nao equivale a revisao para
  publicacao completa; criado `TEXT-EDITORIAL-DEEP-01`.
- **Alt+Up/Down multiline:** o comando existe, mas o teste atual cobre somente
  uma linha; criado `CE-MOVE-LINES-SELECTION-01` para o defeito relatado.
- **Tab com selecao e Spaces:** existe cobertura ao atribuir o estado interno,
  mas o comportamento relatado pelo usuario mostra que o caminho real de
  preferencia/persistencia nao esta garantido; criado
  `CE-INDENT-SELECTION-REGRESSION-01`.
- **Tema escuro dos resultados:** o `ResultsTree` depende parcialmente da paleta
  e nao possui matriz dedicada de contraste/troca runtime; criado
  `FE-DARK-RESULTS-01`.
- **Copia inteligente de atualizados:** nao havia contrato canonico; criado
  `FE-SMART-COPY-01`.
- **Chat do AI File Processor:** o Tutorial Assistant e conversacional, mas o AI
  Processor nao oferece sessao de chat sobre os arquivos; criado
  `AI-FILE-CHAT-01`.
- **Cadastro de agente:** providers existentes nao representam perfil/permissoes
  de agente; criado `AI-AGENT-REGISTRY-01`.
- **Linux Mint:** `LEG-23` foi ampliada para instalacao, atualizacao, launcher,
  desinstalacao e rollback reais no Mint.
- **Open source:** README e wiki declaram MIT, mas nao existe `LICENSE` na raiz;
  criado `DIST-OPEN-SOURCE-01` para resolver licenca, terceiros e seguranca antes
  de qualquer publicacao.
- **Divulgacao:** criado `DIST-OUTREACH-01`; postagem, campanha, preco ou outra
  publicacao externa continua dependente de confirmacao imediata.

### Nao Promovido Como Tarefa Executavel

O pedido de listas de pessoas por cores, criminalidade e suposta ausencia de
punicao nao foi convertido em requisito. Ele mistura dado pessoal sensivel,
acusacao potencialmente difamatoria e rotulos sem dominio, fonte, base legal,
controle de acesso ou criterio de contestacao. Uma futura proposta precisa ser
reformulada como classificacao generica e legalmente revisada, sem inferir crime
ou culpa; ate la, nao pertence ao backlog de implementacao.

## Marcadores Historicos Em `docs/`

Distribuicao dos 295 arquivos que ainda contem checkboxes abertos:

| Area | Arquivos |
| --- | ---: |
| `programmers/` | 50 |
| `action-plans/` | 47 |
| `sprints/` | 38 |
| `reports/` | 30 |
| `sessions/` | 23 |
| `study/` | 22 |
| `specifications/` | 12 |
| `investigations/` | 12 |
| `analysis/` | 11 |
| `refactoring/` | 10 |
| Outras areas combinadas | 40 |

Conclusao: nao esta correto afirmar que todas as tarefas descritas em `docs/`
foram feitas. Tambem nao e correto somar esses marcadores a fila de 54 itens sem
triagem, pois muitos sao copias de planos antigos, checklists de sessao ou
criterios historicos. `DOCS-HISTORICAL-CHECKBOX-AUDIT-01` registra a reconciliacao
restante de forma controlada.
