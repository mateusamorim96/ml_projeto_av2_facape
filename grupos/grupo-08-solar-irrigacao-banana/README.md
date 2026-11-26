# G08 - Previsão de Geração Solar para Irrigação de Banana Pacovan no Vale do São Francisco

> Projeto AV2 de Machine Learning · FACAPE 2026.2
> Pasta: `grupos/grupo-08-solar-irrigacao-banana` · Entrega atual: E1

## Integrantes

| Nome | Matrícula | Papel |
| ---- | --------- | ----- |
| André Medrado Freire | 26726 | dados e pipeline |
| Lázaro Emanoel da Silva de Souza | 25490 | modelagem |
| Juan Glauber Oliveira Porto | 25128 | avaliação e estatística |
| Alessandro Galvão do Nascimento Filho | 25786 | artigo, Docker e apresentação |

---

## 1. ODS, meta e problema

- **ODS:** ODS 7 - Energia Limpa e Acessível (com relação direta com a ODS 2 - Fome Zero e Agricultura Sustentável)
- **Meta:** 7.2 - Aumentar a participação de energias renováveis na matriz energética até 2030 (relacionada à Meta 2.4 de produção agrícola sustentável)
- **Problema:** Em áreas irrigadas do Vale do São Francisco (com referência em Petrolina e Santa Maria da Boa Vista - PE) que usam energia solar *off-grid* sem baterias, a bomba d'água depende direto da potência que os painéis geram naquele horário. No sistema usado como base (1 ha de banana Pacovan, gotejamento de 5.000 L/h, motobomba trifásica de 2 cv em 220/380 V, 8 placas de 550 W somando 4,4 kWp e inversor de 4,4 kW), o produtor liga a irrigação olhando o tempo na hora. Quando entram nuvens e a potência cai de repente, o inversor pode desarmar e interromper a rega.
- **Público/beneficiário:** Produtores rurais e operadores responsáveis pelo manejo de irrigação no Vale do São Francisco.

## 2. Decisão

> “Se o modelo prever potência solar acima do consumo elétrico mínimo da motobomba (estimado inicialmente a partir dos 1,47 kW mecânicos do motor de 2 cv ajustados pelo rendimento, valor que será confirmado na medição de campo) e o intervalo de confiança de 95% também ficar acima desse limite, o operador acionará o setor de gotejamento no turno seguinte, em até 1 hora.”

- **Custo do falso positivo:** Ligar a bomba sem baterias quando a geração real não aguenta a carga, causando queda de tensão, desarme do inversor e parada na irrigação.
- **Custo do falso negativo:** Deixar de irrigar num horário em que havia sol e potência suficientes, perdendo janela útil de bombeamento.
- **Métrica principal:** MAE (Erro Absoluto Médio, em kW / kWh), porque mostra o erro direto na mesma unidade usada para decidir se a bomba liga ou não, sem ser tão puxado por picos isolados. Como apoio, usamos RMSE e $R^2$.

## 3. Dados e licença

- **Fonte:** NASA POWER (`https://power.larc.nasa.gov/api/temporal/hourly/point`, ponto em Santa Maria da Boa Vista/PE) cruzada com os dados horários de geração solar do ONS Dados Abertos (`https://dados.ons.org.br/dataset/geracao-usina-2`, Subsistema Nordeste), com opção de complementar usando a base BR-PVGen.
- **Data de acesso:** Será registrada automaticamente pelo script `src/data/download.py` no arquivo `data/raw/manifest.json` (com URL, data UTC e hash SHA-256) na entrega E2.
- **Licença:** Domínio público (NASA) e licença aberta CC-BY / Dados Abertos (ONS).
- **Volume:** Cerca de 35.040 registros horários (de 2022 a 2025) $\times$ 16 colunas entre variáveis climáticas, irradiância e marcações de tempo (a consolidar na E2).
- **Alvo:** Fator de capacidade solar ($FC_t \in [0, 1]$) convertido para a potência/energia horária equivalente de um arranjo de 4,4 kWp ($\hat{P}_t = FC_t \times 4,4\text{ kW}$).
- Detalhes em [`docs/dicionario-de-dados.md`](docs/dicionario-de-dados.md).

## 4. Como reproduzir

```bash
# 1. ambiente local
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# 2. pipeline completo
python -m src.pipeline --config configs/base.yaml

# 3. ou via Docker (ambiente limpo)
docker build -t grupo-08-solar-irrigacao-banana .
docker run --rm grupo-08-solar-irrigacao-banana
```

- **Tempo estimado de execução:** Cerca de 3 a 6 minutos em CPU comum de 4 núcleos (a confirmar após rodar o pipeline completo)
- **Saídas:** `reports/tables/`, `reports/figures/`, `reports/environment.json`

## 5. Resultados principais

| Modelo | Métrica MAE (média ± desvio) | IC 95% | p-valor vs baseline |
| ------ | ---------------------------- | ------ | ------------------- |
| Persistência (baseline) | Previsto na E3 | — | — |
| Regressão Linear / Ridge | Previsto na E3 | — | — |
| Random Forest Regressor | Previsto na E3 | — | — |
| HistGradientBoostingRegressor | Previsto na E3 | — | — |

Figuras: Serão salvas em `reports/figures/` nas entregas E2 (análise exploratória) e E3/E4 (comparação de modelos e análise de erros).

## 6. Limitações

- Os dados públicos usados vêm de usinas solares do Nordeste (ONS) e de satélite (NASA POWER), não de um medidor instalado direto no inversor da propriedade.
- Dados específicos do equipamento local (placa completa do motor de 2 cv, modelo exato do inversor, o que o medidor registra e horários exatos da bomba) ainda estão sendo conferidos em campo.
- O modelo serve apenas como apoio ao planejamento dos turnos de rega; ele não substitui a avaliação de um eletricista ou engenheiro nem liga a bomba sozinho.

## 7. Uso responsável

- **Não usar para:** Acionar motores ou bombas automaticamente sem supervisão humana, nem calcular sozinho a necessidade de água da lavoura.
- **Dados pessoais:** Nenhum. A base reúne apenas registros climáticos e geração elétrica agregada por usina, sem dados pessoais (de acordo com a LGPD).
- **Desempenho por subgrupo:** Na E4 vamos separar os erros por turno do dia (manhã e tarde) e por períodos mais secos ou mais nublados da região.
- **Uso de IA generativa:** Usamos IA para revisar a redação e organizar a estrutura inicial dos arquivos de documentação e código; cada parte foi conferida, ajustada e testada pelos integrantes do grupo.

---

## Estrutura desta pasta


grupo-08-solar-irrigacao-banana/
├── README.md               ← este arquivo
├── configs/base.yaml       ← seed, caminhos, folds, hiperparâmetros
├── data/raw/               ← NÃO versionado
├── src/                    ← data, features, models, evaluation, pipeline
├── notebooks/              ← EDA e experimentos
├── experiments/runs.csv    ← log de execuções
├── reports/                ← tabelas e figuras geradas
├── article/                ← artigo IMRaD
├── slides/                 ← apresentação
└── docs/                   ← proposta, dicionário, decisões técnicas
