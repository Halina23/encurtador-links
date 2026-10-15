# 0003 - Stack da aplicação

- **Status:** Aceita
- **Data:** 2026-10-15

## Contexto

A aplicação é um encurtador de links: recebe uma URL longa, devolve uma curta,
redireciona e registra cada clique (data e hora). Precisa de uma API, de uma
página web simples e de um banco relacional.

## Decisão

| Necessidade              | Escolha                       |
|--------------------------|-------------------------------|
| Framework web / API      | FastAPI                       |
| Banco de dados           | PostgreSQL                    |
| Acesso ao banco          | SQLAlchemy (ORM)              |
| Migrations               | Alembic                       |
| Página web               | Templates Jinja2 no FastAPI   |
| Dependências Python      | uv (`pyproject.toml` + `uv.lock`) |
| Configuração             | Variáveis de ambiente (pydantic-settings) |
| Testes                   | pytest                        |

## Consequências

- Um único container para a aplicação (API + página), o que simplifica o
  deploy nas fases seguintes.
- O Alembic versiona o esquema do banco, então as migrations podem rodar de
  forma automatizada no deploy (VPS e K3s).
- O `uv.lock` garante builds reprodutíveis: a imagem Docker instala exatamente
  as mesmas versões em qualquer máquina.
- Um frontend separado fica fora do escopo. Se for necessário, um novo ADR
  substitui a escolha do Jinja2.
