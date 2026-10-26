# ============================================================
# Projeto AV2 de Machine Learning — imagem do grupo GXX
# Base fixada por tag. Para reprodutibilidade máxima, fixe também o digest:
#   docker pull python:3.11-slim
#   docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim
#   FROM python:3.11-slim@sha256:<digest>
# ============================================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=42 \
    SEED=42 \
    MPLBACKEND=Agg

WORKDIR /app

# Dependências primeiro: melhora o cache de build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Um único comando executa o pipeline completo
CMD ["python", "-m", "src.pipeline", "--config", "configs/base.yaml"]
