# Manual do Usuário — Clarify Toolkit

## Índice
1. Introdução
2. Instalação
3. Primeiros Passos
4. Funcionalidades Principais
   - Tradução de JSON
   - Reescrita de JSON
   - Substituição de Placeholders
   - File Explorer e Busca de Conteúdo
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
O Clarify Toolkit é uma aplicação desktop para manipulação, tradução e gerenciamento de textos, documentos e arquivos JSON, com interface baseada em ferramentas modulares. O editor interno mantém o nome específico **Clarify Editor**.

## 2. Instalação
- **Requisitos:** Python 3.12+, PySide6. A tradução de PDF requer as ferramentas `pdfinfo` e `pdftotext` do pacote Poppler (`poppler-utils` no Debian/Ubuntu/Linux Mint).
- Execute localmente a partir do código-fonte:
  ```bash
  git clone <repo>
  cd clarify
  poetry install
  python -m src
  ```
- Sem Poetry, use `python -m pip install -e .` em um ambiente virtual.

## 3. Primeiros Passos
- Abra o Clarify e carregue um arquivo JSON.
- Utilize os docks para traduzir, reescrever ou substituir placeholders.
- Salve e gerencie arquivos recentes pelo menu principal.

## 4. Funcionalidades Principais
### Tradução de JSON
- Traduza textos em arquivos JSON para múltiplos idiomas.
- Suporte a tradução automática e manual.
- Em **JSON Translate**, o primeiro par de delimitadores define o escopo principal. Use **+ Escopo** para acrescentar outros pares de regex na mesma execução e **−** para remover pares adicionais.
- Cada linha preenchida deve possuir delimitadores inicial e final. Se todas as linhas estiverem vazias, a tradução considera o arquivo inteiro.
- Escopos sobrepostos são combinados antes da tradução, evitando que o mesmo trecho seja processado duas vezes. Pares de tags específicos, como `<div>`/`</div>` e `<script>`/`</script>`, preservam outras tags fora da seleção.
- Use **Recentes** para recuperar os últimos arquivos ou diretórios-fonte e dicionários selecionados. O Google Translate compartilha a lista de fontes, mas mostra somente arquivos compatíveis com seu modo de arquivo.
- As listas guardam apenas caminhos locais existentes, nunca o texto ou o resultado da tradução, e mantêm no máximo 10 itens por categoria. A ação **Limpar Recentes** remove somente a categoria exibida.
- Traduções concluídas registram metadados resumidos no histórico de operações, sem armazenar o conteúdo traduzido.
- Em **Google Translate**, arquivos `.ipynb` traduzem somente células Markdown preenchidas. Código, outputs, metadados e demais células são preservados; salve o resultado como `.ipynb` para manter a estrutura.
- PDFs são abertos somente para leitura e têm o texto extraído com limites de tamanho e páginas. Layout e imagens não são preservados, e PDFs digitalizados sem camada de texto exigem OCR externo.
- Use **Abrir no Clarify Editor** para revisar a tradução como texto editável antes de salvar. Esse fluxo não sobrescreve o arquivo de origem.

### Reescrita de JSON
- Reescreva chaves/valores conforme regras personalizadas.

### Operações de conjunto em documentos
- **Set Operations** aceita JSON, TXT, DOCX, ODT, IPYNB e PDF. JSON mantém sua estrutura nativa; os demais formatos viram um conjunto canônico e independente de ordem de unidades textuais não vazias.
- Espaços consecutivos são normalizados, duplicatas são removidas por SHA-256 e cada unidade é limitada a 4.096 caracteres, com no máximo 50.000 unidades e 50 MiB por arquivo. PDF reutiliza a extração limitada do Poppler; IPYNB inclui texto de células Markdown e código.
- Essa representação permite interseção, união, diferença e diferença simétrica entre formatos documentais. Os arquivos de origem são somente leitura.

### Substituição de Placeholders
- Substitua variáveis e marcadores em textos JSON.

### Extração JSX/HTML
- Os controles **Include key** e **Include value** funcionam de forma independente tanto no modo de extração do **Format Converter** quanto no **Advanced Extractor**.
- Com ambos ativados, a saída JSON preserva a hierarquia, as chaves extraídas e seus valores.
- Apenas **Include key** gera JSON válido com a hierarquia e os nomes das chaves, sem copiar os valores de origem. Ramos mistos usam listas para representar, no mesmo nível, chaves simples e objetos aninhados.
- Apenas **Include value** gera uma lista plana dos valores extraídos, sem nomes de chave. Com ambos desativados, a saída é `{}`.
- No modo de entrada **Text**, `Ctrl+F` abre busca e substituição. `Enter` no campo de busca avança para a próxima ocorrência; **Replace** altera a ocorrência atual e **Replace All** respeita as opções Regex, Case sensitive e Whole word.

### File Explorer e Busca de Conteúdo
- Abra o **File Explorer**, escolha um diretório e informe um nome de arquivo ou uma consulta de conteúdo. Sem critérios de busca, o comando principal apenas lista os arquivos.
- Em **Tipo de conteúdo**, selecione:
  - **Texto/ASCII (padrão):** pesquisa somente arquivos classificados como texto decodificável.
  - **Binários:** pesquisa a consulta codificada em UTF-8 nos bytes dos arquivos classificados como binários.
  - **Ambos:** pesquisa arquivos de texto e binários. Esse modo pode realizar mais leitura de disco.
- A classificação lê somente uma amostra inicial de 8 KiB. Bytes nulos, UTF-8 inválido ou uma proporção alta de caracteres de controle classificam o arquivo como binário.
- Arquivos binários são examinados em blocos de 64 KiB, sem carregar o arquivo inteiro na memória. Os resultados mostram apenas uma prévia curta em hexadecimal/ASCII, limitada a 200 caracteres; o conteúdo binário bruto completo não é exibido.
- A busca limita os resultados a 10.000 correspondências por arquivo e 50.000 no total. Refine o nome, o conteúdo ou os filtros quando o limite for alcançado.
- **Segurança:** substituição de conteúdo continua exclusiva para arquivos de texto. Resultados binários nunca são modificados pelas ações de substituição.

### Gerenciamento de Arquivos Recentes
- Acesse rapidamente arquivos abertos recentemente.
- As ferramentas de tradução mantêm listas separadas de fontes e dicionários; caminhos removidos do disco são descartados automaticamente.
- No Clarify Editor, **File > Recover Unsaved...** restaura buffers recentes como novas abas não salvas. A retenção padrão é de 24 horas e pode ser ajustada em **File > Recovery Retention...**.
- A recuperação é limitada a 2 MiB por documento, 20 documentos e 20 MiB no total. Salvar ou descartar explicitamente uma aba remove o snapshot correspondente.

### Preferências e Configurações Persistentes
- Tema, idioma, atalhos e preferências salvos automaticamente.
- O menu principal **Tools** organiza as ferramentas em Editing, JSON, Text and Translation, Artificial Intelligence, Files e Utilities. A organização altera apenas a navegação; atalhos e comportamento das ferramentas permanecem os mesmos.
- **Play a sound after processing** é uma preferência global desativada por padrão. Quando ativada, emite um único alerta do sistema após conclusões bem-sucedidas nas ferramentas compatíveis; falhas e cancelamentos permanecem silenciosos.
- O **AI Processor** oferece **Ollama (Local)** sem chave de API nem teste de internet. Use Refresh para listar somente modelos instalados; imagens PNG/JPEG/WebP/GIF/BMP são encaminhadas a modelos multimodais compatíveis, com limite de 10 MiB por imagem. As respostas locais são limitadas a 8 MiB, contexto 4.096 e saída 1.024 tokens.

### Atalhos de Teclado
- **ENTER:** Pressione ENTER em qualquer campo de entrada para executar a ação principal do dock (tradução, busca, extração, etc.)
- **Ctrl+F:** Abra a caixa de busca em qualquer painel de resultados para localizar texto específico
- Consulte a lista completa de atalhos em Ajuda > Atalhos
- Personalize atalhos nas configurações
- No Clarify Editor: `Ctrl+S` salva, `Ctrl+F` busca, `Ctrl+R` abre busca e substituição, `Ctrl+G` vai para uma linha, `Ctrl+L` seleciona a linha atual e `Ctrl+I`/`Ctrl+]` indentam.

### Barra de Status
- Exibe dicas, progresso e status de operações.

### Clarify Editor
- Use **File > Open Folder...** para definir a raiz do explorador lateral. A árvore carrega o sistema de arquivos sob demanda e abre arquivos com clique duplo.
- Use **View > Show Explorer** para mostrar ou ocultar a lateral; a pasta e a visibilidade são persistidas.
- O explorador lateral é apenas para navegação. Pesquisas de conteúdo, filtros e substituições continuam centralizados no **File Explorer**.

### Information Structure
- Use **Tools > Files > Information Structure** para análises estruturais limitadas e somente leitura: mapa dos resultados do File Explorer sem nova varredura, esquema SQLite aberto em modo read-only, contexto AST Python, agrupamento de parágrafos, ancestralidade por DOI e visualizações hierárquicas.
- A saída é JSON e pode ser aberta como uma nova aba não salva do Clarify Editor.

### Editorial Repair
- Use **Tools > Text and Translation > Editorial Repair** para sessões independentes de revisão. **New Tab** cria outra sessão.
- Os modos locais cobrem candidatos ortográficos do Aspell, categorias separadas de defeitos textuais e pré-validação estrutural ABNT. Aspell requer dicionário instalado para o idioma escolhido.
- As ações de AI Processor e Google Translate apenas preparam ou transferem a entrada revisada; não iniciam processamento nem sobrescrevem o original.

### Boolean Logic
- Use **Tools > Utilities > Boolean Logic** para gerar tabela verdade, mintermos e maxtermos de uma expressão restrita, ou fornecer a tabela completa em JSON e obter SOP/POS minimizadas.
- O limite é de 10 variáveis e chamadas de função não são aceitas.

### Voice Programming
- Use **Tools > Artificial Intelligence > Voice Programming** para visualizar comandos derivados de transcrições. Pontuação de programação é reconhecida em português e inglês.
- O comando só chega ao Clarify Editor após confirmação da prévia exata. A transcrição ao vivo exige um backend STT instalado e configurado separadamente.

### Algorithm Analysis
- Use **Tools > Artificial Intelligence > Algorithm Analysis** para executar preflight local e preparar revisão no AI Processor. Python inclui contexto AST limitado; imagens de fluxograma exigem provider multimodal configurado.
- A ferramenta nunca inicia uma requisição de IA automaticamente.

### Recursos de Produtividade (v1.9.0+)
- **Execução Rápida:** Pressione ENTER em campos de entrada para executar ações sem usar o mouse
- **Busca em Resultados:** Use Ctrl+F para encontrar texto nos painéis de resultado
- **Parser Aprimorado:** GenericScopeParser reescrito com suporte a múltiplos padrões de atributos e expressões balanceadas
- Em **Tools > Utilities > Clock**, use as abas Clock, Stopwatch e Timer. O cronômetro e o temporizador possuem controles explícitos de início, pausa e reset; o temporizador usa a preferência global de som ao chegar a zero.
- **Tools > Utilities > Terminal** executa um programa por vez no diretório exibido. Os argumentos aceitam aspas, mas não há shell implícito: pipes, redirecionamento, expansão e comandos internos só funcionam quando o próprio usuário chama explicitamente um shell. A saída retida é limitada a 1 MiB e **Stop** interrompe o processo atual.
- **Tools > Utilities > Lynx Text Browser** renderiza URLs HTTP/HTTPS como texto por meio do executável local `lynx`. A navegação é somente leitura, possui timeout de 30 segundos e retém no máximo 2 MiB; quando Lynx não está instalado, os controles ficam desabilitados com uma mensagem explícita.

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
- Consulte logs em `~/.clarify/logs/clarify.log`.
- Para problemas de interface, reinicie o aplicativo.
- Dúvidas frequentes: [FAQ](#)

## 9. Créditos e Licença
- Desenvolvido por Josue Amaral e colaboradores.
- Licença MIT.
