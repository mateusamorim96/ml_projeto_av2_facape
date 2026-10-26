# GXX — Tema do Grupo (preencher)

> Projeto AV2 de Machine Learning · FACAPE 2026.2
> Pasta: `grupos/grupo-XX-slug` · Entrega atual: E1

## Integrantes

| Nome | Matrícula | Papel |
| ---- | --------- | ----- |
| preencher | | dados e pipeline |
| preencher | | modelagem |
| preencher | | avaliação e estatística |
| preencher | | artigo, Docker e apresentação |

---

## 1. ODS, meta e problema

- **ODS:** preencher (ex.: ODS 6 — Água potável e saneamento)
- **Meta:** preencher (ex.: 6.1 — acesso universal e equitativo à água potável)
- **Problema:** preencher (2–4 linhas, com o recorte local)
- **Público/beneficiário:** preencher

## 2. Decisão

> “Se o modelo indicar **preencher**, a equipe **preencher** fará **preencher**.”

- **Custo do falso positivo:** preencher
- **Custo do falso negativo:** preencher
- **Métrica principal:** preencher (e por que não acurácia, se for o caso)

## 3. Dados e licença

- **Fonte:** preencher (instituição + URL)
- **Data de acesso:** preencher
- **Licença:** preencher
- **Volume:** preencher (registros × atributos)
- **Alvo:** preencher
- Detalhes em [`docs/dicionario-de-dados.md`](docs/dicionario-de-dados.md).

## 4. Como reproduzir

```bash
# 1. ambiente local
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. pipeline completo
python -m src.pipeline --config configs/base.yaml

# 3. ou via Docker (ambiente limpo)
docker build -t grupo-XX .
docker run --rm grupo-XX
```

- **Tempo estimado de execução:** preencher (ex.: 6 min em CPU 4 núcleos)
- **Saídas:** `reports/tables/`, `reports/figures/`, `reports/environment.json`

## 5. Resultados principais

| Modelo | Métrica (média ± desvio) | IC 95% | p-valor vs baseline |
| ------ | ------------------------ | ------ | ------------------- |
| preencher | | | |

Figuras: preencher (links de `reports/figures/`).

## 6. Limitações

- preencher (o que o dado não cobre)
- preencher (viés conhecido, subnotificação, recorte temporal)
- preencher (o que o modelo **não** faz)

## 7. Uso responsável

- **Não usar para:** preencher (ex.: decisão individual automatizada, ranking de pessoas)
- **Dados pessoais:** preencher (ausentes / agregados por município / removidos)
- **Desempenho por subgrupo:** preencher
- **Uso de IA generativa:** preencher (ferramenta, trecho, como foi verificado)

---

## Estrutura desta pasta

```text
grupo-XX-slug/
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
