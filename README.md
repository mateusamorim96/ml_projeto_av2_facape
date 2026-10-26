# 🤖 Projeto AV2 — Machine Learning para os ODS (FACAPE, 2026.2)

> Projeto avaliativo da disciplina **Machine Learning**
> Curso de Engenharia de Software · Professor: Mateus Silva
> Semestre: **2026.2**

---

## 📋 Contexto

Este repositório é o **ponto único de entrega** do Projeto AV2. Cada grupo entrega
o projeto completo (dados, código, modelo, artigo, Docker e slides) **dentro de
uma única pasta**:

```text
grupos/grupo-NN-slug-do-tema/
```

O tema do projeto é livre dentro de uma regra: o problema precisa nascer de **uma
das 17 ODS da Agenda 2030 da ONU**, com **meta específica** identificada pelo
número (ex.: meta 6.1, meta 11.6, meta 3.6). A pergunta de ML deve terminar em uma
**decisão**: “se o modelo indicar X, a equipe Y fará Z”.

Especificação normativa completa: documento **Requisitos do Projeto 2026.2**
(`Requisitos-Projeto-2026.2-ML.pdf`, distribuído com o material da disciplina).
Síntese operacional neste repositório:
[`docs/definicao-projeto.md`](docs/definicao-projeto.md).

---

## 🗂️ Estrutura do Repositório

```text
ml_projeto_av2_facape/
│
├── README.md                        ← este arquivo (mantido pelo professor)
├── CONTRIBUTING.md                  ← regras de contribuição e fluxo de PR
├── LICENSE
│
├── .githooks/
│   └── pre-commit                   ← bloqueia commit fora da pasta do grupo
│
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md     ← checklist obrigatório no PR
│   ├── ISSUE_TEMPLATE/
│   │   └── entrega-grupo.md         ← template de issue de entrega
│   ├── CODEOWNERS
│   └── workflows/
│       └── validar-entrega.yml      ← CI: escopo, estrutura, dados e segredos
│
├── scripts/
│   ├── check_entrega.py             ← validador local (mesma regra da CI)
│   └── novo_grupo.py                ← scaffolder: cria a pasta do grupo
│
├── docs/                            ← fonte de verdade (professor)
│   ├── definicao-projeto.md         ← ODS, decisão, fases do projeto
│   ├── requisitos-entrega.md        ← entregas E0–E8, rubrica, anti-padrões
│   ├── estrutura-projeto.md         ← árvore mínima dentro da pasta do grupo
│   ├── fontes-dados.md              ← catálogo de fontes + critério “não-toy”
│   └── templates/                   ← modelos de artefato (use, não reinvente)
│
└── grupos/
    ├── README.md                    ← alocação dos códigos G01…G12
    ├── _template/                   ← esqueleto completo (copiado pelo script)
    └── grupo-NN-slug-do-tema/       ← A PASTA DE CADA GRUPO
```

> ⚠️ **Regra de ouro:** cada grupo escreve **exclusivamente** dentro de
> `grupos/grupo-NN-*/`. Qualquer alteração fora dela **reprova a CI** e o PR não
> pode ser mesclado. Precisa mudar algo em `docs/`? Abra uma *issue*.

---

## 👥 Grupos, Códigos e Alocação de Pastas

O **número do grupo** (`NN`) é a chave do namespace: dois grupos nunca podem usar
o mesmo `NN`. A alocação oficial fica em [`grupos/README.md`](grupos/README.md).

| Código | Pasta esperada | ODS / tema | Estado |
| ------ | -------------- | ---------- | ------ |
| G01 | `grupos/grupo-01-*` | a definir | livre |
| G02 | `grupos/grupo-02-*` | a definir | livre |
| G03 | `grupos/grupo-03-*` | a definir | livre |
| G04 | `grupos/grupo-04-*` | a definir | livre |
| G05 | `grupos/grupo-05-*` | a definir | livre |
| G06 | `grupos/grupo-06-*` | a definir | livre |
| G07 | `grupos/grupo-07-*` | a definir | livre |
| G08 | `grupos/grupo-08-*` | a definir | livre |
| G09 | `grupos/grupo-09-*` | a definir | livre |
| G10 | `grupos/grupo-10-*` | a definir | livre |
| G11 | `grupos/grupo-11-*` | a definir | livre |
| G12 | `grupos/grupo-12-*` | a definir | livre |

### Criando a pasta do grupo (30 segundos)

```bash
# na raiz do repositório clonado
python3 scripts/novo_grupo.py --numero 3 --tema saneamento-ana
# cria grupos/grupo-03-saneamento-ana/ com o esqueleto completo
```

Regras de nome: `grupo-` + **dois dígitos** + `-` + *slug* em kebab-case, sem
acento e sem espaço (`grupo-03-saneamento-ana`). O script recusa número já usado
por outro grupo.

---

## 🔄 Fluxo de Trabalho

```text
1. Configure o hook local:  git config core.hooksPath .githooks
2. Fork deste repositório para a conta do grupo
3. Clone o fork e cadastre o upstream do professor
4. Crie a pasta do grupo com scripts/novo_grupo.py (uma única vez)
5. Trabalhe APENAS dentro de grupos/grupo-NN-*/
6. Valide localmente:  python3 scripts/check_entrega.py --grupo grupo-03 --entrega E6
7. Commit no padrão:   [G03] feat: adiciona pipeline de preparacao
8. Push na branch:     grupo-03/pipeline-preparacao
9. Abra o Pull Request para main deste repositório
10. CI valida escopo, estrutura, dados e segredos; professor revisa e aprova
```

Regras completas (nomenclatura, commits, conflitos, política de dados):
[`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## 📦 O que cada grupo entrega

O projeto é avaliado em **oito entregas** (E1–E8), acumulativas. O detalhamento,
pesos e critérios de aceite estão em
[`docs/requisitos-entrega.md`](docs/requisitos-entrega.md).

| Entrega | Semana | Conteúdo central | Peso |
| ------- | ------ | ---------------- | ---- |
| E1 | 1 | `docs/proposta.md`: ODS, meta, tema, pergunta e decisão | 5% |
| E2 | 2 | dataset auditado + dicionário de dados + licença | 10% |
| E3 | 3 | EDA (5 visualizações) + pipeline de preparação executável | 10% |
| E4 | 4 | baseline + 3 famílias de modelos + tabela comparativa | 10% |
| E5 | 5 | CV repetida + testes estatísticos + gráficos com IC | 15% |
| E6 | 6 | repositório completo + Docker funcional + README executivo | 20% |
| E7 | 7 | artigo IMRaD + slides | 20% |
| E8 | 8 | apresentação (10 min) + defesa (5 min) | 10% |

Estrutura interna obrigatória da pasta do grupo:
[`docs/estrutura-projeto.md`](docs/estrutura-projeto.md).

---

## 🚫 O que reprova na hora

- Dataset didático (**Iris, Titanic, Wine, Digits, Breast Cancer, Boston,
  Diabetes, Penguins**) ou dados sintéticos fabricados pelo grupo.
- `data/raw/` versionado, dados pessoais identificáveis ou credenciais no repo.
- Arquivo alterado fora da pasta do grupo.
- Pasta de grupo com número duplicado (dois `grupo-03-*`).
- `requirements.txt` sem versões fixas, `Dockerfile` com `:latest`.
- Tabela de resultados digitada à mão em desacordo com o código.

Lista completa de anti-padrões:
[`docs/requisitos-entrega.md`](docs/requisitos-entrega.md#anti-padrões).

---

## 🧰 Validação local

```bash
python3 scripts/check_entrega.py --grupo grupo-03 --entrega E6
python3 scripts/check_entrega.py --namespace          # checa todos os grupos
```

Saída: `ERRO` (bloqueia o PR), `AVISO` (registrado, não bloqueia), `RESULTADO`.
Código de saída `0` = aprovado, `1` = reprovado, `2` = erro de uso. Sem
dependências externas (Python 3.10+).

---

## 📄 Licença

Material didático sob [MIT](LICENSE). Cada grupo declara a licença do **dataset**
usado na seção “Dados e licença” do seu `README.md`.
