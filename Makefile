# Atalhos do dia a dia. Rode "make" para ver a lista.
.DEFAULT_GOAL := help
.PHONY: help up down logs ps test-db test lint format hadolint check

TEST_DB := encurtador-test-db

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-10s %s\n", $$1, $$2}'

# --- Ambiente local (Docker Compose) ---

up: ## Sobe banco, migrations e aplicação (com build)
	docker compose up -d --build

down: ## Derruba os containers (os dados ficam no volume)
	docker compose down

logs: ## Acompanha os logs da aplicação
	docker compose logs -f app

ps: ## Mostra o estado dos serviços
	docker compose ps -a

# --- Testes ---

test-db: ## Garante que o Postgres de testes está rodando
	@docker start $(TEST_DB) >/dev/null 2>&1 || docker run -d --name $(TEST_DB) \
		-p 127.0.0.1:5432:5432 \
		-e POSTGRES_USER=encurtador -e POSTGRES_PASSWORD=encurtador -e POSTGRES_DB=encurtador_test \
		--tmpfs /var/lib/postgresql postgres:18-alpine >/dev/null
	@# -h 127.0.0.1 força TCP: o Postgres temporário da inicialização só escuta no socket local.
	@until docker exec $(TEST_DB) pg_isready -h 127.0.0.1 -U encurtador -d encurtador_test >/dev/null 2>&1; do sleep 1; done

test: test-db ## Roda os testes (sobe o banco de testes se precisar)
	uv run pytest

# --- Qualidade ---

lint: ## Verifica o código com ruff (sem alterar nada)
	uv run ruff check .
	uv run ruff format --check .

format: ## Corrige e formata o código com ruff
	uv run ruff check --fix .
	uv run ruff format .

hadolint: ## Verifica o Dockerfile
	docker run --rm -i hadolint/hadolint:v2.15.1 < Dockerfile

check: lint hadolint test ## Roda tudo o que o CI vai rodar
