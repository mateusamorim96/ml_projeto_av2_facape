# 🤝 Guia de Contribuição — Projeto AV2 de Machine Learning

Este guia define **como** o trabalho entra no repositório. O que entregar está em
[`docs/requisitos-entrega.md`](docs/requisitos-entrega.md); a árvore obrigatória
está em [`docs/estrutura-projeto.md`](docs/estrutura-projeto.md).

---

## 1. Regras Fundamentais

### ❶ Cada grupo toca APENAS a sua pasta

```text
grupos/grupo-NN-slug-do-tema/
```

Alterações fora dessa pasta reprovam a CI (`validar-entrega`) e são bloqueadas
pelo hook local. Não há exceção: nem para “corrigir um errinho” no README do
professor, nem para corrigir o arquivo de outro grupo. Precisa mudar `docs/`?
Abra uma **issue**; o professor altera.

### ❷ Namespace numérico: `NN` é exclusivo

O código do grupo (`G03`) e o número da pasta (`grupo-03`) são **a mesma coisa**.
Duas pastas com o mesmo número quebram o repositório inteiro e reprovam a CI
(`check_entrega.py --namespace`). Nunca renomeie a pasta do grupo depois da
primeira entrega: o histórico e o `CODEOWNERS` dependem dela.

### ❸ Padrão de commits

Use o prefixo do grupo em **todas** as mensagens:

```text
[G03] feat: adiciona pipeline de preparacao de dados
[G03] fix: corrige vazamento no fit do scaler
[G03] docs: descreve dicionario de dados do SINAN
[G03] test: adiciona teste de reprodutibilidade do split
[G03] chore: fixa versoes no requirements
```

Tipos permitidos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
Commits genéricos (`update`, `ajustes`, `final`) são recusados na revisão: eles
apagam a rastreabilidade entre decisão e artifact.

Mínimo de **10 commits ao longo de 4 semanas**, com pelo menos um commit de cada
integrante. `git log --format='%an' | sort | uniq -c` precisa mostrar o grupo
inteiro.

### ❹ Nomenclatura de arquivos

- **kebab-case**, minúsculas, sem acentos e sem espaços:
  `01-eda-saneamento.ipynb` — **não** `Análise Exploratória Final.ipynb`.
- Acentuação correta **dentro** dos arquivos (pt-BR), ASCII **fora** (nomes de
  arquivo, branches, commits).
- Nada de `arquivo-final-v2-AGORA-VAI.ipynb`. Se precisar versionar, use o Git.

### ❺ Política de dados (LGPD)

- `data/raw/` **nunca** é versionado (já está no `.gitignore`). Documente a URL e
  o *hash* do arquivo em `docs/dicionario-de-dados.md`.
- Nenhum dado pessoal identificável (nome, CPF, CNS, endereço, telefone, e-mail,
  `id` que permita reidentificação) no repositório.
- Arquivos acima de **20 MB** são rejeitados pela CI e pelo hook.
- Declare a licença do dataset e a base legal de uso no `README.md`.

### ❻ Sementes e reprodutibilidade

Toda execução precisa ser determinística: `SEED` em `configs/base.yaml` e
propagado para `random`, `numpy` e `random_state` dos estimadores. Resultado sem
semente não é resultado, é anedota.

---

## 2. Fluxo Passo a Passo

### 1. Fork, clone e hook

```bash
# no GitHub: Fork no repositório do professor
git clone https://github.com/SEU_USUARIO/ml_projeto_av2_facape.git
cd ml_projeto_av2_facape
git remote add upstream https://github.com/mateusamorim96/ml_projeto_av2_facape.git
git fetch upstream
git config core.hooksPath .githooks    # ativa o bloqueio de escopo no commit
```

### 2. Crie a pasta do grupo (uma única vez)

```bash
python3 scripts/novo_grupo.py --numero 3 --tema saneamento-ana
```

O script copia `grupos/_template/` para `grupos/grupo-03-saneamento-ana/`,
substitui os marcadores `grupo-XX`/`GXX` e **recusa** número já ocupado.

### 3. Crie a branch de trabalho

```bash
git checkout -b grupo-03/pipeline-preparacao
```

Padrão: `grupo-NN/descricao-curta`.

### 4. Trabalhe na sua pasta e valide localmente

```bash
python3 scripts/check_entrega.py --grupo grupo-03 --entrega E4
```

O validador confere escopo, estrutura mínima da entrega, nomes, dados, segredos,
`requirements.txt` pinado, `Dockerfile`, README executivo e placeholders.

### 5. Commit e push

```bash
git add grupos/grupo-03-saneamento-ana
git commit -m "[G03] feat: adiciona pipeline de preparacao de dados"
git push origin grupo-03/pipeline-preparacao
```

### 6. Abra o Pull Request

- **Base:** repositório do professor, branch `main`
- **Head:** seu fork, branch `grupo-03/descricao-curta`
- **Título:** `[G03] Entrega E4 — Saneamento e perda de água (ODS 6)`
- Preencha o `PULL_REQUEST_TEMPLATE` **completo** (inclusive decisões, limitações e uso de IA)

### 7. Aguarde a CI e a revisão

| Erro da CI | Causa | Correção |
| ---------- | ----- | -------- |
| `arquivo alterado FORA da pasta do grupo` | editou `docs/`, `README.md` ou a pasta de outro grupo | remova do PR (`git checkout upstream/main -- <arquivo>`) |
| `pasta do grupo fora do padrao` | nome com maiúscula, espaço ou acento | renomeie com `git mv` para `grupo-NN-slug` |
| `numero de grupo duplicado` | dois `grupo-03-*` | combine com o professor qual grupo mantém o número |
| `arquivo grande` | `> 20 MB` versionado | remova do histórico (`git rm --cached`) e adicione ao `.gitignore` |
| `dados brutos versionados` | arquivo em `data/raw/` | `git rm --cached -r data/raw` |
| `requirements sem versao fixa` | `scikit-learn` em vez de `scikit-learn==1.5.2` | fixe todas as versões |
| `Dockerfile sem tag fixa` | `FROM python:3.11` ou `:latest` | use tag/digest fixo |
| `placeholder` | texto `preencher`/`TODO` em `.md` | substitua pelo conteúdo real |

---

## 3. Resolução de Conflitos

Como cada grupo trabalha em pasta isolada, conflitos de conteúdo praticamente não
existem. Eles aparecem apenas em três situações:

1. **Fork desatualizado.** Sempre rebase antes de abrir o PR:

   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Pasta duplicada** (dois grupos com o mesmo `NN`). Não resolva no Git:
   alinhe o número com o professor e renomeie **antes** do merge.

3. **`README.md` da raiz ou `docs/`** — não edite. Abra uma issue.

Regra prática: **se o Git pediu merge manual em arquivo fora da sua pasta, você
está fazendo algo errado.**

---

## 4. Definição de Pronto (para abrir o PR)

- [ ] Pasta no padrão `grupos/grupo-NN-slug`
- [ ] `python3 scripts/check_entrega.py --grupo grupo-NN --entrega EN` sem ERRO
- [ ] Nenhum arquivo alterado fora da pasta do grupo
- [ ] `README.md` do grupo com ODS, decisão, dados, resultados e “como reproduzir”
- [ ] Commits no padrão `[GNN] tipo: descricao`, com todos os integrantes
- [ ] Sem dados brutos, sem credenciais, sem arquivo > 20 MB
