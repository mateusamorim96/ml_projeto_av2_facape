# Dicionário de Dados — GXX (preencher)

> Entrega E2. Este arquivo é a auditoria do dataset: quem responde “de onde veio,
> o que significa cada coluna, e o que não podemos usar”.

## 1. Identificação

| Campo | Valor |
| ----- | ----- |
| Fonte | preencher (instituição) |
| URL | preencher |
| Documentação | preencher (dicionário oficial / nota técnica / artigo) |
| Data de acesso | preencher (AAAA-MM-DD) |
| Recorte | preencher (ano, UF, filtros) |
| Licença | preencher (nome + link) |
| Base legal (LGPD) | preencher |
| Hash do arquivo | `sha256:` preencher |
| Registros | preencher |
| Atributos | preencher |
| Arquivo versionado? | não — `data/raw/` é ignorado |

## 2. Critério “não-toy”

| Critério | Situação | Evidência |
| -------- | -------- | --------- |
| (a) proveniência documentada | preencher | |
| (b) ≥ 5.000 registros / ≥ 40 atributos / não tabular | preencher | |
| (c) alvo não trivial | preencher | |
| (d) licença compatível | preencher | |

## 3. Variáveis

| Coluna | Tipo | Unidade | Faixa | % nulos | Descrição | Uso |
| ------ | ---- | ------- | ----- | ------- | --------- | --- |
| preencher | | | | | | atributo / alvo / descartada |

> Toda coluna descartada precisa de motivo (identificador, vazamento, > 60% nulo,
> dado pessoal, constante).

## 4. Variável-alvo

- **Nome:** preencher
- **Definição operacional:** preencher (como o valor é obtido)
- **Distribuição:** preencher (proporção das classes ou faixa da variável)
- **Por que não é trivial:** preencher (não é cópia de coluna, não é regra determinística)

## 5. Qualidade e riscos

| Item verificado | Resultado | Ação |
| --------------- | --------- | ---- |
| duplicatas | | |
| nulos | | |
| valores fora de faixa | | |
| inconsistência temporal | | |
| subnotificação / viés de coleta | | |
| dado pessoal identificável | | |

## 6. LGPD

- Existe dado pessoal? preencher
- Estratégia adotada: preencher (remoção / agregação por município / anonimização)
- Risco de reidentificação: preencher
- Comando de verificação: `sha256sum data/raw/<arquivo>`
