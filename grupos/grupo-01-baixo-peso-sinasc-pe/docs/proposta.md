# Proposta do Projeto — G01 · Risco de baixo peso ao nascer em Pernambuco

Entrega E1 · trabalho individual (Luiz Eduardo, 22770) · números atualizados com a auditoria da E2

## 1. ODS e meta

- **ODS 3, meta 3.2:** acabar com as mortes evitáveis de recém-nascidos. O baixo peso ao nascer (< 2.500 g)
  é um dos principais determinantes da mortalidade neonatal e pode ser antecipado no pré-natal.
- **Relevância local:** em 2024, 8,71% dos nascidos vivos de mães residentes em Pernambuco tiveram baixo
  peso; em **Petrolina**, 9,48%. Petrolina ficou acima da média do estado em todos os anos de 2015 a 2024
  (SINASC; `docs/dicionario-de-dados.md`).

## 2. Problema

A gestante com risco de ter um bebê de baixo peso só é identificada pela avaliação clínica de cada equipe
da Estratégia Saúde da Família (ESF), que tem pouco tempo para consultas extras. O SINASC acumula anos de
nascimentos do território, mas esse histórico não é usado para priorizar o acompanhamento.
**Fora do escopo:** prever o peso exato, diagnosticar condições clínicas, prever prematuridade ou óbito, usar
exames ou prontuário, e uso clínico real (o estudo é retrospectivo). Também ficam fora as gestações múltiplas,
já reconhecidas como de risco sem modelo, e as gestantes sem pré-natal, que a decisão não alcança.

## 3. Pergunta de ML

Em gestações únicas, com o que se sabe na captação (perfil da mãe, histórico obstétrico, mês de início do
pré-natal e região), é possível identificar quem terá um bebê com menos de 2.500 g melhor do que o preditor
trivial, sem queda relevante de recall entre os subgrupos de raça/cor, idade e região?
**Hipótese falsificável:** o melhor modelo tem PR-AUC, em CV repetida, com IC 95% inteiramente acima de
0,070 (a prevalência na população de desenvolvimento, que é a PR-AUC do baseline). Se o IC incluir 0,070, a
hipótese é rejeitada.

## 4. Decisão

> “Se o modelo indicar **risco ≥ c** (limiar escolhido na validação para recall ≥ 0,70), a **equipe de ESF da
> UBS de referência** fará **consulta extra e avaliação nutricional em até 7 dias**.”

- **Quem e quando:** enfermeira(o) ou médica(o) do pré-natal, na captação da gestante.
- **Falso positivo:** uma consulta extra desnecessária. Custo baixo.
- **Falso negativo:** a gestante de risco fica no fluxo padrão e a janela para intervir se perde. Custo alto.
- **Sem o modelo:** a priorização depende só da avaliação clínica de cada equipe.

## 5. Formulação técnica

- **Tipo:** supervisionado, classificação binária desbalanceada. A unidade de análise é o nascido vivo.
- **População:** gestações únicas com mês de início do pré-natal registrado (quem passa pela captação).
- **Alvo:** `baixo_peso = 1` se `PESO < 2500` g (6,96% na população de desenvolvimento).
- **Métrica principal:** **PR-AUC**. Um modelo que sempre responde “não” já passaria de 93% de acurácia sem
  achar nenhum caso. **Secundárias:** recall e precisão no limiar, AUC-ROC, Brier e recall por subgrupo.

## 6. Dados

- **Fonte:** SINASC, Ministério da Saúde/DATASUS (`DNPE{ano}.dbc`), com dicionário oficial. Licença CC BY-ND
  3.0 do portal; a base não é redistribuída. Análise na E2.
- **Recorte:** Pernambuco. Desenvolvimento em 2019–2023 (585.522 registros na população) e **teste temporal
  em 2024** (104.919), usado uma única vez no final.
- **LGPD:** a base é pública e anonimizada. Datas, hora, estabelecimento e naturalidade são removidos.
- **Plano B:** acesso pelo OpenDataSUS se o FTP falhar; tema reserva: hospitalização por dengue (SINAN, ODS 3.3).

## 7. Riscos e plano de contingência

| Risco | Prob. | Impacto | Mitigação |
| ----- | ----- | ------- | --------- |
| base indisponível | baixa | alto | download por script com SHA-256 registrado |
| alvo mal definido | baixa | médio | critério da OMS; pesos fora de 300–6.500 g excluídos |
| desbalanceamento | certa | médio | PR-AUC; `class_weight` ou limiar ajustado dentro da CV |
| vazamento | alta | alto | só variáveis da captação: saem dados do parto, nº de consultas e sexo do bebê (lista em `src/data/esquema.py`); gêmeos fora da população, para não vazar entre folds |
| viés entre subgrupos | média | alto | métricas por raça/cor, idade e região (E5) |
| mudança de distribuição | média | médio | teste temporal em 2024; desempenho por ano |
| reidentificação (LGPD) | baixa | alto | remover datas, hora e estabelecimento; município agregado por região; nenhuma célula publicada com menos de 10 registros |

## 8. O que faria mudar de rumo

- Licença incompatível com a publicação de resultados (pergunta na issue #1): trocar para o tema reserva.
- Nenhum modelo acima do baseline com IC 95%: reportar como resultado e focar em quais fatores explicam o
  risco.
- Recall muito menor em algum subgrupo: recomendar **não** usar o modelo e discutir a causa.

**Uso inadequado:** o modelo não deve ser usado para negar, adiar ou reduzir atendimento a nenhuma gestante.
Ele serve só para **priorizar** acompanhamento extra.
