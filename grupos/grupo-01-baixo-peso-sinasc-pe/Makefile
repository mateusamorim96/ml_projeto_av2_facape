# Atalhos do grupo G01. `make` sem argumento mostra a ajuda.
.PHONY: help setup dados auditoria pipeline docker docker-build validar entrega limpar

PY ?= python3
CONFIG ?= configs/base.yaml
IMAGEM ?= grupo-01-baixo-peso-sinasc-pe:local

help:
	@echo "make setup        - cria .venv e instala requirements"
	@echo "make dados        - baixa DATASUS/IBGE para data/raw/ e confere SHA-256"
	@echo "make auditoria    - recalcula as tabelas de docs/dicionario-de-dados.md"
	@echo "make pipeline     - executa o pipeline completo (local)"
	@echo "make docker-build - constroi a imagem"
	@echo "make docker       - executa o pipeline em container"
	@echo "make validar E=E2 - valida o que vai para o Git (igual à CI)"
	@echo "make entrega E=E6 - valida exatamente a entrega informada"
	@echo "make limpar       - remove artefatos locais"

setup:
	$(PY) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

dados:
	$(PY) -m src.data.download --config $(CONFIG)

auditoria: dados
	$(PY) -m src.data.auditoria --config $(CONFIG)

pipeline:
	$(PY) -m src.pipeline --config $(CONFIG)

docker-build:
	docker build -t $(IMAGEM) .

docker:
	docker run --rm -v "$(PWD)/data/raw:/app/data/raw:ro" $(IMAGEM)

# valida uma cópia só com o que vai para o Git (o mesmo que a CI vê);
# o check_entrega.py varre o disco e acusaria .venv/, data/raw/ e caches ignorados
validar:
	$(PY) tools/validar_limpo.py --entrega $(E)

# validação direta na pasta (inclui arquivos ignorados pelo Git)
entrega:
	$(PY) ../../scripts/check_entrega.py --grupo grupo-01-baixo-peso-sinasc-pe --entrega $(E)

limpar:
	rm -rf .venv __pycache__ .pytest_cache
	find . -name '*.pyc' -delete
