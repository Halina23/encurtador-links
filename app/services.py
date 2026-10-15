"""Regras de negócio do encurtador, usadas tanto pela API quanto pela página web."""

import secrets
import string

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Click, Link

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 7
MAX_ATTEMPTS = 5


def _generate_code() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))


def create_link(db: Session, target_url: str) -> Link:
    for _ in range(MAX_ATTEMPTS):
        code = _generate_code()
        if db.scalar(select(Link.id).where(Link.code == code)) is None:
            link = Link(code=code, target_url=target_url)
            db.add(link)
            db.commit()
            db.refresh(link)
            return link
    raise RuntimeError("Não foi possível gerar um código único")


def get_link(db: Session, code: str) -> Link | None:
    return db.scalar(select(Link).where(Link.code == code))


def register_click(db: Session, link: Link) -> None:
    db.add(Click(link_id=link.id))
    db.commit()


def count_clicks(db: Session, link: Link) -> int:
    return db.scalar(select(func.count(Click.id)).where(Click.link_id == link.id))


def short_url(code: str) -> str:
    return f"{settings.base_url.rstrip('/')}/{code}"
