# Proposta do Projeto — G07 · Acidentes graves nas rodovias federais de Pernambuco

Entrega E1 · integrante: João Matheus Ribeiro Soares (grupo individual)

## 1. ODS e meta

- **ODS:** 3 — Saúde e Bem-Estar
- **Meta:** 3.6 — reduzir pela metade as mortes e os ferimentos globais por acidentes em estradas.
- **Por que essa meta:** acidentes de trânsito estão entre as principais causas de morte de jovens adultos no Brasil e geram custos altos para o SUS, para a previdência e para as famílias. A Polícia Rodoviária Federal (PRF) registra cada acidente atendido nas rodovias federais com informações de local, horário, clima e via, mas esses registros são usados sobretudo para estatística descritiva, e não para antecipar onde a gravidade tende a ser maior.
- **Relevância local:** o sertão de Pernambuco é cortado por rodovias federais de tráfego pesado e longas distâncias entre cidades, como a BR-407, a BR-428, a BR-232 e a BR-116, que ligam Petrolina ao restante do estado e ao Nordeste. Nesses trechos, o socorro costuma demorar mais, o que aumenta o peso de cada acidente grave. A quantificação local do problema (número de acidentes graves por trecho e ano) será feita na E2 com os próprios dados da PRF.

## 2. Problema

Quem sofre o problema são os motoristas, passageiros e pedestres envolvidos em acidentes nas rodovias federais de Pernambuco, e as equipes de resgate e saúde que atendem as ocorrências. Hoje, a distribuição de fiscalização e de ações educativas da PRF depende de levantamentos históricos de quantidade de acidentes e da experiência das equipes. Contar acidentes, porém, não é o mesmo que medir risco de gravidade: um trecho com muitas colisões leves pode receber mais atenção do que um trecho com poucos acidentes, mas quase sempre graves. A informação para separar esses casos já existe nos dados abertos da PRF (horário, dia da semana, condição meteorológica, tipo e traçado da pista, uso do solo, localização), mas não é usada para estimar a probabilidade de um acidente terminar com mortos ou feridos graves.

**Escopo:** acidentes registrados pela PRF em rodovias federais no estado de Pernambuco.

**Fora do escopo:** prever *quantos* acidentes vão acontecer (frequência), rodovias estaduais e municipais (não estão na base da PRF), dados de pessoas envolvidas (idade, sexo) e qualquer aplicação em produção ou com usuários reais.

## 3. Pergunta de ML

É possível estimar, usando apenas informações de contexto conhecidas antes do acidente (local, horário, dia da semana, condição meteorológica e características da via), a probabilidade de um acidente registrado pela PRF em rodovias federais de Pernambuco resultar em vítima fatal ou ferido grave, com desempenho superior a um classificador de referência (baseline) medido por AUC-PR em validação cruzada repetida?

## 4. Decisão

> “Se o modelo indicar risco ≥ c (limiar escolhido para garantir recall ≥ 0,70 na validação) para um trecho de rodovia em determinada faixa de horário, a PRF incluirá esse trecho e horário como prioritários na escala de fiscalização do mês seguinte.”

- **Quem decide:** a coordenação operacional da PRF em Pernambuco (delegacias e Unidades Operacionais responsáveis pelos trechos).
- **Quando decide:** na montagem da escala mensal de fiscalização e no planejamento de operações sazonais (feriados, festas juninas, período de chuvas).
- **Custo do falso positivo:** uma equipe é deslocada para um trecho e horário que não tinham risco elevado, desperdiçando horas de efetivo que poderiam estar em outro ponto.
- **Custo do falso negativo:** um trecho de risco alto fica sem reforço; o custo potencial é uma morte ou lesão grave que a presença da fiscalização poderia ter ajudado a evitar. Por isso, este é o erro mais caro.
- **Consequência de não usar o modelo:** a priorização continua baseada na contagem histórica de acidentes, que mistura ocorrências leves e graves e não considera a combinação de horário, clima e características da via.

**Público e beneficiários:** usuários das rodovias federais de Pernambuco (beneficiários finais), equipes da PRF (usuárias da priorização) e serviços de resgate e saúde da região.

## 5. Formulação técnica

- **Tipo de aprendizado:** supervisionado, classificação binária.
- **Unidade de análise:** a ocorrência (um acidente registrado pela PRF).
- **Variável-alvo:** `acidente_grave` = 1 se o acidente teve pelo menos um morto ou um ferido grave; 0 caso contrário (apenas feridos leves, ilesos ou sem vítimas). A definição será construída a partir das colunas de contagem de vítimas, e **essas colunas não serão usadas como atributos**, assim como a própria classificação de gravidade da PRF, para evitar vazamento do alvo.
- **Atributos previstos:** horário e fase do dia, dia da semana, mês, rodovia (BR) e quilômetro, município, condição meteorológica, tipo de pista, traçado da via, sentido da via e uso do solo. Causa e tipo do acidente só são conhecidos depois da ocorrência e não ajudam a decidir onde fiscalizar, então ficam de fora do modelo principal.
- **Métrica principal:** AUC-PR (área sob a curva precisão-recall). A classe positiva (acidente grave) é minoritária, e o erro mais caro é deixar passar um caso grave; a acurácia seria enganosa, porque um modelo que sempre responde "não grave" já acerta a maioria dos casos.
- **Métricas secundárias:** recall da classe grave no limiar de operação (meta: recall ≥ 0,70, com a maior precisão possível), F1 e ROC-AUC.

## 6. Dados previstos

- **Fonte:** Polícia Rodoviária Federal — Dados Abertos, “Acidentes — agrupados por ocorrência” (datatran), disponíveis no portal de dados abertos da PRF e no Portal Brasileiro de Dados Abertos (dados.gov.br).
- **Licença:** dados abertos governamentais publicados pela PRF; a licença exata será registrada com link na E2.
- **Volume esperado:** um arquivo anual por ocorrência, com cerca de 30 colunas. O recorte de Pernambuco em vários anos (ex.: 2017–2025) deve superar com folga o mínimo de 5.000 registros; o número exato de registros e atributos será confirmado na E2.
- **Risco de LGPD:** baixo. A base agrupada por ocorrência não traz nome, CPF ou placa dos envolvidos. Os identificadores de ocorrência não permitem reidentificar pessoas e não serão usados como atributo. A base por pessoa (com idade e sexo) não será usada.
- **Plano B:** ampliar o recorte para toda a região Nordeste, caso o volume de Pernambuco fique abaixo do necessário ou a classe grave fique rara demais. Como alternativa de tema na mesma meta, usar os óbitos por acidentes de transporte do SIM/DATASUS agregados por município.

## 7. Riscos e plano de contingência

| Risco | Probabilidade | Impacto | Mitigação |
| ----- | ------------- | ------- | --------- |
| base indisponível | baixa | alto | baixar os anos do recorte logo no início, registrar URL e hash; usar a cópia do dados.gov.br se o portal da PRF sair do ar |
| alvo mal definido | média | alto | definir o alvo só pelas contagens de vítimas e excluir do modelo todas as colunas derivadas delas (mortos, feridos, classificação de gravidade) |
| desbalanceamento severo | média | médio | medir a proporção na E2; usar AUC-PR, pesos de classe e ajuste do limiar de decisão em vez de acurácia |
| vazamento temporal | média | médio | validar também com divisão por ano (treinar em anos anteriores e testar no ano mais recente) e manter o pré-processamento inteiro dentro do pipeline |
| mudança de padrão de registro entre anos | média | médio | conferir categorias e nomes de colunas ano a ano na E2 e padronizar antes de juntar |
| viés de registro | média | médio | a base só contém acidentes atendidos pela PRF; registrar essa limitação e não generalizar para rodovias estaduais |

## 8. O que faria o grupo mudar de rumo

- Se, na E2, o recorte de Pernambuco tiver menos de 5.000 acidentes, o recorte passa a ser o Nordeste.
- Se a proporção de acidentes graves ficar abaixo de cerca de 5%, a pergunta passa a priorizar recall em alerta e o limiar de decisão é revisto.
- Se, na E4, nenhum modelo superar o baseline em AUC-PR de forma consistente, a pergunta muda para uma análise de risco agregada por trecho e faixa de horário.
- Se a licença dos dados não permitir publicação dos resultados, a base é trocada pelo plano B.
