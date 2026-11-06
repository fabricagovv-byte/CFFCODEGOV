"""MOD-004 — Pesquisa."""
from tests.conftest import PDF_MINIMO, criar_doc


def _ids(r):
    assert r.status_code == 200, r.text
    return {d["id"] for d in r.json()["itens"]}


def test_pesquisa_por_titulo_assunto_interessado_e_numero(client, usuarios):
    h = usuarios["GESTOR"]
    a = criar_doc(client, h, titulo="Ofício sobre merenda escolar", assunto="Cardápio", interessado="Escola Alfa")
    b = criar_doc(client, h, titulo="Portaria de férias", tipo="Portaria", assunto="Escala de férias", interessado="RH")
    assert _ids(client.get("/api/pesquisa?q=merenda", headers=h)) == {a["id"]}
    assert _ids(client.get("/api/pesquisa?q=FÉRIAS", headers=h)) == {b["id"]}
    assert _ids(client.get("/api/pesquisa?q=alfa", headers=h)) == {a["id"]}
    assert _ids(client.get(f"/api/pesquisa?q={a['numero']}", headers=h)) == {a["id"]}


def test_varios_termos_combinam_com_e(client, usuarios):
    h = usuarios["GESTOR"]
    a = criar_doc(client, h, titulo="Ofício merenda escola", assunto="")
    criar_doc(client, h, titulo="Ofício transporte escola", assunto="")
    assert _ids(client.get("/api/pesquisa?q=escola merenda", headers=h)) == {a["id"]}


def test_pesquisa_por_nome_do_arquivo(client, usuarios):
    h = usuarios["GESTOR"]
    d = criar_doc(client, h, titulo="Sem pista no título")
    client.post(f"/api/documentos/{d['id']}/arquivos", files={"arquivo": ("relatorio-anual-2026.pdf", PDF_MINIMO, "application/pdf")}, headers=h)
    assert _ids(client.get("/api/pesquisa?q=anual-2026", headers=h)) == {d["id"]}


def test_filtros_tipo_status_e_curingas_escapados(client, usuarios):
    h = usuarios["GESTOR"]
    a = criar_doc(client, h, tipo="Portaria", titulo="Portaria 100%")
    b = criar_doc(client, h, tipo="Ofício", titulo="Ofício comum")
    client.delete(f"/api/documentos/{b['id']}", headers=h)
    assert _ids(client.get("/api/pesquisa?tipo=Portaria", headers=h)) == {a["id"]}
    assert _ids(client.get("/api/pesquisa?status=ARQUIVADO", headers=h)) == {b["id"]}
    assert _ids(client.get("/api/pesquisa?q=%25", headers=h)) == {a["id"]}  # '%' literal, não curinga


def test_pesquisa_respeita_classificacao(client, usuarios):
    criar_doc(client, usuarios["GESTOR"], titulo="Parecer sigiloso alfa", classificacao="SIGILOSO")
    assert _ids(client.get("/api/pesquisa?q=alfa", headers=usuarios["CONSULTA"])) == set()
    assert len(_ids(client.get("/api/pesquisa?q=alfa", headers=usuarios["GESTOR"]))) == 1


def test_filtro_por_data_e_tipos(client, usuarios):
    h = usuarios["GESTOR"]
    criar_doc(client, h, tipo="Memorando")
    assert len(_ids(client.get("/api/pesquisa?de=2000-01-01", headers=h))) == 1
    assert _ids(client.get("/api/pesquisa?ate=2000-01-01", headers=h)) == set()
    assert client.get("/api/pesquisa/tipos", headers=h).json() == ["Memorando"]
