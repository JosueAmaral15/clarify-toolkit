import { Translations } from '../types';
export const pt: Translations = {
  mainKeys: {
    location: 'pt-BR'
  },
  common: {
    buttons: {
      next: 'Próximo',
      previous: 'Anterior',
      submit: 'Enviar',
      start: 'Iniciar',
      continue: 'Continuar',
      cancel: 'Cancelar',
      retry: 'Tentar Novamente',
      viewResults: 'Ver Resultados',
      close: 'Fechar',
      saveExit: 'Salvar/Sair'
    },
    labels: {
      score: 'Pontuação',
      time: 'Tempo',
      timeRemaining: 'Tempo Restante',
      question: 'Questão',
      answer: 'Resposta',
      yourAnswer: 'Sua Resposta',
      correctAnswer: 'Resposta Correta',
      feedback: 'Feedback',
      instructions: 'Instruções',
      preparationTime: 'Tempo de Preparação',
      recordingTime: 'Tempo de Gravação'
    },
    messages: {
      loading: 'Carregando...',
      error: 'Ocorreu um erro',
      success: 'Sucesso!',
      submitting: 'Enviando sua resposta...',
      submitted: 'Resposta enviada com sucesso',
      recordingStarted: 'Gravação iniciada',
      recordingStopped: 'Gravação parada',
      preparationComplete: 'Tempo de preparação completo'
    }
  },
  exercises: {
    readAloud: {
      title: 'Leitura em Voz Alta',
      description: 'Leia o texto em voz alta de forma clara e natural',
      instructions: 'Olhe para o texto abaixo. Em 40 segundos, você deve ler este texto em voz alta da forma mais natural e clara possível. Você tem 40 segundos para ler em voz alta.',
      tips: [
        'Fale claramente e em um ritmo rápido',
        'Preste atenção à pontuação',
        'Pronuncie as palavras corretamente',
        'Mantenha uma boa entonação'
      ]
    },
    repeatSentence: {
      title: 'Repetir Frase',
      description: 'Ouça e repita a frase que você ouvir',
      instructions: 'Você ouvirá uma frase. Por favor, repita a frase exatamente como a ouviu. Você ouvirá a frase apenas uma vez.',
      tips: [
        'Concentre-se na pronúncia do orador',
        'Lembre-se das palavras exatas usadas',
        'Mantenha o mesmo padrão de entonação',
        'Fale claramente ao repetir'
      ]
    },
    describeImage: {
      title: 'Descrever Imagem',
      description: 'Descreva a imagem em detalhes',
      instructions: 'Observe a imagem abaixo. Em 25 segundos, por favor, fale no microfone e descreva em detalhes o que a imagem está mostrando. Você terá 40 segundos para dar sua resposta.',
      tips: [
        'Comece com uma visão geral',
        'Descreva os elementos-chave sistematicamente',
        'Use vocabulário apropriado',
        'Fale durante toda a duração'
      ]
    },
    retellLecture: {
      title: 'Recontar Palestra',
      description: 'Ouça uma palestra e reconte-a com suas próprias palavras',
      instructions: 'Você ouvirá uma palestra. Após ouvir a palestra, em 10 segundos, por favor, fale no microfone e reconte o que você acabou de ouvir da palestra com suas próprias palavras. Você terá 40 segundos para dar sua resposta.',
      tips: [
        'Faça anotações enquanto ouve',
        'Concentre-se nos pontos principais',
        'Estruture sua resposta logicamente',
        'Inclua detalhes e exemplos-chave'
      ]
    },
    answerShortQuestion: {
      title: 'Responder Pergunta Curta',
      description: 'Responda a uma pergunta com uma palavra ou frase curta',
      instructions: 'Você ouvirá uma pergunta. Por favor, dê uma resposta simples e curta. Frequentemente, apenas uma ou poucas palavras são suficientes.',
      tips: [
        'Ouça atentamente a pergunta',
        'Responda concisamente',
        'Seja direto e claro',
        'Não pense demais na resposta'
      ]
    },
    summarizeWrittenText: {
      title: 'Resumir Texto Escrito',
      description: 'Escreva um resumo do trecho em uma única frase',
      instructions: 'Leia o trecho abaixo e resuma-o em uma frase. Sua resposta deve ter entre 5 e 75 palavras.',
      tips: [
        'Identifique a ideia principal',
        'Inclua os pontos de apoio chave',
        'Use estruturas de frases complexas',
        'Mantenha-se dentro dos limites de palavras'
      ]
    },
    essay: {
      title: 'Redação',
      description: 'Escreva uma redação sobre o tema dado',
      instructions: 'Você terá 20 minutos para planejar, escrever e revisar uma redação sobre o tópico abaixo. Sua resposta será avaliada pela forma como você desenvolve uma posição, organiza suas ideias, apresenta detalhes de apoio e controla os elementos do inglês escrito padrão. Você deve escrever 200-300 palavras.',
      tips: [
        'Planeje a estrutura da sua redação',
        'Inclua introdução, corpo e conclusão',
        'Apoie argumentos com exemplos',
        'Revise a gramática e a ortografia'
      ]
    },
    multipleChoiceSingle: {
      title: 'Múltipla Escolha (Resposta Única)',
      description: 'Escolha a única resposta correta',
      instructions: 'Leia o texto e escolha a única resposta correta para a pergunta.',
      tips: [
        'Leia a pergunta cuidadosamente',
        'Elimine opções incorretas',
        'Procure por palavras-chave no texto',
        'Escolha a resposta mais apropriada'
      ]
    },
    multipleChoiceMultiple: {
      title: 'Múltipla Escolha (Múltiplas Respostas)',
      description: 'Escolha todas as respostas corretas',
      instructions: 'Leia o texto e escolha todas as respostas corretas para a pergunta. Mais de uma resposta está correta.',
      tips: [
        'Leia todas as opções cuidadosamente',
        'Várias respostas podem estar corretas',
        'Verifique cada opção em relação ao texto',
        'Não presuma que apenas uma está correta'
      ]
    },
    reorderParagraphs: {
      title: 'Reordenar Parágrafos',
      description: 'Organize as caixas de texto na ordem correta',
      instructions: 'As caixas de texto abaixo foram colocadas em ordem aleatória. Restaure a ordem original arrastando as caixas de texto do painel esquerdo para o painel direito.',
      tips: [
        'Procure por conexões lógicas',
        'Identifique introdução e conclusão',
        'Verifique referências de pronomes',
        'Siga a ordem cronológica, se presente'
      ]
    },
    fillInTheBlanks: {
      title: 'Preencher as Lacunas',
      description: 'Selecione palavras para completar o texto',
      instructions: 'Abaixo está um texto com lacunas. Clique em cada lacuna e selecione a resposta apropriada na lista suspensa.',
      tips: [
        'Considere os requisitos gramaticais',
        'Verifique as colocações de palavras',
        'Leia a frase inteira',
        'Verifique se suas escolhas fazem sentido'
      ]
    },
    highlightCorrectSummary: {
      title: 'Destacar Resumo Correto',
      description: 'Escolha o melhor resumo do texto',
      instructions: 'Leia o texto e escolha o parágrafo que melhor resume o trecho.',
      tips: [
        'Identifique as ideias principais',
        'Verifique a precisão dos fatos',
        'Evite opções apenas com detalhes menores',
        'Escolha o resumo mais abrangente'
      ]
    },
    summarizeSpokenText: {
      title: 'Resumir Texto Falado',
      description: 'Escreva um resumo da palestra',
      instructions: 'Você ouvirá uma breve palestra. Escreva um resumo para um colega de estudante que não estava presente. Você deve escrever 50-70 palavras.',
      tips: [
        'Escreva em terceira pessoa'
      ]
    },
    listeningMultipleChoice: {
      title: 'Múltipla Escolha (Compreensão Auditiva)',
      description: 'Responda às perguntas com base no áudio',
      instructions: 'Ouça a gravação e responda à pergunta de múltipla escolha selecionando a resposta correta.',
      tips: [
        'Leia as perguntas antes de ouvir',
        'Faça anotações das informações-chave',
        'Ouça detalhes específicos',
        'Escolha com base no que você ouviu'
      ]
    },
    listeningFillBlanks: {
      title: 'Preencher Lacunas (Compreensão Auditiva)',
      description: 'Digite as palavras que faltam na gravação',
      instructions: 'Você ouvirá uma gravação. Digite as palavras que faltam em cada lacuna.',
      tips: [
        'Concentre-se no contexto',
        'Ouça as terminações das palavras',
        'Verifique a ortografia cuidadosamente',
        'Use pistas de contexto'
      ]
    },
    highlightIncorrectWords: {
      title: 'Destacar Palavras Incorretas',
      description: 'Selecione as palavras que diferem da gravação',
      instructions: 'Você ouvirá uma gravação. Abaixo está uma transcrição da gravação. Algumas palavras na transcrição diferem do que o orador disse. Clique nas palavras que são diferentes.',
      tips: [
        'Acompanhe o texto',
        'Ouça as palavras exatas',
        'Marque as diferenças imediatamente',
        'Concentre-se nas variações de pronúncia'
      ]
    },
    selectMissingWord: {
      title: 'Selecionar Palavra Ausente',
      description: 'Escolha a palavra que falta na gravação',
      instructions: 'Você ouvirá uma gravação sobre um tópico. No final da gravação, a última palavra ou grupo de palavras foi substituído por um "beep". Selecione a opção correta para completar a gravação.',
      tips: [
        'Entenda o contexto geral',
        'Ouça a conclusão lógica',
        'Considere gramática e significado',
        'Preveja antes de ver as opções'
      ]
    },
    writeFromDictation: {
      title: 'Escrever por Ditado',
      description: 'Digite a frase que você ouvir',
      instructions: 'Você ouvirá uma frase. Digite a frase exatamente como a ouviu. Escreva o máximo da frase que puder. Você ouvirá a frase apenas uma vez.',
      tips: [
        'Concentre-se em cada palavra',
        'Lembre-se das regras de pontuação',
        'Verifique ortografia e gramática',
        'Escreva o que você se lembra',
      ]
    }
  },
  pages: {
    aiTutorPage: {
      title: 'Tutor de Fala com IA',
      connected: 'Conectado',
      connectToStartChatting: 'Conecte-se para começar a conversar...',
      initializing: 'Inicializando...',
      connectToUseVoice: 'Conecte-se para usar a voz',
      typeYourMessage: 'Digite sua mensagem ou use o microfone para falar',
      muteMicrophone: 'Silenciar microfone',
      unmuteMicrophone: 'Ativar microfone',
      disconnected: 'Desconectado',
      beta: 'BETA',
      connecting: 'Conectando...',
      startSession: 'Iniciar Sessão',
      endSession: 'Encerrar Sessão',
      settings: 'Configurações',
      clearConversation: 'Limpar Conversa',
      volume: 'Volume',
      initializingAITutor: 'Inicializando Tutor de IA...',
      startConversation: 'Iniciar uma conversa',
      starters: {
        practiceImages: 'Vamos praticar a descrição de imagens',
        helpPronunciation: 'Ajude-me com a pronúncia',
        improveFluency: 'Quero melhorar minha fluência',
        practiceInterview: 'Praticar perguntas de entrevista'
      },
      aiThinking: 'A IA está pensando...',
      AuthGuard: {
        title: {
          volumeSettings: 'Configurações de volume',
          settings: "Configurações"
        }
      },
      letSPractice: 'Vamos praticar a descrição de imagens',
      ismicenabled: 'Microfone habilitado?'
    },
    authCallback: {
      authenticating: 'Autenticando...',
      pleaseWaitLogin: 'Por favor, aguarde enquanto fazemos seu login',
      pleaseWait: 'Por favor, aguarde'
    },
    auth: {
      brandTitle: 'PTEasy',
      brandSubtitle: 'Domine seu exame PTE com prática alimentada por IA'
    },
    describeImageTemplate: {
      backToBlog: '← Voltar ao Blog',
      title: 'Modelo de Descrição de Imagem para PTE',
      subtitle: 'Domine todos os tipos de imagem com nossos modelos e estratégias abrangentes',
      stats: {
        speakingTime: '40 segundos de tempo de fala',
        imageTypes: 'Mais de 6 tipos de imagem',
        readTime: '7 min de leitura'
      },
      universalTemplate: {
        title: 'Modelo Universal',
        structureTitle: 'Estrutura do Modelo',
        steps: {
          opening: 'Abertura: Identifique o tipo de imagem e o tópico principal',
          components: 'Componentes: Descreva o que a imagem contém',
          keyData: 'Dados Chave: Mencione detalhes específicos, números ou tendências',
          conclusion: 'Conclusão: Resuma a principal descoberta ou mensagem'
        }
      },
      templatesByType: 'Modelos por Tipo de Imagem',
      realExamples: 'Exemplos Reais',
      vocabulary: 'Vocabulário Essencial para Tendências',
      tips: {
        title: 'Dicas Profissionais para o Sucesso'
      },
      mistakes: {
        title: 'Erros Comuns a Evitar'
      },
      timeManagement: {
        title: 'Estratégia de Gerenciamento de Tempo',
        stage1: '0-5 segundos:',
        stage2: '5-15 segundos:',
        stage3: '15-25 segundos:',
        stage4: 'Fala (35-40 seg):'
      },
      cta: {
        title: 'Pronto para Praticar?',
        subtitle: 'Domine a Descrição de Imagens com exercícios ilimitados e feedback instantâneo da IA',
        startFree: 'Comece a Praticar Grátis',
        tryExercise: 'Experimentar Exercício Agora'
      },
      related: {
        title: 'Modelos Relacionados',
        retellLecture: {
          title: 'Modelo de Recontar Palestra',
          description: 'Abordagem estruturada para resumos de palestras'
        },
        essayWriting: {
          title: 'Modelos de Redação',
          description: 'Modelos para todos os tipos de redação'
        }
      }
    },
    essayWritingTemplates: {
      title: 'Modelos de Redação para PTE',
      subtitle: 'Obtenha 79+ pontos com nossos modelos e estratégias de redação comprovados',
      stats: {
        writingTime: '20 minutos de tempo de escrita',
        wordCount: '200-300 palavras',
        readTime: '8 min de leitura'
      },
      universalTemplate: {
        title: 'Modelo Universal de Redação',
        copyButton: 'Copiar Modelo',
        copiedButton: 'Copiado!',
        tip: {
          title: 'Dica Profissional:',
          message: 'Você pode inventar citações, estatísticas e exemplos! O PTE não verifica fatos. Apenas certifique-se de que sejam relevantes e apoiem seu argumento.'
        }
      },
      templatesByType: {
        title: 'Modelos por Tipo de Redação',
        essays: {
          agreeDisagree: {
            title: 'Redação de Concordância/Divergência',
            prompt: 'Em que medida você concorda ou discorda?'
          },
          discussion: {
            title: 'Redação de Discussão',
            prompt: 'Discuta ambos os pontos de vista e dê sua opinião.'
          },
          problemSolution: {
            title: 'Redação de Problema-Solução',
            prompt: 'Quais são os problemas e as soluções?'
          }
        },
        copyButton: 'Copiar'
      },
      example: {
        title: 'Exemplo Completo de Redação',
        topicLabel: 'Tópico:',
        wordCount: 'Contagem de palavras: ~240 palavras'
      },
      transitionPhrases: {
        title: 'Frases de Transição Essenciais',
        categories: {
          adding: 'Adicionando Informações',
          contrasting: 'Contrastando',
          examples: 'Dando Exemplos',
          concluding: 'Concluindo',
          opinion: 'Expressando Opinião'
        }
      },
      vocabulary: {
        title: 'Vocabulário Específico do Tópico',
        topics: [
          'Tecnologia',
          'Meio Ambiente',
          'Educação',
          'Saúde',
          'Economia'
        ]
      },
      tips: {
        title: 'Dicas Profissionais para Altas Pontuações'
      },
      mistakes: {
        list: [
          'Escrever menos de 200 ou mais de 300 palavras',
          'Não abordar a pergunta diretamente',
          'Usar linguagem informal ou contrações',
          'Esquecer de incluir exemplos',
          'Ter apenas um argumento principal',
          'Não revisar a gramática e a ortografia',
          'Escrever redações memorizadas sem adaptá-las ao tópico',
          'Conclusão fraca ou ausente'
        ]
      },
      timeManagement: {
        title: 'Gerenciamento de Tempo de 20 Minutos',
        steps: {
          planning: '0-3 min: Analisar pergunta, fazer brainstorming de ideias, escolher modelo',
          writing: '3-17 min: Escrever redação seguindo a estrutura do modelo',
          proofreading: '17-20 min: Revisar gramática, ortografia, contagem de palavras'
        }
      },
      cta: {
        title: 'Pronto para Escrever Redações Perfeitas?',
        subtitle: 'Pratique com tópicos reais de redação PTE e obtenha feedback instantâneo da IA sobre sua escrita',
        tryExercise: 'Experimentar Exercício de Redação'
      },
      related: {
        describeImage: {
          title: 'Modelo de Descrição de Imagem',
          description: 'Estrutura perfeita para descrição de imagens'
        },
        retellLecture: {
          description: 'Abordagem estruturada para palestras'
        }
      }
    },
    summarizeWrittenText: {
      backToBlog: 'Voltar ao Blog',
      subtitle: 'Domine a arte de condensar passagens em frases poderosas e únicas',
      stats: {
        time: '10 minutos por tarefa',
        wordLimit: '5-75 palavras',
        oneSentence: 'APENAS UMA frase'
      },
      criticalRule: {
        title: 'Regra Crítica',
        description: 'Você DEVE escrever exatamente UMA frase. Escrever múltiplas frases = ZERO pontos!',
        note: 'Sua frase deve ter entre 5-75 palavras (ideal: 25-35 palavras)'
      },
      strategy: {
        title: 'Estratégia de 4 Passos',
        steps: {
          step1: {
            title: 'Identifique o Tópico Principal',
            description: 'Leia as primeiras e últimas frases cuidadosamente - elas geralmente contêm a ideia principal',
            tip: 'Pergunte a si mesmo: \'Sobre o que é este trecho principalmente?\''
          },
          step2: {
            title: 'Encontre Pontos de Apoio Chave',
            description: 'Procure 2-3 ideias principais de apoio que expliquem ou desenvolvam o tópico principal',
            tip: 'Concentre-se em ideias que aparecem várias vezes ou que possuem exemplos'
          },
          step3: {
            title: 'Use Conectores Efetivamente',
            description: 'Conecte ideias usando palavras como \'e\', \'mas\', \'embora\', \'enquanto\', \'além disso\'',
            tip: 'Evite usar \'e\' muitas vezes - varie seus conectores'
          },
          step4: {
            title: 'Mantenha o Tom Acadêmico',
            description: 'Use vocabulário formal e evite opiniões pessoais ou interpretações',
            tip: 'Mantenha-se no que o autor diz, não no que você pensa'
          }
        }
      },
      sentenceStructures: {
        title: 'Estruturas de Frases Úteis',
        description: 'Aprenda padrões para criar resumos concisos e precisos'
      },
      mistakes: {
        title: 'Erros Comuns e Como Corrigi-los'
      },
      grammar: {
        title: 'Gramática Essencial'
      },
      timeManagement: {
        title: 'Estratégia de Tempo de 10 Minutos'
      },
      connectors: {
        title: 'Frases de Conexão Úteis',
        sections: {
          add: 'Para Adicionar Informações',
          contrast: 'Para Mostrar Contraste',
          cause: 'Para Mostrar Causa/Efeito',
          conclude: 'Para Concluir'
        }
      },
      cta: {
        subtitle: 'Domine o Resumo de Texto Escrito com trechos reais e feedback instantâneo da IA'
      },
      related: {
        title: 'Recursos Relacionados',
        essayWriting: {
          description: 'Estruturas de redação de 200-300 palavras'
        },
        describeImage: {
          description: 'Descrição de imagem para tarefa de fala'
        },
        retellLecture: {
          description: 'Estratégias de resumo de palestra'
        }
      },
      loading: 'Carregando exercício...',
      error: 'Ocorreu um erro ao carregar o exercício.',
      wordCount: 'Contagem de palavras: {count}',
      textAreaPlaceholder: 'Comece a escrever seu resumo aqui...'
    },
    blog: {
      title: 'Blog de Preparação PTE',
      subtitle: 'Dicas de especialistas, estratégias e insights para ajudar você a alcançar sua pontuação alvo no PTE',
      numberArticles: 'Artigos de {0}',
      categories: [
        "Todos",
        "Falar",
        "Escrever",
        "Leitura",
        "Ouvir",
        "Modelos"
      ],
      sidebar: {
        categories: 'Categorias',
        popularPosts: 'Posts Populares',
        newsletter: {
          title: 'Newsletter',
          description: 'Receba dicas semanais do PTE em sua caixa de entrada',
          placeholder: 'Seu e-mail',
          button: {
            subscribing: 'Inscrevendo-se...',
            subscribe: 'Assinar'
          },
          messages: {
            success: 'Inscrição realizada com sucesso!',
            error: 'Falha na inscrição. Por favor, tente novamente.'
          }
        }
      },
      main: {
        headings: {
          all: 'Modelos e Estratégias PTE',
          templates: 'Todos os Modelos'
        },
        noArticles: {
          message: 'Nenhum artigo encontrado nesta categoria ainda.',
          hint: 'Volte em breve para mais conteúdo!'
        }
      },
      cta: {
        title: 'Pronto para melhorar sua pontuação no PTE?',
        subtitle: 'Comece a praticar com nossa plataforma completa de preparação para o PTE',
        button: 'Comece a Praticar Grátis'
      },
      articles: [
        {
          title: 'Modelo de recontagem de palestra para PTE',
          description: 'Domine a tarefa Retell Lecture com nosso modelo comprovado e dicas de especialistas para organizar sua resposta de forma eficaz.',
          category: 'Falando',
          readTime: '5 min',
          tags: ['Falando', 'Modelos', 'Recontar a Palestra']
        },
        {
          title: 'Modelo de descrever imagem para PTE',
          description: 'Guia completo com modelos para todos os tipos de imagem - gráficos, tabelas, diagramas, mapas e muito mais.',
          category: 'Falando',
          readTime: '7 min',
          tags: ['Falando', 'Modelos', 'Descreva a imagem']
        },
        {
          title: 'Modelos de Redação de Dissertação para PTE',
          description: 'Alcance 79+ com nossos modelos abrangentes de dissertação cobrindo todos os tipos e tópicos de redação.',
          category: 'Escrevendo',
          readTime: '8 min',
          tags: ['Escrevendo', 'Modelos', 'Ensaio']
        },
        {
          title: 'Resumir texto escrito - Dicas e Estratégias',
          description: 'Aprenda a condensar passagens em frases únicas e poderosas com nossas estratégias de especialistas.',
          category: 'Escrevendo',
          readTime: '6 min',
          tags: ['Escrevendo', 'Modelos', 'Resumir texto']
        }
      ]
    },
    contact: {
      hero: {
        title: 'Fale Conosco',
        subtitle: 'Estamos aqui para ajudar você a ter sucesso em sua jornada PTE',
        haveAQuestionOrNeedHelp: "Tem alguma dúvida ou precisa de ajuda? Estamos aqui para te auxiliar."
      },
      info: {
        title: 'Entre em Contato',
        email: 'E-mail',
        phone: 'Telefone',
        location: 'Localização',
        supportHours: 'Horário de Suporte',
        languages: 'Idiomas'
      },
      quickLinks: {
        title: 'Links Rápidos',
        helpCenter: 'Central de Ajuda',
        faq: 'Perguntas Frequentes'
      },
      form: {
        title: 'Envie-nos uma Mensagem',
        labels: {
          name: 'Seu Nome *',
          email: 'Endereço de E-mail *',
          emailFill: 'E-mail *',
          category: 'Categoria *',
          subject: 'Assunto *',
          message: 'Mensagem *',
          requiredFields: '* Campos obrigatórios',
        },
        value: {
          general: "geral",
          technical: "técnico",
          billing: "cobrança",
          feedback: "feedback",
          partnership: "parceria"
        },
        placeholders: {
          subject: 'Breve descrição de sua dúvida',
          message: 'Por favor, forneça o máximo de detalhes possível...',
          yourFullName: "Seu nome completo",
          whatIsThisAbout: "Sobre o que se trata?",
          tellUsHowWeCanHelpYou: "Diga-nos como podemos ajudar você..."
        },
        options: {
          general: 'Dúvida Geral',
          technical: 'Suporte Técnico',
          billing: 'Cobrança e Assinatura',
          partnership: 'Parceria'
        },
        buttons: {
          sending: 'Enviando...',
          send: 'Enviar Mensagem'
        },
      },
      notice: {
        responseTime: [
          'Tempo médio de resposta: Geralmente respondemos em até 24 horas durante dias úteis. Para problemas técnicos urgentes, inclua "URGENTE" no campo de assunto.',
          'Tempo médio de resposta: Geralmente respondemos em até 24 horas durante dias úteis. Para problemas técnicos urgentes, inclua "URGENT" no campo de assunto.' // Mantendo 'URGENT' conforme a versão original em inglês
        ]
      },
      failedToSendYourMessage: 'Falha ao enviar sua mensagem. Tente novamente ou envie um e-mail diretamente para support@pteasy.com.au',
      success: 'Obrigado pela sua mensagem! Responderemos em até 24 horas.',
      responseTime: "Tempo de Resposta",
      within24Hours: "Em até 24 horas",
      sendUsAMessage: "Envie-nos uma mensagem",
      thankYouForContactingUs: "Obrigado por nos contatar! Sua mensagem foi enviada com sucesso. Responderemos em até 24 horas.",
      lookingForQuickAnswers: "Procurando respostas rápidas? Confira nossa",
      faqPage: "página de Perguntas Frequentes",
      weReHereToHelp: 'Estamos aqui para ajudar você a ter sucesso em sua jornada PTE',
      sOPauloBrazil: 'São Paulo, Brasil',
      monFri9am6pm: 'Seg-Sex: 9h - 18h BRT',
      sat10am2pmBrt: 'Sáb: 10h - 14h BRT',
      english: 'Inglês, Português, Espanhol',
      averageResponse: 'Tempo médio de resposta:',
      weTypically: 'Geralmente respondemos em até 24 horas durante dias úteis. Para problemas técnicos urgentes, inclua "URGENTE" no campo de assunto.',
    },
    cookiePolicy: {
      hero: {
        title: 'Política de Cookies',
        subtitle: 'Entenda como usamos cookies para melhorar sua experiência',
        lastUpdated: 'Última atualização: 15 de janeiro de 2025'
      },
      summary: {
        title: 'Resumo Rápido',
        description: 'Usamos cookies para lembrar suas preferências, manter você logado, analisar o uso do site e melhorar sua experiência de aprendizado. Você pode controlar as configurações de cookies através do seu navegador, embora alguns recursos possam não funcionar corretamente sem eles.'
      },
      sections: {
        whatAreCookies: {
          title: 'O Que São Cookies?',
          paragraphs: [
            'Cookies são pequenos arquivos de texto que são colocados em seu dispositivo quando você visita um site. Eles ajudam o site a lembrar informações sobre sua visita, tornando sua próxima visita mais fácil e o site mais útil para você.',
            'Cookies não contêm nenhuma informação que o identifique pessoalmente, mas informações pessoais que armazenamos sobre você podem ser vinculadas às informações obtidas de cookies.'
          ]
        },
        whyWeUseCookies: {
          title: 'Por Que Usamos Cookies',
          description: 'O PTEasy usa cookies para vários propósitos importantes:',
          list: [
            'Autenticação: Para manter você logado em sua conta',
            'Preferências: Para lembrar suas configurações e preferências',
            'Segurança: Para dar suporte a recursos de segurança e detectar atividades maliciosas',
            'Análise: Para entender como você usa nossa plataforma e melhorá-la',
            'Desempenho: Para garantir que a plataforma funcione de forma eficiente',
            'Personalização: Para personalizar sua experiência de aprendizado'
          ]
        },
        typesOfCookies: {
          title: 'Tipos de Cookies Que Usamos',
          essential: {
            title: 'Cookies Essenciais',
            description: 'Esses cookies são necessários para o funcionamento adequado do site. Eles não podem ser desativados.',
            list: [
              'Autenticação do usuário e gerenciamento de sessão',
              'Tokens de segurança e proteção CSRF',
              'Balanceamento de carga e atribuição de servidor',
              'Funcionalidade básica da plataforma'
            ]
          },
          functional: {
            title: 'Cookies Funcionais',
            description: 'Esses cookies ativam recursos personalizados e lembram suas escolhas.',
            list: [
              'Preferências de idioma',
              'Configurações e preferências de estudo',
              'Configurações de volume para exercícios de áudio',
              'Exercícios visualizados recentemente'
            ]
          },
          analytics: {
            title: 'Cookies de Análise',
            description: 'Esses cookies nos ajudam a entender como os visitantes interagem com nossa plataforma.',
            list: [
              'Páginas visitadas e tempo gasto',
              'Taxas de conclusão de exercícios',
              'Rastreamento de erros e depuração',
              'Métricas de desempenho'
            ]
          },
          marketing: {
            title: 'Cookies de Marketing',
            description: 'Esses cookies podem ser usados para mostrar conteúdo relevante e medir a eficácia da campanha.',
            list: [
              'Rastrear conversões de campanhas de marketing',
              'Medir a eficácia dos anúncios',
              'Retargeting para ofertas relevantes'
            ]
          }
        },
        thirdParty: {
          title: 'Cookies de Terceiros',
          description: 'Usamos serviços de provedores terceirizados que podem definir seus próprios cookies:',
          list: [
            'Stripe: Processamento de pagamentos e prevenção de fraudes',
            'Cloudinary: Entrega e otimização de mídia',
            'Google Analytics: Estatísticas de uso do site (se ativado)',
            'Google OAuth: Autenticação segura'
          ],
          note: 'Esses provedores têm suas próprias políticas de privacidade e práticas de cookies. Recomendamos revisar suas políticas para obter mais informações.'
        },
        duration: {
          title: 'Duração dos Cookies',
          description: 'Usamos cookies de sessão e persistentes:',
          session: {
            title: 'Cookies de Sessão',
            text: 'Cookies temporários que são excluídos quando você fecha o navegador. Usados para manter sua sessão enquanto você navega na plataforma.'
          },
          persistent: {
            title: 'Cookies Persistentes',
            text: 'Permanecem em seu dispositivo por um período definido. Usados para lembrar suas preferências e informações de login. Normalmente expiram após 30-90 dias.'
          }
        },
        managing: {
          title: 'Gerenciando Cookies',
          browserSettings: {
            title: 'Configurações do Navegador',
            description: 'Você pode controlar e excluir cookies através das configurações do seu navegador. Veja como para navegadores populares:',
            browsers: [
              'Chrome',
              'Firefox',
              'Safari',
              'Internet Explorer/Edge'
            ],
            note: 'Desabilitar cookies pode afetar a funcionalidade do PTEasy. Alguns recursos podem não funcionar corretamente sem cookies ativados.'
          },
          optOut: {
            title: 'Opções de Opt-Out',
            description: 'Você pode optar por não participar de categorias específicas de cookies:',
            options: [
              'Cookies de análise: Instale o Complemento do Navegador para desativar o Google Analytics',
              'Cookies de marketing: Visite a página de opt-out da Digital Advertising Alliance'
            ]
          }
        },
        impact: {
          title: 'Impacto da Desativação de Cookies',
          description: 'Se você desativar os cookies, poderá experimentar:',
          list: [
            'Incapacidade de permanecer logado',
            'Perda de configurações personalizadas',
            'Funcionalidade reduzida nos exercícios',
            'Necessidade de reinserir informações com mais frequência',
            'Experiência de aprendizado menos personalizada'
          ]
        },
        doNotTrack: {
          title: 'Não Rastrear (Do Not Track)',
          description: 'O PTEasy atualmente não responde aos sinais de navegador "Do Not Track" (DNT). Continuamos trabalhando em formas de responder aos sinais DNT do navegador e atualizaremos esta política quando o fizermos.'
        },
        updates: {
          title: 'Atualizações Desta Política',
          description: 'Podemos atualizar esta Política de Cookies periodicamente. Notificaremos você sobre quaisquer alterações materiais publicando a nova Política de Cookies nesta página e atualizando a data de \'Última atualização\'.'
        }
      },
      consent: {
        message: 'Seu Consentimento: Ao continuar a usar o PTEasy, você consente com nosso uso de cookies conforme descrito nesta política. Você pode retirar seu consentimento a qualquer momento ajustando as configurações do seu navegador.'
      },
      related: {
        title: 'Políticas Relacionadas',
        links: [
          'Política de Privacidade',
          'Termos de Serviço'
        ]
      }
    },
    account: {
      signOut: 'Sair',
      signingOut: 'Saindo...',
      memberSince: 'Membro desde',
      manage: 'Gerenciar',
      openingStripePortal: 'Abrindo Portal Stripe...',
      profile: {
        defaultName: 'Usuário',
        withoutEmail: 'Sem email',
        noEmail: 'Nenhum e-mail disponível',
        memberSince: 'Membro desde',
        recently: 'Recentemente'
      },
      stats: {
        practiceSessions: 'Sessões de Prática',
        dayStreak: 'Sequência de Dias'
      },
      buttons: {
        startPractice: 'Iniciar Prática',
        viewProgress: 'Ver Progresso',
        signOut: 'Sair',
        signingOut: 'Saindo...'
      },
      sections: {
        accountSettings: 'Configurações da Conta',
        studyProgress: 'Progresso de Estudo',
        support: 'Suporte'
      },
      menu: {
        editProfile: {
          title: 'Editar Perfil',
          description: 'Atualize suas informações pessoais'
        },
        subscription: {
          title: 'Assinatura',
          description: 'Gratuito',
          badge: 'Atualizar',
        },
        changePassword: {
          title: 'Alterar Senha',
          description: 'Atualize a senha da sua conta'
        },
        emailPreferences: {
          title: 'Preferências de E-mail',
          description: 'Gerenciar newsletter e notificações por e-mail'
        },
        progressReport: {
          title: 'Relatório de Progresso',
          description: 'Ver análises detalhadas'
        },
        achievements: {
          title: 'Conquistas',
          description: 'Acompanhe seus marcos'
        },
        practiceHistory: {
          title: 'Histórico de Prática',
          description: 'Revisar exercícios anteriores'
        },
        helpCenter: {
          description: 'FAQs e suporte'
        },
        privacySecurity: {
          title: 'Privacidade e Segurança',
          description: 'Configurações de dados e privacidade'
        }
      },
      menuSections: [
        {
          title: "Configurações da Conta",
          items: [
            {
              title: "Editar Perfil",
              description: "Atualize suas informações pessoais",
            },
            {
              title: "Assinatura",
            },
            {
              title: "Alterar Senha",
              description: "Atualize a senha da sua conta",
            },
            {
              title: "Preferências de E-mail",
              description: "Gerenciar newsletter e notificações por e-mail",
            },
          ],
        },
        {
          title: "Progresso de Estudo",
          items: [
            {
              title: "Relatório de Progresso",
              description: "Ver análises detalhadas",
            },
            {
              title: "Conquistas",
              description: "Acompanhe seus marcos",
            },
            {
              title: "Histórico de Prática",
              description: "Revisar exercícios anteriores",
            },
          ],
        },
        {
          title: "Suporte",
          items: [
            {
              title: "Central de Ajuda",
              description: "FAQs e suporte",
            },
            {
              title: "Privacidade e Segurança",
              description: "Configurações de dados e privacidade",
            },
          ],
        },
      ]
    },
    achievements: {
      backButton: 'Voltar para a Conta',
      header: {
        subtitle: 'Acompanhe seus marcos e desbloqueie recompensas à medida que avança'
      },
      comingSoon: {
        title: 'Sistema de Conquistas em Breve!',
        description: 'Estamos construindo um sistema de conquistas emocionante para tornar sua jornada de preparação para o PTE ainda mais gratificante! Navegue pelos distintivos incríveis que você poderá colecionar e veja quais desafios esperam por você.',
        highlights: [
          'Desbloqueie distintivos únicos',
          'Complete desafios',
          'Acompanhe seu progresso',
          'Ganhe recompensas'
        ]
      },
      progressOverview: {
        title: 'Progresso Geral',
        levelTitle: 'Nível',
        streak: {
          title: 'Sequência Atual',
          empty: 'Comece a praticar para construir sua sequência!'
        },
        stats: {
          unlocked: 'desbloqueado',
          remaining: 'restantes',
          toNextLevel: '{0}/500 para o próximo nível'
        }
      },
      nextAchievements: {
        title: 'Quase Lá!'
      },
      filters: {
        showUnlockedOnly: 'Mostrar apenas desbloqueados'
      },
      rewards: {
        title: 'Próximas Recompensas',
        levels: [
          {
            level: 'Nível 5',
            name: 'Distintivo: Estrela Ascendente',
            requirement: '2.500 pontos necessários'
          },
          {
            level: 'Nível 10',
            name: 'Título: PTE Expert',
            requirement: '5.000 pontos necessários'
          },
          {
            level: 'Nível 15',
            name: 'Tema de Perfil: Ouro',
            requirement: '7.500 pontos necessários'
          }
        ]
      },
      howItWorks: {
        title: 'Como o Sistema de Conquistas Funcionará',
        items: [
          'Rastreamento Automático: Suas conquistas serão rastreadas automaticamente à medida que você pratica',
          'Atualizações em Tempo Real: As barras de progresso serão atualizadas em tempo real à medida que você completa os exercícios',
          'Sistema de Notificação: Seja notificado instantaneamente quando desbloquear novos distintivos',
          'Exibição de Perfil: Mostre suas conquistas em sua página de perfil',
          'Pontos de Recompensa: Ganhe pontos por cada conquista para desbloquear recursos especiais'
        ]
      },
      achievementsStatistics: {
        consistency: [
          {
            name: 'Sequência de 3 Dias',
            description: 'Pratique por 3 dias seguidos',
            rarity: 'comum'
          },
          {
            name: 'Guerreiro da Semana',
            description: 'Pratique por 7 dias seguidos',
            rarity: 'incomum'
          },
          {
            name: 'Lutador da Quinzena',
            description: 'Pratique por 14 dias seguidos',
            rarity: 'rara'
          },
          {
            name: 'Mestre Mensal',
            description: 'Pratique por 30 dias seguidos',
            rarity: 'épica'
          },
          {
            name: 'Campeão do Século',
            description: 'Pratique por 100 dias seguidos',
            rarity: 'lendária'
          }
        ],
        milestones: [
          {
            name: 'Começando',
            description: 'Complete 10 exercícios',
            rarity: 'comum'
          },
          {
            name: 'Meio Século',
            description: 'Complete 50 exercícios',
            rarity: 'incomum'
          },
          {
            name: 'Centurião',
            description: 'Complete 100 exercícios',
            rarity: 'rara'
          },
          {
            name: 'Expert em Exercícios',
            description: 'Complete 500 exercícios',
            rarity: 'épica'
          },
          {
            name: 'Lenda da Prática',
            description: 'Complete 1000 exercícios',
            rarity: 'lendária'
          }
        ],
        skills: [
          {
            name: 'Mestre da Fala',
            description: 'Conquiste mais de 80 pontos em Fala',
            rarity: 'rara'
          },
          {
            name: 'Mago da Escrita',
            description: 'Conquiste mais de 80 pontos em Escrita',
            rarity: 'rara'
          },
          {
            name: 'Campeão da Leitura',
            description: 'Conquiste mais de 80 pontos em Leitura',
            rarity: 'rara'
          },
          {
            name: 'Lenda da Compreensão Auditiva',
            description: 'Conquiste mais de 80 pontos em Compreensão Auditiva',
            rarity: 'rara'
          },
          {
            name: 'Multitarefas',
            description: 'Conquiste mais de 75 pontos em todas as quatro habilidades',
            rarity: 'lendária'
          }
        ],
        special: [
          {
            name: 'Pontuação Perfeita',
            description: 'Conquiste 90 pontos em qualquer exercício',
            rarity: 'épica'
          },
          {
            name: 'Coruja da Noite',
            description: 'Pratique depois da meia-noite',
            rarity: 'incomum'
          },
          {
            name: 'Madrugador',
            description: 'Pratique antes das 6 AM',
            rarity: 'incomum'
          },
          {
            name: 'Herói do Simulado',
            description: 'Complete 10 simulados',
            rarity: 'épica'
          },
          {
            name: 'Velocista',
            description: 'Complete 10 exercícios em menos de 30 minutos',
            rarity: 'rara'
          }
        ]
      },
      categories: [
        'Todos',
        'Consistência',
        'Marcos',
        'Habilidades',
        'Especial',
      ]
    },
    changePassword: {
      header: {
        subtitle: 'Atualize a senha da sua conta para mantê-la segura'
      },
      form: {
        currentPasswordLabel: 'Senha Atual',
        currentPasswordPlaceholder: 'Digite sua senha atual',
        newPasswordLabel: 'Nova Senha',
        newPasswordPlaceholder: 'Digite sua nova senha',
        confirmPasswordLabel: 'Confirmar Nova Senha',
        confirmPasswordPlaceholder: 'Confirme sua nova senha',
        errors: {
          allFieldsRequired: 'Todos os campos são obrigatórios',
          passwordTooShort: 'A senha deve ter pelo menos 6 caracteres',
          passwordsDoNotMatch: 'As novas senhas não coincidem',
          sameAsCurrent: 'A nova senha deve ser diferente da senha atual'
        },
        success: 'Senha alterada com sucesso!',
        failure: 'Falha ao alterar a senha. Por favor, verifique sua senha atual e tente novamente.',
        passwordStrength: {
          weak: 'Fraca',
          fair: 'Razoável',
          good: 'Boa',
          strong: 'Forte',
          veryStrong: 'Muito Forte'
        },
        passwordTips: [
          'Considere adicionar uma letra maiúscula para maior segurança',
          'Considere adicionar um número para maior segurança',
          'Considere adicionar um caractere especial para maior segurança'
        ],
        confirmationError: 'As senhas não coincidem'
      },
      securityTips: {
        title: 'Dicas de Segurança',
        list: [
          'Use uma senha única que você não usa em outros sites',
          'Considere usar um gerenciador de senhas para gerar e armazenar senhas',
          'Altere sua senha regularmente para manter a segurança da conta'
        ]
      },
      buttons: {
        changePasswordButton: 'Alterar Senha',
        loading: 'Alterando Senha...'
      }
    },
    dashboard: {
      header: {
        greeting: {
          morning: 'Bom dia',
          afternoon: 'Boa tarde',
          evening: 'Boa noite'
        },
        subtitle: 'Pronto para praticar para o seu exame PTE? Vamos melhorar suas habilidades hoje.'
      },
      stats: {
        todaysPractice: {
          label: 'Prática de Hoje',
          subtext: 'Continue assim!'
        },
        weeklyGoal: {
          label: 'Meta Semanal',
          subtext: 'Complete 100 exercícios'
        },
        currentStreak: {
          subtext: 'dias',
          passed: 'Concluído',
          today: 'Hoje!',
          oneDay: '1 dia',
          multipleDays: '{0} dias'
        },
        daysToExam: {
          label: 'Dias para o Exame',
          subtextSet: 'Até o exame PTE',
          subtextUnset: 'Definir sua data'
        }
      },
      progress: {
        weeklyProgress: {
          title: 'Progresso Semanal',
          exercisesCompleted: 'Exercícios Concluídos'
        },
        targetScore: {
          title: 'Pontuação Alvo',
          current: 'Atual',
          target: 'Alvo',
          saveButton: 'Salvar'
        },
        dailyTip: {
          title: 'Dica Diária',
          action: 'Praticar Agora →'
        }
      },
      skills: {
        title: 'Praticar por Habilidade',
        subtitle: 'Escolha uma habilidade para começar a praticar'
      },
      quickActions: {
        takeMockTest: 'Fazer Simulado',
        practiceWeakAreas: 'Praticar Áreas Fracas',
        dailyChallenge: 'Desafio Diário',
        studyPlan: 'Plano de Estudo'
      },
      modals: {
        examDate: {
          title: 'Defina a Data do Seu Exame'
        }
      },
      greeting: 'Olá,',
      title: 'Vamos começar a praticar',
      searchPlaceholder: 'Buscar um exercício...',
      allSkills: 'Todas as Habilidades',
      sidebar: {
        practice: 'Prática',
        mockTests: 'Simulados',
        community: 'Comunidade',
        myAccount: 'Minha Conta',
        logout: 'Sair'
      },
      welcome: {
        title: 'Bem-vindo ao seu centro de prática PTE',
        subtitle: 'Todas as ferramentas que você precisa para se preparar para o seu teste, em um só lugar.'
      },
      practicePrompt: 'O que você gostaria de praticar hoje?',
      progressText: '{count} exercícios concluídos',
      noResults: 'Nenhum exercício encontrado correspondendo à sua busca.',
      clearSearch: 'Limpar Busca',
      studyPlan: {
        title: 'Meu Plano de Estudo',
        recommended: {
          title: 'Recomendado para você',
          subtitle: 'Com base no seu desempenho e objetivos.'
        },
        continue: {
          title: 'Continue de onde parou',
        },
        weeklyGoals: {
          title: 'Metas Semanais',
          exercises: 'Exercícios a completar',
          mockTests: 'Simulados a fazer',
          practiceHours: 'Horas de prática'
        },
        practiceSummary: {
          title: 'Resumo da Prática',
          viewReport: 'Ver Relatório Completo'
        },
        enrolledModules: {
          title: 'Módulos Matriculados',
          viewAll: 'Ver Todos os Módulos'
        },
        overallScore: {
          title: 'Pontuação Geral'
        },
        studyGroup: {
          title: 'Grupo de Estudo'
        }
      },
      label: {
        todaysPractice: "Prática de Hoje",
        weeklyGoal: 'Meta Semanal',
        currentStreak: 'Sequência Atual',
        daysToExam: 'Dias para o Exame',
        uploadProgress: 'Enviar Progresso'
      },
      subtext: {
        keepItUp: "Continue assim!",
        complete5Exercices: "Complete 100 exercícios",
        days: "dias",
        untilPteExam: "Até o exame PTE",
        setYourDate: "Defina sua data"
      }
    },
    mockTests: {
      questionsNumber: '{0} questões',
      questionNumber: '{0} questão',
      hourNumber: '{0} hora',
      hoursNumber: '{0} horas',
      estimatedScoreRange: 'Intervalo de pontuação estimado:',
      wereWorkingToAdd: "Estamos trabalhando para adicionar mais simulados, e eles estarão disponíveis em breve!",
      exercisesPracticed: 'Exercícios Praticados',
      header: {
        subtitle: 'Pratique com simulados PTE completos e acompanhe seu progresso',
        stats: {
          testsCompleted: 'Testes Concluídos',
          avgScore: 'Pontuação Média',
          bestScore: 'Melhor Pontuação'
        },
        tabs: {
          available: 'Testes Disponíveis',
          completed: 'Meus Resultados'
        }
      },
      filters: {
        difficultyLabel: 'Filtrar por dificuldade:',
        all: 'Todos',
        easy: 'Fácil',
        medium: 'Médio',
        hard: 'Difícil'
      },
      available: {
        estimatedScore: 'Faixa de pontuação estimada',
        startTest: 'Iniciar Teste',
        continuePreviousSession: 'Continuar sessão anterior',
        noTests: {
          message: 'Nenhum teste disponível para a dificuldade selecionada'
        }
      },
      completed: {
        noTests: {
          title: 'Nenhum Teste Concluído Ainda',
          message: 'Comece seu primeiro simulado para ver seu desempenho e acompanhar seu progresso ao longo do tempo.',
          button: 'Navegar por Testes Disponíveis'
        },
        statuses: {
          processing: 'Processando',
          evaluated: 'Avaliado',
          completed: 'Concluído'
        },
        evaluation: {
          inProgress: 'Avaliação em Andamento',
          message: 'Seu teste está sendo avaliado por nosso sistema de pontuação de IA. Isso geralmente leva de 2 a 5 minutos.'
        },
        scores: {
          overall: 'Geral',
          sections: {
            speaking: 'Fala',
            writing: 'Escrita',
            reading: 'Leitura',
            listening: 'Compreensão Auditiva'
          }
        }
      }
    },
    notificationSettings: {
      header: {
        subtitle: 'Gerencie como e quando você recebe e-mails do PTEasy'
      },
      loading: 'Carregando preferências...',
      messages: {
        success: 'Preferências de e-mail salvas com sucesso!',
        error: 'Falha ao salvar preferências. Por favor, tente novamente.'
      },
      section: {
        title: 'Assinaturas de E-mail',
        description: 'Escolha os tipos de e-mail que você gostaria de receber do PTEasy'
      },
      emailCategories: [
        {
          title: 'Newsletter e Atualizações',
          description: 'Receba nossa newsletter com dicas de estudo, atualizações da plataforma e histórias de sucesso',
        },
        {
          title: 'Lembretes de Prática',
          description: 'Seja lembrado para completar suas sessões de prática diárias e manter sua sequência',
        },
        {
          title: 'Notificações de Conquistas',
          description: 'Seja notificado quando atingir marcos, completar metas ou ganhar distintivos',
        },
        {
          title: 'Anúncios Importantes',
          description: 'Atualizações críticas sobre manutenção, novos recursos e alterações na plataforma',
        }
      ],
      notice: {
        title: 'Importante',
        message: 'Você sempre receberá e-mails transacionais essenciais, como redefinições de senha, confirmações de pagamento e alertas de segurança, independentemente dessas configurações.'
      },
      buttons: {
        save: 'Salvar Preferências',
        saving: 'Salvando...'
      }
    },
    onboarding: {
      skipOnboarding: "Pular integração? Você sempre pode atualizar essas preferências mais tarde nas configurações do seu perfil.",
      steps: {
        one: {
          title: 'Idioma Nativo',
          subtitle: 'Para dicas personalizadas'
        },
        two: {
          title: 'Como Você se Identifica',
          subtitle: 'Personalize a experiência'
        },
        three: {
          title: 'Nível de Inglês',
          subtitle: 'Proficiência atual'
        },
        four: {
          title: 'Data do Exame',
          subtitle: 'Planeje seu cronograma'
        },
        five: {
          subtitle: 'Defina suas metas'
        },
        six: {
          title: 'Tempo de Estudo',
          subtitle: 'Compromisso diário'
        },
        seven: {
          title: 'Tudo Pronto!',
          subtitle: 'Revisar e começar'
        }
      },
      onboardingSteps: [
        { title: "Idioma Nativo", subtitle: "Para dicas personalizadas" },
        { title: "Como Você se Identifica", subtitle: "Personalizar experiência" },
        { title: "Nível de Inglês", subtitle: "Proficiência atual" },
        { title: "Data do Exame", subtitle: "Planeje seu cronograma" },
        { title: "Pontuação Alvo", subtitle: "Defina suas metas" },
        { title: "Tempo de Estudo", subtitle: "Compromisso diário" },
        { title: "Tudo Pronto!", subtitle: "Revisar e começar" },
      ],
      messages: {
        skipConfirm: 'Pular integração? Você sempre pode atualizar essas preferências mais tarde nas configurações do seu perfil.',
        saving: 'Salvando dados de integração...',
        success: 'Integração concluída com sucesso!',
        error: 'Erro ao salvar dados de integração. Por favor, tente novamente.',
        evaluation: 'Suas preferências estão sendo salvas...'
      },
      navigationHints: {
        skip: 'Pular',
        navigate: 'Navegar'
      }
    },
    subscription: {
      header: {
        subtitle: 'Gerencie seu plano atual e explore opções de upgrade',
        updatingYourSubscription: 'Atualizando sua assinatura...',
        plaseWaitWhileWeRefresh: 'Por favor, aguarde enquanto atualizamos as informações da sua conta'
      },
      currentPlan: {
        title: 'Plano Atual',
        label: 'Você está atualmente no',
        free: 'Plano Gratuito',
        premium: 'Plano Premium',
        expiry: 'Expira em',
        renews: 'Renova em',
        featuresTitle: 'Recursos incluídos:'
      },
      actions: {
        upgrade: 'Atualizar Plano',
        cancel: 'Cancelar Assinatura',
        renew: 'Renovar Assinatura',
        loading: 'Processando...'
      },
      upgradeOptions: {
        title: 'Opções de Upgrade',
        monthly: {
          title: 'Plano Mensal',
          description: 'Cobrado mensalmente, cancele a qualquer momento'
        },
        yearly: {
          title: 'Plano Anual',
          description: 'Economize 20% com faturamento anual'
        }
      },
      confirmation: {
        cancelTitle: 'Cancelar Assinatura?',
        cancelMessage: 'Tem certeza de que deseja cancelar sua assinatura? Você ainda terá acesso até o final do ciclo de faturamento atual.',
        confirmCancel: 'Sim, Cancelar',
        keep: 'Manter Assinatura'
      },
      messages: {
        successUpgrade: 'Assinatura atualizada com sucesso!',
        successCancel: 'Assinatura cancelada com sucesso!',
        error: 'Algo deu errado. Por favor, tente novamente.'
      },
      features: {
        unlimitedPractice: 'Acesso Ilimitado à Prática',
        mockTests: 'Simulados Completos',
        aiScoring: 'Pontuação e Feedback Baseados em IA',
        detailedReports: 'Relatórios de Desempenho Detalhados',
        prioritySupport: 'Suporte Prioritário'
      },
      status: {
        active: 'Ativo',
        expired: 'Expirado',
        trial: 'Teste',
        canceled: 'Cancelado'
      }
    },
    practiceHistory: {
      subtitle: 'Revise seus exercícios anteriores e acompanhe sua melhoria',
      exportButton: 'Exportar Histórico',
      totalSessions: 'Total de Sessões',
      practiceTime: 'Tempo de Prática',
      averageScore: 'Pontuação Média',
      pteScoreBreakdown: 'Detalhes da pontuação PTE:',
      avgImprovement: 'Melhoria Média',
      searchPlaceholder: 'Buscar exercícios...',
  yourAnswerCorrect: 'Sua resposta (Correta!)',
  yourAnswerIncorrect: 'Sua resposta (Incorreta)',
  correctAnswer: 'Resposta correta',
  correct: 'Correta!',
  incorrect: 'Incorreta',
  missed: 'Não respondida', // ou 'Perdida', dependendo do contexto. 'Não respondida' é mais comum em feedback de prova.
  noFeedbackAvailable: 'Nenhum feedback disponível',
      filters: {
        today: 'Hoje',
        week: 'Última Semana',
        month: 'Último Mês',
        all: 'Todo o Período',
        sortByDate: 'Ordenar por Data',
        sortByScore: 'Ordenar por Pontuação',
        sortBySkill: 'Ordenar por Habilidade'
      },
      loading: 'Carregando seu histórico de prática...',
      showing: 'Mostrando',
      sessions: 'sessões',
      session: 'sessão',
      showingNumberSessions: 'Mostrando {0} {1}',
      exercises: {
        retellLecture: {
          title: 'Recontar Palestra'
        }
      }
    },
    profile: {
      backButton: 'Voltar',
      header: {
        save: 'Salvar Alterações'
      },
      messages: {
        success: 'Perfil atualizado com sucesso!',
        error: 'Falha ao atualizar perfil'
      },
      sections: {
        personalInfo: 'Informações Pessoais',
        targetScores: 'Pontuações Alvo PTE',
        studyPreferences: 'Preferências de Estudo'
      },
      avatar: {
        label: 'Foto de perfil',
        description: 'Seu avatar é gerado a partir do seu nome'
      },
      form: {
        name: {
          label: 'Nome Completo',
          placeholder: 'Digite seu nome completo'
        },
        email: {
          label: 'Endereço de E-mail'
        },
        nativeLanguage: {
          placeholder: 'Selecione seu idioma nativo',
          options: [
            'Português',
            'Espanhol',
            'Inglês',
            'Francês',
            'Alemão',
            'Italiano',
            'Chinês',
            'Japonês',
            'Coreano',
            'Outro'
          ]
        },
        gender: {
          label: 'Gênero',
          placeholder: 'Selecionar gênero',
          options: [
            'Masculino',
            'Feminino',
            'Prefiro não dizer'
          ]
        },
        proficiencyLevel: {
          label: 'Nível de Proficiência em Inglês',
          placeholder: 'Selecione seu nível',
          options: [
            {
              label: 'A0 - Iniciante',
              description: "Sou completamente novo no inglês",
            },
            {
              label: 'A1 - Elementar',
              description: 'Conheço algumas frases e sentenças básicas',
            },
            {
              label: 'A2 - Pré-Intermediário',
              description: 'Consigo gerenciar conversas básicas',
            },
            {
              label: 'B1 - Intermediário',
              description: 'Consigo conversar sobre tópicos do dia a dia',
            },
            {
              label: 'B2 - Pós-Intermediário',
              description: 'Consigo me comunicar confortavelmente com falantes nativos',
            },
            {
              label: 'C1 - Avançado',
              description: "Sou um usuário experiente",
            },
            {
              label: 'C2 - Proficiente',
              description: "Tenho proficiência em nível nativo",
            }
          ]
        },
        memberSince: {
          label: 'Membro Desde',
          recent: 'Recém-membro'
        },
        studyTime: {
          label: 'Tempo de Estudo Diário',
          placeholder: 'Selecione o tempo de estudo diário',
          options: [
            '15-30 minutos',
            '30-60 minutos',
            '1-2 horas',
            'Mais de 2 horas'
          ]
        },
        focusAreas: {
          label: 'Áreas de Foco',
          options: [
            'fala',
            'escrita',
            'leitura',
            'compreensão auditiva',
            'vocabulário',
            'gramática',
            'pronúncia'
          ],
          optionsUpperCase: [
            'Fala',
            'Escrita',
            'Leitura',
            'Compreensão auditiva',
            'Vocabulário',
            'Gramática',
            'Pronúncia'
          ]
        }
      },
      infoBox: {
        note: 'Nota:',
        description: 'As alterações no seu perfil serão refletidas em todos os seus dispositivos e ajudarão a personalizar sua experiência de aprendizado.'
      }
    },
    progressReport: {
      header: {
        subtitle: 'Acompanhe sua jornada de preparação para o PTE e identifique áreas para melhoria',
        exportButton: 'Exportar PDF'
      },
      messages: {
        insufficientDataTitle: 'Continue Praticando!',
        insufficientDataDescription: 'Pratique mais para que possamos ter dados suficientes para gerar um relatório preciso. Complete pelo menos 10 exercícios para ver sua análise detalhada de progresso.',
        startPracticing: 'Comece a Praticar'
      },
      metrics: {
        currentScore: 'Pontuação Atual',
        timeToExam: 'Tempo para o Exame',
        bestStreak: 'Melhor Sequência',
        total: 'total',
        daysRemaining: 'dias restantes',
        notSet: 'Não definido',
        target: 'Alvo',
        days: 'dias',
        best: 'Melhor'
      },
      sections: {
        skillsBreakdown: 'Detalhes das Habilidades',
        recentActivity: 'Atividade Recente',
        recommendations: 'Recomendações de Estudo',
        achievements: 'Conquistas Recentes'
      },
      skills: {
        exerciseTypes: 'Tipos de Exercício'
      },
      activity: {
        exercises: 'exercícios',
        average: 'Média'
      },
      recommendations: {
        priorityHigh: 'Prioridade Alta',
        priorityMedium: 'Prioridade Média',
        priorityLow: 'Prioridade Baixa'
      },
      fullMockData: {
        recommendations: [
          { priority: 'high', skill: 'Leitura', message: 'Concentre-se em Reordenar Parágrafos - sua área mais fraca' },
          { priority: 'medium', skill: 'Escrita', message: 'Pratique mais redações para atingir sua pontuação alvo' },
          { priority: 'low', skill: 'Fala', message: 'Mantenha a rotina de prática atual - ótimo progresso!' },
        ]
      }
    },
    audioChecker: {
      title: 'Ferramenta de Depuração de Envio de Áudio',
      description: 'Esta página ajuda a verificar se os URLs do Cloudinary estão sendo armazenados no banco de dados.',
      howToCheck: {
        title: 'Como Verificar:',
        steps: [
          'Complete um exercício de Leitura em Voz Alta ou Repetir Frase',
          'Verifique o console do navegador para logs mostrando:',
          'Use os botões na ferramenta de verificação (canto inferior direito) para buscar envios',
          'Se os URLs forem armazenados, você os verá nos resultados'
        ],
        logs: [
          'Áudio enviado para Cloudinary: [URL]',
          '[Leitura em Voz Alta] Enviando URL do Cloudinary para o backend: [URL]',
          '[Leitura em Voz Alta] Resposta do backend: ...'
        ]
      },
      manualCheck: {
        title: 'Verificação Manual do Banco de Dados:',
        description: 'Você também pode verificar diretamente em seu banco de dados MongoDB:',
        instructions: [
          'No MongoDB Compass ou sua ferramenta de banco de dados, procure por estas coleções e campos:',
          'Para envios de exercícios, consulte por userId e exerciseType (readAloud ou repeatSentence)',
          'Verifique se os documentos têm os campos audioUrl, cloudinaryUrl e audioPublicId'
        ]
      }
    },
    examPrep: {
      header: {
        title: 'Hub de Preparação para o Exame PTE',
        subtitle: 'Tudo o que você precisa para se destacar no seu exame PTE - modelos, dicas e módulos de aprendizado abrangentes'
      },
      stats: {
        templates: 'Modelos',
        examTips: 'Dicas para o Exame',
        modules: 'Módulos',
        scoreGoal: 'Meta de Pontuação'
      },
      featured: {
        badge: 'ESTRATÉGIA EM DESTAQUE',
        title: 'A Fórmula de Sucesso em 3 Passos',
        description: 'Domine nossa abordagem comprovada: 1) Aprenda o formato e os modelos, 2) Pratique com exercícios cronometrados, 3) Analise seu desempenho e adapte. Este método ajudou milhares a atingir suas pontuações alvo.',
        button: 'Iniciar Caminho de Aprendizado'
      },
      tabs: {
        templates: 'Modelos de Exercícios',
        modules: 'Módulos de Aprendizado'
      },
      templatesButton: {
        buttonView: 'Ver Modelo',
        buttonPremium: 'Modelo Premium'
      },
      tips: {
        priorityHigh: 'ALTA PRIORIDADE',
        priorityMedium: 'MÉDIA PRIORIDADE',
        priorityLow: 'BAIXA PRIORIDADE'
      },
      modules: {
        ribbon: 'EM BREVE',
        progressLabel: 'Progresso',
        buttonComingSoon: 'Em Breve',
        buttonDetails: 'Ver Detalhes'
      },
      resources: {
        title: 'Recursos Rápidos',
        freeTemplates: {
          title: 'Modelos Gratuitos',
          description: 'Baixe modelos prontos para uso para todas as seções do PTE',
          button: 'Ver Modelos'
        },
        studyTips: {
          title: 'Dicas de Estudo',
          description: 'Estratégias e técnicas de especialistas para uma preparação eficaz',
          button: 'Saiba Mais'
        },
        testFormat: {
          title: 'Guia de Formato do Teste',
          description: 'Visão geral completa da estrutura e pontuação do exame PTE',
          multipleChoice: 'Múltipla Escolha (Múltiplas)',
          multipleChoiceSingle: 'Múltipla Escolha (Única)'
        }
      },
      templates: [
        {
          title: 'Modelo de Recontar Palestra para PTE',
          category: 'fala',
          description: 'Domine a tarefa Recontar Palestra com nosso modelo comprovado e dicas de especialistas para organizar sua resposta de forma eficaz.',
          difficulty: 'difícil',
        },
        {
          title: 'Modelo de Descrever Imagem para PTE',
          category: 'fala',
          description: 'Guia completo com modelos para todos os tipos de imagens - gráficos, diagramas, mapas e mais.',
          difficulty: 'média',
        },
        {
          title: 'Modelos de Redação de Ensaio para PTE',
          category: 'escrita',
          description: 'Alcance 79+ com nossos modelos de ensaio abrangentes, cobrindo todos os tipos e tópicos de redação.',
          difficulty: 'média',
        },
        {
          title: 'Resumir Texto Escrito - Dicas e Estratégias',
          category: 'escrita',
          description: 'Aprenda a condensar passagens em frases únicas e poderosas com nossas estratégias de especialistas.',
          difficulty: 'difícil',
        },
      ],
      examTips: [
        {
          title: 'Gerenciamento de Tempo é Fundamental',
          category: 'Geral',
          content: 'Sempre controle o tempo. As tarefas de fala são estritamente cronometradas - pratique com um cronômetro para construir memória muscular.',
          priority: 'alta'
        },
        {
          title: 'Use Modelos com Sabedoria',
          category: 'Fala',
          content: 'Ter modelos ajuda, mas não soe robótico. Pratique transições naturais entre as frases do modelo.',
          priority: 'alta'
        },
        {
          title: 'Estratégia de Anotações',
          category: 'Escuta',
          content: 'Use símbolos e abreviações. Concentre-se em palavras-chave, não em frases completas. Pratique sua taquigrafia diariamente.',
          priority: 'média'
        },
        {
          title: 'Fluência em Leitura em Voz Alta',
          category: 'Fala',
          content: 'Não se apresse. Pronúncia clara > velocidade. Respire nas vírgulas e pontos finais naturalmente.',
          priority: 'alta'
        },
        {
          title: 'Contagem de Palavras do Ensaio',
          category: 'Escrita',
          content: 'Almeje 220-250 palavras. Qualidade acima de quantidade, mas não fique abaixo de 200 ou acima de 300 palavras.',
          priority: 'média'
        },
        {
          title: 'Posicionamento do Microfone',
          category: 'Fala',
          content: 'Mantenha o microfone a 2-3 cm da boca, ligeiramente para o lado para evitar sons de respiração.',
          priority: 'alta'
        }
      ],
      learningModules: [
        {
          title: 'Fundamentos do PTE',
          description: 'Introdução completa ao formato do exame PTE, sistema de pontuação e estratégias básicas',
          duration: '5 horas',
          topics: ['Formato do Exame', 'Sistema de Pontuação', 'Tipos de Questões', 'Estratégias Básicas'],
          level: 'iniciante',
        },
        {
          title: 'Programa de Maestria em Fala',
          description: 'Desenvolvimento abrangente de habilidades de fala com foco em pronúncia e fluência',
          duration: '8 horas',
          topics: ['Pronúncia', 'Fluência', 'Modelos de Fluência Oral', 'Desenvolvimento de Conteúdo'],
          level: 'intermediário',
        },
        {
          title: 'Excelência em Escrita Acadêmica',
          description: 'Técnicas avançadas de escrita para ensaios e resumos',
          duration: '6 horas',
          topics: ['Estrutura do Ensaio', 'Vocabulário Acadêmico', 'Padrões Gramaticais', 'Coerência'],
          level: 'avançado',
        },
        {
          title: 'Escuta e Anotações',
          description: 'Desenvolva habilidades de escuta ativa e métodos eficientes de anotações',
          duration: '7 horas',
          topics: ['Escuta Ativa', 'Símbolos de Anotações', 'Técnicas de Memória', 'Habilidades de Ditado'],
          level: 'intermediário',
        },
        {
          title: 'Velocidade e Compreensão de Leitura',
          description: 'Técnicas para melhorar a velocidade de leitura mantendo a compreensão',
          duration: '5 horas',
          topics: ['Passar o Olhar', 'Escaneamento', 'Pistas de Contexto', 'Gerenciamento de Tempo'],
          level: 'intermediário',
        },
        {
          title: 'Estratégias para Testes Simulados',
          description: 'Aprenda a abordar testes simulados de forma eficaz e a analisar seu desempenho',
          duration: '3 horas',
          topics: ['Psicologia do Teste', 'Alocação de Tempo', 'Análise de Desempenho', 'Melhoria de Pontuação'],
          level: 'avançado',
        }
      ]
    },
    readingWritingBlanksList: {
      header: {
        title: 'Leitura e Escrita: Preencher Lacunas',
        description: 'Complete passagens selecionando as palavras mais apropriadas em menus suspensos. Este exercício testa seu vocabulário, gramática e compreensão contextual.'
      },
      stats: {
        timePerExercise: '2-3 minutos por exercício',
        pointsPerAnswer: '1 ponto por resposta correta'
      },
      error: {
        message: 'Falha ao carregar exercícios',
        retry: 'Tentar novamente'
      },
      empty: {
        title: 'Nenhum exercício disponível',
        description: 'Volte mais tarde para novos exercícios de Leitura e Escrita: Preencher Lacunas.'
      },
      difficulty: {
        easy: 'fácil',
        medium: 'médio',
        hard: 'difícil'
      },
      labels: {
        blanks: 'lacunas'
      }
    },
    faq: {
      header: {
        subtitle: 'Encontre respostas para perguntas comuns sobre o PTEasy',
        searchPlaceholder: 'Buscar FAQs...'
      },
      placeholders: {
        searchFaqs: "Search FAQs..."
      },
      categories: [
        'Todas as Perguntas',
        'Geral',
        'Conta e Perfil',
        'Assinatura e Cobrança',
        'Exercícios de Prática',
        'Problemas Técnicos',
        'Pontuação e Resultados'
      ],
      empty: {
        title: 'Nenhuma pergunta encontrada correspondendo à sua busca.',
        description: 'Tente palavras-chave diferentes ou navegue por todas as categorias.'
      },
      cta: {
        title: 'Ainda tem perguntas?',
        description: 'Não consegue encontrar o que procura? Nossa equipe de suporte está aqui para ajudar.',
        contactSupport: 'Entrar em Contato com o Suporte',
        visitHelpCenter: 'Visitar Central de Ajuda'
      },
      faqData: [
        {
          question: 'O que é o PTEasy e como ele me ajuda a me preparar para o PTE?',
          answer: 'PTEasy é uma plataforma completa de preparação para o exame PTE, projetada especificamente para estudantes brasileiros e latino-americanos. Ele oferece aprendizado adaptativo, avaliação impulsionada por IA, caminhos de estudo personalizados e todos os 21 tipos de exercícios do PTE. Nossa plataforma ajuda você a praticar com questões semelhantes às do exame real, acompanhar seu progresso e melhorar suas pontuações através de feedback direcionado.'
        },
        {
          question: 'O PTEasy é adequado para iniciantes?',
          answer: 'Sim! O PTEasy é projetado para todos os níveis de habilidade. Nosso sistema de aprendizado adaptativo se ajusta ao seu nível atual e ajuda você a progredir no seu próprio ritmo. Oferecemos guias completos, tutoriais e um Tutor de IA para apoiar iniciantes em toda a sua jornada de aprendizado.'
        },
        {
          question: 'Como eu crio uma conta?',
          answer: 'Criar uma conta é simples: Clique no botão "Inscrever-se" na página inicial, preencha seus dados (nome, e-mail, senha), verifique seu endereço de e-mail e complete o processo de integração para definir seus objetivos de estudo e pontuações alvo.'
        },
        {
          question: 'Posso alterar meu endereço de e-mail ou senha?',
          answer: 'Sim, você pode atualizar as informações da sua conta a qualquer momento. Vá para as configurações do seu perfil no painel, clique em "Configurações da Conta" e você poderá atualizar seu e-mail, senha ou outras informações pessoais. Para alterações de e-mail, você precisará verificar o novo endereço de e-mail.'
        },
        {
          question: 'Quais planos de assinatura estão disponíveis?',
          answer: 'Oferecemos quatro níveis de assinatura: Gratuito (exercícios individuais, pontuação básica), Básico ($19/mês - 5 simulados, pontuação completa, acompanhamento de progresso), Premium ($39/mês - 20 simulados, análises avançadas, modelos personalizados) e Empresarial (preços personalizados - testes ilimitados, suporte prioritário, integrações personalizadas).'
        },
        {
          question: 'Posso cancelar minha assinatura a qualquer momento?',
          answer: 'Sim, você pode cancelar sua assinatura a qualquer momento nas configurações da sua conta. Seu acesso continuará até o final do seu período de faturamento atual. Sem perguntas, e você pode se reinscrever quando quiser.'
        },
        {
          question: 'Quais métodos de pagamento vocês aceitam?',
          answer: 'Aceitamos todos os principais cartões de crédito (Visa, MasterCard, American Express), cartões de débito e pagamentos via Stripe. Todos os pagamentos são processados com segurança, e nunca armazenamos os detalhes do seu cartão em nossos servidores.'
        },
        {
          question: 'Quantos tipos de exercícios o PTEasy oferece?',
          answer: 'PTEasy oferece todos os 21 tipos oficiais de exercícios PTE em Fala (5 tipos), Escrita (2 tipos), Leitura (5 tipos) e Audição (9 tipos). Cada tipo de exercício inclui múltiplas questões de prática com níveis de dificuldade variados.'
        },
        {
          question: 'Posso praticar tipos de exercícios específicos?',
          answer: 'Com certeza! Você pode praticar qualquer tipo de exercício individualmente na seção de Prática. Escolha a área de habilidade (Fala, Escrita, Leitura ou Audição) e então selecione o tipo de exercício específico no qual deseja focar.'
        },
        {
          question: 'Como funcionam os simulados?',
          answer: 'Os simulados replicam a experiência real do exame PTE com seções cronometradas, todos os tipos de exercícios e pontuação autêntica. Eles duram aproximadamente 2 horas e incluem as seções de Fala e Escrita (54-67 min) e Leitura (29-30 min). Recursos da seção de Audição serão adicionados em breve.'
        },
        {
          question: 'Posso pausar e retomar um simulado?',
          answer: 'Sim! Você pode pausar um simulado e retomá-lo mais tarde, dentro de 7 dias. Seu progresso é salvo automaticamente. Ao retornar, você continuará de onde parou com o tempo restante para aquela seção.'
        },
        {
          question: 'Quantos simulados posso fazer?',
          answer: 'O número de simulados depende da sua assinatura: Usuários gratuitos podem fazer exercícios de prática, mas não simulados completos; assinantes Básicos recebem 5 simulados por mês; assinantes Premium recebem 20 simulados por mês; e usuários Empresariais têm simulados ilimitados.'
        },
        {
          question: 'Quais são os requisitos de sistema?',
          answer: 'Você precisa de um navegador web moderno (Chrome, Firefox, Safari ou Edge - últimas versões), conexão de internet estável (mínimo de 2 Mbps), microfone funcionando para exercícios de fala e alto-falantes/fones de ouvido para exercícios de audição. Recomendamos usar um desktop ou laptop para a melhor experiência.'
        },
        {
          question: 'Meu microfone não está funcionando. O que devo fazer?',
          answer: 'Primeiro, certifique-se de que seu navegador tenha as permissões de microfone ativadas. Verifique as configurações do seu sistema para confirmar que o microfone está definido como padrão. Tente atualizar a página ou usar um navegador diferente. Teste seu microfone na seção "Verificação de Microfone" antes de iniciar os exercícios. Se os problemas persistirem, entre em contato com nossa equipe de suporte.'
        },
        {
          question: 'Por que minha gravação de áudio não está sendo carregada?',
          answer: 'Isso pode ser devido a problemas de conectividade com a internet, tamanhos de arquivo grandes ou restrições do navegador. Certifique-se de ter uma conexão de internet estável, tente limpar o cache do seu navegador, desative quaisquer bloqueadores de anúncios ou extensões que possam interferir e, se o problema persistir, tente usar um navegador diferente.'
        },
        {
          question: 'Como minha pontuação é calculada?',
          answer: 'O PTEasy usa um sistema de pontuação impulsionado por IA que avalia múltiplos fatores: Conteúdo (relevância e completude), Forma (requisitos de estrutura e comprimento), Gramática (precisão e complexidade), Vocabulário (amplitude e adequação), Ortografia e, para a fala: Pronúncia e Fluência. As pontuações variam de 10 a 90, correspondendo à escala oficial do PTE.'
        },
        {
          question: 'Quão precisa é a pontuação comparada ao exame PTE real?',
          answer: 'Nosso sistema de pontuação de IA é treinado em milhares de respostas reais do PTE e continuamente aprimorado. Embora nenhuma plataforma de prática possa garantir 100% de precisão, nossa pontuação geralmente se alinha em 5-10 pontos das pontuações reais do PTE, fornecendo um indicador confiável do seu nível de desempenho.'
        },
        {
          question: 'Posso ver feedback detalhado sobre minhas respostas?',
          answer: 'Sim! Após cada exercício, você recebe feedback abrangente, incluindo o detalhamento da sua pontuação, áreas de força e melhoria, erros específicos destacados, sugestões de melhoria e respostas modelo para comparação (planos Premium e Empresarial).'
        }
      ]
    },
    features: {
      hero: {
        badge: 'Recursos da Plataforma',
        title: 'Tudo o que Você Precisa para Tirar Nota Máxima no Seu Exame PTE',
        subtitle: 'Plataforma de preparação alimentada por IA com aprendizado adaptativo, pontuação em tempo real e análises abrangentes',
        stats: {
          students: {
            label: 'Alunos'
          },
          successRate: {
            label: 'Taxa de Sucesso'
          },
          support: {
            label: 'Suporte de IA'
          }
        }
      },
      section: {
        badge: 'O Que Oferecemos',
        title: 'Recursos Poderosos para o Sucesso no PTE',
        subtitle: 'Tudo o que você precisa em uma plataforma abrangente',
        cards: [
          {
            title: 'Banco de Questões Completo',
            description: 'Pratique todos os 21 tipos de questão do PTE com milhares de perguntas autênticas para praticar.',
            highlight: 'Prática Ilimitada'
          },
          {
            title: 'Mecanismo de Pontuação de IA',
            description: 'Pontuação instantânea com 95% de precisão em comparação com as pontuações oficiais do PTE.',
            highlight: 'Feedback em Tempo Real'
          },
          {
            title: 'Análises Avançadas',
            description: 'Acompanhe o progresso com insights detalhados e sugestões de melhoria personalizadas.',
            highlight: 'Aprendizado Orientado por Dados'
          },
          {
            title: 'Ferramentas de Áudio Inteligentes',
            description: 'Gravação profissional com cancelamento de ruído e análise de pronúncia.',
            highlight: 'Qualidade de Estúdio'
          },
          {
            description: 'Simulação de exame realista com pontuação completa e gerenciamento de tempo.',
            highlight: 'Pronto para o Exame'
          },
          {
            title: 'Recursos de Especialistas',
            description: 'Modelos, guias e estratégias de especialistas PTE e alunos com altas pontuações.',
            highlight: 'Métodos Comprovados'
          }
        ]
      },
      adaptive: {
        badge: 'Tecnologia Adaptativa',
        title: 'IA Que Aprende Com Você',
        description: 'Nosso algoritmo inteligente analisa seu desempenho em tempo real, criando um caminho de aprendizado personalizado que evolui à medida que você melhora.',
        features: [
          {
            title: 'Dificuldade Dinâmica',
            description: 'As perguntas se adaptam ao seu nível de habilidade em tempo real'
          },
          {
            title: 'Rastreamento de Desempenho',
            description: 'Monitore a melhoria em todas as áreas de habilidade'
          },
          {
            title: 'Recomendações Inteligentes',
            description: 'Receba sugestões de estudo personalizadas diariamente'
          }
        ]
      },
      scores: {
        predicted: 'Pontuação Prevista'
      },
      features_elements: [
        {
          title: 'Banco de Questões Extenso',
          description: 'Acesse milhares de questões precisas no estilo do exame em Speaking, Writing, Reading e Listening para prática abrangente.'
        },
        {
          title: 'Aplicativo PTEasy',
          description: 'Prepare-se em qualquer lugar, a qualquer hora com nosso aplicativo móvel dedicado. Acesse questões práticas, testes simulados e feedback instantâneo de IA em movimento'
        },
        {
          title: 'Testes Simulados com IA',
          description: 'Pratique com simulações de exames realistas, potencializadas por tecnologia avançada de IA para previsões de pontuação precisas.'
        },
        {
          title: 'Feedback Instantâneo',
          description: 'Obtenha resultados imediatos com explicações detalhadas e sugestões personalizadas de melhoria.'
        },
        {
          title: 'Análise de Desempenho',
          description: 'Painel de análise avançada para acompanhar seu progresso e identificar áreas para melhoria.'
        },
        {
          title: 'Conteúdo de Especialistas',
          description: 'Questões e materiais criados por especialistas em PTE e ex-examinadores para uma prática autêntica.'
        }
      ],
      faqs: [
        {
          question: 'O que é PTEasy?',
          answer: 'PTEasy é uma plataforma com tecnologia de IA projetada especificamente para a preparação do teste PTE Academic. Oferecemos testes práticos, simulados, feedback instantâneo e análises detalhadas para ajudar você a alcançar sua pontuação alvo.',
        },
        {
          question: 'O que está incluído no plano gratuito?',
          answer: 'O plano gratuito inclui exercícios ilimitados de Listening e Reading, 5 exercícios de Speaking e Writing por dia e feedback básico de pontuação. O feedback com IA e a prática ilimitada estão disponíveis nos planos pagos.',
        },
        {
          question: 'Existe um teste gratuito?',
          answer: 'Sim! Os planos Premium e Pro vêm com um teste gratuito de 7 dias. Não é necessário cartão de crédito.',
        },
        {
          question: 'Posso cancelar a qualquer momento?',
          answer: 'Sim, você pode cancelar sua assinatura a qualquer momento. Não são exigidos compromissos de longo prazo.',
        },
        {
          question: 'Como funciona a pontuação por IA?',
          answer: 'Nossa tecnologia avançada de IA analisa suas respostas de fala e escrita em tempo real, fornecendo pontuações e feedback com base nos critérios oficiais de pontuação do PTE Academic.',
        },
        {
          question: 'Posso praticar em dispositivos móveis?',
          answer: 'Sim! O PTEasy é totalmente responsivo e funciona em todos os dispositivos - smartphones, tablets e computadores. Também oferecemos um aplicativo móvel dedicado para uma experiência móvel otimizada.',
        }
      ]
    },
    testimonials: {
      badge: 'Histórias de Sucesso',
      title: 'O Que Nossos Alunos Dizem',
      subtitle: 'Junte-se a milhares de candidatos bem-sucedidos no PTE',
      items: [
        {
          text: '"O PTEasy me ajudou a atingir minha pontuação alvo de 79 em apenas 3 semanas! A pontuação da IA é incrivelmente precisa."',
          author: 'Maria Silva',
          score: 'Pontuação: 79 Geral'
        },
        {
          text: '"Os simulados são exatamente como o exame real. Senti-me completamente preparado no dia do teste."',
          author: 'João Santos',
          score: 'Pontuação: 85 Geral'
        },
        {
          text: '"O recurso de aprendizado adaptativo me ajudou a focar nas minhas áreas fracas. Minha pontuação de fala melhorou em 15 pontos!"',
          author: 'Ana Costa',
          score: 'Pontuação: 82 Geral'
        }
      ]
    },
    cta: {
      title: 'Comece Sua História de Sucesso no PTE',
      subtitle: 'Junte-se a milhares de candidatos bem-sucedidos que alcançaram suas pontuações desejadas com o PTEasy',
      primaryButton: 'Comece o Teste Gratuito'
    },
    helpCenter: {
      hero: {
        title: 'Como podemos te ajudar?',
        subtitle: 'Encontre respostas para suas perguntas e aprenda a aproveitar ao máximo o PTEasy',
        searchPlaceholder: 'Buscar artigos de ajuda...',
        searchButton: 'Buscar'
      },
      quickLinks: {
        viewFAQ: 'Ver FAQ',
        pteGuide: 'Guia PTE'
      },
      viewAll: 'Ver todos os artigos',
      browserByCategory: 'Navegar por Categoria',
      categories: [
        {
          title: 'Primeiros Passos',
          description: 'Aprenda o básico sobre como usar o PTEasy',
          articles: [
            'Como criar uma conta',
            'Entendendo o painel',
            'Configurando seu perfil',
            'Escolhendo seu plano de estudo'
          ],
        },
        {
          title: 'Exercícios de Prática',
          description: 'Domine todos os tipos de exercícios PTE',
          articles: [
            'Guia de exercícios de Fala',
            'Dicas para exercícios de Escrita',
            'Estratégias de Leitura',
            'Técnicas de Escuta'
          ]
        },
        {
          title: 'Simulados',
          description: 'Tudo sobre simulados',
          articles: [
            'Como iniciar um simulado',
            'Entendendo suas pontuações',
            'Formato e tempo de teste',
            'Retomando testes pausados'
          ]
        },
        {
          title: 'Assinatura e Cobrança',
          description: 'Gerencie sua assinatura',
          articles: [
            'Planos de assinatura explicados',
            'Fazendo upgrade do seu plano',
            'Métodos de pagamento',
            'Política de cancelamento'
          ]
        },
        {
          title: 'Suporte Técnico',
          description: 'Solução de problemas técnicos',
          articles: [
            'Guia de configuração de microfone',
            'Requisitos do navegador',
            'Problemas de gravação de áudio',
            'Problemas de conexão'
          ]
        },
        {
          title: 'Configurações da Conta',
          description: 'Gerencie sua conta',
          articles: [
            'Alterando sua senha',
            'Atualizando informações do perfil',
            'Preferências de notificação',
            'Configurações de privacidade de dados'
          ]
        }
      ],
      popularArticles: {
        title: 'Artigos Populares',
        items: [
          {
            title: 'Como melhorar sua pontuação de fala',
            category: 'Fala'
          },
          {
            title: 'Entendendo o sistema de pontuação PTE',
            category: 'Pontuação'
          },
          {
            title: 'Melhores práticas para redação de dissertação',
            category: 'Escrita'
          },
          {
            title: 'Configuração e teste de microfone',
            category: 'Técnico'
          },
          {
            title: 'Como usar o Tutor IA de forma eficaz',
            category: 'Recursos'
          },
          {
            title: 'Gerenciando a ansiedade do teste',
            category: 'Dicas'
          }
        ]
      },
      stillNeedHelp: {
        title: 'Ainda precisa de ajuda?',
        description: 'Nossa equipe de suporte está aqui para ajudar você a ter sucesso na sua jornada PTE. Obtenha assistência personalizada da nossa equipe de especialistas.',
        browseFAQ: 'Navegar no FAQ'
      }
    },
    practiceSkills: [
      {
        title: 'Fala',
        description: 'Melhore a pronúncia e a fluência',
        exercises: [
          { type: 'read-aloud', label: 'Leitura em Voz Alta', count: 15 },
          { type: 'repeat-sentence', label: 'Repetir Frase', count: 12 },
          { type: 'describe-image', label: 'Descrever Imagem', count: 10 },
          { type: 'retell-lecture', label: 'Recontar Palestra', count: 8 },
          { type: 'answer-short', label: 'Responder Pergunta Curta', count: 20 },
          { type: 'respond-to-situation', label: 'Responder a uma Situação', count: 10 },
          { type: 'summarize-group-discussion', label: 'Resumir Discussão em Grupo', count: 8 }
        ]
      },
      {
        title: 'Escrita',
        description: 'Aprimore as habilidades de escrita e gramática',
        exercises: [
          { type: 'summarize-written', label: 'Resumir Texto Escrito', count: 10 },
          { type: 'essay', label: 'Escrever Redação', count: 8 }
        ]
      },
      {
        title: 'Leitura',
        description: 'Desenvolva a compreensão e a velocidade',
        exercises: [
          { type: 'reading-writing-blanks', label: 'Preencher Lacunas (Dropdown)', count: 15 },
          { type: 'multiple-choice-multiple', label: 'Múltipla Escolha (Múltiplas)', count: 10 },
          { type: 'reorder-paragraph', label: 'Reordenar Parágrafos', count: 8 },
          { type: 'reading-blanks', label: 'Preencher Lacunas (Arrastar e Soltar)', count: 12 },
          { type: 'multiple-choice-single', label: 'Múltipla Escolha (Única)', count: 10 }
        ]
      },
      {
        title: 'Compreensão Auditiva',
        description: 'Aprimore a escuta e a anotação',
        exercises: [
          { type: 'summarize-spoken', label: 'Resumir Texto Falado', count: 10 },
          { type: 'listening-multiple', label: 'Múltipla Escolha (Múltiplas)', count: 8 },
          { type: 'listening-single', label: 'Múltipla Escolha (Única)', count: 10 },
          { type: 'listening-blanks', label: 'Preencher Lacunas', count: 12 },
          { type: 'highlight-correct', label: 'Destacar Resumo Correto', count: 10 },
          { type: 'select-missing', label: 'Selecionar Palavra Ausente', count: 8 },
          { type: 'highlight-incorrect', label: 'Destacar Palavras Incorretas', count: 10 },
          { type: 'write-dictation', label: 'Escrever por Ditado', count: 15 }
        ]
      }
    ],
    answerShortQuestion: {
      audioRecorder: 'Gravador de Áudio',
      listeningToQuestion: 'Ouvindo a pergunta...',
      recording: 'Gravando',
      recordingCompleted: 'Gravação concluída'
    },
    describeImageExercise: {
      instructions: {
        lookAtTheTable: 'Observe a tabela abaixo. Em 25 segundos, por favor, fale no microfone e descreva em detalhes o que a tabela está mostrando. Você terá 40 segundos para dar sua resposta.',
      },
      noImage: 'Nenhuma imagem disponível',
      preparing: 'Preparando para gravar...'
    },
    translation: {
      onboarding: {
        prompt: 'Você gostaria de usar o PTEasy em Português?',
        toggleLabel: 'Usar a interface do PTEasy em Português?',
        futureSpanishPrompt: 'Usar a interface do PTEasy em Espanhol?'
      }
    },
    mockTestIntro: {
      headerTitle: 'Teste Prático Pontuado 1',
      progressStep: '{current} de {total}',
      progressLabel: 'Introdução',
      title: 'Lista de Verificação do Teste',
      checklistItems: [
        'Use caneta e papel para fazer anotações. Um quadro branco e caneta são fornecidos para o teste ao vivo.',
        'Recomendamos um fone de ouvido, pois são usados no teste ao vivo, mas não são essenciais para este teste.',
        'Recomendamos um teclado QWERTY, pois são usados no teste ao vivo, mas não é essencial para este teste.',
        "Escolha um local tranquilo onde você não será interrompido.",
        'Garanta uma conexão Wi-Fi forte e consistente.',
      ],
    },
    microphoneCheck: {
      title: 'Verificação do Microfone',
      subtitle: 'Vamos verificar seu microfone',
      instructionsText: 'Por favor, grave-se falando por alguns segundos.',
      recordButton: 'Gravar',
      stopButton: 'Parar',
      playButton: 'Reproduzir Gravação',
      recordingStatus: 'Gravando...',
      playbackStatus: 'Reprodução',
      successMessage: 'Seu microfone parece estar funcionando!',
      noAudioMessage: 'Não conseguimos detectar nenhum áudio.',
      noAudioSuggestion: 'Por favor, verifique seu microfone e tente novamente.',
      permissionDenied: 'Permissão de microfone negada. Por favor, permita o acesso ao microfone e tente novamente.',
      noMicrophone: 'Nenhum microfone encontrado. Por favor, conecte um microfone e tente novamente.',
      accessError: 'Erro ao acessar o microfone: {error}',
      playbackError: 'Falha ao reproduzir áudio. Por favor, tente gravar novamente.',
      nextTooltip: 'Por favor, complete a verificação do microfone antes de continuar'
    },
    personalIntroduction: {
      initialPrompt: 'Você tem 1 minuto para ler a solicitação e preparar sua resposta. Você terá então 30 segundos para gravar sua resposta.',
      recordingFinished: 'Sua gravação terminou.',
      timesUp: 'Tempo esgotado. Sua gravação foi salva automaticamente.',
      responseSaved: 'Sua resposta foi salva. Agora passaremos para a primeira seção.',
      prompt: 'Leia a solicitação abaixo. Em 25 segundos, você deve responder com suas próprias palavras, da forma mais natural e clara possível. Você tem 30 segundos para gravar sua resposta.'
    },
    readAloudTransition: {
      title: 'A primeira seção é Fala.',
      duration: 'Esta seção tem um tempo total de 30-35 minutos.',
      countdown: 'Começando em {countdown}...'
    },
    readyPage: {
      title: 'Pronto?',
      subtitle: 'Você está prestes a iniciar o Teste Prático Pontuado.',
      point1: 'Este é um simulado completo do PTE Academic.',
      point2: 'O teste levará aproximadamente 2 horas para ser concluído.',
      point3: 'Uma vez iniciado, você não poderá pausar o teste.'
    },
    reTellLecture: {
      status: 'Status Atual: {phase}'
    },
    sectionOverview: {
      title: 'Visão Geral: Fala e Escrita',
      duration: 'Esta seção tem um tempo total de 54-67 minutos.',
      description: 'Você será testado em suas habilidades de fala e escrita. Esta seção inclui vários tipos de perguntas.',
      checklistItem1: 'Certifique-se de que seu microfone esteja funcionando.',
      checklistItem2: 'Fale claramente e em um ritmo natural.',
      checklistItem3: 'Gerencie seu tempo de forma eficaz.',
      startButton: 'Iniciar Seção'
    },
    speakingWritingComplete: {
      title: 'Seção de Fala e Escrita completa',
      subtitle: 'Você completou a primeira seção do teste.',
      submittingMessage: 'Enviando suas respostas...',
      successMessage: 'Suas respostas foram enviadas com sucesso.',
      waitMessage: 'Por favor, aguarde enquanto preparamos a próxima seção.',
      continueButton: 'Continuar para a próxima seção'
    },
    respondToSituation: {
      instructions: 'Você ouvirá uma descrição de uma situação. Você terá 10 segundos para se preparar, e então 40 segundos para responder. Por favor, fale claramente e aborde diretamente a situação apresentada. Sua resposta deve ser apropriada para o contexto.',
      tips: [
        'Leia a situação cuidadosamente e entenda o que está sendo perguntado',
        'Forneça uma resposta clara e apropriada para o contexto',
        'Use linguagem formal ou informal com base na situação',
        'Inclua detalhes e explicações relevantes em sua resposta',
        'Fale claramente e mantenha um ritmo constante',
        'Mantenha-se dentro do limite de tempo de 40 segundos'
      ]
    },
    testFormat: {
      title: 'Formato do Teste',
      subtitle: 'Este teste prático pontuado tem o mesmo formato do teste PTE Academic real:',
      speakingWriting: 'Fala e Escrita',
      speakingWritingDuration: '54-67 Minutos',
      readingDuration: '29-30 Minutos',
      listeningDuration: '30-43 Minutos'
    },
    pteGuide: {
      hero: {
        title: 'Guia Completo PTE Academic 2025',
        subtitle: 'Tudo o que você precisa saber sobre formato do teste, pontuação e estratégias'
      },
      sidebar: {
        navTitle: 'Navegação Rápida',
        navLinks: {
          overview: 'Visão Geral do Teste',
          skills: 'Habilidades Testadas',
          scoring: 'Sistema de Pontuação',
          newQuestions: 'Novas Perguntas 2025',
          strategies: 'Estratégias de Teste',
          preparation: 'Dicas de Preparação'
        },
        factsTitle: 'Fatos Chave',
        duration: 'Duração:',
        durationValue: '2 horas e 15 minutos',
        scoreValidity: 'Validade da Pontuação:',
        scoreValidityValue: '2 anos',
        acceptedBy: 'Aceito Por:',
        acceptedByValue: 'Mais de 3.000 instituições em todo o mundo',
        testFee: 'Taxa do Teste:',
        testFeeValue: 'Varia por localidade'
      },
      overview: {
        title: 'Visão Geral do Teste PTE Academic',
        description: 'O Pearson Test of English (PTE) Academic é um teste de inglês baseado em computador para falantes não nativos de inglês que desejam estudar no exterior. Ele testa Leitura, Escrita, Compreensão Auditiva e Fala.',
        point1: 'Totalmente baseado em computador, incluindo a seção de fala.',
        point2: 'Usa pontuação por IA para resultados imparciais e consistentes.',
        point3: 'Os resultados geralmente estão disponíveis em 48 horas.',
        point4: 'Foca no inglês acadêmico \'da vida real\'.'
      },
      format: {
        title: 'Detalhamento do Formato do Teste',
        speakingWritingTitle: 'Parte 1: Fala e Escrita',
        speakingWritingDuration: '(54-67 minutos)',
        speakingWritingDescription: 'Esta seção testa seu inglês falado e sua capacidade de escrever inglês acadêmico. Você será solicitado a ler em voz alta, repetir frases, descrever imagens, recontar palestras, responder a perguntas curtas, resumir textos e escrever uma redação.',
        readingTitle: 'Parte 2: Leitura',
        readingDuration: '(29-30 minutos)',
        readingDescription: 'Esta seção avalia sua capacidade de ler e compreender textos acadêmicos. Os tipos de perguntas incluem múltipla escolha, reordenar parágrafos e preencher lacunas.',
        listeningTitle: 'Parte 3: Compreensão Auditiva',
        listeningDuration: '(30-43 minutos)',
        listeningDescription: 'Esta seção testa sua capacidade de compreender o inglês falado em um contexto acadêmico. As tarefas incluem resumir texto falado, perguntas de múltipla escolha, preencher lacunas e escrever por ditado.'
      },
      newQuestions: {
        title: 'Novos Tipos de Perguntas 2025',
        intro: 'A partir de agosto de 2025, dois novos tipos de perguntas foram introduzidos para melhor refletir cenários acadêmicos:',
        summarizeDiscussionTitle: 'Resumir Discussão em Grupo',
        summarizeDiscussionDescription: 'Você ouvirá uma breve discussão entre vários oradores (por exemplo, um grupo de tutoria de estudantes) e então escreverá um resumo de 50-70 palavras.',
        respondSituationTitle: 'Responder a uma Situação',
        respondSituationDescription: 'Você será apresentado a uma breve descrição de uma situação universitária ou acadêmica e, em seguida, terá 40 segundos para gravar sua resposta falada.'
      },
      preparation: {
        title: 'Sua Linha do Tempo de Preparação para o PTE',
        foundation: 'Construção da Fundação',
        foundationTimeline: '8-12 semanas',
        foundationDescription: 'Faça um teste de diagnóstico, identifique áreas fracas e comece com vocabulário e gramática básicos.',
        skillDevelopment: 'Desenvolvimento de Habilidades',
        skillDevelopmentTimeline: '6-8 semanas',
        skillDevelopmentDescription: 'Concentre-se em habilidades individuais, pratique tipos de perguntas específicas e construa estratégias de realização de testes.',
        practiceTests: 'Testes Práticos',
        practiceTestsTimeline: '4-6 semanas',
        practiceTestsDescription: 'Faça simulados regularmente, analise erros e ajuste sua abordagem.',
        finalPrep: 'Preparação Final',
        finalPrepTimeline: '2-4 semanas',
        finalPrepDescription: 'Revise áreas fracas, pratique o tempo do teste e certifique-se de estar familiarizado com o formato do teste.'
      },
      cta: {
        title: 'Pronto para iniciar sua preparação para o PTE?',
        subtitle: 'Junte-se a milhares de estudantes que atingiram suas pontuações alvo com nossa plataforma de prática abrangente'
      }
    },
    freeTemplates: {
      hero: {
        title: 'Modelos de Resposta PTE Gratuitos',
        subtitle: 'Modelos e estruturas de resposta comprovados para estruturar suas respostas para pontuações máximas'
      },
      describeImage: {
        tag2: 'Gráficos e Tabelas',
        tag3: 'Alta Pontuação',
        description: 'Modelo perfeito para descrever gráficos, tabelas, imagens e diagramas com abordagem estruturada.'
      },
      reTellLecture: {
        title: 'Modelo de Recontar Palestra',
        tag2: 'Palestra em Áudio',
        tag3: 'Pontos Chave',
        description: 'Domine a estrutura para recontar palestras, incluindo pontos chave e conclusões.'
      },
      summarizeWrittenText: {
        tag2: 'Resumo de Texto',
        tag3: 'Uma Frase',
        description: 'Domine a arte de condensar textos complexos em uma única frase de resumo poderosa.'
      },
      cta: {
        title: 'Quer mais modelos?',
        subtitle: 'Obtenha acesso à nossa biblioteca completa de modelos com o PTEasy Premium'
      },
      buttons: {
        downloadPdf: 'Baixar PDF'
      }
    },
    studyTips: {
      hero: {
        title: 'Dicas e Estratégias de Estudo PTE',
        subtitle: 'Conselhos de especialistas e técnicas comprovadas para maximizar a eficiência de sua preparação para o PTE'
      },
      tips: {
        schedule: {
          title: 'Crie um Cronograma de Estudos',
          description: 'Dedique de 1 a 3 horas diárias para a preparação do PTE. Concentre-se nas suas fraquezas e dedique mais tempo praticando as áreas onde você mais precisa melhorar.'
        },
        highScoring: {
          title: 'Concentre-se em Tarefas de Alta Pontuação',
          description: 'Priorize tarefas que contribuem para várias habilidades e têm mais peso na pontuação.',
          item1: 'Leitura em Voz Alta (Fala + Leitura)',
          item2: 'Repetir Frase (Fala + Compreensão Auditiva)',
          item3: 'Resumir Texto Escrito (Escrita + Leitura)'
        },
        speaking: {
          title: 'Melhore a Fluência na Fala',
          description: 'A prática regular com técnicas adequadas pode aumentar significativamente suas pontuações de fala.',
          item1: 'Grave-se diariamente',
          item2: 'Pratique a técnica de shadowing',
          item3: 'Mantenha fluência e fale em ritmo rápido'
        },
        writing: {
          title: 'Domine a Escrita de Redações',
          description: 'Uma redação bem estruturada com gramática adequada pode garantir altas pontuações em escrita.',
          item1: 'Use modelos de redação',
          item2: 'Pratique velocidade de digitação',
          item3: 'Aprenda frases de transição'
        },
        listening: {
          title: 'Melhore as Habilidades de Compreensão Auditiva',
          description: 'A escuta ativa e a tomada de notas são cruciais para obter boas pontuações na seção de compreensão auditiva.',
          item1: 'Assista palestras acadêmicas',
          item2: 'Pratique atalhos para tomar notas',
          item3: 'Concentre-se em palavras-chave'
        },
        reading: {
          title: 'Compreensão de Leitura',
          description: 'A leitura dinâmica com compreensão é essencial para o gerenciamento do tempo na seção de leitura.',
          item1: 'Pratique técnicas de leitura rápida',
          item2: 'Construa vocabulário acadêmico',
          item3: 'Leia diversos tópicos diariamente'
        }
      },
      weeklyPlan: {
        title: 'Plano de Estudo de 4 Semanas',
        week1: 'Semana 1: Fundação',
        week1Desc: 'Entenda o formato do teste, faça o teste de diagnóstico, identifique áreas fracas',
        week2: 'Semana 2: Desenvolvimento de Habilidades',
        week2Desc: 'Concentre-se em tipos de perguntas individuais, aprenda modelos e estratégias',
        week3: 'Semana 3: Prática',
        week3Desc: 'Complete exercícios cronometrados, faça simulados, analise erros',
        week4: 'Semana 4: Polimento',
        week4Desc: 'Simulados finais, revise áreas fracas, prática de gerenciamento de tempo'
      },
      cta: {
        title: 'Pronto para iniciar sua jornada no PTE?',
        subtitle: 'Acesse materiais de prática abrangentes e acompanhe seu progresso',
        button: 'Comece a Praticar Agora'
      }
    },
    testFormatDetail: {
      hero: {
        title: 'Formato do Teste PTE Academic',
        subtitle: 'Análise detalhada de todos os 20 tipos de questões do PTE Academic'
      },
      speakingWriting: {
        duration: '77-93 minutos',
        personalIntroduction: {
          title: 'Introdução Pessoal',
          duration: '30 segundos',
          scoring: 'Não pontuado',
          description: 'Apresente-se brevemente. Isso é enviado às instituições, mas não é pontuado.'
        },
        readAloud: {
          duration: '30-40 segundos',
          questions: '6-7 questões',
          description: 'Leia um texto curto em voz alta.'
        },
        repeatSentence: {
          duration: 'N/A',
          questions: '10-12 questões',
          description: 'Repita uma frase que você ouvir.'
        },
        describeImage: {
          duration: '25 segundos de preparação',
          questions: '3-4 questões',
          description: 'Descreva uma imagem em detalhes.'
        },
        reTellLecture: {
          duration: '10 segundos de preparação',
          questions: '1-2 questões',
          description: 'Ouça uma palestra e reconte-a com suas próprias palavras.'
        },
        answerShortQuestion: {
          questions: '5-6 questões',
          description: 'Responda a uma pergunta simples com uma ou poucas palavras.'
        },
        summarizeWrittenText: {
          duration: '10 minutos',
          description: 'Leia uma passagem e escreva um resumo de uma frase.'
        },
        essay: {
          duration: '20 minutos',
          description: 'Escreva uma redação argumentativa de 200-300 palavras.'
        }
      },
      reading: {
        duration: '29-30 minutos',
        readingWritingFillInTheBlanks: {
          description: 'Selecione a palavra correta em uma lista suspensa para preencher as lacunas.'
        },
        multipleChoiceMultipleAnswers: {
          description: 'Selecione mais de uma resposta correta.'
        },
        reorderParagraphs: {
          questions: '2-3 questões',
          description: 'Arraste e solte parágrafos na ordem correta.'
        },
        readingFillInTheBlanks: {
          questions: '4-5 questões',
          description: 'Arraste palavras de uma caixa para preencher as lacunas.'
        },
        multipleChoiceSingleAnswer: {
          description: 'Selecione apenas uma resposta correta.'
        }
      },
      listening: {
        duration: '30-43 minutos',
        summarizeSpokenText: {
          description: 'Ouça uma gravação e escreva um resumo de 50-70 palavras.'
        },
        multipleChoiceMultipleAnswersListening: {
          description: 'Ouça e selecione mais de uma resposta correta.'
        },
        fillInTheBlanksListening: {
          description: 'Digite a palavra que falta em cada lacuna enquanto ouve.'
        },
        multipleChoiceSingleAnswerListening: {
          description: 'Escolha uma resposta correta com base no áudio.'
        },
        selectMissingWord: {
          description: 'Selecione a palavra que completa o áudio no bipe.'
        },
        highlightIncorrectWords: {
          description: 'Clique nas palavras que diferem do que o orador diz.'
        },
        writeFromDictation: {
          description: 'Digite a frase exatamente como a ouviu.'
        }
      },
      cta: {
        title: 'Domine todos os tipos de questões',
        subtitle: 'Pratique com perguntas reais do PTE e receba feedback instantâneo da IA'
      }
    },
    checkoutPage: {
      title: 'Finalizar Compra',
      subtitle: 'Complete sua compra',
      upgradingTo: 'Você está atualizando para o',
      billed: 'Faturado',
      plan: 'Plano',
      price: 'Preço',
      paymentInfo: 'Informações de Pagamento',
      cardholderName: 'Nome do Titular do Cartão',
      cardNumber: 'Número do Cartão',
      expiryDate: 'Data de Expiração',
      cvc: 'CVC',
      agreement: 'Ao confirmar sua assinatura, você concorda com nossos Termos de Serviço e Política de Privacidade.',
      securityMessage: 'Suas informações de pagamento são criptografadas e seguras.',
      placeholders: {
        expiry: 'MM/AA',
        cvc: '123'
      }
    },
    pricingPage: {
      hero: {
        title: 'Atualize sua preparação para o PTE',
        subtitle: 'Libere todo o seu potencial com o PTEasy Premium. Obtenha prática ilimitada, feedback de IA e estratégias lideradas por especialistas.'
      },
      then: 'Então',
      monthAfterTrial: 'mês após o teste',
      tabs: {
        monthly: 'Mensal',
        yearly: 'Anual',
        save: 'Economize 25%'
      },
      plans: {
        monthly: {
          price: '$19',
          period: '/mês',
          billing: 'Faturado mensalmente',
          features: [
            'Acesso ilimitado a todos os exercícios',
            'Pontuação e feedback avançados de IA',
            'Planos de estudo personalizados',
            'Simulados completos',
            'Suporte prioritário'
          ],
          button: 'Iniciar Teste Gratuito de 7 dias'
        },
        yearly: {
          price: '$14.25',
          billing: 'Faturado anualmente ($171)',
          features: [
            'Tudo no Plano Mensal, mais:',
            'Acesso exclusivo a aulas ao vivo',
            'Rastreamento de progresso avançado',
            'Sessão de coaching individual'
          ],
          popular: 'Primeiro Mês Grátis'
        }
      },
      faq: {
        items: [
          {
            question: 'Posso cancelar minha assinatura a qualquer momento?',
            answer: 'Sim, você pode cancelar sua assinatura a qualquer momento nas configurações da sua conta. Seu acesso continuará até o final do período de faturamento atual.'
          },
          {
            question: 'Quais métodos de pagamento vocês aceitam?',
            answer: 'Aceitamos todos os principais cartões de crédito, incluindo Visa, Mastercard e American Express. Todos os pagamentos são processados com segurança.'
          },
          {
            question: 'Existe um teste gratuito disponível?',
            answer: 'Sim, oferecemos um teste gratuito de 7 dias para nossos planos Mensal e Anual. Você não será cobrado até o final do período de teste.'
          },
          {
            question: 'O que acontece após o teste gratuito?',
            answer: 'Após o teste de 7 dias, sua assinatura escolhida começará automaticamente. Você pode cancelar a qualquer momento antes do término do teste para evitar cobranças.'
          },
          {
            question: 'Posso mudar entre os planos?',
            answer: 'Você pode fazer upgrade do plano Mensal para o Anual a qualquer momento. Os downgrades entrarão em vigor no final do seu ciclo de faturamento atual.'
          }
        ]
      }
    },
    successPage: {
      title: 'Bem-vindo ao PTEasy Premium',
      subtitle: 'Você desbloqueou com sucesso todos os recursos premium.',
      whatsNext: 'Qual o próximo passo?',
      nextSteps: [
        'Faça um teste de diagnóstico para avaliar seu nível atual',
        'Defina seu cronograma e metas de estudo',
        'Explore exercícios premium com feedback de IA',
        'Acompanhe seu progresso com análises avançadas'
      ],
      goToDashboard: 'Ir para o Painel',
      needHelp: 'Precisa de ajuda?'
    },
    trialStarted: {
      title: 'Seu Teste Premium de 7 Dias Começou!',
      loading: 'Carregando informações do seu teste...',
      trialEndDate: 'Seu teste termina em',
      onboardingPending: 'Complete sua integração para personalizar seu plano de estudo.',
      goToOnboarding: 'Ir para Integração'
    },
    termsOfService: {
      hero: {
        subtitle: 'Por favor, leia estes termos cuidadosamente antes de usar o PTEasy',
        effectiveDate: 'Data de Vigência: 15 de janeiro de 2025'
      },
      sections: {
        introduction: {
          title: '1. Introdução',
          text: 'Bem-vindo ao PTEasy (\'nós\', \'nos\', ou \'nosso\'). Estes Termos de Serviço (\'Termos\') regem o uso do nosso site, aplicativos e serviços (coletivamente, o \'Serviço\'). Ao acessar ou usar nosso Serviço, você concorda em ficar vinculado a estes Termos.'
        },
        acceptance: {
          title: '2. Aceitação dos Termos',
          text: 'Ao criar uma conta e usar o Serviço, você confirma que tem pelo menos 18 anos de idade e é legalmente capaz de celebrar um contrato vinculativo. Você concorda em cumprir estes Termos e todas as leis locais, estaduais, nacionais e internacionais aplicáveis.'
        },
        userAccounts: {
          title: '3. Contas de Usuário',
          text: 'Para acessar a maioria dos recursos, você deve se registrar para uma conta. Você é responsável por manter a confidencialidade das informações da sua conta e por todas as atividades que ocorrem sob sua conta. Você deve nos notificar imediatamente sobre qualquer uso não autorizado.'
        },
        userConduct: {
          title: '4. Conduta do Usuário',
          text: 'Você concorda em não usar o Serviço para: (a) carregar ou distribuir qualquer conteúdo que seja ilegal, prejudicial ou de outra forma questionável; (b) se passar por qualquer pessoa ou entidade; (c) se envolver em qualquer atividade que interfira ou interrompa o Serviço.'
        },
        serviceDescription: {
          title: '5. Descrição do Serviço',
          text: 'PTEasy oferece uma plataforma para preparação para o teste PTE Academic, incluindo exercícios práticos, simulados e pontuação alimentada por IA. As pontuações da IA são para fins de prática e não são pontuações oficiais do PTE. Elas são destinadas como um guia para ajudar você a se preparar.'
        },
        intellectualProperty: {
          title: '6. Propriedade Intelectual',
          text: 'Todo o conteúdo e materiais do Serviço, incluindo texto, gráficos, logotipos e software, são propriedade exclusiva da PTEasy ou de seus licenciadores e são protegidos por direitos autorais e outras leis de propriedade intelectual.'
        },
        subscription: {
          title: '7. Assinatura e Pagamento',
          text: 'Oferecemos planos de assinatura gratuitos e pagos. Ao selecionar um plano pago, você concorda em pagar as taxas especificadas. As taxas são cobradas antecipadamente de forma recorrente. Você pode cancelar sua assinatura a qualquer momento, mas nenhum reembolso será fornecido para o ciclo de faturamento atual.'
        },
        termination: {
          title: '8. Rescisão',
          text: 'Podemos rescindir ou suspender sua conta a nosso exclusivo critério, sem aviso prévio, por conduta que viole estes Termos ou seja prejudicial a outros usuários ou a nós.'
        },
        disclaimer: {
          title: '9. Isenção de Garantias',
          text: 'O Serviço é fornecido \'como está\' e \'conforme disponível\'. Não oferecemos garantias, expressas ou implícitas, de que o Serviço será ininterrupto, livre de erros ou seguro.'
        },
        limitationOfLiability: {
          title: '10. Limitação de Responsabilidade',
          text: 'Em nenhuma circunstância o PTEasy será responsável por quaisquer danos indiretos, incidentais, especiais ou consequenciais decorrentes ou relacionados ao seu uso do Serviço.'
        },
        indemnification: {
          title: '11. Indenização',
          text: 'Você concorda em indenizar e isentar o PTEasy e seus funcionários de quaisquer reivindicações, danos ou despesas decorrentes do seu uso do Serviço ou da sua violação destes Termos.'
        },
        governingLaw: {
          title: '12. Lei Aplicável',
          text: 'Estes Termos serão regidos e interpretados de acordo com as leis da jurisdição em que nossa empresa está sediada, sem considerar seus princípios de conflito de leis.'
        },
        disputeResolution: {
          title: '13. Resolução de Disputas',
          text: 'Quaisquer disputas decorrentes destes Termos serão resolvidas por meio de arbitragem vinculativa, e não em tribunal, exceto que você pode apresentar reclamações em tribunal de pequenas causas se suas reclamações se qualificarem.'
        },
        changesToTerms: {
          title: '14. Alterações aos Termos',
          text: 'Reservamo-nos o direito de modificar estes Termos a qualquer momento. Se fizermos alterações materiais, iremos notificá-lo por e-mail ou publicando um aviso no Serviço. Seu uso contínuo após as alterações constitui aceitação dos novos Termos.'
        }
      },
      agreementNotice: {
        title: 'Ao usar o PTEasy, você reconhece que leu, compreendeu e concorda em ficar vinculado a estes Termos de Serviço.'
      },
      relatedLinks: {
        title: 'Documentos Relacionados'
      }
    },
    testDescribeImage: {
      title: 'Exercício de Teste Descrever Imagem',
      description: 'Esta é uma página de teste para o componente de exercício Descrever Imagem.'
    },
    testHighlightIncorrectPage: {
      exerciseId: 'ID do Exercício:',
      title: 'Exercício de Teste Destacar Palavras Incorretas',
      descriptionSection: {
        title: 'Descrição do Exercício',
        paragraphs: [
          'O exercício Destacar Palavras Incorretas é uma tarefa de compreensão auditiva do PTE onde:'
        ],
        list: [
          'Você ouve uma gravação de áudio',
          'Você lê uma transcrição que contém algumas palavras incorretas',
          'Você clica nas palavras que diferem do que foi falado',
          'Pontuação PTE: +1 para cada identificação correta, -1 para falsos positivos'
        ]
      },
      testExercises: {
        title: 'Exercícios de Teste',
        description: 'Clique em qualquer exercício abaixo para testar a implementação:',
        buttonLabel: 'Testar Exercício',
        exerciseId: 'ID do Exercício'
      },
      notes: {
        title: 'Notas de Implementação:',
        list: [
          'Componente: src/components/exercises/listening/HighlightIncorrectWords.tsx',
          'Rota da Página: src/app/(exercises)/exercises/highlight-incorrect/[id]/page.tsx',
          'Endpoint da API: /api/highlightIncorrectWords',
          'Tipo de Exercício: highlight-incorrect'
        ]
      },
      backButton: 'Voltar à Página Inicial'
    },
    testReadingWritingBlanksPage: {
      title: 'Exercício de Teste Leitura e Escrita: Preencher Lacunas',
      descriptionSection: {
        paragraphs: [
          'Esta página carrega o componente do exercício Leitura e Escrita: Preencher Lacunas para fins de teste.'
        ],
        list: [
          'Exibe o componente ReadingWritingBlanks',
          'Usa um ID de teste para o exercício',
          'Mostra um spinner de carregamento enquanto o exercício está sendo carregado'
        ]
      },
      notes: {
        list: [
          'Componente: src/components/exercises/reading/ReadingWritingBlanks.tsx',
          'Rota da Página: src/app/(exercises)/exercises/test-reading-writing-blanks/page.tsx',
          'ID do Exercício usado para teste: rwb-001'
        ]
      }
    },
    testRetellLecturePage: {
      title: 'Exercício de Teste Recontar Palestra',
      description: 'Testando o componente Recontar Palestra com dados simulados',
      notes: {
        list: [
          'Componente: src/components/exercises/speaking/RetellLectureExercise.tsx',
          'Rota da Página: src/app/(exercises)/exercises/test-retell-lecture/page.tsx',
          'Usa dados simulados: src/data/mock/retell-lecture-mock.ts',
          'ID do Exercício usado para teste: test-exercise-id'
        ]
      }
    },
    unauthorizedPage: {
      errorCode: '403',
      title: 'Acesso Negado',
      description: 'Você não tem permissão para acessar esta página. Isso pode ser porque:',
      reasons: {
        loginRequired: 'Você precisa estar logado para acessar esta página',
        noPermissions: 'Sua conta não tem as permissões necessárias',
        noSubscription: 'Seu nível de assinatura não inclui este recurso'
      },
      actions: {
        goBack: 'Voltar',
        viewPlans: 'Ver Planos de Assinatura'
      },
      help: {
        message: 'Ainda está com problemas?',
        linkText: 'Verifique nosso FAQ'
      }
    },
    adminDashboard: {
      title: 'Painel de Administração',
      cards: {
        totalUsers: {
          title: 'Total de Usuários',
          active: '{0} ativos'
        },
        exercises: {
          title: 'Exercícios',
          completionRate: '{0} de conclusão'
        },
        revenue: {
          title: 'Receita Mensal',
          growth: '{0} de crescimento'
        },
        systemHealth: {
          title: 'Saúde do Sistema',
          uptime: 'tempo de atividade',
          responseTime: 'médio'
        }
      },
      recentActivity: {
        placeholder: 'O feed de atividades será exibido aqui'
      },
      quickActions: {
        title: 'Ações Rápidas',
        manageUsers: 'Gerenciar Usuários',
        createExercise: 'Criar Exercício',
        viewReports: 'Ver Relatórios',
        systemSettings: 'Configurações do Sistema'
      }
    },
    forgotPasswordForm: {
      header: {
        title: 'Esqueceu a Senha?',
        subtitle: 'Digite seu e-mail para receber as instruções de redefinição'
      },
      form: {
        emailPlaceholder: 'Digite seu e-mail',
        submitButton: {
          default: 'Enviar E-mail de Redefinição'
        }
      },
      messages: {
        success: 'As instruções de redefinição de senha foram enviadas para o seu e-mail. Por favor, verifique sua caixa de entrada.',
        error: 'Falha ao enviar e-mail de redefinição'
      },
      prompt: {
        text: 'Lembra sua senha?',
        link: 'Fazer login'
      }
    },
    resetPasswordForm: {
      header: {
        title: 'Redefinir Sua Senha',
        subtitle: 'Digite sua nova senha abaixo'
      },
      form: {
        newPassword: {
          placeholder: 'Pelo menos 8 caracteres'
        },
        confirmPassword: {
          label: 'Confirmar Senha',
          placeholder: 'Redigite sua senha'
        },
        submitButton: {
          default: 'Redefinir Senha',
          loading: 'Redefinindo...'
        }
      },
      messages: {
        success: 'Senha redefinida com sucesso! Redirecionando para o login...',
        errorShort: 'A senha deve ter pelo menos 8 caracteres',
        errorFailed: 'Falha ao redefinir a senha'
      }
    },
    audioSubmissionChecker: {
      title: 'Verificador de Envio de Áudio',
      buttons: {
        fetchAll: 'Buscar Todos os Envios',
        latestReadAloud: 'Mais Recente Leitura em Voz Alta',
        latestRepeat: 'Mais Recente Repetir'
      },
      messages: {
        errorFetch: 'Não foi possível buscar os envios. Verifique o console para detalhes.',
        errorLatest: 'Não foi possível buscar o envio {0} mais recente.'
      },
      results: {
        title: 'Envios Encontrados:',
        type: 'Tipo:',
        date: 'Data:',
        url: 'URL do Cloudinary:',
        view: 'Ver/Reproduzir Áudio',
        notStored: 'Não armazenado',
        score: 'Pontuação:'
      },
      notes: {
        console: 'Verifique o console do navegador para logs detalhados',
        backend: 'O backend pode precisar de endpoints para buscar envios'
      }
    },
    highlightCorrectSummaryExercise: {
      audioSectionTitle: 'Áudio',
      selectSummaryTitle: 'Selecione o Resumo Correto',
      noSelection: 'Nenhuma seleção',
      oneSelection: '1 resumo selecionado',
      chooseParagraphInstruction: 'Escolha o parágrafo que melhor resume a gravação:',
      resetSelection: 'Redefinir Seleção',
      submitAnswer: 'Enviar Resposta',
      submitting: 'Enviando...',
      alertSelectSummary: 'Por favor, selecione um resumo antes de enviar.',
      correctSummaryBadge: 'Resumo Correto',
      showTranscript: 'Mostrar Transcrição',
      hideTranscript: 'Ocultar Transcrição',
      transcriptTitle: 'Transcrição do Áudio:',
      aiScoringTitle: 'Pontuação por IA',
      aiScoringEvaluating: 'Avaliando sua seleção...',
      aiScoringSteps: {
        analyzing: 'Analisando',
        comparing: 'Comparando'
      },
      feedback: {
        correct: 'Correto!',
        incorrect: 'Incorreto',
        reviewTip: 'Revise o resumo correto para entender os pontos-chave que deveriam ser capturados.'
      },
      instructionsDefault: 'Ouça a gravação e selecione o parágrafo que melhor resume o áudio.',
      tips: [
        'Ouça o áudio cuidadosamente e entenda a ideia principal',
        'Você pode reproduzir o áudio quantas vezes forem necessárias',
        'Leia todos os resumos antes de fazer sua seleção',
        'Selecione o parágrafo que melhor capta os pontos-chave',
        'Procure o resumo que inclui todas as ideias principais',
        'Pontuação PTE: 1 ponto para seleção correta, 0 para incorreta'
      ],
      description: 'Ouça e selecione o parágrafo que melhor resume a gravação.'
    },
    highlightIncorrectWordsExercise: {
      transcriptSection: {
        title: 'Transcrição',
        stats: {
          wordsSelected: '{{count}} palavra(s) selecionada(s)',
          correctCount: '{{correct}}/{{total}} corretas'
        },
        instructions: 'Clique nas palavras que diferem do que você ouve no áudio'
      },
      feedback: {
        correct: 'Corretamente identificado',
        missed: 'Palavras incorretas perdidas',
        falsePositive: 'Falsos positivos',
        reviewTip: 'Revise as palavras destacadas para entender as diferenças entre o áudio e a transcrição.',
        showTranscript: 'Mostrar Transcrição Correta',
        hideTranscript: 'Ocultar Transcrição Correta',
        correctTranscriptTitle: 'Transcrição de Áudio Correta:'
      },
      aiScoring: {
        evaluating: 'Avaliando suas seleções...',
        steps: {
          accuracy: 'Precisão',
          comprehension: 'Compreensão'
        }
      },
      alerts: {
        selectWord: 'Por favor, selecione pelo menos uma palavra antes de enviar.'
      },
      errors: {
        notFound: 'Exercício não encontrado'
      }
    },
    listeningMultipleChoice: {
      instructions: [
        'Selecione todas as respostas corretas com base na gravação.'
      ],
      tips: [
        [
          'Ouça o áudio cuidadosamente e faça anotações mentais',
          'Selecione todas as respostas mencionadas no áudio',
          'Preste atenção aos detalhes específicos e palavras-chave',
          'Revise suas seleções antes de enviar',
          'Pontuação PTE: +1 por correto, -1 por seleção incorreta'
        ]
      ],
      question: {
        instruction: 'Selecione todas as respostas corretas',
        selectedCount: '{{count}} selecionado(s)',
        scoringHint: 'Pontuação PTE: +1 por correto, -1 por incorreto'
      },
      buttons: {
        reset: 'Redefinir Respostas',
        submit: 'Enviar Respostas'
      },
      feedback: {
        evaluating: 'Avaliando suas respostas...'
      },
      messages: {
        selectAtLeastOne: 'Por favor, selecione pelo menos uma resposta antes de enviar.',
        dataUnavailable: 'Dados do exercício não disponíveis'
      }
    },
    listeningSingleChoice: {
      exerciseTypeLabel: 'Múltipla Escolha Única (Compreensão Auditiva)',
      instructions: 'Selecione a melhor resposta com base na gravação.',
      tips: [
        'Selecione apenas UMA resposta que melhor corresponda ao áudio',
        'Revise sua seleção antes de enviar',
        'Resposta Única: Escolha a opção mais precisa'
      ],
      question: {
        selectedCount: '1 selecionado',
        instruction: 'Selecione a melhor resposta'
      },
      buttons: {
        reset: 'Redefinir Resposta'
      },
      feedback: {
        evaluating: 'Avaliando sua resposta...'
      },
      messages: {
        selectBeforeSubmit: 'Por favor, selecione uma resposta antes de enviar.'
      }
    },
    selectMissingWord: {
      audioHint: 'O áudio termina com um bipe onde uma palavra está faltando',
      sectionTitle: 'Selecione a Palavra Ausente',
      instructionText: 'Selecione a palavra que completa a gravação:',
      scoringStepContext: 'Contexto',
      showTranscript: 'Mostrar Transcrição Completa',
      hideTranscript: 'Ocultar Transcrição Completa',
      completeTranscript: 'Transcrição Completa:',
      missingWordLabel: 'Palavra ausente:'
    },
    summarizeSpokenTextKeys: {
      timerNote: 'O cronômetro inicia quando o áudio começa a tocar',
      summarySectionTitle: 'Seu Resumo',
      summaryInstruction: 'Escreva um resumo da palestra em 50-70 palavras:',
      summaryPlaceholder: 'Comece a digitar seu resumo aqui...',
      resetButton: 'Redefinir',
      submitButton: 'Enviar Resumo',
      minWordsAlert: 'Por favor, escreva pelo menos 5 palavras.',
      maxWordsAlert: 'Por favor, mantenha seu resumo dentro de 70 palavras.',
      perfectWordCount: 'Contagem de palavras perfeita!',
      needMoreWords: 'Precisa de mais {count} palavras',
      overWordLimit: '{count} palavras acima do limite',
      wordCountLabel: '{count}/70 palavras',
      successTitleExcellent: 'Resumo Excelente!',
      successTitleGood: 'Bom Resumo!',
      contentLabel: 'Conteúdo',
      formLabel: 'Forma',
      spellingLabel: 'Ortografia',
      feedbackDefault: 'Avaliação da IA concluída',
      aiScoringText: 'Analisando seu resumo...',
      instructionsDefault: 'Você ouvirá uma palestra. Escreva um resumo para um colega de estudante que não estava presente. Você deve escrever 50-70 palavras. Você tem 10 minutos para terminar esta tarefa.',
      tips: [
        'Ouça o áudio cuidadosamente e faça anotações',
        'Concentre-se nas ideias principais e nos detalhes de apoio chave',
        'Escreva entre 50-70 palavras',
        'Verifique gramática, ortografia e pontuação',
        'Você tem 10 minutos para completar a tarefa',
        'O áudio será reproduzido automaticamente apenas uma vez'
      ]
    },
    highlightIncorrectWords: {
      scoring: {
        correctIdentification: '+1 para cada identificação correta',
        falsePositive: '-1 para falsos positivos'
      }
    },
    listeningFillInTheBlanks: {
      tips: [
        'Ouça o áudio cuidadosamente',
        'Digite as palavras que faltam nas lacunas',
        'Você pode reproduzir o áudio várias vezes',
        'Preste atenção ao contexto de cada lacuna',
        'Verifique a ortografia antes de enviar',
        'Cada palavra correta pontua 1 ponto'
      ],
      stats: {
        blanksFilled: 'lacunas preenchidas'
      },
      buttons: {
        clearAll: 'Limpar Tudo'
      },
      feedback: {
        perfect: 'Perfeito!',
        greatJob: 'Ótimo Trabalho!',
        goodAttempt: 'Boa Tentativa!',
        excellent: 'Excelente! Você preencheu todas as lacunas corretamente.',
        review: 'Bom esforço! Revise as respostas corretas acima para ver onde você pode melhorar.'
      },
      review: {
        title: 'Revise Suas Respostas:'
      },
      aiScoring: {
        checking: 'Verificando suas respostas...'
      },
      messages: {
        fillOneBlank: 'Por favor, preencha pelo menos uma lacuna antes de enviar.'
      }
    },
    writeFromDictation: {
      instructions: [
        'Você ouvirá uma frase. Digite a frase na caixa abaixo exatamente como a ouvir.'
      ],
      section: {
        writeWhatYouHear: 'Escreva o que você ouve',
        statsWords: '{{count}} palavra(s)'
      },
      textarea: {
        placeholder: 'Comece a digitar o que você ouve...'
      },
      buttons: {
        clear: 'Limpar'
      },
      alerts: {
        emptySubmission: 'Por favor, escreva o que você ouviu antes de enviar.'
      },
      feedback: {
        perfect: 'Perfeito! Você escreveu cada palavra corretamente.',
        effort: 'Bom esforço! Você acertou {{score}} de {{total}} palavras. Revise as palavras incorretas: {{incorrectWords}}',
        generic: 'Você marcou {{score}} de {{total}} palavras. Continue praticando para melhorar sua precisão!'
      },
      comparison: {
        showDetailed: 'Mostrar Comparação Detalhada',
        hideDetailed: 'Ocultar Comparação Detalhada',
        showAnswer: 'Mostrar Resposta Correta',
        hideAnswer: 'Ocultar Resposta'
      },
      aiScoring: {
        checking: 'Verificando seu ditado...',
        steps: {
          punctuation: 'Pontuação'
        }
      },
      errors: {
        fetchFail: 'Falha ao obter pontuação da IA. Por favor, tente novamente.'
      },
      input: {
        placeholder: 'Digite o que você ouve...'
      }
    },
    fillBlanksDragDrop: {
      instructions: 'Leia o texto abaixo e arraste as palavras do banco de palavras para preencher as lacunas. Você tem 2-3 minutos para completar.',
      tips: [
        'Leia a passagem inteira primeiro para entender o contexto',
        'Arraste as palavras do banco de palavras para preencher as lacunas',
        'Você pode mover palavras entre as lacunas ou de volta para o banco de palavras',
        'Preste atenção à gramática e às pistas de contexto',
        'Você tem 2-3 minutos para completar'
      ]
    },
    readingWritingBlanks: {
      instructions: 'Abaixo está um texto com lacunas. Selecione a palavra mais apropriada no menu suspenso para cada lacuna. Você tem 2-3 minutos para completar.',
      tips: [
        'Selecione a palavra correta no menu suspenso para cada lacuna',
        'Considere a parte do discurso necessária para cada lacuna',
        'Cada resposta correta pontua 1 ponto'
      ]
    },
    summarizeGroupDiscussion: {
      instructions: 'Ouça a discussão em grupo e resuma os pontos-chave com suas próprias palavras. Você tem 10 segundos para se preparar e 2 minutos para falar.',
      tips: [
        'Ouça atentamente para identificar os pontos principais e os argumentos chave de cada orador',
        'Faça anotações sobre as diferentes perspectivas apresentadas na discussão',
        'Estruture seu resumo com uma introdução, pontos principais e conclusão',
        'Inclua os argumentos chave e quaisquer consensos ou desacordos',
        'Fale claramente e organize seus pensamentos durante o tempo de preparação',
        'Procure cobrir todos os pontos principais dentro do limite de tempo de 2 minutos'
      ]
    },
    browserCheck: {
      title: 'Verificação do navegador',
      compatibleMessage: 'Seu navegador é totalmente compatível',
      compatibilityWarning: 'Aviso de compatibilidade do navegador',
      recommendedBrowsers: 'Navegadores recomendados para a melhor experiência:',
      next: 'Próximo →'
    },
    readyToStart: {
      readyToStartTheTest: 'Pronto para iniciar o teste?',
      instructions: 'Iniciar o teste acionará o cronômetro. Você terá aproximadamente 2 horas.',
      youCanPauseTheTest: 'Você pode pausar o teste a qualquer momento e retomar usando o botão "Salvar/Sair"',
      tips: [
        'Certifique-se de ter tudo pronto antes de começar:',
        'Ambiente tranquilo',
        'Conexão estável com a internet',
        'Microfone testado e funcionando',
        'Caneta e papel para anotações'
      ],
      startTest: 'Iniciar Teste →'
    },
    DashboardPage: {
      AuthGuard: {
        readyToPractice: 'Pronto para praticar para o seu exame PTE? Vamos melhorar suas habilidades hoje.',
        current: 'Atual:',
        target: 'Alvo:',
        StatsCard: {
          label: {
            todaySPractice: "Prática de Hoje",
            weeklyGoal: "Meta Semanal",
            currentStreak: "Sequência Atual",
            daysToExam: "Dias para o Exame"
          }
        }
      }
    },
    ProgressReportPage: {
      AuthGuard: {
        value: {
          week: 'semana',
          month: 'mês',
          all: 'tudo'
        },
        currentScore: 'Pontuação Atual:',
        exercises: "exercícios"
      }
    },
    ChangePasswordPage: {
      useAUnique: 'Use uma senha única que você não usa em outros sites',
      AuthGuard: {
        placeholder: {
          enterYourCurrent: "Digite sua senha atual",
          enterYourNew: "Digite sua nova senha",
          confirmYourNew: "Confirme sua nova senha"
        }
      }
    },
    practiceHistoryPage: {
      AuthGuard: {
        placeholder: {
          searchExercises: "Buscar exercícios..."
        },
        value: {
          all: "tudo",
          speaking: 'fala',
          writing: 'escrita',
          reading: 'leitura',
          listening: 'compreensão auditiva',
          today: 'hoje',
          date: 'data',
          week: "semana",
          score: 'pontuação',
          skill: 'habilidade'
        },
        alt: {
          imageToDescribe: 'Imagem a descrever',
          lectureVisual: 'Visual da palestra'
        }
      },
      session: 'sessão',
      isexpanded: 'está expandido?',
      exerciseReview: 'Revisão do Exercício',
      readTheText: 'Leia o texto em voz alta de forma clara e natural, prestando atenção à pronúncia e fluência.',
      textToRead: 'Texto para Ler:',
      pteScore: 'Pontuação PTE:',
      originalTranscript: 'Transcrição Original:',
      accuracyOfContent: 'Precisão do conteúdo repetido',
      clarityAnd: 'Clareza e correção dos sons',
      oralFluency: 'Fluência Oral',
      smoothAndNatural: 'Fluxo de fala suave e natural',
      originalDiscursion: 'Discussão Original:',
      overallScore: 'Pontuação Geral:',
      speakingTips: 'Dicas de Fala:',
      listenToThe: 'Ouça a discussão em grupo e resuma os pontos-chave.',
      listenToTheQuestion: 'Ouça a pergunta e responda em 1-3 palavras.',
      sentenceTo: 'Frase a Repetir:',
      originalAudio: 'Áudio Original:',
      yourBrowserDoes: 'Seu navegador não suporta o elemento de áudio.',
      lookAtThe: 'Observe a imagem e descreva em detalhes o que você vê.',
      imageToDescribe: 'Imagem a Descrever:',
      modelDescription: 'Descrição do Modelo:',
      yourDescription: 'Sua Descrição:',
      pteScoreBreakdown: 'Detalhes da Pontuação PTE:',
      relevanceAnd: 'Relevância e completude da descrição',
      originalLecture: 'Palestra Original:',
      accompanying: 'Visual Acompanhante:',
      lecture: 'Transcrição da Palestra:',
      yourResponse: 'Sua Resposta:',
      coverageOfKeyPoints: 'Cobertura dos pontos-chave e detalhes',
      coverageOfKey: 'Cobertura dos pontos-chave da discussão',
      questionAudio: 'Áudio da Pergunta:',
      question: 'Pergunta:',
      blank: 'Lacuna',
      yourAnswer: 'Sua Resposta:',
      correctAnswer: 'Resposta Correta:',
      otherAcceptable: 'Outras Respostas Aceitáveis:',
      tipsForAnswer: 'Dicas para Responder Perguntas Curtas:',
      readThe: 'Leia a situação e forneça uma resposta apropriada.',
      situation: 'Situação:',
      listenToTheLecture: 'Ouça a palestra e reconte o conteúdo com suas próprias palavras.',
      appropriatenessAnd: 'Adequação e completude da resposta',
      speakers: 'Oradores:',
      discussion: 'Transcrição da Discussão:',
      yourSummary: 'Seu Resumo:',
      keyPoints: 'Pontos-Chave Abordados:',
      pointsTo: 'Pontos a Incluir:',
      pteScoringBreakdown: 'Detalhes da Pontuação PTE:',
      summarizeThe: 'Resuma o trecho em UMA frase de 5-75 palavras.',
      originalPassage: 'Passagem Original:',
      wordCount: 'Contagem de Palavras:',
      pteScoring: 'Pontuação PTE:',
      keyInformationAnd: 'Informações-chave e ideias principais',
      oneSentence575: 'Uma frase, 5-75 palavras',
      grammarAnd: 'Gramática e estrutura da frase',
      wordChoiceAnd: 'Escolha e amplitude do vocabulário',
      spellingAccuracy: 'Precisão ortográfica em toda a redação',
      totalScore: 'Pontuação Total',
      feedback: 'Feedback:',
      sampleAnswer: 'Exemplo de Resposta:',
      tips: 'Dicas:',
      withTheUserS: 'com a resposta do usuário',
      replacement: "substituição",
      answerAnalysis: 'Análise da Resposta:',
      correct: 'Correto',
      passage: 'Passagem:',
      options: 'Opções:',
      summaryOptions: 'Opções de Resumo:',
      explanation: 'Explicação:',
      audio: 'Áudio:',
      scoreBreakDown: 'Detalhes da Pontuação:',
      whatWasShown: 'O que foi mostrado (Texto de Exibição)',
      wordcountRequirements: 'Requisitos de contagem de palavras (200-300 palavras)',
      listeningMultipleChoice: 'Múltipla Escolha (Múltiplas Respostas) de Compreensão Auditiva',
      transcript: 'Transcrição:',
      audioTranscript: 'Transcrição do Áudio:',
      minimumScoreIs0: 'A pontuação mínima é 0.',
      pointForEachSelection: '+1 ponto para cada seleção correta, -1 ponto para cada seleção incorreta.',
      whatWeHeardYourSpeech: 'O Que Ouvimos (Sua Fala)',
      accuracyOfContentDelivered: 'Precisão do conteúdo entregue',
      yourScore: 'Sua pontuação:',
      yourScoreBlanksCorrect: 'Sua pontuação: {0} / {1} lacunas corretas = {2} pontos',
      fiveSeventyFiveWords: '5-75 palavras',
      listeningSingle: 'Múltipla Escolha Única (Compreensão Auditiva)',
      listeningFillIn: 'Preencher Lacunas (Compreensão Auditiva)',
      transcriptWith: 'Transcrição com Lacunas:',
      partialCredit1: 'Crédito parcial: 1 ponto para cada lacuna correta.',
      listenToTheSentence: 'Ouça a frase e repita-a exatamente como a ouvir.',
      points: 'pontos',
      original: 'Original',
      correctWithExclamation: 'Correto!',
      whatsWasSaid: 'O que foi dito (Transcrição):',
      asAny: 'como qualquer',
      blanksCorrect: 'lacunas corretas',
      missingWord: 'Palavra Ausente:',
      theMissingWord: 'A palavra ausente era:',
      results: 'Resultados:',
      correctly: 'Corretamente Destacado:',
      incorrectly: 'Incorretamente Destacado:',
      missedWords: 'Palavras Perdidas:',
      totalIncorrect: 'Total de Palavras Incorretas:',
      corrections: 'Correções:',
      wordByWord: 'Comparação Palavra por Palavra:',
      correctWords: 'Palavras Corretas:',
      totalWords: 'Total de Palavras:',
      accuracy: 'Precisão:',
      missingWords: 'Palavras Ausentes:',
      extraWords: 'Palavras Extras:',
      spellingErrors: 'Erros de Ortografia:',
      writeAnEssay: 'Escreva uma redação de 200-300 palavras sobre o tema dado.',
      essayPrompt: 'Prompt da Redação:',
      yourEssay: 'Sua Redação:',
      relevance: 'Relevância, completude e desenvolvimento das ideias',
      grammatical: 'Precisão e complexidade gramatical',
      rangeAnd: 'Amplitude e adequação do vocabulário',
      linguisticRange: 'Amplitude Linguística',
      varietyOfSentence: 'Variedade de estruturas de frases e expressões',
      logical: 'Organização lógica e desenvolvimento de parágrafos',
      writingTips: 'Dicas de Escrita:',
      dragWordsFrom: 'Arraste palavras do banco de palavras para preencher as lacunas na passagem.',
      passageWithYour: 'Passagem com Suas Respostas:',
      wordBank: 'Banco de Palavras:',
      answerDetails: 'Detalhes da Resposta:',
      theSentences: 'As frases abaixo foram organizadas na ordem correta. Sua ordem enviada é mostrada com indicadores.',
      yourSubmitted: 'Sua Ordem Enviada:',
      shouldBe: 'Deveria ser:',
      correctOrder: 'Ordem Correta:',
      scoreBreakdown: 'Detalhes da Pontuação',
      yourRecording: 'Sua Gravação:',
      smoothnessAnd: 'Fluidez e ritmo natural',
      whatWeHeard: 'O Que Ouvimos:',
      wordAccuracy: 'Análise de Precisão de Palavras:',
      wordsPerMinute: 'Palavras por Minuto:',
      aiFeedback: 'Feedback da IA:',
      retelllecture: "Recontar Palestra",
      retellTraceLecture: "Recontar Palestra",
      answershortquestion: "Responder Pergunta Curta",
      respondtosituation: "Responder a uma Situação",
      summarizegroupdiscu: "Resumir Discussão em Grupo",
      summarizeWritten: "Resumir Texto Escrito",
      selectMissingWord: "Selecionar Palavra Ausente",
      writeFrom: "Escrever por Ditado",
      HighlightIncorrectWords: "Destacar Palavras Incorretas",
      exerciseType: 'Tipo de exercício:',
      exerciseData: 'Dados do Exercício Disponíveis:',
      detailedExercise: 'Dados detalhados do exercício não disponíveis para este envio.',
      newSubmissions: 'Novos envios incluirão reconstrução completa do exercício.',
      missed: 'Perdidas',
      practiceAgain: 'Praticar Novamente',
      noPractice: 'Nenhuma sessão de prática encontrada',
      tryAdjustingYour: 'Tente ajustar seus filtros ou comece a praticar para construir seu histórico',
      thisPractice: 'Este histórico de prática usa dados de demonstração. As sessões reais serão rastreadas à medida que você completa os exercícios.',
      point: 'ponto',
      returnWord: 'retornar',
      showing: "Mostrando",
      return: "retornar",
      else: "outro",
      duration: "Duração:",
      score: "Pontuação:",
    },
    ProfilePage: {
      AuthGuard: {
        placeholder: {
          enterYourFullName: "Digite seu nome completo"
        },
        value: {
          male: 'masculino',
          female: 'feminino',
          portuguese: "Português",
          spanish: "Espanhol",
          english: "Inglês",
          french: "Francês",
          german: "Alemão",
          italian: "Italiano",
          chinese: "Chinês",
          japanese: "Japonês",
          korean: "Coreano",
          other: "Outro",
          fifteenMin: "15-30min",
          thirtyMin: "30-60min",
          twelveHours: "1-2horas",
          twoPlusHours: "2horas+"
        }
      }
    },
    ExerciseWithTranslation: {
      Card: {
        exerciseType: {
          readaloud: 'leitura em voz alta'
        }
      }
    },
    EssayExercise: {
      BaseExercise: {
        exerciseType: {
          essay: 'redação'
        },
        ExerciseSection: {
          title: {
            yourEssay: 'Sua Redação'
          },
          placeholder: {
            startWritingYour: 'Comece a escrever sua redação aqui... Lembre-se de incluir uma introdução, parágrafos de desenvolvimento com exemplos de apoio e uma conclusão.'
          }
        },
        analyzingYour: 'Analisando sua redação...'
      }
    },
    SummarizeWrittenExercise: {
      BaseExercise: {
        analyzingYour: 'Analisando sua resposta...'
      }
    },
    WriteFromDictationExercise: {
      BaseExercise: {
        ExerciseSection: {
          ExerciseSection: {
            SubmissionFeedback: {
              title: {
                submissionComplete: 'Envio Concluído'
              }
            }
          }
        }
      }
    },
    SummarizeSpokenTextExercise: {
      BaseExercise: {
        ExerciseSection: {
          ExerciseSection: {
            SubmissionFeedback: {
              title: {
                summarySubmitted: 'Resumo Enviado'
              }
            }
          }
        },
        wordcount: 'contagem de palavras'
      }
    },
    HighlightIncorrectWords: {
      BaseExercise: {
        correctTranscript: 'Transcrição Correta'
      }
    },
    SummarizeGroupDiscussionExercise: {
      BaseExercise: {
        ExerciseSection: {
          title: {
            listenToThe: 'Ouça a Discussão'
          },
          ExerciseSection: {
            title: {
              discussion: 'Transcrição da Discussão'
            },
            ExerciseSection: {
              ReadyToRecord: {
                message: {
                  clickThe: 'Clique no microfone para começar a gravar agora, ou espere o áudio terminar'
                }
              },
              PreparationPhase: {
                message: {
                  reviewYourNotes: 'Revise suas anotações e prepare-se para resumir a discussão'
                }
              },
              SubmissionFeedback: {
                title: {
                  recordingSubmitted: 'Gravação Enviada com Sucesso!'
                }
              }
            }
          }
        },
        audioStopped: 'Áudio parado - Gravação em andamento',
        fluency: 'Fluência'
      }
    },
    DescribeImageExercise: {
      BaseExercise: {
        ExerciseSection: {
          title: {
            imageToDescribe: 'Imagem a Descrever'
          },
          ExerciseSection: {
            ariaLabel: {
              startRecording: 'Iniciar Gravação'
            }
          }
        },
        imageNotAvailable: 'Imagem não disponível',
        preparingToRecord: 'Preparando para Gravar',
        studyTheImage: 'Estude a imagem cuidadosamente. A gravação começará automaticamente em',
        seconds: 'segundos.',
        stopRecording: 'Parar Gravação',
        isplayingrecording: 'está reproduzindo a gravação?',
        submitRecording: 'Enviar Gravação',
        analyzingYour: 'Analisando sua descrição...'
      }
    },
    RetellLectureExercise: {
      BaseExercise: {
        ExerciseSection: {
          title: {
            relatedImage: 'Imagem Relacionada'
          },
          alt: {
            lectureRelated: 'Imagem relacionada à palestra'
          },
          ExerciseSection: {
            title: {
              listenToThe: 'Ouça a Palestra'
            },
            ExerciseSection: {
              title: {
                yourResponse: 'Sua Resposta'
              },
              PreparationPhase: {
                message: {
                  reviewYourNotes: 'Revise suas anotações e prepare-se para recontar a palestra'
                }
              }
            }
          }
        },
        analyzingYour: 'Analisando seu reconto da palestra...'
      }
    },
    RespondToSituationExercise: {
      BaseExercise: {
        TextPassageSection: {
          title: {
            situation: 'Situação'
          }
        },
        getReadyToRespond: 'Prepare-se para Responder',
        reviewThe: 'Revise a situação acima. A gravação começará automaticamente quando o cronômetro terminar, ou você pode iniciar manualmente.'
      }
    },
    RepeatSentenceExercise: {
      BaseExercise: {
        ExerciseSection: {
          title: {
            listenToThe: 'Ouça a Frase'
          },
          ExerciseSection: {
            SubmissionFeedback: {
              title: {
                recordingEvaluated: 'Gravação Avaliada com Sucesso!'
              }
            }
          }
        },
        recordingIn: 'Gravando em andamento',
        readyToRecord: 'Pronto para Gravar',
        evaluationError: 'Erro de Avaliação',
        tryAgain: 'Tentar Novamente'
      }
    },
    AnswerShortQuestionExercise: {
      BaseExercise: {
        ExerciseSection: {
          title: {
            listenToThe: 'Ouça a Pergunta'
          }
        },
        questionStopped: 'Pergunta parada - Gravando sua resposta',
        readyToAnswer: 'Pronto para Responder',
        clickThe: 'Clique no microfone para começar a responder agora, ou espere a pergunta terminar',
        analyzingYour: 'Analisando sua resposta...',
        relevance: 'Relevância'
      }
    },
    ReadAloudExercise: {
      BaseExercise: {
        getReadyToRecord: 'Prepare-se para Gravar',
        readTheTextAbove: 'Leia o texto acima em silêncio. A gravação começará automaticamente quando o cronômetro terminar, ou você pode iniciar manualmente.'
      }
    },
    AIAssistant: {
      ariaLabel: {
        openAiAssistant: 'Abrir Assistente de IA'
      },
      newInsight: 'Novo insight!',
      aiLearning: 'Assistente de Aprendizado de IA',
      iMHereToHelp: 'Estou aqui para ajudar!',
      completeThe: 'Complete o exercício e eu fornecerei feedback detalhado sobre seu desempenho.',
      quickTipsForThis: 'Dicas rápidas para este exercício:',
      readTheQuestion: 'Leia a pergunta cuidadosamente para entender o que está sendo pedido',
      multipleAnswers: 'Múltiplas respostas podem estar corretas - não pare em encontrar apenas uma',
      eliminateObviously: 'Elimine as respostas obviamente erradas primeiro',
      lookForEvidence: 'Procure por evidências na passagem para apoiar suas escolhas',
      aiIsAnalyzing: 'A IA está analisando suas respostas...',
      getting: 'Obtendo feedback personalizado só para você',
      analysis: 'Análise:',
      learningTips: 'Dicas de Aprendizado:',
      answerBreakdown: 'Detalhes da Resposta:',
      nextSteps: 'Próximos Passos:',
      reviewThePassage: 'Revise a passagem novamente com esses insights em mente',
      tryToIdentifyThe: 'Tente identificar as palavras-chave que apontaram para as respostas corretas',
      practiceSimilar: 'Pratique perguntas semelhantes para reforçar este aprendizado'
    },
    MultipleChoiceSingle: {
      BaseExercise: {
        ExerciseSection: {
          title: {
            readingPassage: 'Trecho de Leitura'
          }
        },
        readingPassage: 'Trecho de Leitura:'
      }
    },
    ReadingFillBlanks: {
      BaseExercise: {
        timeSUp: 'Tempo esgotado! Enviando suas respostas...',
        completeText: 'Texto Completo:'
      }
    },
    ReadingWritingBlanks: {
      BaseExercise: {
        ExerciseSection: {
          title: {
            completeTheText: 'Complete o Texto'
          }
        }
      },
      value: {
        text: ''
      }
    },
    FillBlanksDragDrop: {
      ariaLabel: {
        removeWord: 'Remover palavra'
      },
      BaseExercise: {
        wordBank: 'Banco de Palavras',
        allWordsHaveBeen: 'Todas as palavras foram colocadas',
        resetAll: 'Redefinir Tudo'
      }
    },
    SlidingPanel: {
      role: {
        dialog: 'diálogo'
      },
      ariaLabel: {
        closePanel: 'Fechar painel'
      }
    },
    SubscriptionGuard: {
      monthlyLimitReached: 'Limite Mensal Atingido',
      upgradeRequired: 'Atualização Necessária',
      thisFeature: 'Este recurso requer uma',
      subscription: 'assinatura.',
      viewPlans: 'Ver Planos',
      upgradeToPremium: 'Atualizar para o plano Premium',
      upgradeYourPlan: 'Atualize seu plano',
    },
    SignupForm: {
      createYourAccount: 'Crie sua conta',
      joinPteasyAnd: 'Junte-se ao PTEasy e comece sua jornada',
      password: 'Senha',
      creatingAccount: 'Criando conta...',
      createAccount: '\'Criar Conta\'',
      signUpWithGoogle: 'Cadastre-se com o Google',
      alreadyHaveAn: 'Já tem uma conta?'
    },
    LoginForm: {
      welcomeBack: 'Bem-vindo(a) de volta',
      pleaseSignInTo: 'Por favor, faça login em sua conta',
      forgotPassword: 'Esqueceu a senha?',
      signingIn: 'Entrando...',
      signIn: '\'Entrar\'',
      continueWithGoogle: 'Continuar com o Google',
      donTHaveAn: 'Não tem uma conta?',
      signUp: 'Cadastre-se'
    },
    termsOfServicePage: {
      tableOfContents: 'Índice',
      acceptanceOf: '1. Aceitação dos Termos',
      eligibility: '2. Elegibilidade',
      account: '3. Registro de Conta',
      services: '4. Descrição dos Serviços',
      paymentSubscriptions: '5. Pagamento e Assinaturas',
      userContent: '6. Conteúdo do Usuário',
      userConduct: '7. Conduta do Usuário',
      intellectual: '8. Propriedade Intelectual',
      privacy: '9. Privacidade',
      disclaimers: '10. Isenções de Responsabilidade',
      LimitationOf: '11. Limitação de Responsabilidade',
      Termination: '12. Rescisão',
      byAcessingOrUsing: 'Ao acessar ou usar o PTEasy ("o Serviço"), você concorda em ficar vinculado a estes Termos de Serviço ("Termos"). Se você não concordar com qualquer parte destes termos, você não tem permissão para acessar o Serviço.',
      theseTermsApply: 'Estes Termos se aplicam a todos os visitantes, usuários e outros que acessam ou usam o Serviço, incluindo, mas não se limitando a, usuários registrados, assinantes e contribuidores de conteúdo.',
      toUsePteasyYou: 'Para usar o PTEasy, você deve:',
      beAtLeast13: 'Ter pelo menos 13 anos de idade',
      haveTheLegal: 'Ter capacidade legal para celebrar um contrato vinculativo',
      notBeProhibited: 'Não ser proibido de usar o Serviço sob as leis aplicáveis',
      provideAccurate: 'Fornecer informações precisas, atuais e completas',
      provideCurrent: 'Fornecer informações de registro precisas e completas',
      ifYouAreUnder: 'Se você tem menos de 18 anos, você deve ter o consentimento dos pais ou responsável para usar o Serviço.',
      accountCreation: 'Criação de Conta',
      whenYouCreateAn: 'Ao criar uma conta, você concorda em:',
      maintainAnd: 'Manter e prontamente atualizar suas informações de conta',
      maintainThe: 'Manter a segurança de sua senha e conta',
      accept: 'Aceitar a responsabilidade por todas as atividades sob sua conta',
      immediatelyNotify: 'Notificar-nos imediatamente sobre qualquer uso não autorizado',
      accountRestrictions: 'Restrições da Conta',
      oneAccountPer: 'Uma conta por pessoa',
      accountsAre: 'As contas são intransferíveis',
      youMayNotShare: 'Você não pode compartilhar suas credenciais de conta',
      youMayNotUse: 'Você não pode usar a conta de outra pessoa',
      pteasyProvides: 'O PTEasy oferece:',
      pteExam: 'Materiais e exercícios de preparação para o exame PTE',
      mockTests: 'Simulados que simulam o exame PTE real',
      aiPoweredScoring: 'Pontuação e feedback alimentados por IA',
      progressTracking: 'Rastreamento de progresso e análises',
      studyPlansAnd: 'Planos de estudo e recomendações',
      important: 'Importante:',
      theServiceAndItsOriginalContent: 'O Serviço e seu conteúdo original (excluindo o conteúdo do usuário), recursos e funcionalidades são e permanecerão propriedade exclusiva da PTEasy. O Serviço é protegido por direitos autorais, marca registrada e outras leis.',
      pteasyIsAn: 'PTEasy é uma plataforma independente de preparação para testes e não é afiliada, endossada ou associada à Pearson PLC ou ao exame oficial PTE Academic.',
      subscriptionPlans: 'Planos de Assinatura',
      weOfferVarious: 'Oferecemos vários níveis de assinatura:',
      limitedAccessTo: 'Acesso limitado a exercícios individuais',
      customPricingFor: 'Preços personalizados para instituições',
      billingTerms: 'Termos de Faturamento',
      subscriptions: 'As assinaturas são renovadas automaticamente, a menos que sejam canceladas',
      paymentIsDueAt: 'O pagamento é devido no início de cada ciclo de faturamento',
      allFeesAre: 'Todas as taxas não são reembolsáveis, exceto conforme exigido por lei',
      weReserveThe: 'Reservamo-nos o direito de alterar os preços com aviso prévio de 30 dias',
      cancellation: 'Cancelamento',
      youMayCancelYour: 'Você pode cancelar sua assinatura a qualquer momento. O acesso continua até o final do período de faturamento atual. Não são fornecidos reembolsos parciais por tempo não utilizado.',
      yourContent: 'Seu Conteúdo',
      youRetain: 'Você retém a propriedade do conteúdo que você envia, incluindo:',
      writtenResponses: 'Respostas escritas aos exercícios',
      audioRecordings: 'Gravações de áudio para exercícios de fala',
      profileInformation: 'Informações de perfil e notas de estudo',
      licenseGrant: 'Concessão de Licença',
      bySubmitting: 'Ao enviar conteúdo, você concede ao PTEasy uma licença mundial, não exclusiva e livre de royalties para usar, reproduzir e analisar seu conteúdo para:',
      providingAnd: 'Fornecer e melhorar nossos serviços',
      generatingScores: 'Gerar pontuações e feedback',
      researchAnd: 'Fins de pesquisa e desenvolvimento',
      creatingAnonymized: 'Criar dados agregados anonimizados',
      acceptableUse: 'Uso Aceitável',
      youAgreeToUse: 'Você concorda em usar o PTEasy apenas para fins legais e de acordo com estes Termos.',
      prohibited: 'Atividades Proibidas',
      youMayNot: 'Você não pode:',
      shareOrDistribute: 'Compartilhar ou distribuir conteúdo protegido por direitos autorais sem permissão',
      useAutomated: 'Usar sistemas automatizados para acessar o Serviço',
      attemptToGain: 'Tentar obter acesso não autorizado a qualquer parte do Serviço',
      interfereWithOr: 'Interferir ou interromper o Serviço ou servidores',
      reverseEngineerOr: 'Fazer engenharia reversa ou descompilar qualquer parte do Serviço',
      useTheServiceFor: 'Usar o Serviço para qualquer finalidade comercial sem permissão',
      impersonateAnother: 'Se passar por outra pessoa ou entidade',
      collectOrHarvest: 'Coletar ou colher informações do usuário',
      uploadMalicious: 'Carregar código malicioso ou vírus',
      pteasyProperty: 'Propriedade do PTEasy',
      trademarks: 'Marcas Registradas',
      pteasyNameLogo: 'O nome, logotipo e todos os nomes, logotipos, produtos e nomes de serviços relacionados ao PTEasy são marcas registradas do PTEasy. Você não pode usar essas marcas sem nossa permissão prévia por escrito.',
      yourUseOfPteasy: 'Seu uso do PTEasy também é regido pela nossa',
      pleaseReviewOur: '. Por favor, revise nossa Política de Privacidade, que explica como coletamos, usamos e protegemos suas informações.',
      theServiceIs: 'O SERVIÇO É FORNECIDO "COMO ESTÁ" E "CONFORME DISPONÍVEL" SEM GARANTIAS DE QUALQUER TIPO.',
      weDoNotGuarantee: 'Não garantimos que o Serviço será ininterrupto, seguro ou livre de erros. Não garantimos a precisão, completude ou utilidade de qualquer informação no Serviço.',
      noGuaranteeOf: 'Nenhuma Garantia de Resultados',
      pteasyDoesNot: 'O PTEasy não garante nenhuma pontuação ou resultado específico. O sucesso no exame PTE depende de muitos fatores fora do nosso controle, incluindo esforço individual, aptidão e desempenho no dia do teste.',
      toTheMaximum: 'Na extensão máxima permitida por lei, o PTEasy não será responsável por quaisquer danos indiretos, incidentais, especiais, consequenciais ou punitivos, incluindo, mas não se limitando a:',
      lossOfProfits: 'Perda de lucros, dados ou uso',
      testPerformanceOr: 'Desempenho ou pontuações no teste',
      interruptionOf: 'Interrupção de negócios',
      costOfSubstitute: 'Custo de serviços substitutos',
      ourTotalLiability: 'Nossa responsabilidade total não excederá o valor pago por você ao PTEasy nos 12 meses anteriores à reclamação.',
      weMayTerminateOr: 'Podemos rescindir ou suspender sua conta imediatamente, sem aviso prévio, por:',
      breachOfThese: 'Violação destes Termos',
      fraudulentOr: 'Atividade fraudulenta ou ilegal',
      nonPaymentOfFees: 'Não pagamento de taxas',
      atOurSole: 'A nosso exclusivo critério por qualquer motivo',
      uponTermination: 'Após a rescisão, seu direito de usar o Serviço cessará imediatamente. Todas as disposições dos Termos que razoavelmente deveriam sobreviver à rescisão sobreviverão.',
      GoverningLaw: '13. Lei Aplicável',
      theseTermsShall: 'Estes Termos serão regidos e interpretados de acordo com as leis do Brasil, sem considerar suas disposições de conflito de leis. Quaisquer disputas serão resolvidas nos tribunais de São Paulo, Brasil.',
      byAccessingOr: 'Ao acessar ou usar',
      fiveMockTests: '5 simulados, pontuação completa',
      twentyMockTests: '20 simulados, recursos avançados'
    },
    MockTestPage: {
      loadingTest: 'Carregando teste...'
    },
    RepeatSentencePage: {
      audioWillPlay: 'O áudio será reproduzido automaticamente',
      listening: 'Ouvindo...',
      of33: 'de 33'
    },
    ReTellLecturePage: {
      recordingIn: 'Gravando em',
      listeningTo: 'Ouvindo palestra...'
    },
    ReadyPage: {
      readyToStartThe: 'Pronto para iniciar o teste?',
      startingTheTest77Minutes: 'Iniciar o teste acionará o cronômetro. Parte 1 (Fala e Escrita) tem 77 minutos.',
      of4: 'de 4'
    },
    SpeakingWritingCompletePage: {
      pleaseClick: 'Por favor, clique',
      next: '\"próximo\"',
      toProceedToThe: 'para prosseguir para a próxima seção.'
    },
    SummarizeWrittenTextPage: {
      readThePassage: 'Leia o trecho abaixo e resuma-o em uma frase. Digite sua resposta na caixa na parte inferior da tela. Você tem 10 minutos para terminar esta tarefa. Sua resposta será julgada pela qualidade de sua escrita e pela forma como ela apresenta os pontos-chave do trecho.',
      paste: 'Colar',
      summarizeWritten: 'Resumir Texto Escrito - Escrita PTE',
      criticalRule: "Regra Crítica",
      step: 'Passo',
      whenToUse: 'Quando usar:',
      original: 'Original:',
      originalPassage: 'trecho original da passagem',
      words: 'palavras):',
      keyPointsCaptured: 'Pontos-Chave Capturados:',
      whyItSWrong: 'Por que está errado:',
      fix: 'Corrigir:',
      andAlso: 'e também demonstra que...',
      while: 'enquanto... no entanto...',
      moreover: 'além disso, destacando...',
      furthermore: 'explicando ainda...',
      although: 'embora... no entanto...',
      despite: 'apesar de... ainda assim...',
      evenThough: 'mesmo que... ainda assim...',
      resultingIn: 'resultando em...',
      leadingTo: 'levando a...',
      consequently: 'consequentemente causando...',
      thereby: 'assim criando...',
      ultimately: 'em última análise, mostrando...',
      thus: 'assim demonstrando...',
      therefore: 'portanto indicando...',
      henceProving: 'provando assim...',
      includeNumbersOr: 'Inclua números ou estatísticas do trecho se forem centrais para o argumento',
      startWithThe: 'Comece com "A passagem" ou "O autor" para sinalizar imediatamente que você está resumindo',
      practiceTyping: 'Pratique digitar frases complexas - você precisará de boa velocidade de digitação',
      of1: 'de 1'
    },
    ReadAloudExercisePage: {
      lookAtTheText: 'Observe o texto abaixo. Em 35 segundos, você deve ler este texto em voz alta da forma mais natural e clara possível. Você tem 35 segundos para ler em voz alta.',
      loadingPassage: 'Carregando trecho...',
      recordingIn: "Gravando em",
      noPassageAvailable: 'Nenhum trecho disponível'
    },
    SpeakingWritingOverviewPage: {
      part1Speaking: 'Parte 1: Fala e Escrita',
      inThisPartYou: 'Nesta parte você será testado em suas habilidades de fala e escrita',
      readThe: 'Leia as instruções de cada pergunta cuidadosamente e responda conforme as orientações',
      pleaseSpeak: 'Por favor, fale claramente e diretamente no microfone',
      inTheWriting: 'Nas seções de escrita, por favor, use pontuação e capitalização apropriadas.',
      essaysWrittenAll: 'Redações escritas todas em MAIÚSCULAS ou sem pontuação receberão 0 (zero) pontos.',
      makeSureYouKeep: 'Certifique-se de manter-se estritamente dentro dos limites de palavras.',
      section: 'Seção',
      itemType: 'Tipo de Item',
      timeAllowed: 'Tempo permitido',
      section1: 'Seção 1',
      section2: 'Seção 2',
      readAloud: 'Leitura em voz alta',
      repeatSentence: 'Repetir frase',
      describeImage: 'Descrever imagem',
      reTellLecture: 'Recontar palestra',
      answerShort: 'Responder pergunta curta',
      summarizeGroup: 'Resumir discussão em grupo',
      respondingToA: 'Respondendo a uma situação',
      section3: 'Seção 3',
      summarizeWritten: 'Resumir texto escrito',
      section4: 'Seção 4',
      oneMinute: '1 minuto',
      thirtyFourMinutes: '34 Minutos'
    },
    PersonalIntroductionPage: {
      pleaseIntroduce: 'Por favor, apresente-se. Por exemplo, você poderia falar sobre um ou mais dos seguintes:',
      yourInterests: 'Seus interesses',
      yourPlansFor: 'Seus planos para estudos futuros',
      whyYouWantTo: 'Por que você quer estudar no exterior',
      whyYouNeedTo: 'Por que você precisa aprender inglês',
      whyYouChoseThe: 'Por que você escolheu o Pearson Test of English',
      recordingWill: 'A gravação começará em',
      seconds: 'segundos',
      of2: 'de 2'
    },
    TestFormatPage: {
      thisTestIs: 'Este teste tem aproximadamente 2 horas de duração.',
      part: 'Parte',
      timeAllowed: 'Tempo Permitido',
      introduction: 'Introdução',
      notTimed: 'Não cronometrado',
      part1: 'Parte 1',
      speakingAndWriting: 'Fala e Escrita',
      part2: 'Parte 2',
      part3: 'Parte 3',
      howTheTimerWorks: 'Como o cronômetro funciona',
      thisTestHas3: 'Este teste tem 3 partes ou seções principais.',
      whenYouStartEach: 'Ao iniciar cada parte, um cronômetro aparecerá no canto superior direito. Ele mostra quanto tempo você tem para completar a seção.',
      readATextAloud: 'Leia um texto em voz alta. Testa pronúncia e fluência oral.',
      listenAndRepeat: 'Ouça e repita a frase exatamente como a ouvir.',
      listenToALecture: 'Ouça uma palestra e reconte os pontos principais com suas próprias palavras.',
      answerSimple: 'Responda a perguntas simples com uma ou poucas palavras.',
      essayWriting: 'Escrita de Redação',
      selectAppropriate: 'Selecione as palavras apropriadas nos menus suspensos para completar o texto.',
      chooseOneCorrect: 'Escolha uma resposta correta entre várias opções.',
      arrangeTextBoxes: 'Organize as caixas de texto na ordem lógica correta.',
      readingFillIn: 'Leitura: Preencher Lacunas',
      dragWordsFromA: 'Arraste palavras de uma caixa para preencher as lacunas no texto.',
      selectMultiple: 'Selecione múltiplas respostas corretas com base no áudio.',
      typeMissingWords: 'Digite as palavras que faltam enquanto ouve a gravação.',
      chooseThe: 'Escolha o parágrafo que melhor resume a gravação.',
      seventySevenMinutes: '77 Minutos',
      twentyFiveMinutes: '25 Minutos',
      thirtyOneMinutes: '31 Minutos',
      writeAn: 'Escreva uma redação argumentativa (200-300 palavras) sobre um determinado tema.',
      thirtyTwoMinutes: '32-41 minutos',
      moreThanOneMay: '(mais de uma pode estar correta).',
      fortyFiveMinutes: '45-57 minutos',
      writeASummary: 'Escreva um resumo (50-70 palavras) da palestra em áudio.',
      describeAnImage: 'Descreva uma imagem (gráfico, tabela, mapa, etc.) em detalhes.',
      selectAllCorrect: 'Selecione todas as respostas corretas (mais de uma pode estar correta).'
    },
    MicrophoneCheckPage: {
      youAreUsing: 'Você está usando o navegador:',
      microphoneCheck: 'Verificação do microfone',
      recordingComplete: 'Gravação Concluída',
      clickPlaybackTo: 'Clique em Reproduzir para revisar',
      readyToRecord: 'Pronto para gravar',
      clickRecordTo: 'Clique em Gravar para iniciar',
      youMustCheckYour: 'Você deve verificar seu microfone antes de clicar em próximo e continuar com o teste.',
      makeSureYour: 'Certifique-se de que seu microfone esteja ligado.',
      whenYouAreReady: 'Quando estiver pronto, clique no botão Gravar e diga',
      theManFelt: '\"O homem se sentiu mal, então decidiu tomar um remédio e ir para a cama.\"',
      intoTheMicrophone: 'no microfone.',
      afterYouHave: 'Depois de falar, clique no botão Parar. Sua gravação está agora completa.',
      nowClickOnThe: 'Agora clique no botão Reproduzir. Você deve se ouvir falando claramente.',
      ifYouCanNotHear: 'Se você não consegue ouvir sua voz claramente, ou o feedback é que o microfone',
      isTooLoudOr: 'está muito alto ou baixo, recomendamos mudar a posição do seu microfone,',
      orYourMicrophone: 'ou as configurações do seu microfone no seu computador antes de clicar em próximo.',
      audioLevel: 'Nível de Áudio:',
      audioTooLoud: 'Áudio muito alto - afaste o microfone',
      audiolevel: 'nível de áudio',
      audioTooQuiet: 'Áudio muito baixo - fale mais alto ou aproxime o microfone',
      theAudioSample: 'A amostra de áudio que você gravou é aceitável',
      microphoneAccess: 'O acesso ao microfone é necessário. Por favor, habilite as permissões do microfone nas configurações do seu navegador.',
      of4: "de 4"
    },
    MockTestIntroPage: {
      weRecommendA: 'Recomendamos um teclado QWERTY, pois são usados no teste ao vivo, mas não é essencial para este teste.',
      chooseAQuiet: 'Escolha um local tranquilo onde você não será interrompido.',
      ensureStrongAnd: 'Garanta uma conexão Wi-Fi forte e consistente.',
      checkingSession: 'Verificando status da sessão...'
    },
    WriteFromDictationPage: {
      noExerciseData: 'Nenhum dado de exercício disponível',
      youWillHearA: 'Você ouvirá uma frase. Digite a frase na caixa abaixo exatamente como a ouvir. Escreva o máximo da frase que puder. Você ouvirá a frase apenas uma vez.',
      audioPlayer: 'Reprodutor de Áudio',
      beginningIn: 'Começando em',
      paste: "Colar"
    },
    ListeningMultipleChoiceMultiplePage: {
      listenToThe: "Ouça a gravação e responda à pergunta selecionando todas as respostas corretas. Você precisará selecionar mais de uma resposta.",
      audioPlayer: "Reprodutor de Áudio",
      beginningIn: "Começando em"
    },
    SummarizeSpokenTextPage: {
      youWillHearA: 'Você ouvirá uma breve palestra. Escreva um resumo para um colega de estudante que não estava presente na palestra. Você deve escrever 50-70 palavras.',
      youHave10Minutes: 'Você tem 10 minutos para terminar esta tarefa. Sua resposta será julgada pela qualidade de sua escrita e pela forma como ela apresenta os pontos-chave apresentados na palestra.',
      audioPlayer: "Reprodutor de Áudio",
      beginningIn: "Começando em",
      paste: "Colar"
    },
    FillBlanksDragPage: {
      errorNoText: 'Erro: Nenhum conteúdo de texto encontrado',
      index: 'índice',
      inTheTextBelow: 'No texto abaixo, algumas palavras estão faltando. Arraste as palavras da caixa abaixo para o local apropriado no texto. Para desfazer uma escolha de resposta, arraste a palavra de volta para a caixa abaixo do texto.',
      of16: 'de 16',
      allWordsHaveBeen: "Todas as palavras foram colocadas"
    },
    ReadingStartPage: {
      inThisPartYou: 'Nesta parte você será testado principalmente em suas habilidades de leitura',
      theNextScreen: 'A próxima tela apresentará a primeira tarefa de leitura',
      multipleChoice: 'Múltipla escolha, escolha uma única resposta',
      reOrderParagraphs: 'Reordenar parágrafos',
      readThe: "Leia as instruções de cada pergunta cuidadosamente e responda conforme as orientações",
      itemType: "Tipo de Item",
      timeAllowed: "Tempo permitido",
      twentyFiveMinutes: "25 Minutos",
    },
    ListeningFillBlanksPage: {
      loadingExercise: 'Carregando conteúdo do exercício...',
      ifThisPersists: 'Se isso persistir, os dados do exercício podem estar faltando.',
      audioPlayer: "Reprodutor de Áudio",
      beginningIn: "Começando em"
    },
    MultipleChoiceSinglePage: {
      readTheTextAnd: 'Leia o texto e responda à pergunta de múltipla escolha selecionando a resposta correta. Apenas uma resposta está correta.'
    },
    SelectMissingWordPage: {
      youWillHearA: 'Você ouvirá uma gravação. No final da gravação, a última palavra ou grupo de palavras foi substituído por um bipe. Selecione a opção correta para completar a gravação.',
      playing: 'Reproduzindo',
      noExerciseData: "Nenhum dado de exercício disponível",
      audioPlayer: "Reprodutor de Áudio",
      beginningIn: "Começando em"
    },
    MultipleChoiceMultiplePage: {
      of16: "de 16",
      readTheTextAnd: 'Leia o texto e responda à pergunta selecionando todas as respostas corretas. Você precisará selecionar mais de uma resposta.'
    },
    ListeningStartPage: {
      inThisPartYou: 'Nesta parte você será testado principalmente em suas habilidades de compreensão auditiva',
      summarizeSpoken: 'Resumir texto falado',
      highlightCorrect: 'Destacar resumo correto',
      selectMissingWord: 'Selecionar palavra ausente',
      highlightIncorrect: 'Destacar palavras incorretas',
      writeFromDictation: 'Escrever por ditado',
      loadingListening: 'Carregando exercícios de compreensão auditiva...',
      nineteenMinutes: '19 Minutos',
      readThe: "Leia as instruções de cada pergunta cuidadosamente e responda conforme as orientações",
      section: "Seção",
      itemType: "Tipo de Item",
      timeAllowed: "Tempo permitido",
      section1: "Seção 1",
      section2: "Seção 2",
      multipleChoice: "Múltipla escolha, escolha única resposta",
    },
    ReadingFillBlanksPage: {
      pidx: 'pIdx',
      select: 'Selecionar',
      belowIsAText: 'Abaixo está um texto com lacunas. Clique em cada lacuna, uma lista de opções aparecerá. Selecione a opção de resposta apropriada para cada lacuna.'
    },
    ReorderParagraphsPage: {
      theTextBoxesIn: 'As caixas de texto no painel esquerdo foram colocadas em ordem aleatória. Restaure a ordem original arrastando as caixas de texto do painel esquerdo para o painel direito.',
      source: 'Fonte',
      allParagraphsHave: 'Todos os parágrafos foram movidos para o painel de destino',
      dragParagraphs: 'Arrastar parágrafos aqui para reordená-los',
      of16: "de 16"
    },
    HighlightCorrectSummaryPage: {
      youWillHearA: 'Você ouvirá uma gravação. Clique no parágrafo que melhor se relaciona com a gravação.',
      noExerciseData: "Nenhum dado de exercício disponível",
      audioPlayer: "Reprodutor de Áudio",
      playing: "Reproduzindo",
      beginningIn: "Começando em"
    },
    RespondToSituationPage: {
      listenAndReadA: 'Ouça e leia uma descrição de uma situação. Você terá 10 segundos para pensar sobre sua resposta. Em seguida, você ouvirá um bipe. Você terá 40 segundos para responder à pergunta. Por favor, responda o mais completamente possível.',
      listeningTo: 'Ouvindo situação...',
      of33: "de 33",
      recordingIn: "Gravando em",
    },
    ListeningCompletePage: {
      testComplete: 'Teste Concluído!',
      congratulations: 'Parabéns! Você concluiu com sucesso todo o simulado.',
      resultsProcessing: 'Processamento de Resultados',
      yourResponsesHave: 'Suas respostas foram enviadas para avaliação. Os resultados completos e o detalhamento da pontuação estarão disponíveis em breve na seção de Simulados do seu painel.',
      youWillReceiveA: 'Você receberá uma notificação assim que suas pontuações estiverem prontas.',
      testSummary: 'Resumo do Teste',
      testName: 'Nome do Teste:',
      ChooseWhichTypesOfEmails: 'Escolha os tipos de e-mail que você gostaria de receber do PTEasy',
      testStatus: 'Status do Teste:',
      complete: 'Completo',
      goToMockTests: 'Ir para Simulados',
      returnToDashboard: 'Voltar ao Painel',
      youWillBe: 'Você será automaticamente redirecionado para a seção de Simulados em 7 segundos...',
      needHelp: 'Precisa de ajuda para entender suas pontuações?',
      learnAboutPte: 'Saiba mais sobre a pontuação do PTE'
    },
    SummarizeGroupDiscussionPage: {
      youWillHearThree: 'Você ouvirá três pessoas tendo uma discussão. Quando ouvir o bipe, resuma toda a discussão. Você terá 10 segundos para se preparar e 2 minutos para dar sua resposta.',
      listeningTo: 'Ouvindo discussão...',
      of33: "de 33",
      recordingIn: "Gravando em"
    },
    CookiePolicyPage: {
      weUseCookiesTo: 'Usamos cookies para lembrar suas preferências, manter você logado, analisar o uso do site e melhorar sua experiência de aprendizado. Você pode controlar as configurações de cookies através do seu navegador, embora alguns recursos possam não funcionar corretamente sem eles.',
      authentication: 'Autenticação:',
      websiteUsageStatistics: 'Estatísticas de uso do website (se ativado)',
      toKeepYouSigned: 'Para manter você logado em sua conta',
      preferences: 'Preferências:',
      toRememberYour: 'Para lembrar suas configurações e preferências',
      security: 'Segurança:',
      toSupportSecurity: 'Para dar suporte a recursos de segurança e detectar atividades maliciosas',
      analytics: 'Análise:',
      toUnderstandHow: 'Para entender como você usa nossa plataforma e melhorá-la',
      performance: 'Desempenho:',
      toEnsureThe: 'Para garantir que a plataforma funcione eficientemente',
      personalization: 'Personalização:',
      toCustomizeYour: 'Para personalizar sua experiência de aprendizado',
      stripe: 'Stripe:',
      paymentProcessing: 'Processamento de pagamentos e prevenção de fraudes',
      cloudinary: 'Cloudinary:',
      audioUploadedToCloudinary: 'Áudio enviado para o Cloudinary:',
      mediaDeliveryAnd: 'Entrega e otimização de mídia',
      googleAnalyticsOptOut: 'Complemento do Navegador para desativar o Google Analytics',
      googleOauth: 'Google OAuth:',
      secure: 'Autenticação segura',
      analyticsCookies: 'Cookies de análise: Instale o',
      marketingCookies: 'Cookies de marketing: Visite a',
      digitalAdvertising: 'página de opt-out da Digital Advertising Alliance',
      weMayUpdateThis: 'Podemos atualizar esta Política de Cookies periodicamente. Notificaremos você sobre quaisquer alterações materiais publicando a nova Política de Cookies nesta página e atualizando a data de "Última atualização".',
      yourConsent: 'Seu Consentimento:',
      byContinuingTo: 'Ao continuar a usar o PTEasy, você consente com nosso uso de cookies conforme descrito nesta política. Você pode retirar seu consentimento a qualquer momento ajustando as configurações do seu navegador.',
      google: 'Google',
      googleAnalytics: 'Google Analytics:'
    },
    AudioCheckerPage: {
      uploadedTo: 'enviado para',
      ifUrlsAreStored: "Se os URLs estiverem armazenados, você os verá nos resultados"
    },
    MockTestsPage: {
      AuthGuard: {
        questions: 'perguntas',
        estimatedScore: 'Faixa de pontuação estimada:',
        premium: 'Premium'
      }
    },
    NotificationSettingsPage: {
      chooseWhichTypes: 'Escolha os tipos de e-mail que você gostaria de receber do PTEasy',
      youWillAlways: 'Você sempre receberá e-mails transacionais essenciais, como redefinições de senha, confirmações de pagamento e alertas de segurança, independentemente dessas configurações.',
      important: "Importante:",
    },
    AchievementsPage: {
      AuthGuard: {
        weReBuildingAn: 'Estamos construindo um sistema de conquistas emocionante para tornar sua jornada de preparação para o PTE ainda mais gratificante!',
        browseThroughThe: 'Navegue pelos distintivos incríveis que você poderá colecionar e veja quais desafios esperam por você.',
        unlocked: 'Desbloqueado',
        automatic: 'Rastreamento Automático:',
        yourAchievements: 'Suas conquistas serão rastreadas automaticamente à medida que você pratica',
        realTimeUpdates: 'Atualizações em Tempo Real:',
        progressBarsWill: 'As barras de progresso serão atualizadas em tempo real à medida que você completa os exercícios',
        notification: 'Sistema de Notificação:',
        getNotified: 'Seja notificado instantaneamente quando desbloquear novos distintivos',
        profileDisplay: 'Exibição de Perfil:',
        showOffYour: 'Mostre suas conquistas em sua página de perfil',
        rewardPoints: 'Pontos de Recompensa:',
        earnPointsFor: 'Ganhe pontos por cada conquista para desbloquear recursos especiais',
        pts: 'pts',
        achievement: "Sistema de Conquistas em Breve!",
        unlockUnique: "Desbloqueie distintivos únicos",
        complete: "Complete desafios",
        trackYour: "Acompanhe seu progresso",
        earnRewards: "Ganhe recompensas",
        remaining: "restantes",
        Days: "dias",
      }
    },
    FillBlanksDragDropTestPage: {
      testMode: 'Modo de Teste',
      thisIsATestPage: 'Esta é uma página de teste com dados simulados para o'
    },
    ReadingWritingBlanksListPage: {
      loadingExercises: 'Carregando exercícios...',
      completePassages: 'Complete passagens selecionando as palavras mais apropriadas em menus suspensos.',
      thisExerciseTests: 'Este exercício testa seu vocabulário, gramática e compreensão contextual.'
    },
    FAQPage: {
      canTFindWhat: 'Não consegue encontrar o que procura? Nossa equipe de suporte está aqui para ajudar.'
    },
    HelpCenterPage: {
      ourSupportTeamIs: 'Nossa equipe de suporte está aqui para ajudar você a ter sucesso em sua jornada no PTE. Obtenha assistência personalizada de nossa equipe de especialistas.'
    },
    FreeTemplatesPage: {
      comprehensiveEssay: 'Modelos de redação abrangentes para redações argumentativas, de opinião, de vantagens e desvantagens.',
      academicContent: 'Conteúdo Acadêmico',
      essayTypes: 'Tipos de Redação',
      contentFocus: 'Foco do Conteúdo',
      structuredApproach: 'Abordagem estruturada para recontar palestras com identificação e entrega de pontos-chave.',
      types: 'Tipos',
      band90: 'Banda 90'
    },
    StudyTipsPage: {
      improveSpeaking: 'Melhore a Fluência na Fala',
      regularPractice: 'A prática regular com técnicas adequadas pode aumentar significativamente suas pontuações de fala.',
      recordYourself: 'Grave-se diariamente',
      practiceShadowing: 'Pratique a técnica de shadowing',
      focusOnClear: 'Concentre-se na pronúncia clara',
      masterEssayWriting: 'Domine a Escrita de Redações',
      aWellStructured: 'Uma redação bem estruturada com gramática adequada pode garantir altas pontuações na escrita.',
      useEssayTemplates: 'Use modelos de redação',
      practiceTyping: 'Pratique a velocidade de digitação',
      learnTransition: 'Aprenda frases de transição',
      enhanceListening: 'Aprimore as Habilidades de Compreensão Auditiva',
      activeListening: 'A escuta ativa e a anotação são cruciais para pontuar bem na seção de compreensão auditiva.',
      watchAcademic: 'Assista a palestras acadêmicas',
      practice: 'Pratique atalhos para anotações',
      focusOnKeywords: 'Concentre-se em palavras-chave'
    },
    TrialStartedPage: {
      welcomeToPteasyPlanName: 'Bem-vindo ao PTEasy {0}!',
      welcomeToYourTrialPlanName: 'Bem-vindo ao seu teste {0}!',
      welcomeToPteasy: 'Bem-vindo ao PTEasy',
      yourDayFree: 'Seu teste gratuito de {0} dias começou com sucesso',
      trialPeriod: 'Período de Teste',
      billingCycle: 'Ciclo de Faturamento',
      unlimited: 'Ilimitado',
      subscription: 'assinatura',
      trial: 'teste',
      mockTestsPerMonth: "10 Simulados por mês",
      unlimitedMockTests: "Simulados ilimitados",
      whatsIncludedInYour: "O que está incluído no seu {0}:",
      numberRemaining: '{0} restantes',
      unlimitedPracticeExercices: 'Exercícios práticos ilimitados',
      renewsOn: 'Renova em',
      subscriptionInfoWith: '{0} com análise detalhada',
      aiPowered: 'Feedback alimentado por IA',
      yoursubcriptionIsActive: 'Sua assinatura está ativa e pronta para uso',
      mockTestsWith: 'Simulados com análise detalhada',
      addAPayment: 'Adicione um método de pagamento para continuar após o término do seu teste',
      addPaymentMethod: 'Adicionar Método de Pagamento',
      cancelAnytime: 'Cancele a qualquer momento durante o período de teste sem custos',
      numberDaysRemaining: "{0} dias restantes",
      advancedAnalytics: 'Análises avançadas',
      plan: "Plano",
      goToDashboard: "Ir para o Painel",
      manageSubscription: 'Gerenciar Assinatura',
      planNamePlan: "{0} Plano",
      prioritySuport: 'Suporte prioritário',
      goToOnboarding: "Ir para Integração",
      personalized: "Planos de estudo personalizados",
      progressTracking: "Rastreamento de progresso e análises",
      manageYourSubscription: "Gerencie sua assinatura a qualquer momento nas configurações da sua conta"
    },
    StudyPlanPage: {
      AuthGuard: {
        yourPersonalized: "Seu Plano de Estudo Personalizado",
        aiPoweredAdaptive: "Caminho de aprendizado adaptativo alimentado por IA, adaptado aos seus objetivos",
        loadingYourStudy: "Carregando seu plano de estudo...",
        days: "dias",
        recommendedPace: "Ritmo recomendado",
        aiStudyAssistant: "Assistente de Estudo de IA",
        basedOnYour: "Com base em seu desempenho, recomendamos focar em",
        speakingExcellence: "Excelência na Fala",
        thisWeek: "esta semana. Você está fazendo um ótimo progresso!",
        youReMakingGreat: "Você está fazendo um ótimo progresso!",
        startTodayS: "Iniciar Sessão de Hoje",
        adjustPlan: "Ajustar Plano",
        yourLearning: "Seus Módulos de Aprendizado",
        score: "Pontuação:",
        continueModule: "Continuar Módulo",
        reviewModule: "Revisar Módulo",
        complete5Mock: "Complete 5 simulados",
        practice50: "Pratique 50 exercícios",
        study15Hours: "Estude 15 horas",
        achieve75: 'Conquiste 75+ pontos',
        pending: "Pendente",
        yourProgress: "Seu Progresso",
        weeklyPractice: "Prática Semanal",
        exercises: "exercícios",
        studyStreak: "Sequência de Estudos",
        day: "dia",
        inARow: "consecutivos",
        dayInARow: '{0} dias consecutivos',
        daysInARow: '{0} dias consecutivos',
        join2847Students: "Junte-se a 2.847 estudantes se preparando para o PTE",
        joinCommunity: "Juntar-se à Comunidade",
        targetAchieved: 'Meta alcançada!',
        targetNeeded: `Alvo: {0} (+{1} necessário)`,
        targetNumber: '(Alvo: {0})',
        numberDay: '{0}h/dia'
      },
      studyModules: [
        {
          title: "Habilidades Fundamentais",
          description:
            "Domine o básico do formato PTE e técnicas fundamentais de fala",
          duration: "2 semanas",
          difficulty: "iniciante",
          exerciseTypes: ["Leitura em Voz Alta", "Repetir Frases", "Responder Pergunta Curta"],
        },
        {
          title: "Excelência em Fala",
          description: "Pronúncia avançada, fluência e tarefas complexas de fala",
          duration: "3 semanas",
          difficulty: "intermediário",
          exerciseTypes: ["Descrever Imagem", "Recontar Palestra", "Leitura em Voz Alta"],
        },
        {
          title: "Domínio da Escrita",
          description: "Aperfeiçoe sua estrutura de ensaio e habilidades de resumo",
          duration: "2 semanas",
          difficulty: "intermediário",
          exerciseTypes: ["Ensaio", "Resumir Texto Escrito"],
        },
        {
          title: "Foco na Escuta",
          description:
            "Aprimore sua compreensão auditiva e habilidades de anotação",
          duration: "3 semanas",
          difficulty: "avançado",
          exerciseTypes: [
            "Resumir Texto Falado",
            "Preencher Lacunas",
            "Escrever por Ditado",
          ],
        },
        {
          title: "Estratégias de Leitura",
          description: "Técnicas de leitura dinâmica e análise de texto complexo",
          duration: "2 semanas",
          difficulty: "avançado",
          exerciseTypes: [
            "Reordenar Parágrafos",
            "Múltipla Escolha",
            "Preencher Lacunas",
          ]
        }
      ]
    },
    SuccessPage: {
      welcomeToPteasy: 'Bem-vindo ao PTEasy Premium!',
      yourSubscription: 'Sua assinatura foi ativada com sucesso. Agora você tem acesso a todos os recursos premium.',
      whatSNext: 'Qual o Próximo Passo?',
      takeYourFirst: 'Faça seu primeiro simulado para avaliar seu nível atual'
    },
    CheckoutPage: {
      completeYour: 'Complete Sua Compra',
      orderSummary: 'Resumo do Pedido',
      total: 'Total',
      youWonTBe: 'Você não será cobrado hoje. Cancele a qualquer momento durante seu teste.',
      paymentDetails: 'Detalhes do Pagamento',
      sevenDay: '7 Dias',
      placeholder: {
        johnDoe: "João da Silva",
      }
    },
    FeaturesPage: {
      everythingYouNeed: 'Tudo o que Você Precisa para',
      aceYourPteExam: 'Gabaritar Seu Exame PTE',
      aiPowered: 'Plataforma de preparação alimentada por IA com aprendizado adaptativo, em tempo real',
      scoringAnd: 'pontuação e análises abrangentes',
      practiceAll21Pte: 'Pratique todos os 21 tipos de questões do PTE com milhares de',
      practiceQuestions: 'questões de prática autênticas.',
      trackProgressWith: 'Acompanhe o progresso com insights detalhados e sugestões de melhoria personalizadas.',
      professional: 'Gravação profissional com cancelamento de ruído e análise de pronúncia.',
      realisticExam: 'Simulação de exame realista com pontuação completa e gerenciamento de tempo.',
      templatesGuides: 'Modelos, guias e estratégias de especialistas PTE e alunos com altas pontuações.',
      ourIntelligent: 'Nosso algoritmo inteligente analisa seu desempenho em tempo real, criando um caminho de aprendizado personalizado que evolui à medida que você melhora.',
      pteasyHelpedMe: '\"O PTEasy me ajudou a atingir minha pontuação alvo de 79 em apenas 3 semanas! A pontuação da IA é incrivelmente precisa.\"',
      theMockTestsAre: '\"Os simulados são exatamente como o exame real. Senti-me completamente preparado no dia do teste.\"',
      theAdaptive: '\"O recurso de aprendizado adaptativo me ajudou a focar nas minhas áreas fracas. Minha pontuação de fala melhorou em 15 pontos!\"',
      joinThousandsOf: 'Junte-se a milhares de candidatos bem-sucedidos que alcançaram suas pontuações desejadas com o PTEasy'
    },
    PrivacyPolicyPage: {
      pteasyIsNotIntended: 'PTEasy não é destinado a crianças menores de 13 anos. Não coletamos intencionalmente informações pessoais de crianças menores de 13 anos. Se você acredita que coletamos informações de uma criança menor de 13 anos, entre em contato conosco imediatamente em privacy@pteasy.com.',
      yourPrivacyIs: 'Sua privacidade é importante para nós. Saiba como protegemos seus dados.',
      lastUpdated: 'Última atualização: 15 de setembro de 2025',
      informationWe: 'Informações que Coletamos',
      howWeUse: 'Como Usamos as Informações',
      toExerciceTheseRights: 'Para exercer esses direitos, entre em contato conosco em privacy@pteasy.com.',
      dataSharing: 'Compartilhamento de Dados',
      dataSecurity: 'Segurança dos Dados',
      yourRights: 'Seus Direitos',
      nameAndContact: 'Nome e informações de contato (endereço de e-mail, número de telefone)',
      accountCredentials: 'Credenciais da conta (nome de usuário e senha criptografada)',
      profileInformation: 'Informações de perfil (pontuações alvo PTE, data do exame, idioma nativo)',
      paymentInformation: 'Informações de pagamento (processadas com segurança via Stripe)',
      sendYouUpdates: 'Enviar a você atualizações, newsletters e comunicações de marketing (com seu consentimento)',
      withTrustedThird: 'Com serviços de terceiros confiáveis que nos ajudam a operar nossa plataforma (por exemplo, Cloudinary para armazenamento de áudio, Stripe para pagamentos)',
      cookies: 'Cookies',
      childrenSPrivacy: 'Privacidade de Crianças',
      byUsingPteasy: 'Ao usar o PTEasy, você concorda com a coleta e o uso de informações de acordo com esta política. Se você não concordar com os termos desta política de privacidade, por favor, não acesse o site.',
      educational: 'Formação educacional e nível de proficiência em inglês',
      usageInformation: 'Informações de Uso',
      exerciseResponses: 'Respostas de exercícios e histórico de prática',
      mockTestResults: 'Resultados e pontuações de simulados',
      learningProgress: 'Progresso de aprendizado e análises de desempenho',
      deviceInformation: 'Informações do dispositivo e endereço IP',
      browserTypeAnd: 'Tipo de navegador e sistema operacional',
      howWeUseYour: 'Como Usamos Suas Informações',
      weUseThe: 'Usamos as informações coletadas para:',
      provideAnd: 'Fornecer e manter nossos serviços',
      personalizeYour: 'Personalizar sua experiência de aprendizado',
      processYour: 'Processar suas transações e assinaturas',
      analyzeAndImprove: 'Analisar e melhorar a eficácia de nossa plataforma',
      provideCustomer: 'Fornecer suporte ao cliente e responder a consultas',
      detectAndPrevent: 'Detectar e prevenir fraudes ou abusos',
      complyWithLegal: 'Cumprir com obrigações legais',
      informationSharing: 'Compartilhamento e Divulgação de Informações',
      weDoNotSellYour: 'Não vendemos suas informações pessoais. Podemos compartilhar suas informações apenas nas seguintes situações:',
      serviceProviders: 'Provedores de Serviço:',
      legalRequirements: 'Requisitos Legais:',
      whenRequiredBy: 'Quando exigido por lei ou para responder a processos legais',
      protectionOf: 'Proteção de Direitos:',
      toProtectOur: 'Para proteger nossos direitos, privacidade, segurança ou propriedade',
      businessTransfers: 'Transferências de Negócios:',
      inConnectionWith: 'Em conexão com uma fusão, aquisição ou venda de ativos',
      withYourConsent: 'Com Seu Consentimento:',
      whenYouExplicitly: 'Quando você concorda explicitamente em compartilhar suas informações',
      weImplement: 'Implementamos medidas de segurança apropriadas para proteger suas informações:',
      encryptionOf: 'Criptografia de dados sensíveis em trânsito e em repouso',
      secureHttps: 'Conexões HTTPS seguras',
      regularSecurity: 'Auditorias e atualizações de segurança regulares',
      limitedAccessTo: 'Acesso limitado a informações pessoais com base na necessidade de conhecimento',
      securePassword: 'Armazenamento seguro de senhas usando hashing padrão da indústria',
      howeverNoMethod: 'No entanto, nenhum método de transmissão pela Internet é 100% seguro. Embora nos esforcemos para proteger suas informações pessoais, não podemos garantir segurança absoluta.',
      yourRightsAnd: 'Seus Direitos e Escolhas',
      youHaveThe: 'Você tem os seguintes direitos em relação às suas informações pessoais:',
      access: 'Acesso:',
      requestACopyOf: 'Solicitar uma cópia de seus dados pessoais',
      correction: 'Correção:',
      updateOrCorrect: 'Atualizar ou corrigir informações imprecisas',
      deletion: 'Exclusão:',
      requestDeletionOf: 'Solicitar a exclusão de sua conta e dados pessoais',
      portability: 'Portabilidade:',
      receiveYourData: 'Receber seus dados em um formato estruturado',
      optOut: 'Opt-out:',
      unsubscribeFrom: 'Cancelar inscrição de comunicações de marketing',
      restriction: 'Restrição:',
      limitHowWeUse: 'Limitar como usamos suas informações',
      cookiesAnd: 'Cookies e Tecnologias de Rastreamento',
      weUseCookiesAnd: 'Usamos cookies e tecnologias de rastreamento semelhantes para aprimorar sua experiência. Estes incluem:',
      essentialCookies: 'Cookies Essenciais:',
      requiredFor: 'Necessários para a funcionalidade da plataforma',
      analyticsCookies: 'Cookies de Análise:',
      helpUsUnderstand: 'Ajude-nos a entender os padrões de uso',
      preferenceCookies: 'Cookies de Preferência:',
      rememberYour: 'Lembre-se de suas configurações e preferências',
      youCanControl: 'Você pode controlar os cookies através das configurações do seu navegador. Para mais detalhes, consulte nossa',
      internationalData: 'Transferências Internacionais de Dados',
      yourInformation: 'Suas informações podem ser transferidas e processadas em países diferentes do seu país de residência. Esses países podem ter leis de proteção de dados diferentes. Ao usar o PTEasy, você consente com tais transferências.',
      dataRetention: 'Retenção de Dados',
      weRetainYour: 'Retemos suas informações pessoais pelo tempo necessário para fornecer nossos serviços e cumprir obrigações legais. Quando você exclui sua conta, excluiremos ou anonimizaremos suas informações pessoais em até 30 dias, exceto quando a retenção for exigida por lei.',
      changesToThis: 'Alterações nesta Política',
      weMayUpdateThis: 'Podemos atualizar esta Política de Privacidade periodicamente. Notificaremos você sobre quaisquer alterações publicando a nova Política de Privacidade nesta página e atualizando a data de "Última atualização". Para alterações significativas, forneceremos aviso adicional via e-mail ou notificação da plataforma.',
      weOurOr: 'PTEasy ("nós," "nosso," ou "nós") está comprometido em proteger sua privacidade. Esta Política de Privacidade explica como coletamos, usamos, divulgamos e protegemos suas informações ao usar nosso site e serviços.',
      nativeLanguage: ', idioma nativo)'
    },
    ExamPrepPage: {
      AuthGuard: {
        priority: 'PRIORIDADE',
      },
      masterOurProvenApproach: 'Domine nossa abordagem comprovada: \n1) Aprenda o formato e os modelos, \n2) Pratique com exercícios cronometrados, \n3) Analise seu desempenho e adapte. Este método ajudou milhares a atingir suas pontuações alvo.'
    },
    PTEGuidePage: {
      listenToRead: 'Ouça/leia um cenário cotidiano (até 60 palavras)',
      about3minutes: 'cerca de 3 minutos',
      upTo60Words: 'até 60 palavras',
      these3tasks: 'Estas 3 tarefas = 50%+ da sua pontuação total',
      questionTypes: 'Tipos de Questões:',
      skipIfStuck: 'Pule se estiver preso - não respondido = zero pontos',
      scoreRange: 'Faixa de Pontuação',
      scoreRangesInterpretations: 'Faixas de Pontuação e Interpretações',
      within48Hours: 'Em 48 horas',
      validity: 'Validade:',
      acceptedBy: 'Aceito por mais de 3.000 instituições globalmente',
      speakingWritingSection: 'A seção de Fala e Escrita agora tem 65-75 tarefas (anteriormente 52-64)',
      format: 'Formato:',
      lastest2025updates: 'Últimas Atualizações de 2025 (Vigente a partir de 7 de agosto de 2025)',
      sectionNowHas: 'a seção agora tem 65-75 tarefas (anteriormente 52-64)',
      differentQuestionTypes: '22 tipos de questões diferentes (excluindo introdução pessoal)',
      rangesInterpretations: "Faixas e Interpretações",
      whatIsPte: 'O que é o PTE Academic?',
      listenToASpeaker: "Ouça uma discussão com 2-4 oradores (cerca de 3 minutos)",
      pteAcademicIsA: 'O PTE Academic é um teste de inglês totalmente baseado em computador que usa pontuação avançada de IA para avaliar a proficiência em inglês de falantes não nativos. É aceito por milhares de universidades, faculdades e governos em todo o mundo, inclusive para vistos australianos e neozelandeses.',
      whyChoosePte: 'Por Que Escolher o PTE Academic?',
      fastResults: 'Resultados rápidos - tipicamente em 48 horas',
      aiPowered: 'Pontuação alimentada por IA - imparcial e consistente',
      testAvailable: 'Teste disponível 365 dias por ano',
      validFor2Years: 'Válido por 2 anos a partir da data do teste',
      integratedSkills: 'Avaliação de habilidades integradas - reflete o uso da linguagem no mundo real',
      totalTest: 'Duração total do teste aumentada para ~2 horas e 15 minutos',
      enhancedScoring: 'Granularidade de pontuação aprimorada para melhor feedback',
      focusOn: 'Foco em habilidades de comunicação autênticas e do mundo real',
      tasks: 'Tarefas:',
      newCapital: 'NOVO',
      twoNewSpeakingTasks: 'Duas novas tarefas de fala adicionadas: Resumir Discussão em Grupo e Responder a uma Situação',
      normalNew: 'Novo',
      upperIntermediate: 'Intermediário Superior',
      multipleChoiceMultiple: 'Múltipla Escolha - Múltiplas Respostas',
      multipleChoiceSingle: 'Múltipla Escolha - Única',
      multipleChoiceSingleAnswer: 'Múltipla Escolha - Única resposta',
      writeFromDictation: 'Escrever por Ditado ★',
      highScoring: 'Alta pontuação!',
      pronunciationOral: 'Pronúncia, fluência oral e precisão do conteúdo. Fale com fluência em um ritmo ligeiramente mais rápido que sua velocidade natural, mas evite falar muito rápido.',
      newQuestionTypes: 'Novos Tipos de Questões',
      grammarVocabulary: 'Gramática, amplitude de vocabulário, discurso escrito, ortografia e coerência. A pontuação da redação agora usa uma escala de 0-6 para feedback mais detalhado.',
      reading: 'Compreensão de leitura em diferentes tipos de texto e contextos acadêmicos.',
      understanding: 'Compreensão do inglês falado em contextos acadêmicos e do mundo real, incluindo discussões em grupo com vários oradores.',
      keyScoringFacts: 'Fatos Chave sobre a Pontuação',
      fullyAutomated: 'Pontuação por IA totalmente automatizada - sem viés humano',
      integrated: 'Pontuação integrada - muitas tarefas contribuem para múltiplas habilidades',
      writeFrom: 'Escrever por Ditado - tarefa de maior pontuação!',
      description: 'Descrição',
      expert: 'Especialista',
      nativeLikeCommand: 'Domínio de inglês em nível nativo',
      advanced: 'Avançado',
      highProficiency: 'Alta proficiência para contextos acadêmicos e profissionais',
      goodCommand: 'Bom domínio - requisito típico universitário',
      intermediate: 'Intermediário',
      effective: 'Comunicação eficaz em contextos familiares',
      elementary: 'Elementar',
      basicEnglish: 'Inglês Básico',
      beginner: 'Iniciante',
      limitedAbilityTo: 'Capacidade limitada de se comunicar em inglês',
      SummarizeGroup: '1. Resumir Discussão em Grupo',
      task: 'Tarefa:',
      questionTypesNumber: 'Tipos de Questões ({0} total):',
      personalIntroduction: 'Introdução Pessoal (não pontuado)',
      response: 'Resposta:',
      deliverA2Minute: 'Apresentar um resumo oral de 2 minutos',
      skillsTested: 'Habilidades Testadas:',
      listening: 'Compreensão auditiva, seleção de conteúdo, fluência oral',
      respondToA: '2. Responder a uma Situação',
      speakANatural: 'Fale uma resposta natural e contextual por 40 segundos',
      spontaneous: 'Fala espontânea, registro apropriado, comunicação prática',
      useAppropriate: 'Use nível de formalidade apropriado, seja específico e relevante para a situação',
      timeManagement: 'Gerenciamento de Tempo',
      practiceWithTimed: 'Pratique com exercícios cronometrados',
      donTSpendToo: 'Não gaste muito tempo em questões de baixa pontuação',
      useTheErasable: 'Use a lousa apagável de forma eficaz',
      reviewAnswersIf: 'Revise as respostas se o tempo permitir',
      highScoringTasks: 'Foco em Tarefas de Alta Pontuação',
      keepMouth23: 'Mantenha a boca a 2-3 polegadas do microfone',
      naturalSpeech: 'A fala natural supera os modelos memorizados',
      multipleChoiceMultipleAnswers: 'Múltipla escolha - Respostas múltiplas',
      practice: 'Pratique respostas espontâneas para novas tarefas',
      writingStrategies: 'Estratégias de Escrita',
      multipleChoice: "Múltipla escolha - Respostas múltiplas",
      summarizeOne: 'Resumir: UMA frase, 30-75 palavras',
      useComplex: 'Use frases complexas para melhores pontuações',
      alwaysLeave23: 'Sempre reserve 2-3 minutos para revisar',
      payCloseAttention: 'Preste muita atenção à ortografia, pois você perde pontos por palavras escritas incorretamente',
      criticalTips: 'Dicas Críticas',
      audioPlaysOnly: 'O áudio toca apenas UMA VEZ - mantenha o foco',
      bewareNegative: 'Cuidado com a pontuação negativa em MCQ múltiplos',
      noteTakingIs: 'Fazer anotações é essencial para a compreensão auditiva',
      preparationTimeline: 'Cronograma de Preparação',
      twentyTwoDifferentTypes: '22 tipos diferentes',
      oneHundredComputerBased: '100% Baseado em Computador',
      twoNew: 'Duas novas',
      tasksAdded: 'tarefas adicionadas:',
      minutes: 'minutos',
      notScored: '(não pontuado)',
      negativeMarking: 'Pontuação negativa se aplica a Múltipla Escolha (Múltiplas Respostas)',
      writeFromDictationhasTheHighest: 'Escrever por Ditado tem o maior peso na pontuação do teste',
      upper: 'Superior',
      takeNotesOnEach: 'Faça anotações sobre os pontos principais de cada orador, identifique acordos/desacordos',
      readAloudContributesTo: 'Leitura em Voz Alta - contribui para Fala e Leitura',
      highWeightIn: 'Repetir Frase - alto peso em Fala e Compreensão Auditiva',
      donTStopTo: 'não pare para corrigir',
      aimFor250: 'Redação: 200-300 palavras (objetive 250)',
      speakingTips: 'Dicas de Fala (2025)',
      fluencyAccuracyDont: 'Fluência > Precisão - Não pare para corrigir'
    },
    TestDescribeImagePage: {
      thisIsATestPage: 'Esta é uma página de teste para o componente de exercício Descrever Imagem com dados simulados'
    },
    BlogPage: {
      read: 'ler'
    },
    RetellLectureTemplatePage: {
      howToUseThis: "Como Usar Este Modelo",
      retellLecture: 'Modelo de Recontar Palestra para PTE',
      masterTheRetell: 'Domine a tarefa Recontar Palestra com exercícios ilimitados e feedback alimentado por IA',
      fiveMinRead: '5 min de leitura',
      minRead: 'min de leitura',
      theEssential: 'O Modelo Essencial',
      mainTopic: 'Tópico Principal:',
      identifyThe: 'Identifique o tema central na primeira frase',
      keyPoints: 'Pontos-Chave:',
      include34Main: 'Inclua 3-4 pontos principais da palestra',
      transitions: 'Transições:',
      useConnecting: 'Use palavras de conexão para ligar seus pontos suavemente',
      conclusion: 'Conclusão:',
      summarizeTheMain: 'Resuma a mensagem principal ou o resultado',
      timeManagement: 'Gerenciamento de Tempo:',
      aimToSpeakFor: 'Procure falar por 35-40 segundos',
      alternative: 'Modelos Alternativos',
      speakingForLess: 'Falar por menos de 30 segundos',
      includingToo: 'Incluir muitos detalhes menores',
      usingPresent: 'Usar presente em vez de passado',
      missingTheMain: 'Perder o tópico principal ou a conclusão',
      speakingTooFast: 'Falar muito rápido ou muito devagar',
      scoringCriteria: 'Critérios de Pontuação',
      accurateMain: 'Identificação precisa do tópico principal',
      keyPointsFrom: 'Pontos-chave da palestra',
      logicalSequence: 'Sequência lógica de ideias',
      smoothNatural: 'Entrega suave e natural',
      appropriatePace: 'Ritmo apropriado',
      minimal: 'Mínimas hesitações',
      clearArticulation: 'Articulação clara',
      topic: "Tópico:",
      correctWord: 'Acentuação correta das palavras',
      naturalIntonation: 'Entonação natural',
      perfectStructure: 'Estrutura perfeita para descrever imagens em 40 segundos',
      structured: 'Modelos estruturados para todos os tipos de redação',
      oneSentence: 'Técnicas de resumo de uma frase'
    },
    EssayWritingTemplatesPage: {
      youCanMakeUp: "Você pode inventar citações, estatísticas e exemplos! O PTE não verifica fatos. Apenas certifique-se de que sejam relevantes e apoiem seu argumento.",
      commonPrompt: "Prompt comum:",
      topic: "Tópico:",
      writingLessThan: "Escrever menos de 200 ou mais de 300 palavras",
      notAddressing: "Não abordar a pergunta diretamente",
      usingInformal: "Usar linguagem informal ou contrações",
      forgettingTo: "Esquecer de incluir exemplos",
      havingOnlyOne: "Ter apenas um argumento principal",
      notProofreading: "Não revisar a gramática e a ortografia",
      writingMemorized: "Escrever redações memorizadas sem adaptar ao tópico",
      weakOrMissing: "Conclusão fraca ou ausente",
      analyzeQuestion: "Analisar pergunta, fazer brainstorming de ideias, escolher modelo",
      writeEssay: "Escrever redação seguindo a estrutura do modelo",
      proofreadFor: "Revisar gramática, ortografia, contagem de palavras",
      masterOneSentence: "Domine resumos de uma frase"
    },
    DescribeImageTemplatePage: {
      opening: 'Abertura:',
      identifyTheImage: 'Identifique o tipo de imagem e o tópico principal',
      components: 'Componentes:',
      describeWhatThe: 'Descreva o que a imagem contém',
      keyData: 'Dados Chave:',
      mentionSpecific: 'Mencione detalhes específicos, números ou tendências',
      summarizeTheMain: 'Resuma a principal descoberta ou mensagem',
      notMentioning: 'Não mencionar números ou dados específicos',
      describingEvery: 'Descrever cada pequeno detalhe em vez das características principais',
      forgettingTo: 'Esquecer de declarar uma conclusão',
      usingVague: 'Usar linguagem vaga em vez de descrições precisas',
      notIdentifying: 'Não identificar o tipo de imagem no início',
      poorTime: 'Má gestão do tempo durante a preparação',
      identifyImageType: 'Identifique o tipo de imagem e o tópico principal',
      noteKeyData: 'Anote os pontos de dados e tendências principais',
      planYourResponse: 'Planeje a estrutura da sua resposta',
      deliverStructured: 'Entregue uma resposta estruturada com confiança'
    },
    PracticePage: {
      AuthGuard: {
        practiceCenter: 'Centro de Prática',
        masterYourPte: 'Domine suas habilidades PTE com {0} tipos de exercícios em {1} áreas de habilidade',
        totalExercises: 'Total de Exercícios',
        found: 'Encontrado',
        skill: "habilidade",
        skillAreas: 'Áreas de habilidade',
        matching: 'correspondendo a \"',
        zeroExercises: '0 exercícios concluídos',
        exercisesCompleted: 'exercícios concluídos',
        foundSkill: 'Encontradas {0} habilidades correspondentes',
        foundSkills: 'Encontradas {0} habilidades correspondentes'

      }
    },
    SaveExitDialog: {
      saveAndExitTest: 'Salvar e Sair do Teste?',
      doYouWantToSave: 'Você deseja salvar seu progresso antes de sair? Você pode retomar o teste mais tarde de onde parou.',
      saveProgressAnd: 'Salvar Progresso e Sair',
      exitWithoutSaving: 'Sair Sem Salvar',
      yourProgressWill: 'Seu progresso será salvo automaticamente e você poderá retomar este teste nos próximos 7 dias.'
    },
    ResumePausedSessionDialog: {
      resumePrevious: 'Retomar Sessão Anterior?',
      youHaveAPaused: 'Você tem uma sessão de simulado pausada. Gostaria de continuar de onde parou ou iniciar um novo teste?',
      pausedSession: 'Detalhes da Sessão Pausada:',
      started: 'Iniciada:',
      progressExercisesCompleted: 'Progresso: {0} de {1} exercícios concluídos',
      progress: 'Progresso:',
      complete: '% completo',
      continuePrevious: 'Continuar Sessão Anterior',
      startNewTest: 'Iniciar Novo Teste',
      startingANewTest: 'Iniciar um novo teste abandonará sua sessão anterior. Seu progresso anterior será salvo, mas não poderá ser retomado.'
    },
    ExerciseListPanel: {
      checkBackLater: 'Volte mais tarde para novo conteúdo',
      loadingMore: 'Carregando mais exercícios...',
      youVeReachedThe: 'Você chegou ao fim da lista!'
    },
    ExerciseInstructions: {
      tipsForSuccess: 'Dicas para o Sucesso:'
    },
    BaseExercise: {
      backToExercises: 'Voltar para os Exercícios',
      exercise: 'Exercício'
    },
    Essay: {
      writeEssay: 'Escrever Redação',
      wordCount: 'Contagem de palavras:'
    },
    WriteFromDictation: {
      audioUrl: 'URL do Áudio:'
    },
    AIHelper: {
      answerExplanations: 'Explicações da Resposta',
      performanceAnalysis: 'Análise de Desempenho',
      learningTips: 'Dicas de Aprendizado',
      detailedAnswer: 'Explicações Detalhadas da Resposta',
      correctSelection: 'Seleção Correta',
      incorrect: '✗ Seleção Incorreta',
      missedCorrect: 'Resposta Correta Perdida',
      notSelected: 'Não Selecionado',
      aiFeedback: 'Feedback da IA',
      keyInsights: 'Principais Insights',
      perfectScoreYou: 'Pontuação perfeita! Você identificou todas as respostas corretas sem erros.',
      youSelected: 'Você selecionou',
      incorrectOption: 'opção incorreta',
      reviewWhyThese: 'Revise por que estas não foram suportadas pela passagem.',
      youMissed: 'Você perdeu',
      correctAnswer: 'resposta correta',
      practice: '. Pratique a identificação de informações-chave na passagem.',
      youCorrectly: 'Você identificou corretamente',
      outOf: 'de',
      correctAnswers: 'respostas corretas.',
      personalized: 'Dicas de Aprendizado Personalizadas',
      readEachOption: 'Leia cada opção independentemente - não as compare entre si',
      lookForDirect: 'Procure por evidências diretas na passagem para cada opção',
      avoidOptionsThat: 'Evite opções que usam linguagem extrema não encontrada na passagem',
      checkIfTheOption: 'Verifique se a opção contradiz alguma informação na passagem'
    },
    TextPassageSection: {
      noPassageText: 'Nenhum texto de passagem disponível'
    },
    SubmissionFeedback: {
      percentage: ') : porcentagem',
      answerReview: 'Revisão da Resposta:',
      corrections: "Correções:",
      feedback: 'Feedback:',
      tryAgain: 'Tentar Novamente',
      goodJob: 'Bom Trabalho!',
      excellentPerformance: "Desempenho Excelente!"
    },
    exerciseLimitModal: {
      upgradeToPremiumForUnlimitedAI: 'Faça upgrade para Premium para pontuação por IA ilimitada e feedback detalhado.',
      upgradeNowToContinue: 'Faça upgrade agora para continuar com pontuação por IA ilimitada.',
      aiScoringLimitApproaching: 'Limite de Pontuação por IA se Aproximando',
      aiScoringLimitReached: 'Limite de Pontuação por IA Atingido',
      youHave: "Você tem {0} este mês.",
      remaining: "restantes",
      unlimitedAIScoredExercises: "exercícios com pontuação de IA ilimitados",
      aiScoredExercise: "{0} exercício com pontuação de IA restante",
      aiScoredExercises: "{0} exercícios com pontuação de IA restantes",
      thisMonth: "este mês.",
      youVeReachedYourMonthly: "Você atingiu seu limite mensal de",
      tenAiScoredExercises: "10 exercícios com pontuação por IA",
      continueInPracticeMode: "Continuar no Modo Prática",
      keepPracticingWithoutAi: "Continue praticando sem pontuação por IA. Suas respostas serão salvas, mas você não receberá feedback e pontuações detalhadas impulsionadas por IA.",
      viewPremiumPlans: "Ver Planos Premium",
      continueForNow: 'Continuar por enquanto',
      maybeLater: 'Talvez mais tarde'
    },
    Pricing: {
      chooseYourPteasy: 'Escolha Seu Plano PTEasy',
      joinThousandsOf: 'Junte-se a milhares de estudantes que atingiram suas pontuações alvo com nossa',
      aiPoweredPlatform: 'plataforma alimentada por IA',
      yourCurrentPlan: 'Seu Plano Atual',
      successRate: '95% Taxa de Sucesso',
      securePayments: 'Pagamentos Seguros',
      daysFreeTrial: 'Teste gratuito de {0} dias',
      dayMoneyBack: 'Garantia de devolução do dinheiro em {0} dias',
      allPlansInclude: 'Todos os planos incluem:',
      practiceAnywhere: 'Pratique em qualquer lugar, a qualquer hora em qualquer dispositivo',
      yourDataIs: 'Seus dados são protegidos com segurança de nível empresarial',
      progressTracking: 'Rastreamento de Progresso',
      monitorYour: 'Monitore sua melhoria com análises detalhadas',
      authenticContent: 'Conteúdo Autêntico',
      practiceWithReal: 'Pratique com questões reais do exame PTE',
      detailedComparison: 'comparação detalhada',
      tenThousandStudents: 'Mais de 10.000 Estudantes',
      mobileDesktopAccess: 'Acesso Móvel e Desktop',
      securePrivate: 'Seguro e Privado',
      unableToStartCheckout: 'Incapaz de iniciar o checkout. Por favor, tente novamente mais tarde.',
      pricingPlans: [
        {
          description: 'Perfeito para começar',
          features: [
            'Exercícios ilimitados de Listening e Reading',
            '5 exercícios de Speaking e Writing por dia',
            'Feedback de pontuação básico'
          ],
          limitations: [
            'Feedback alimentado por IA',
            'Prática ilimitada',
            'Simulados'
          ],
          buttonText: 'Comece Grátis'
        },
        {
          description: 'Melhor custo-benefício para alunos sérios',
          features: [
            'Exercícios práticos ilimitados',
            'Análise de fala alimentada por IA',
            'Previsões de pontuação detalhadas',
            'Simulados (10 por mês)',
            'Rastreamento de progresso avançado',
            'Suporte por e-mail prioritário',
            'Identificação de pontos fracos'
          ],
          buttonText: 'Iniciar Premium'
        },
        {
          description: 'Para preparação intensiva',
          subheader: 'Tudo no Premium, mais:',
          features: [
            'Simulados ilimitados',
            'Plano de estudo pessoal',
            'Suporte de chat com tutor de IA',
            'Suporte prioritário 24/7',
            'Análises avançadas'
          ],
          buttonText: 'Escolha Pro'
        }
      ],
      allFeatures: [
        {
          name: 'Acesso a Exercícios',
          free: 'Acesso Limitado',
          premium: 'Ilimitado',
          pro: 'Ilimitado',
        },
        {
          name: 'Simulados',
          free: '—',
          premium: '10/mês',
          pro: 'Ilimitado'
        },
        {
          name: 'Pontuação por IA',
          free: 'Básico',
          premium: 'Avançado',
          pro: 'Avançado'
        },
        {
          name: 'Análises de Progresso',
          free: '—',
          premium: 'Avançado',
          pro: 'Avançado'
        },
        {
          name: 'Planos de Estudo',
          free: '—',
          premium: '—',
          pro: 'Personalizado',
        },
        {
          name: 'Suporte',
          free: '—',
          premium: 'E-mail Prioritário',
          pro: 'Prioritário 24/7'
        },
        {
          name: 'Chat com Tutor de IA',
          free: '—',
          premium: '—',
          pro: '✓'
        }
      ]
    },
    Features: {
      whyChoosePteasy: 'Por Que Escolher o PTEasy?',
      everythingYouNeed: 'Tudo o que você precisa para gabaritar seu exame PTE com confiança'
    },
    FAQ: {
      everythingYouNeed: 'Tudo o que você precisa saber sobre o PTEasy'
    },
    HeroBanner: {
      ptePracticeApp: 'Aplicativo de Prática PTE nº 1',
      joinStudentsWhoAchieved: 'Junte-se a milhares de estudantes usando o PTEasy para praticar questões de Speaking, Writing, Reading e Listening, fazer simulados realistas e obter pontuação alimentada por IA com feedback detalhado para dominar cada seção do exame',
      noCreditCardRequired: 'Não é necessário cartão de crédito • Teste gratuito de 30 dias',
      trustedByStudentsWorldwide: 'Confiado por milhares de estudantes em todo o mundo',
      masterPteIn: 'Alcance seus objetivos PTE',
      thirtyDays: 'mais rápido!',
      achieveYourPte: 'Alcance seus objetivos PTE mais rápido!',
      joinThousandsOf: 'Junte-se a milhares de estudantes usando o PTEasy para praticar questões de Speaking, Writing, Reading e Listening, fazer simulados realistas e obter pontuação alimentada por IA com feedback detalhado para dominar cada seção do exame',
      joinForFree: 'Pratique agora gratuitamente',
      myProgress: 'Meu Progresso',
      overallScore: 'Projeção de Pontuação Geral:',
      practiceQuestion: 'Questão de Prática: Repetir Frase',
      recordNow: 'Gravar Agora',
      startYourFree: 'Comece Seu Teste Gratuito',
      noCreditCard: 'Não é necessário cartão de crédito • Teste gratuito de 30 dias',
      studentsAlready: 'alunos já se juntaram',
      happyStudents: 'Alunos Satisfeitos',
      passRate: 'Taxa de Aprovação',
      appRating: 'Avaliação do Aplicativo',
      instantResults: 'Resultados Instantâneos',
      expertApproved: 'Aprovado por Especialistas',
      questionsAnswered: 'Questões Respondidas',
      securePrivate: 'Seguro e Privado',
      questionsToPracticeNumber: '1000+',
      questionsToPracticeLabel: 'Questões para Praticar',
      instantText: 'Instantâneo',
      aiScoringFeedback: 'Pontuação e Feedback de IA',
      oneGoalNumber: '1 Objetivo',
      yourSuccessLabel: 'Seu Sucesso',
    },
    navbar: {
      homepage: 'Página Inicial',
      ptePractice: 'Prática PTE',
      mockTest: 'Simulado',
      pricing: 'Preços',
      pteGuide: 'Guia PTE',
      blog: 'Blog',
      resources: 'Recursos',
      dashboard: 'Painel',
      profile: 'Perfil',
      logout: 'Sair',
      signUp: 'Cadastre-se'
    },
    Footer: {
      stayUpdated: 'Mantenha-se Atualizado',
      getTheLatestPte: 'Receba as últimas dicas, questões práticas e atualizações do PTE em sua caixa de entrada.',
      pt: 'PT',
      en: 'EN',
      theMostAdvanced: 'A plataforma mais avançada alimentada por IA para preparação para o PTE Academic. Junte-se a milhares de estudantes que atingem suas pontuações alvo.',
      product: 'Produto',
      faq: 'FAQ',
      contactUs: 'Fale Conosco',
      pteasyAllRights: 'PTEasy. Todos os direitos reservados.',
      aiPowered: 'Alimentado por IA',
      trustedBy: 'Aprovado por milhares de estudantes',
      legal: 'Jurídico',
    },
    ForgotPasswordForm: {
      sendResetEmail: '\'Enviar E-mail de Redefinição\''
    },
    ResetPasswordForm: {
      resetPassword: '\'Redefinir Senha\''
    },
    SubscriptionUpgradeModal: {
      youVeUsedAll: 'Você usou todos',
      ofYour: 'dos seus',
      mockTestsThis: 'simulados este mês.',
      upgradeToContinue: 'Faça upgrade para continuar praticando com mais simulados.',
      specialOffer: 'Oferta Especial:',
      startWithA14Day: 'Comece o plano premium com um teste gratuito de {0} dias - Cancele a qualquer momento!',
      mostPopular: 'MAIS POPULAR',
      start14DaysFree: 'Começar {0} Dias Grátis',
      getCertifiedScores: 'Obtenha pontuações certificadas',
      allPlansInclude: 'Todos os planos incluem acesso a exercícios práticos individuais',
      maybeLater: 'Talvez mais tarde',
      youveUsedAllOfYour: "Você usou todos os seus {0} de {1} simulados este mês.",
      thenMonthAfterTrial: "Então {0}/mês após o teste",
      planPriceMonth: '{0}/mês',
      uogradeTo: 'Atualizar para {0}',
      unlimited: 'Ilimitado',
      yourCurrentPlan: "Seu plano atual não inclui acesso a {0}. Faça upgrade para desbloquear este recurso.",
      yourCurrentPlanCustom: "Seu plano {0} não inclui acesso a {1}. Faça upgrade para o Pro para desbloquear este recurso.",
      freeAccountsDontHaveWithTrial: "Contas gratuitas não têm acesso a {0}. Escolha um plano para desbloquear este recurso e começar seu teste gratuito de {1} dias!",
      freeAccountsDontHave: "Seu plano atual não inclui acesso a {0}. Atualize para desbloquear este recurso.",
      planMockTestsMonth: "{0}/mês",
      unlockUnlimited: "Desbloqueie exercícios ilimitados com pontuação por IA, testes simulados e recursos premium.",
      upgradeToUnlock: "Atualize para desbloquear todos os recursos premium!",
      start14DayTrial: "Comece hoje mesmo seu teste gratuito de {0} dias!",
      upgradeTo: "Atualizar para {0}",
      subscribeTo: "Assinar {0}",
      plans: [
        [
          'Exercícios práticos ilimitados',
          '10 simulados por mês',
          'Análise de fala alimentada por IA',
          'Previsões de pontuação detalhadas',
          'Rastreamento de progresso e análises',
          'Suporte por e-mail prioritário'
        ],
        [
          'Tudo no Premium',
          'Simulados ilimitados',
          'Plano de estudo pessoal',
          'Suporte de chat com tutor de IA',
          'Feedback de especialistas em fala',
          'Suporte prioritário 24/7'
        ]
      ]
    },
    StepIllustration: {
      helpUsPersonalize: 'Ajude-nos a personalizar sua experiência',
      yourCurrentLevel: 'Seu nível atual',
      setYourTargetDate: 'Defina sua data alvo',
      aimHigh: 'Mire alto!',
      readyToGo: 'Pronto para começar!'
    },
    OnboardingSidebar: {
      numberOfNumber: '{0} de {1}',
      welcomeToPteasy: 'Bem-vindo ao PTEasy!',
      letSPersonalize: 'Vamos personalizar sua experiência de aprendizado',
      letsGetStarted: "Vamos começar! 🚀",
      youredoingGreat: "Você está indo muito bem! Continue assim! 💪",
      almostThere: "Quase lá! Apenas revise e confirme! 🎉"
    },
    GenderStep: {
      howDoYouIdentify: 'Como você se identifica?',
      thisHelpsUs: 'Isso nos ajuda a personalizar sua experiência de aprendizado'
    },
    CompletionStep: {
      youReAllSet: 'Tudo pronto!',
      weVeCreatedA: 'Criamos um plano de estudo personalizado para você',
      daysToPrepare: '{0} dias para preparar',
      notScheduledYet: 'Não agendado ainda',
      notSet: 'Não definido',
      flexibleStudy: 'Cronograma de estudo flexível',
      targetScores: 'Pontuações Alvo',
      overall: 'Geral:',
      speaking: 'Fala:',
      writing: 'Escrita:',
      reading: 'Leitura:',
      listening: 'Compreensão Auditiva:',
      perDay: 'por dia',
      startLearning: 'Começar a Aprender'
    },
    NativeLanguageStep: {
      whatIsYourNative: 'Qual é o seu idioma nativo?',
      hintsAnd: 'Dicas e traduções aparecerão neste idioma',
      wouldYouLikeTo: 'Você gostaria de usar o PTEasy em inglês ou mudar para português?',
      placeholders: {
        searchLanguage: 'Pesquisar idiomas...'
      },
      languages: [
        "Português (Brasil)",
        "Espanhol",
        "Italiano",
        "Francês",
        "Alemão",
        "Chinês (Mandarim)",
        "Japonês",
        "Coreano",
        "Árabe",
        "Hindi",
        "Turco",
        "Russo",
        "Tailandês",
        "Vietnamita",
        "Outro",
      ],
      aliasLanguages: [
        "Português",
        "Espanhol",
        "Italiano",
        "Francês",
        "Alemão",
        "Chinês",
        "Japonês",
        "Coreano",
        "Árabe",
        "Hindi",
        "Turco",
        "Russo",
        "Tailandês",
        "Vietnamita",
        "Outro",
      ],
    },
    ProficiencyLevelStep: {
      whatSYourCurrent: 'Qual é o seu nível atual de inglês?',
      thisHelpsUs: 'Isso nos ajuda a criar o plano de estudo perfeito para você'
    },
    StudyPreferencesStep: {
      personalizeYour: 'Personalize seu plano de estudo',
      helpUsCreateThe: 'Ajude-nos a criar o cronograma de aprendizado perfeito para você',
      howMuchTimeCan: 'Quanto tempo você pode estudar diariamente?',
      whatAreasDoYou: 'Em quais áreas você quer focar?',
      selectAllThat: 'Selecione todas que se aplicam',
      whenShouldWe: 'Quando devemos lembrá-lo de estudar?',
      timeOptions: [
        '15-30 minutos',
        '30-60 minutos',
        '1-2 horas',
        'Mais de 2 horas',
      ],
      focusAreaOptions: [
        'Fala',
        'Escrita',
        'Leitura',
        'Compreensão Auditiva',
        'Vocabulário',
        'Gramática',
        'Pronúncia',
        'Gerenciamento de Tempo',
      ],
      reminderTimeOptions: [
        'Manhã (8:00 AM)',
        'Meio-dia (12:00 PM)',
        'Tarde (3:00 PM)',
        'Noite (6:00 PM)',
        'Madrugada (9:00 PM)',
        'Sem lembretes',
      ]
    },
    ExamDateStep: {
      whenIsYourPte: 'Quando é o seu exame PTE?',
      weLlCreateA: 'Criaremos um cronograma de estudo personalizado com base na data do seu exame',
      selectYourExam: 'Selecione a data do seu exame',
      iHavenTScheduled: 'Ainda não agendei meu exame',
      noWorriesWeLl: 'Não se preocupe! Ajudaremos você a se preparar no seu próprio ritmo. Você pode atualizar a data do seu exame a qualquer momento nas configurações do seu perfil.',
      or: "OU",
      YouHaveLessThan: "⚡ Você tem menos de uma semana! Vamos focar em práticas de alto impacto.",
      goodTimingWellCreateAn: "📚 Ótimo momento! Criaremos um plano de estudo intensivo para você.",
      perfectYouHaveEnoughTime: "🎯 Perfeito! Você tem tempo suficiente para uma preparação abrangente.",
      excellentWellBuildAThorough: "🌟 Excelente! Criaremos um cronograma de estudos completo e bem ritmado."
    },
    TargetScoreStep: {
      whatAreYour: 'Quais são suas pontuações alvo?',
      setYourPteScore: 'Defina suas metas de pontuação PTE para cada seção',
      commonTargetScores: 'Pontuações alvo comuns',
      customizeYour: 'Personalize suas pontuações alvo',
      presetScores: [
        {
          name: 'Inglês Profissional',
          description: 'Para fins vocacionais'
        },
        {
          name: 'Inglês Competente',
          description: 'Para fins de estudo e trabalho'
        },
        {
          name: 'Inglês Proficiente',
          description: 'Para registro profissional'
        },
        {
          name: 'Inglês Superior',
          description: 'Para fins acadêmicos avançados'
        },
      ],
      skillAreas: [
        'Compreensão Auditiva',
        'Leitura',
        'Fala',
        'Escrita',
        'Geral',
      ],
    },
    Dashboard: {
      completion: '% de conclusão',
      growth: '% de crescimento'
    },
    OnboardingPage: {
      AuthGuard: {
        enter: "Entrar",
        continue: "Continuar",
        esc: "Esc"
      }
    },
    TermsOfServicePage: {
      provideAccurate: "Fornecer informações de registro precisas e completas"
    },
    DescribeImageExercisePage: {
      of33: "de 33",
      recordingIn: "Gravando em"
    },
    ReadAloudTransitionPage: {
      of2: "2 de 2",
      pleaseClick: "Por favor, clique",
      next: "\"próximo\"",
      toProceedToThe: "para prosseguir para a próxima seção."
    },
    AnswerShortQuestionPage: {
      of33: "de 33"
    },
    EssayPage: {
      of1: "de 1",
      paste: "Colar"
    },
    HighlightIncorrectWordsPage: {
      noExerciseData: "Nenhum dado de exercício disponível",
      audioPlayer: "Reprodutor de Áudio",
      playing: "Reproduzindo",
      beginningIn: "Começando em"
    },
    ListeningMultipleChoiceSinglePage: {
      noExerciseData: "Nenhum dado de exercício disponível",
      audioPlayer: "Reprodutor de Áudio",
      playing: "Reproduzindo",
      beginningIn: "Começando em"
    },
    AccountPage: {
      AuthGuard: {
        memberSince: "Membro desde"
      }
    },
    dailyTips: [
      // Speaking Tips
      {
        category: 'fala',
        title: 'Mantenha o Ritmo ao Falar',
        content: 'Mantenha um ritmo constante no Read Aloud (Leitura em Voz Alta). Muito rápido causa erros, muito lento afeta as pontuações de fluência.',
        priority: 'alta'
      },
      {
        category: 'fala',
        title: 'Use Modelos para Descrever Imagem',
        content: 'Comece com "Esta imagem mostra..." e siga com as principais características, depois detalhes específicos.',
        priority: 'alta'
      },
      {
        category: 'fala',
        title: 'Estratégia para Repetir Frases',
        content: 'Concentre-se no significado, não nas palavras individuais. Seu cérebro se lembra melhor de conceitos do que de sequências de palavras.',
        priority: 'média'
      },
      {
        category: 'fala',
        title: 'A Distância do Microfone Importa',
        content: 'Mantenha a boca a 5-8 centímetros do microfone. Muito perto causa distorção, muito longe reduz a clareza.',
        priority: 'alta'
      },
      {
        category: 'fala',
        title: 'Responda Perguntas Curtas Rapidamente',
        content: 'Dê respostas de uma ou duas palavras imediatamente. Não pense demais - o primeiro instinto geralmente está correto.',
        priority: 'média'
      },

      // Writing Tips
      {
        category: 'escrita',
        title: 'A Estrutura do Ensaio é Fundamental',
        content: 'Sempre use: Introdução (2-3 frases), Desenvolvimento (2 parágrafos), Conclusão (1-2 frases).',
        priority: 'alta'
      },
      {
        category: 'escrita',
        title: 'Fórmula para Resumir Texto Escrito',
        content: 'Uma frase, 30-40 palavras, inclua ideia principal + pontos de apoio. Use conectores como "embora" ou "enquanto".',
        priority: 'alta'
      },
      {
        category: 'escrita',
        title: 'Frases Complexas Pontuam Mais',
        content: 'Use frases compostas e complexas com pontuação adequada para melhores pontuações de gramática.',
        priority: 'média'
      },
      {
        category: 'escrita',
        title: 'A Contagem de Palavras Importa',
        content: 'Ensaio: almeje 220-250 palavras. Resumir: exatamente uma frase com menos de 75 palavras.',
        priority: 'alta'
      },
      {
        category: 'escrita',
        title: 'Gestão do Tempo na Escrita',
        content: 'Ensaio: 2 min planejamento, 15 min escrita, 3 min revisão. Nunca pule a revisão!',
        priority: 'média'
      },

      // Reading Tips
      {
        category: 'leitura',
        title: 'Passe o Olhar Primeiro, Leia Depois',
        content: 'Escaneie rapidamente a passagem inteira antes de ler as perguntas. O contexto ajuda a responder mais rápido.',
        priority: 'alta'
      },
      {
        category: 'leitura',
        title: 'Truque para Reordenar Parágrafos',
        content: 'Encontre primeiro a frase de abertura independente (sem pronomes ou referências a outras ideias).',
        priority: 'alta'
      },
      {
        category: 'leitura',
        title: 'Palavras-Chave em Preencher Lacunas',
        content: 'Olhe as palavras antes e depois da lacuna. A gramática (a/an, singular/plural) geralmente dá a resposta.',
        priority: 'média'
      },
      {
        category: 'leitura',
        title: 'Estratégia de Múltipla Escolha',
        content: 'Elimine primeiro as respostas obviamente erradas. Se estiver em dúvida entre duas, escolha a mais específica.',
        priority: 'média'
      },
      {
        category: 'leitura',
        title: 'Tempo Por Pergunta',
        content: 'Múltipla escolha de resposta única: 1.5 minutos no máximo. Múltipla escolha de múltiplas respostas: 2 minutos no máximo. Avance se estiver travado!',
        priority: 'alta'
      },

      // Listening Tips
      {
        category: 'escuta',
        title: 'Fazer Anotações é Crucial',
        content: 'Escreva palavras-chave, não frases completas. Concentre-se em: números, nomes, ideias principais, contrastes.',
        priority: 'alta'
      },
      {
        category: 'escuta',
        title: 'Ouro em Escrever por Ditado',
        content: 'Esta tarefa tem o maior peso na pontuação. Escreva cada palavra que ouvir, mesmo que esteja inseguro sobre a ortografia.',
        priority: 'alta'
      },
      {
        category: 'escuta',
        title: 'Foco em Destacar Palavras Incorretas',
        content: 'Leia a transcrição antes do áudio começar. Marque palavras que soam diferentes, não erros de gramática.',
        priority: 'média'
      },
      {
        category: 'escuta',
        title: 'Padrão de Selecionar Palavra Faltante',
        content: 'O tom geralmente muda antes do bipe. Um tom ascendente frequentemente indica uma pergunta.',
        priority: 'média'
      },
      {
        category: 'escuta',
        title: 'O Áudio Toca Apenas Uma Vez',
        content: 'Mantenha o foco! Você não pode repetir. Se perder algo, arrisque a melhor resposta e avance.',
        priority: 'alta'
      },
      // General Strategy Tips
      {
        category: 'geral',
        title: 'Testes Simulados Aumentam a Resistência',
        content: 'Faça um teste simulado completo semanalmente. O formato de 3 horas exige resistência mental.',
        priority: 'alta'
      },
      {
        category: 'geral',
        title: 'Pontue Mais em Menos Tempo',
        content: 'Concentre-se nas tarefas de alta pontuação: Read Aloud, Repeat Sentence, Write from Dictation.',
        priority: 'alta'
      },
      {
        category: 'geral',
        title: 'Alerta de Pontuação Negativa',
        content: 'Múltipla escolha (múltiplas respostas) tem pontuação negativa. Selecione apenas se tiver certeza!',
        priority: 'alta'
      },
      {
        category: 'geral',
        title: 'Pratique Diariamente, Mesmo que 15 Minutos',
        content: 'Consistência supera intensidade. A prática diária mantém sua "memória muscular" em inglês.',
        priority: 'média'
      },
      {
        category: 'geral',
        title: 'Revise Seus Erros',
        content: 'Gaste 5 minutos revisando respostas incorretas. Entender por que errou evita a repetição.',
        priority: 'alta'
      },

      // Advanced Strategy Tips
      {
        category: 'estratégia',
        title: 'Benefícios de Habilidades Cruzadas',
        content: 'Ler em voz alta melhora as pontuações de fala E leitura. Benefício em dobro!',
        priority: 'alta'
      },
      {
        category: 'estratégia',
        title: 'Regra de Gestão do Tempo',
        content: 'Nunca gaste mais do que o tempo alocado. Uma pergunta não respondida pontua zero.',
        priority: 'alta'
      },
      {
        category: 'estratégia',
        title: 'Fluência Acima da Precisão',
        content: 'Na fala, manter o fluxo pontua mais do que pronúncia perfeita com hesitações.',
        priority: 'média'
      },
      {
        category: 'estratégia',
        title: 'Domínio de Modelos',
        content: 'Memorize modelos para tarefas previsíveis (introdução/conclusão de ensaio, descrever imagem).',
        priority: 'alta'
      },
      {
        category: 'estratégia',
        title: 'Áreas Fracas Primeiro',
        content: 'Pratique sua seção mais fraca primeiro a cada dia, quando sua mente está descansada.',
        priority: 'média'
      },
      {
        category: 'estratégia',
        title: 'A Regra do 80/20',
        content: '80% da sua pontuação vem de 20% dos tipos de perguntas. Domine primeiro as de alta pontuação.',
        priority: 'alta'
      },
      {
        category: 'estratégia',
        title: 'O Sotaque Não Importa',
        content: 'O PTE aceita todos os sotaques. Concentre-se na clareza e fluência, não em soar "nativo".',
        priority: 'média'
      },
      {
        category: 'estratégia',
        title: 'Pratique com Cronômetro',
        content: 'Sempre pratique com limites de tempo. A velocidade é tão importante quanto a precisão no PTE.',
        priority: 'alta'
      },
      {
        category: 'estratégia',
        title: 'Amplitude de Vocabulário',
        content: 'Use vocabulário variado, mas mantenha-se natural. Palavras complexas forçadas podem prejudicar a fluência.',
        priority: 'média'
      },
      {
        category: 'estratégia',
        title: 'Preparação para o Dia do Teste',
        content: 'Chegue 30 minutos mais cedo. Teste seu microfone corretamente. Mantenha a calma e controle seu ritmo.',
        priority: 'alta'
      }
    ],
    accountDeletionPage: {
      accountDeletion: "Exclusão de Conta",
      manageYourPteasyAccount: "Gerencie seus dados de conta PTEasy",
      importantNotice: "Aviso Importante",
      accountDeletionIsPermanent: "A exclusão de conta é permanente e não pode ser desfeita. Todos os seus dados serão permanentemente removidos de nossos sistemas.",
      howToDeleteYourAccount: "Como Excluir Sua Conta",
      youCanDeleteYourPteasy: "Você pode excluir sua conta PTEasy diretamente no aplicativo móvel seguindo estas etapas:",
      openThePteasyMobileApp: "Abra o aplicativo móvel PTEasy",
      launchTheAppOnYourDevice: "Inicie o aplicativo em seu dispositivo",
      navigateToTheProfileTab: "Navegue até a aba Perfil",
      tapOnTheProfileIconIn: "Toque no ícone Perfil na barra de navegação inferior",
      findTheAccountSection: "Encontre a seção Conta",
      scrollDownToLocateThe: "Role para baixo para localizar a seção de configurações da Conta",
      tapDeleteAccount: "Toque em \"Excluir conta\"",
      confirmDeletion: "Confirmar exclusão",
      readTheConfirmationMessage: "Leia a mensagem de confirmação e toque em \"Excluir\" para confirmar",
      yourAccountWillBeDeleted: "Sua conta será excluída imediatamente após a confirmação. Você será desconectado automaticamente.",
      whatDataGetsDeleted: "Quais Dados São Excluídos",
      whenYouDeleteYourAccount: "Ao excluir sua conta, os seguintes dados são permanentemente removidos de nossos sistemas:",
      profileInformation: "Informações de Perfil:",
      yourNameEmailAddressAnd: "Seu nome, endereço de e-mail e credenciais de conta",
      practiceHistory: "Histórico de Prática:",
      allYourExerciseResponses: "Todas as suas respostas a exercícios e sessões de prática",
      testResults: "Resultados de Testes:",
      mockTestScoresAnd: "Pontuações de testes simulados e análises de desempenho",
      audioRecordings: "Gravações de Áudio:",
      anySpeakingPractice: "Quaisquer gravações de prática de fala",
      progressData: "Dados de Progresso:",
      learningProgress: "Progresso de aprendizado, conquistas e estatísticas",
      preferences: "Preferências:",
      studyPreferences: "Preferências de estudo, configurações de notificação e configurações do aplicativo",
      subscriptionInformation: "Informações de Assinatura:",
      paymentHistoryAnd: "Histórico de pagamento e detalhes da assinatura",
      dataRetentionPolicy: "Política de Retenção de Dados",
      immediateDeletion: "Exclusão imediata:",
      yourAccountAndPersonal: "Sua conta e dados pessoais são excluídos imediatamente após a confirmação",
      noRetention: "Sem retenção:",
      weDoNotRetainAnyOfYour: "Não retemos nenhum dos seus dados pessoais após a exclusão da conta",
      irreversible: "Irreversível:",
      thisActionCannotBeUndone: "Esta ação não pode ser desfeita - todos os dados são perdidos permanentemente",
      legalCompliance: "Conformidade legal:",
      someAnonymizedDataMayBe: "Alguns dados anonimizados podem ser retidos apenas para fins legais ou regulamentares",
      beforeYouDeleteYourAccount: "Antes de Excluir Sua Conta",
      pleaseConsiderThese: "Considere estas alternativas:",
      ifYouReHavingIssuesWith: "Se você estiver tendo problemas com o aplicativo, entre em contato com nossa equipe de suporte primeiro",
      youCanTemporarily: "Você pode desativar temporariamente as notificações nas configurações do seu perfil",
      considerExportingYourData: "Considere exportar seus dados antes da exclusão, se precisar deles para referência futura",
      cancelAnyActive: "Cancele quaisquer assinaturas ativas antes de excluir sua conta",
      needHelp: "Precisa de Ajuda?",
      ifYouHaveQuestionsAbout: "Se você tiver dúvidas sobre a exclusão da conta ou precisar de assistência, entre em contato conosco:",
      emailSupport: "Suporte por Email",
      contactForm: "Formulário de Contato",
      visitOurContactPage: "Visite nossa página de contato",
      relatedInformation: "Informações Relacionadas",
      privacyPolicy: "Política de Privacidade",
      termsOfService: "Termos de Serviço",
      contactUs: "Fale Conosco",
      selectTheDeleteAccount: "Selecione a opção \"Excluir conta\" (mostrada em vermelho)"
    }
  },
  components: {
    mobileAppPrompt: {
      ios: {
        title: 'Baixe o App Nativo!',
        description: 'Baixe nosso aplicativo móvel para uma experiência melhor com desempenho otimizado e recursos nativos.',
        downloadButton: 'Baixar da App Store',
        note: 'Disponível agora na App Store'
      },
      android: {
        title: 'Participe dos Testes Android!',
        description: 'Nosso app Android está em testes internos. Envie seu e-mail para obter acesso à versão beta.',
        emailPlaceholder: 'Digite seu e-mail',
        submitButton: 'Solicitar Acesso',
        submitting: 'Enviando...',
        note: 'Adicionaremos você ao nosso grupo de testes internos',
        successTitle: 'Você está na lista!',
        successDescription: 'Enviaremos instruções de teste para',
        errors: {
          invalidEmail: 'Por favor, insira um endereço de e-mail válido',
          serverError: 'Algo deu errado. Por favor, tente novamente.',
          networkError: 'Erro de rede. Por favor, tente novamente.'
        }
      }
    },
    mobileRestriction: {
      title: 'Testes Simulados Requerem um Desktop',
      description: 'Para garantir a melhor experiência de simulação de exame, os testes simulados estão disponíveis apenas em computadores desktop ou laptop.',
      reasons: {
        fullScreen: {
          title: 'Experiência em Tela Cheia',
          description: 'Os testes simulados requerem uma tela grande para exibir corretamente todo o conteúdo e controles do exame.'
        },
        realExam: {
          title: 'Corresponde ao Exame Real',
          description: 'O exame PTE real é feito em um computador desktop, então praticar em um te prepara melhor.'
        }
      },
      cta: 'Enquanto isso, você pode praticar exercícios individuais:',
      practiceButton: 'Ir para Exercícios de Prática'
    }
  }
};
