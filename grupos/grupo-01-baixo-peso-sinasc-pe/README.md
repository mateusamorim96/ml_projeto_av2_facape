# G01 — Risco de baixo peso ao nascer em Pernambuco (ODS 3.2)

> Projeto AV2 de Machine Learning · FACAPE 2026.2 Pasta:
> `grupos/grupo-01-baixo-peso-sinasc-pe` · Entrega atual: E1

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
- **Data de acesso:** 2026-11-12 (verificação inicial com `DNPE2023.dbc`).
- **Licença:** o conjunto não declara licença própria. O portal de dados abertos
  do Ministério da Saúde usa CC BY-ND 3.0. A análise completa sai na E2.
- **Volume:** 116.175 registros × 61 colunas em PE 2023. O recorte provisório de
  2019 a 2023 tem cerca de 580 mil registros.
- **Alvo:** `baixo_peso = 1` se `PESO < 2500` g.
- Detalhes em [`docs/dicionario-de-dados.md`](docs/dicionario-de-dados.md)
  (entrega E2).

## 4. Como reproduzir

```bash
# 1. ambiente local
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. pipeline completo
python -m src.pipeline --config configs/base.yaml

# 3. ou via Docker (ambiente limpo)
docker build -t grupo-01-baixo-peso-sinasc-pe .
docker run --rm grupo-01-baixo-peso-sinasc-pe
```

- **Tempo estimado de execução:** será medido na E6.
- **Saídas:** `reports/tables/`, `reports/figures/`, `reports/environment.json`

## 5. Resultados principais

Disponíveis a partir da E4 (modelagem) e da E5 (comparação estatística).

## 6. Limitações

- Estudo retrospectivo: os registros do SINASC são preenchidos no parto, mas o
  modelo é pensado para o início do pré-natal. Por isso, só são usadas variáveis
  conhecidas nesse momento.
- A qualidade do registro varia entre municípios e anos, e os anos de 2020 e
  2021 foram afetados pela pandemia.
- O modelo não prevê o peso exato nem diagnostica condições clínicas.

## 7. Uso responsável

- **Não usar para:** negar, adiar ou reduzir atendimento a qualquer gestante. O
  modelo serve apenas para priorizar acompanhamento extra.
- **Dados pessoais:** a base é pública e anonimizada. Datas de nascimento,
  código do estabelecimento, lote e contador são removidos, e `data/raw/` não é
  versionado.
- **Desempenho por subgrupo:** recall e precisão por raça/cor da mãe, faixa
  etária da mãe e região de saúde (entrega E5).
- **Uso de IA generativa:** Claude Code (Anthropic) foi usado para pesquisar as
  fontes de dados, verificar colunas e prevalências no arquivo `DNPE2023.dbc` e
  redigir a proposta e este README. Os números citados foram calculados por
  script a partir do arquivo original.

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
