#!/usr/bin/env python3
"""Pipeline ponta a ponta do grupo GXX (preencher).

Uso:
    python -m src.pipeline --config configs/base.yaml
    python -m src.pipeline --config configs/base.yaml --etapa preparacao

Contrato deste esqueleto:
  1. le a configuracao YAML em `configs/base.yaml`;
  2. valida o ambiente e registra `reports/environment.json`;
  3. executa as etapas em ordem: dados -> features -> modelos -> avaliacao;
  4. grava tabelas em `reports/tables/` e figuras em `reports/figures/`.

As etapas abaixo sao intencionalmente vazias: implemente-as mantendo a assinatura.
Nao crie um `notebook` paralelo com a logica do pipeline -- o Docker executa AQUI.
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


def etapa_dados(cfg: dict) -> None:
    """Carrega o dado bruto e valida colunas esperadas.

    Implemente:
      * ler `dados.raw` + `dados.arquivo` (CSV/Parquet/JSON);
      * conferir presenca da coluna alvo e das colunas usadas;
      * aplicar filtros de recorte documentados no dicionario de dados;
      * gravar em `dados.processed`.
    """
    raise NotImplementedError("etapa_dados: implemente a carga e a validacao")


def etapa_features(cfg: dict) -> None:
    """Constroi o ColumnTransformer e o split de treino/teste.

    Implemente:
      * split ANTES de qualquer fit de transformacao (evita vazamento);
      * imputacao, escalonamento e encoding vindos de `preprocessamento`;
      * retorno do pipeline de features pronto para o modelo.
    """
    raise NotImplementedError("etapa_features: implemente o pre-processamento")


def etapa_modelos(cfg: dict) -> None:
    """Treina baseline + tres familias e registra em experiments/runs.csv.

    Implemente:
      * uma funcao build_*() por familia, lendo hiperparametros do YAML;
      * busca de hiperparametros em CV interna (nunca no teste);
      * log append-only em `saidas.runs` com modelo, params, seed e metricas.
    """
    raise NotImplementedError("etapa_modelos: implemente o treino e a busca")


def etapa_avaliacao(cfg: dict) -> None:
    """Valida com CV repetida, aplica teste estatistico e gera figuras.

    Implemente:
      * mesma lista de folds (mesma seed) para todos os modelos;
      * media e desvio da metrica principal;
      * teste conforme `teste_estatistico` + tamanho de efeito + IC;
      * tabelas em `saidas.tabelas` e figuras em `saidas.figuras`.
    """
    raise NotImplementedError("etapa_avaliacao: implemente a comparacao estatistica")


ETAPAS = {
    "dados": etapa_dados,
    "features": etapa_features,
    "modelos": etapa_modelos,
    "avaliacao": etapa_avaliacao,
}


# ---------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pipeline do projeto AV2 (GXX).")
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
