#!/usr/bin/env python3
"""Pipeline ponta a ponta do grupo G01 — risco de baixo peso ao nascer (SINASC/PE).

Uso:
    python -m src.pipeline --config configs/base.yaml
    python -m src.pipeline --config configs/base.yaml --etapa dados

Etapas, em ordem:
  1. dados     -> baixa e confere os brutos (SHA-256), limpa, aplica a populacao e
                  faz o split temporal: data/processed/desenvolvimento.pkl (2019-2023)
                  e data/processed/teste.pkl (2024);
  2. eda       -> figuras e tabelas da analise exploratoria (so desenvolvimento);
  3. features  -> monta o Pipeline de pre-processamento, confere vazamento e lista
                  os atributos gerados;
  4. modelos   -> E4 (pendente);
  5. avaliacao -> E5 (pendente).

O conjunto de teste e gravado na etapa `dados` e so e lido na avaliacao final.
Nao ha notebook paralelo com a logica: o Docker executa AQUI.
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

import pandas as pd

from src.config import RAIZ, carregar_config

ARQUIVO_DESENVOLVIMENTO = "desenvolvimento.pkl"
ARQUIVO_TESTE = "teste.pkl"


# ----------------------------------------------------------------- utilidades


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


def registrar_ambiente(cfg: dict, seed: int, destino: Path) -> None:
    """Grava reports/environment.json (exigido na E6)."""
    import importlib.metadata as md

    pacotes = sorted({d.split("==")[0].strip().lower() for d in _requirements() if d.strip()})
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
                "seed": seed,
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
    return [ln.split("#")[0].strip() for ln in linhas if ln.strip() and not ln.strip().startswith("-")]


def caminho_processado(cfg: dict, nome: str) -> Path:
    return RAIZ / cfg["dados"]["processed"] / nome


def ler_processado(cfg: dict, nome: str) -> pd.DataFrame:
    caminho = caminho_processado(cfg, nome)
    if not caminho.is_file():
        raise SystemExit(f"[pipeline] {caminho.name} ausente. Rode antes: python -m src.pipeline --etapa dados")
    return pd.read_pickle(caminho)


def gravar_tabela(cfg: dict, tabela: pd.DataFrame, nome: str) -> None:
    pasta = RAIZ / cfg["saidas"]["tabelas"]
    pasta.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(pasta / nome, index=False)


def mesorregioes(cfg: dict) -> dict[str, str]:
    from src.data.carregar import carregar_municipios

    return carregar_municipios(cfg).set_index("CODMUN6")["mesorregiao"].to_dict()


def conferir_vazamento(X: pd.DataFrame, cfg: dict) -> None:
    """Falha se alguma coluna proibida chegar ao modelo (RQ-PRE-02)."""
    from src.data.esquema import ATRIBUTOS, COLUNAS

    proibidas = {c.nome for c in COLUNAS if c.uso in ("descartada", "filtro", "alvo")}
    proibidas |= {"ANO", cfg["dados"]["alvo"]}
    presentes = sorted(set(X.columns) & proibidas)
    if presentes:
        raise SystemExit(f"[pipeline] VAZAMENTO: colunas proibidas nos atributos: {presentes}")
    if set(X.columns) != set(ATRIBUTOS):
        raise SystemExit(f"[pipeline] atributos inesperados: {sorted(set(X.columns) ^ set(ATRIBUTOS))}")


# -------------------------------------------------------------------- etapas


def etapa_dados(cfg: dict) -> None:
    """Brutos -> limpeza -> populacao -> alvo -> split temporal (antes de qualquer fit)."""
    from src.data.carregar import carregar_sinasc
    from src.data.download import sincronizar
    from src.data.esquema import ATRIBUTOS, POR_NOME
    from src.data.preparar import preparar, separar

    if sincronizar(cfg) != 0:
        raise SystemExit("[pipeline] dados brutos diferentes do registro de hashes (ver mensagem acima)")
    preparado = preparar(carregar_sinasc(cfg), cfg)
    desenvolvimento, teste = separar(preparado, cfg)
    caminho_processado(cfg, "").mkdir(parents=True, exist_ok=True)
    desenvolvimento.to_pickle(caminho_processado(cfg, ARQUIVO_DESENVOLVIMENTO))
    teste.to_pickle(caminho_processado(cfg, ARQUIVO_TESTE))

    alvo = cfg["dados"]["alvo"]
    conjuntos = []
    for nome, parte in (("desenvolvimento", desenvolvimento), ("teste temporal", teste)):
        anos = sorted(parte["ANO"].unique())
        conjuntos.append({"conjunto": nome, "anos": f"{anos[0]}–{anos[-1]}" if len(anos) > 1 else str(anos[0]),
                          "registros": len(parte), "baixo_peso": int(parte[alvo].sum()),
                          "pct_baixo_peso": round(100 * parte[alvo].mean(), 2)})
    gravar_tabela(cfg, pd.DataFrame(conjuntos), "tabela-preparacao-conjuntos.csv")

    from src.features.construcao import NUMERICAS

    def tratamento(nome: str) -> str:
        if nome in NUMERICAS:
            return "mediana do treino de cada fold (SimpleImputer)"
        if nome == "CODMUNRES":
            return "município ignorado (260000) vira mesorregião 'ignorado'"
        return "categoria própria 'ignorado' (SimpleImputer constante)"

    ausentes = [{"atributo": nome, "tipo_original": POR_NOME[nome].tipo,
                 "pct_ausente_desenvolvimento": round(100 * desenvolvimento[nome].isna().mean(), 2),
                 "tratamento": tratamento(nome)} for nome in ATRIBUTOS]
    gravar_tabela(cfg, pd.DataFrame(ausentes), "tabela-preparacao-ausentes.csv")
    for linha in conjuntos:
        print(f"[dados] {linha['conjunto']}: {linha['registros']:,} registros, "
              f"{linha['pct_baixo_peso']}% de baixo peso")


def etapa_eda(cfg: dict) -> None:
    """Figuras e tabelas da EDA (so desenvolvimento); explicadas em notebooks/01-eda-baixo-peso.ipynb."""
    from src.evaluation.eda import gerar_todas

    print(f"[eda] {len(gerar_todas(cfg))} figuras em {cfg['saidas']['figuras']}")


def etapa_features(cfg: dict) -> None:
    """Monta o pre-processamento e confere que ele funciona sem vazamento.

    O `fit` abaixo usa so o desenvolvimento e serve apenas para inspecao (lista de
    atributos gerados). Na validacao cruzada (E4/E5) o mesmo Pipeline e reajustado
    no treino de cada fold; o teste (2024) nunca e lido aqui.
    """
    import numpy as np

    from src.features.preprocessamento import construir_preprocessador

    desenvolvimento = ler_processado(cfg, ARQUIVO_DESENVOLVIMENTO)
    anos_fora = set(desenvolvimento["ANO"]) - set(cfg["dados"]["anos_desenvolvimento"])
    if anos_fora:
        raise SystemExit(f"[pipeline] anos fora do desenvolvimento no conjunto de treino: {sorted(anos_fora)}")
    X = desenvolvimento.drop(columns=["ANO", cfg["dados"]["alvo"]])
    conferir_vazamento(X, cfg)

    preprocessador = construir_preprocessador(cfg, mesorregioes(cfg))
    matriz = preprocessador.fit_transform(X)
    if np.isnan(matriz).any():
        raise SystemExit("[pipeline] ainda ha ausentes depois do pre-processamento")
    nomes = preprocessador.named_steps["colunas"].get_feature_names_out()
    atributos = pd.DataFrame({"bloco": [n.split("__", 1)[0] for n in nomes],
                              "atributo": [n.split("__", 1)[1] for n in nomes]})
    gravar_tabela(cfg, atributos, "tabela-preparacao-atributos.csv")
    print(f"[features] {matriz.shape[0]:,} registros x {matriz.shape[1]} atributos depois do pre-processamento "
          f"(sem ausentes; nenhuma coluna proibida)")


def etapa_modelos(cfg: dict) -> None:
    raise NotImplementedError("modelos: baseline e tres familias entram na E4")


def etapa_avaliacao(cfg: dict) -> None:
    raise NotImplementedError("avaliacao: CV repetida e testes estatisticos entram na E5")


ETAPAS = {
    "dados": etapa_dados,
    "eda": etapa_eda,
    "features": etapa_features,
    "modelos": etapa_modelos,
    "avaliacao": etapa_avaliacao,
}


# ---------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pipeline do projeto AV2 (G01).")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--etapa", choices=list(ETAPAS), help="executa apenas uma etapa (default: todas, em ordem)")
    parser.add_argument("--somente-ambiente", action="store_true",
                        help="apenas valida config e grava reports/environment.json")
    args = parser.parse_args(argv)

    cfg = carregar_config(args.config)
    seed = int(os.environ.get("SEED", cfg.get("project", {}).get("seed", 42)))
    fixar_sementes(seed)

    for chave in ("tabelas", "figuras"):
        (RAIZ / cfg["saidas"][chave]).mkdir(parents=True, exist_ok=True)
    registrar_ambiente(cfg, seed, RAIZ / cfg["saidas"]["ambiente"])
    print(f"[pipeline] grupo={cfg['project'].get('grupo')} seed={seed} commit={versao_git()}")

    if args.somente_ambiente:
        print("[pipeline] ambiente registrado; etapas nao executadas")
        return 0

    ordem = [args.etapa] if args.etapa else list(ETAPAS)
    for nome in ordem:
        print(f"[pipeline] etapa: {nome}")
        try:
            ETAPAS[nome](cfg)
        except NotImplementedError as exc:
            if args.etapa:  # pedida explicitamente: falha com codigo proprio
                print(f"[pipeline] etapa pendente: {exc}", file=sys.stderr)
                return 2
            print(f"[pipeline] pendente: {exc}")
    print("[pipeline] concluido")
    return 0


if __name__ == "__main__":
    sys.exit(main())
