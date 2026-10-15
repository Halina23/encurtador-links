import os

# Precisa vir antes de importar a app, porque a configuração é lida no import.
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def db_session():
    """Banco SQLite em memória, novo e vazio para cada teste."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, expire_on_commit=False)() as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app, follow_redirects=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()
