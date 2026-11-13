# Encurtador de Links

[![CI](https://github.com/Halina23/encurtador-links/actions/workflows/ci.yml/badge.svg)](https://github.com/Halina23/encurtador-links/actions/workflows/ci.yml)

Um mini Bit.ly: você cola um link comprido e recebe um link curto. Cada acesso
ao link curto redireciona para o destino e registra o clique (data e hora).

Este é um projeto de estudo de **DevOps**. A aplicação é simples de propósito:
o foco está em como ela é empacotada, testada, observada e entregue. O projeto
evolui em fases, do localhost até um cluster Kubernetes com GitOps.

## Arquitetura (Fase 1)

```
              ┌──────────────── Docker Compose ─────────────────┐
navegador ───►│  app (FastAPI)  ──►  db (PostgreSQL 18)          │
 :8000        │      ▲                   ▲                       │
              │      │                   │  migrate (Alembic)    │
              │  /metrics, /health       │  roda e termina       │
              └──────────────────────────────────────────────────┘
```

| Componente | Tecnologia |
|---|---|
| API e página web | Python 3.12, FastAPI, Jinja2 |
| Banco de dados | PostgreSQL 18, SQLAlchemy, Alembic (migrations) |
| Dependências | uv (`pyproject.toml` + `uv.lock`) |
| Containers | Docker (multi-stage, não-root) e Docker Compose |
| Observabilidade | Logs em JSON, métricas no formato Prometheus |
| Qualidade | pytest, Ruff, Hadolint, pre-commit |
| CI | GitHub Actions, Trivy, Dependabot, GHCR |

## Como rodar

**Pré-requisitos:** Docker com Docker Compose e `make`.

```bash
git clone https://github.com/Halina23/encurtador-links.git
cd encurtador-links
cp .env.example .env   # troque POSTGRES_PASSWORD (ex.: openssl rand -hex 16)
make up
```

Acesse **http://localhost:8000**.

O `make up` sobe os serviços na ordem certa: o banco fica saudável, as
migrations rodam e só então a aplicação inicia.

### Endpoints

| Rota | Descrição |
|---|---|
| `GET /` | Página com o formulário |
| `POST /api/links` | Cria um link curto: `{"url": "https://..."}` |
| `GET /api/links/{code}` | Dados do link e total de cliques |
| `GET /{code}` | Redireciona (307) e registra o clique |
| `GET /health` | Liveness: o processo está respondendo |
| `GET /ready` | Readiness: o banco está acessível |
| `GET /metrics` | Métricas no formato Prometheus |
| `GET /docs` | Documentação interativa da API |

### Configuração

Variáveis lidas do `.env` (modelo em [`.env.example`](.env.example)):

| Variável | Descrição | Padrão |
|---|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Credenciais do banco | obrigatórias |
| `BASE_URL` | Endereço usado para montar os links curtos | `http://localhost:8000` |
| `LOG_LEVEL` | Nível dos logs | `INFO` |
| `APP_PORT` | Porta da sua máquina onde a aplicação fica acessível | `8000` |

## Desenvolvimento

**Pré-requisitos adicionais:** [uv](https://docs.astral.sh/uv/).

```bash
uv sync                      # instala as dependências no .venv
uv run pre-commit install    # ativa as verificações antes de cada commit
make check                   # lint + hadolint + testes
```

Os testes rodam contra um PostgreSQL de verdade, num container descartável
(`encurtador-test-db`, dados em memória). O `make test` sobe esse container
sozinho quando necessário. A cada rodada, as migrations são aplicadas e
desfeitas, então elas também são testadas.

### Comandos

| Comando | O que faz |
|---|---|
| `make up` / `make down` | Sobe / derruba o ambiente (os dados ficam no volume) |
| `make logs` | Acompanha os logs da aplicação |
| `make ps` | Estado dos serviços |
| `make test` | Roda os testes |
| `make lint` / `make format` | Verifica / corrige o código com Ruff |
| `make hadolint` | Verifica o Dockerfile |
| `make check` | Tudo o que o CI roda |

## Observabilidade

- **Logs:** JSON no stdout, com `request_id` em todos os logs de uma mesma
  requisição. As chamadas a `/health`, `/ready` e `/metrics` não geram log.
- **Métricas** (método RED):
  - `http_requests_total{method, route, status}`
  - `http_request_duration_seconds{method, route}` (histograma)
  - `http_requests_in_progress`
  - `links_created_total` e `redirects_total`

As labels usam o modelo da rota (`/{code}`), nunca o valor, para não explodir
a cardinalidade.

## CI

A cada push, o [workflow](.github/workflows/ci.yml) roda:

1. **Lint:** `make lint` e `make hadolint`
2. **Testes:** pytest contra um PostgreSQL 18 (service container)
3. **Build + Trivy:** build da imagem e scan de vulnerabilidades; reprova se
   houver CRITICAL com correção disponível

Na `main`, a imagem é publicada no GitHub Container Registry:

```bash
docker pull ghcr.io/halina23/encurtador-links:latest
```

A `main` é protegida: o merge exige os três checks verdes. O Dependabot abre
PRs semanais para Python, Docker e GitHub Actions.

## Estrutura

```
app/                  aplicação (rotas, modelos, observabilidade, template)
migrations/           migrations do banco (Alembic)
tests/                testes (pytest)
deploy/               infraestrutura das próximas fases
docs/decisoes/        ADRs (registro de decisões)
.github/              CI, Dependabot e template de PR
```

## Decisões

As escolhas do projeto estão registradas como ADRs em
[`docs/decisoes/`](docs/decisoes/).

## Roadmap

- [x] **Fase 1:** aplicação no localhost com Docker Compose, testes,
  observabilidade básica e CI
- [ ] **Fase 2:** deploy em VPS com Ansible e migração para K3s
- [ ] **Fase 3:** Prometheus, Grafana, Loki, Tempo (OpenTelemetry),
  alertas no Telegram e testes de carga com k6
- [ ] **Fase 4:** Argo CD (GitOps), OpenBao (segredos) e OpenTofu (DNS)

Detalhes em [`deploy/README.md`](deploy/README.md).
