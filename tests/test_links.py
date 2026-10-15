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
