def test_pagina_inicial_tem_formulario(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "<form" in response.text


def test_formulario_mostra_link_curto(client):
    response = client.post("/", data={"url": "https://example.com/"})

    assert response.status_code == 200
    assert "Seu link curto" in response.text


def test_formulario_rejeita_url_invalida(client):
    response = client.post("/", data={"url": "nada-a-ver"})

    assert response.status_code == 422
    assert "URL inválida" in response.text
