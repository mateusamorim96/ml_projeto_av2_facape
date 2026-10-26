# 📊 Qual teste estatístico usar

> Escolha pelo **número de modelos** e pelo **tipo de medição**. A regra que não
> muda: folds **idênticos** entre modelos (comparação pareada).

---

## 1. Tabela de decisão

| Situação | Teste | Alternativa conservadora |
| -------- | ----- | ------------------------ |
| 2 modelos, métrica contínua por fold (F1, AUC, RMSE) | **Wilcoxon signed-rank** | t pareado corrigido (Nadeau–Bengio) |
| 2 modelos, acerto/erro no **mesmo** conjunto de teste | **McNemar** | McNemar com correção de continuidade |
| ≥ 3 modelos, métricas por fold | **Friedman + post-hoc** | ANOVA de medidas repetidas (se normalidade) |
| ≥ 3 modelos, post-hoc par a par | **Nemenyi** (todos contra todos) ou **Bonferroni–Dunn** (contra o campeão) | Holm |
| 1 modelo vs baseline teórico | teste binomial / bootstrap | — |
| Métrica com distribuição desconhecida e amostra pequena | **bootstrap** (10 mil reamostragens) | — |

> Regra prática do curso: **≥ 3 modelos → Friedman**. Comparar 8 modelos com 28
> testes t infla o falso positivo; Friedman + post-hoc resolve isso.

---

## 2. O que reportar (sempre os três)

| Item | Formato no artigo | Por quê |
| ---- | ----------------- | ------- |
| Média e dispersão | `F1 = 0,842 ± 0,017` (média ± desvio em 10×5 folds) | Mostra estabilidade, não um número solto |
| p-valor | `p = 0,003` (Wilcoxon, bilateral, n = 50 folds) | Mostra que a diferença não é ruído |
| Tamanho de efeito / IC | `ΔF1 = 0,031 [0,012; 0,050]` | Mostra se a diferença **importa** |
| Correção múltipla | `α = 0,05/3 = 0,017 (Bonferroni)` | Evita p-hacking por comparação repetida |

Frase-modelo para o artigo:

> “O Gradient Boosting superou o baseline linear em F1 (0,842 ± 0,017 vs
> 0,795 ± 0,024; Wilcoxon, n = 50 folds, p < 0,001, Δ = 0,047 [0,031; 0,063]).
> A diferença é estável, porém concentrada na classe minoritária de municípios
> com subnotificação.”

---

## 3. Protocolo mínimo de validação

```text
1. Fixe a semente (SEED) e o split externo (holdout final, 20%).
2. CV repetida: RepeatedStratifiedKFold(n_splits=5, n_repeats=10) → 50 medidas.
3. Todos os modelos veem os MESMOS folds (mesmo objeto de CV, mesma seed).
4. Transformações dentro do Pipeline: fit só no treino de cada fold.
5. Ajuste de hiperparâmetros em CV interna (nested), nunca no teste.
6. O holdout é aberto UMA vez, no final, para confirmar.
```

Sem esses seis passos, o teste estatístico mede a mesma coisa que mediria um
empate técnico: nada.

---

## 4. Erros que anulam o teste

| Erro | Consequência |
| ---- | ------------ |
| Folds diferentes entre modelos | comparação não é pareada; o teste perde validade |
| Reportar só o melhor fold | viés de seleção |
| Rodar 30 comparações e reportar a que deu p < 0,05 | falso positivo garantido (sem correção) |
| Escolher hiperparâmetro no conjunto de teste | vazamento; métrica otimista |
| Normalizar antes do split | vazamento; métrica otimista |
| Trocar de métrica depois de ver o resultado | HARKing; a pergunta vira “qual métrica me favorece” |
| Concluir superioridade com p = 0,049 e Δ = 0,002 | significância estatística ≠ relevância prática |
