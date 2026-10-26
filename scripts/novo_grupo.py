#!/usr/bin/env python3
"""Cria a pasta de um grupo a partir de `grupos/_template/`.

Regras que o script garante:
  * nome no padrao `grupo-NN-slug-em-kebab-case` (NN com dois digitos);
  * `NN` nunca duplicado (dois grupos nao colidem no mesmo namespace);
  * substituicao dos marcadores `grupo-XX` e `GXX` em todos os arquivos de texto.

Uso:
    python3 scripts/novo_grupo.py --numero 3 --tema saneamento-ana
    python3 scripts/novo_grupo.py --numero 7 --tema saude-triagem --raiz .

Saida: caminho da pasta criada e proximos passos. Codigo 0 = criado,
1 = recusado, 2 = erro de uso.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import unicodedata
from pathlib import Path

GRUPOS_DIR = "grupos"
TEMPLATE = "_template"
RE_SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
EXT_TEXTO = {
    ".md",
    ".py",
    ".yaml",
    ".yml",
    ".toml",
    ".cfg",
    ".ini",
    ".tex",
    ".bib",
    ".csv",
    ".json",
    ".txt",
    ".sh",
    ".gitignore",
    "",
}
NOMES_TEXTO = {"Makefile", "Dockerfile", "docker-compose.yml", ".gitignore", ".dockerignore"}


def normalizar_slug(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return re.sub(r"-{2,}", "-", texto).strip("-")


def e_texto(caminho: Path) -> bool:
    if caminho.name in NOMES_TEXTO:
        return True
    sufixo = caminho.suffix.lower()
    return sufixo in EXT_TEXTO


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cria grupos/grupo-NN-slug/ a partir de grupos/_template/."
    )
    parser.add_argument("--numero", required=True, help="numero do grupo (1..99)")
    parser.add_argument("--tema", required=True, help="slug do tema, ex.: saneamento-ana")
    parser.add_argument("--raiz", default=".", help="raiz do repositorio (default: .)")
    args = parser.parse_args()

    raiz = Path(args.raiz).resolve()
    base = raiz / GRUPOS_DIR
    template = base / TEMPLATE

    if not template.is_dir():
        print(f"ERRO: template ausente em {template}", file=sys.stderr)
        return 2

    try:
        numero = int(args.numero)
    except ValueError:
        print("ERRO: --numero precisa ser inteiro (ex.: 3)", file=sys.stderr)
        return 2
    if not 1 <= numero <= 99:
        print("ERRO: --numero deve estar entre 1 e 99", file=sys.stderr)
        return 2

    slug = normalizar_slug(args.tema)
    if not RE_SLUG.match(slug):
        print(
            f"ERRO: tema invalido apos normalizacao ('{slug}'). "
            "Use letras minusculas, numeros e hifens.",
            file=sys.stderr,
        )
        return 2

    nn = f"{numero:02d}"
    nome = f"grupo-{nn}-{slug}"
    destino = base / nome

    ocupados = sorted(p.name for p in base.iterdir() if p.is_dir() and p.name.startswith(f"grupo-{nn}-"))
    if ocupados:
        print(
            f"ERRO: o numero {nn} ja esta em uso por: {', '.join(ocupados)}.\n"
            "O numero do grupo e um namespace unico: combine outro numero com o professor "
            "(veja grupos/README.md).",
            file=sys.stderr,
        )
        return 1
    if destino.exists():
        print(f"ERRO: {destino} ja existe", file=sys.stderr)
        return 1

    shutil.copytree(template, destino)
    gxx = f"G{nn}"
    alterados = 0
    for arquivo in sorted(destino.rglob("*")):
        if not arquivo.is_file() or not e_texto(arquivo):
            continue
        try:
            conteudo = arquivo.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        novo = conteudo.replace("grupo-XX", nome).replace("GXX", gxx)
        if novo != conteudo:
            arquivo.write_text(novo, encoding="utf-8")
            alterados += 1

    print(f"OK: pasta criada em {destino.relative_to(raiz)}")
    print(f"    marcadores substituidos em {alterados} arquivo(s): grupo-XX -> {nome}, GXX -> {gxx}")
    print("\nProximos passos:")
    print(f"  1. git checkout -b grupo-{nn}/entrega-e1")
    print(f"  2. preencha {nome}/README.md e {nome}/docs/proposta.md")
    print(f"  3. python3 scripts/check_entrega.py --grupo grupo-{nn} --entrega E1")
    print(f"  4. git add {nome} && git commit -m \"[{gxx}] feat: estrutura inicial do grupo\"")
    print("  5. avise o professor do codigo escolhido (issue 'Entrega de Grupo')")
    return 0


if __name__ == "__main__":
    sys.exit(main())
