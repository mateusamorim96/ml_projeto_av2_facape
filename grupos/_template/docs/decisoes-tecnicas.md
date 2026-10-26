# Decisões Técnicas — GXX (preencher)

> Registro das decisões que a banca vai perguntar. Formato curto: decisão,
> alternativa rejeitada, evidência.

## 1. Protocolo de validação (E5)

| Item | Decisão |
| ---- | ------- |
| Split externo (holdout) | preencher (ex.: 20% estratificado, seed 42) |
| Esquema de CV | preencher (ex.: RepeatedStratifiedKFold 5×10) |
| Folds compartilhados entre modelos | sim (obrigatório) |
| Transformações | dentro do `Pipeline`, `fit` só no treino |
| Ajuste de hiperparâmetros | preencher (grid/random/bayes; nested CV) |
| Métrica de seleção | preencher |

## 2. Modelos comparados

| Família | Implementação | Justificativa | Hiperparâmetros testados |
| ------- | ------------- | ------------- | ------------------------ |
| baseline | preencher | referência interpretável | |
| 1 | preencher | | |
| 2 | preencher | | |
| 3 | preencher | | |

## 3. Teste estatístico (E5)

- **Teste escolhido:** preencher — ver
  [`docs/templates/tabela-teste-estatistico.md`](../../../docs/templates/tabela-teste-estatistico.md)
- **Por que esse teste:** preencher (número de modelos, tipo de medida, pareamento)
- **Correção múltipla:** preencher
- **Tamanho de efeito:** preencher
- **Intervalo de confiança:** preencher (método: bootstrap / t)

## 4. Decisões de dados

| Decisão | Alternativa rejeitada | Evidência |
| ------- | --------------------- | --------- |
| preencher (ex.: imputar mediana) | | figura/tabela que sustenta |

## 5. Decisões descartadas (e por quê)

<!-- Registre o que foi tentado e abandonado: modelos que não couberam no tempo,
atributos que vazaram, métricas que não conversavam com a decisão. A banca
valoriza mais o “por que não” do que o “o que usei”. -->

## 6. Riscos residuais

- preencher (o que ainda pode invalidar o resultado)
- preencher (o que faríamos com mais tempo/dados)
