#!/usr/bin/env python3
"""Baixa os dados brutos e confere a integridade por SHA-256 (RQ-DAD-02).

Arquivos baixados para `dados.raw` (data/raw/, fora do Git):
  * DNPE{ano}.dbc            -> SINASC, residentes em Pernambuco (DATASUS)
  * ibge-municipios-pe.json  -> municipios de PE com meso/microrregiao (IBGE)

Uso:
    python -m src.data.download --config configs/base.yaml
    python -m src.data.download --config configs/base.yaml --anos 2023 2024
    python -m src.data.download --config configs/base.yaml --registrar

Regras:
  * data/raw/ e imutavel: arquivo existente nunca e sobrescrito;
  * o hash de cada arquivo fica registrado em `dados.fonte.hashes`
    (CSV versionado); hash divergente interrompe a execucao, porque o DATASUS
    republica arquivos de anos antigos e o resultado deixaria de ser
    reproduzivel. Use --registrar apenas depois de decidir aceitar a nova versao.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

from src.config import RAIZ, carregar_config

CAMPOS_REGISTRO = ("arquivo", "bytes", "sha256", "url", "registrado_em")
TENTATIVAS = 3


def sha256(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1 << 20), b""):
            digest.update(bloco)
    return digest.hexdigest()


def baixar(url: str, destino: Path) -> None:
    """Baixa para um arquivo temporario e so renomeia no fim (sem arquivo parcial)."""
    temporario = destino.with_name(destino.name + ".parcial")
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            with urllib.request.urlopen(url, timeout=120) as resposta, temporario.open("wb") as saida:
                shutil.copyfileobj(resposta, saida)
            temporario.rename(destino)
            return
        except OSError as exc:
            temporario.unlink(missing_ok=True)
            if tentativa == TENTATIVAS:
                raise SystemExit(f"[download] falhou apos {TENTATIVAS} tentativas: {url} ({exc})") from exc
            print(f"[download] tentativa {tentativa} falhou ({exc}); repetindo...")
            time.sleep(5 * tentativa)


def ler_registro(caminho: Path) -> dict[str, dict[str, str]]:
    if not caminho.is_file():
        return {}
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return {linha["arquivo"]: linha for linha in csv.DictReader(arquivo)}


def gravar_registro(caminho: Path, registro: dict[str, dict[str, str]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_REGISTRO, lineterminator="\n")
        escritor.writeheader()
        for nome in sorted(registro):
            escritor.writerow({campo: registro[nome][campo] for campo in CAMPOS_REGISTRO})


def alvos_de_download(cfg: dict, anos: list[int]) -> list[tuple[str, str]]:
    fonte = cfg["dados"]["fonte"]
    alvos = [(cfg["dados"]["arquivo"].format(ano=ano), fonte["sinasc_url"].format(ano=ano)) for ano in anos]
    alvos.append((fonte["ibge_arquivo"], fonte["ibge_url"]))
    return alvos


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Baixa e confere os dados brutos (G01).")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--anos", type=int, nargs="+", help="subconjunto de anos (default: dados.anos)")
    parser.add_argument("--registrar", action="store_true",
                        help="aceita e registra hashes novos ou divergentes")
    args = parser.parse_args(argv)

    cfg = carregar_config(args.config)
    anos = args.anos or list(cfg["dados"]["anos"])
    pasta_raw = RAIZ / cfg["dados"]["raw"]
    pasta_raw.mkdir(parents=True, exist_ok=True)
    caminho_registro = RAIZ / cfg["dados"]["fonte"]["hashes"]
    registro = ler_registro(caminho_registro)

    divergentes: list[str] = []
    alterado = False
    for nome, url in alvos_de_download(cfg, anos):
        destino = pasta_raw / nome
        if destino.exists():
            print(f"[download] {nome}: ja existe, nao baixado de novo")
        else:
            print(f"[download] {nome}: baixando {url}")
            baixar(url, destino)
        digest, tamanho = sha256(destino), destino.stat().st_size
        esperado = registro.get(nome)
        if esperado and esperado["sha256"] == digest:
            print(f"[download] {nome}: sha256 confere ({digest[:12]}...)")
            continue
        if esperado and not args.registrar:
            divergentes.append(f"{nome}: esperado {esperado['sha256'][:12]}..., obtido {digest[:12]}...")
            continue
        acao = "atualizado" if esperado else "registrado"
        registro[nome] = {"arquivo": nome, "bytes": str(tamanho), "sha256": digest, "url": url,
                          "registrado_em": date.today().isoformat()}
        alterado = True
        print(f"[download] {nome}: sha256 {acao} ({digest[:12]}...)")

    if alterado:
        gravar_registro(caminho_registro, registro)
        print(f"[download] registro de hashes gravado em {caminho_registro.relative_to(RAIZ)}")
    if divergentes:
        print("[download] ERRO: arquivos diferentes dos registrados:", *divergentes, sep="\n  - ",
              file=sys.stderr)
        print("[download] apague o arquivo em data/raw/ e baixe de novo, ou use --registrar "
              "se a nova versao for aceita (e documente a troca).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
