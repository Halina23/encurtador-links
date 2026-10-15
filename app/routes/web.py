from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import HttpUrl, TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app import services
from app.database import get_db

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")
url_validator = TypeAdapter(HttpUrl)


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@router.post("/", response_class=HTMLResponse)
def shorten_from_form(
    request: Request, url: str = Form(...), db: Session = Depends(get_db)
) -> HTMLResponse:
    try:
        valid_url = url_validator.validate_python(url)
    except ValidationError:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"error": "URL inválida. Use um endereço começando com http:// ou https://", "url": url},
            status_code=422,
        )
    link = services.create_link(db, str(valid_url))
    return templates.TemplateResponse(
        request,
        "index.html",
        {"short_url": services.short_url(link.code), "url": link.target_url},
    )
