# Atalhos do grupo GXX. `make` sem argumento mostra a ajuda.
.PHONY: help setup pipeline docker docker-build validar entrega limpar

PY ?= python3
CONFIG ?= configs/base.yaml
IMAGEM ?= grupo-XX:local

help:
	@echo "make setup        - cria .venv e instala requirements"
	@echo "make pipeline     - executa o pipeline completo (local)"
	@echo "make docker-build - constroi a imagem"
	@echo "make docker       - executa o pipeline em container"
	@echo "make validar      - valida a pasta do grupo"
	@echo "make entrega E=E6 - valida exatamente a entrega informada"
	@echo "make limpar       - remove artefatos locais"

setup:
	$(PY) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

pipeline:
	$(PY) -m src.pipeline --config $(CONFIG)

docker-build:
	docker build -t $(IMAGEM) .

docker:
	docker run --rm -v "$(PWD)/data/raw:/app/data/raw:ro" $(IMAGEM)

validar:
	$(PY) ../scripts/check_entrega.py --grupo grupo-XX --entrega $(E)

entrega:
	$(PY) ../scripts/check_entrega.py --grupo grupo-XX --entrega $(E)

limpar:
	rm -rf .venv __pycache__ .pytest_cache
	find . -name '*.pyc' -delete
