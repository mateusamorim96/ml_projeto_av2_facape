#!/usr/bin/env python3
"""Auditoria do dataset (E2): gera as tabelas do dicionario de dados.

Uso:
    python -m src.data.auditoria --config configs/base.yaml

Saidas:
  * reports/tables/e2-*.csv  -> tabelas em formato de maquina;
  * docs/dicionario-de-dados.md -> os blocos entre marcadores
    `<!-- auditoria:NOME:inicio -->` e `<!-- auditoria:NOME:fim -->` sao
    reescritos a cada execucao. Nenhum numero do dicionario e digitado a mao.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

from src.config import RAIZ, carregar_config
from src.data.carregar import carregar_municipios, carregar_sinasc
from src.data.download import ler_registro
from src.data.esquema import COLUNAS, POR_NOME, Coluna

DICIONARIO = RAIZ / "docs" / "dicionario-de-dados.md"
INTERNAS = ("CONTADOR", "NUMEROLOTE", "DTCADASTRO", "DTRECEBIM", "DTRECORIGA", "DIFDATA",
            "VERSAOSIST", "ORIGEM", "STDNEPIDEM", "STDNNOVA", "CODPAISRES")
PESO_PLAUSIVEL = (300, 6500)  # g; fora disso o registro e tratado como erro de digitacao
IDADE_PLAUSIVEL = (10, 55)    # anos
MUNICIPIO_IGNORADO = "260000"
CELULA_MINIMA = 10            # cruzamentos com menos registros nao sao publicados


# ------------------------------------------------------------------ formatacao

def fmt_int(valor: float) -> str:
    return f"{int(valor):,}".replace(",", ".")


def fmt_pct(valor: float, casas: int = 1) -> str:
    return f"{valor:.{casas}f}".replace(".", ",") + "%"


def tabela_md(df: pd.DataFrame) -> str:
    cabecalho = "| " + " | ".join(map(str, df.columns)) + " |"
    separador = "| " + " | ".join("---" for _ in df.columns) + " |"
    linhas = ["| " + " | ".join(str(v).replace("|", "/") for v in linha) + " |"
              for linha in df.itertuples(index=False)]
    return "\n".join([cabecalho, separador, *linhas])


def atualizar_blocos(caminho: Path, blocos: dict[str, str]) -> None:
    texto = caminho.read_text(encoding="utf-8")
    for nome, conteudo in blocos.items():
        padrao = re.compile(
            rf"(<!-- auditoria:{nome}:inicio -->).*?(<!-- auditoria:{nome}:fim -->)", re.DOTALL)
        if not padrao.search(texto):
            raise SystemExit(f"Marcador 'auditoria:{nome}' ausente em {caminho.name}")
        texto = padrao.sub(lambda m, c=conteudo: f"{m.group(1)}\n{c}\n{m.group(2)}", texto)
    caminho.write_text(texto, encoding="utf-8")


# --------------------------------------------------------------------- calculo

def peso_numerico(df: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(df["PESO"], errors="coerce")


def ausente_ou_ignorado(serie: pd.Series, coluna: Coluna | None) -> pd.Series:
    ignorado = serie.isin(coluna.ignorado) if coluna and coluna.ignorado else False
    return serie.isna() | ignorado


def tabela_arquivos(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    registro = ler_registro(RAIZ / cfg["dados"]["fonte"]["hashes"])
    linhas = []
    for ano, grupo in df.groupby("ANO"):
        nome = cfg["dados"]["arquivo"].format(ano=ano)
        info = registro.get(nome, {})
        colunas_com_dado = int(grupo.drop(columns="ANO").notna().any().sum())
        linhas.append({"arquivo": nome, "bytes": fmt_int(int(info.get("bytes", 0))),
                       "registros": fmt_int(len(grupo)), "colunas com dado": colunas_com_dado,
                       "sha256": f"`{info.get('sha256', 'sem registro')}`"})
    return pd.DataFrame(linhas)


def tabela_resumo_anos(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    local = cfg["dados"]["municipio_local"]
    limiar = cfg["dados"]["limiar_peso_g"]
    peso = peso_numerico(df)
    valido = peso.between(*PESO_PLAUSIVEL)
    linhas = []
    for ano in sorted(df["ANO"].unique()):
        no_ano = df["ANO"] == ano
        base = no_ano & valido
        baixo = base & (peso < limiar)
        loc = base & (df["CODMUNRES"] == local)

        def falta(col: str) -> str:
            return fmt_pct(100 * ausente_ou_ignorado(df.loc[no_ano, col], POR_NOME[col]).mean())

        linhas.append({
            "ano": ano,
            "registros": fmt_int(no_ano.sum()),
            "peso válido": fmt_int(base.sum()),
            "baixo peso": fmt_int(baixo.sum()),
            "% baixo peso": fmt_pct(100 * baixo.sum() / base.sum(), 2),
            "Petrolina": fmt_int(loc.sum()),
            "% baixo peso Petrolina": fmt_pct(100 * (loc & (peso < limiar)).sum() / loc.sum(), 2),
            "MESPRENAT aus./ign.": falta("MESPRENAT"),
            "ESCMAE2010 aus./ign.": falta("ESCMAE2010"),
            "RACACORMAE aus.": falta("RACACORMAE"),
            "CODOCUPMAE aus.": falta("CODOCUPMAE"),
        })
    return pd.DataFrame(linhas)


def faixa_observada(serie: pd.Series, coluna: Coluna) -> str:
    valores = serie.dropna()
    if coluna.ignorado:
        valores = valores[~valores.isin(coluna.ignorado)]
    if valores.empty:
        return "sem dado"
    if coluna.tipo == "numerica":
        numeros = pd.to_numeric(valores, errors="coerce").dropna()
        if numeros.empty:
            return "não numérico"
        return f"{fmt_int(numeros.min())}–{fmt_int(numeros.max())}"
    if coluna.tipo == "data":
        return "ddmmaaaa"
    distintos = sorted(valores.unique())
    if len(distintos) <= 12:
        return ", ".join(distintos)
    return f"{fmt_int(len(distintos))} códigos"


def tabela_variaveis(df: pd.DataFrame) -> pd.DataFrame:
    ordem_uso = {"alvo": 0, "atributo": 1, "subgrupo": 2, "descartada": 3}
    linhas = []
    for coluna in sorted(COLUNAS, key=lambda c: ordem_uso[c.uso]):
        if coluna.nome not in df.columns:
            linhas.append({"coluna": coluna.nome, "tipo": coluna.tipo, "unidade": coluna.unidade,
                           "faixa observada": "ausente nos arquivos", "% nulos": "—",
                           "% ignorado": "—", "descrição": coluna.descricao, "uso": coluna.uso,
                           "motivo / observação": coluna.motivo})
            continue
        serie = df[coluna.nome]
        nulos = 100 * serie.isna().mean()
        ignorados = 100 * serie.isin(coluna.ignorado).mean() if coluna.ignorado else 0.0
        linhas.append({
            "coluna": f"`{coluna.nome}`",
            "tipo": coluna.tipo,
            "unidade": coluna.unidade,
            "faixa observada": faixa_observada(serie, coluna),
            "% nulos": fmt_pct(nulos),
            "% ignorado": fmt_pct(ignorados) if coluna.ignorado else "—",
            "descrição": coluna.descricao,
            "uso": coluna.uso,
            "motivo / observação": coluna.motivo,
        })
    nao_documentadas = [c for c in df.columns if c != "ANO" and c not in POR_NOME]
    for nome in nao_documentadas:
        linhas.append({"coluna": f"`{nome}`", "tipo": "?", "unidade": "?", "faixa observada": "?",
                       "% nulos": fmt_pct(100 * df[nome].isna().mean()), "% ignorado": "—",
                       "descrição": "não documentada no dicionário oficial", "uso": "descartada",
                       "motivo / observação": "sem documentação"})
    return pd.DataFrame(linhas)


def tabela_qualidade(df: pd.DataFrame, cfg: dict, municipios: pd.DataFrame) -> pd.DataFrame:
    peso = peso_numerico(df)
    idade = pd.to_numeric(df["IDADEMAE"].where(df["IDADEMAE"] != "99"), errors="coerce")
    qtd = ["QTDGESTANT", "QTDPARTNOR", "QTDPARTCES", "QTDFILVIVO", "QTDFILMORT"]
    qtd_num = df[qtd].apply(lambda s: pd.to_numeric(s.where(s != "99"), errors="coerce"))
    chave = [c for c in df.columns if c not in INTERNAS]
    duplicadas = int(df.duplicated(subset=chave).sum())
    sem_municipio = int((~df["CODMUNRES"].isin(municipios["CODMUN6"])).sum())
    mes = df["MESPRENAT"]
    mes_invalido = int((mes.notna() & ~mes.isin([f"{m:02d}" for m in range(1, 10)] + ["99"])).sum())
    paridade_incoerente = int(((df["PARIDADE"] == "0") & (qtd_num["QTDFILVIVO"] > 0)).sum())
    total = len(df)

    def linha(item: str, n: int, acao: str) -> dict:
        return {"item verificado": item, "registros": fmt_int(n), "% do total": fmt_pct(100 * n / total, 2),
                "ação (E3)": acao}

    return pd.DataFrame([
        linha("duplicatas (todas as colunas, exceto as internas do sistema)", duplicadas,
              "remover a cópia (iguais até em hora e peso do nascimento: DN digitada em duplicidade)"),
        linha("`PESO` ausente ou não numérico", int(peso.isna().sum()), "excluir (alvo indefinido)"),
        linha(f"`PESO` fora de {PESO_PLAUSIVEL[0]}–{PESO_PLAUSIVEL[1]} g", int((peso.notna() & ~peso.between(
            *PESO_PLAUSIVEL)).sum()), "excluir (provável erro de digitação)"),
        linha("`IDADEMAE` ausente ou ignorada (99)", int(idade.isna().sum()), "imputar dentro do pipeline"),
        linha(f"`IDADEMAE` fora de {IDADE_PLAUSIVEL[0]}–{IDADE_PLAUSIVEL[1]} anos",
              int((idade.notna() & ~idade.between(*IDADE_PLAUSIVEL)).sum()), "tratar como ausente"),
        linha("histórico obstétrico (`QTD*`) com valor > 20", int((qtd_num > 20).any(axis=1).sum()),
              "tratar como ausente"),
        linha("`MESPRENAT` com código fora de 01–09/99", mes_invalido, "tratar como ausente"),
        linha("`PARIDADE` = nulípara com filhos vivos > 0", paridade_incoerente,
              "manter; registrar como inconsistência de preenchimento"),
        linha(f"`CODMUNRES` = {MUNICIPIO_IGNORADO} (município ignorado) ou sem par no IBGE", sem_municipio,
              "região = 'ignorada'"),
    ])


def tabela_subgrupos(df: pd.DataFrame, cfg: dict, municipios: pd.DataFrame) -> pd.DataFrame:
    limiar = cfg["dados"]["limiar_peso_g"]
    peso = peso_numerico(df)
    base = df[peso.between(*PESO_PLAUSIVEL)].copy()
    base["baixo_peso"] = peso[base.index] < limiar
    raca = {"1": "branca", "2": "preta", "3": "amarela", "4": "parda", "5": "indígena"}
    idade = pd.to_numeric(base["IDADEMAE"].where(base["IDADEMAE"] != "99"), errors="coerce")
    faixas = pd.cut(idade, bins=[0, 19, 34, 200], labels=["até 19 anos", "20–34 anos", "35 anos ou mais"])
    meso = base["CODMUNRES"].map(municipios.set_index("CODMUN6")["mesorregiao"])
    grupos = {
        "raça/cor da mãe": base["RACACORMAE"].map(raca).fillna("ignorada"),
        "idade da mãe": faixas.astype("string").fillna("ignorada"),
        "mesorregião de residência": meso.fillna("ignorada"),
        "município de residência": base["CODMUNRES"].eq(cfg["dados"]["municipio_local"]).map(
            {True: "Petrolina", False: "demais municípios"}),
    }
    linhas = []
    for nome, rotulos in grupos.items():
        resumo = base.groupby(rotulos.values)["baixo_peso"].agg(["size", "sum"])
        for categoria, (n, positivos) in resumo.sort_values("size", ascending=False).iterrows():
            if n < CELULA_MINIMA:  # supressao de celula pequena (LGPD)
                linhas.append({"subgrupo": nome, "categoria": categoria, "registros": f"< {CELULA_MINIMA}",
                               "% da base": "—", "baixo peso": "—", "% baixo peso": "—"})
                continue
            linhas.append({"subgrupo": nome, "categoria": categoria, "registros": fmt_int(n),
                           "% da base": fmt_pct(100 * n / len(base)),
                           "baixo peso": fmt_int(positivos) if positivos >= CELULA_MINIMA else f"< {CELULA_MINIMA}",
                           "% baixo peso": fmt_pct(100 * positivos / n, 2)})
    return pd.DataFrame(linhas)


def tabela_recorte(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Tamanho e prevalencia dos conjuntos de desenvolvimento e de teste temporal."""
    limiar = cfg["dados"]["limiar_peso_g"]
    peso = peso_numerico(df)
    valido = peso.between(*PESO_PLAUSIVEL)
    conjuntos = {
        "desenvolvimento (treino + CV)": cfg["dados"]["anos_desenvolvimento"],
        "teste temporal (uso único)": [cfg["dados"]["ano_teste"]],
    }
    linhas = []
    for nome, anos in conjuntos.items():
        filtro = valido & df["ANO"].isin(anos)
        positivos = int((filtro & (peso < limiar)).sum())
        linhas.append({"conjunto": nome, "anos": f"{min(anos)}–{max(anos)}" if len(anos) > 1 else str(anos[0]),
                       "registros com peso plausível": fmt_int(filtro.sum()), "baixo peso": fmt_int(positivos),
                       "% baixo peso": fmt_pct(100 * positivos / filtro.sum(), 2)})
    return pd.DataFrame(linhas)


def resumo_alvo(df: pd.DataFrame, cfg: dict) -> str:
    peso = peso_numerico(df)
    base = peso.between(*PESO_PLAUSIVEL)
    positivos = int((base & (peso < cfg["dados"]["limiar_peso_g"])).sum())
    n = int(base.sum())
    anos = sorted(df["ANO"].unique())
    return (f"- **Período auditado:** {anos[0]}–{anos[-1]} ({len(anos)} anos), "
            f"{fmt_int(len(df))} registros brutos e {fmt_int(n)} com peso plausível.\n"
            f"- **Distribuição:** {fmt_int(positivos)} casos de baixo peso "
            f"({fmt_pct(100 * positivos / n, 2)}) e {fmt_int(n - positivos)} sem baixo peso "
            f"({fmt_pct(100 * (n - positivos) / n, 2)}). Razão de desbalanceamento ≈ 1:"
            f"{round((n - positivos) / positivos)}.")


# ------------------------------------------------------------------------ main

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Auditoria do dataset (G01, E2).")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--sem-cache", action="store_true", help="relê os .dbc ignorando o cache")
    args = parser.parse_args(argv)

    cfg = carregar_config(args.config)
    df = carregar_sinasc(cfg, usar_cache=not args.sem_cache)
    municipios = carregar_municipios(cfg)
    print(f"[auditoria] {len(df):,} registros, {df.shape[1] - 1} colunas")

    tabelas = {
        "arquivos": tabela_arquivos(df, cfg),
        "resumo-anos": tabela_resumo_anos(df, cfg),
        "variaveis": tabela_variaveis(df),
        "qualidade": tabela_qualidade(df, cfg, municipios),
        "subgrupos": tabela_subgrupos(df, cfg, municipios),
        "recorte": tabela_recorte(df, cfg),
    }
    pasta = RAIZ / cfg["saidas"]["tabelas"]
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, tabela in tabelas.items():
        tabela.to_csv(pasta / f"e2-{nome}.csv", index=False)
    blocos = {nome: tabela_md(tabela) for nome, tabela in tabelas.items()}
    blocos["alvo"] = resumo_alvo(df, cfg)
    atualizar_blocos(DICIONARIO, blocos)
    print(f"[auditoria] tabelas em {pasta.relative_to(RAIZ)}/ e blocos atualizados em "
          f"{DICIONARIO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
