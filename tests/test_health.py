def test_health_responde_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_verifica_banco(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
