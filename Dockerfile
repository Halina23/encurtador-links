# syntax=docker/dockerfile:1

# =============================================================================
# Estágio 1: builder ("oficina") - instala as dependências num .venv
# =============================================================================
FROM python:3.12-slim AS builder

# Copia só o executável do uv da imagem oficial (sem instalar nada via pip).
COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /usr/local/bin/uv

# UV_COMPILE_BYTECODE: pré-compila os .pyc, deixando a inicialização mais rápida.
# UV_LINK_MODE=copy: copia os arquivos em vez de criar links (o cache é montado à parte).
# UV_PYTHON_DOWNLOADS=never: usa o Python da imagem, nunca baixa outro.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Primeiro só a lista de dependências: esta camada fica em cache
# enquanto pyproject.toml e uv.lock não mudarem.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# =============================================================================
# Estágio 2: imagem final - só o necessário para rodar
# =============================================================================
FROM python:3.12-slim

# PYTHONDONTWRITEBYTECODE: não grava .pyc em tempo de execução.
# PYTHONUNBUFFERED: os logs saem no stdout na hora, sem ficar presos em buffer.
# PATH: faz "python" e "uvicorn" virem do .venv.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Usuário sem privilégios de administrador, com UID/GID fixos (1000).
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --create-home app

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app

# Numérico para o Kubernetes conseguir verificar que não é root (runAsNonRoot).
USER 1000:1000

# Apenas documenta a porta. Quem publica de fato é o "-p" ou o Compose.
EXPOSE 8000

# Exec form: o uvicorn é o processo principal e recebe o SIGTERM direto,
# permitindo o encerramento gracioso (graceful shutdown).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
