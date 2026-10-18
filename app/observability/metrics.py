"""Métricas no formato do Prometheus, expostas em /metrics."""

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

# --- Método RED: Rate, Errors, Duration ---

HTTP_REQUESTS = Counter(
    "http_requests",  # o prometheus-client adiciona o sufixo _total
    "Total de requisições HTTP",
    ["method", "route", "status"],
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Duração das requisições HTTP em segundos",
    ["method", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Requisições HTTP sendo processadas agora",
)

# --- Métricas de negócio ---

LINKS_CREATED = Counter("links_created", "Total de links curtos criados")
REDIRECTS = Counter("redirects", "Total de redirecionamentos realizados")


router = APIRouter(include_in_schema=False)


@router.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
