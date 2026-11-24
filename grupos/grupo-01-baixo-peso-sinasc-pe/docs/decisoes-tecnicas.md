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
| Excluir 2015–2018 da modelagem (só auditoria e EDA) | usar os 10 anos | anos mais distantes do patamar atual de prevalência; o desenvolvimento já tem 621.404 registros (`tabela-auditoria-recorte.csv`) |
| Manter 2020 e 2021 (pandemia) no desenvolvimento | excluir os dois anos | prevalência e completude sem quebra nesses anos (`tabela-auditoria-resumo-anos.csv`); o desempenho por ano será comparado na E5 |
| Só atributos conhecidos na captação da gestante | usar todas as colunas da DN | regra de vazamento; colunas excluídas e motivo de cada uma em `src/data/esquema.py` e na tabela de variáveis do dicionário |
| Excluir `CONSPRENAT`, `CONSULTAS` e `KOTELCHUCK`; usar `MESPRENAT` | usar o nº de consultas, preditor forte | o nº de consultas depende da duração da gestação: um parto prematuro tem menos consultas por ter sido mais curto |
| Excluir `SEXO` e `RACACOR` do bebê | usar como atributo | desconhecidos na captação; a raça/cor da **mãe** (`RACACORMAE`) é usada |
| Excluir `IDADEPAI` | imputar | 80,0% de nulos (`tabela-auditoria-variaveis.csv`), acima do limite de 60% do template |
| Excluir registros com `PESO` ausente ou fora de 300–6.500 g | manter e imputar o alvo | 556 registros (0,04%); alvo indefinido ou provável erro de digitação (`tabela-auditoria-qualidade.csv`) |
| Remover as 33 duplicatas (mantendo uma cópia) | manter | idênticas em todas as colunas fora as internas, inclusive hora e peso do nascimento, o que gêmeos quase nunca seriam. Mantidas, as cópias poderiam cair em folds diferentes e inflar a validação (`tabela-auditoria-qualidade.csv`) |
| Município como mesorregião ou região imediata do IBGE, mais um indicador de Petrolina | usar o código do município (186 categorias) | reduz a cardinalidade e o risco de reidentificação (LGPD) |
| Suprimir cruzamentos com menos de 10 registros nas tabelas publicadas | publicar todas as células | LGPD; aplicado em `src/data/auditoria.py` |

## 5. Decisões descartadas (e por quê)

- **`CODPAISRES` como filtro de residentes no Brasil:** a coluna só existe em 2015 e 2017, e o arquivo
  `DNPE` já é selecionado por residência em Pernambuco.
- **Anos 2025 e 2026:** ainda estão na pasta `PRELIM` do DATASUS e podem mudar. Usá-los quebraria a
  reprodutibilidade garantida pelo registro de hashes.

## 6. Riscos residuais

- preencher (o que ainda pode invalidar o resultado)
- preencher (o que faríamos com mais tempo/dados)
