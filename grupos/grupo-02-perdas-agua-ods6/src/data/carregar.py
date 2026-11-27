"""Carga e montagem da base modelavel (E3) - G02.

Le as planilhas SINISA de 2023 (preditores) e 2024 (alvo), pareia os municipios
pelo codigo IBGE e aplica o recorte documentado em `docs/dicionario-de-dados.md`:

  * apenas a macrorregiao definida em `dados.recorte_macrorregiao` (Nordeste);
  * apenas municipios com IAG2013 numerico e dentro de `dados.faixa_alvo` nos
    dois anos (regra de plausibilidade da E2).

Nada aqui e ajustado (`fit`) aos dados: so leitura, conversao de tipos e
filtros determinísticos. A selecao de preditores por % de ausentes e todo o
pre-processamento acontecem DEPOIS do split, em `src/features/preparacao.py`.

Os leitores de planilha sao os mesmos da auditoria (`auditoria_sinisa.py`), para
que E2 e E3 interpretem o layout SINISA exatamente da mesma forma.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.auditoria_sinisa import RE_INDICADOR, ler_planilha, sha256

# Colunas que nunca entram como preditor (identificacao, recorte e subgrupos).
COLUNAS_ID = ["cod_IBGE", "Município", "UF", "Macrorregião", "Capital", "RM/RIDE"]
ALVO_T = "alvo_t"     # IAG2013 em 2023 (persistencia / preditor defasado)
ALVO_T1 = "alvo_t1"   # IAG2013 em 2024 (variavel-alvo)


def conferir_arquivos(raw: Path, dados: dict) -> list[Path]:
    arquivos = [raw / dados["arquivo_t"], raw / dados["arquivo_t1"]]
    faltando = [a for a in arquivos if not a.is_file()]
    if faltando:
        nomes = "\n  ".join(str(a) for a in faltando)
        raise SystemExit(
            f"arquivo bruto ausente:\n  {nomes}\n"
            "Baixe os ZIPs oficiais e extraia a pasta 'Água - Base Municipal' em "
            "data/raw/ (passo a passo em docs/dicionario-de-dados.md, secao 7)."
        )
    return arquivos


def conferir_hashes(arquivos: list[Path], esperados: dict[str, str] | None) -> None:
    """Interrompe se o arquivo baixado nao for o mesmo auditado na E2."""
    if not esperados:
        return
    for arq in arquivos:
        esperado = esperados.get(arq.name)
        if esperado and sha256(arq) != esperado.upper():
            raise SystemExit(
                f"SHA-256 de {arq.name} difere do registrado na E2. "
                "O arquivo oficial pode ter sido republicado; refaça a auditoria."
            )


def montar_base(raiz: Path, dados: dict) -> pd.DataFrame:
    """Devolve uma linha por municipio do recorte: ids + indicadores 2023 + alvo."""
    raw = raiz / dados["raw"]
    arquivos = conferir_arquivos(raw, dados)
    conferir_hashes(arquivos, dados.get("sha256"))
    chave, alvo = dados["chave"], dados["alvo"]
    lo, hi = dados["faixa_alvo"]

    t, _, _, _ = ler_planilha(arquivos[0], dados["abas_t"])
    t1, _, _, _ = ler_planilha(arquivos[1], dados["abas_t1"])

    indicadores = sorted(c for c in t.columns if RE_INDICADOR.match(c))
    ids = [c for c in COLUNAS_ID if c in t.columns]
    base = t[ids + indicadores].copy()
    # "Não Calc.- Dados Não Inf." / "Não Calc.- Div/0" viram ausente (NaN), nunca zero.
    for c in indicadores:
        base[c] = pd.to_numeric(base[c], errors="coerce")

    base = base.merge(
        t1[[chave, alvo]].rename(columns={alvo: ALVO_T1}), on=chave, how="inner"
    )
    base = base.rename(columns={alvo: ALVO_T})
    base[ALVO_T1] = pd.to_numeric(base[ALVO_T1], errors="coerce")

    base = base[base["Macrorregião"] == dados["recorte_macrorregiao"]]
    base = base[base[ALVO_T].between(lo, hi) & base[ALVO_T1].between(lo, hi)]
    if base[chave].duplicated().any():
        raise SystemExit("codigo IBGE duplicado apos o pareamento (esperado 1:1)")

    sub = dados.get("subgrupos", {})
    base["subgrupo_pe_ba"] = base["UF"].isin(sub.get("ufs_pe_ba", []))
    base["subgrupo_ride"] = base["RM/RIDE"] == sub.get("ride_petrolina_juazeiro")
    return base.sort_values(chave).reset_index(drop=True)


def colunas_indicadores(base: pd.DataFrame) -> list[str]:
    """Indicadores de 2023 candidatos (o IAG2013 de 2023 entra como `alvo_t`)."""
    return [c for c in base.columns if RE_INDICADOR.match(c)]
