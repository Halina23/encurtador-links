# 0002 - Estrutura de pastas

- **Status:** Aceita
- **Data:** 2026-10-15

## Contexto

O projeto começa como uma aplicação rodando via Docker Compose (Fase 1), mas
vai ganhar deploy em VPS, Ansible, K3s, stack de observabilidade e GitOps nas
fases seguintes. A estrutura precisa acomodar esse crescimento sem
reorganizações grandes.

## Decisão

```
app/                  código da aplicação (FastAPI)
  routes/             endpoints separados por assunto
  observability/      logs, métricas e (futuramente) traces
  templates/          página web (Jinja2)
migrations/           migrations do banco (Alembic)
tests/                testes automatizados (pytest)
deploy/               infraestrutura das fases futuras
docs/decisoes/        ADRs
.github/              workflows do GitHub Actions e Dependabot
```

Na raiz ficam os arquivos de build e configuração: `Dockerfile`,
`compose.yaml`, `pyproject.toml`, `.env.example` e `Makefile`.

- Código da aplicação e infraestrutura ficam separados: mudanças de deploy não
  tocam em `app/`.
- Observabilidade fica isolada em `app/observability/`, para que a
  instrumentação com OpenTelemetry (Fase 3) entre sem espalhar código.
- Subpastas de `deploy/` (ex.: `ansible/`, `k8s/`) só são criadas quando forem
  usadas. Até lá, `deploy/README.md` descreve o plano.

## Consequências

- Cada fase tem um lugar óbvio para seus arquivos.
- A mesma imagem Docker serve para todos os ambientes, porque a configuração
  vem de variáveis de ambiente (12-Factor App).
- A estrutura de `deploy/` ainda vai ser detalhada em ADRs futuros.
