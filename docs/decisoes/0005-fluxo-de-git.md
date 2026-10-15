# 0005 - Fluxo de Git

- **Status:** Aceita
- **Data:** 2026-10-15

## Contexto

O repositório faz parte de um portfólio. O histórico precisa contar a
evolução do projeto de forma clara, e o fluxo deve se parecer com o usado em
equipes profissionais.

## Decisão

- Mensagens de commit no padrão Conventional Commits
  (`feat`, `fix`, `docs`, `test`, `ci`, `build`, `chore`, `refactor`).
- Commits pequenos, um por parte lógica do trabalho.
- Cada etapa é feita numa branch própria (`tipo/descricao`, ex.: `docs/adrs`)
  e entra na `main` via Pull Request.
- O CI roda nos Pull Requests e nos pushes para a `main`.

## Consequências

- O histórico fica legível e fácil de navegar.
- A `main` só recebe código que passou pelo CI.
- Um pouco mais de cerimônia do que commitar direto na `main`.
