"""Limpeza e recorte (E3): do registro bruto ao conjunto de modelagem.

Tudo aqui e regra deterministica por registro -- nenhuma estatistica e
calculada sobre os dados (sem media, mediana, moda ou frequencia). Por isso
pode rodar antes do split sem vazamento. Imputacao, padronizacao e codificacao
ficam no `Pipeline` (src/features/preprocessamento.py), ajustadas so no treino.

Regras (justificativa em docs/decisoes-tecnicas.md e no dicionario de dados):
  1. remove duplicatas exatas (fora as colunas internas do sistema);
  2. aplica a populacao do modelo (src/data/populacao.py);
  3. cria o alvo `baixo_peso` (PESO < limiar);
  4. mantem so os atributos conhecidos na captacao (src/data/esquema.py);
  5. codigos de "ignorado" e valores implausiveis viram ausentes (<NA>).
"""
from __future__ import annotations

import pandas as pd

from src.data.esquema import ATRIBUTOS, POR_NOME
from src.data.populacao import mascara_populacao, peso_numerico

INTERNAS = ("CONTADOR", "NUMEROLOTE", "DTCADASTRO", "DTRECEBIM", "DTRECORIGA", "DIFDATA",
            "VERSAOSIST", "ORIGEM", "STDNEPIDEM", "STDNNOVA", "CODPAISRES")
IDADE_PLAUSIVEL = (10, 55)   # anos; fora disso, tratado como erro de digitacao
HISTORICO_MAXIMO = 20        # contagens obstetricas acima disso sao tratadas como erro
HISTORICO = ("QTDGESTANT", "QTDPARTNOR", "QTDPARTCES", "QTDFILVIVO", "QTDFILMORT")


def remover_duplicatas(df: pd.DataFrame) -> pd.DataFrame:
    chave = [c for c in df.columns if c not in INTERNAS]
    return df.loc[~df.duplicated(subset=chave)]


def limpar_atributos(df: pd.DataFrame) -> pd.DataFrame:
    """Converte tipos e troca 'ignorado' e implausiveis por <NA>."""
    saida = pd.DataFrame(index=df.index)
    for nome in ATRIBUTOS:
        coluna = POR_NOME[nome]
        serie = df[nome].astype("string")
        if coluna.ignorado:
            serie = serie.mask(serie.isin(coluna.ignorado))
        if coluna.tipo == "numerica":
            numeros = pd.to_numeric(serie, errors="coerce").astype("Float64")
            if nome == "IDADEMAE":
                numeros = numeros.where(numeros.between(*IDADE_PLAUSIVEL))
            elif nome in HISTORICO:
                numeros = numeros.where(numeros <= HISTORICO_MAXIMO)
            saida[nome] = numeros
        else:
            saida[nome] = serie
    return saida


def preparar(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Registro bruto -> conjunto de modelagem (ANO, atributos limpos e alvo)."""
    df = remover_duplicatas(df)
    df = df.loc[mascara_populacao(df, cfg)]
    preparado = limpar_atributos(df)
    preparado.insert(0, "ANO", df["ANO"].astype(int))
    preparado[cfg["dados"]["alvo"]] = (peso_numerico(df) < cfg["dados"]["limiar_peso_g"]).astype(int)
    return preparado.reset_index(drop=True)


def separar(preparado: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split temporal: desenvolvimento (treino + CV) e teste (uso unico, no fim)."""
    dev = preparado.loc[preparado["ANO"].isin(cfg["dados"]["anos_desenvolvimento"])].reset_index(drop=True)
    teste = preparado.loc[preparado["ANO"] == cfg["dados"]["ano_teste"]].reset_index(drop=True)
    return dev, teste
