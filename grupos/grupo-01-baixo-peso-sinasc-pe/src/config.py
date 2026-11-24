"""Configuracao compartilhada: raiz do projeto e leitura do YAML."""
from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def carregar_config(caminho: Path | str) -> dict:
    """Le o YAML de configuracao (dependencia: pyyaml)."""
    try:
        import yaml
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise SystemExit("Falta pyyaml. Rode: pip install -r requirements.txt") from exc
    caminho = Path(caminho)
    if not caminho.is_absolute():
        caminho = RAIZ / caminho
    if not caminho.is_file():
        raise SystemExit(f"Config nao encontrada: {caminho}")
    with caminho.open(encoding="utf-8") as arquivo:
        return yaml.safe_load(arquivo)
