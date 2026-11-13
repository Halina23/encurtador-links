# 0006 - Publicação da imagem no GHCR e política do Trivy

- **Status:** Aceita
- **Data:** 2026-11-13

## Contexto

O CI (GitHub Actions) faz o build da imagem Docker a cada push. Na Fase 2, a
VPS e depois o K3s vão precisar baixar essa imagem de algum registro. Também é
preciso definir quando uma vulnerabilidade encontrada na imagem deve impedir a
publicação.

## Decisão

**Registro:** GitHub Container Registry (GHCR), em
`ghcr.io/halina23/encurtador-links`.

- Todo push faz build e scan, mas só a `main` publica.
- Tags: `sha-<commit completo>` (rastreável e imutável) e `latest` (só na `main`).
- Autenticação com o `GITHUB_TOKEN` temporário do workflow, sem segredos
  cadastrados. Apenas o job de build recebe `packages: write`.

**Trivy:** dois passos no CI.

- Relatório de vulnerabilidades HIGH e CRITICAL, sem reprovar o pipeline.
- Portão: reprova se houver CRITICAL **com correção disponível**
  (`ignore-unfixed`). Falhas sem correção não bloqueiam, porque não há ação
  possível.

A `main` é protegida por um ruleset que exige os três checks do CI verdes
para o merge.

## Consequências

- O deploy da Fase 2 só precisa fazer `docker pull` de uma tag `sha-...`.
- Uma imagem com CRITICAL corrigível nunca chega ao registro.
- Vulnerabilidades HIGH ficam visíveis no relatório e precisam ser
  acompanhadas manualmente.
- O pacote no GHCR herdou a visibilidade pública do repositório.
