"""Split treino/teste e pre-processamento sem vazamento (E3) - G02.

Ordem obrigatoria (ver `docs/decisoes-tecnicas.md`, secao 4):

  1. `dividir_treino_teste`  -> separa o teste ANTES de qualquer `fit`;
  2. `selecionar_preditores` -> regra de % de ausentes medida SO no treino;
  3. `construir_preprocessador` -> Pipeline sklearn NAO ajustado
     (recorte por percentis -> imputacao pela mediana + indicador -> padronizacao).

Na E4/E5 o objeto de `construir_preprocessador` deve ir DENTRO do Pipeline de
cada modelo, para que o `fit` aconteca apenas no treino de cada fold.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_is_fitted

from src.data.carregar import ALVO_T, ALVO_T1


class RecortePercentil(BaseEstimator, TransformerMixin):
    """Limita cada coluna aos percentis [inferior, superior] aprendidos no `fit`.

    Os indicadores SINISA tem caudas extremas (ex.: IFA2011 ate 154.089 %,
    IAG2005 com -719 m³/economia/mes). Em vez de apagar municipios, os valores
    sao limitados (winsorizacao) com limites calculados apenas no treino.
    NaN e preservado para a imputacao seguinte.
    """

    def __init__(self, inferior: float = 1.0, superior: float = 99.0):
        self.inferior = inferior
        self.superior = superior

    def fit(self, X, y=None):
        if isinstance(X, pd.DataFrame):
            self.feature_names_in_ = np.asarray(X.columns, dtype=object)
        X = np.asarray(X, dtype=float)
        self.n_features_in_ = X.shape[1]
        self.limite_inferior_ = np.nanpercentile(X, self.inferior, axis=0)
        self.limite_superior_ = np.nanpercentile(X, self.superior, axis=0)
        return self

    def transform(self, X):
        check_is_fitted(self, "limite_inferior_")
        colunas = X.columns if isinstance(X, pd.DataFrame) else None
        Z = np.clip(np.asarray(X, dtype=float), self.limite_inferior_, self.limite_superior_)
        return pd.DataFrame(Z, columns=colunas, index=X.index) if colunas is not None else Z

    def get_feature_names_out(self, input_features=None):
        if input_features is not None:
            return np.asarray(input_features, dtype=object)
        if hasattr(self, "feature_names_in_"):
            return self.feature_names_in_.copy()
        return np.asarray([f"x{i}" for i in range(self.n_features_in_)], dtype=object)


def faixas_do_alvo(y: pd.Series, n_faixas: int) -> pd.Series:
    """Quantis do alvo usados so para estratificar o split (nenhum fit)."""
    return pd.qcut(y, q=n_faixas, labels=False, duplicates="drop")


def dividir_treino_teste(base: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    dados = cfg["dados"]
    estratos = None
    if dados.get("estratificar", True):
        estratos = faixas_do_alvo(base[ALVO_T1], int(dados.get("n_faixas_estratificacao", 5)))
    treino, teste = train_test_split(
        base,
        test_size=float(dados["proporcao_teste"]),
        random_state=int(cfg["project"]["seed"]),
        stratify=estratos,
    )
    return treino.sort_index(), teste.sort_index()


def selecionar_preditores(
    treino: pd.DataFrame, candidatos: list[str], limite: float
) -> tuple[list[str], pd.DataFrame]:
    """Mantem indicadores com ate `limite` de ausentes NO TREINO.

    A mesma regra da E2 (20 %), agora medida no conjunto de treino para que nem
    a escolha de colunas dependa do teste. `alvo_t` entra sempre como preditor.
    """
    ausente = treino[candidatos].isna().mean()
    selecionados = [c for c in candidatos if ausente[c] <= limite]
    tabela = pd.DataFrame(
        {
            "coluna": candidatos,
            "ausente_treino_pct": (100 * ausente).round(2).values,
            "selecionado": [c in selecionados for c in candidatos],
        }
    )
    return [ALVO_T] + selecionados, tabela


def construir_preprocessador(cfg: dict) -> Pipeline:
    """Pipeline de preparacao NAO ajustado, parametrizado por `preprocessamento`."""
    prep = cfg["preprocessamento"]
    estrategias = {"mediana": "median", "media": "mean", "constante": "constant"}
    passos: list[tuple[str, object]] = []
    recorte = prep.get("recorte_percentis")
    if recorte:
        passos.append(("recorte", RecortePercentil(inferior=recorte[0], superior=recorte[1])))
    passos.append(
        (
            "imputacao",
            SimpleImputer(
                strategy=estrategias[prep.get("imputacao_numerica", "mediana")],
                add_indicator=bool(prep.get("indicador_ausencia", True)),
                fill_value=0,
            ),
        )
    )
    if prep.get("escalonamento", "standard") == "standard":
        passos.append(("escala", StandardScaler()))
    return Pipeline(passos).set_output(transform="pandas")


def tabela_tratamento(
    preprocessador: Pipeline,
    preditores: list[str],
    treino: pd.DataFrame,
    teste: pd.DataFrame,
) -> pd.DataFrame:
    """Documenta, por preditor, o que o preprocessador aprendeu no treino."""
    passos = preprocessador.named_steps
    imputador = passos["imputacao"]
    linhas = []
    for i, c in enumerate(preditores):
        linha = {
            "preditor": c,
            "ausente_treino_pct": round(100 * treino[c].isna().mean(), 2),
            "ausente_teste_pct": round(100 * teste[c].isna().mean(), 2),
            "valor_imputado_treino": round(float(imputador.statistics_[i]), 4),
            "ganha_indicador_ausencia": bool(
                imputador.indicator_ is not None and i in imputador.indicator_.features_
            ),
        }
        if "recorte" in passos:
            r = passos["recorte"]
            lo, hi = r.limite_inferior_[i], r.limite_superior_[i]
            linha.update(
                {
                    "limite_inferior_treino": round(float(lo), 4),
                    "limite_superior_treino": round(float(hi), 4),
                    "recortados_treino": int(((treino[c] < lo) | (treino[c] > hi)).sum()),
                    "recortados_teste": int(((teste[c] < lo) | (teste[c] > hi)).sum()),
                }
            )
        linhas.append(linha)
    return pd.DataFrame(linhas)


def diagnostico_desbalanceamento(
    conjuntos: dict[str, pd.DataFrame], limites: list[float]
) -> pd.DataFrame:
    """Proporcao de municipios acima de cada limite candidato de alerta.

    O alvo e continuo (regressao), mas a decisao da E1 e um alerta "perda acima
    de um limite". A proporcao da classe "alerta" mostra se uma metrica de
    classificacao derivada (E5) seria desbalanceada.
    """
    linhas = []
    for nome, d in conjuntos.items():
        for lim in limites:
            acima = int((d[ALVO_T1] > lim).sum())
            linhas.append(
                {
                    "conjunto": nome,
                    "limite_pct": lim,
                    "municipios": len(d),
                    "acima_do_limite": acima,
                    "proporcao_acima_pct": round(100 * acima / len(d), 1),
                }
            )
    return pd.DataFrame(linhas)
