# 0007 - Versão do Python e atualização da imagem base

- **Status:** Aceita
- **Data:** 2026-11-13

## Contexto

O Dependabot abriu um PR trocando a imagem base de `python:3.12-slim` para
`python:3.15-slim`. O ambiente local, o CI e o `pyproject.toml` usam Python
3.12, então aceitar o PR faria a produção rodar uma versão que nenhum teste
usou.

Além disso, a tag `3.12-slim` é móvel: é reconstruída com correções de
segurança sem mudar de nome. O Dependabot não enxerga essas reconstruções, e o
build passa a usar outra imagem sem que ninguém perceba.

## Decisão

- O projeto fica no **Python 3.12** por enquanto.
- A imagem base é fixada por **digest** (`python:3.12-slim@sha256:...`), usando
  o digest do índice multiarquitetura.
- O Dependabot **ignora mudanças de versão** (minor e major) da imagem
  `python`, mas continua abrindo PRs de **troca de digest**.
- Mudar a versão do Python é uma decisão planejada, registrada em um novo ADR,
  e feita de uma vez no Dockerfile, no CI (`UV_PYTHON`) e no `requires-python`.

## Consequências

- Builds reprodutíveis: a imagem base só muda quando um PR aprovar a troca.
- Correções de segurança chegam como PRs de digest e passam pelo CI e pelo
  Trivy antes de entrar.
- Paridade entre ambiente local, CI e produção.
- A atualização de versão do Python não acontece sozinha e precisa ser
  lembrada.
