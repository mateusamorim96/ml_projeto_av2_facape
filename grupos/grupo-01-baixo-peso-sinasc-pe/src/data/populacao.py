"""Populacao do modelo: quem passa pela decisao da proposta.

Fonte unica para a auditoria (E2) e para a preparacao (E3). A decisao acontece
na captacao da gestante, entao a populacao e:
  * registro com peso plausivel (alvo definido);
  * gestacao unica -- gestacoes multiplas tem ~60% de baixo peso, ja sao
    reconhecidas como alto risco sem modelo e geram registros correlacionados
    (um por bebe, sem identificador da mae para agrupar nos folds);
  * mes de inicio do pre-natal registrado (01-09) -- quem passa pela captacao
    tem esse mes conhecido; a ausencia so existe no registro retrospectivo.
"""
from __future__ import annotations

import pandas as pd

PESO_PLAUSIVEL = (300, 6500)  # g; fora disso o registro e tratado como erro de digitacao
MESES_PRENATAL = tuple(f"{mes:02d}" for mes in range(1, 10))


def peso_numerico(df: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(df["PESO"], errors="coerce")


def etapas_populacao(df: pd.DataFrame, cfg: dict) -> list[tuple[str, pd.Series]]:
    """Criterios cumulativos de inclusao, na ordem em que sao aplicados."""
    regras = cfg["dados"]["populacao"]
    criterios = [
        (f"peso plausível ({PESO_PLAUSIVEL[0]}–{PESO_PLAUSIVEL[1]:,} g)".replace(",", "."),
         peso_numerico(df).between(*PESO_PLAUSIVEL)),
        ("gestação única", df["GRAVIDEZ"].isin(regras["gravidez"])),
    ]
    if regras.get("exigir_mesprenat", True):
        criterios.append(("mês de início do pré-natal registrado (01–09)", df["MESPRENAT"].isin(MESES_PRENATAL)))
    etapas = []
    mascara = pd.Series(True, index=df.index)
    for nome, criterio in criterios:
        mascara = mascara & criterio
        etapas.append((nome, mascara.copy()))
    return etapas


def mascara_populacao(df: pd.DataFrame, cfg: dict) -> pd.Series:
    return etapas_populacao(df, cfg)[-1][1]
