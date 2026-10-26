# 🗂️ Estrutura Interna da Pasta do Grupo

> Gerada automaticamente por `python3 scripts/novo_grupo.py`. Não invente uma
> árvore diferente: a CI valida os caminhos abaixo.

```text
grupos/grupo-NN-slug-do-tema/
│
├── README.md                    ← executivo: ODS, dados, reproduzir, resultados (E6)
├── Makefile                     ← atalhos: make setup / make pipeline / make docker
├── Dockerfile                   ← base fixada + CMD (E6)
├── docker-compose.yml           ← comando único opcional (E6)
├── requirements.txt             ← todas as versões com `==` (E6)
├── .gitignore                   ← espelho das regras da raiz
│
├── configs/
│   └── base.yaml                ← SEED, caminhos, hiperparâmetros, folds (E3)
│
├── data/
│   ├── raw/.gitkeep             ← NUNCA versionado (só o .gitkeep)
│   └── processed/.gitkeep       ← gerado pelo pipeline
│
├── src/
│   ├── data/                    ← carga e limpeza
│   ├── features/                ← transformações e engenharia de atributos
│   ├── models/                  ← definição e treino dos modelos (E4)
│   ├── evaluation/              ← métricas, CV, testes estatísticos
│   └── pipeline.py              ← ponto de entrada (E3)
│
├── notebooks/
│   └── 01-eda-*.ipynb           ← EDA com 5 visualizações (E3)
│
├── experiments/
│   └── runs.csv                 ← uma linha por execução (E4)
│
├── reports/
│   ├── figures/                 ← ≥ 3 figuras na E5
│   ├── tables/                  ← tabelas geradas por script
│   └── environment.json         ← versões + hash do commit (E6)
│
├── article/
│   ├── artigo.tex               ← IMRaD, 4–8 páginas (E7)
│   └── referencias.bib          ← ≥ 8 referências (E7)
│
├── slides/                      ← 8–12 slides (E7)
│
└── docs/
    ├── proposta.md              ← E1
    ├── dicionario-de-dados.md   ← E2
    └── decisoes-tecnicas.md     ← protocolo de CV/teste, alternativas rejeitadas
```

---

## Para que serve cada pasta

| Caminho | Regra prática |
| ------- | ------------- |
| `src/data/` | Só leitura/limpeza. Se precisa transformar atributos, é `features/`. |
| `src/features/` | Todo transformador é `FunctionTransformer`/`TransformerMixin` para entrar no `Pipeline`. |
| `src/models/` | Uma função `build_*()` por família de modelo; hiperparâmetros vêm do YAML. |
| `src/evaluation/` | Métricas, CV repetida, testes estatísticos e geração de figuras. |
| `src/pipeline.py` | Executa o fluxo completo a partir de `configs/base.yaml`. É o que o Docker roda. |
| `experiments/runs.csv` | Log append-only; nunca sobrescreva linhas antigas. |
| `reports/` | Saídas **geradas**; o que é versionado é o script que as produz. |
| `article/` | LaTeX puro. Tabela e figura entram via `\input{}`/`\includegraphics{}` do que o script gerou. |
| `docs/` | Texto humano: proposta, dicionário, decisões. É onde a banca procura o raciocínio. |

---

## O que **não** entra no repositório

| Item | Por quê |
| ---- | ------- |
| `data/raw/` (dados, `.zip`, `.csv` grande) | LGPD + tamanho; registre URL e hash no dicionário |
| `*.pkl`, `*.joblib`, `*.pt`, `*.h5` | Modelo é artefato de execução, não de versionamento |
| `.venv/`, `__pycache__/`, `.ipynb_checkpoints/` | Lixo de máquina |
| `.env`, `credentials.json`, `kaggle.json` | Segredo vazado em repositório público é irreversível |
| Arquivos > 20 MB | A CI e o hook bloqueiam |
| `main.pdf`/auxiliares LaTeX | Só o `.pdf` do artigo (se quiser) e as fontes |

---

## Nomes de arquivo

- **kebab-case**, minúsculo, sem acento, sem espaço:
  `03-modelagem-baseline.ipynb`, `matriz-confusao-final.png`.
- Notebooks com prefixo numérico de ordem: `01-eda`, `02-preparacao`,
  `03-modelagem`, `04-comparacao`.
- Saídas seguem o padrão `<tipo>-<assunto>.<ext>`: `tabela-cv-wilcoxon.csv`,
  `figura-importancia-atributos.png`.

Validar antes de commitar:

```bash
python3 scripts/check_entrega.py --grupo grupo-NN --entrega E6
```
