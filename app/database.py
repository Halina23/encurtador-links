from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# pool_pre_ping testa a conexão antes de usar, evitando erro após o banco reiniciar.
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    """Dependência do FastAPI: abre uma sessão por requisição e fecha no final."""
    with SessionLocal() as db:
        yield db
