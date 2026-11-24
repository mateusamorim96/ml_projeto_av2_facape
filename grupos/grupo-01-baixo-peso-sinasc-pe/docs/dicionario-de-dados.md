# Dicionário de Dados — G01 · SINASC Pernambuco

> Entrega E2. Auditoria do dataset: de onde ele veio, o que significa cada coluna e o que não pode ser usado.
>
> Os blocos entre os marcadores `auditoria:*` são **gerados por script** e reescritos a cada execução de
> `python -m src.data.auditoria --config configs/base.yaml`. Nenhum número desses blocos foi digitado à mão.
> As tabelas também ficam em `reports/tables/tabela-auditoria-*.csv`.

## 1. Identificação

| Campo | Valor |
| ----- | ----- |
| Fonte | Ministério da Saúde — Sistema de Informações sobre Nascidos Vivos (SINASC), gerido pela CGIAE/DASNT/SVS e distribuído pelo DATASUS |
| URL | `ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Dados/DNRES/DNPE{ano}.dbc` (um arquivo por ano, residentes em Pernambuco). Página do conjunto: <https://dadosabertos.saude.gov.br/dataset/sistema-de-informacao-sobre-nascidos-vivos-sinasc> |
| Documentação | “Estrutura do SINASC”, CGIAE/DASNT/SVS/MS, atualizada em 12/2019: `ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Doc/Estrutura_SINASC_para_CD.pdf` |
| Tabela auxiliar | Municípios de Pernambuco com micro e mesorregião — API de Localidades do IBGE: <https://servicodados.ibge.gov.br/api/v1/localidades/estados/26/municipios> |
| Data de acesso | 2026-11-23 (registrada por arquivo em `configs/hashes-dados-brutos.csv`) |
| Recorte | UF de residência = PE; anos definitivos de 2015 a 2024. Os de 2025 e 2026 ainda estão na pasta `PRELIM` do DATASUS e não foram usados |
| Licença | Creative Commons Atribuição-SemDerivações 3.0 (CC BY-ND 3.0) — <https://creativecommons.org/licenses/by-nd/3.0/deed.pt-br>. Declarada para o portal inteiro; o conjunto não declara licença própria (ver seção 7) |
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
| (d) desbalanceamento, ausentes, ruído ou heterogeneidade | **atende** | entre 7% e 8% de positivos (seção 4); pesos implausíveis; prevalência muda entre anos e regiões (seções 4, 5 e 6) |
| (e) licença compatível com uso acadêmico | **atende, com ressalva** | seção 7 |

## 3. Variáveis

Tipos, códigos e descrições seguem o dicionário oficial. A coluna **uso** vem de `src/data/esquema.py`, que
é a mesma fonte usada pela preparação dos dados na E3. Percentuais calculados sobre 2015–2024.

<!-- auditoria:variaveis:inicio -->
| coluna | tipo | unidade | origem | faixa observada | % nulos | % ignorado | descrição | uso | motivo / observação |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `PESO` | numerica | g | DN, bloco I (recém-nascido) | 100–7.000 | 0,0% | — | Peso ao nascer, verificado até a 5ª hora de vida (códigos: 4 dígitos) | alvo | alvo = 1 se PESO < 2500 g |
| `IDADEMAE` | numerica | anos | DN, bloco III (mãe) | 10–65 | 0,0% | 0,0% | Idade da mãe | atributo |  |
| `ESCMAE2010` | categorica | — | DN, bloco III (mãe) | 0, 1, 2, 3, 4, 5 | 0,6% | 0,5% | Escolaridade da mãe (última série concluída), nível (códigos: 0 sem escolaridade; 1 fundamental I; 2 fundamental II; 3 médio; 4 superior incompleto; 5 superior completo; 9 ignorado) | atributo |  |
| `RACACORMAE` | categorica | — | DN, bloco III (mãe) | 1, 2, 3, 4, 5 | 1,3% | — | Raça/cor da mãe (códigos: 1 branca; 2 preta; 3 amarela; 4 parda; 5 indígena) | atributo | também usada na análise por subgrupo (RQ-ÉT-02) |
| `ESTCIVMAE` | categorica | — | DN, bloco III (mãe) | 1, 2, 3, 4, 5 | 0,6% | 0,3% | Situação conjugal da mãe (códigos: 1 solteira; 2 casada; 3 viúva; 4 separada; 5 união estável; 9 ignorada) | atributo |  |
| `CODOCUPMAE` | categorica | — | DN, bloco III (mãe) | 1.571 códigos | 4,2% | — | Ocupação da mãe (CBO 2002) (códigos: 6 dígitos CBO) | atributo | alta cardinalidade: agrupar pelo grande grupo da CBO na E3 |
| `QTDGESTANT` | numerica | gestações | DN, bloco V (gestação e parto) | 0–50 | 0,6% | 0,0% | Número de gestações anteriores | atributo |  |
| `QTDPARTNOR` | numerica | partos | DN, bloco V (gestação e parto) | 0–91 | 0,7% | 0,0% | Número de partos vaginais anteriores | atributo |  |
| `QTDPARTCES` | numerica | partos | DN, bloco V (gestação e parto) | 0–60 | 0,8% | 0,0% | Número de cesáreas anteriores | atributo |  |
| `QTDFILVIVO` | numerica | filhos | DN, bloco V (gestação e parto) | 0–30 | 0,6% | 0,0% | Número de filhos vivos | atributo |  |
| `QTDFILMORT` | numerica | perdas | DN, bloco V (gestação e parto) | 0–26 | 0,8% | 0,0% | Número de perdas fetais e abortos | atributo |  |
| `PARIDADE` | categorica | — | calculada pelo sistema | 0, 1 | 0,0% | 0,0% | Paridade, calculada pelo sistema a partir do histórico (códigos: 0 nulípara; 1 multípara; 9 ignorado) | atributo |  |
| `MESPRENAT` | numerica | mês | DN, bloco V (gestação e parto) | 1–9 | 1,5% | 2,5% | Mês de gestação em que iniciou o pré-natal (códigos: 01 … 09; 99 ignorado) | atributo | registros sem o mês ficam fora da população (seção 6) |
| `CODMUNRES` | categorica | — | DN, bloco III (mãe) | 186 códigos | 0,0% | — | Município de residência da mãe (IBGE, 6 dígitos) (códigos: código IBGE sem dígito verificador) | atributo | convertido em mesorregião/região imediata (IBGE) na E3; Petrolina = 261110 |
| `GRAVIDEZ` | categorica | — | DN, bloco V (gestação e parto) | 1, 2, 3 | 0,1% | 0,0% | Tipo de gravidez (códigos: 1 única; 2 dupla; 3 tripla ou mais; 9 ignorado) | filtro | população = só gestação única (seção 6); constante dentro dela |
| `DTNASC` | data | — | DN, bloco I (recém-nascido) | ddmmaaaa | 0,0% | — | Data do nascimento | descartada | identificador ou data que permite reidentificação; o ano vem do nome do arquivo |
| `IDADEPAI` | numerica | anos | DN, bloco IV (pai) | 1–98 | 80,0% | 0,0% | Idade do pai | descartada | mais de 60% de nulos (ver auditoria) |
| `CODPAISRES` | categorica | — | demais campos do arquivo | 1 | 21,9% | — | País de residência | descartada | existe só em 2015 e 2017; o arquivo já é de residentes em PE |
| `SEMAGESTAC` | numerica | semanas | DN, bloco V (gestação e parto) | 19–45 | 1,9% | — | Semanas de gestação | descartada | vazamento: só é conhecida no parto ou depois dele |
| `GESTACAO` | categorica | — | DN, bloco V (gestação e parto) | 1, 2, 3, 4, 5, 6, 9 | 1,9% | — | Semanas de gestação, agrupado (DN antiga) | descartada | vazamento: só é conhecida no parto ou depois dele |
| `TPMETESTIM` | categorica | — | DN, bloco V (gestação e parto) | 1, 2, 8, 9 | 1,9% | — | Método para estimar a idade gestacional | descartada | vazamento: só é conhecida no parto ou depois dele |
| `PARTO` | categorica | — | DN, bloco V (gestação e parto) | 1, 2, 9 | 0,1% | — | Tipo de parto | descartada | vazamento: só é conhecida no parto ou depois dele |
| `STTRABPART` | categorica | — | DN, bloco V (gestação e parto) | 1, 2, 9 | 0,7% | — | Trabalho de parto induzido | descartada | vazamento: só é conhecida no parto ou depois dele |
| `STCESPARTO` | categorica | — | DN, bloco V (gestação e parto) | 1, 2, 3, 9 | 6,5% | — | Cesárea antes do trabalho de parto | descartada | vazamento: só é conhecida no parto ou depois dele |
| `TPAPRESENT` | categorica | — | DN, bloco V (gestação e parto) | 1, 2, 3, 9 | 0,4% | — | Apresentação do recém-nascido | descartada | vazamento: só é conhecida no parto ou depois dele |
| `TPROBSON` | categorica | — | calculada pelo sistema | 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11 | 0,0% | — | Grupo de Robson (gerado a partir de dados do parto) | descartada | vazamento: só é conhecida no parto ou depois dele |
| `TPNASCASSI` | categorica | — | DN, bloco V (gestação e parto) | 1, 2, 3, 4, 9 | 0,3% | — | Profissional que assistiu o parto | descartada | vazamento: só é conhecida no parto ou depois dele |
| `LOCNASC` | categorica | — | DN, bloco II (local do parto) | 1, 2, 3, 4, 9 | 0,0% | — | Local de ocorrência do nascimento | descartada | vazamento: só é conhecida no parto ou depois dele |
| `CODMUNNASC` | categorica | — | DN, bloco II (local do parto) | 461 códigos | 0,0% | — | Município de ocorrência do nascimento | descartada | vazamento: só é conhecida no parto ou depois dele |
| `APGAR1` | numerica | — | DN, bloco I (recém-nascido) | 0–99 | 0,9% | — | Índice de Apgar no 1º minuto | descartada | vazamento: só é conhecida no parto ou depois dele |
| `APGAR5` | numerica | — | DN, bloco I (recém-nascido) | 0–99 | 0,8% | — | Índice de Apgar no 5º minuto | descartada | vazamento: só é conhecida no parto ou depois dele |
| `IDANOMAL` | categorica | — | DN, bloco I (recém-nascido) | 1, 2, 9 | 0,2% | — | Anomalia congênita detectada no nascimento | descartada | vazamento: só é conhecida no parto ou depois dele |
| `CODANOMAL` | texto | — | DN, bloco VI (anomalia) | 2.138 códigos | 98,9% | — | Anomalias congênitas (CID-10) | descartada | vazamento: só é conhecida no parto ou depois dele |
| `HORANASC` | texto | — | DN, bloco I (recém-nascido) | 1.440 códigos | 0,1% | — | Hora do nascimento | descartada | vazamento: só é conhecida no parto ou depois dele |
| `SEXO` | categorica | — | DN, bloco I (recém-nascido) | 0, 1, 2 | 0,0% | — | Sexo do recém-nascido (códigos: os arquivos usam 0, 1 e 2; o dicionário oficial cita M, F e I) | descartada | característica do recém-nascido, desconhecida na captação |
| `RACACOR` | categorica | — | DN, bloco I (recém-nascido) | 1, 2, 3, 4, 5 | 1,2% | — | Raça/cor do recém-nascido | descartada | característica do recém-nascido, desconhecida na captação; usa-se RACACORMAE |
| `CONSPRENAT` | numerica | — | DN, bloco V (gestação e parto) | 0–99 | 1,1% | — | Número de consultas de pré-natal | descartada | vazamento: depende da duração da gestação |
| `CONSULTAS` | categorica | — | DN, bloco V (gestação e parto) | 1, 2, 3, 4, 9 | 0,1% | — | Consultas de pré-natal, agrupado (DN antiga) | descartada | vazamento: depende da duração da gestação |
| `KOTELCHUCK` | categorica | — | calculada pelo sistema | 1, 2, 3, 4, 5, 9 | 0,0% | — | Índice de adequação do pré-natal (usa nº de consultas) | descartada | vazamento: depende da duração da gestação |
| `DTNASCMAE` | data | — | DN, bloco III (mãe) | ddmmaaaa | 0,3% | — | Data de nascimento da mãe | descartada | identificador ou data que permite reidentificação |
| `DTULTMENST` | data | — | DN, bloco V (gestação e parto) | ddmmaaaa | 41,8% | — | Data da última menstruação | descartada | identificador ou data que permite reidentificação |
| `CODESTAB` | categorica | — | DN, bloco II (local do parto) | 844 códigos | 0,5% | — | Estabelecimento de nascimento (CNES) | descartada | identificador ou data que permite reidentificação; também é dado do parto |
| `NUMEROLOTE` | texto | — | interna do sistema | 719 códigos | 0,0% | — | Número do lote | descartada | campo interno do sistema, sem significado clínico |
| `CONTADOR` | texto | — | arquivo DATASUS, ausente do dicionário oficial | 618.822 códigos | 0,0% | — | Contador sequencial do registro (minúsculo em 2015 e 2017) | descartada | campo interno do sistema, sem significado clínico |
| `DTDECLARAC` | data | — | DN, bloco VII (preenchimento) | ddmmaaaa | 0,3% | — | Data de preenchimento da DN | descartada | dado do preenchimento da DN, registrado depois do parto |
| `DTCADASTRO` | data | — | interna do sistema | ddmmaaaa | 0,0% | — | Data de cadastro no sistema | descartada | campo interno do sistema, sem significado clínico |
| `DTRECEBIM` | data | — | interna do sistema | ddmmaaaa | 0,0% | — | Data do último recebimento do lote | descartada | campo interno do sistema, sem significado clínico |
| `DTRECORIGA` | data | — | interna do sistema | sem dado | 100,0% | — | Data de recebimento original | descartada | campo interno do sistema, sem significado clínico |
| `DIFDATA` | numerica | — | interna do sistema | 0–804 | 0,0% | — | Diferença entre datas do sistema | descartada | campo interno do sistema, sem significado clínico |
| `VERSAOSIST` | texto | — | interna do sistema | 2.2.00, 2.2.03, 2.2.08, 3.2.00, 3.2.01, 3.2.02, 3.2.50 | 0,0% | — | Versão do sistema | descartada | campo interno do sistema, sem significado clínico |
| `ORIGEM` | categorica | — | interna do sistema | 1, 2 | 0,0% | — | Banco de dados de origem | descartada | campo interno do sistema, sem significado clínico |
| `STDNEPIDEM` | categorica | — | interna do sistema | 0, 1 | 0,0% | — | Status de DN epidemiológica | descartada | campo interno do sistema, sem significado clínico |
| `STDNNOVA` | categorica | — | interna do sistema | 0, 1 | 0,0% | — | Status de DN nova | descartada | campo interno do sistema, sem significado clínico |
| `TPFUNCRESP` | categorica | — | DN, bloco VII (preenchimento) | 1, 2, 3, 4, 5 | 3,9% | — | Função de quem preencheu a DN | descartada | dado do preenchimento da DN, registrado depois do parto |
| `TPDOCRESP` | categorica | — | DN, bloco VII (preenchimento) | 0, 1, 2, 3, 4, 5 | 0,2% | — | Documento de quem preencheu a DN | descartada | dado do preenchimento da DN, registrado depois do parto |
| `ESCMAE` | categorica | — | DN, bloco III (mãe) | 1, 2, 3, 4, 5, 9 | 0,5% | — | Escolaridade em anos de estudo (DN antiga) | descartada | codificação da DN antiga, substituída por campo mais detalhado |
| `ESCMAEAGR1` | categorica | — | calculada pelo sistema | 13 códigos | 0,6% | — | Escolaridade 2010 agregada | descartada | redundante com ESCMAE2010 |
| `SERIESCMAE` | numerica | — | DN, bloco III (mãe) | 1–8 | 29,7% | — | Última série concluída | descartada | redundante com ESCMAE2010 |
| `NATURALMAE` | categorica | — | DN, bloco III (mãe) | 27 códigos | 0,4% | — | Naturalidade da mãe (país, se estrangeira) | descartada | baixo valor preditivo esperado e aumenta risco de reidentificação |
| `CODMUNNATU` | categorica | — | demais campos do arquivo | 3.056 códigos | 0,4% | — | Município de naturalidade da mãe | descartada | baixo valor preditivo esperado e aumenta risco de reidentificação |
| `CODUFNATU` | categorica | — | demais campos do arquivo | 27 códigos | 0,4% | — | UF de naturalidade da mãe | descartada | baixo valor preditivo esperado e aumenta risco de reidentificação |
<!-- auditoria:variaveis:fim -->

**Regra para atributos:** só entra no modelo o que é conhecido **na captação da gestante** (início do
pré-natal), que é o momento da decisão da proposta. Por isso saem:

- tudo o que só existe no parto ou depois dele: idade gestacional, tipo de parto, Apgar, apresentação,
  grupo de Robson, local e município do parto, anomalias;
- o que depende de quanto tempo a gestação durou (`CONSPRENAT`, `CONSULTAS`, `KOTELCHUCK`). Um parto
  prematuro tem menos consultas por ter sido mais curto, o que vazaria o desfecho;
- características do bebê (`SEXO`, `RACACOR`), desconhecidas na captação.

`GRAVIDEZ` e `MESPRENAT` também **definem a população** do modelo (seção 6): só entram gestações únicas
com mês de início do pré-natal registrado. Por isso `GRAVIDEZ` é filtro, não atributo, já que fica constante
dentro da população.

## 4. Variável-alvo

- **Nome:** `baixo_peso`.
- **Definição operacional:** `baixo_peso = 1` se `PESO < 2500` g, e `0` se `PESO ≥ 2500` g. É o critério da
  OMS. `PESO` é o peso medido até a 5ª hora de vida. Registros com peso ausente ou fora de 300–6.500 g são
  excluídos (seção 5).
- **Distribuição:**

<!-- auditoria:alvo:inicio -->
- **Período auditado:** 2015–2024 (10 anos), 1.282.496 registros brutos e 1.281.940 com peso plausível, dos quais 102.937 com baixo peso (8,03%).
- **População do modelo, desenvolvimento (2019–2023):** 585.522 registros, 40.761 com baixo peso (6,96%) e 544.761 sem (93,04%). Razão de desbalanceamento ≈ 1:13. PR-AUC do baseline (prevalência) ≈ 0,070.
<!-- auditoria:alvo:fim -->

- **Por que não é trivial:**
  - o peso é uma medida feita no nascimento. Não é cópia de nenhuma coluna usada como atributo, nem
    resultado de regra determinística sobre elas;
  - as colunas que praticamente anteciparam o desfecho (semanas de gestação, Apgar, nº de consultas) foram
    retiradas de propósito, então o modelo só tem fatores de risco **anteriores** ao parto;
  - o baseline que sempre responde “não” tem PR-AUC igual à prevalência da população (valor no bloco
    acima). Qualquer ganho acima disso precisa vir de sinal real;
  - as gestações múltiplas, em que o baixo peso seria quase óbvio, ficaram fora da população (seção 6),
    para que o modelo não ganhe desempenho com um caso que a equipe já reconhece sem ele.

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
| nulos | nos atributos, o maior índice de ausência é o de `CODOCUPMAE` (4,2%); os demais ficam em até 1,3% (seção 3). `MESPRENAT` (1,5% nulo + 2,5% ignorado) não é imputado: o registro sem o mês sai da população (seção 6) | imputação dentro do `Pipeline`, ajustada só no treino de cada fold (E3) |
| inconsistência temporal | as colunas internas mudam entre anos (`CONTADOR` minúsculo e `CODPAISRES` só em 2015 e 2017); nenhuma coluna usada como atributo muda de layout | nomes padronizados em maiúsculas na leitura (`src/data/carregar.py`) |
| mudança de distribuição | a prevalência de baixo peso sobe a partir de 2021 (seção 6) | recorte em anos recentes e teste temporal em 2024 (seção 6) |
| subnotificação / viés de coleta | o SINASC registra nascidos vivos, não perdas fetais: gestações que terminam em óbito fetal não entram na base. A cobertura do SINASC em PE não foi medida aqui | discutir como limitação; checar o indicador de cobertura da RIPSA (“Cobertura dos sistemas de informações de nascidos vivos”) no artigo |
| `RACACORMAE` ignorada | 1,3% dos registros de 2015–2024, com prevalência de baixo peso mais baixa que a dos demais grupos (seção 8) | categoria “ignorada” mantida separada, sem imputar raça/cor |
| dado pessoal identificável | não há nome, CPF ou endereço; há datas e códigos de estabelecimento | removidos (seção 9) |

## 6. Recorte temporal e população do modelo

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

### População do modelo

A decisão acontece na **captação da gestante**, então o modelo só é treinado e avaliado com quem passaria
por ela. Os critérios ficam em `src/data/populacao.py` e `configs/base.yaml` (`dados.populacao`) e são
aplicados nesta ordem:

<!-- auditoria:populacao:inicio -->
| conjunto | anos | etapa | registros | % do período | baixo peso | % baixo peso |
| --- | --- | --- | --- | --- | --- | --- |
| desenvolvimento (treino + CV) | 2019–2023 | registros no período | 621.663 | 100,0% | — | — |
| desenvolvimento (treino + CV) | 2019–2023 | + peso plausível (300–6.500 g) | 621.404 | 100,0% | 50.765 | 8,17% |
| desenvolvimento (treino + CV) | 2019–2023 | + gestação única | 608.642 | 97,9% | 43.471 | 7,14% |
| desenvolvimento (treino + CV) | 2019–2023 | + mês de início do pré-natal registrado (01–09) | 585.522 | 94,2% | 40.761 | 6,96% |
| teste temporal (uso único) | 2024 | registros no período | 110.827 | 100,0% | — | — |
| teste temporal (uso único) | 2024 | + peso plausível (300–6.500 g) | 110.759 | 99,9% | 9.643 | 8,71% |
| teste temporal (uso único) | 2024 | + gestação única | 108.343 | 97,8% | 8.231 | 7,60% |
| teste temporal (uso único) | 2024 | + mês de início do pré-natal registrado (01–09) | 104.919 | 94,7% | 7.732 | 7,37% |
<!-- auditoria:populacao:fim -->

Prevalência nos grupos retirados (desenvolvimento, só peso plausível):

<!-- auditoria:excluidos:inicio -->
| grupo | registros | % do desenvolvimento | baixo peso | % baixo peso |
| --- | --- | --- | --- | --- |
| gestação múltipla (GRAVIDEZ 2 ou 3) | 12.209 | 2,0% | 7.250 | 59,38% |
| tipo de gravidez ausente ou ignorado | 553 | 0,1% | 44 | 7,96% |
| gestação única sem mês de início do pré-natal | 23.120 | 3,7% | 2.710 | 11,72% |
| população do modelo | 585.522 | 94,2% | 40.761 | 6,96% |
<!-- auditoria:excluidos:fim -->

**Por que cada grupo sai:**

- **Gestação múltipla.** A prevalência de baixo peso nesse grupo é muito maior que na gestação única
  (tabela acima). Mantê-lo faria o modelo ganhar desempenho só por “descobrir” que gêmeo nasce com baixo
  peso, algo que a equipe já sabe sem modelo: o *Manual de gestação de alto risco* do Ministério da Saúde
  (2022, cap. 17) considera a gestação gemelar de alto risco “independentemente da presença ou da ausência
  de complicações” e aponta o baixo peso entre as complicações fetais mais frequentes. Cada bebê também gera
  um registro, e a mesma gestação aparece
  mais de uma vez: os pares cairiam em folds diferentes e inflariam a validação (RQ-PRE-03), sem
  identificador da mãe para usar `GroupKFold`. Com o corte, a ressalva sobre detectar a gestação múltipla
  no ultrassom deixa de existir.
- **Sem mês de início do pré-natal.** Quem passa pela captação tem esse mês conhecido. A ausência só
  existe no registro retrospectivo, e, como o grupo tem prevalência maior, o modelo aprenderia a usar um
  “ausente” que nunca aparece no momento da decisão. Ficam fora também as gestantes que não fizeram
  pré-natal, que a decisão não alcança; isso é registrado como limitação.
- **Tipo de gravidez ausente ou ignorado.** Não é possível saber se a gestação é única.

**Conjuntos finais** (população do modelo):

<!-- auditoria:recorte:inicio -->
| conjunto | anos | registros na população | baixo peso | % baixo peso |
| --- | --- | --- | --- | --- |
| desenvolvimento (treino + CV) | 2019–2023 | 585.522 | 40.761 | 6,96% |
| teste temporal (uso único) | 2024 | 104.919 | 7.732 | 7,37% |
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
  - o SINASC é publicado pelo Ministério da Saúde, e a Política de Dados Abertos do Executivo federal diz
    que “os dados disponibilizados pelo Poder Executivo federal […] são de livre utilização pelos Poderes
    Públicos e pela sociedade” (Decreto 8.777/2016, art. 4º, com redação do Decreto 9.903/2019);
  - conclusão: o uso acadêmico com publicação de resultados é compatível.
- **Ressalva:** a interpretação foi submetida ao professor na issue #1 do repositório da disciplina. Se a
  resposta for negativa, vale o plano de contingência da proposta (troca para o tema reserva).

## 8. Subgrupos e viés (RQ-ÉT-02)

Tamanho e prevalência dos subgrupos que serão usados na análise de desempenho por grupo (E5), na
**população do modelo** (seção 6), anos de desenvolvimento. Cruzamentos com menos de 10 registros não são
publicados.

<!-- auditoria:subgrupos:inicio -->
| subgrupo | categoria | registros | % da base | baixo peso | % baixo peso |
| --- | --- | --- | --- | --- | --- |
| raça/cor da mãe | parda | 426.214 | 72,8% | 29.535 | 6,93% |
| raça/cor da mãe | branca | 110.534 | 18,9% | 7.471 | 6,76% |
| raça/cor da mãe | preta | 34.986 | 6,0% | 2.921 | 8,35% |
| raça/cor da mãe | ignorada | 6.313 | 1,1% | 318 | 5,04% |
| raça/cor da mãe | indígena | 5.775 | 1,0% | 394 | 6,82% |
| raça/cor da mãe | amarela | 1.700 | 0,3% | 122 | 7,18% |
| idade da mãe | 20–34 anos | 407.501 | 69,6% | 26.024 | 6,39% |
| idade da mãe | até 19 anos | 92.673 | 15,8% | 7.960 | 8,59% |
| idade da mãe | 35 anos ou mais | 85.348 | 14,6% | 6.777 | 7,94% |
| mesorregião de residência | Metropolitana de Recife | 220.622 | 37,7% | 15.702 | 7,12% |
| mesorregião de residência | Agreste Pernambucano | 156.469 | 26,7% | 10.599 | 6,77% |
| mesorregião de residência | Mata Pernambucana | 81.850 | 14,0% | 5.249 | 6,41% |
| mesorregião de residência | Sertão Pernambucano | 74.731 | 12,8% | 5.410 | 7,24% |
| mesorregião de residência | São Francisco Pernambucano | 51.798 | 8,8% | 3.795 | 7,33% |
| mesorregião de residência | ignorada | 52 | 0,0% | < 10 | — |
| município de residência | demais municípios | 555.675 | 94,9% | 38.482 | 6,93% |
| município de residência | Petrolina | 29.847 | 5,1% | 2.279 | 7,64% |
<!-- auditoria:subgrupos:fim -->

**O que isso muda na modelagem:**

- a prevalência difere entre os grupos de raça/cor e de idade da mãe. Um único limiar de decisão pode dar
  recall diferente para cada grupo, e isso será medido na E5;
- “indígena” e “amarela” têm cerca de 1% da base ou menos cada. As métricas desses grupos terão
  intervalos de confiança largos, e isso será reportado assim, sem esconder;
- a raça/cor da mãe é usada como atributo porque a prevalência de baixo peso difere entre os grupos
  (tabela acima: mães pretas acima de brancas e pardas). O modelo serve apenas para **priorizar**
  acompanhamento extra, nunca para negar atendimento (uso inadequado declarado na proposta).

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
python -m src.data.auditoria --config configs/base.yaml   # recalcula as tabelas deste arquivo (4–5 min na 1ª vez)
```

Reprodução conferida em clone limpo: ambiente novo a partir do `requirements.txt`, download com os 11
hashes conferidos e auditoria regenerando este arquivo e as tabelas idênticos aos versionados.

## 11. Referências

- BRASIL. Ministério da Saúde. Secretaria de Vigilância em Saúde. *Estrutura do SINASC*. Brasília:
  CGIAE/DASNT/SVS, atualizado em dez. 2019. Disponível em:
  `ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Doc/Estrutura_SINASC_para_CD.pdf`.
- BRASIL. Ministério da Saúde. Secretaria de Atenção Primária à Saúde. *Manual de gestação de alto risco*
  [recurso eletrônico]. Brasília: Ministério da Saúde, 2022. ISBN 978-65-5993-312-9. Cap. 17, “Gestação
  múltipla”. Disponível em: <https://bvsms.saude.gov.br/bvs/publicacoes/manual_gestacao_alto_risco.pdf>.
- BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD), art. 12.
- BRASIL. Decreto nº 8.777, de 11 de maio de 2016. Institui a Política de Dados Abertos do Poder Executivo
  federal. Art. 4º com redação dada pelo Decreto nº 9.903, de 8 de julho de 2019. Texto consolidado:
  <https://www2.camara.leg.br/legin/fed/decret/2016/decreto-8777-11-maio-2016-783082-normaatualizada-pe.html>.
- CREATIVE COMMONS. *Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0)*. Disponível em:
  <https://creativecommons.org/licenses/by-nd/3.0/deed.pt-br>.
- IBGE. *API de Localidades*: municípios de Pernambuco. Disponível em:
  <https://servicodados.ibge.gov.br/api/v1/localidades/estados/26/municipios>.
