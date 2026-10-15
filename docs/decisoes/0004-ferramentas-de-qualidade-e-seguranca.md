# 0004 - Ferramentas de qualidade e segurança

- **Status:** Aceita
- **Data:** 2026-10-15

## Contexto

Mesmo sendo um projeto pequeno, ele deve demonstrar práticas de mercado:
código padronizado, Dockerfile bem escrito, imagem sem vulnerabilidades
conhecidas e dependências atualizadas.

## Decisão

Adotar na Fase 1:

| Ferramenta  | Papel                                                        |
|-------------|--------------------------------------------------------------|
| Ruff        | Linter e formatter de Python                                 |
| pre-commit  | Roda Ruff e outras verificações antes de cada commit         |
| Hadolint    | Linter do `Dockerfile`                                       |
| Trivy       | Scan de vulnerabilidades da imagem Docker no CI              |
| Dependabot  | PRs automáticos de atualização (Python, Docker, Actions)     |
| Makefile    | Atalhos para os comandos do dia a dia (`make up`, `make test`) |

Adiado:

- **Reverse proxy:** entra na Fase 2. O K3s já traz o Traefik como Ingress
  Controller.
- **Redis (cache):** só será adicionado se os testes de carga com k6 (Fase 3)
  mostrarem necessidade.

## Consequências

- O CI fica mais completo (lint, testes, build e scan), e por isso um pouco
  mais lento.
- Problemas de estilo e segurança aparecem antes de chegar à `main`.
- O Dependabot vai gerar PRs periódicos que precisam de revisão.
