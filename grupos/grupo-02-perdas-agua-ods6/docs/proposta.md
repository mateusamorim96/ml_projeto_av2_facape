# Proposta do Projeto — G02

> Entrega E1 · Projeto AV2 de Machine Learning · FACAPE 2026.2

## 1. ODS e meta

- **ODS:** 6 — Água potável e saneamento.
- **Meta:** 6.4 — Aumentar a eficiência do uso da água e contribuir para o
  enfrentamento da escassez hídrica.
- **Por que essa meta:** Perdas de água na distribuição significam que parte da
  água disponibilizada não chega ao uso final esperado. Prever municípios com
  perdas elevadas pode ajudar equipes responsáveis pelo abastecimento a
  direcionar avaliações técnicas e apoiar ações de uso mais eficiente da água.
- **Relevância local:** O estudo abrangerá municípios brasileiros presentes na
  base oficial. A cobertura de municípios de Pernambuco e do entorno da FACAPE
  será verificada na auditoria dos dados; não presumimos que todos estarão
  representados nem que os dados, por si só, comprovem a situação local.

## 2. Problema

As equipes responsáveis pelo abastecimento precisam decidir onde priorizar
avaliações técnicas, mas recursos e tempo para inspeções são limitados. Os dados
anuais municipais do SINISA/SNIS podem oferecer indicadores de abastecimento e
perdas, mas a disponibilidade de uma série histórica metodologicamente
comparável ainda precisa ser confirmada.

O projeto investigará se indicadores de um ano podem ajudar a prever o
percentual de perdas do ano seguinte para um município. A previsão servirá
somente como sinal de apoio à triagem e à priorização de avaliações. Ela não
identifica a causa da perda, não substitui inspeções, nem deve ser usada como
avaliação definitiva do desempenho de um prestador.

## 3. Pergunta de ML

Usando os indicadores municipais do SINISA/SNIS no ano `t`, é possível prever o
percentual de perdas de água no ano `t+1` com erro absoluto médio (MAE) menor do
que o de uma referência que repete o valor de perdas do ano `t`, em municípios
com observações comparáveis nos dois anos?

## 4. Decisão

> “Se o modelo indicar uma previsão de perdas de água acima de um limite
> previamente definido, a equipe responsável pelo abastecimento poderá priorizar
> uma avaliação técnica do sistema em até 30 dias.”

- **Quem decide:** equipe responsável pela operação ou gestão do abastecimento
  de água no município.
- **Quando decide:** após a publicação e validação dos dados anuais, durante o
  planejamento de avaliações técnicas; a avaliação priorizada deverá ocorrer,
  quando viável, em até 30 dias da decisão.
- **Custo do falso positivo:** priorizar uma avaliação de um sistema que não
  esteja entre os de maior perda, ocupando temporariamente recursos que
  poderiam ser direcionados a outro local.
- **Custo do falso negativo:** não priorizar um sistema com perdas elevadas,
  atrasando sua avaliação e possíveis ações corretivas.
- **Consequência de não usar o modelo:** a equipe continuará priorizando
  avaliações com os critérios e informações operacionais que já utiliza.
- **Limite de alerta:** será definido após a auditoria da distribuição do alvo
  e discussão com o responsável pela decisão; não será escolhido apenas para
  melhorar métricas do modelo.

## 5. Formulação técnica

- **Tipo de aprendizado:** supervisionado — regressão.
- **Unidade de análise:** município-ano.
- **Variável-alvo:** percentual anual de perdas de água na distribuição. O nome
  exato do indicador, sua unidade e se é informado diretamente ou calculado
  serão confirmados no dicionário do SINISA/SNIS na E2.
- **Métrica principal:** MAE, reportado em pontos percentuais se a definição e
  unidade do indicador permitirem essa interpretação. O MAE expressa o tamanho
  médio do erro na unidade do alvo e é adequado à tarefa de regressão.
- **Métricas secundárias:** RMSE, para evidenciar erros maiores, e R² como
  medida complementar. O resultado principal será comparado à referência
  temporal definida na pergunta de pesquisa. A acurácia não se aplica a um
  alvo contínuo.

## 6. Dados previstos

- **Fonte:** SINISA — Sistema Nacional de Informações em Saneamento Básico,
  módulo Abastecimento de Água, planilha Base Municipal de 2024 e, se
  comparáveis, anos históricos. Portal informado: https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/resultados-sinisa/resultados-sinisa-2025
- **Instituição:** Ministério das Cidades.
- **Licença:** será verificada nos termos da base e registrada com o link
  correspondente no dicionário de dados antes de reutilizar ou redistribuir os
  arquivos.
- **Volume esperado:** ainda não medido; quantidade de registros, atributos e
  cobertura temporal serão registrados após baixar e auditar os arquivos na
  E2.
- **Risco de LGPD:** espera-se trabalhar com dados agregados por município,
  sem dados pessoais. Isso será verificado na E2; qualquer campo que permita
  identificar pessoas será removido e documentado.
- **Plano B:** se a série histórica não estiver disponível ou não for
  metodologicamente comparável, restringir a análise aos anos compatíveis
  documentados ou reformular, com orientação do professor, a pergunta para
  outro recorte temporal oficial adequado. Não combinar indicadores de
  definições incompatíveis.

## 7. Riscos e plano de contingência

| Risco | Probabilidade inicial | Impacto | Mitigação |
| ----- | --------------------- | ------- | --------- |
| Série histórica ou download indisponível | média | alto | Registrar fonte, data, arquivos e hash; consultar a série histórica oficial e discutir alternativas com o professor |
| Definição do indicador alterada entre anos | média | alto | Comparar dicionários e notas metodológicas; usar somente anos compatíveis |
| Cobertura incompleta ou mudanças na participação dos municípios | média | alto | Medir cobertura por ano e documentar os critérios de inclusão |
| Alvo ausente, inconsistente ou com muitos valores inválidos | média | alto | Auditar unidade, faixa, nulos e regra de cálculo; rever o recorte se necessário |
| Vazamento de informação entre anos | baixa | alto | Usar preditores disponíveis em `t` para prever `t+1` e separar a validação por tempo |
| Previsão tratada como diagnóstico ou decisão automática | baixa | alto | Apresentar a ferramenta como apoio à triagem; exigir avaliação técnica antes de qualquer ação |

## 8. O que faria o grupo mudar de rumo

- Se as definições do alvo ou dos preditores não forem comparáveis entre anos,
  não faremos uma previsão temporal com esses anos; vamos selecionar um recorte
  compatível ou revisar a pergunta com o professor.
- Se não houver um indicador contínuo de perdas com definição e cobertura
  suficientes, vamos reavaliar o alvo antes de escolher outro problema ou tipo
  de aprendizado.
- Se o SINISA/SNIS não oferecer dados reutilizáveis ou suficientes, vamos
  discutir uma fonte oficial alternativa com o professor e registrar a decisão.
- Se a equipe usuária considerar que subestimar perdas tem custo muito maior
  que superestimá-las, vamos discutir uma métrica complementar ou uma abordagem
  de decisão que reflita essa assimetria, sem abandonar a avaliação do MAE
  solicitada para a proposta inicial.
