from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import services
from app.database import get_db
from app.models import Link
from app.schemas import LinkCreate, LinkOut

router = APIRouter(tags=["links"])


def _to_out(db: Session, link: Link) -> LinkOut:
    return LinkOut(
        code=link.code,
        short_url=services.short_url(link.code),
        target_url=link.target_url,
        created_at=link.created_at,
        clicks=services.count_clicks(db, link),
    )


def _get_or_404(db: Session, code: str) -> Link:
    link = services.get_link(db, code)
    if link is None:
        raise HTTPException(status_code=404, detail="Link não encontrado")
    return link


@router.post("/api/links", status_code=201)
def create_link(payload: LinkCreate, db: Session = Depends(get_db)) -> LinkOut:
    link = services.create_link(db, str(payload.url))
    return _to_out(db, link)


@router.get("/api/links/{code}")
def link_stats(code: str, db: Session = Depends(get_db)) -> LinkOut:
    return _to_out(db, _get_or_404(db, code))


# Rota "pega-tudo": precisa ser registrada por último no main.py.
@router.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)) -> RedirectResponse:
    link = _get_or_404(db, code)
    services.register_click(db, link)
    # 307 (temporário) em vez de 301: o navegador não guarda o redirecionamento
    # em cache, então todo acesso passa pela aplicação e o clique é contado.
    return RedirectResponse(link.target_url, status_code=307)
