"""MOD-003 — Upload de PDF."""
import hashlib

from tests.conftest import PDF_MINIMO, criar_doc


def enviar(client, h, did, conteudo, nome="oficio.pdf", tipo="application/pdf"):
    return client.post(f"/api/documentos/{did}/arquivos", files={"arquivo": (nome, conteudo, tipo)}, headers=h)


def test_upload_pdf_valido_e_download_integro(client, usuarios):
    d = criar_doc(client, usuarios["OPERADOR"])
    r = enviar(client, usuarios["OPERADOR"], d["id"], PDF_MINIMO)
    assert r.status_code == 201, r.text
    a = r.json()
    assert a["sha256"] == hashlib.sha256(PDF_MINIMO).hexdigest() and a["tamanho"] == len(PDF_MINIMO)
    dl = client.get(f"/api/arquivos/{a['id']}", headers=usuarios["CONSULTA"])
    assert dl.status_code == 200 and dl.content == PDF_MINIMO
    assert dl.headers["content-type"] == "application/pdf"
    det = client.get(f"/api/documentos/{d['id']}", headers=usuarios["OPERADOR"]).json()
    assert len(det["arquivos"]) == 1


def test_rejeita_extensao_e_conteudo_falso(client, usuarios):
    d = criar_doc(client, usuarios["OPERADOR"])
    assert enviar(client, usuarios["OPERADOR"], d["id"], PDF_MINIMO, nome="a.exe").status_code == 422
    assert enviar(client, usuarios["OPERADOR"], d["id"], b"MZ executavel", nome="falso.pdf").status_code == 422
    assert enviar(client, usuarios["OPERADOR"], d["id"], b"", nome="vazio.pdf").status_code == 422


def test_rejeita_arquivo_acima_do_limite(client, usuarios):
    d = criar_doc(client, usuarios["OPERADOR"])
    grande = PDF_MINIMO + b"0" * (1024 * 1024 + 10)  # MAX_UPLOAD_MB=1 nos testes
    r = enviar(client, usuarios["OPERADOR"], d["id"], grande)
    assert r.status_code == 422 and "limite" in r.json()["detail"]


def test_nome_com_caminho_e_sanitizado(client, usuarios):
    d = criar_doc(client, usuarios["OPERADOR"])
    r = enviar(client, usuarios["OPERADOR"], d["id"], PDF_MINIMO, nome="../../etc/passwd.pdf")
    assert r.status_code == 201
    assert r.json()["nome_original"] == "passwd.pdf"


def test_consulta_nao_envia_e_restrito_nao_baixa(client, usuarios):
    d = criar_doc(client, usuarios["GESTOR"], classificacao="RESTRITO")
    assert enviar(client, usuarios["CONSULTA"], d["id"], PDF_MINIMO).status_code == 403
    a = enviar(client, usuarios["GESTOR"], d["id"], PDF_MINIMO).json()
    assert client.get(f"/api/arquivos/{a['id']}", headers=usuarios["CONSULTA"]).status_code == 404
    assert client.get(f"/api/arquivos/{a['id']}", headers=usuarios["OPERADOR"]).status_code == 200


def test_documento_arquivado_nao_recebe_anexo(client, usuarios):
    d = criar_doc(client, usuarios["GESTOR"])
    client.delete(f"/api/documentos/{d['id']}", headers=usuarios["GESTOR"])
    assert enviar(client, usuarios["GESTOR"], d["id"], PDF_MINIMO).status_code == 409
