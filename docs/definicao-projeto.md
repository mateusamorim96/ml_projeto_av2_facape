# 📌 Definição do Projeto AV2 — ML para os ODS

> Documento de referência do professor. É a **fonte de verdade** do que conta como
> projeto válido. Alterações aqui são feitas apenas pelo professor (via issue).

---

## 1. O problema que o projeto resolve

Toda equipe de ML enfrenta a mesma tentação: começar pelo algoritmo. O projeto
AV2 inverte a ordem — começa pelo **problema social** e termina em uma **decisão
operacional** que alguém tomaria com o modelo em mãos.

```text
ODS da ONU  →  meta específica  →  tema  →  pergunta de ML
                                              ↓
                    decisão ("se o modelo indicar X, Y fará Z")
                                              ↓
        dados reais → pipeline → modelos → validação estatística
                                              ↓
              artigo → Docker → repositório → defesa
```

Sem decisão explícita, o projeto é um exercício de `fit`/`predict`: tecnicamente
correto e socialmente irrelevante.

---

## 2. Regras de escopo

### 2.1 ODS e meta (obrigatório)

- Escolher **uma** das 17 ODS da Agenda 2030.
- Identificar a **meta pelo número** (ex.: meta 6.1, meta 11.6, meta 3.6), não a
  ODS “em geral”.
- Justificar por que o problema tem relevância **local** (Pernambuco, semiárido,
  bacia hidrográfica, rede municipal de ensino etc.), quando possível.

### 2.2 Pergunta e decisão (obrigatório)

A pergunta precisa ser falsificável e terminar em ação:

| Ruim | Bom |
| ---- | --- |
| “Prever a qualidade da água” | “Classificar amostras com risco de não conformidade para priorizar coleta — se o modelo indicar risco alto em um ponto, a equipe de campo visita esse ponto na semana seguinte” |
| “Analisar evasão escolar” | “Identificar escolas com risco de queda de frequência acima de 5 p.p. para alocar o programa de busca ativa — se risco > 0,6, a escola entra na lista de visitas do bimestre” |

### 2.3 Dados (obrigatório)

- Dataset **real, documentado e de fonte identificável**.
- **Proibidos** (e equivalentes de tutorial): Iris, Titanic, Wine, Digits, Breast
  Cancer Wisconsin, Boston Housing, Diabetes (sklearn), Penguins.
- Também proibido: dados sintéticos fabricados pelo próprio grupo.
- Critério “não-toy” (atender a **pelo menos três**, sendo (a) e (b) obrigatórios):
  1. (a) proveniência institucional/pública com documentação (dicionário de dados,
     nota técnica ou artigo);
  2. (b) ≥ 5.000 registros **ou** ≥ 40 atributos **ou** dados não tabulares
     (imagem, texto, série temporal, geoespacial);
  3. alvo não trivial (não é cópia de outra coluna nem regra determinística);
  4. licença compatível com uso acadêmico e publicação do código.

Catálogo de fontes sugeridas: [`fontes-dados.md`](fontes-dados.md).

### 2.4 Modelagem (obrigatório)

- **Baseline** simples e interpretável antes de qualquer modelo complexo
  (regressão logística, árvore rasa, `DummyClassifier`/`DummyRegressor`).
- Pelo menos **três famílias** de modelos comparadas.
- Preparação **sem vazamento**: todo `fit` de transformação dentro do `Pipeline`,
  ajustado apenas no treino de cada fold.
- Ajuste de hiperparâmetros **aninhado** quando o mesmo CV for usado para
  selecionar e avaliar.

### 2.5 Comparação estatística (obrigatório)

- Folds **idênticos** entre modelos (comparação pareada).
- Média **e** desvio em validação cruzada repetida.
- Teste estatístico adequado: Wilcoxon (2 modelos), t pareado corrigido de
  Nadeau–Bengio, McNemar (mesmo conjunto de teste), Friedman + Nemenyi/
  Bonferroni–Dunn (≥ 3 modelos).
- Reportar **tamanho de efeito** e **intervalo de confiança**; p-valor sozinho não
  decide nada.

### 2.6 Entregáveis de comunicação (obrigatório)

- **Artigo curto IMRaD** (4–8 páginas, ≥ 8 referências, tabelas geradas por
  script).
- **README executivo** com ODS, problema, dados, como reproduzir, resultados e
  limitações.
- **Slides** (8–12) e defesa de 10 min + 5 min de arguição.

### 2.7 Reprodutibilidade (obrigatório)

- `Dockerfile` com imagem base **fixada** (tag ou digest) e `requirements.txt`
  com versões `==`.
- **Um único comando** executa o pipeline completo em ambiente limpo.
- Sementes fixadas (`SEED`) e `reports/environment.json` com versões e hash do
  commit.
- Evidência de reprodução por terceiro (log, captura ou CI).

### 2.8 Ética, LGPD e uso responsável (obrigatório)

- Nenhum dado pessoal identificável no repositório.
- Desempenho **por subgrupo** quando o modelo afeta pessoas, com discussão de
  risco de discriminação.
- Declarar usos inadequados (“este modelo não deve ser usado para…”).
- Declarar uso de IA generativa (quais partes, finalidade, como foi verificado).

### 2.9 Fora do escopo

Implantação em produção com usuários reais, aplicativo/front-end elaborado,
treinamento de LLM, *deep learning* como único método, coleta primária com seres
humanos e serviços pagos de nuvem.

---

## 3. Fases do projeto

| Fase | Pergunta que a fase responde | Entrega |
| ---- | ---------------------------- | ------- |
| 1. ODS e tema | Qual problema social, de qual meta, com qual decisão? | E1 |
| 2. Dados | Que dados existem, de onde vêm, qual a licença e o risco? | E2 |
| 3. Formulação | Classificação/regressão/clustering? Qual métrica e por quê? | E2–E3 |
| 4. Preparação | Como evitar vazamento e garantir pipeline reproduzível? | E3 |
| 5. Modelagem | Baseline, três famílias, ajuste e seleção | E4 |
| 6. Comparação | A diferença é real? Teste, efeito e IC | E5 |
| 7. Interpretação | O que o modelo erra e para quem? Qual o uso seguro? | E6–E7 |
| 8. Artigo | IMRaD com números coerentes com o código | E7 |
| 9. Reprodutibilidade | Alguém reproduz com um comando? | E6 |
| 10. Repositório e defesa | O trabalho é auditável e defendido? | E6–E8 |

Detalhamento de critérios de aceite por entrega:
[`requisitos-entrega.md`](requisitos-entrega.md).

---

## 4. Identificadores de requisito

Os critérios usam prefixos estáveis, úteis para citar no README e no artigo:

| Prefixo | Dimensão | Exemplo |
| ------- | -------- | ------- |
| `RQ-ODS` | ODS, meta, tema e decisão | `RQ-ODS-01` |
| `RQ-DAD` | dados, licença, LGPD | `RQ-DAD-03` |
| `RQ-FOR` | formulação e métrica | `RQ-FOR-01` |
| `RQ-MOD` | modelagem e baseline | `RQ-MOD-04` |
| `RQ-EST` | comparação estatística | `RQ-EST-01` |
| `RQ-REP` | reprodutibilidade | `RQ-REP-01` |
| `RQ-GIT` | repositório e histórico | `RQ-GIT-03` |
| `RQ-ART` | artigo e números | `RQ-ART-02` |
| `RQ-ÉT` | ética e uso responsável | `RQ-ÉT-02` |
| `RQ-APR` | apresentação e defesa | `RQ-APR-02` |

A versão completa, com critério de aceite verificável por requisito, está no
documento **Requisitos do Projeto 2026.2 — Machine Learning** distribuído com o
material da disciplina (aula 21 do plano de aulas).
