import os
from pathlib import Path

# Precisa vir antes de importar a app, porque a configuração é lida no import.
# Credenciais do banco de teste descartável (ver README): não são segredos.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://encurtador:encurtador@localhost:5432/encurtador_test",
)

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.exc import OperationalError  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine, get_db  # noqa: E402
from app.main import app  # noqa: E402

ALEMBIC_INI = Path(__file__).parent.parent / "alembic.ini"


@pytest.fixture(scope="session")
def migrated_engine():
    """Aplica as migrations uma vez por rodada e desfaz tudo no final."""
    try:
        engine.connect().close()
    except OperationalError:
        pytest.exit(
            "Postgres de testes inacessível. Suba o container encurtador-test-db (ver README).",
            returncode=1,
        )

    alembic_cfg = Config(str(ALEMBIC_INI))
    command.upgrade(alembic_cfg, "head")
    yield engine
    command.downgrade(alembic_cfg, "base")


@pytest.fixture
def db_session(migrated_engine):
    """Cada teste roda dentro de uma transação que é desfeita no final.

    Os commits da aplicação viram SAVEPOINTs, então nada fica gravado
    e cada teste começa com o banco vazio.
    """
    with migrated_engine.connect() as connection:
        transaction = connection.begin()
        session = Session(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )
        yield session
        session.close()
        transaction.rollback()


@pytest.fixture
def client(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app, follow_redirects=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()
