# ✅ Checklist de Entrega (imprimível)

Grupo: `G____` — Tema: ______________________ — Entrega: `E___`

---

## E1 — Proposta

- [ ] ODS: ____ · Meta: ____
- [ ] Relevância local justificada
- [ ] Pergunta falsificável
- [ ] Decisão: “se o modelo indicar ___, ___ fará ___”
- [ ] Tipo de aprendizado + métrica principal justificada
- [ ] Riscos iniciais listados
- [ ] `docs/proposta.md` completo, sem “preencher”

## E2 — Dados

- [ ] Fonte, URL, data de acesso e licença no dicionário
- [ ] Critério não-toy com números (registros/atributos/não tabular)
- [ ] Tabela de variáveis (tipo, unidade, nulos, origem)
- [ ] Alvo definido e não trivial
- [ ] LGPD verificada
- [ ] `data/raw/` fora do Git; hash registrado

## E3 — EDA e preparação

- [ ] 5 visualizações com conclusão escrita
- [ ] `src/pipeline.py` executável a partir de `configs/base.yaml`
- [ ] Nulos tratados com justificativa
- [ ] Split antes de qualquer `fit` de transformação
- [ ] Desbalanceamento medido

## E4 — Modelagem

- [ ] Baseline interpretável medido
- [ ] 3 famílias de modelos
- [ ] `experiments/runs.csv` com ≥ 3 execuções
- [ ] Tabela comparativa em `reports/tables/`
- [ ] Hiperparâmetros ajustados sem tocar no teste

## E5 — Comparação estatística

- [ ] Protocolo de CV documentado (folds idênticos, repetições)
- [ ] Média ± desvio em CV repetida
- [ ] Teste escolhido conforme a tabela de decisão
- [ ] p-valor + efeito + IC
- [ ] 3 figuras com IC ou barras de erro
- [ ] Discussão de relevância prática

## E6 — Repositório, Docker e README

- [ ] Árvore de `docs/estrutura-projeto.md` respeitada
- [ ] `requirements.txt` 100% pinado
- [ ] `Dockerfile` com base fixa e `CMD`
- [ ] `docker build` + `docker run` funcionam em ambiente limpo
- [ ] README com ODS, decisão, dados, reprodução, resultados, limitações, usos inadequados
- [ ] `reports/environment.json` com versões e hash do commit
- [ ] ≥ 10 commits, todos os integrantes com autoria

## E7 — Artigo e slides

- [ ] `article/artigo.tex` compila (4–8 páginas)
- [ ] ≥ 8 referências em `referencias.bib`
- [ ] IMRaD completo
- [ ] Tabelas/figuras geradas por script
- [ ] Declaração de reprodutibilidade (repo, tag, comando, imagem)
- [ ] Resultados por subgrupo avaliados
- [ ] `slides/` com 8–12 slides

## E8 — Apresentação

- [ ] 10 min de fala ensaiados
- [ ] `docker run` demonstrável
- [ ] Cada integrante explica código, dados, resultado e limitação
- [ ] Perguntas prováveis preparadas (métrica, teste, erros, uso indevido)

---

## Antes do PR

```bash
python3 scripts/check_entrega.py --grupo grupo-NN --entrega E7 --strict
git status --short          # nada fora da pasta do grupo
git log --oneline | head    # mensagens [GNN] tipo: descricao
```
