# G01 — Risco de baixo peso ao nascer em Pernambuco (ODS 3.2)

> Projeto AV2 de Machine Learning · FACAPE 2026.2 · Pasta
> `grupos/grupo-01-baixo-peso-sinasc-pe` · Entrega atual: E3

## Integrantes

Trabalho individual.

| Nome         | Matrícula | Papel                                                      |
| ------------ | --------- | ---------------------------------------------------------- |
| Luiz Eduardo | 22770     | dados, modelagem, avaliação, artigo, Docker e apresentação |

---

## 1. ODS, meta e problema

- **ODS:** 3 — Saúde e bem-estar.
- **Meta:** 3.2 — acabar com as mortes evitáveis de recém-nascidos e crianças
  menores de 5 anos.
- **Problema:** o baixo peso ao nascer (< 2.500 g) é um dos principais
  determinantes da mortalidade neonatal. Em 2024, 8,71% dos nascidos vivos de
  mães residentes em Pernambuco tiveram baixo peso. Em Petrolina foram 9,48%, e
  o município ficou acima da média do estado em todos os anos de 2015 a 2024
  (SINASC/DATASUS). O projeto investiga se dá para identificar as gestantes de
  maior risco já no início do pré-natal.
- **Público/beneficiário:** equipes da Estratégia Saúde da Família (ESF) e
  coordenação de atenção primária. Beneficiários finais: gestantes e
  recém-nascidos.

Proposta completa: [`docs/proposta.md`](docs/proposta.md).

## 2. Decisão

> “Se o modelo indicar **risco ≥ c** (limiar com recall ≥ 0,70 na validação), a
> equipe **de ESF da UBS de referência** fará **consulta extra e avaliação
> nutricional em até 7 dias**.”

- **Custo do falso positivo:** uma consulta extra desnecessária. Custo baixo.
- **Custo do falso negativo:** a gestante de risco fica sem acompanhamento
  reforçado. Custo alto.
- **Métrica principal:** PR-AUC. Com cerca de 7% de positivos, um modelo que
  sempre responde “não” já teria mais de 93% de acurácia, por isso a acurácia
  não serve como métrica.

## 3. Dados e licença

- **Fonte:** Ministério da Saúde/DATASUS — Sistema de Informações sobre Nascidos
  Vivos (SINASC),
  `ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Dados/DNRES/` e
  <https://dadosabertos.saude.gov.br/dataset/sistema-de-informacao-sobre-nascidos-vivos-sinasc>.
- **Data de acesso:** 2026-11-23. O SHA-256 de cada arquivo está em
  `configs/hashes-dados-brutos.csv`.
- **Licença:** o conjunto não declara licença própria. O Portal de Dados Abertos
  do SUS declara CC BY-ND 3.0 para o site inteiro. O projeto não redistribui a
  base, só publica código e resultados agregados com atribuição ao Ministério da
  Saúde. A análise completa está na seção 7 do dicionário de dados.
- **Base legal de uso:** dados abertos publicados pelo Ministério da Saúde
  (Política de Dados Abertos, Decreto 8.777/2016), já anonimizados na origem.
  Dados anonimizados não são considerados dados pessoais pela LGPD (Lei
  13.709/2018, art. 12). Quase-identificadores (datas, hora, estabelecimento)
  são removidos antes de qualquer análise.
- **Volume:** 1.282.496 registros × 61 colunas (PE, 2015–2024).
- **População do modelo:** gestações únicas com mês de início do pré-natal
  registrado, que é quem passa pela captação.
- **Recorte:** desenvolvimento em 2019–2023 (585.505 registros na população) e
  teste temporal em 2024 (104.917), usado uma única vez no final.
- **Alvo:** `baixo_peso = 1` se `PESO < 2500` g (6,96% no desenvolvimento).
- Auditoria completa, gerada por script, em
  [`docs/dicionario-de-dados.md`](docs/dicionario-de-dados.md).

## 4. Como reproduzir

```bash
# 1. ambiente local
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. pipeline: baixa e confere os dados (SHA-256), prepara, faz o split
#    temporal, gera as figuras da EDA e monta o pré-processamento
python -m src.pipeline --config configs/base.yaml
python -m src.pipeline --config configs/base.yaml --etapa dados   # uma etapa só

# 3. auditoria dos dados (reescreve as tabelas do dicionário de dados)
python -m src.data.auditoria --config configs/base.yaml

# 4. ou via Docker (ambiente limpo; validado na E6)
docker build -t grupo-01-baixo-peso-sinasc-pe .
docker run --rm grupo-01-baixo-peso-sinasc-pe
```

- **Etapas do pipeline:** `dados` → `eda` → `features` → `modelos` (E4) →
  `avaliacao` (E5). As etapas ainda não implementadas aparecem como pendentes,
  sem interromper a execução.
- **EDA:** as figuras saem em `reports/figures/figura-eda-*.png`, com a leitura
  e a decisão de cada uma em
  [`notebooks/01-eda-baixo-peso.ipynb`](notebooks/01-eda-baixo-peso.ipynb).
- **Tempo estimado de execução:** de 5 a 6 min na primeira vez, com download e
  leitura dos 10 arquivos `.dbc` (medido em clone limpo; varia com a velocidade
  do FTP do DATASUS). Depois, menos de 1 min (cache em `data/processed/`).
- **Saídas:** `data/processed/` (conjuntos de desenvolvimento e teste, fora do
  Git), `reports/tables/`, `reports/figures/`, `reports/environment.json`

## 5. Resultados principais

Disponíveis a partir da E4 (modelagem) e da E5 (comparação estatística).

## 6. Limitações

- Estudo retrospectivo: os registros do SINASC são preenchidos no parto, mas o
  modelo é pensado para o início do pré-natal. Por isso, só são usadas variáveis
  conhecidas nesse momento.
- A prevalência de baixo peso entre todos os nascidos vivos de PE sobe a partir
  de 2021 (de cerca de 7,8% para 8,7%). O teste temporal em 2024 mede se o
  modelo aguenta essa mudança.
- O SINASC só registra nascidos vivos: gestações que terminam em perda fetal
  não entram na base.
- O modelo não prevê o peso exato nem diagnostica condições clínicas.
- Não se aplica a gestações múltiplas nem a gestantes que não fizeram pré-natal:
  os dois grupos ficaram fora da população e têm prevalência maior de baixo
  peso.

## 7. Uso responsável

- **Não usar para:** negar, adiar ou reduzir atendimento a qualquer gestante. O
  modelo serve apenas para priorizar acompanhamento extra.
- **Dados pessoais:** a base é pública e anonimizada. Datas, hora do nascimento,
  código do estabelecimento, lote, contador e naturalidade são removidos. O
  município entra agregado por região. Nenhuma tabela publicada tem célula com
  menos de 10 registros, e `data/raw/` não é versionado.
- **Desempenho por subgrupo:** recall e precisão por raça/cor da mãe, faixa
  etária da mãe e mesorregião de residência (IBGE), com destaque para Petrolina
  (entrega E5).
- **Uso de IA generativa:** Claude Code (Anthropic) foi usado para pesquisar as
  fontes de dados, escrever o código (`src/`), gerar as figuras da EDA e redigir
  a proposta, o dicionário de dados, as decisões técnicas, o notebook e este
  README. Os números citados são calculados pelos scripts a partir dos arquivos
  originais do DATASUS; as tabelas do dicionário são reescritas pela auditoria a
  cada execução, e o notebook é executado de ponta a ponta.

---

## Estrutura desta pasta

```text
grupo-01-baixo-peso-sinasc-pe/
├── README.md               ← este arquivo
├── configs/base.yaml       ← seed, caminhos, folds, hiperparâmetros
├── data/raw/               ← NÃO versionado
├── src/                    ← data, features, models, evaluation, pipeline
├── notebooks/              ← EDA e experimentos
├── experiments/runs.csv    ← log de execuções
├── reports/                ← tabelas e figuras geradas
├── article/                ← artigo IMRaD
├── slides/                 ← apresentação
└── docs/                   ← proposta, dicionário, decisões técnicas
```
