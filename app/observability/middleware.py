"""Middleware que envolve toda requisição: request_id, métricas e log de acesso."""

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from app.observability.logging import request_id_var
from app.observability.metrics import (
    HTTP_REQUEST_DURATION,
    HTTP_REQUESTS,
    HTTP_REQUESTS_IN_PROGRESS,
)

logger = logging.getLogger("app.access")

# Chamadas automáticas e frequentes (Prometheus e probes do Kubernetes).
# Continuam sendo medidas, mas não geram log, para não poluir.
QUIET_PATHS = {"/metrics", "/health", "/ready"}


def _route_template(request: Request) -> str:
    """Devolve o modelo da rota (ex.: /{code}), nunca o valor real (/abc1234).

    Usar o valor real como label explodiria a cardinalidade das métricas.
    """
    route = request.scope.get("route")
    return getattr(route, "path", "<sem rota>")


async def observability_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    # Reaproveita o ID se ele já vier de um proxy na frente da app.
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    token = request_id_var.set(request_id)

    HTTP_REQUESTS_IN_PROGRESS.inc()
    start = time.perf_counter()
    status = 500  # se der exceção, é registrada como erro do servidor
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        duration = time.perf_counter() - start
        route = _route_template(request)

        HTTP_REQUESTS_IN_PROGRESS.dec()
        HTTP_REQUESTS.labels(request.method, route, str(status)).inc()
        HTTP_REQUEST_DURATION.labels(request.method, route).observe(duration)

        if request.url.path not in QUIET_PATHS:
            logger.info(
                "requisição atendida",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "route": route,
                    "status": status,
                    "duration_ms": round(duration * 1000, 2),
                },
            )
        request_id_var.reset(token)
