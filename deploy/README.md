# deploy/

Infraestrutura das próximas fases do projeto. As subpastas são criadas
conforme cada fase começa (ver [ADR 0002](../docs/decisoes/0002-estrutura-de-pastas.md)).

## Fase 2 - Deploy em VPS

| Pasta prevista | Conteúdo |
|---|---|
| `ansible/` | Playbooks para configurar a VPS (Hostinger): usuários, SSH, firewall, Docker e K3s |
| `k8s/` | Manifestos do Kubernetes: Deployment, Service, Ingress, Job de migrations e Secrets |

Etapas planejadas:

1. Configurar a VPS com Ansible.
2. Rodar a aplicação com Docker Compose na VPS, usando a imagem do GHCR.
3. Migrar para K3s:
   - as migrations viram um *Job* (mesmo modelo do serviço `migrate` do Compose)
   - `/health` e `/ready` viram `livenessProbe` e `readinessProbe`
   - `runAsNonRoot` (a imagem já roda com UID 1000)
   - Traefik (incluído no K3s) como Ingress, com HTTPS
   - `/metrics` sem exposição pública

## Fase 3 - Observabilidade

| Pasta prevista | Conteúdo |
|---|---|
| `observability/` | Configuração de Prometheus, Grafana, Loki, Tempo e Alertmanager |
| `load-tests/` | Scripts do k6 |

- **Métricas:** Prometheus coleta o `/metrics`; dashboards no Grafana.
- **Logs:** Grafana Alloy lê o stdout dos containers e envia para o Loki.
- **Traces:** instrumentação com OpenTelemetry em `app/observability/` e envio para o Tempo.
- **Alertas:** Alertmanager envia para um bot do Telegram:
  - site fora do ar (`up == 0`)
  - percentual de respostas 5xx acima do limite
  - p95 de latência acima do limite
- **Testes de carga:** k6, observando o comportamento nos dashboards.

## Fase 4 - GitOps, segredos e DNS

| Pasta prevista | Conteúdo |
|---|---|
| `argocd/` | Aplicações do Argo CD, que sincroniza o cluster com o Git |
| `tofu/` | OpenTofu para gerenciar o DNS como código |

- **Argo CD:** o estado do cluster passa a ser o que está na `main`.
- **OpenBao:** armazenamento dos segredos, substituindo os Secrets em texto.
- **OpenTofu:** registros DNS versionados no Git.
