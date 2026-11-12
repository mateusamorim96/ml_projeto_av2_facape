# Proposta do Projeto — G01 · Risco de baixo peso ao nascer em Pernambuco

Entrega E1 · trabalho individual (Luiz Eduardo)

## 1. ODS e meta

- **ODS:** 3 — Saúde e bem-estar.
- **Meta:** 3.2 — até 2030, acabar com as mortes evitáveis de recém-nascidos e
  crianças menores de 5 anos.
- **Por que essa meta:** o baixo peso ao nascer (< 2.500 g) é um dos principais
  determinantes da mortalidade neonatal e da morbidade na infância. Diferente do
  óbito, ele é registrado em quase cem por cento dos nascimentos e pode ser
  antecipado no pré-natal. Isso permite agir antes do desfecho, que é o que a
  meta pede ao falar em mortes **evitáveis**.
- **Relevância local:** no SINASC 2023, Pernambuco teve **116.175 nascidos
  vivos**, com **8,61%** de baixo peso. **Petrolina** teve **6.022 nascidos
  vivos**, com **9,22%** de baixo peso, acima da média do estado. Os números
  foram calculados a partir do arquivo `DNPE2023.dbc` do DATASUS. Petrolina tem
  uma zona rural extensa no semiárido, onde a busca ativa de gestantes custa
  caro, por isso priorizar quem procurar primeiro faz diferença.

## 2. Problema

A gestante de risco para baixo peso só é identificada quando a equipe percebe
sinais clínicos ou quando ela se encaixa nos critérios de risco gestacional.
Isso depende da experiência de cada profissional e da regularidade das
consultas. As equipes da Estratégia Saúde da Família (ESF) têm tempo limitado
para consultas extras e visitas. O SINASC acumula anos de nascimentos do
território, com o perfil da mãe, o histórico obstétrico e o início do pré-natal,
mas essa informação não é usada para priorizar o acompanhamento.

**Fora do escopo:** prever o peso exato (regressão); diagnosticar condições
clínicas; prever prematuridade ou óbito; usar exames, ultrassom ou prontuário;
gestantes residentes fora de Pernambuco; ser uma ferramenta clínica validada
para uso real. O projeto é um estudo retrospectivo.

## 3. Pergunta de ML

É possível identificar, com informações disponíveis no início do pré-natal
(perfil sociodemográfico da mãe, histórico obstétrico, gestação única ou
múltipla e mês de início do pré-natal), quais nascidos vivos de mães residentes
em Pernambuco terão peso < 2.500 g, com **PR-AUC significativamente maior que a
do preditor trivial** (≈ 0,086) e sem queda relevante de recall entre subgrupos
de raça/cor, idade da mãe e região?

**Hipótese falsificável:** o melhor modelo tem PR-AUC em CV repetida com IC 95%
inteiramente acima de 0,086 e, com recall ≥ 0,70, tem precisão maior que a
prevalência. Se o IC incluir 0,086, a hipótese é rejeitada.

## 4. Decisão

> “Se o modelo indicar **risco ≥ c** (limiar escolhido na validação para recall
> ≥ 0,70), a **equipe de ESF da UBS de referência** fará **consulta extra e
> avaliação nutricional em até 7 dias**.”

- **Quem decide:** enfermeira(o) ou médica(o) da ESF responsável pelo pré-natal,
  com apoio da coordenação de atenção primária do município.
- **Quando decide:** na captação da gestante (primeira consulta de pré-natal),
  com reavaliação quando houver atualização cadastral.
- **Custo do falso positivo:** uma consulta e uma avaliação nutricional a mais.
  Custo baixo, de tempo da equipe.
- **Custo do falso negativo:** a gestante de risco segue no fluxo padrão e
  perde-se a janela para intervir (nutrição, investigação de infecções, controle
  de hipertensão). Custo alto.
- **Consequência de não usar o modelo:** a priorização continua dependendo só da
  avaliação clínica de cada equipe, sem considerar o padrão histórico de
  nascimentos do território.

## 5. Formulação técnica

- **Tipo de aprendizado:** supervisionado, classificação binária desbalanceada.
- **Unidade de análise:** nascido vivo, ou seja, uma Declaração de Nascido Vivo
  de mãe residente em PE.
- **Variável-alvo:** `baixo_peso = 1` se `PESO < 2500` g; `0` se `PESO ≥ 2500`
  g. Registros sem peso válido são excluídos.
- **Métrica principal:** **PR-AUC**. Com cerca de 8,6% de positivos, a acurácia
  de um modelo que só responde “não” já passaria de 91% sem detectar nenhum
  caso. Já a PR-AUC mede o quanto o modelo encontra os positivos sem gerar
  alarmes demais.
- **Métricas secundárias:** recall e precisão no limiar de operação; AUC-ROC;
  Brier score (calibração); recall por subgrupo (raça/cor da mãe, faixa etária
  da mãe, macrorregião de saúde).

## 6. Dados previstos

- **Fonte:** Ministério da Saúde/DATASUS, Sistema de Informações sobre Nascidos
  Vivos (SINASC). Arquivos por UF em
  `ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Dados/DNRES/`
  (`DNPEAAAA.dbc`) e no portal
  <https://dadosabertos.saude.gov.br/dataset/sistema-de-informacao-sobre-nascidos-vivos-sinasc>.
- **Licença:** o conjunto não declara licença própria. O portal de dados abertos
  do Ministério da Saúde usa Creative Commons Atribuição-SemDerivações 3.0. A
  análise completa da licença sai na E2. Os dados brutos não serão
  redistribuídos, porque `data/raw/` não é versionado.
- **Volume esperado:** cerca de 116 mil registros por ano × 61 colunas
  (verificado em 2023). O recorte provisório de 2019 a 2023 dá cerca de 580 mil
  registros. O período final será decidido na E2, considerando o efeito da
  pandemia em 2020 e 2021.
- **Risco de LGPD:** baixo. Os dados são públicos e anonimizados, e o menor
  nível geográfico é o município. Mesmo assim, serão removidos datas de
  nascimento da mãe e do bebê, código do estabelecimento, lote e contador, e
  nenhum resultado será publicado em células com menos de 10 casos.
- **Plano B:** mesma base com acesso pelo portal OpenDataSUS (CSV nacional) caso
  o FTP falhe. Se a pergunta se mostrar inviável, o tema reserva é
  hospitalização por dengue (SINAN, ODS 3.3).

## 7. Riscos e plano de contingência

| Risco                              | Probabilidade  | Impacto | Mitigação                                                                                                                                                                                                                                                        |
| ---------------------------------- | -------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| base indisponível                  | baixa          | alto    | já baixada e lida (`DNPE2023.dbc`); download por script com hash; acesso alternativo pelo OpenDataSUS                                                                                                                                                            |
| alvo mal definido                  | baixa          | médio   | definição objetiva (`PESO < 2500` g, critério OMS); excluir pesos ausentes ou implausíveis                                                                                                                                                                       |
| desbalanceamento severo            | certa (≈ 8,6%) | médio   | PR-AUC como métrica; `class_weight` ou ajuste de limiar dentro da CV; sem reamostrar o teste                                                                                                                                                                     |
| vazamento temporal                 | alta           | alto    | excluir variáveis que só existem no parto (`SEMAGESTAC`, `GESTACAO`, `PARTO`, `APGAR1/5`, `TPAPRESENT`, `TPROBSON`, `STTRABPART`, `STCESPARTO`, `IDANOMAL`) e as que dependem da duração da gestação (`CONSULTAS`, `CONSPRENAT`, `KOTELCHUCK`); usar `MESPRENAT` |
| viés entre subgrupos               | média          | alto    | recall e precisão por raça/cor, idade e região; discussão de discriminação algorítmica                                                                                                                                                                           |
| mudança de distribuição (pandemia) | média          | médio   | comparar anos na EDA; testar o modelo também num ano posterior ao treino                                                                                                                                                                                         |

## 8. O que faria mudar de rumo

- Se, na E2, a licença do SINASC impedir a publicação de resultados derivados,
  troca-se para o tema reserva (SINAN Dengue).
- Se as variáveis disponíveis no pré-natal tiverem mais de 30% de nulos em algum
  ano, o período é restrito aos anos com boa completude.
- Se, na E4, nenhum modelo superar o baseline em PR-AUC com IC 95%, isso é
  reportado como resultado. A pergunta passa a ser quais fatores explicam o
  risco, com foco em interpretação.
- Se o recall de algum subgrupo de raça/cor ou região for muito menor que o
  geral, o artigo recomenda **não** usar o modelo em produção e discute a causa
  (sub-registro, tamanho da amostra).

**Uso inadequado:** este modelo não deve ser usado para negar, adiar ou reduzir
atendimento a nenhuma gestante. Ele serve apenas para **priorizar**
acompanhamento extra.
