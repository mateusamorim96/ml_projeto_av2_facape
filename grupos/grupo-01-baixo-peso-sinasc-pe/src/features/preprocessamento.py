"""Pre-processamento como `Pipeline` do scikit-learn (RQ-PRE-02).

Todo passo com estado (imputacao, padronizacao, codificacao) vive aqui dentro e
so e ajustado com `fit` no treino de cada fold. O modelo da E4 entra como passo
final do mesmo `Pipeline`, de modo que a validacao cruzada reajusta tudo junto.
"""
from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (FunctionTransformer, MinMaxScaler, OneHotEncoder, SplineTransformer,
                                   StandardScaler)

from src.features.construcao import BINARIAS, CATEGORICAS, NUMERICAS, construir_atributos

ROTULO_AUSENTE = "ignorado"
_IMPUTACAO_NUMERICA = {"mediana": "median", "media": "mean"}
_ESCALONADORES = {"standard": StandardScaler, "minmax": MinMaxScaler}


def construir_preprocessador(cfg: dict, mesorregioes: dict[str, str]) -> Pipeline:
    pre = cfg["preprocessamento"]
    numericas = [("imputar", SimpleImputer(strategy=_IMPUTACAO_NUMERICA[pre["imputacao_numerica"]]))]
    if pre.get("idade_splines"):  # curva em U da idade (figura 3 da EDA); nos ajustados so no treino
        numericas.append(("splines", SplineTransformer(n_knots=pre["idade_splines"]["nos"],
                                                       degree=pre["idade_splines"]["grau"])))
    if pre["escalonamento"] != "none":
        numericas.append(("escalonar", _ESCALONADORES[pre["escalonamento"]]()))
    if pre["imputacao_categorica"] == "constante":
        imputar_categorica = SimpleImputer(strategy="constant", fill_value=ROTULO_AUSENTE)
    else:
        imputar_categorica = SimpleImputer(strategy="most_frequent")
    categoricas = Pipeline([
        ("imputar", imputar_categorica),
        ("codificar", OneHotEncoder(handle_unknown="infrequent_if_exist",
                                    min_frequency=pre["one_hot_min_frequency"], sparse_output=False)),
    ])
    colunas = ColumnTransformer([
        ("numericas", Pipeline(numericas), list(NUMERICAS)),
        ("categoricas", categoricas, list(CATEGORICAS)),
        ("binarias", "passthrough", list(BINARIAS)),
    ], verbose_feature_names_out=True)
    atributos = FunctionTransformer(
        construir_atributos,
        kw_args={"mesorregioes": mesorregioes, "municipio_local": cfg["dados"]["municipio_local"],
                 "tetos": pre["historico_teto"]},
    )
    return Pipeline([("atributos", atributos), ("colunas", colunas)])
