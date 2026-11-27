# Dicionário de Dados — G02

> E2 — auditoria dos indicadores municipais do SINISA (água), referência
> 2023 → 2024, recorte **Região Nordeste**. Todos os números desta página são
> gerados por `src/data/auditoria_sinisa.py` e gravados em `reports/tables/`.
> A licença específica das planilhas e a comparabilidade metodológica plena
> não foram confirmadas; ver decisões e limitações abaixo.

## 1. Identificação

| Campo | Valor |
| ----- | ----- |
| Fonte | SINISA — Ministério das Cidades, módulo Abastecimento de Água |
| Página oficial | [Resultados SINISA 2024 — referência 2023](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/resultados-sinisa); [Resultados SINISA 2025 — referência 2024](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/resultados-sinisa/resultados-sinisa-2025) |
| Downloads oficiais | [Planilhas de referência 2023](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/arquivos/SINISA_Resultados_Ref2023.zip); [planilhas de referência 2024](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/resultados-sinisa/SINISA_Resultados_Ref2024.zip) |
| Pasta usada dos ZIPs | `Água - Base Municipal` (uma linha por município). As pastas `Locais + Regionais` (uma linha por prestador) e `UF / Macrorregião / Brasil` (totais agregados) não são usadas |
| Documentação | [Glossário de Indicadores   de Água](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/resultados-sinisa/GlossriodeIndicadores_GUA_2024.pdf) e abas “Nota metodológica” dos arquivos |
| Consulta das páginas | 2026-11-25; reconferência das fontes oficiais em 2026-11-26 |
| Data original de download | 23/11/2026 |
| Recorte | **Anos:** 2023 (entrada) → 2024 (alvo); dados de referência 2025 ainda não publicados em 2026-11-26. **Região:** Nordeste (9 UFs). **Filtro:** excluídos os municípios fora da macrorregião Nordeste e os que não têm IAG2013 numérico entre 0 e 100% nos dois anos. **Subgrupos de análise:** RIDE do Polo Petrolina/PE e Juazeiro/BA e PE+BA |
| Licença/termos | O rodapé do portal declara [CC BY-ND 3.0](https://creativecommons.org/licenses/by-nd/3.0/) para o conteúdo do site. |
| Verificação dos termos | Páginas oficiais consultadas em 2026-11-25 e reconferidas em 2026-11-26; nenhum arquivo de licença separado foi localizado nos ZIPs. A análise registra a incerteza, não constitui parecer jurídico |
| LGPD | Nos campos municipais examinados, não foi identificado dado de pessoa natural. Manter a análise agregada por município e excluir campos de identificação do prestador dos preditores; reavaliar se outras fontes forem combinadas |
| Arquivos locais | `data/raw/` (ignorado pelo Git; não versionar os XLSX) |

| Referência | Arquivo usado | Abas | Municípios no arquivo (Brasil / Nordeste) | Indicadores | SHA-256 |
| ---------- | ------------- | ---- | ----------------------------------------: | ----------: | ------- |
| 2023 (entrada) | `SINISA_AGUA_Indicadores_Base Municipal_2023.xlsx` | Atendimento; Estruturais e Operacionais; Qualidade; Administrativo e Financeiro | 5.241 / 1.668 | 55 distintos | `39AD4D8B7433629F08A1FBCF7ADB1CD34D2966D5365EEE654F59145FDCD6FE64` |
| 2024 (alvo) | `SINISA_AGUA_Indicadores_Base Municipal_2024_Retificação.xlsx` | Indicadores de Gestão | 5.144 / — | 57 (inclui IAG3004 e IAG3005, ausentes em 2023) | `262F74F515B6225B7C9C122576159AB45576AE15628AE67612D7CEE6C333623D` |

Os hashes foram recalculados em 2026-11-26 sobre os arquivos extraídos dos
ZIPs oficiais e conferem com os registrados na auditoria anterior; o script
regrava-os em `reports/tables/hashes-dados-brutos.csv` a cada execução. Da
planilha de 2024 só se lê o alvo; nenhum indicador de 2024 entra como
preditor.

As planilhas de **informações** (`Gestão Técnica`, `Administrativo e
Financeiro`) da mesma pasta não são usadas nesta etapa: os 55 indicadores já
resumem essas informações. Se forem adotadas na E3, só as de 2023 podem entrar
como preditores, porque os campos de 2024 (GTA1001, GTA1009, GTA1203, GTA1207,
GTA1211) compõem o próprio alvo.

## 2. Escolha do recorte

A RIDE do Polo Petrolina/PE e
Juazeiro/BA tem só **8 municípios** com alvo válido, insuficiente para treinar
e validar um modelo com cerca de 50 preditores. A tabela abaixo
(`reports/tables/cobertura-recortes.csv`) compara os recortes avaliados:

| Recorte | Pares válidos | Média IAG2013 2024 (%) | Desvio (p.p.) | Preditores candidatos | Linhas por preditor |
| ------- | ------------: | ---------------------: | ------------: | --------------------: | ------------------: |
| Brasil | 4.575 | 33,2 | 18,3 | 50 | 91,5 |
| **Nordeste (escolhido)** | **1.458** | **39,9** | **20,4** | **52** | **28,0** |
| PE + BA | 572 | 28,9 | 13,6 | 52 | 11,0 |
| PE | 176 | 33,7 | 17,1 | 53 | 3,3 |
| BA | 396 | 26,7 | 11,0 | 52 | 7,6 |
| RIDE Petrolina–Juazeiro | 8 | 45,3 | 15,0 | 52 | 0,2 |

**Decisão:** treinar e validar no **Nordeste**.

- Com 28 linhas por preditor, fica acima da regra prática de 10–20 e permite
  CV repetida com cerca de 290 municípios por fold de teste (5 folds). PE+BA
  ficaria no limite (11 linhas por preditor; ~115 por fold).
- Inclui os municípios nordestinos da bacia do São Francisco (BA, PE, AL e SE)
  e o contexto semiárido da região da FACAPE.
- A relevância local entra como **análise por subgrupo**: os 8 municípios da
  RIDE e os 572 de PE+BA terão erro reportado separadamente. Eles não filtram o
  treino.
- O recorte nacional daria mais linhas, mas mistura realidades operacionais muito
  diferentes da região de interesse; fica como comparação de sensibilidade
  possível na E5.

## 3. Critério “não-toy”

| Critério | Situação | Evidência |
| -------- | -------- | --------- |
| (a) proveniência documentada | Atendido | Páginas, instituição, data de consulta, arquivos e hashes identificados na seção 1 |
| (b) volume e atributos | Atendido pelo critério de atributos | O recorte tem 1.458 municípios (abaixo de 5.000), mas a base de 2023 contém 55 indicadores distintos (acima do mínimo alternativo de 40 atributos); 52 passam pela regra de ausência |
| (c) alvo não trivial | Atendido com ressalva temporal | IAG2013 é calculado a partir de cinco campos; prevê-se 2024 com dados de 2023, sem usar atributos de 2024. A variação absoluta média entre os anos é de 8,2 p.p., e 65 municípios variam mais de 30 p.p., então repetir o valor anterior não resolve o problema |
| (d) licença | Análise documentada; aplicabilidade não confirmada | O site declara CC BY-ND 3.0 para seu conteúdo, mas não foi localizada licença específica para as planilhas. Não redistribuir os arquivos; confirmar com o Ministério antes de publicar dados derivados |

O conjunto é tabular. Reportar o tamanho real e não aumentar a contagem
misturando níveis municipal, prestador e regional.

## 4. Variáveis

O perfil completo de cada indicador no recorte (aba, nome, unidade, % ausente,
mínimo, mediana, máximo, uso) está em
[`../reports/tables/perfil-preditores-nordeste-ref2023.csv`](../reports/tables/perfil-preditores-nordeste-ref2023.csv).
Resumo por grupo:

| Coluna / grupo | Tipo | Unidade | Faixa no recorte | % nulos | Origem | Uso |
| -------------- | ---- | ------- | ---------------- | ------: | ------ | --- |
| `cod_IBGE` | Identificador | código municipal | 7 dígitos; sem duplicatas em cada ano | 0 | todas as abas | Junção 2023 ↔ 2024; excluir dos preditores |
| Macrorregião, UF, Município | Categórica | — | 9 UFs do Nordeste | 0 | todas as abas | Filtro do recorte, subgrupos e conferência; excluir dos preditores |
| Capital, RM/RIDE | Categórica | — | RM/RIDE em branco quando o município não pertence a uma região metropolitana | — | todas as abas | Identifica o subgrupo RIDE Petrolina–Juazeiro; excluir dos preditores |
| Natureza jurídica, nome e sigla do prestador (CAD0002/5/6) | Categórica | — | Alta cardinalidade | — | todas as abas | Excluir: identificam o prestador e não generalizam |
| IAG0001–IAG0006 (atendimento) | Numérica | % | 0–100 | 1,0–3,0 (IAG0005: 42,0) | Atendimento 2023 | Candidatos, exceto IAG0005 |
| IAG1001–IAG1004 (estrutura) | Numérica | m/ligação, econ./ligação, % | ex.: IAG1001 1,9–784,1 m/ligação | 0,3–1,8 | Estruturais e Operacionais 2023 | Candidatos |
| IAG2001–IAG2016, IAG2023 (operação, consumo e perdas) | Numérica | %, m³/economia/mês, l/hab/dia, m³/km/dia, l/lig/dia, kWh/m³ | ex.: IAG2006 8,8–6.374,9 l/hab/dia; IAG2005 mínimo −719,1 | 0–3,8 | Estruturais e Operacionais 2023 | Candidatos; revisar extremos na E3 |
| IAG3001–IAG3008 (qualidade) | Numérica | economias/evento, horas/reparo, % | ex.: IAG3007 0,01–604,9% | 1,8–17,3 (IAG3002: 40,1) | Qualidade 2023 | Candidatos, exceto IAG3002 |
| IFA0001–IFA2016 (administrativo e financeiro) | Numérica | R$/m³, %, dias, ligações/empregado | ex.: IFA1004 −70,7–100%; IFA2011 até 154.089% | 0,1–3,6 | Administrativo e Financeiro 2023 | Candidatos; revisar extremos na E3 |
| **IAG2013 — 2023** | Numérica | % | 0–97,8 | 0 no recorte | Estruturais e Operacionais 2023 | Alvo defasado: baseline de persistência e preditor |
| **IAG2013 — 2024** | Numérica | % | 0–100 | 0 no recorte | Indicadores de Gestão 2024 | **Alvo** |

**Regra de seleção:** entram como candidatos os indicadores numéricos de 2023
com até 20% de valores ausentes ou “Não Calc.” no recorte (parâmetro
`max_ausentes_preditor` em `src/data/auditoria_sinisa.py`). Resultado: **52 candidatos**,
mais IAG2013 de 2023. Ficam fora **IAG0005** (42,0% ausente) e **IAG3002**
(40,1%). IAG3001 (17,3%) e IAG3007 (14,8%) passam no corte, mas vão exigir
imputação justificada na E3.

Textos como “Não Calc.- Dados Não Inf.” e “Não Calc.- Div/0” são contados
como ausentes, e não como zero.

**Atenção à colinearidade:** IAG2010, IAG2011, IAG2012, IAG2014 e IAG2015
medem consumo, faturamento ou perdas do mesmo ano de 2023 e são fortemente
ligados a IAG2013 de 2023. Isso não é vazamento, porque todos são do ano `t`.
Mesmo assim, a E3 precisa tratar essa redundância, por correlação ou por
seleção de atributos dentro da CV.

## 5. Variável-alvo

- **Nome/código:** IAG2013 — Perdas totais de água na distribuição.
- **Unidade:** percentual.
- **Definição operacional:** `[(GTA1001 + GTA1009 - GTA1207 - GTA1211 - GTA1203) / (GTA1001 + GTA1009)] × 100`,
  ou seja, o volume produzido e importado menos o consumido e o exportado,
  dividido pelo volume produzido e importado.
- **Distribuição no recorte:** 2024 tem média de 39,9%, desvio de 20,4 p.p.,
  mínimo de 0% e máximo de 100%. Para comparação, o Brasil tem média de 33,2%;
  o Nordeste perde mais água que a média nacional.
- **Por que não é trivial:** é uma razão entre cinco campos informados pelo
  prestador, não uma cópia de coluna. O modelo usa só dados de 2023 para prever
  2024. A persistência (repetir o valor de 2023) erra em média 8,2 p.p. no
  recorte, e essa é exatamente a referência que o modelo precisa superar
  (pergunta da E1).

As notas metodológicas confirmam a mesma fórmula nos dois anos. Porém, em 2023
também não se calcula o indicador quando `GTA1203 > 5 × GTA1211`, condição que
não aparece em 2024. Portanto, **a igualdade da fórmula não comprova
comparabilidade plena da série**. A análise 2023→2024 é exploratória, com uma
única transição anual. Não interpretar o resultado como validação em anos
futuros.

O filtro 0–100% é uma regra de plausibilidade, não uma correção dos registros.
No Nordeste, 2 valores de 2023 estão fora da faixa e não entram na amostra.

## 6. Qualidade e riscos

Valores medidos no recorte Nordeste. As contagens estão em
[`../reports/tables/qualidade-alvo-nordeste.csv`](../reports/tables/qualidade-alvo-nordeste.csv),
e a lista de municípios com alvo extremo ou salto entre os anos está em
[`../reports/tables/casos-alvo-nordeste.csv`](../reports/tables/casos-alvo-nordeste.csv).

| Item verificado | Resultado | Ação |
| --------------- | --------- | ---- |
| Duplicatas | Nenhum `cod_IBGE` duplicado em 2023 nem em 2024 | Junção 1:1 pelo código IBGE, nunca pelo nome |
| Nulos no alvo de 2023 | 41 de 1.668 municípios não numéricos (31 “Dados Não Inf.”, 10 “Div/0”) | Excluir do pareamento |
| Municípios sem linha em 2024 | 172 municípios do Nordeste presentes em 2023 não aparecem no arquivo de 2024; 9 aparecem sem valor numérico | Excluir; registrar como perda de cobertura |
| **Cobertura do Piauí** | Só 17 de 181 municípios do PI no arquivo de 2023 têm par válido (9,4%): o arquivo de 2024 traz apenas 36 municípios do PI. As demais UFs têm cobertura de 91% a 100% (`reports/tables/cobertura-nordeste-uf.csv`) | O modelo não representa o Piauí; não generalizar para essa UF e reportar a limitação |
| Valores fora de faixa no alvo | 2 negativos em 2023; nenhum em 2024 | Fora da amostra pelo filtro 0–100% |
| Valores extremos plausíveis? | 20 pares têm IAG2013 ≤ 1% ou ≥ 95% em algum dos anos (ex.: Cacimbas/PB e Desterro/PB com 0% nos dois anos; Riacho dos Cavalos/PB de 0% para 100%) | Perda de 0% ou 100% é fisicamente implausível; testar na E5 a sensibilidade com e sem esses casos |
| Saltos entre anos | 65 municípios variam mais de 30 p.p. de 2023 para 2024; na RIDE, Casa Nova/BA vai de 7,0% para 68,1% | Pode ser mudança real ou de informação; documentar como limite do baseline e analisar nos erros |
| Extremos nos preditores | Valores negativos ou muito altos em IAG2005, IAG2006, IAG2012, IFA1001, IFA1004, IFA2011 e outros (ver CSV) | Investigar antes de limitar ou transformar (E3); não remover sem justificativa |
| Variáveis constantes | Nenhum dos 55 indicadores é constante no recorte | — |
| Inconsistência temporal | Uma única transição (2023 → 2024); critério extra de não cálculo em 2023 | Análise exploratória; não alegar comparabilidade plena |
| Subnotificação / viés | Dados autodeclarados por prestadores; a cobertura varia por UF (caso do PI) | Descrever a cobertura; não tratar como censo operacional |
| Dado pessoal identificável | Nenhum campo de pessoa natural; há nomes de município e prestador | Excluir identificadores dos preditores |

## 7. LGPD e reprodutibilidade

- **Dados pessoais:** nenhum dado de pessoa natural foi identificado nos campos examinados. Códigos municipais e campos de identificação do prestador são mantidos apenas para junção e conferência.
- **Estratégia:** dados já agregados por município. Os identificadores ficam fora dos preditores. Esta verificação precisa ser refeita caso outras fontes sejam adicionadas.
- **Risco de reidentificação:** baixo nos indicadores agregados; reavaliar se outras fontes forem combinadas.
- **Base legal:** não há tratamento de dado pessoal de pessoa natural no recorte atual; reavaliar se o escopo mudar.
- **Licença:** ver seção 1. A licença geral do site não foi presumida como licença dos arquivos de dados.
- **Como reproduzir esta auditoria:**
  1. Baixar os dois ZIPs da seção 1.
  2. Extrair os dois arquivos de indicadores da pasta `Água - Base Municipal` para `data/raw/`.
  3. Executar `python -m src.data.auditoria_sinisa` a partir da pasta do grupo (requer pandas e openpyxl).
- **Verificação manual do hash no Windows:** `Get-FileHash "data/raw/<arquivo.xlsx>" -Algorithm SHA256`
