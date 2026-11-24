# G01 — Risco de baixo peso ao nascer em Pernambuco (ODS 3.2)

> Projeto AV2 de Machine Learning · FACAPE 2026.2 Pasta:
> `grupos/grupo-01-baixo-peso-sinasc-pe` · Entrega atual: E2

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
  determinantes da mortalidade neonatal. Em 2023, 8,61% dos nascidos vivos de
  mães residentes em Pernambuco tiveram baixo peso. Em Petrolina foram 9,22%
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
- **Métrica principal:** PR-AUC. Com cerca de 8,6% de positivos, um modelo que
  sempre responde “não” já teria mais de 91% de acurácia, por isso a acurácia
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
- **Volume:** 1.282.496 registros × 61 colunas (PE, 2015–2024).
- **Recorte:** desenvolvimento em 2019–2023 (621.404 registros) e teste temporal
  em 2024 (110.759 registros), usado uma única vez no final.
- **Alvo:** `baixo_peso = 1` se `PESO < 2500` g (8,17% no desenvolvimento).
- Auditoria completa, gerada por script, em
  [`docs/dicionario-de-dados.md`](docs/dicionario-de-dados.md).

## 4. Como reproduzir

```bash
# 1. ambiente local
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. dados brutos (DATASUS + IBGE) com conferência de SHA-256, e auditoria
python -m src.data.download  --config configs/base.yaml
python -m src.data.auditoria --config configs/base.yaml

# 3. pipeline completo (a partir da E3)
python -m src.pipeline --config configs/base.yaml

# 4. ou via Docker (ambiente limpo)
docker build -t grupo-01-baixo-peso-sinasc-pe .
docker run --rm grupo-01-baixo-peso-sinasc-pe
```

- **Tempo estimado de execução:** download cerca de 3 min; auditoria cerca de 4 min
  na primeira vez (lê 10 arquivos `.dbc`) e segundos nas seguintes (cache em
  `data/processed/`). O pipeline completo será medido na E6.
- **Saídas:** `reports/tables/`, `reports/figures/`, `reports/environment.json`

## 5. Resultados principais

Disponíveis a partir da E4 (modelagem) e da E5 (comparação estatística).

## 6. Limitações

- Estudo retrospectivo: os registros do SINASC são preenchidos no parto, mas o
  modelo é pensado para o início do pré-natal. Por isso, só são usadas variáveis
  conhecidas nesse momento.
- A prevalência de baixo peso sobe a partir de 2021 (7,8% → 8,7%). O teste
  temporal em 2024 mede se o modelo aguenta essa mudança.
- O SINASC só registra nascidos vivos: gestações que terminam em perda fetal
  não entram na base.
- O modelo não prevê o peso exato nem diagnostica condições clínicas.

## 7. Uso responsável

- **Não usar para:** negar, adiar ou reduzir atendimento a qualquer gestante. O
  modelo serve apenas para priorizar acompanhamento extra.
- **Dados pessoais:** a base é pública e anonimizada. Datas, hora do nascimento,
  código do estabelecimento, lote, contador e naturalidade são removidos. O
  município entra agregado por região. Nenhuma tabela publicada tem célula com
  menos de 10 registros, e `data/raw/` não é versionado.
- **Desempenho por subgrupo:** recall e precisão por raça/cor da mãe, faixa
  etária da mãe e região de saúde (entrega E5).
- **Uso de IA generativa:** Claude Code (Anthropic) foi usado para pesquisar as
  fontes de dados, escrever os scripts de download e auditoria (`src/data/`) e
  redigir a proposta, o dicionário de dados e este README. Os números citados
  são calculados pelos scripts a partir dos arquivos originais do DATASUS; as
  tabelas do dicionário são reescritas pela auditoria a cada execução.

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
