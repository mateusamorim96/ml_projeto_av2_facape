# Decisões Técnicas — G02

> Registro das decisões que a banca vai perguntar. Formato curto: decisão,
> alternativa rejeitada, evidência. As seções 1 (parcial) e 4 foram preenchidas
> na E3; as demais são completadas na E4/E5.

## 1. Protocolo de validação (E5)

| Item | Decisão |
| ---- | ------- |
| Split externo (holdout) | 20 % dos municípios (292 de 1.458), seed 42, estratificado por quintis do alvo de 2024 — implementado em `src/features/preparacao.py` (E3) |
| Esquema de CV | KFold repetido 5 × 10 **dentro do treino** (`configs/base.yaml → validacao`); implementação na E5 |
| Folds compartilhados entre modelos | sim (obrigatório) |
| Transformações | dentro do `Pipeline`, `fit` só no treino (E3: `construir_preprocessador`) |
| Ajuste de hiperparâmetros | a definir na E4 (CV interna de 3 folds sobre o treino; nunca no teste) |
| Métrica de seleção | MAE (p.p.); RMSE secundária |

**Por que split por município e não por tempo:** só existe uma transição
(2023 → 2024). O “tempo” já está embutido no desenho (preditores de `t`, alvo de
`t+1`), então o holdout separa **municípios**: o modelo é testado em municípios
que nunca viu. Não é validação em anos futuros (limitação registrada na E2).

## 2. Modelos comparados

| Família | Implementação | Justificativa | Hiperparâmetros testados |
| ------- | ------------- | ------------- | ------------------------ |
| baseline | persistência (IAG2013 de 2023) | referência da pergunta da E1 | — |
| 1 | a definir na E4 | | |
| 2 | a definir na E4 | | |
| 3 | a definir na E4 | | |

Indicações da EDA para a E4 (ver `notebooks/01-eda-perdas-agua.ipynb`): linear
**regularizado** por causa da colinearidade (fig. 5); árvores/ensembles lidam
bem com caudas e ausências; kNN exige a padronização já feita.

## 3. Teste estatístico (E5)

- **Teste escolhido:** a definir na E5 — ver
  [`docs/templates/tabela-teste-estatistico.md`](../../../docs/templates/tabela-teste-estatistico.md)
- **Por que esse teste:** a definir na E5 (número de modelos, tipo de medida, pareamento)
- **Correção múltipla:** a definir na E5
- **Tamanho de efeito:** a definir na E5
- **Intervalo de confiança:** a definir na E5 (método: bootstrap / t)

## 4. Decisões de dados (E3)

Todas implementadas em `src/data/carregar.py` e `src/features/preparacao.py`,
parametrizadas em `configs/base.yaml` e executadas por `python -m src.pipeline`.
As figuras citadas estão em `reports/figures/` e no notebook de EDA.

| Decisão | Alternativa rejeitada | Evidência |
| ------- | --------------------- | --------- |
| **Split antes de qualquer `fit`**: treino 1.166 / teste 292, estratificado por quintis do alvo | split aleatório simples (pode desbalancear a cauda de perdas altas num teste de 292) | `reports/tables/preparacao-split.csv`; % acima de 40 %: base 42,8 / treino 43,0 / teste 42,1 |
| Regra de exclusão por ausentes (> 20 %) medida **só no treino** | medir na base inteira (como na E2), o que deixa o teste influenciar a escolha de colunas | `reports/tables/preparacao-selecao-preditores.csv`: exclui IAG0005 (41,9 %) e IAG3002 (40,6 %), mesmo resultado da E2 |
| “Não Calc.” → ausente (NaN), nunca zero | `fillna(0)`: zero é valor real para vários indicadores (ex.: 0 % de setorização) e criaria municípios falsos com “perda zero” | dicionário de dados, seção 4 |
| **Imputação pela mediana do treino** | média (distorcida pelas caudas: 33 de 53 preditores com \|assimetria\| > 2); remover linhas (perde municípios de perda alta) | fig. 3 e 4; `preparacao-tratamento-preditores.csv` (coluna `valor_imputado_treino`) |
| **Indicador binário de ausência** por coluna com NaN no treino (41 colunas extras) | só imputar (perde o sinal) | fig. 3: sem IAG3001 a perda mediana em 2024 é 54,6 % vs. 34,7 % com o dado; ausência concentrada em MA e SE |
| **Winsorização P1–P99** com limites do treino (`RecortePercentil`) | remover outliers (amostra pequena: 28 linhas/preditor); `log` (há zeros e negativos, ex.: IAG2005 = −719) | fig. 4; limites e nº de valores recortados por coluna em `preparacao-tratamento-preditores.csv` |
| **Padronização** (`StandardScaler`) após recorte e imputação | sem escala (indicadores em R$/empregado.ano dominariam modelos lineares regularizados e kNN) | fig. 4; checagem do notebook (seção 7): média 0 no treino, ≠ 0 no teste |
| `alvo_t` (IAG2013 de 2023) sempre como preditor; identificadores, UF e prestador fora | usar UF como preditor no modelo principal | fig. 2 (r ≈ 0,78); fig. 6: UF entra só como análise de sensibilidade na E4 |
| Manter os 20 pares extremos e os 54 saltos do treino na base | removê-los agora (decisão sobre o alvo que depende do resultado) | fig. 2: saltos = 4,6 % das linhas e ~27 % do erro da persistência; sensibilidade na E5 |
| Diagnóstico de desbalanceamento com limites 30/40/50 % | escolher o limite de alerta para melhorar métrica | `preparacao-desbalanceamento-alvo.csv`: 64 / 43 / 30 % acima; sem reamostragem |

## 5. Decisões descartadas (e por quê)

- **Seleção de atributos por correlação neste notebook:** descartada; a
  redundância (IAG2011 × IAG2012 = −1,00; IAG2010 × alvo de 2023 = −0,97) é real,
  mas qualquer seleção que olhe o alvo precisa ocorrer **dentro da CV** (E4/E5)
  para não vazar informação dos folds de validação.
- **Validação temporal:** impossível com uma única transição anual; ver seção 1.
- **Planilhas de informações (GTA/FN) como preditores:** fora da E3; se
  entrarem depois, só as de 2023 (os campos de 2024 compõem o próprio alvo).

## 6. Riscos residuais

- Uma única transição anual e critério de não cálculo diferente em 2023: o
  resultado não vale como previsão para anos futuros.
- Os valores implausíveis podem ser erros de informação; a winsorização limita o
  impacto, mas não corrige o dado. Os saltos no alvo podem ser mudança de
  informação, não de operação, e dominam o erro.
- Piauí sub-representado (17 municípios): nenhuma conclusão vale para essa UF.
- 41 indicadores de ausência são em parte redundantes (11 indicadores faltam
  juntos para os mesmos 21 municípios do treino, 1,8 %); a E4 pode desligá-los
  (`indicador_ausencia: false`) como sensibilidade.
