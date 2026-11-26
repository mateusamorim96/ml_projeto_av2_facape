# Proposta do Projeto - G08
Entrega E1 · Projeto Integrador de Machine Learning (FACAPE 2026.2)

## 1. ODS e meta

- **ODS:** ODS 7 - Energia Limpa e Acessível (com impacto complementar na ODS 2 - Fome Zero e Agricultura Sustentável)
- **Meta:** 7.2 - Aumentar a participação de energias renováveis na matriz energética até 2030 (relacionada também à Meta 2.4 de produção agrícola sustentável)
- **Por que essa meta:** Usar energia solar para bombear água na agricultura reduz o custo com energia elétrica e a dependência da rede convencional. Como a geração fotovoltaica varia ao longo do dia conforme a passagem de nuvens e a temperatura, prever essa disponibilidade ajuda o produtor a usar o sistema solar de forma mais estável.
- **Relevância local:** No Vale do São Francisco (com foco em Petrolina e Santa Maria da Boa Vista - PE), a fruticultura irrigada tem alta demanda diária de água e forte incidência solar ao longo do ano inteiro. O trabalho usa como referência uma área de 1 hectare de banana Pacovan irrigada por gotejamento com sistema solar *off-grid* de 4,4 kWp e sem banco de baterias.

## 2. Problema

Em propriedades rurais do Vale do São Francisco que usam energia solar isolada da rede (*off-grid*) e sem baterias, a bomba de irrigação depende diretamente da potência gerada pelos painéis naquele momento. No sistema tomado como referência (1 ha de banana Pacovan, gotejamento com vazão nominal de 5.000 L/h, motobomba trifásica de 2 cv em 220/380 V, 8 painéis de 550 W somando 4,4 kWp e inversor de 4,4 kW), o produtor decide ligar ou desligar a irrigação observando o tempo na hora, sem uma estimativa prévia de geração. Se entram nuvens carregadas no meio do turno da manhã ou da tarde, a potência cai e a bomba pode desarmar. Já existem séries históricas públicas de clima e geração solar para a região, mas esses dados não são usados no planejamento diário da rega. Alguns dados específicos da propriedade (placa completa do motor, modelo do inversor, o que o medidor registra e horários exatos da bomba) ainda estão sendo levantados em campo e ficam sinalizados como pendências.

## 3. Pergunta de ML

É possível prever a potência ativa e a energia horária disponível para um sistema fotovoltaico de 4,4 kWp no Vale do São Francisco, usando dados meteorológicos históricos e valores passados da própria geração, com Erro Absoluto Médio (MAE) menor que o baseline de persistência ($p < 0,05$)?

## 4. Decisão

> “Se o modelo indicar potência solar prevista acima do consumo mínimo exigido pela motobomba (estimado inicialmente a partir dos 1,47 kW mecânicos do motor de 2 cv corrigidos pelo rendimento, a ser confirmado na medição de campo) com intervalo de confiança de 95% acima desse patamar, o produtor ou operador da irrigação acionará o setor de gotejamento no turno seguinte em até 1 hora.”

- **Quem decide:** Produtor rural ou operador responsável pelo manejo da irrigação.
- **Quando decide:** Antes e durante os turnos de irrigação (manhã e tarde), em intervalos horários.
- **Custo do falso positivo:** O modelo prevê energia suficiente, o operador liga a bomba sem baterias de apoio e a queda de potência desarma o inversor ou interrompe a irrigação no meio do turno.
- **Custo do falso negativo:** O modelo prevê energia insuficiente quando haveria geração disponível, fazendo o produtor adiar a rega sem necessidade e desperdiçar energia solar.
- **Consequência de não usar o modelo:** Continuar operando no modo manual e reativo atual, sem conseguir antecipar quedas de geração por nebulosidade.

## 5. Formulação técnica

- **Tipo de aprendizado:** Supervisionado - regressão em série temporal, com divisão estritamente cronológica entre treino, validação e teste (`TimeSeriesSplit`), sem embaralhar os dados.
- **Unidade de análise:** Registro horário da série de geração fotovoltaica e clima.
- **Variável-alvo:** Fator de capacidade solar ($FC_t \in [0, 1]$) convertido para a potência ativa / energia horária equivalente do arranjo de 4,4 kWp ($\hat{P}_t = FC_t \times 4,4\text{ kW}$, em kW / kWh).
- **Métrica principal:** MAE (Erro Absoluto Médio, em kW / kWh), escolhida por mostrar o erro médio direto na mesma unidade física da decisão e não sofrer distorção exagerada com picos isolados.
- **Métricas secundárias:** RMSE (para penalizar erros maiores em mudanças bruscas de nuvens) e $R^2$.

## 6. Dados previstos

- **Fonte:** NASA POWER API (`https://power.larc.nasa.gov/api/temporal/hourly/point`, coordenadas de Santa Maria da Boa Vista/PE: `-8.807, -39.825`) cruzada com os registros horários públicos de geração solar do ONS Dados Abertos (`https://dados.ons.org.br/dataset/geracao-usina-2`, Subsistema Nordeste), com opção de complementar usando o dataset BR-PVGen.
- **Licença:** Domínio público governamental (NASA) e licença aberta CC-BY / Dados Abertos (ONS), permitindo uso acadêmico e reprodução.
- **Volume esperado:** Cerca de 35.040 registros horários (2022 a 2025) $\times$ 16 variáveis meteorológicas, de irradiância e temporais (acima do mínimo de 5.000 registros).
- **Risco de LGPD:** Nenhum. Os arquivos contêm apenas dados ambientais e geração elétrica agregada por usina, sem qualquer dado pessoal.
- **Plano B:** Se alguma API ficar fora do ar na E2, usar os dados históricos das estações do INMET (Petrolina/PE) ou a base pública BR-PVGen.

## 7. Riscos e plano de contingência

| Risco | Probabilidade | Impacto | Mitigação |
| ----- | ------------- | ------- | --------- |
| base indisponível | Baixa | Alto | Configurar tentativas automáticas no script de download e manter opção de carga via BR-PVGen ou INMET. |
| alvo mal definido | Média | Alto | Calcular o fator de capacidade apenas com estatísticas do treino, escalonar para 4,4 kWp e deixar claro no texto que geração estimada não é o consumo medido na bomba. |
| desbalanceamento severo | Baixa | Médio | Como o período noturno tem geração zero e puxa o erro médio para baixo, filtrar a janela diurna ativa e avaliar o erro por faixa de irradiância. |
| vazamento temporal | Média | Alto | Separar treino e teste por data, criar *lags* só com horários passados ($t-1, t-2, t-24$) e ajustar transformações dentro do `Pipeline` apenas no treino. |

## 8. O que faria o grupo mudar de rumo

- Se a série horária do ONS tiver muitas falhas entre 2022 e 2025 na E2, passamos a usar o BR-PVGen (15 minutos) junto com a NASA POWER como base principal.
- Se conseguirmos coletar a placa do motor, o modelo do inversor e os registros reais do medidor da propriedade a tempo, incluímos uma validação comparando as previsões com os dados medidos no local.
- Se os erros forem muito assimétricos em dias parcialmente nublados, adicionamos regressão quantílica para estimar direto o limite inferior de segurança da potência.