#!/usr/bin/env python3
"""Roda o validador do professor sobre uma copia limpa do repositorio.

`scripts/check_entrega.py` varre todos os arquivos no disco (rglob), inclusive
os ignorados pelo Git (.venv/, data/raw/, cache em data/processed/). Este script
copia para uma pasta temporaria apenas o que iria para o Git (arquivos
rastreados + novos nao ignorados) e roda o validador la -- o mesmo que a CI ve.

Uso (a partir da pasta do grupo):
    python3 tools/validar_limpo.py --entrega E2
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PASTA_GRUPO = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--entrega", required=True, help="E1..E8")
    args = parser.parse_args()

    raiz = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=PASTA_GRUPO,
                               capture_output=True, text=True, check=True).stdout.strip())
    listagem = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                              cwd=raiz, capture_output=True, check=True).stdout
    arquivos = [Path(p) for p in listagem.decode().split("\0") if p]

    with tempfile.TemporaryDirectory(prefix="validar-limpo-") as tmp:
        destino = Path(tmp)
        for relativo in arquivos:
            origem = raiz / relativo
            if not origem.is_file():  # rastreado mas apagado no working tree
                continue
            (destino / relativo).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, destino / relativo)
        print(f"[validar-limpo] {len(arquivos)} arquivos copiados para a validação")
        grupo = PASTA_GRUPO.name.split("-")[0] + "-" + PASTA_GRUPO.name.split("-")[1]
        return subprocess.run([sys.executable, "scripts/check_entrega.py", "--grupo", grupo,
                               "--entrega", args.entrega], cwd=destino).returncode


if __name__ == "__main__":
    sys.exit(main())
