"""Leitura dos arquivos brutos (somente leitura: nada e gravado em data/raw/)."""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import pandas as pd

from src.config import RAIZ

# Incrementar sempre que ler_dbc mudar: invalida caches gerados pela versao anterior.
VERSAO_LEITURA = 1


def ler_dbc(caminho: Path) -> pd.DataFrame:
    """Le um .dbc do DATASUS como texto (todas as colunas do SINASC sao 'Caracter').

    O .dbc e expandido para um .dbf em pasta temporaria, fora de data/raw/.
    Campos vazios viram <NA>; os codigos de 'ignorado' (9, 99) sao mantidos,
    porque a auditoria precisa distingui-los de ausencia.
    """
    from dbfread import DBF
    from pyreaddbc import dbc2dbf

    with tempfile.TemporaryDirectory() as pasta_tmp:
        dbf = Path(pasta_tmp) / f"{caminho.stem}.dbf"
        dbc2dbf(str(caminho), str(dbf))
        registros = DBF(str(dbf), encoding="latin-1", char_decode_errors="replace")
        df = pd.DataFrame(iter(registros))
    df.columns = [c.upper() for c in df.columns]  # 'contador' vem minusculo em 2015/2017
    df = df.astype("string").apply(lambda coluna: coluna.str.strip())
    return df.replace("", pd.NA)


def _chave_cache(cfg: dict, anos: list[int]) -> str:
    """Chave ligada aos hashes registrados: arquivo bruto novo invalida o cache."""
    from src.data.download import ler_registro

    registro = ler_registro(RAIZ / cfg["dados"]["fonte"]["hashes"])
    digest = hashlib.sha256(f"leitura-v{VERSAO_LEITURA};".encode())
    for ano in anos:
        nome = cfg["dados"]["arquivo"].format(ano=ano)
        digest.update(f"{nome}:{registro.get(nome, {}).get('sha256', 'sem-hash')};".encode())
    return digest.hexdigest()[:16]


def carregar_sinasc(cfg: dict, anos: list[int] | None = None, usar_cache: bool = True) -> pd.DataFrame:
    """Concatena os anos pedidos e acrescenta a coluna ANO (do nome do arquivo).

    Ler os .dbc leva minutos; a leitura fica em cache em `dados.processed`
    (fora do Git), com chave derivada dos hashes dos arquivos brutos.
    """
    anos = sorted(anos or cfg["dados"]["anos"])
    pasta_raw = RAIZ / cfg["dados"]["raw"]
    cache = RAIZ / cfg["dados"]["processed"] / f"cache-sinasc-{anos[0]}-{anos[-1]}-{_chave_cache(cfg, anos)}.pkl"
    if usar_cache and cache.is_file():
        print(f"[carregar] usando cache {cache.name}")
        return pd.read_pickle(cache)
    partes = []
    for ano in anos:
        caminho = pasta_raw / cfg["dados"]["arquivo"].format(ano=ano)
        if not caminho.is_file():
            raise SystemExit(f"Arquivo ausente: {caminho}. Rode: python -m src.data.download")
        print(f"[carregar] lendo {caminho.name}")
        df = ler_dbc(caminho)
        df.insert(0, "ANO", ano)
        partes.append(df)
    df = pd.concat(partes, ignore_index=True)
    if usar_cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        df.to_pickle(cache)
    return df


def carregar_municipios(cfg: dict) -> pd.DataFrame:
    """Municipios de PE (IBGE): codigo de 6 digitos -> nome, micro e mesorregiao."""
    caminho = RAIZ / cfg["dados"]["raw"] / cfg["dados"]["fonte"]["ibge_arquivo"]
    if not caminho.is_file():
        raise SystemExit(f"Arquivo ausente: {caminho}. Rode: python -m src.data.download")
    itens = json.loads(caminho.read_text(encoding="utf-8"))
    linhas = []
    for item in itens:
        micro = item.get("microrregiao") or {}
        meso = micro.get("mesorregiao") or {}
        imediata = item.get("regiao-imediata") or {}
        linhas.append({
            "CODMUN6": str(item["id"])[:6],
            "municipio": item["nome"],
            "microrregiao": micro.get("nome"),
            "mesorregiao": meso.get("nome"),
            "regiao_imediata": imediata.get("nome"),
        })
    return pd.DataFrame(linhas)
