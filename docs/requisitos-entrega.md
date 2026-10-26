# 📦 Requisitos de Entrega — E0 a E8

> Cada entrega é **acumulativa**: a E4 inclui tudo da E1–E3. A CI valida a
> estrutura da entrega declarada no título do PR
> (`[G03] Entrega E4 — Tema`).

Validação local:

```bash
python3 scripts/check_entrega.py --grupo grupo-03 --entrega E4
```

---

## Cronograma

| **Entrega** | **Semana** | **Conteúdo** | **Peso** |
| :---------- | :--------- | :----------- | :------- |
| E0 | 0 | Formação do grupo (até 4) e escolha da ODS | — |
| E1 | 1 | `docs/proposta.md`: ODS, meta, tema, pergunta e decisão | 5% |
| E2 | 2 | Dataset auditado + dicionário de dados + análise de licença | 10% |
| E3 | 3 | EDA (5 visualizações) + pipeline de preparação executável | 10% |
| E4 | 4 | Baseline + 3 famílias de modelos + tabela comparativa preliminar | 10% |
| E5 | 5 | Protocolo de CV, testes estatísticos e gráficos com IC | 15% |
| E6 | 6 | Repositório completo + Docker funcional + README executivo | 20% |
| E7 | 7 | Artigo final + slides | 20% |
| E8 | 8 | Apresentação e defesa | 10% |

---

## Critérios de aceite por entrega

### E0 — Grupo e ODS (sem nota)

- Grupo de até **4 integrantes**, com papéis definidos.
- ODS escolhida (uma das 17) e meta numerada.
- Pasta criada com `scripts/novo_grupo.py` e código `GNN` registrado na issue
  “Entrega de Grupo”.

### E1 — Proposta (5%)

Arquivo: `docs/proposta.md`.

- [ ] ODS + **meta numerada** (ex.: meta 6.1) e justificativa de relevância local.
- [ ] Tema delimitado (o que **não** está no escopo também).
- [ ] Pergunta de ML falsificável.
- [ ] **Decisão**: “se o modelo indicar X, a equipe Y fará Z”.
- [ ] Público/beneficiário identificado.
- [ ] Tipo de aprendizado proposto (supervisionado/não supervisionado) e métrica
      principal com justificativa (por que não acurácia, se for o caso).
- [ ] Riscos iniciais (dados, viés, privacidade) e o que faria o projeto mudar de
      rumo.

### E2 — Dados (10%)

Arquivos: `docs/dicionario-de-dados.md` (+ atualização do README).

- [ ] Fonte identificável (URL + instituição), data de acesso e **licença**.
- [ ] Critério “não-toy” comprovado (≥ 5.000 registros **ou** ≥ 40 atributos
      **ou** dado não tabular), com números.
- [ ] Tabela de variáveis: nome, tipo, unidade, faixa, % de nulos, origem.
- [ ] Variável-alvo definida e **não trivial** (justificar por que não é cópia de
      coluna nem regra determinística).
- [ ] Verificação de LGPD: existe dado pessoal? Como foi tratado (agregação,
      remoção, anonimização)?
- [ ] `data/raw/` **não** versionado; hash/checksum do arquivo registrado.

### E3 — EDA e preparação (10%)

- [ ] `notebooks/01-eda-*.ipynb` com **5 visualizações** , cada uma com uma frase
      de conclusão (“o que isso muda na modelagem”).
- [ ] `src/pipeline.py` executável que lê `configs/base.yaml` e gera
      `data/processed/` (ou equivalente documentado).
- [ ] Tratamento de nulos documentado (por quê, não só “fillna(0)”).
- [ ] Nenhuma transformação ajustada no dataset completo (vazamento): split antes
      do `fit`.
- [ ] Desbalanceamento diagnosticado (proporção da classe alvo).

### E4 — Modelagem (10%)

- [ ] Baseline interpretável implementado e medido.
- [ ] **Três famílias** distintas (ex.: linear, árvore, distância/ensemble).
- [ ] `experiments/runs.csv` com ≥ 3 execuções: modelo, hiperparâmetros, seed,
      métrica de treino e de validação.
- [ ] Tabela comparativa preliminar em `reports/tables/`.
- [ ] Ajuste de hiperparâmetros sem tocar o conjunto de teste.

### E5 — Comparação estatística (15%)

- [ ] `docs/decisoes-tecnicas.md` com o protocolo: tipo de CV, número de
      repetições, folds idênticos entre modelos.
- [ ] Métrica reportada como média ± desvio em CV **repetida**.
- [ ] Teste estatístico escolhido com justificativa (tabela de decisão em
      `docs/decisoes-tecnicas.md`).
- [ ] p-valor **e** tamanho de efeito **e** intervalo de confiança.
- [ ] ≥ 3 figuras em `reports/figures/` (comparação com barras de erro, matriz de
      confusão/curva, importância de atributos ou resíduos).
- [ ] Discussão honesta: a diferença entre o campeão e o segundo colocado importa
      na prática?

### E6 — Repositório, Docker e README (20%)

- [ ] Árvore conforme [`estrutura-projeto.md`](estrutura-projeto.md).
- [ ] `requirements.txt` com todas as versões `==`.
- [ ] `Dockerfile` com base fixada, `CMD`/`ENTRYPOINT` e build funcionando.
- [ ] `docker build -t grupo-NN .` + `docker run --rm grupo-NN` executam o
      pipeline ponta a ponta em ambiente limpo.
- [ ] README executivo com: ODS e problema, decisão, dados e licença, como
      reproduzir (com tempo estimado), resultados principais, limitações,
      estrutura do repositório e usos inadequados.
- [ ] `reports/environment.json` com versões e hash do commit.
- [ ] Sementes fixadas e propagadas.
- [ ] **≥ 10 commits** ao longo das 4 semanas, com mensagens descritivas e
      presença de todos os integrantes.

### E7 — Artigo e slides (20%)

- [ ] `article/artigo.tex` compilando, 4–8 páginas, ≥ 8 referências em
      `referencias.bib`.
- [ ] Estrutura IMRaD: introdução, métodos, resultados, discussão, conclusão.
- [ ] **Todas** as tabelas e figuras geradas por script (nada digitado à mão).
- [ ] Declaração de reprodutibilidade: link do repositório, tag `v1.0-entrega`,
      comando de execução e imagem Docker.
- [ ] Resultados por subgrupo (quando o modelo afeta pessoas) e limitações.
- [ ] `slides/` com 8–12 slides no roteiro: ODS/decisão → dados → método →
      resultados com IC → interpretação → limitações → demo do `docker run` →
      o que faria diferente.

### E8 — Apresentação e defesa (10%)

- [ ] 10 minutos de apresentação + 5 de arguição, dentro do tempo.
- [ ] Demonstração do `docker run` (ao vivo ou vídeo de 30 s).
- [ ] **Todos** os integrantes sabem explicar qualquer parte (código, dados,
      resultado, limitação). A nota é individual dentro do grupo.
- [ ] Perguntas esperadas: por que essa métrica? por que esse teste? o que o
      modelo erra? qual o risco de uso indevido?

---

## Rubrica de avaliação

| **Critério** | **Peso** | **Atende** | **Supera** |
| :----------- | :------- | :--------- | :--------- |
| ODS, tema e formulação | 10% | ODS e meta claras, decisão definida | problema local justificado, hipótese falsificável |
| Dados: origem, qualidade, ética | 15% | dataset real e documentado | auditoria de viés e limitações discutidas |
| Preparação sem vazamento | 10% | pipeline sklearn correto | decisões justificadas por evidência da EDA |
| Modelagem e ajuste | 15% | 3 famílias + baseline | busca aninhada, seleção de atributos |
| Comparação estatística | 15% | CV + teste + IC | efeito prático, correção múltipla, discussão |
| Interpretação e erros | 10% | importância + 3 erros analisados | análise por subgrupo e recomendação de uso |
| Artigo | 10% | IMRaD, 8 referências, números coerentes | texto crítico, comparação com literatura |
| Reprodutibilidade (Docker + GitHub) | 10% | comando único em ambiente limpo | CI automatizado e imagem publicada |
| Apresentação | 5% | dentro do tempo, clara | defesa sólida e demonstração ao vivo |

---

## Anti-padrões

Cada item abaixo gera **desconto direto** na rubrica:

- Dataset didático (Iris, Titanic e afins) ou dados sintéticos do próprio grupo.
- Reportar apenas acurácia em problema desbalanceado.
- “Melhor modelo” escolhido por diferença de terceira casa decimal, sem teste.
- Ajustar hiperparâmetros olhando o conjunto de teste.
- Notebook único com 200 células fora de ordem e resultados irreprodutíveis.
- Tabela de resultados digitada à mão, divergente do código.
- README genérico (“projeto de ML”) sem instrução de execução.
- `Dockerfile` que não constrói (`latest` sem pin, dependência faltante, caminho
  absoluto).
- Artigo sem números, gráfico sem unidade ou sem legenda.
- Conclusão que promete impacto social não sustentado pelos resultados.
- `data/raw/` versionado com dados pessoais.
- Histórico de commits com uma única mensagem `update` no último dia.

---

## Checklist final (antes de abrir o PR da E7/E8)

```bash
# 1. estrutura e conteúdo
python3 scripts/check_entrega.py --grupo grupo-NN --entrega E7 --strict

# 2. ambiente limpo (o teste que vale)
docker build -t grupo-NN . && docker run --rm grupo-NN

# 3. histórico
git log --oneline | head -20
git tag v1.0-entrega && git push origin v1.0-entrega
```
