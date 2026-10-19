# Clarify Editor - Indentacao De Selecao

Data: 19/10/2026
Tarefa: `CE-INDENT-SELECTION-REGRESSION-01`
Branch: `COM-953b3953-5ce6-49d9-8058-ae5c11110b1c`
Checkpoint de origem: `44340c3`

## Defeito Comprovado

O caminho principal ja calculava a unidade por `_indent_unit()`, mas a view
dividida nao instalava o filtro do `EditorDock` e nao era reconhecida como uma
view da guia. Antes da correcao, pressionar `Tab` sobre uma selecao no split
substituia a selecao por um tab literal. Uma acao de menu tambem operava no
cursor da view principal, mesmo quando o usuario estava no split.

## Correcao

- o split participa do filtro de eventos e e associado a sua guia de origem;
- foco recente determina a view usada pelas acoes Indent/Outdent;
- `Tab` e `Shift+Tab` recebem explicitamente o editor observado;
- a largura visual de tabs e sincronizada com a preferencia persistida;
- fechar o split devolve a view ativa para o editor principal;
- outdent usa a largura configurada, sem constante fixa de quatro espacos.

Arquivos e tabs literais preexistentes nao sao convertidos. A operacao continua
sendo um unico bloco de undo.

## Evidencia

Os modulos foram executados serialmente, cada um em processo Qt offscreen
isolado, com HOME temporario, timeout pytest de 20 s, limite de 180 s, RAM do
sistema em 85% e RSS da arvore em 600 MiB:

| Modulo | Resultado | Pico RSS |
| --- | ---: | ---: |
| `test_editor_priority_stage1.py` | 6 passed | 207.8 MiB |
| `test_editor_priority_stage4_tabs.py` | 8 passed | 206.0 MiB |
| `test_editor_recent_interactions.py` | 7 passed | 205.4 MiB |
| `test_editor_priority_stage5_sessions.py` | 6 passed | 204.7 MiB |
| `test_editor_dock.py` | 69 passed | 226.7 MiB |

Total: **96 testes aprovados**. Nao houve crash nativo, SIGSEGV, timeout ou
acionamento dos guardioes de RAM/RSS/tempo.

Tambem passaram `py_compile`, Pylint em modo errors-only e `git diff --check`.
O arquivo legado completo nao foi reformatado: uma tentativa de Black revelou
ruido amplo e foi retirada antes da validacao final.

## Limite Da Entrega

Esta etapa nao altera paste entre documentos, Find, atalhos restantes, observers
de classes/imports nem itens do File Explorer. Eles permanecem tarefas separadas
no roadmap canonico.
