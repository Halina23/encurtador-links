import io
import json
import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from sqlalchemy import create_engine, text

from app.observability.logging import create_handler
from app.observability.tracing import setup_tracing


def _logger_em_memoria(nome: str) -> tuple[logging.Logger, io.StringIO]:
    stream = io.StringIO()
    logger = logging.getLogger(nome)
    logger.handlers = [create_handler(stream)]
    logger.propagate = False
    # Nível próprio: o alembic (rodado no início da suíte) muda o nível global.
    logger.setLevel(logging.INFO)
    return logger, stream


def test_log_dentro_de_um_span_tem_trace_id():
    logger, stream = _logger_em_memoria("teste.trace")
    tracer = TracerProvider().get_tracer("teste")

    with tracer.start_as_current_span("operacao") as span:
        logger.info("dentro do span")
        esperado = format(span.get_span_context().trace_id, "032x")

    assert json.loads(stream.getvalue())["trace_id"] == esperado


def test_log_fora_de_span_tem_trace_id_vazio():
    logger, stream = _logger_em_memoria("teste.sem_trace")

    logger.info("sem span")

    assert json.loads(stream.getvalue())["trace_id"] is None


def test_tracing_desligado_sem_endpoint(monkeypatch):
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)

    assert setup_tracing(FastAPI(), create_engine("sqlite://")) is None


def test_requisicao_gera_spans_http_e_banco():
    engine = create_engine("sqlite://")
    app = FastAPI()

    @app.get("/consulta")
    def consulta():
        with engine.connect() as conn:
            return {"valor": conn.execute(text("SELECT 1")).scalar()}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    exporter = InMemorySpanExporter()
    try:
        assert setup_tracing(app, engine, exporter=exporter) is not None
        client = TestClient(app)

        assert client.get("/consulta").json() == {"valor": 1}
        client.get("/health")  # rota excluída: não pode gerar span

        spans = exporter.get_finished_spans()
        http = [s for s in spans if s.name == "GET /consulta"]
        banco = [s for s in spans if s.name.startswith("SELECT")]

        assert len(http) == 1
        assert len(banco) == 1
        # O span do banco é filho do span da requisição: mesmo trace.
        assert banco[0].context.trace_id == http[0].context.trace_id
        assert banco[0].parent.span_id == http[0].context.span_id
        assert not any("health" in s.name for s in spans)
    finally:
        SQLAlchemyInstrumentor().uninstrument()
