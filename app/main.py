from fastapi import FastAPI

from app.config import settings
from app.database import engine
from app.observability import metrics
from app.observability.logging import setup_logging
from app.observability.middleware import observability_middleware
from app.observability.tracing import setup_tracing
from app.routes import health, links, web

setup_logging(settings.log_level)

app = FastAPI(title="Encurtador de Links", version="0.1.0")
app.middleware("http")(observability_middleware)
# Depois do nosso middleware: o do OpenTelemetry fica por fora e o span já existe
# quando o log de acesso é escrito (assim ele sai com o trace_id).
setup_tracing(app, engine)

app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(web.router)
# Por último, porque contém a rota "pega-tudo" /{code}.
app.include_router(links.router)
