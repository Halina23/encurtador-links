"""Traces distribuídos com OpenTelemetry.

Cada requisição vira um trace: um span para a requisição HTTP e um span filho
para cada consulta ao banco. Os spans são enviados por OTLP/HTTP para o endereço
em OTEL_EXPORTER_OTLP_ENDPOINT (no cluster, o Alloy, que repassa ao Tempo).

Sem essa variável, o tracing fica desligado: em desenvolvimento e nos testes a
aplicação funciona normalmente, sem tentar enviar spans para lugar nenhum.
"""

import logging
import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, SpanExporter
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

# Rotas que não geram trace: são chamadas o tempo todo pelo Kubernetes e pelo
# Prometheus e só encheriam o Tempo de ruído (o mesmo critério dos logs de acesso).
EXCLUDED_URLS = "/health$,/ready$,/metrics$"


def setup_tracing(
    app: FastAPI,
    engine: Engine,
    exporter: SpanExporter | None = None,
) -> TracerProvider | None:
    """Liga o tracing da aplicação e do banco. Devolve o provider, ou None se desligado.

    exporter: usado nos testes (ex.: InMemorySpanExporter). Sem ele, usa o OTLP,
    configurado pelas variáveis padrão OTEL_EXPORTER_OTLP_* e OTEL_SERVICE_NAME.
    """
    if exporter is None and not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        logger.info("traces desligados (OTEL_EXPORTER_OTLP_ENDPOINT vazio)")
        return None

    resource = Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "encurtador")})
    provider = TracerProvider(resource=resource)

    if exporter is None:
        # Batch: junta os spans e envia em lotes, sem atrasar as requisições.
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(provider)
    else:
        # Simple: envia na hora, para o teste ver os spans logo após a requisição.
        provider.add_span_processor(SimpleSpanProcessor(exporter))

    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=provider,
        excluded_urls=EXCLUDED_URLS,
        # Sem os spans internos de "receive"/"send" do ASGI, que só poluem o trace.
        exclude_spans=["receive", "send"],
    )
    # skip_dep_check: a instrumentação declara suporte só até o SQLAlchemy 2.0, mas
    # funciona por eventos (before/after_cursor_execute), que seguem iguais na 2.1.
    # O teste test_requisicao_gera_spans_http_e_banco garante que os spans saem.
    SQLAlchemyInstrumentor().instrument(
        engine=engine, tracer_provider=provider, skip_dep_check=True
    )

    logger.info("traces ligados", extra={"service": resource.attributes["service.name"]})
    return provider
