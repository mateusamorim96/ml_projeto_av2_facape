"""Esquema das colunas do SINASC: descricao, codificacao e decisao de uso.

Fonte unica de verdade para a auditoria (E2) e para a preparacao (E3).
Descricoes e codigos seguem o documento oficial "Estrutura do SINASC"
(CGIAE/DASNT/SVS/MS, atualizado em 12/2019), disponivel em
ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Doc/Estrutura_SINASC_para_CD.pdf

Usos possiveis:
  alvo       -> origem da variavel-alvo
  atributo   -> entra no modelo (conhecido no inicio do pre-natal)
  filtro     -> define a populacao (src/data/populacao.py), nao entra no modelo
  descartada -> fora do modelo; `motivo` explica por que
"""
from __future__ import annotations

from dataclasses import dataclass

# Motivos padronizados de descarte
VAZAMENTO_PARTO = "vazamento: só é conhecida no parto ou depois dele"
VAZAMENTO_DURACAO = "vazamento: depende da duração da gestação"
IDENTIFICADOR = "identificador ou data que permite reidentificação"
INTERNO = "campo interno do sistema, sem significado clínico"
DN_ANTIGA = "codificação da DN antiga, substituída por campo mais detalhado"
BEBE = "característica do recém-nascido, desconhecida na captação"
NATURALIDADE = "baixo valor preditivo esperado e aumenta risco de reidentificação"
PREENCHIMENTO = "dado do preenchimento da DN, registrado depois do parto"


@dataclass(frozen=True)
class Coluna:
    nome: str
    descricao: str
    tipo: str  # numerica | categorica | data | texto
    uso: str
    unidade: str = "—"
    codigos: str = "—"
    ignorado: tuple[str, ...] = ()  # codigos que significam "ignorado"
    motivo: str = ""


COLUNAS: tuple[Coluna, ...] = (
    # ------------------------------------------------------------ alvo
    Coluna("PESO", "Peso ao nascer, verificado até a 5ª hora de vida", "numerica", "alvo",
           unidade="g", codigos="4 dígitos", motivo="alvo = 1 se PESO < 2500 g"),
    # ------------------------------------------------------- atributos
    Coluna("IDADEMAE", "Idade da mãe", "numerica", "atributo", unidade="anos", ignorado=("99",)),
    Coluna("ESCMAE2010", "Escolaridade da mãe (última série concluída), nível", "categorica",
           "atributo", codigos="0 sem escolaridade; 1 fundamental I; 2 fundamental II; 3 médio; "
                               "4 superior incompleto; 5 superior completo; 9 ignorado",
           ignorado=("9",)),
    Coluna("RACACORMAE", "Raça/cor da mãe", "categorica", "atributo",
           codigos="1 branca; 2 preta; 3 amarela; 4 parda; 5 indígena",
           motivo="também usada na análise por subgrupo (RQ-ÉT-02)"),
    Coluna("ESTCIVMAE", "Situação conjugal da mãe", "categorica", "atributo",
           codigos="1 solteira; 2 casada; 3 viúva; 4 separada; 5 união estável; 9 ignorada",
           ignorado=("9",)),
    Coluna("CODOCUPMAE", "Ocupação da mãe (CBO 2002)", "categorica", "atributo",
           codigos="6 dígitos CBO", motivo="alta cardinalidade: agrupar pelo grande grupo da CBO na E3"),
    Coluna("QTDGESTANT", "Número de gestações anteriores", "numerica", "atributo", unidade="gestações",
           ignorado=("99",)),
    Coluna("QTDPARTNOR", "Número de partos vaginais anteriores", "numerica", "atributo", unidade="partos",
           ignorado=("99",)),
    Coluna("QTDPARTCES", "Número de cesáreas anteriores", "numerica", "atributo", unidade="partos",
           ignorado=("99",)),
    Coluna("QTDFILVIVO", "Número de filhos vivos", "numerica", "atributo", unidade="filhos",
           ignorado=("99",)),
    Coluna("QTDFILMORT", "Número de perdas fetais e abortos", "numerica", "atributo", unidade="perdas",
           ignorado=("99",)),
    Coluna("PARIDADE", "Paridade, calculada pelo sistema a partir do histórico", "categorica", "atributo",
           codigos="0 nulípara; 1 multípara; 9 ignorado", ignorado=("9",)),
    Coluna("GRAVIDEZ", "Tipo de gravidez", "categorica", "filtro",
           codigos="1 única; 2 dupla; 3 tripla ou mais; 9 ignorado", ignorado=("9",),
           motivo="população = só gestação única (seção 6); constante dentro dela"),
    Coluna("MESPRENAT", "Mês de gestação em que iniciou o pré-natal", "numerica", "atributo",
           unidade="mês", codigos="01 … 09; 99 ignorado", ignorado=("99",),
           motivo="registros sem o mês ficam fora da população (seção 6)"),
    Coluna("CODMUNRES", "Município de residência da mãe (IBGE, 6 dígitos)", "categorica", "atributo",
           codigos="código IBGE sem dígito verificador",
           motivo="convertido em mesorregião/região imediata (IBGE) na E3; Petrolina = 261110"),
    Coluna("DTNASC", "Data do nascimento", "data", "descartada",
           motivo=IDENTIFICADOR + "; o ano vem do nome do arquivo"),
    # ------------------------------------------------- descartadas: completude
    Coluna("IDADEPAI", "Idade do pai", "numerica", "descartada", unidade="anos", ignorado=("99",),
           motivo="mais de 60% de nulos (ver auditoria)"),
    Coluna("CODPAISRES", "País de residência", "categorica", "descartada",
           motivo="existe só em 2015 e 2017; o arquivo já é de residentes em PE"),
    # ------------------------------------------------- descartadas: parto
    Coluna("SEMAGESTAC", "Semanas de gestação", "numerica", "descartada", unidade="semanas",
           motivo=VAZAMENTO_PARTO),
    Coluna("GESTACAO", "Semanas de gestação, agrupado (DN antiga)", "categorica", "descartada",
           motivo=VAZAMENTO_PARTO),
    Coluna("TPMETESTIM", "Método para estimar a idade gestacional", "categorica", "descartada",
           motivo=VAZAMENTO_PARTO),
    Coluna("PARTO", "Tipo de parto", "categorica", "descartada", motivo=VAZAMENTO_PARTO),
    Coluna("STTRABPART", "Trabalho de parto induzido", "categorica", "descartada", motivo=VAZAMENTO_PARTO),
    Coluna("STCESPARTO", "Cesárea antes do trabalho de parto", "categorica", "descartada",
           motivo=VAZAMENTO_PARTO),
    Coluna("TPAPRESENT", "Apresentação do recém-nascido", "categorica", "descartada",
           motivo=VAZAMENTO_PARTO),
    Coluna("TPROBSON", "Grupo de Robson (gerado a partir de dados do parto)", "categorica", "descartada",
           motivo=VAZAMENTO_PARTO),
    Coluna("TPNASCASSI", "Profissional que assistiu o parto", "categorica", "descartada",
           motivo=VAZAMENTO_PARTO),
    Coluna("LOCNASC", "Local de ocorrência do nascimento", "categorica", "descartada",
           motivo=VAZAMENTO_PARTO),
    Coluna("CODMUNNASC", "Município de ocorrência do nascimento", "categorica", "descartada",
           motivo=VAZAMENTO_PARTO),
    Coluna("APGAR1", "Índice de Apgar no 1º minuto", "numerica", "descartada", motivo=VAZAMENTO_PARTO),
    Coluna("APGAR5", "Índice de Apgar no 5º minuto", "numerica", "descartada", motivo=VAZAMENTO_PARTO),
    Coluna("IDANOMAL", "Anomalia congênita detectada no nascimento", "categorica", "descartada",
           motivo=VAZAMENTO_PARTO),
    Coluna("CODANOMAL", "Anomalias congênitas (CID-10)", "texto", "descartada", motivo=VAZAMENTO_PARTO),
    Coluna("HORANASC", "Hora do nascimento", "texto", "descartada", motivo=VAZAMENTO_PARTO),
    Coluna("SEXO", "Sexo do recém-nascido", "categorica", "descartada",
           codigos="os arquivos usam 0, 1 e 2; o dicionário oficial cita M, F e I", motivo=BEBE),
    Coluna("RACACOR", "Raça/cor do recém-nascido", "categorica", "descartada",
           motivo=BEBE + "; usa-se RACACORMAE"),
    # --------------------------------------- descartadas: duracao da gestacao
    Coluna("CONSPRENAT", "Número de consultas de pré-natal", "numerica", "descartada",
           motivo=VAZAMENTO_DURACAO),
    Coluna("CONSULTAS", "Consultas de pré-natal, agrupado (DN antiga)", "categorica", "descartada",
           motivo=VAZAMENTO_DURACAO),
    Coluna("KOTELCHUCK", "Índice de adequação do pré-natal (usa nº de consultas)", "categorica",
           "descartada", motivo=VAZAMENTO_DURACAO),
    # ------------------------------------- descartadas: identificacao/datas
    Coluna("DTNASCMAE", "Data de nascimento da mãe", "data", "descartada", motivo=IDENTIFICADOR),
    Coluna("DTULTMENST", "Data da última menstruação", "data", "descartada", motivo=IDENTIFICADOR),
    Coluna("CODESTAB", "Estabelecimento de nascimento (CNES)", "categorica", "descartada",
           motivo=IDENTIFICADOR + "; também é dado do parto"),
    Coluna("NUMEROLOTE", "Número do lote", "texto", "descartada", motivo=INTERNO),
    Coluna("CONTADOR", "Contador sequencial do registro (minúsculo em 2015 e 2017)", "texto", "descartada",
           motivo=INTERNO),
    Coluna("DTDECLARAC", "Data de preenchimento da DN", "data", "descartada", motivo=PREENCHIMENTO),
    Coluna("DTCADASTRO", "Data de cadastro no sistema", "data", "descartada", motivo=INTERNO),
    Coluna("DTRECEBIM", "Data do último recebimento do lote", "data", "descartada", motivo=INTERNO),
    Coluna("DTRECORIGA", "Data de recebimento original", "data", "descartada", motivo=INTERNO),
    Coluna("DIFDATA", "Diferença entre datas do sistema", "numerica", "descartada", motivo=INTERNO),
    Coluna("VERSAOSIST", "Versão do sistema", "texto", "descartada", motivo=INTERNO),
    Coluna("ORIGEM", "Banco de dados de origem", "categorica", "descartada", motivo=INTERNO),
    Coluna("STDNEPIDEM", "Status de DN epidemiológica", "categorica", "descartada", motivo=INTERNO),
    Coluna("STDNNOVA", "Status de DN nova", "categorica", "descartada", motivo=INTERNO),
    Coluna("TPFUNCRESP", "Função de quem preencheu a DN", "categorica", "descartada", motivo=PREENCHIMENTO),
    Coluna("TPDOCRESP", "Documento de quem preencheu a DN", "categorica", "descartada", motivo=PREENCHIMENTO),
    # ---------------------------------- descartadas: redundantes / naturalidade
    Coluna("ESCMAE", "Escolaridade em anos de estudo (DN antiga)", "categorica", "descartada",
           motivo=DN_ANTIGA),
    Coluna("ESCMAEAGR1", "Escolaridade 2010 agregada", "categorica", "descartada",
           motivo="redundante com ESCMAE2010"),
    Coluna("SERIESCMAE", "Última série concluída", "numerica", "descartada",
           motivo="redundante com ESCMAE2010"),
    Coluna("NATURALMAE", "Naturalidade da mãe (país, se estrangeira)", "categorica", "descartada",
           motivo=NATURALIDADE),
    Coluna("CODMUNNATU", "Município de naturalidade da mãe", "categorica", "descartada",
           motivo=NATURALIDADE),
    Coluna("CODUFNATU", "UF de naturalidade da mãe", "categorica", "descartada", motivo=NATURALIDADE),
)

# Origem de cada coluna: bloco da Declaracao de Nascido Vivo (DN) em que o campo
# e preenchido, ou campo gerado pelo sistema -- conforme "Estrutura do SINASC".
_ORIGENS: dict[str, tuple[str, ...]] = {
    "DN, bloco I (recém-nascido)": ("DTNASC", "HORANASC", "SEXO", "RACACOR", "PESO", "APGAR1", "APGAR5",
                                    "IDANOMAL"),
    "DN, bloco II (local do parto)": ("LOCNASC", "CODESTAB", "CODMUNNASC"),
    "DN, bloco III (mãe)": ("ESCMAE", "ESCMAE2010", "SERIESCMAE", "CODOCUPMAE", "DTNASCMAE", "IDADEMAE",
                            "NATURALMAE", "ESTCIVMAE", "RACACORMAE", "CODMUNRES"),
    "DN, bloco IV (pai)": ("IDADEPAI",),
    "DN, bloco V (gestação e parto)": ("QTDGESTANT", "QTDPARTNOR", "QTDPARTCES", "QTDFILVIVO", "QTDFILMORT",
                                       "DTULTMENST", "GESTACAO", "SEMAGESTAC", "TPMETESTIM", "CONSULTAS",
                                       "CONSPRENAT", "MESPRENAT", "GRAVIDEZ", "TPAPRESENT", "STTRABPART",
                                       "PARTO", "STCESPARTO", "TPNASCASSI"),
    "DN, bloco VI (anomalia)": ("CODANOMAL",),
    "DN, bloco VII (preenchimento)": ("DTDECLARAC", "TPFUNCRESP", "TPDOCRESP"),
    "calculada pelo sistema": ("ESCMAEAGR1", "TPROBSON", "PARIDADE", "KOTELCHUCK"),
    "demais campos do arquivo": ("CODUFNATU", "CODMUNNATU", "CODPAISRES"),
    "interna do sistema": ("STDNEPIDEM", "STDNNOVA", "DTRECORIGA", "DIFDATA", "DTRECEBIM", "VERSAOSIST",
                           "NUMEROLOTE", "DTCADASTRO", "ORIGEM"),
}
ORIGEM = {nome: origem for origem, nomes in _ORIGENS.items() for nome in nomes}


def origem(nome: str) -> str:
    """Bloco da DN ou origem sistemica; colunas fora do dicionario oficial sao sinalizadas."""
    return ORIGEM.get(nome, "arquivo DATASUS, ausente do dicionário oficial")


POR_NOME = {c.nome: c for c in COLUNAS}
ATRIBUTOS = tuple(c.nome for c in COLUNAS if c.uso == "atributo")
DESCARTADAS = tuple(c.nome for c in COLUNAS if c.uso == "descartada")
