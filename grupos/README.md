# 👥 Pastas dos Grupos — Alocação de Códigos

Cada grupo ocupa **uma pasta** aqui dentro. O número `NN` é um namespace único:
dois grupos nunca podem usar o mesmo número.

---

## Alocação

| Código | Pasta | ODS / meta | Tema | Integrantes | Estado |
| ------ | ----- | ---------- | ---- | ----------- | ------ |
| G01 | `grupo-01-*` | — | a definir | — | livre |
| G02 | `grupo-02-*` | — | a definir | — | livre |
| G03 | `grupo-03-*` | — | a definir | — | livre |
| G04 | `grupo-04-*` | — | a definir | — | livre |
| G05 | `grupo-05-*` | — | a definir | — | livre |
| G06 | `grupo-06-*` | — | a definir | — | livre |
| G07 | `grupo-07-*` | — | a definir | — | livre |
| G08 | `grupo-08-*` | — | a definir | — | livre |
| G09 | `grupo-09-*` | — | a definir | — | livre |
| G10 | `grupo-10-*` | — | a definir | — | livre |
| G11 | `grupo-11-*` | — | a definir | — | livre |
| G12 | `grupo-12-*` | — | a definir | — | livre |

> Esta tabela é mantida **pelo professor**. Não edite aqui: informe o código e a
> ODS na issue “Entrega de Grupo” e o professor atualiza.

---

## Como criar a pasta

```bash
python3 scripts/novo_grupo.py --numero 3 --tema saneamento-ana
```

Resultado: `grupos/grupo-03-saneamento-ana/` com o esqueleto completo.

Regras do nome:

- `grupo-` + **dois dígitos** + `-` + slug em kebab-case;
- minúsculas, sem acento, sem espaço, no máximo ~30 caracteres de slug;
- o slug descreve o **tema**, não o nome dos integrantes;
- nunca renomeie a pasta depois da primeira entrega.

Exemplos válidos: `grupo-01-evasa-escolar-inep`,
`grupo-07-irrigacao-semiariado`, `grupo-12-licitacoes-anomalias`.

---

## Por que numeração (e não o nome do grupo)

O fluxo é **fork + pull request**. Se cada grupo escolhesse livremente o nome da
pasta, dois grupos poderiam criar `grupos/projeto-ml/` e o merge viraria um
conflito de conteúdo — justamente o que este desenho evita.

Com `grupo-NN-slug`:

1. pastas nunca colidem (o número é alocado);
2. a CI identifica o grupo pelo número no título do PR (`[G03] Entrega E4 — ...`);
3. o hook `pre-commit` bloqueia commit fora da pasta do próprio grupo;
4. revisão é possível: dá para ver o histórico de um grupo isolado
   (`git log --oneline -- grupos/grupo-03-*`).

---

## Validação global

```bash
python3 scripts/check_entrega.py --namespace
```

Confere: padrão do nome de todas as pastas, unicidade dos números e presença de
`README.md` em cada uma. Roda na CI a cada PR.
