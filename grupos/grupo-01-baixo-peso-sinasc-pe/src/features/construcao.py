"""Construcao de atributos derivados (sem estado: nada e aprendido dos dados).

Entra no `Pipeline` como `FunctionTransformer`:
  * CODMUNRES  -> MESORREGIAO (tabela do IBGE) e PETROLINA (0/1);
  * CODOCUPMAE -> CBO_GRUPO: grande grupo da CBO 2002 (1o digito) ou, para os
    codigos especiais 9999xx do SINASC, uma categoria por codigo -- o 1o digito
    os misturaria com o grande grupo 9 (manutencao), e o significado de cada
    codigo especial nao consta no dicionario oficial;
  * MESPRENAT e historico obstetrico -> categorias. A relacao com o alvo nao e
    monotonica (figuras 4 e 5 da EDA); as contagens sao limitadas ao teto do
    config (percentil 99 do desenvolvimento), virando "N+".
"""
from __future__ import annotations

import numpy as np
import pandas as pd

HISTORICO = ("QTDGESTANT", "QTDPARTNOR", "QTDPARTCES", "QTDFILVIVO", "QTDFILMORT")
NUMERICAS = ("IDADEMAE",)
CATEGORICAS = ("MESPRENAT", *HISTORICO, "ESCMAE2010", "RACACORMAE", "ESTCIVMAE", "PARIDADE", "CBO_GRUPO",
               "MESORREGIAO")
BINARIAS = ("PETROLINA",)


def contagem_com_teto(valores: pd.Series, teto: int) -> pd.Series:
    """0, 1, ..., teto-1 e 'teto+' como texto; ausente continua ausente."""
    numeros = pd.to_numeric(valores, errors="coerce")
    rotulo = numeros.clip(upper=teto).astype("Int64").astype("string")
    # fillna(False): sem isso, ausente >= teto da <NA> e o mask o trataria como "teto+"
    rotulo = rotulo.mask((numeros >= teto).fillna(False), f"{teto}+")
    if int(rotulo.isna().sum()) != int(numeros.isna().sum()):
        raise ValueError("contagem_com_teto alterou a quantidade de ausentes")
    return rotulo


def grupo_cbo(codigo: pd.Series) -> pd.Series:
    codigo = codigo.astype("string")
    especial = codigo.str.startswith("9999", na=False)
    grupo = ("grupo-" + codigo.str[0]).where(codigo.str.len() == 6)
    return grupo.mask(especial, "especial-" + codigo)


def construir_atributos(df: pd.DataFrame, mesorregioes: dict[str, str], municipio_local: str,
                        tetos: dict[str, int]) -> pd.DataFrame:
    """Recebe o conjunto preparado e devolve as colunas que o pre-processamento usa.

    Ausentes saem como np.nan (o SimpleImputer do scikit-learn nao reconhece pd.NA).
    """
    saida = pd.DataFrame(index=df.index)
    for nome in NUMERICAS:
        saida[nome] = pd.to_numeric(df[nome], errors="coerce").astype(float)
    municipio = df["CODMUNRES"].astype("string")
    derivadas = {
        "MESPRENAT": pd.to_numeric(df["MESPRENAT"], errors="coerce").astype("Int64").astype("string"),
        **{nome: contagem_com_teto(df[nome], tetos[nome]) for nome in HISTORICO},
        "ESCMAE2010": df["ESCMAE2010"],
        "RACACORMAE": df["RACACORMAE"],
        "ESTCIVMAE": df["ESTCIVMAE"],
        "PARIDADE": df["PARIDADE"],
        "CBO_GRUPO": grupo_cbo(df["CODOCUPMAE"]),
        "MESORREGIAO": municipio.map(mesorregioes),
    }
    for nome, serie in derivadas.items():
        serie = serie.astype("string")
        saida[nome] = serie.astype(object).where(serie.notna(), np.nan)
    saida["PETROLINA"] = (municipio == municipio_local).fillna(False).astype(float)
    return saida
