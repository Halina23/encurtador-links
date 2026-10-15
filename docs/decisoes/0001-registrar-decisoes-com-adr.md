# 0001 - Registrar decisões com ADRs

- **Status:** Aceita
- **Data:** 2026-10-15

## Contexto

Este é um projeto de aprendizado de DevOps que vai evoluir em fases (localhost,
VPS, K3s, observabilidade, GitOps). Decisões tomadas em conversas se perdem com
facilidade, e no futuro será difícil lembrar por que algo foi feito de um jeito.

## Decisão

Registrar cada decisão de arquitetura relevante como um ADR (Architecture
Decision Record) em `docs/decisoes/`, no formato de Michael Nygard:
Status, Contexto, Decisão e Consequências.

- Arquivos numerados em sequência: `NNNN-titulo-em-kebab-case.md`.
- ADRs aceitos não são reescritos. Se uma decisão mudar, um novo ADR a
  substitui e o antigo recebe o status `Substituída por NNNN`.

## Consequências

- O histórico do raciocínio fica no próprio repositório, junto com o código.
- Quem lê o projeto (inclusive recrutadores) entende o porquê das escolhas.
- Exige a disciplina de escrever um ADR a cada decisão importante.
