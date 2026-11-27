# G02 — Previsão de perdas de água em municípios do Nordeste

> Projeto AV2 de Machine Learning · FACAPE 2026.2  
> Pasta: `grupos/grupo-02-perdas-agua-ods6` · E2: auditoria concluída, com ressalvas ·
> E3: EDA e pipeline de preparação executáveis

## Integrantes

| Nome | Matrícula | Papel |
| ---- | --------- | ----- |
| Alan Herculino Siqueira | 25782 | A definir pelo grupo |
| Davi Cordeiro Gomes | 25794 | A definir pelo grupo |
| Henderson Silva | 25883 | A definir pelo grupo |
| Bruno Barros da Silva | 25932 | A definir pelo grupo |

## 1. ODS, meta e problema

- **ODS:** 6 — Água potável e saneamento.
- **Meta:** 6.4 — aumentar a eficiência do uso da água e contribuir para o
  enfrentamento da escassez hídrica.
- **Tema:** previsão de perdas de água em redes de distribuição de municípios
  brasileiros por meio de Machine Learning.
- **Problema:** avaliar se indicadores municipais de um ano permitem prever o
  percentual de perdas de água no ano seguinte, sujeito à compatibilidade
  metodológica da série histórica.
- **Público/beneficiário:** equipes responsáveis pelo abastecimento e gestores
  municipais de saneamento.

## 2. Decisão

> “Se o modelo indicar uma previsão de perdas de água acima de um limite
> previamente definido, a equipe responsável pelo abastecimento poderá priorizar
> uma avaliação técnica do sistema em até 30 dias.”

- **Custo do falso positivo:** priorizar avaliação de um sistema que não esteja
  entre os de maior perda, utilizando recursos que poderiam ser direcionados a
  outro local.
- **Custo do falso negativo:** atrasar a avaliação de um sistema com perdas
  elevadas.
- **Métrica principal:** MAE, em pontos percentuais se compatível com a unidade
  oficial do alvo. A acurácia não se aplica à regressão.
- A previsão é apoio à triagem, não diagnóstico nem decisão automática. O
  limite de alerta será definido após auditar o alvo e discutir o critério de
  priorização.

## 3. Dados e licença

- **Fonte:** SINISA — módulo Abastecimento de Água, Bases Municipais com anos
  de referência 2023 e 2024.
- **Instituição:** Ministério das Cidades.
- **Portal de referência 2023:** https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/resultados-sinisa
- **Portal de referência 2024:** https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/resultados-sinisa/resultados-sinisa-2025
- **Produtos de água:** [planilhas SINISA referência 2023](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/arquivos/SINISA_Resultados_Ref2023.zip) e [planilhas SINISA referência 2024](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/resultados-sinisa/SINISA_Resultados_Ref2024.zip).
- **Arquivos usados:** pasta `Água - Base Municipal` de cada ZIP; planilha de
  indicadores de 2023 (entrada) e de 2024 (alvo, versão “Retificação”).
- **Recorte:** Região **Nordeste**, transição 2023 → 2024. A RIDE do Polo
  Petrolina/PE e Juazeiro/BA (8 municípios) e PE+BA (572) são analisados como
  subgrupos; sozinhos não têm linhas suficientes para treinar e validar. A
  comparação entre recortes está no dicionário de dados.
- **Consulta das páginas:** 2026-11-25; reconferência das fontes oficiais em 2026-11-26. Download dos arquivos em 23/11/2026.
- **Licença/termos de uso:** o rodapé do portal declara CC BY-ND 3.0 para o conteúdo do site ([licença](https://creativecommons.org/licenses/by-nd/3.0/)); não foi localizada licença específica das planilhas nem confirmação de que a declaração geral se aplique a elas. O grupo não redistribuirá os arquivos originais ou bases derivadas enquanto isso não for esclarecido. Detalhes e limitações no dicionário de dados.
- **Volume observado:** 1.458 municípios do Nordeste com IAG2013 numérico e
  entre 0–100% nos dois anos (de 1.668 no arquivo de 2023); 52 indicadores
  candidatos a preditor. A base de 2023 tem 55 indicadores distintos, atendendo
  ao critério alternativo de pelo menos 40 atributos; a amostra fica abaixo de
  5.000 registros. O Piauí tem cobertura de só 9,4% e não é representado.
- **Alvo:** IAG2013 — Perdas totais de água na distribuição, em percentual. A fórmula, cobertura e limitações metodológicas estão registradas no dicionário de dados.
- **Dados pessoais:** não identificamos campos de pessoa natural nas planilhas
  municipais de indicadores examinadas. Campos de identificação do município
  e do prestador não serão usados como preditores.
- Detalhes da auditoria estão registrados em
  [`docs/dicionario-de-dados.md`](docs/dicionario-de-dados.md).
- As tabelas da auditoria são geradas por
  `python -m src.data.auditoria_sinisa` (requer pandas e openpyxl) em
  `reports/tables/` (perfil dos preditores do Nordeste, cobertura por recorte
  e por UF, qualidade do alvo, hashes). O perfil nacional anterior continua em
  [`reports/tables/perfil-preditores-ref2023.csv`](reports/tables/perfil-preditores-ref2023.csv)
  como referência.

## 4. Como reproduzir

Pré-requisito: baixar os dois ZIPs oficiais da seção 3 e extrair a pasta
`Água - Base Municipal` de cada um em `data/raw/` (os arquivos não são
versionados). O pipeline confere o SHA-256 dos dois arquivos de indicadores e
para se eles diferirem dos auditados na E2.

```bash
# a partir de grupos/grupo-02-perdas-agua-ods6/ (Python 3.11+)
python -m venv .venv
.venv/Scripts/activate            # Windows (Linux/macOS: source .venv/bin/activate)
python -m pip install -r requirements.txt
python -m src.pipeline --config configs/base.yaml   # ~5 s: carga + split + preparação
make eda                                            # ~30 s: reexecuta o notebook de EDA
```

Sem `make` (Windows), o equivalente de `make eda` é:

```bash
python -c "import nbformat; from nbclient import NotebookClient; p='notebooks/01-eda-perdas-agua.ipynb'; nb=nbformat.read(p, 4); NotebookClient(nb, timeout=600, kernel_name='python3', resources={'metadata': {'path': 'notebooks'}}).execute(); nbformat.write(nb, p)"
```

Também é possível abrir o notebook no VS Code/Jupyter e executar todas as células.

Etapas implementadas até a E3: `dados` (carga, recorte e pareamento
2023 → 2024) e `features` (split treino/teste e preparação sem vazamento). As
etapas `modelos` (E4) e `avaliacao` (E5) aparecem como pendentes, sem erro.
Saídas: `data/processed/` (base pareada, treino/teste originais e preparados;
não versionado), `reports/tables/preparacao-*.csv` e `reports/environment.json`.
O comando Docker será validado na E6.

## E3 — EDA e preparação

- **Notebook:** [`notebooks/01-eda-perdas-agua.ipynb`](notebooks/01-eda-perdas-agua.ipynb),
  com 6 visualizações (5 exigidas + 1 por UF), cada uma com “o que isso muda na
  modelagem”. A EDA usa **só o treino**; figuras em `reports/figures/figura-eda-*.png`.
- **Split antes de qualquer `fit`:** 1.166 municípios de treino e 292 de teste
  (20 %, seed 42), estratificado por quintis do alvo.
- **Preparação** (`src/features/preparacao.py`, ajustada só no treino):
  winsorização P1–P99 → mediana + indicador de ausência → padronização.
  53 preditores (52 indicadores de 2023 + perda de 2023); IAG0005 e IAG3002
  excluídos por ausência > 20 % no treino.
- **Nulos:** “Não Calc.” vira ausente, nunca zero. A ausência é informativa:
  municípios sem IAG3001 têm perda mediana de 54,6 % vs. 34,7 %.
- **Desbalanceamento:** proporção acima do limite de alerta = 64 % (30 %),
  43 % (40 %) e 30 % (50 %), igual em treino e teste; sem reamostragem.
- **Referência a superar:** a persistência (repetir 2023) tem MAE de 8,0 p.p. no
  treino; 54 saltos > 30 p.p. (4,6 %) respondem por ~27 % desse erro.
- Justificativas e alternativas rejeitadas: [`docs/decisoes-tecnicas.md`](docs/decisoes-tecnicas.md), seção 4.

## 5. Resultados principais

Ainda não há resultados de modelos. A avaliação planejada é de regressão, com
MAE como métrica principal e comparação com uma referência que repete a perda
observada no ano anterior. O par 2023→2024 será tratado como exploratório:
embora a fórmula do alvo seja a mesma, as notas metodológicas têm critérios de
não cálculo diferentes. Não se afirma comparabilidade plena nem generalização
para outros anos; a ressalva está detalhada no dicionário de dados.

## 6. Limitações iniciais

- A cobertura municipal, os anos disponíveis e a comparabilidade metodológica
  limitam a interpretação: há apenas uma transição anual e uma diferença nos
  critérios de não cálculo do alvo entre as referências.
- Indicadores agregados não descrevem necessariamente as condições de cada
  trecho da rede nem identificam a causa das perdas.
- Uma previsão não substitui inspeção, medição local ou avaliação por
  profissionais responsáveis.
- A licença específica das planilhas não foi localizada; não redistribuir os
  arquivos ou assumir que a licença geral do site se aplica a eles.

## 7. Uso responsável

- **Não usar para:** decisão automática, penalização de municípios ou
  prestadores, nem como diagnóstico definitivo da rede.
- **Dados pessoais:** a auditoria inicial não identificou dados de pessoa
  natural nas planilhas municipais; reavaliar se outras fontes forem usadas.
- **Desempenho por subgrupo:** o erro será reportado separadamente para a
  RIDE Petrolina–Juazeiro, para PE+BA e por UF; não há resultados nesta etapa.
  Não usar o modelo para o Piauí, sub-representado na base.
- **Uso de IA generativa:** assistente de IA foi usado como apoio para organizar
  e redigir os documentos iniciais. O grupo deve revisar as decisões e validar
  todas as informações sobre dados e metodologia.
- **Uso de IA generativa na E3:** assistente de IA (Claude) gerou o código de
  carga/preparação, o notebook de EDA e o rascunho das justificativas. Verificação:
  o pipeline foi executado do zero; a auditoria da E2 foi reexecutada e reproduziu
  as tabelas versionadas; os números citados nos textos foram conferidos com as
  saídas do código; os hashes dos arquivos baixados conferem com os da E2.

## Estrutura desta pasta

```text
grupo-02-perdas-agua-ods6/
├── README.md
├── configs/base.yaml
├── data/raw/                 # não versionar os dados brutos
├── src/
│   ├── data/                 # auditoria (E2) e carga da base pareada (E3)
│   ├── features/             # split e preparação sem vazamento (E3)
│   └── pipeline.py           # ponto de entrada
├── notebooks/                # 01-eda-perdas-agua.ipynb (E3)
├── experiments/runs.csv
├── reports/                  # tabelas e figuras geradas
├── article/                  # artigo IMRaD
├── slides/                   # apresentação
└── docs/
    ├── proposta.md
    ├── dicionario-de-dados.md
    └── decisoes-tecnicas.md
```
