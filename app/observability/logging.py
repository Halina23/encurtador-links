"""Logs estruturados em JSON, escritos no stdout (12-Factor)."""

import logging
import sys
from contextvars import ContextVar
from typing import TextIO

from pythonjsonlogger.json import JsonFormatter

# Guarda o request_id da requisição atual. Cada requisição tem o seu próprio
# valor, mesmo com várias acontecendo ao mesmo tempo.
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """Adiciona o request_id da requisição atual em todo log."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        # O uvicorn anexa uma cópia da mensagem com códigos de cor do terminal.
        record.__dict__.pop("color_message", None)
        return True


def create_handler(stream: TextIO) -> logging.Handler:
    handler = logging.StreamHandler(stream)
    handler.setFormatter(
        JsonFormatter(
            "%(levelname)s %(name)s %(message)s %(request_id)s",
            rename_fields={"levelname": "level", "name": "logger"},
            timestamp=True,
            json_ensure_ascii=False,  # mantém acentos legíveis
        )
    )
    handler.addFilter(RequestIdFilter())
    return handler


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.handlers = [create_handler(sys.stdout)]
    root.setLevel(level.upper())

    # Os logs do uvicorn passam a sair pelo nosso handler, em JSON.
    for name in ("uvicorn", "uvicorn.error"):
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # O log de acesso em texto do uvicorn é substituído pelo do nosso middleware.
    logging.getLogger("uvicorn.access").disabled = True
