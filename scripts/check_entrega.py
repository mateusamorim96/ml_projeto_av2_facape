#!/usr/bin/env python3
"""Validador de entrega dos grupos do Projeto AV2 de Machine Learning (FACAPE).

Roda sem dependencias externas (Python 3.10+) e aplica a MESMA regra da CI
(`.github/workflows/validar-entrega.yml`) e do hook `.githooks/pre-commit`.

Uso:
    python3 scripts/check_entrega.py --grupo grupo-03
    python3 scripts/check_entrega.py --grupo g3 --entrega E6
    python3 scripts/check_entrega.py --grupo grupo-03 --entrega E6 --base origin/main
    python3 scripts/check_entrega.py --namespace          # valida todos os grupos
    python3 scripts/check_entrega.py --grupo g3 --strict  # AVISO vira ERRO

Saida: ERRO (bloqueia o PR), AVISO (registrado, nao bloqueia), RESULTADO.
Codigo de saida: 0 = aprovado, 1 = reprovado, 2 = erro de uso.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

GRUPOS_DIR = "grupos"
TEMPLATE_DIR = "_template"
LIMITE_MB = 20

README_OBRIGATORIO = "README.md"

# Estrutura minima acumulativa por entrega (E1..E8).
# Arquivos: caminhos relativos a pasta do grupo. Pastas: minimo de arquivos reais.
MINIMOS: dict[str, dict[str, object]] = {
    "E1": {
        "arquivos": ["docs/proposta.md"],
        "pastas": {},
    },
    "E2": {
        "arquivos": ["docs/dicionario-de-dados.md"],
        "pastas": {},
    },
    "E3": {
        "arquivos": ["src/pipeline.py"],
        "pastas": {"notebooks": 1},
    },
    "E4": {
        "arquivos": ["configs/base.yaml", "experiments/runs.csv"],
        "pastas": {"src/models": 1},
    },
    "E5": {
        "arquivos": [],
        "pastas": {"reports/tables": 1, "reports/figures": 3},
    },
    "E6": {
        "arquivos": ["Dockerfile", "requirements.txt"],
        "pastas": {},
    },
    "E7": {
        "arquivos": ["article/artigo.tex", "article/referencias.bib"],
        "pastas": {"slides": 1},
    },
    "E8": {
        "arquivos": [],
        "pastas": {},
    },
}
ORDEM_ENTREGAS = ("E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8")

# Secoes que o README executivo precisa conter (comparacao sem acento, minuscula).
README_SECOES = {
    "ods": ("ods", "objetivo de desenvolvimento sustent"),
    "decisao": ("decisao", "decisão"),
    "dados": ("dados", "dataset"),
    "reproduzir": ("reproduzir", "reprodução", "reproducao", "como executar"),
    "resultados": ("resultado", "metrica", "métrica"),
    "limitacoes": ("limitac", "limitacões", "limitacoes"),
}

ARQUIVOS_CONSAGRADOS = {
    "README.md",
    "LICENSE",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    "pyproject.toml",
    ".gitignore",
    ".gitkeep",
    ".dockerignore",
}

EXT_DADOS = (
    ".parquet",
    ".feather",
    ".h5",
    ".hdf5",
    ".sqlite",
    ".db",
    ".zip",
    ".7z",
    ".rar",
    ".gz",
    ".tar",
    ".pkl",
    ".joblib",
)
NOMES_SEGREDO = re.compile(
    r"(^|/)(\.env(\..*)?|credentials\.json|client_secret.*\.json|token.*\.json|"
    r"kaggle\.json|secrets\.ya?ml|[^/]*\.pem|[^/]*\.key)$",
    re.IGNORECASE,
)
PADROES_SEGREDO = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"sk-[A-Za-z0-9]{32,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)
RE_GRUPO = re.compile(r"^grupo-(\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*$")
RE_NOME_OK = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
RE_PLACEHOLDER = re.compile(r"\b(preencher|tbd|todo|lorem|xxx)\b", re.IGNORECASE)
RE_PIN = re.compile(r"(==|@\s*https?://|~=|>=)")
RE_FROM = re.compile(r"^\s*FROM\s+(\S+)", re.IGNORECASE | re.MULTILINE)


def sem_acento(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def tem_acento_ou_maiuscula(nome: str) -> bool:
    ascii_norm = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return ascii_norm != nome or nome != nome.lower()


class Relatorio:
    def __init__(self) -> None:
        self.erros: list[str] = []
        self.avisos: list[str] = []

    def erro(self, msg: str) -> None:
        self.erros.append(msg)

    def aviso(self, msg: str) -> None:
        self.avisos.append(msg)

    def imprimir(self, cabecalho: dict[str, str]) -> int:
        for chave, valor in cabecalho.items():
            print(f"{chave}: {valor}")
        if self.avisos:
            print(f"\nAVISO ({len(self.avisos)}):")
            for a in self.avisos:
                print(f"  - {a}")
        if self.erros:
            print(f"\nERRO ({len(self.erros)}):")
            for e in self.erros:
                print(f"  - {e}")
            print("\nRESULTADO: REPROVADO")
            return 1
        print("\nRESULTADO: APROVADO")
        return 0


# ---------------------------------------------------------------- utilidades


def normalizar_grupo(valor: str) -> str:
    valor = valor.strip().lower()
    m = re.fullmatch(r"g?0?(\d{1,2})", valor)
    if m:
        return f"grupo-{int(m.group(1)):02d}"
    return valor.rstrip("/").rstrip("-")


def localizar_pasta(raiz: Path, grupo: str) -> Path | None:
    base = raiz / GRUPOS_DIR
    if not base.is_dir():
        return None
    if grupo.startswith("grupo-") and (base / grupo).is_dir():
        return base / grupo
    candidatos = sorted(
        p for p in base.iterdir() if p.is_dir() and p.name.startswith(grupo + "-")
    )
    if len(candidatos) == 1:
        return candidatos[0]
    if len(candidatos) > 1:
        nomes = ", ".join(c.name for c in candidatos)
        raise ValueError(f"grupo ambiguo '{grupo}': {nomes}")
    return None


def arquivos_do_grupo(pasta: Path) -> list[Path]:
    return sorted(p for p in pasta.rglob("*") if p.is_file())


def contar_reais(pasta: Path, padrao: str | None = None) -> int:
    alvo = pasta / padrao if padrao else pasta
    if not alvo.is_dir():
        return 0
    itens = [p for p in alvo.iterdir() if p.is_file() and p.name not in (".gitkeep", ".DS_Store")]
    return len(itens)


def ler(caminho: Path, limite: int = 400_000) -> str:
    try:
        dados = caminho.read_bytes()[:limite]
        return dados.decode("utf-8", errors="ignore")
    except OSError:
        return ""


# ------------------------------------------------------------------- checagens


def checar_estrutura(pasta: Path, rel: Relatorio, entrega: str | None) -> None:
    if not (pasta / README_OBRIGATORIO).is_file():
        rel.erro(
            f"arquivo obrigatorio ausente: {README_OBRIGATORIO} "
            f"(use docs/templates/README-grupo.md)"
        )
    if not entrega:
        rel.aviso("entrega (E1..E8) nao informada: apenas estrutura-base foi validada")
        return

    indice = ORDEM_ENTREGAS.index(entrega)
    for fase in ORDEM_ENTREGAS[: indice + 1]:
        regra = MINIMOS[fase]
        for arquivo in regra["arquivos"]:  # type: ignore[union-attr]
            if not (pasta / arquivo).is_file():
                rel.erro(f"[{fase}] arquivo obrigatorio ausente: {arquivo}")
        for sub, minimo in regra["pastas"].items():  # type: ignore[union-attr]
            alvo = pasta / sub
            if not alvo.is_dir():
                rel.erro(f"[{fase}] pasta obrigatoria ausente: {sub}/")
                continue
            reais = contar_reais(alvo)
            if reais < minimo:
                rel.erro(
                    f"[{fase}] pasta {sub}/ tem {reais} arquivo(s); minimo {minimo}"
                )


def checar_nomes(pasta: Path, rel: Relatorio) -> None:
    for arq in arquivos_do_grupo(pasta):
        nome = arq.name
        relativo = arq.relative_to(pasta.parent)
        if nome in ARQUIVOS_CONSAGRADOS or nome.endswith(".gitkeep"):
            continue
        if tem_acento_ou_maiuscula(nome):
            rel.erro(f"nome com maiuscula ou acento (use kebab-case): {relativo}")
            continue
        if " " in nome:
            rel.erro(f"nome com espaco: {relativo}")
        elif not RE_NOME_OK.match(nome):
            rel.erro(f"nome com caractere invalido (use [a-z0-9._-]): {relativo}")
        if "__pycache__" in str(relativo) or nome.endswith((".pyc", ".ipynb_checkpoints")):
            rel.erro(f"arquivo gerado que nao deve ser versionado: {relativo}")


def checar_dados(pasta: Path, rel: Relatorio) -> None:
    for arq in arquivos_do_grupo(pasta):
        relativo = arq.relative_to(pasta.parent)
        partes = relativo.parts
        em_raw = "data" in partes and "raw" in partes
        if em_raw and arq.name != ".gitkeep":
            rel.erro(f"dado bruto versionado (data/raw/ nao vai para o Git): {relativo}")
            continue
        if arq.suffix.lower() in EXT_DADOS:
            rel.erro(f"arquivo de dados/binario nao permitido no Git: {relativo}")
        tamanho = arq.stat().st_size
        if tamanho > LIMITE_MB * 1024 * 1024:
            rel.erro(
                f"arquivo maior que {LIMITE_MB} MB: {relativo} "
                f"({tamanho / (1024 * 1024):.1f} MB)"
            )


def checar_segredos(pasta: Path, rel: Relatorio) -> None:
    for arq in arquivos_do_grupo(pasta):
        relativo = arq.relative_to(pasta.parent)
        if NOMES_SEGREDO.search(str(relativo)):
            rel.erro(f"arquivo de credencial/segredo: {relativo}")
            continue
        if arq.stat().st_size > 1_000_000 or arq.suffix.lower() not in (
            ".py",
            ".md",
            ".txt",
            ".yaml",
            ".yml",
            ".json",
            ".toml",
            ".cfg",
            ".ini",
            ".env",
            ".ipynb",
        ):
            continue
        texto = ler(arq)
        for padrao in PADROES_SEGREDO:
            if padrao.search(texto):
                rel.erro(f"possivel segredo em {relativo}: {padrao.pattern[:24]}...")
                break


def checar_readme(pasta: Path, rel: Relatorio, entrega: str | None) -> None:
    caminho = pasta / README_OBRIGATORIO
    if not caminho.is_file():
        return
    texto = sem_acento(ler(caminho, 200_000))
    ausentes = [
        nome
        for nome, chaves in README_SECOES.items()
        if not any(sem_acento(c) in texto for c in chaves)
    ]
    if ausentes:
        msg = "README executivo sem as secoes: " + ", ".join(ausentes)
        if entrega in ("E6", "E7", "E8"):
            rel.erro(msg + " (obrigatorio a partir da E6)")
        else:
            rel.aviso(msg)
    if len(texto.split()) < 150 and entrega in ("E6", "E7", "E8"):
        rel.erro("README executivo muito curto (< 150 palavras) para a entrega atual")


def checar_requirements(pasta: Path, rel: Relatorio, entrega: str | None) -> None:
    caminho = pasta / "requirements.txt"
    if not caminho.is_file():
        return
    linhas = [
        ln.strip()
        for ln in ler(caminho, 100_000).splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    if not linhas:
        rel.erro("requirements.txt vazio")
        return
    sem_pin = [ln for ln in linhas if not ln.startswith("-") and not RE_PIN.search(ln)]
    if sem_pin:
        exemplo = sem_pin[0][:40]
        rel.erro(
            f"requirements.txt sem versao fixa ({len(sem_pin)} linha(s), ex.: '{exemplo}'). "
            "Use 'pacote==x.y.z'"
        )
    if any(ln.startswith("-") for ln in linhas):
        rel.aviso("requirements.txt usa opcoes (-r/--index-url); confirme que a imagem resolve")


def checar_dockerfile(pasta: Path, rel: Relatorio, entrega: str | None) -> None:
    caminho = pasta / "Dockerfile"
    if not caminho.is_file():
        return
    texto = ler(caminho, 100_000)
    bases = RE_FROM.findall(texto)
    if not bases:
        rel.erro("Dockerfile sem instrucao FROM")
    for base in bases:
        if base.endswith(":latest"):
            rel.erro(f"Dockerfile usa ':latest' ({base}); fixe a tag")
        elif ":" not in base and "@sha256" not in base:
            rel.erro(f"Dockerfile com imagem sem tag ({base}); use python:3.11-slim")
        elif "@sha256" not in base:
            rel.aviso(f"Dockerfile sem digest em FROM ({base}); recomendado para reprodutibilidade")
    if not re.search(r"^\s*(CMD|ENTRYPOINT)\s", texto, re.IGNORECASE | re.MULTILINE):
        rel.erro("Dockerfile sem CMD/ENTRYPOINT: nao executa nada")
    if "requirements.txt" not in texto:
        rel.aviso("Dockerfile nao instala requirements.txt")


def checar_experimentos(pasta: Path, rel: Relatorio, entrega: str | None) -> None:
    caminho = pasta / "experiments" / "runs.csv"
    if not caminho.is_file():
        return
    if entrega is None or ORDEM_ENTREGAS.index(entrega) < ORDEM_ENTREGAS.index("E4"):
        return
    linhas = [ln for ln in ler(caminho).splitlines() if ln.strip()]
    if len(linhas) < 2:
        rel.erro("experiments/runs.csv sem registros (esperado cabecalho + linhas)")
        return
    if len(linhas) < 4:
        rel.erro(
            f"experiments/runs.csv com {len(linhas) - 1} registro(s); "
            "a E4+ exige no minimo 3 execucoes (baseline + 2)"
        )


def checar_artigo(pasta: Path, rel: Relatorio, entrega: str | None) -> None:
    caminho = pasta / "article" / "artigo.tex"
    if not caminho.is_file():
        return
    texto = sem_acento(ler(caminho, 300_000))
    if "\\documentclass" not in texto:
        rel.erro("article/artigo.tex sem \\documentclass (nao compila)")
    secoes = ("introdu", "metod", "resultado", "conclus")
    faltando = [s for s in secoes if s not in texto]
    if faltando:
        rel.erro("artigo fora do padrao IMRaD; faltam secoes: " + ", ".join(faltando))


def checar_placeholders(pasta: Path, rel: Relatorio, entrega: str | None) -> None:
    limite = entrega in ("E6", "E7", "E8")
    for arq in arquivos_do_grupo(pasta):
        if arq.suffix.lower() not in (".md", ".yaml", ".yml"):
            continue
        texto = ler(arq, 200_000)
        achados = sorted({m.group(0).lower() for m in RE_PLACEHOLDER.finditer(texto)})
        if not achados:
            continue
        msg = f"placeholder em {arq.relative_to(pasta.parent)}: {', '.join(achados)}"
        rel.erro(msg) if limite else rel.aviso(msg)


def checar_escopo(pasta: Path, raiz: Path, base: str, rel: Relatorio) -> None:
    cmd = ["git", "-C", str(raiz), "diff", "--name-only", f"{base}...HEAD"]
    try:
        saida = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        rel.aviso(f"nao foi possivel comparar com {base}: {exc}")
        return
    if saida.returncode != 0:
        rel.aviso(
            f"git diff contra '{base}' falhou ({saida.stderr.strip()[:120]}); "
            "rode 'git fetch' e confira a branch base"
        )
        return
    permitido = str(pasta.relative_to(raiz)) + "/"
    for linha in saida.stdout.splitlines():
        caminho = linha.strip()
        if not caminho:
            continue
        if not (caminho + "/").startswith(permitido) and not caminho.startswith(permitido):
            rel.erro(f"arquivo alterado FORA da pasta do grupo ({permitido}): {caminho}")


def checar_namespace(raiz: Path, rel: Relatorio, atual: Path | None = None) -> None:
    base = raiz / GRUPOS_DIR
    if not base.is_dir():
        rel.erro(f"pasta '{GRUPOS_DIR}/' nao encontrada")
        return
    pastas = sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith("_"))
    if not pastas and atual is None:
        rel.aviso("nenhuma pasta de grupo criada ainda")
    vistos: dict[str, str] = {}
    for pasta in pastas:
        m = RE_GRUPO.match(pasta.name)
        if not m:
            # Na validacao de um grupo isolado, o nome das outras pastas e
            # responsabilidade do grupo dono -> fica para o modo --namespace.
            if atual is None:
                rel.erro(
                    f"pasta do grupo fora do padrao 'grupo-NN-slug-kebab-case': {pasta.name}"
                )
            continue
        numero = m.group(1)
        if numero in vistos:
            if atual is None or pasta == atual or vistos[numero] == atual.name:
                rel.erro(
                    f"numero de grupo duplicado: '{numero}' usado por "
                    f"{vistos[numero]} e {pasta.name}"
                )
        else:
            vistos[numero] = pasta.name
            if atual is None and not (pasta / README_OBRIGATORIO).is_file():
                rel.erro(f"pasta sem README.md: {pasta.name}")


# ------------------------------------------------------------------------ main


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida a entrega de um grupo do Projeto AV2 de Machine Learning."
    )
    parser.add_argument("--grupo", help="ex.: grupo-03, g3 ou 03")
    parser.add_argument("--raiz", default=".", help="raiz do repositorio (default: .)")
    parser.add_argument(
        "--entrega",
        choices=ORDEM_ENTREGAS,
        help="entrega avaliada (E1..E8); aplica os minimos acumulados",
    )
    parser.add_argument(
        "--base",
        help="base para checar escopo (ex.: origin/main). Sem isso o escopo nao e verificado.",
    )
    parser.add_argument(
        "--namespace",
        action="store_true",
        help="valida todas as pastas de grupo (nome, numero unico, README)",
    )
    parser.add_argument("--strict", action="store_true", help="trata AVISO como ERRO")
    args = parser.parse_args()

    raiz = Path(args.raiz).resolve()
    rel = Relatorio()

    if args.namespace:
        checar_namespace(raiz, rel)
        codigo = rel.imprimir({"modo": "namespace", "raiz": str(raiz)})
        if codigo == 0 and args.strict and rel.avisos:
            print("RESULTADO (--strict): REPROVADO por AVISOs")
            return 1
        return codigo

    if not args.grupo:
        parser.error("informe --grupo (ou use --namespace)")

    if not (raiz / GRUPOS_DIR).is_dir():
        print(f"ERRO: nao encontrei '{GRUPOS_DIR}/' em {raiz}", file=sys.stderr)
        return 2

    chave = normalizar_grupo(args.grupo)
    try:
        pasta = localizar_pasta(raiz, chave)
    except ValueError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    if pasta is None:
        existentes = sorted(
            p.name for p in (raiz / GRUPOS_DIR).iterdir() if p.is_dir()
        )
        print(f"ERRO: grupo '{args.grupo}' nao encontrado.", file=sys.stderr)
        print("Disponiveis: " + (", ".join(existentes) or "nenhuma pasta"), file=sys.stderr)
        print(
            "Crie com: python3 scripts/novo_grupo.py --numero NN --tema slug-do-tema",
            file=sys.stderr,
        )
        return 2

    if not RE_GRUPO.match(pasta.name):
        print(
            f"ERRO: pasta '{pasta.name}' fora do padrao 'grupo-NN-slug-kebab-case'",
            file=sys.stderr,
        )
        return 2

    checar_estrutura(pasta, rel, args.entrega)
    checar_nomes(pasta, rel)
    checar_dados(pasta, rel)
    checar_segredos(pasta, rel)
    checar_readme(pasta, rel, args.entrega)
    checar_requirements(pasta, rel, args.entrega)
    checar_dockerfile(pasta, rel, args.entrega)
    checar_experimentos(pasta, rel, args.entrega)
    checar_artigo(pasta, rel, args.entrega)
    checar_placeholders(pasta, rel, args.entrega)
    checar_namespace(raiz, rel, atual=pasta)
    if args.base:
        checar_escopo(pasta, raiz, args.base, rel)

    codigo = rel.imprimir(
        {
            "grupo": pasta.name,
            "pasta": str(pasta.relative_to(raiz)),
            "entrega": args.entrega or "nao informada",
        }
    )
    if codigo == 0 and args.strict and rel.avisos:
        print("RESULTADO (--strict): REPROVADO por AVISOs")
        return 1
    return codigo


if __name__ == "__main__":
    sys.exit(main())
