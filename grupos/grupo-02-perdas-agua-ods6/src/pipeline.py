#!/usr/bin/env python3
"""Pipeline ponta a ponta do grupo G02 - perdas de agua no Nordeste (ODS 6.4).

Uso:
    python -m src.pipeline --config configs/base.yaml
    python -m src.pipeline --config configs/base.yaml --etapa preparacao

Contrato deste esqueleto:
  1. le a configuracao YAML em `configs/base.yaml`;
  2. valida o ambiente e registra `reports/environment.json`;
  3. executa as etapas em ordem: dados -> features -> modelos -> avaliacao;
  4. grava tabelas em `reports/tables/` e figuras em `reports/figures/`.

Estado: `dados` e `features` implementadas na E3; `modelos` (E4) e `avaliacao`
(E5) ainda pendentes -- sao puladas com aviso, sem falhar a execucao.
Nao crie um `notebook` paralelo com a logica do pipeline -- o Docker executa AQUI.
O notebook de EDA apenas LE as saidas desta etapa.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------- utilidades


def carregar_config(caminho: Path) -> dict:
    """Le o YAML de configuracao (dependencia: pyyaml)."""
    try:
        import yaml
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise SystemExit("Falta pyyaml. Rode: pip install -r requirements.txt") from exc
    if not caminho.is_file():
        raise SystemExit(f"Config nao encontrada: {caminho}")
    with caminho.open(encoding="utf-8") as arquivo:
        return yaml.safe_load(arquivo)


def fixar_sementes(seed: int) -> None:
    """Fixa sementes de random/numpy para reprodutibilidade."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ModuleNotFoundError:
        pass


def versao_git() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=RAIZ,
            timeout=10,
        ).stdout.strip() or "sem-git"
    except (OSError, subprocess.SubprocessError):
        return "sem-git"


def registrar_ambiente(cfg: dict, destino: Path) -> None:
    """Grava reports/environment.json (exigido na E6)."""
    import importlib.metadata as md

    pacotes = sorted(
        {d.split("==")[0].strip().lower() for d in _requirements() if d.strip()}
    )
    versoes = {}
    for pacote in pacotes:
        try:
            versoes[pacote] = md.version(pacote)
        except md.PackageNotFoundError:
            versoes[pacote] = "nao instalado"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(
            {
                "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "commit": versao_git(),
                "python": platform.python_version(),
                "plataforma": platform.platform(),
                "seed": cfg.get("project", {}).get("seed"),
                "grupo": cfg.get("project", {}).get("grupo"),
                "pacotes": versoes,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _requirements() -> list[str]:
    arquivo = RAIZ / "requirements.txt"
    if not arquivo.is_file():
        return []
    linhas = arquivo.read_text(encoding="utf-8").splitlines()
    return [
        ln.split("#")[0].strip()
        for ln in linhas
        if ln.strip() and not ln.strip().startswith("-")
    ]


# -------------------------------------------------------------------- etapas


def _csv(df, caminho: Path) -> None:
    """CSV com fim de linha LF (evita diff falso entre Windows e Linux)."""
    df.to_csv(caminho, index=False, lineterminator="\n")


def etapa_dados(cfg: dict) -> None:
    """Le o SINISA 2023/2024, aplica o recorte da E2 e grava a base pareada.

    Saida: `data/processed/base-nordeste.csv` (uma linha por municipio). Nenhum
    `fit` acontece aqui: so leitura, conversao de "Nao Calc." em NaN e filtros.
    """
    from src.data.carregar import ALVO_T, ALVO_T1, colunas_indicadores, montar_base

    processed = RAIZ / cfg["dados"]["processed"]
    processed.mkdir(parents=True, exist_ok=True)
    base = montar_base(RAIZ, cfg["dados"])
    _csv(base, processed / "base-nordeste.csv")
    print(
        f"[dados] {len(base)} municipios | {len(colunas_indicadores(base))} indicadores 2023 "
        f"+ {ALVO_T} | alvo {ALVO_T1}: media {base[ALVO_T1].mean():.2f} %"
    )


def etapa_features(cfg: dict) -> None:
    """Split treino/teste, selecao de preditores e preparacao SEM vazamento.

    1. split estratificado por quintis do alvo, ANTES de qualquer fit;
    2. regra de % de ausentes medida so no treino;
    3. preprocessador (recorte -> imputacao -> escala) ajustado so no treino e
       apenas aplicado (`transform`) ao teste.

    Saidas em `data/processed/`: treino.csv, teste.csv (valores originais),
    treino-preparado.csv, teste-preparado.csv e preditores.json.
    Tabelas em `reports/tables/`: preparacao-*.csv.
    """
    import pandas as pd

    from src.data.carregar import ALVO_T, ALVO_T1, COLUNAS_ID, colunas_indicadores
    from src.features.preparacao import (
        construir_preprocessador,
        diagnostico_desbalanceamento,
        dividir_treino_teste,
        selecionar_preditores,
        tabela_tratamento,
    )

    dados = cfg["dados"]
    processed = RAIZ / dados["processed"]
    tabelas = RAIZ / cfg["saidas"]["tabelas"]
    origem = processed / "base-nordeste.csv"
    if not origem.is_file():
        raise SystemExit("rode antes a etapa 'dados' (base-nordeste.csv ausente)")
    base = pd.read_csv(origem)

    treino, teste = dividir_treino_teste(base, cfg)
    preditores, selecao = selecionar_preditores(
        treino, colunas_indicadores(base), float(dados["max_ausentes_preditor"])
    )

    prep = construir_preprocessador(cfg)
    X_treino = prep.fit_transform(treino[preditores])   # fit SO no treino
    X_teste = prep.transform(teste[preditores])         # teste: apenas transform

    meta = [c for c in COLUNAS_ID + ["subgrupo_pe_ba", "subgrupo_ride"] if c in base.columns]
    _csv(treino, processed / "treino.csv")
    _csv(teste, processed / "teste.csv")
    for nome, X, d in (("treino", X_treino, treino), ("teste", X_teste, teste)):
        saida = pd.concat(
            [d[meta].reset_index(drop=True), X.reset_index(drop=True),
             d[[ALVO_T1]].reset_index(drop=True)],
            axis=1,
        )
        _csv(saida, processed / f"{nome}-preparado.csv")
    (processed / "preditores.json").write_text(
        json.dumps({"alvo": ALVO_T1, "preditores": preditores,
                    "colunas_preparadas": list(X_treino.columns)}, indent=2),
        encoding="utf-8",
    )

    _csv(tabela_tratamento(prep, preditores, treino, teste),
         tabelas / "preparacao-tratamento-preditores.csv")
    _csv(selecao, tabelas / "preparacao-selecao-preditores.csv")
    limites = [float(x) for x in cfg.get("diagnostico", {}).get("limites_alerta_pct", [])]
    _csv(diagnostico_desbalanceamento({"base": base, "treino": treino, "teste": teste}, limites),
         tabelas / "preparacao-desbalanceamento-alvo.csv")

    def resumo(nome, d):
        return {
            "conjunto": nome, "municipios": len(d),
            "alvo_t1_media": round(d[ALVO_T1].mean(), 2),
            "alvo_t1_desvio": round(d[ALVO_T1].std(), 2),
            "alvo_t1_mediana": round(d[ALVO_T1].median(), 2),
            "pe_ba": int(d["subgrupo_pe_ba"].sum()),
            "ride_petrolina_juazeiro": int(d["subgrupo_ride"].sum()),
            **{f"uf_{uf}": int((d["UF"] == uf).sum()) for uf in sorted(base["UF"].unique())},
        }
    _csv(pd.DataFrame([resumo("base", base), resumo("treino", treino), resumo("teste", teste)]),
         tabelas / "preparacao-split.csv")

    excluidos = selecao.loc[~selecao["selecionado"], "coluna"].tolist()
    print(
        f"[features] treino={len(treino)} teste={len(teste)} | preditores={len(preditores)} "
        f"(excluidos por ausencia no treino: {excluidos}) | "
        f"colunas apos preparacao={X_treino.shape[1]}"
    )


def etapa_modelos(cfg: dict) -> None:
    """Treina baseline + tres familias e registra em experiments/runs.csv.

    Implemente:
      * uma funcao build_*() por familia, lendo hiperparametros do YAML;
      * busca de hiperparametros em CV interna (nunca no teste);
      * log append-only em `saidas.runs` com modelo, params, seed e metricas.
    """
    print("[modelos] pendente: implementada na E4 (baseline de persistencia + 3 familias)")


def etapa_avaliacao(cfg: dict) -> None:
    """Valida com CV repetida, aplica teste estatistico e gera figuras.

    Implemente:
      * mesma lista de folds (mesma seed) para todos os modelos;
      * media e desvio da metrica principal;
      * teste conforme `teste_estatistico` + tamanho de efeito + IC;
      * tabelas em `saidas.tabelas` e figuras em `saidas.figuras`.
    """
    print("[avaliacao] pendente: implementada na E5 (CV repetida + teste estatistico)")


ETAPAS = {
    "dados": etapa_dados,
    "features": etapa_features,
    "modelos": etapa_modelos,
    "avaliacao": etapa_avaliacao,
}


# ---------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pipeline do projeto AV2 (G02).")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument(
        "--etapa",
        choices=sorted(ETAPAS),
        help="executa apenas uma etapa (default: todas, em ordem)",
    )
    parser.add_argument(
        "--somente-ambiente",
        action="store_true",
        help="apenas valida config e grava reports/environment.json",
    )
    args = parser.parse_args(argv)

    cfg = carregar_config(RAIZ / args.config)
    seed = int(cfg.get("project", {}).get("seed", 42))
    fixar_sementes(seed)

    for chave in ("tabelas", "figuras"):
        (RAIZ / cfg["saidas"][chave]).mkdir(parents=True, exist_ok=True)
    registrar_ambiente(cfg, RAIZ / cfg["saidas"]["ambiente"])
    print(f"[pipeline] grupo={cfg['project'].get('grupo')} seed={seed} commit={versao_git()}")

    if args.somente_ambiente:
        print("[pipeline] ambiente registrado; etapas nao executadas")
        return 0

    ordem = [args.etapa] if args.etapa else ["dados", "features", "modelos", "avaliacao"]
    for nome in ordem:
        print(f"[pipeline] etapa: {nome}")
        ETAPAS[nome](cfg)
    print("[pipeline] concluido")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except NotImplementedError as exc:
        print(f"[pipeline] etapa pendente: {exc}", file=sys.stderr)
        sys.exit(2)
