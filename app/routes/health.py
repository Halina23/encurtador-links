from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(tags=["saúde"])


@router.get("/health")
def health() -> dict:
    """Liveness: o processo está vivo e respondendo. Não depende do banco."""
    return {"status": "ok"}


@router.get("/ready")
def ready(db: Session = Depends(get_db)) -> JSONResponse:
    """Readiness: a aplicação está pronta para receber tráfego (banco acessível)."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503, content={"status": "error", "database": "unavailable"}
        )
    return JSONResponse(content={"status": "ok", "database": "ok"})
