import io
import json
import logging

from prometheus_client import REGISTRY

from app.observability.logging import create_handler, request_id_var


def _sample(name: str, labels: dict | None = None) -> float:
    return REGISTRY.get_sample_value(name, labels or {}) or 0.0


def test_metrics_expoe_formato_prometheus(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "http_requests_total" in response.text


def test_requisicao_incrementa_contador_com_rota_modelo(client):
    labels = {"method": "GET", "route": "/{code}", "status": "404"}
    antes = _sample("http_requests_total", labels)

    client.get("/codigo-que-nao-existe")

    # A label usa o modelo /{code}, e não o valor digitado na URL.
    assert _sample("http_requests_total", labels) == antes + 1


def test_duracao_e_registrada_no_histograma(client):
    labels = {"method": "GET", "route": "/health"}
    antes = _sample("http_request_duration_seconds_count", labels)

    client.get("/health")

    assert _sample("http_request_duration_seconds_count", labels) == antes + 1


def test_metricas_de_negocio(client):
    criados_antes = _sample("links_created_total")
    redirects_antes = _sample("redirects_total")

    code = client.post("/api/links", json={"url": "https://example.com/"}).json()["code"]
    client.get(f"/{code}")

    assert _sample("links_created_total") == criados_antes + 1
    assert _sample("redirects_total") == redirects_antes + 1


def test_resposta_tem_request_id(client):
    gerado = client.get("/health").headers["x-request-id"]
    reaproveitado = client.get("/health", headers={"X-Request-ID": "abc-123"}).headers[
        "x-request-id"
    ]

    assert len(gerado) == 32
    assert reaproveitado == "abc-123"


def test_log_sai_em_json_com_request_id():
    stream = io.StringIO()
    logger = logging.getLogger("teste.json")
    logger.addHandler(create_handler(stream))
    logger.propagate = False

    token = request_id_var.set("req-42")
    logger.warning("algo aconteceu", extra={"code": "abc1234"})
    request_id_var.reset(token)

    log = json.loads(stream.getvalue())
    assert log["level"] == "WARNING"
    assert log["message"] == "algo aconteceu"
    assert log["request_id"] == "req-42"
    assert log["code"] == "abc1234"
    assert "timestamp" in log
