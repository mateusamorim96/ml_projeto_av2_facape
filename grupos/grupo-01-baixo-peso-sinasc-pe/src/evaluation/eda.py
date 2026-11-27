#!/usr/bin/env python3
"""Figuras da analise exploratoria (E3), geradas por script.

Uso:
    python -m src.evaluation.eda --config configs/base.yaml
    (tambem roda como etapa `eda` do pipeline)

Regras:
  * so o conjunto de DESENVOLVIMENTO (2019-2023); o teste (2024) nao e explorado;
  * cada figura grava reports/figures/figura-eda-NN-<assunto>.png e os dados
    plotados em reports/tables/tabela-eda-NN-<assunto>.csv;
  * prevalencias com IC 95% de Wilson.
O notebook notebooks/01-eda-baixo-peso.ipynb chama estas funcoes e registra a
decisao que cada figura sustenta.
"""
from __future__ import annotations

import argparse
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.config import RAIZ, carregar_config  # noqa: E402

# Paleta de referencia (skill dataviz), validada para o fundo claro.
AZUL, LARANJA = "#257de0", "#f47230"
TEXTO, TEXTO_2, GRADE = "#191919", "#666666", "#e6e6e6"
Z95 = 1.959964

plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 150, "font.size": 10,
    "axes.edgecolor": GRADE, "axes.labelcolor": TEXTO_2, "axes.titlecolor": TEXTO,
    "axes.titlesize": 11, "axes.titleweight": "semibold", "axes.titlelocation": "left",
    "xtick.color": TEXTO_2, "ytick.color": TEXTO_2, "axes.grid": True, "grid.color": GRADE,
    "grid.linewidth": 0.8, "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False,
})


# ------------------------------------------------------------------ utilidades

def wilson(positivos: np.ndarray, n: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """IC 95% de Wilson para uma proporcao (em %)."""
    positivos, n = np.asarray(positivos, float), np.asarray(n, float)
    p = positivos / n
    centro = (p + Z95**2 / (2 * n)) / (1 + Z95**2 / n)
    meia = Z95 * np.sqrt(p * (1 - p) / n + Z95**2 / (4 * n**2)) / (1 + Z95**2 / n)
    return 100 * (centro - meia), 100 * (centro + meia)


def prevalencia(grupos: pd.Series, alvo: pd.Series, minimo: int = 0) -> pd.DataFrame:
    tabela = alvo.groupby(grupos, dropna=False, observed=True).agg(registros="size", baixo_peso="sum")
    tabela = tabela[tabela["registros"] >= minimo].copy()
    tabela["pct_baixo_peso"] = 100 * tabela["baixo_peso"] / tabela["registros"]
    tabela["ic95_inf"], tabela["ic95_sup"] = wilson(tabela["baixo_peso"], tabela["registros"])
    return tabela.round(3)


def salvar(fig: plt.Figure, tabela: pd.DataFrame, nome: str, cfg: dict) -> None:
    fig.savefig(RAIZ / cfg["saidas"]["figuras"] / f"figura-eda-{nome}.png", bbox_inches="tight", facecolor="white")
    tabela.to_csv(RAIZ / cfg["saidas"]["tabelas"] / f"tabela-eda-{nome}.csv")


def linha_referencia(ax: plt.Axes, valor: float, rotulo: str, vertical: bool = False) -> None:
    desenhar = ax.axvline if vertical else ax.axhline
    desenhar(valor, color=TEXTO_2, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
    if vertical:
        ax.annotate(rotulo, (valor, 1.0), xycoords=("data", "axes fraction"), xytext=(3, 0),
                    textcoords="offset points", color=TEXTO_2, fontsize=8, va="top")
    else:
        ax.annotate(rotulo, (1.0, valor), xycoords=("axes fraction", "data"), xytext=(0, 3),
                    textcoords="offset points", color=TEXTO_2, fontsize=8, ha="right")


def carregar_desenvolvimento(cfg: dict) -> pd.DataFrame:
    caminho = RAIZ / cfg["dados"]["processed"] / "desenvolvimento.pkl"
    if not caminho.is_file():
        raise SystemExit("desenvolvimento.pkl ausente. Rode antes: python -m src.pipeline --etapa dados")
    return pd.read_pickle(caminho)


# --------------------------------------------------------------------- figuras

def figura_prevalencia_por_ano(cfg: dict) -> tuple[plt.Figure, pd.DataFrame]:
    """F1: desbalanceamento e tendencia, todos os nascidos vivos x populacao do modelo."""
    from src.data.carregar import carregar_sinasc
    from src.data.populacao import PESO_PLAUSIVEL, mascara_populacao, peso_numerico
    from src.data.preparar import remover_duplicatas

    bruto = remover_duplicatas(carregar_sinasc(cfg))  # mesma limpeza do pipeline
    bruto = bruto[bruto["ANO"] < cfg["dados"]["ano_teste"]]  # 2024 e o teste: fora da EDA
    peso = peso_numerico(bruto)
    plausivel = peso.between(*PESO_PLAUSIVEL)
    baixo = (peso < cfg["dados"]["limiar_peso_g"]).fillna(False).astype(int)  # NA so fora do plausivel
    todos = prevalencia(bruto.loc[plausivel, "ANO"], baixo[plausivel])
    populacao = mascara_populacao(bruto, cfg)
    modelo = prevalencia(bruto.loc[populacao, "ANO"], baixo[populacao])
    tabela = pd.concat({"todos os nascidos vivos": todos, "população do modelo": modelo}, names=["grupo", "ano"])

    fig, ax = plt.subplots(figsize=(8, 4.2))
    dev = cfg["dados"]["anos_desenvolvimento"]
    ax.axvspan(min(dev) - 0.5, max(dev) + 0.5, color="#f4f4f4", zorder=0, linewidth=0)
    ax.annotate("desenvolvimento", (np.mean(dev), 1.0), xycoords=("data", "axes fraction"),
                ha="center", va="top", color=TEXTO_2, fontsize=8)
    for rotulo, serie, cor in (("todos os nascidos vivos", todos, LARANJA), ("população do modelo", modelo, AZUL)):
        ax.fill_between(serie.index, serie["ic95_inf"], serie["ic95_sup"], color=cor, alpha=0.15, linewidth=0)
        ax.plot(serie.index, serie["pct_baixo_peso"], color=cor, linewidth=2, marker="o", markersize=5,
                markeredgecolor="white", markeredgewidth=1.5, label=rotulo)
        ultimo = serie.index.max()
        ax.annotate(rotulo, (ultimo, serie.loc[ultimo, "pct_baixo_peso"]), xytext=(8, 0),
                    textcoords="offset points", va="center", color=TEXTO, fontsize=9)
    ax.set_xticks(todos.index)
    ax.set_xlim(todos.index.min() - 0.5, todos.index.max() + 2.6)
    ax.set_ylabel("baixo peso ao nascer (%)")
    ax.set_xlabel("ano de nascimento")
    ax.set_title("Prevalência de baixo peso por ano, Pernambuco (IC 95%)")
    ax.legend(loc="upper left", fontsize=9)
    return fig, tabela


def figura_ausentes(df: pd.DataFrame, cfg: dict) -> tuple[plt.Figure, pd.DataFrame]:
    """F2: ausentes por atributo e prevalencia entre quem tem o dado ausente."""
    from src.data.esquema import ATRIBUTOS

    alvo = df[cfg["dados"]["alvo"]]
    linhas = []
    for nome in ATRIBUTOS:
        ausente = df[nome].isna()
        linhas.append({"atributo": nome, "pct_ausente": 100 * ausente.mean(), "ausentes": int(ausente.sum()),
                       "pct_baixo_peso_ausente": 100 * alvo[ausente].mean() if ausente.any() else np.nan,
                       "pct_baixo_peso_presente": 100 * alvo[~ausente].mean()})
    tabela = pd.DataFrame(linhas).set_index("atributo").sort_values("pct_ausente").round(3)
    com_ausente = tabela[tabela["ausentes"] > 0]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(com_ausente.index, com_ausente["pct_ausente"], color=AZUL, height=0.6)
    for nome, linha in com_ausente.iterrows():
        texto = "< 0,01%" if linha["pct_ausente"] < 0.01 else f"{linha['pct_ausente']:.2f}%".replace(".", ",")
        ax.annotate(texto, (linha["pct_ausente"], nome),
                    xytext=(4, 0), textcoords="offset points", va="center", color=TEXTO, fontsize=8)
    ax.set_xlabel("registros com o atributo ausente ou ignorado (%)")
    ax.set_xlim(0, com_ausente["pct_ausente"].max() * 1.2)
    ax.grid(axis="y", visible=False)
    sem = ", ".join(tabela.index[tabela["ausentes"] == 0])
    ax.set_title("Ausentes por atributo, população de desenvolvimento")
    ax.annotate(f"sem ausentes: {sem}", (0, -0.2), xycoords="axes fraction", color=TEXTO_2, fontsize=8)
    return fig, tabela


def figura_idade_mae(df: pd.DataFrame, cfg: dict) -> tuple[plt.Figure, pd.DataFrame]:
    """F3: prevalencia por idade da mae (anos completos, so idades com >= 500 registros)."""
    alvo = df[cfg["dados"]["alvo"]]
    tabela = prevalencia(df["IDADEMAE"].astype("Int64"), alvo, minimo=500)
    tabela.index = tabela.index.astype(int)
    total = 100 * alvo.mean()

    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.fill_between(tabela.index, tabela["ic95_inf"], tabela["ic95_sup"], color=AZUL, alpha=0.18, linewidth=0)
    ax.plot(tabela.index, tabela["pct_baixo_peso"], color=AZUL, linewidth=2)
    minimo = tabela["pct_baixo_peso"].idxmin()
    ax.plot([minimo], [tabela.loc[minimo, "pct_baixo_peso"]], marker="o", markersize=8, color=AZUL,
            markeredgecolor="white", markeredgewidth=2)
    ax.annotate(f"mínimo aos {minimo} anos", (minimo, tabela.loc[minimo, "pct_baixo_peso"]), xytext=(0, -16),
                textcoords="offset points", ha="center", color=TEXTO, fontsize=8)
    linha_referencia(ax, total, f"média da população: {total:.2f}%".replace(".", ","))
    ax.set_xlabel("idade da mãe (anos)")
    ax.set_ylabel("baixo peso ao nascer (%)")
    ax.set_title("Prevalência de baixo peso por idade da mãe (IC 95%)")
    return fig, tabela


def figura_mes_prenatal(df: pd.DataFrame, cfg: dict) -> tuple[plt.Figure, pd.DataFrame]:
    """F4: prevalencia por mes de inicio do pre-natal."""
    alvo = df[cfg["dados"]["alvo"]]
    tabela = prevalencia(df["MESPRENAT"].astype("Int64"), alvo)
    tabela.index = tabela.index.astype(int)
    total = 100 * alvo.mean()

    fig, ax = plt.subplots(figsize=(8, 4.2))
    erro = [tabela["pct_baixo_peso"] - tabela["ic95_inf"], tabela["ic95_sup"] - tabela["pct_baixo_peso"]]
    ax.errorbar(tabela.index, tabela["pct_baixo_peso"], yerr=erro, fmt="o", color=AZUL, markersize=7,
                markeredgecolor="white", markeredgewidth=1.5, elinewidth=1.5, capsize=0)
    linha_referencia(ax, total, f"média da população: {total:.2f}%".replace(".", ","))
    rotulos = [f"{mes}\nn={int(n):,}".replace(",", ".") for mes, n in tabela["registros"].items()]
    ax.set_xticks(tabela.index, rotulos, fontsize=8)
    ax.set_xlabel("mês de gestação em que o pré-natal começou")
    ax.set_ylabel("baixo peso ao nascer (%)")
    ax.set_title("Prevalência de baixo peso por mês de início do pré-natal (IC 95%)")
    return fig, tabela


def figura_historico(df: pd.DataFrame, cfg: dict) -> tuple[plt.Figure, pd.DataFrame]:
    """F5: historico obstetrico, com a cauda agrupada em 'N+' pelos mesmos tetos do modelo (config)."""
    from src.features.construcao import contagem_com_teto

    alvo = df[cfg["dados"]["alvo"]]
    tetos = cfg["preprocessamento"]["historico_teto"]
    paineis = (("QTDGESTANT", "gestações anteriores"), ("QTDPARTCES", "cesáreas anteriores"),
               ("QTDFILMORT", "perdas fetais e abortos"))
    total = 100 * alvo.mean()
    tabelas = {}
    fig, eixos = plt.subplots(1, 3, figsize=(10, 3.8), sharey=True)
    for ax, (coluna, rotulo) in zip(eixos, paineis):
        teto = tetos[coluna]
        rotulos = contagem_com_teto(df[coluna], teto)
        tabela = prevalencia(rotulos, alvo).drop(index=pd.NA, errors="ignore")
        tabela = tabela.loc[[str(i) for i in range(teto)] + [f"{teto}+"]]
        tabelas[coluna] = tabela
        erro = [tabela["pct_baixo_peso"] - tabela["ic95_inf"], tabela["ic95_sup"] - tabela["pct_baixo_peso"]]
        ax.errorbar(range(len(tabela)), tabela["pct_baixo_peso"], yerr=erro, fmt="o", color=AZUL, markersize=6,
                    markeredgecolor="white", markeredgewidth=1.5, elinewidth=1.5, capsize=0)
        ax.axhline(total, color=TEXTO_2, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
        ax.set_xticks(range(len(tabela)), tabela.index)
        ax.set_xlabel(rotulo)
        ax.set_title(rotulo.capitalize(), fontsize=10)
    eixos[0].set_ylabel("baixo peso ao nascer (%)")
    eixos[-1].annotate(f"média: {total:.2f}%".replace(".", ","), (1.0, total), xycoords=("axes fraction", "data"),
                       xytext=(0, 3), textcoords="offset points", ha="right", color=TEXTO_2, fontsize=8)
    fig.suptitle("Prevalência de baixo peso por histórico obstétrico (IC 95%)", x=0.01, ha="left",
                 fontsize=11, fontweight="semibold", color=TEXTO)
    fig.tight_layout()
    return fig, pd.concat(tabelas, names=["atributo", "valor"])


def figura_perfil(df: pd.DataFrame, cfg: dict) -> tuple[plt.Figure, pd.DataFrame]:
    """F6: escolaridade, raca/cor e ocupacao (grupos com >= 1.000 registros)."""
    from src.features.construcao import grupo_cbo

    alvo = df[cfg["dados"]["alvo"]]
    escolaridade = {"0": "sem escolaridade", "1": "fundamental I", "2": "fundamental II", "3": "médio",
                    "4": "superior incompleto", "5": "superior completo"}
    raca = {"1": "branca", "2": "preta", "3": "amarela", "4": "parda", "5": "indígena"}
    blocos = {
        "escolaridade": df["ESCMAE2010"].map(escolaridade).fillna("ignorada"),
        "raça/cor": df["RACACORMAE"].map(raca).fillna("ignorada"),
        "ocupação (CBO)": grupo_cbo(df["CODOCUPMAE"]).fillna("ignorada"),
    }
    ordem_escolaridade = list(escolaridade.values()) + ["ignorada"]
    tabelas = {}
    for nome, rotulos in blocos.items():
        tabela = prevalencia(rotulos, alvo, minimo=1000)
        if nome == "escolaridade":
            tabela = tabela.reindex([r for r in ordem_escolaridade if r in tabela.index])
        else:
            tabela = tabela.sort_values("pct_baixo_peso")
        tabelas[nome] = tabela
    total = 100 * alvo.mean()

    alturas = [len(t) for t in tabelas.values()]
    fig, eixos = plt.subplots(len(tabelas), 1, figsize=(8, 0.32 * sum(alturas) + 2.4), sharex=True,
                              gridspec_kw={"height_ratios": alturas})
    for ax, (nome, tabela) in zip(eixos, tabelas.items()):
        posicoes = np.arange(len(tabela))
        erro = [tabela["pct_baixo_peso"] - tabela["ic95_inf"], tabela["ic95_sup"] - tabela["pct_baixo_peso"]]
        ax.errorbar(tabela["pct_baixo_peso"], posicoes, xerr=erro, fmt="o", color=AZUL, markersize=6,
                    markeredgecolor="white", markeredgewidth=1.5, elinewidth=1.5, capsize=0)
        ax.axvline(total, color=TEXTO_2, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
        ax.set_yticks(posicoes, [str(i) for i in tabela.index])
        ax.set_ylim(-0.6, len(tabela) - 0.4)
        ax.grid(axis="y", visible=False)
        ax.set_title(nome, fontsize=10)
    eixos[0].annotate(f"média: {total:.2f}%".replace(".", ","), (total, 1.0), xycoords=("data", "axes fraction"),
                      xytext=(3, 2), textcoords="offset points", color=TEXTO_2, fontsize=8)
    eixos[-1].set_xlabel("baixo peso ao nascer (%), IC 95%")
    fig.suptitle("Prevalência de baixo peso por perfil da mãe (grupos com ≥ 1.000 registros)", x=0.01, ha="left",
                 fontsize=11, fontweight="semibold", color=TEXTO)
    fig.tight_layout()
    return fig, pd.concat(tabelas, names=["bloco", "categoria"])


FIGURAS = (
    ("01-prevalencia-por-ano", lambda df, cfg: figura_prevalencia_por_ano(cfg)),
    ("02-ausentes", figura_ausentes),
    ("03-idade-mae", figura_idade_mae),
    ("04-mes-inicio-prenatal", figura_mes_prenatal),
    ("05-historico-obstetrico", figura_historico),
    ("06-perfil-mae", figura_perfil),
)


def gerar_todas(cfg: dict) -> list[str]:
    for chave in ("tabelas", "figuras"):
        (RAIZ / cfg["saidas"][chave]).mkdir(parents=True, exist_ok=True)
    df = carregar_desenvolvimento(cfg)
    geradas = []
    for nome, funcao in FIGURAS:
        fig, tabela = funcao(df, cfg)
        salvar(fig, tabela, nome, cfg)
        plt.close(fig)
        geradas.append(f"figura-eda-{nome}.png")
    return geradas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Figuras da EDA (G01, E3).")
    parser.add_argument("--config", default="configs/base.yaml")
    args = parser.parse_args(argv)
    for nome in gerar_todas(carregar_config(args.config)):
        print(f"[eda] {nome}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
