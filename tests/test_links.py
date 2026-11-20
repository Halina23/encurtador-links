def test_cria_link_curto(client):
    response = client.post("/api/links", json={"url": "https://example.com/pagina/muito/comprida"})

    assert response.status_code == 201
    body = response.json()
    assert len(body["code"]) == 7
    assert body["short_url"].endswith(f"/{body['code']}")
    assert body["target_url"] == "https://example.com/pagina/muito/comprida"
    assert body["clicks"] == 0


def test_rejeita_url_invalida(client):
    response = client.post("/api/links", json={"url": "isso não é uma url"})

    assert response.status_code == 422


def test_redireciona_e_registra_clique(client):
    code = client.post("/api/links", json={"url": "https://example.com/"}).json()["code"]

    response = client.get(f"/{code}")

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/"
    assert client.get(f"/api/links/{code}").json()["clicks"] == 1


def test_codigo_inexistente_retorna_404(client):
    assert client.get("/naoexiste").status_code == 404
    assert client.get("/api/links/naoexiste").status_code == 404


def test_codigos_sao_unicos(client):
    codes = {
        client.post("/api/links", json={"url": "https://example.com/"}).json()["code"]
        for _ in range(20)
    }

    assert len(codes) == 20


def test_short_url_usa_endereco_da_requisicao_sem_base_url(client, monkeypatch):
    monkeypatch.setattr("app.services.settings.base_url", "")

    body = client.post(
        "/api/links", json={"url": "https://example.com/"}, headers={"Host": "203.0.113.10"}
    ).json()

    assert body["short_url"] == f"http://203.0.113.10/{body['code']}"


def test_short_url_usa_base_url_quando_definido(client, monkeypatch):
    monkeypatch.setattr("app.services.settings.base_url", "https://encurta.exemplo.com/")

    body = client.post("/api/links", json={"url": "https://example.com/"}).json()

    assert body["short_url"] == f"https://encurta.exemplo.com/{body['code']}"
