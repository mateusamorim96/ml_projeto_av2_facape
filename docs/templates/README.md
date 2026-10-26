# 🧩 Templates e Guias de Preenchimento

O **esqueleto executável** de um grupo está em
[`../../grupos/_template/`](../../grupos/_template/) e é copiado automaticamente
por:

```bash
python3 scripts/novo_grupo.py --numero 3 --tema saneamento-ana
```

Não copie arquivos à mão — o script substitui os marcadores `grupo-XX` e `GXX`
em todos os arquivos de texto.

---

## O que já vem pronto no esqueleto

| Arquivo | Estado inicial | O que o grupo faz |
| ------- | -------------- | ----------------- |
| `README.md` | tabelas com marcadores | preencher ODS, decisão, dados, resultados |
| `docs/proposta.md` | roteiro com perguntas | escrever a proposta (E1) |
| `docs/dicionario-de-dados.md` | tabela vazia + campos de auditoria | preencher na E2 |
| `docs/decisoes-tecnicas.md` | roteiro de decisões | registrar protocolo de CV/teste (E5) |
| `configs/base.yaml` | seed, caminhos, folds | ajustar ao problema |
| `src/pipeline.py` | esqueleto com `TODO` | implementar o fluxo ponta a ponta |
| `requirements.txt` | 4 dependências pinadas | acrescentar o que usar, **sempre com `==`** |
| `Dockerfile` | `python:3.11-slim` + `CMD` | trocar só se necessário |
| `Makefile` | atalhos `setup/pipeline/docker` | opcional manter |
| `article/artigo.tex` | IMRaD com seções vazias | escrever na E7 |
| `experiments/runs.csv` | cabeçalho | registrar cada execução (append-only) |

---

## Guias neste diretório

- [`tabela-teste-estatistico.md`](tabela-teste-estatistico.md) — qual teste usar
  com 2, 3 ou mais modelos; como reportar efeito e IC.
- [`checklist-entrega.md`](checklist-entrega.md) — checklist imprimível por
  entrega (E1–E8).

---

## Regra de ouro dos templates

Template não é para ser “preenchido como formulário”: é para evitar que o grupo
gaste energia decidindo onde colocar cada coisa. O conteúdo — pergunta, decisão,
métrica, limitações — é responsabilidade intelectual do grupo, e é exatamente o
que a banca vai arguir.
