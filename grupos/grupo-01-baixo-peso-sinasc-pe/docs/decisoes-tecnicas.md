# Decisões Técnicas — G01 · Baixo peso ao nascer (SINASC/PE)

> Registro das decisões que a banca vai perguntar. Formato curto: decisão,
> alternativa rejeitada, evidência.

## 1. Protocolo de validação (E5)

| Item                               | Decisão                                       |
| ---------------------------------- | --------------------------------------------- |
| Split externo (holdout)            | temporal: 2024 inteiro (decidido na E2, ver seção 4) |
| Esquema de CV                      | preencher (ex.: RepeatedStratifiedKFold 5×10) |
| Folds compartilhados entre modelos | sim (obrigatório)                             |
| Transformações                     | dentro do `Pipeline`, `fit` só no treino      |
| Ajuste de hiperparâmetros          | preencher (grid/random/bayes; nested CV)      |
| Métrica de seleção                 | preencher                                     |

## 2. Modelos comparados

| Família  | Implementação | Justificativa            | Hiperparâmetros testados |
| -------- | ------------- | ------------------------ | ------------------------ |
| baseline | preencher     | referência interpretável |                          |
| 1        | preencher     |                          |                          |
| 2        | preencher     |                          |                          |
| 3        | preencher     |                          |                          |

## 3. Teste estatístico (E5)

- **Teste escolhido:** preencher — ver
  [`docs/templates/tabela-teste-estatistico.md`](../../../docs/templates/tabela-teste-estatistico.md)
- **Por que esse teste:** preencher (número de modelos, tipo de medida,
  pareamento)
- **Correção múltipla:** preencher
- **Tamanho de efeito:** preencher
- **Intervalo de confiança:** preencher (método: bootstrap / t)

## 4. Decisões de dados

Decisões tomadas na E2. As evidências estão em `docs/dicionario-de-dados.md` e em `reports/tables/tabela-auditoria-*.csv`.

| Decisão | Alternativa rejeitada | Evidência |
| ------- | --------------------- | --------- |
| Desenvolvimento em 2019–2023 e teste temporal em 2024, usado uma única vez | holdout aleatório de 20% sobre todos os anos | a prevalência sobe de cerca de 7,8% (2015–2020) para cerca de 8,7% (2022–2024) (`tabela-auditoria-resumo-anos.csv`). O teste temporal reproduz o uso real: treinar com o passado e prever o ano seguinte |
| Excluir 2015–2018 da modelagem (só auditoria e EDA) | usar os 10 anos | anos mais distantes do patamar atual de prevalência; a população de desenvolvimento já tem 585.522 registros (`tabela-auditoria-recorte.csv`) |
| População = gestação única com mês de início do pré-natal registrado | modelar todos os nascidos vivos | é quem passa pela decisão na captação (`src/data/populacao.py`; fluxo em `tabela-auditoria-populacao.csv`) |
| Excluir gestações múltiplas | mantê-las e agrupar os gêmeos com `GroupKFold` | 59,38% de baixo peso contra 7,14% na gestação única (`tabela-auditoria-excluidos.csv`): o modelo ganharia desempenho com um risco que a equipe já reconhece, já que a gestação gemelar é de alto risco por definição (Ministério da Saúde, *Manual de gestação de alto risco*, 2022, cap. 17). Os registros do mesmo parto vazariam entre folds, e não há identificador da mãe para agrupar |
| Excluir registros sem mês de início do pré-natal | imputar `MESPRENAT` | prevalência de 11,72% no grupo (`tabela-auditoria-excluidos.csv`): o “ausente” carrega sinal, mas não existe na captação, em que o mês é conhecido |
| Manter 2020 e 2021 (pandemia) no desenvolvimento | excluir os dois anos | prevalência e completude sem quebra nesses anos (`tabela-auditoria-resumo-anos.csv`); o desempenho por ano será comparado na E5 |
| Só atributos conhecidos na captação da gestante | usar todas as colunas da DN | regra de vazamento; colunas excluídas e motivo de cada uma em `src/data/esquema.py` e na tabela de variáveis do dicionário |
| Excluir `CONSPRENAT`, `CONSULTAS` e `KOTELCHUCK`; usar `MESPRENAT` | usar o nº de consultas, preditor forte | o nº de consultas depende da duração da gestação: um parto prematuro tem menos consultas por ter sido mais curto |
| Excluir `SEXO` e `RACACOR` do bebê | usar como atributo | desconhecidos na captação; a raça/cor da **mãe** (`RACACORMAE`) é usada |
| Excluir `IDADEPAI` | imputar | 80,0% de nulos (`tabela-auditoria-variaveis.csv`), acima do limite de 60% do template |
| Excluir registros com `PESO` ausente ou fora de 300–6.500 g | manter e imputar o alvo | 556 registros (0,04%); alvo indefinido ou provável erro de digitação (`tabela-auditoria-qualidade.csv`) |
| Remover as 33 duplicatas (mantendo uma cópia) | manter | idênticas em todas as colunas fora as internas, inclusive hora e peso do nascimento, o que gêmeos quase nunca seriam. Mantidas, as cópias poderiam cair em folds diferentes e inflar a validação (`tabela-auditoria-qualidade.csv`) |
| Município como mesorregião do IBGE (5 categorias), mais um indicador de Petrolina | usar o código do município (186 categorias) | reduz a cardinalidade e o risco de reidentificação (LGPD) |
| Suprimir cruzamentos com menos de 10 registros nas tabelas publicadas | publicar todas as células | LGPD; aplicado em `src/data/auditoria.py` |

### Preparação e EDA (E3)

As figuras e os dados de cada uma estão em `reports/figures/figura-eda-*.png` e `reports/tables/tabela-eda-*.csv`; a leitura completa está em `notebooks/01-eda-baixo-peso.ipynb`. A EDA usa só o desenvolvimento (2019–2023).

| Decisão | Alternativa rejeitada | Evidência |
| ------- | --------------------- | --------- |
| Limpeza por registro (duplicatas, população, alvo, códigos “ignorado” e valores implausíveis → ausente) antes do split; tudo que aprende dos dados fica no `Pipeline` | limpar e imputar no conjunto inteiro | as regras de `src/data/preparar.py` não calculam nenhuma estatística, então não vazam; imputação, splines e one-hot são ajustados só no treino de cada fold (`src/features/preprocessamento.py`) |
| Split temporal gravado na etapa `dados`: `desenvolvimento.pkl` (2019–2023) e `teste.pkl` (2024) | separar o teste só na modelagem | o teste fica isolado desde a preparação, e a etapa `features` falha se aparecer um ano fora do desenvolvimento |
| Checagem automática de vazamento no pipeline | conferir a lista de colunas à mão | `conferir_vazamento` em `src/pipeline.py` falha se uma coluna descartada, de filtro, o alvo ou o ano chegar ao modelo |
| Não descartar registros com atributo ausente | remover linhas incompletas | menos de 4% de ausentes, mas com prevalência menor (5,0%–5,8% contra 6,96%): descartar tiraria um grupo de risco diferente (figura 2) |
| Categórico ausente → categoria própria `ignorado` | imputar a moda | “ignorado” tem a menor prevalência em escolaridade, raça/cor e ocupação (figuras 2 e 6); a moda o misturaria a um grupo de risco diferente |
| Idade da mãe com splines (5 nós, grau 3) | idade linear ou em faixas fixas | curva em U: 15,19% aos 13 anos, 5,88% aos 26, 8,52% aos 40 (figura 3) |
| `MESPRENAT` como categoria | mês como número | sobe de 5,43% (mês 1) para 8,66% (mês 5) e cai para 3,88% (mês 9), sem relação linear (figura 4) |
| Histórico obstétrico com teto no percentil 99 e como categoria | contagens como número | relações em U (primeira gestação 8,15%, uma ou duas anteriores cerca de 5,97%) e caudas raras (figura 5) |
| Ocupação pelo grande grupo da CBO, com os códigos especiais `9999xx` separados | 1º dígito para todos os códigos | o 1º dígito juntaria os códigos especiais ao grande grupo 9 (manutenção); eles têm prevalências entre 6,47% e 9,59% (figura 6) |
| Desbalanceamento tratado no modelo (pesos de classe ou limiar), sem reamostrar | sobreamostragem (SMOTE ou similar) | cerca de 7% de positivos e 585.505 registros (figura 1): há casos positivos suficientes, e a reamostragem distorceria a calibração das probabilidades. A escolha final fica para a E4 |

## 5. Decisões descartadas (e por quê)

- **Região imediata do IBGE no lugar da mesorregião:** mais categorias, sem ganho para a análise por
  subgrupo, que já usa a mesorregião.
- **`CODPAISRES` como filtro de residentes no Brasil:** a coluna só existe em 2015 e 2017, e o arquivo
  `DNPE` já é selecionado por residência em Pernambuco.
- **Anos 2025 e 2026:** ainda estão na pasta `PRELIM` do DATASUS e podem mudar. Usá-los quebraria a
  reprodutibilidade garantida pelo registro de hashes.

## 6. Riscos residuais

- preencher (o que ainda pode invalidar o resultado)
- preencher (o que faríamos com mais tempo/dados)
