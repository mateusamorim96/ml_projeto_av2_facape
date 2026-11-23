# G02 — Previsão de perdas de água em municípios brasileiros

> Projeto AV2 de Machine Learning · FACAPE 2026.2  
> Pasta: `grupos/grupo-02-perdas-agua-ods6` · Entrega atual: E1

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

- **Fonte prevista:** SINISA — módulo Abastecimento de Água, Base Municipal de
  2024 e dados históricos, se forem metodologicamente compatíveis.
- **Instituição:** Ministério das Cidades.
- **Portal:** https://portal1.snis.gov.br/
- **Data de acesso e download:** a registrar na E2, quando os arquivos forem
  obtidos e auditados.
- **Licença/termos de uso:** a confirmar na fonte oficial antes de reutilizar
  ou redistribuir os dados.
- **Volume e cobertura temporal:** a medir e documentar na E2.
- **Alvo previsto:** percentual municipal anual de perdas de água; nome,
  unidade e definição operacional serão confirmados no dicionário oficial.
- **Dados pessoais:** o plano é usar dados agregados por município; a presença
  de campos pessoais ou identificáveis será verificada antes do uso.
- Detalhes da auditoria serão registrados em
  [`docs/dicionario-de-dados.md`](docs/dicionario-de-dados.md).

## 4. Como reproduzir

O pipeline e o ambiente reprodutível serão concluídos em etapas posteriores.
Após a implementação, as instruções serão:

```bash
python3 -m venv .venv
python -m pip install -r requirements.txt
python -m src.pipeline --config configs/base.yaml
```

O comando Docker será documentado e validado na E6. O pipeline ainda não foi
implementado nem executado nesta E1; portanto, tempo de execução e saídas ainda
não estão disponíveis.

## 5. Resultados principais

Ainda não há resultados de modelos. A avaliação planejada é de regressão, com
MAE como métrica principal e comparação com uma referência que repete a perda
observada no ano anterior. Essa referência depende da confirmação de uma série
temporal compatível na E2.

## 6. Limitações iniciais

- A cobertura municipal, os anos disponíveis e a comparabilidade metodológica
  ainda serão auditados.
- Indicadores agregados não descrevem necessariamente as condições de cada
  trecho da rede nem identificam a causa das perdas.
- Uma previsão não substitui inspeção, medição local ou avaliação por
  profissionais responsáveis.
- A disponibilidade e os termos de uso dos arquivos precisam ser confirmados
  na fonte oficial.

## 7. Uso responsável

- **Não usar para:** decisão automática, penalização de municípios ou
  prestadores, nem como diagnóstico definitivo da rede.
- **Dados pessoais:** a análise será municipal e agregada; isso será verificado
  na auditoria dos arquivos antes do uso.
- **Desempenho por subgrupo:** será avaliado após identificar cobertura
  suficiente, por exemplo, entre regiões e períodos; não há resultados nesta
  etapa.
- **Uso de IA generativa:** assistente de IA foi usado como apoio para organizar
  e redigir os documentos iniciais. O grupo deve revisar as decisões e validar
  todas as informações sobre dados e metodologia.

## Estrutura desta pasta

```text
grupo-02-perdas-agua-ods6/
├── README.md
├── configs/base.yaml
├── data/raw/                 # não versionar os dados brutos
├── src/                      # carregamento, preparação, modelos e avaliação
├── notebooks/                # EDA e experimentos
├── experiments/runs.csv
├── reports/                  # tabelas e figuras geradas
├── article/                  # artigo IMRaD
├── slides/                   # apresentação
└── docs/
    ├── proposta.md
    ├── dicionario-de-dados.md
    └── decisoes-tecnicas.md
```
