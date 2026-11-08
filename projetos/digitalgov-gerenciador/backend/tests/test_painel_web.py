def test_painel_web_e_servido_com_politica_de_seguranca(cliente):
    r = cliente.get("/")
    assert r.status_code == 200 and "Gerenciador Central DigitalGov" in r.text
    assert "script-src 'self'" in r.headers["content-security-policy"]
    assert cliente.get("/static/app.js").status_code == 200
    assert cliente.get("/static/style.css").status_code == 200
