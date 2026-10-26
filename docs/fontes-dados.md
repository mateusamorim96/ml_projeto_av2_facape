# 🔎 Fontes de Dados e Critério “Não-Toy”

> Escolher dados é a decisão mais irreversível do projeto. Um dataset ruim
> consome três semanas e entrega um resultado que ninguém acredita.

---

## 1. O filtro obrigatório

Antes de investir tempo, aplique os cinco testes. Se falhar em qualquer um,
troque de dataset **na E2**, não na E5.

| # | Teste | Pergunta objetiva |
| - | ----- | ----------------- |
| 1 | Proveniência | Existe instituição responsável, documentação e data de referência? |
| 2 | Volume | ≥ 5.000 registros **ou** ≥ 40 atributos **ou** dado não tabular? |
| 3 | Alvo não trivial | O alvo é cópia de coluna, resultado de regra determinística ou rótulo ruidoso? |
| 4 | Licença | Permite uso acadêmico e publicação de código e resultados? |
| 5 | LGPD | Há dado pessoal identificável? Dá para agregar/remover sem destruir o sinal? |

### Proibidos

Iris, Titanic, Wine, Digits, Breast Cancer Wisconsin, Boston Housing, Diabetes
(sklearn), Penguins — e qualquer variação de tutorial desses conjuntos. Também é
proibido gerar dados sintéticos próprios para simular o problema.

---

## 2. Catálogo de fontes por área

| Fonte | O que oferece | Cuidados |
| ----- | ------------- | -------- |
| **dados.gov.br** | Dados abertos federais: saúde, educação, meio ambiente, transporte | metadados irregulares; confira periodicidade |
| **OpenDataSUS / DATASUS** | SIH, SIM, SINASC, SINAN, e-SUS | microdados com risco de reidentificação: agregue por município |
| **INEP** | Censo Escolar, ENEM, SAEB, indicadores de fluxo | granularidade escolar é suficiente e menos sensível |
| **IBGE (SIDRA, PNAD, Censo)** | população, renda, saneamento, trabalho | chaves de junção por município/ano |
| **INPE / TerraBrasilis** | PRODES (desmatamento), focos de queimada, satélite | séries temporais e dados geoespaciais |
| **SNIS / ANA / INMET** | saneamento, recursos hídricos, clima | cobertura municipal desigual |
| **UCI ML Repository** | bases reais de energia, água, sensores | escolha as que têm dicionário de dados |
| **OpenML** | coleções com metadados de tarefa | confira se não é versão de dataset didático |
| **Kaggle Datasets** | volume alto | exige checar origem primária e licença; nunca versione o arquivo |
| **World Bank / WHO / UN Data** | indicadores por país | agregação alta; bom para séries temporais |
| **Portal da Transparência / TCE** | execução orçamentária, licitações | útil para ODS 16 |

---

## 3. Mapa ODS → problema → métrica típica

| ODS | Exemplo de problema de ML | Métrica principal |
| --- | ------------------------- | ----------------- |
| 2 Fome zero | prever insegurança alimentar por município | F1 (classe minoritária) |
| 3 Saúde | triagem de risco / tempo até óbito | recall, AUC-PR |
| 4 Educação | risco de evasão ou queda de proficiência | recall + custo por erro |
| 6 Água potável | não conformidade de amostras de água | AUC-PR, precisão em alerta |
| 7 Energia limpa | previsão de geração renovável | MAE/MAPE por horizonte |
| 8 Trabalho decente | risco de acidente ocupacional | recall, AUC |
| 11 Cidades | expansão urbana / ilhas de calor | IoU, MAE espacial |
| 13 Clima | focos de queimada / desmatamento | AUC-PR, recall em alerta |
| 16 Instituições | anomalias em licitações públicas | precision@k, AUC-PR |

A métrica precisa conversar com a **decisão**. Em alerta com equipe pequena, o
erro caro é o falso negativo: priorize recall com precisão mínima aceitável.

---

## 4. Auditoria de dados (o que registrar na E2)

Preencha no `docs/dicionario-de-dados.md`:

```text
Fonte:            <instituição> — <URL>
Data de acesso:   AAAA-MM-DD
Versão/recorte:   <ano, UF, filtros aplicados>
Licença:          <nome> — <link da licença>
Hash do arquivo:  sha256:<...>   (obtido com `sha256sum arquivo.csv`)
Registros:        <n>
Atributos:        <n>
Alvo:             <nome> — <definição operacional>
Desbalanceamento: <proporção das classes>
Nulos por coluna: <tabela>
Risco LGPD:       <nenhum / dado pessoal removido / agregado por município>
```

Comando útil para o hash:

```bash
sha256sum data/raw/arquivo-baixado.csv | tee -a docs/dicionario-de-dados.md
```

---

## 5. Sinais de que o dataset vai dar problema (troque agora)

- A variável-alvo é derivada de uma coluna que você também usa como atributo.
- O alvo tem 98% de uma classe e não há métrica além de acurácia planejada.
- Chaves de junção por município, mas você quer inferência individual.
- Documentação inexistente e colunas sem dicionário.
- Série temporal com quebras de metodologia no meio.
- Dados pessoais sem possibilidade de agregação.
- O arquivo só existe em um link temporário (Drive pessoal, por exemplo).
