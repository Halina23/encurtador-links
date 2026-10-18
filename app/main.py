from fastapi import FastAPI

from app.config import settings
from app.observability import metrics
from app.observability.logging import setup_logging
from app.observability.middleware import observability_middleware
from app.routes import health, links, web

setup_logging(settings.log_level)

app = FastAPI(title="Encurtador de Links", version="0.1.0")
app.middleware("http")(observability_middleware)

app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(web.router)
# Por último, porque contém a rota "pega-tudo" /{code}.
app.include_router(links.router)
