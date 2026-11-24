# Dicionário de Dados — G01 · SINASC Pernambuco

> Entrega E2. Auditoria do dataset: de onde ele veio, o que significa cada coluna e o que não pode ser usado.
>
> Os blocos entre os marcadores `auditoria:*` são **gerados por script** e reescritos a cada execução de
> `python -m src.data.auditoria --config configs/base.yaml`. Nenhum número desses blocos foi digitado à mão.
> As tabelas também ficam em `reports/tables/e2-*.csv`.

## 1. Identificação

| Campo | Valor |
| ----- | ----- |
| Fonte | Ministério da Saúde — Sistema de Informações sobre Nascidos Vivos (SINASC), gerido pela CGIAE/DASNT/SVS e distribuído pelo DATASUS |
| URL | `ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Dados/DNRES/DNPE{ano}.dbc` (um arquivo por ano, residentes em Pernambuco). Página do conjunto: <https://dadosabertos.saude.gov.br/dataset/sistema-de-informacao-sobre-nascidos-vivos-sinasc> |
| Documentação | “Estrutura do SINASC”, CGIAE/DASNT/SVS/MS, atualizada em 12/2019: `ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Doc/Estrutura_SINASC_para_CD.pdf` |
| Tabela auxiliar | Municípios de Pernambuco com micro e mesorregião — API de Localidades do IBGE: <https://servicodados.ibge.gov.br/api/v1/localidades/estados/26/municipios> |
| Data de acesso | 2026-11-23 (registrada por arquivo em `configs/hashes-dados-brutos.csv`) |
| Recorte | UF de residência = PE; anos definitivos de 2015 a 2024. Os de 2025 e 2026 ainda estão na pasta `PRELIM` do DATASUS e não foram usados |
| Licença | Creative Commons Atribuição-SemDerivações 3.0 (CC BY-ND 3.0), declarada para o portal inteiro. O conjunto não declara licença própria (ver seção 7) |
| Base legal (LGPD) | Dados publicados pelo próprio Ministério da Saúde de forma anonimizada. Dados anonimizados não são considerados dados pessoais (Lei 13.709/2018, art. 12). Política de Dados Abertos do Executivo federal (Decreto 8.777/2016) |
| Hash dos arquivos | SHA-256 de cada arquivo na tabela abaixo e em `configs/hashes-dados-brutos.csv` |
| Registros e atributos | ver tabela abaixo (registros por ano; 61 colunas no total, das quais 59 ou 60 têm dado em cada ano) |
| Arquivo versionado? | não — `data/raw/` é ignorado pelo Git; o download é refeito por `python -m src.data.download` |

<!-- auditoria:arquivos:inicio -->
| arquivo | bytes | registros | colunas com dado | sha256 |
| --- | --- | --- | --- | --- |
| DNPE2015.dbc | 10.353.625 | 145.024 | 59 | `3d249eeea470260075d037f27e14bedba8e7ab155d35f160b2a385b5503aa8fa` |
| DNPE2016.dbc | 6.624.317 | 130.733 | 60 | `3505bad6c6c32b1b8c66c26d6e8b0c3f102a3af8785e4ba07347080ae5ec946c` |
| DNPE2017.dbc | 9.903.887 | 135.932 | 59 | `42c4b10ae8700054cbed6f22637a9e53bc574a1e057f9c9abc9ba5b2aa24dd20` |
| DNPE2018.dbc | 6.942.740 | 138.317 | 60 | `a366c341dc93731df84633d3543ba51f069d50701ed2023b8822538325d160f5` |
| DNPE2019.dbc | 6.701.467 | 133.359 | 60 | `980686801076d2acd7fb9ec67b4d46b971ed48b12e45070dab3e6d2d0174c9e0` |
| DNPE2020.dbc | 6.445.729 | 128.481 | 60 | `70a77c70b891a7255dade1bdf7213c9efcb4a45eb3b762594ffc98335eaadd58` |
| DNPE2021.dbc | 6.331.295 | 126.211 | 60 | `7c9e782e2616a4618a78794cedeefbd60469cee0ed9905ffbeee760763377d59` |
| DNPE2022.dbc | 5.894.169 | 117.437 | 60 | `0541cb17fc56582266b429406990e5da1e153917084db9b88d9a9dd93742efae` |
| DNPE2023.dbc | 5.810.363 | 116.175 | 60 | `ec0915c38460490f7f568acc3564c3e38a9a0e347e46f173634b7d0956547817` |
| DNPE2024.dbc | 5.544.754 | 110.827 | 60 | `413ab891ee289bd50d5078de2040565aaf411d1db1dd14797ec20eb733bd3656` |
<!-- auditoria:arquivos:fim -->

**Integridade:** o download nunca sobrescreve um arquivo existente e compara o SHA-256 com o registrado. Se o
DATASUS republicar um ano (o arquivo de 2016 foi republicado em 2025, por exemplo), a execução para com erro.

## 2. Critério “não-toy” (RQ-DAD-01)

| Critério | Situação | Evidência |
| -------- | -------- | --------- |
| (a) proveniência institucional documentada | **atende** | Ministério da Saúde/SVS, com dicionário oficial (seção 1) |
| (b) ≥ 5.000 registros ou ≥ 40 atributos | **atende** | mais de 1,2 milhão de registros e 61 colunas (tabela da seção 1) |
| (c) alvo não trivial | **atende** | seção 4: o peso é medido, não derivado de outra coluna, e as colunas que o antecipam foram excluídas |
| (d) desbalanceamento, ausentes, ruído ou heterogeneidade | **atende** | cerca de 8% de positivos; pesos implausíveis; prevalência muda entre anos e regiões (seções 4, 5 e 6) |
| (e) licença compatível com uso acadêmico | **atende, com ressalva** | seção 7 |

## 3. Variáveis

Tipos, códigos e descrições seguem o dicionário oficial. A coluna **uso** vem de `src/data/esquema.py`, que
é a mesma fonte usada pela preparação dos dados na E3. Percentuais calculados sobre 2015–2024.

<!-- auditoria:variaveis:inicio -->
| coluna | tipo | unidade | faixa observada | % nulos | % ignorado | descrição | uso | motivo / observação |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `PESO` | numerica | g | 100–7.000 | 0,0% | — | Peso ao nascer, verificado até a 5ª hora de vida | alvo | alvo = 1 se PESO < 2500 g |
| `IDADEMAE` | numerica | anos | 10–65 | 0,0% | 0,0% | Idade da mãe | atributo |  |
| `ESCMAE2010` | categorica | — | 0, 1, 2, 3, 4, 5 | 0,6% | 0,5% | Escolaridade da mãe (última série concluída), nível | atributo |  |
| `RACACORMAE` | categorica | — | 1, 2, 3, 4, 5 | 1,3% | — | Raça/cor da mãe | atributo | também usada na análise por subgrupo (RQ-ÉT-02) |
| `ESTCIVMAE` | categorica | — | 1, 2, 3, 4, 5 | 0,6% | 0,3% | Situação conjugal da mãe | atributo |  |
| `CODOCUPMAE` | categorica | — | 1.571 códigos | 4,2% | — | Ocupação da mãe (CBO 2002) | atributo | alta cardinalidade: agrupar pelo grande grupo da CBO na E3 |
| `QTDGESTANT` | numerica | gestações | 0–50 | 0,6% | 0,0% | Número de gestações anteriores | atributo |  |
| `QTDPARTNOR` | numerica | partos | 0–91 | 0,7% | 0,0% | Número de partos vaginais anteriores | atributo |  |
| `QTDPARTCES` | numerica | partos | 0–60 | 0,8% | 0,0% | Número de cesáreas anteriores | atributo |  |
| `QTDFILVIVO` | numerica | filhos | 0–30 | 0,6% | 0,0% | Número de filhos vivos | atributo |  |
| `QTDFILMORT` | numerica | perdas | 0–26 | 0,8% | 0,0% | Número de perdas fetais e abortos | atributo |  |
| `PARIDADE` | categorica | — | 0, 1 | 0,0% | 0,0% | Paridade, calculada pelo sistema a partir do histórico | atributo |  |
| `GRAVIDEZ` | categorica | — | 1, 2, 3 | 0,1% | 0,0% | Tipo de gravidez | atributo | supõe gestação múltipla já detectada (ultrassom) na captação — ameaça à validade |
| `MESPRENAT` | numerica | mês | 1–9 | 1,5% | 2,5% | Mês de gestação em que iniciou o pré-natal | atributo |  |
| `CODMUNRES` | categorica | — | 186 códigos | 0,0% | — | Município de residência da mãe (IBGE, 6 dígitos) | atributo | convertido em mesorregião/região imediata (IBGE) na E3; Petrolina = 261110 |
| `DTNASC` | data | — | ddmmaaaa | 0,0% | — | Data do nascimento | subgrupo | só confirma o ano do registro; a data em si não entra no modelo |
| `IDADEPAI` | numerica | anos | 1–98 | 80,0% | 0,0% | Idade do pai | descartada | mais de 60% de nulos (ver auditoria) |
| `CODPAISRES` | categorica | — | 1 | 21,9% | — | País de residência | descartada | existe só em 2015 e 2017; o arquivo já é de residentes em PE |
| `SEMAGESTAC` | numerica | semanas | 19–45 | 1,9% | — | Semanas de gestação | descartada | vazamento: só é conhecida no parto ou depois dele |
| `GESTACAO` | categorica | — | 1, 2, 3, 4, 5, 6, 9 | 1,9% | — | Semanas de gestação, agrupado (DN antiga) | descartada | vazamento: só é conhecida no parto ou depois dele |
| `TPMETESTIM` | categorica | — | 1, 2, 8, 9 | 1,9% | — | Método para estimar a idade gestacional | descartada | vazamento: só é conhecida no parto ou depois dele |
| `PARTO` | categorica | — | 1, 2, 9 | 0,1% | — | Tipo de parto | descartada | vazamento: só é conhecida no parto ou depois dele |
| `STTRABPART` | categorica | — | 1, 2, 9 | 0,7% | — | Trabalho de parto induzido | descartada | vazamento: só é conhecida no parto ou depois dele |
| `STCESPARTO` | categorica | — | 1, 2, 3, 9 | 6,5% | — | Cesárea antes do trabalho de parto | descartada | vazamento: só é conhecida no parto ou depois dele |
| `TPAPRESENT` | categorica | — | 1, 2, 3, 9 | 0,4% | — | Apresentação do recém-nascido | descartada | vazamento: só é conhecida no parto ou depois dele |
| `TPROBSON` | categorica | — | 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11 | 0,0% | — | Grupo de Robson (gerado a partir de dados do parto) | descartada | vazamento: só é conhecida no parto ou depois dele |
| `TPNASCASSI` | categorica | — | 1, 2, 3, 4, 9 | 0,3% | — | Profissional que assistiu o parto | descartada | vazamento: só é conhecida no parto ou depois dele |
| `LOCNASC` | categorica | — | 1, 2, 3, 4, 9 | 0,0% | — | Local de ocorrência do nascimento | descartada | vazamento: só é conhecida no parto ou depois dele |
| `CODMUNNASC` | categorica | — | 461 códigos | 0,0% | — | Município de ocorrência do nascimento | descartada | vazamento: só é conhecida no parto ou depois dele |
| `APGAR1` | numerica | — | 0–99 | 0,9% | — | Índice de Apgar no 1º minuto | descartada | vazamento: só é conhecida no parto ou depois dele |
| `APGAR5` | numerica | — | 0–99 | 0,8% | — | Índice de Apgar no 5º minuto | descartada | vazamento: só é conhecida no parto ou depois dele |
| `IDANOMAL` | categorica | — | 1, 2, 9 | 0,2% | — | Anomalia congênita detectada no nascimento | descartada | vazamento: só é conhecida no parto ou depois dele |
| `CODANOMAL` | texto | — | 2.138 códigos | 98,9% | — | Anomalias congênitas (CID-10) | descartada | vazamento: só é conhecida no parto ou depois dele |
| `HORANASC` | texto | — | 1.440 códigos | 0,1% | — | Hora do nascimento | descartada | vazamento: só é conhecida no parto ou depois dele |
| `SEXO` | categorica | — | 0, 1, 2 | 0,0% | — | Sexo do recém-nascido | descartada | característica do recém-nascido, desconhecida na captação |
| `RACACOR` | categorica | — | 1, 2, 3, 4, 5 | 1,2% | — | Raça/cor do recém-nascido | descartada | característica do recém-nascido, desconhecida na captação; usa-se RACACORMAE |
| `CONSPRENAT` | numerica | — | 0–99 | 1,1% | — | Número de consultas de pré-natal | descartada | vazamento: depende da duração da gestação |
| `CONSULTAS` | categorica | — | 1, 2, 3, 4, 9 | 0,1% | — | Consultas de pré-natal, agrupado (DN antiga) | descartada | vazamento: depende da duração da gestação |
| `KOTELCHUCK` | categorica | — | 1, 2, 3, 4, 5, 9 | 0,0% | — | Índice de adequação do pré-natal (usa nº de consultas) | descartada | vazamento: depende da duração da gestação |
| `DTNASCMAE` | data | — | ddmmaaaa | 0,3% | — | Data de nascimento da mãe | descartada | identificador ou data que permite reidentificação |
| `DTULTMENST` | data | — | ddmmaaaa | 41,8% | — | Data da última menstruação | descartada | identificador ou data que permite reidentificação |
| `CODESTAB` | categorica | — | 844 códigos | 0,5% | — | Estabelecimento de nascimento (CNES) | descartada | identificador ou data que permite reidentificação; também é dado do parto |
| `NUMEROLOTE` | texto | — | 719 códigos | 0,0% | — | Número do lote | descartada | campo interno do sistema, sem significado clínico |
| `CONTADOR` | texto | — | 618.822 códigos | 0,0% | — | Contador sequencial do registro (minúsculo em 2015 e 2017) | descartada | campo interno do sistema, sem significado clínico |
| `DTDECLARAC` | data | — | ddmmaaaa | 0,3% | — | Data de preenchimento da DN | descartada | campo interno do sistema, sem significado clínico |
| `DTCADASTRO` | data | — | ddmmaaaa | 0,0% | — | Data de cadastro no sistema | descartada | campo interno do sistema, sem significado clínico |
| `DTRECEBIM` | data | — | ddmmaaaa | 0,0% | — | Data do último recebimento do lote | descartada | campo interno do sistema, sem significado clínico |
| `DTRECORIGA` | data | — | sem dado | 100,0% | — | Data de recebimento original | descartada | campo interno do sistema, sem significado clínico |
| `DIFDATA` | numerica | — | 0–804 | 0,0% | — | Diferença entre datas do sistema | descartada | campo interno do sistema, sem significado clínico |
| `VERSAOSIST` | texto | — | 2.2.00, 2.2.03, 2.2.08, 3.2.00, 3.2.01, 3.2.02, 3.2.50 | 0,0% | — | Versão do sistema | descartada | campo interno do sistema, sem significado clínico |
| `ORIGEM` | categorica | — | 1, 2 | 0,0% | — | Banco de dados de origem | descartada | campo interno do sistema, sem significado clínico |
| `STDNEPIDEM` | categorica | — | 0, 1 | 0,0% | — | Status de DN epidemiológica | descartada | campo interno do sistema, sem significado clínico |
| `STDNNOVA` | categorica | — | 0, 1 | 0,0% | — | Status de DN nova | descartada | campo interno do sistema, sem significado clínico |
| `TPFUNCRESP` | categorica | — | 1, 2, 3, 4, 5 | 3,9% | — | Função de quem preencheu a DN | descartada | campo interno do sistema, sem significado clínico |
| `TPDOCRESP` | categorica | — | 0, 1, 2, 3, 4, 5 | 0,2% | — | Documento de quem preencheu a DN | descartada | campo interno do sistema, sem significado clínico |
| `ESCMAE` | categorica | — | 1, 2, 3, 4, 5, 9 | 0,5% | — | Escolaridade em anos de estudo (DN antiga) | descartada | codificação da DN antiga, substituída por campo mais detalhado |
| `ESCMAEAGR1` | categorica | — | 13 códigos | 0,6% | — | Escolaridade 2010 agregada | descartada | redundante com ESCMAE2010 |
| `SERIESCMAE` | numerica | — | 1–8 | 29,7% | — | Última série concluída | descartada | redundante com ESCMAE2010 |
| `NATURALMAE` | categorica | — | 27 códigos | 0,4% | — | Naturalidade da mãe (país, se estrangeira) | descartada | baixo valor preditivo esperado e aumenta risco de reidentificação |
| `CODMUNNATU` | categorica | — | 3.056 códigos | 0,4% | — | Município de naturalidade da mãe | descartada | baixo valor preditivo esperado e aumenta risco de reidentificação |
| `CODUFNATU` | categorica | — | 27 códigos | 0,4% | — | UF de naturalidade da mãe | descartada | baixo valor preditivo esperado e aumenta risco de reidentificação |
<!-- auditoria:variaveis:fim -->

**Regra para atributos:** só entra no modelo o que é conhecido **na captação da gestante** (início do
pré-natal), que é o momento da decisão da proposta. Por isso saem:

- tudo o que só existe no parto ou depois dele: idade gestacional, tipo de parto, Apgar, apresentação,
  grupo de Robson, local e município do parto, anomalias;
- o que depende de quanto tempo a gestação durou (`CONSPRENAT`, `CONSULTAS`, `KOTELCHUCK`). Um parto
  prematuro tem menos consultas por ter sido mais curto, o que vazaria o desfecho;
- características do bebê (`SEXO`, `RACACOR`), desconhecidas na captação.

## 4. Variável-alvo

- **Nome:** `baixo_peso`.
- **Definição operacional:** `baixo_peso = 1` se `PESO < 2500` g, e `0` se `PESO ≥ 2500` g. É o critério da
  OMS. `PESO` é o peso medido até a 5ª hora de vida. Registros com peso ausente ou fora de 300–6.500 g são
  excluídos (seção 5).
- **Distribuição:**

<!-- auditoria:alvo:inicio -->
- **Período auditado:** 2015–2024 (10 anos), 1.282.496 registros brutos e 1.281.940 com peso plausível.
- **Distribuição:** 102.937 casos de baixo peso (8,03%) e 1.179.003 sem baixo peso (91,97%). Razão de desbalanceamento ≈ 1:11.
<!-- auditoria:alvo:fim -->

- **Por que não é trivial:**
  - o peso é uma medida feita no nascimento. Não é cópia de nenhuma coluna usada como atributo, nem
    resultado de regra determinística sobre elas;
  - as colunas que praticamente anteciparam o desfecho (semanas de gestação, Apgar, nº de consultas) foram
    retiradas de propósito, então o modelo só tem fatores de risco **anteriores** ao parto;
  - o baseline que sempre responde “não” tem PR-AUC igual à prevalência (cerca de 0,08). Qualquer ganho
    acima disso precisa vir de sinal real.

## 5. Qualidade e riscos

<!-- auditoria:qualidade:inicio -->
| item verificado | registros | % do total | ação (E3) |
| --- | --- | --- | --- |
| duplicatas (todas as colunas, exceto as internas do sistema) | 33 | 0,00% | remover a cópia (iguais até em hora e peso do nascimento: DN digitada em duplicidade) |
| `PESO` ausente ou não numérico | 99 | 0,01% | excluir (alvo indefinido) |
| `PESO` fora de 300–6500 g | 457 | 0,04% | excluir (provável erro de digitação) |
| `IDADEMAE` ausente ou ignorada (99) | 4 | 0,00% | imputar dentro do pipeline |
| `IDADEMAE` fora de 10–55 anos | 29 | 0,00% | tratar como ausente |
| histórico obstétrico (`QTD*`) com valor > 20 | 125 | 0,01% | tratar como ausente |
| `MESPRENAT` com código fora de 01–09/99 | 0 | 0,00% | tratar como ausente |
| `PARIDADE` = nulípara com filhos vivos > 0 | 0 | 0,00% | manter; registrar como inconsistência de preenchimento |
| `CODMUNRES` = 260000 (município ignorado) ou sem par no IBGE | 138 | 0,01% | região = 'ignorada' |
<!-- auditoria:qualidade:fim -->

Os problemas de preenchimento atingem menos de 0,1% dos registros e não ameaçam a análise. As ações
listadas entram na preparação da E3, dentro do pipeline, depois do split.

| Item verificado | Resultado | Ação |
| --------------- | --------- | ---- |
| inconsistência temporal | as colunas internas mudam entre anos (`CONTADOR` minúsculo e `CODPAISRES` só em 2015 e 2017); nenhuma coluna usada como atributo muda de layout | nomes padronizados em maiúsculas na leitura (`src/data/carregar.py`) |
| mudança de distribuição | a prevalência de baixo peso sobe a partir de 2021 (seção 6) | recorte em anos recentes e teste temporal em 2024 (seção 6) |
| subnotificação / viés de coleta | o SINASC registra nascidos vivos, não perdas fetais: gestações que terminam em óbito fetal não entram na base. A cobertura do SINASC em PE não foi medida aqui | discutir como limitação; checar o indicador de cobertura da RIPSA (“Cobertura dos sistemas de informações de nascidos vivos”) no artigo |
| `RACACORMAE` ignorada | 1,3% dos registros, com prevalência de baixo peso mais baixa que a dos demais grupos (seção 8) | categoria “ignorada” mantida separada, sem imputar raça/cor |
| dado pessoal identificável | não há nome, CPF ou endereço; há datas e códigos de estabelecimento | removidos (seção 9) |

## 6. Recorte temporal

<!-- auditoria:resumo-anos:inicio -->
| ano | registros | peso válido | baixo peso | % baixo peso | Petrolina | % baixo peso Petrolina | MESPRENAT aus./ign. | ESCMAE2010 aus./ign. | RACACORMAE aus. | CODOCUPMAE aus. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015 | 145.024 | 144.963 | 11.352 | 7,83% | 6.585 | 8,73% | 4,8% | 1,1% | 1,1% | 4,6% |
| 2016 | 130.733 | 130.679 | 10.165 | 7,78% | 6.239 | 9,30% | 4,8% | 1,1% | 1,4% | 4,3% |
| 2017 | 135.932 | 135.878 | 10.455 | 7,69% | 6.206 | 8,86% | 4,5% | 1,1% | 1,6% | 4,3% |
| 2018 | 138.317 | 138.257 | 10.557 | 7,64% | 6.577 | 8,38% | 3,6% | 1,0% | 1,3% | 3,8% |
| 2019 | 133.359 | 133.304 | 10.380 | 7,79% | 6.418 | 8,73% | 3,8% | 1,2% | 1,2% | 3,6% |
| 2020 | 128.481 | 128.433 | 10.006 | 7,79% | 6.199 | 9,23% | 3,8% | 1,3% | 1,3% | 3,7% |
| 2021 | 126.211 | 126.176 | 10.285 | 8,15% | 6.298 | 8,21% | 3,6% | 1,0% | 1,0% | 3,2% |
| 2022 | 117.437 | 117.375 | 10.150 | 8,65% | 6.119 | 9,20% | 3,8% | 0,9% | 1,2% | 4,7% |
| 2023 | 116.175 | 116.116 | 9.944 | 8,56% | 6.021 | 9,20% | 4,1% | 1,4% | 1,6% | 4,7% |
| 2024 | 110.827 | 110.759 | 9.643 | 8,71% | 6.172 | 9,48% | 3,2% | 0,9% | 0,8% | 4,8% |
<!-- auditoria:resumo-anos:fim -->

**Leitura:**

- A prevalência de baixo peso é estável entre 2015 e 2020 e sobe a partir de 2021. É uma mudança real de
  distribuição, não uma mudança de preenchimento: a completude das colunas usadas como atributo fica
  estável em todos os anos.
- O número de nascimentos cai ao longo do período.
- Petrolina fica acima da média do estado em todos os anos.

**Decisão:**

- **Desenvolvimento:** 2019 a 2023, com treino, validação cruzada e ajuste de hiperparâmetros. São os anos
  mais próximos do uso real e incluem o patamar mais alto de prevalência.
- **Teste:** **2024**, último ano definitivo, como teste temporal externo, **usado uma única vez** no fim do
  projeto. Testar num ano posterior ao treino mede a validade externa melhor que um teste aleatório, porque
  reproduz o uso real: treinar com o passado e prever o ano seguinte.
- **2015 a 2018:** ficam só na auditoria e na EDA, para documentar a tendência.
- **Pandemia (2020 e 2021):** os dois anos ficam no desenvolvimento. A E5 vai comparar o desempenho por ano
  para ver se eles se comportam diferente.

<!-- auditoria:recorte:inicio -->
| conjunto | anos | registros com peso plausível | baixo peso | % baixo peso |
| --- | --- | --- | --- | --- |
| desenvolvimento (treino + CV) | 2019–2023 | 621.404 | 50.765 | 8,17% |
| teste temporal (uso único) | 2024 | 110.759 | 9.643 | 8,71% |
<!-- auditoria:recorte:fim -->

## 7. Licença

- **O que está declarado:** a página do SINASC no Portal de Dados Abertos do SUS não traz licença
  específica, e o campo “licença de uso” do conjunto está vazio. O aviso geral do portal diz que o conteúdo
  do site está publicado “sob a licença Creative Commons Atribuição-SemDerivações 3.0”.
  O FTP do DATASUS não declara licença.
- **O que este projeto faz com os dados:**
  - **não redistribui** a base nem versões modificadas dela: `data/raw/` e `data/processed/` ficam fora do
    Git, e o repositório só tem o script que baixa da fonte oficial;
  - **publica** código, estatísticas agregadas e resultados de modelos, sempre com atribuição ao Ministério
    da Saúde/SINASC.
- **Análise:**
  - a cláusula “SemDerivações” restringe o compartilhamento de versões adaptadas do material, e o projeto
    não compartilha nenhuma;
  - estatísticas e resultados de análise não reproduzem a base;
  - a Política de Dados Abertos do Executivo federal (Decreto 8.777/2016) orienta o uso livre dos dados
    publicados pelo governo;
  - conclusão: o uso acadêmico com publicação de resultados é compatível.
- **Ressalva:** a interpretação foi submetida ao professor na issue #1 do repositório da disciplina. Se a
  resposta for negativa, vale o plano de contingência da proposta (troca para o tema reserva).

## 8. Subgrupos e viés (RQ-ÉT-02)

Tamanho e prevalência dos subgrupos que serão usados na análise de desempenho por grupo (E5). Período
2015–2024, só registros com peso plausível. Cruzamentos com menos de 10 registros não são publicados.

<!-- auditoria:subgrupos:inicio -->
| subgrupo | categoria | registros | % da base | baixo peso | % baixo peso |
| --- | --- | --- | --- | --- | --- |
| raça/cor da mãe | parda | 938.673 | 73,2% | 74.851 | 7,97% |
| raça/cor da mãe | branca | 242.470 | 18,9% | 19.331 | 7,97% |
| raça/cor da mãe | preta | 69.426 | 5,4% | 6.742 | 9,71% |
| raça/cor da mãe | ignorada | 16.286 | 1,3% | 898 | 5,51% |
| raça/cor da mãe | indígena | 11.407 | 0,9% | 810 | 7,10% |
| raça/cor da mãe | amarela | 3.678 | 0,3% | 305 | 8,29% |
| idade da mãe | 20–34 anos | 887.506 | 69,2% | 65.706 | 7,40% |
| idade da mãe | até 19 anos | 221.111 | 17,2% | 20.605 | 9,32% |
| idade da mãe | 35 anos ou mais | 173.319 | 13,5% | 16.626 | 9,59% |
| idade da mãe | ignorada | < 10 | — | — | — |
| mesorregião de residência | Metropolitana de Recife | 502.869 | 39,2% | 42.190 | 8,39% |
| mesorregião de residência | Agreste Pernambucano | 330.117 | 25,8% | 25.524 | 7,73% |
| mesorregião de residência | Mata Pernambucana | 182.258 | 14,2% | 13.377 | 7,34% |
| mesorregião de residência | Sertão Pernambucano | 156.963 | 12,2% | 12.606 | 8,03% |
| mesorregião de residência | São Francisco Pernambucano | 109.595 | 8,5% | 9.226 | 8,42% |
| mesorregião de residência | ignorada | 138 | 0,0% | 14 | 10,14% |
| município de residência | demais municípios | 1.219.106 | 95,1% | 97.330 | 7,98% |
| município de residência | Petrolina | 62.834 | 4,9% | 5.607 | 8,92% |
<!-- auditoria:subgrupos:fim -->

**O que isso muda na modelagem:**

- a prevalência difere entre os grupos de raça/cor e de idade da mãe. Um único limiar de decisão pode dar
  recall diferente para cada grupo, e isso será medido na E5;
- “indígena” e “amarela” são menos de 1% da base cada. As métricas desses grupos terão intervalos de
  confiança largos, e isso será reportado assim, sem esconder;
- a raça/cor da mãe é usada como atributo porque é fator de risco documentado. O modelo serve apenas para
  **priorizar** acompanhamento extra, nunca para negar atendimento (uso inadequado declarado na proposta).

## 9. LGPD

- **Existe dado pessoal?** Não há identificador direto (nome, CPF, CNS, endereço). Há quase-identificadores:
  datas de nascimento da mãe e do bebê, hora do nascimento, estabelecimento e município. Combinados, podem
  permitir reidentificação em municípios pequenos.
- **Estratégia adotada:**
  - **remoção** de `DTNASC` (só o ano é mantido, derivado do nome do arquivo), `DTNASCMAE`, `DTULTMENST`,
    `HORANASC`, `CODESTAB`, `NUMEROLOTE`, `CONTADOR` e das naturalidades;
  - o município entra no modelo só como **mesorregião ou região imediata** (agregação), com exceção do
    indicador de Petrolina, que é um município de cerca de 6 mil nascimentos por ano;
  - nenhum cruzamento publicado tem menos de 10 registros;
  - nenhum dado em nível de registro vai para o Git.
- **Risco de reidentificação:** baixo depois da remoção. O dado de origem já é público e anonimizado pelo
  Ministério da Saúde, e o projeto não cruza a base com nenhuma outra fonte individual.
- **Comando de verificação:** `shasum -a 256 data/raw/*.dbc` (ou `sha256sum`) e comparar com
  `configs/hashes-dados-brutos.csv`, que o próprio `python -m src.data.download` já confere.

## 10. Como reproduzir esta auditoria

```bash
python -m src.data.download  --config configs/base.yaml   # baixa 2015–2024 + IBGE e confere SHA-256 (~3 min)
python -m src.data.auditoria --config configs/base.yaml   # recalcula as tabelas deste arquivo (~4 min na 1ª vez)
```
