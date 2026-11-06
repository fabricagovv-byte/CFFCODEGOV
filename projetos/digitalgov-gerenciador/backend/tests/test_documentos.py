import hashlib
import os
from pathlib import Path


def _enviar(cliente, h, contrato_id, nome="edital.pdf", conteudo=b"%PDF-1.4 edital", tipo="EDITAL"):
    return cliente.post("/api/documentos", headers=h, data={"tipo": tipo, "titulo": "Edital do pregão", "contrato_id": str(contrato_id)},
                        files={"arquivo": (nome, conteudo, "application/pdf")})


def test_anexar_e_baixar_edital(cliente, base):
    h, ct = base["h"], base["contrato"]
    r = _enviar(cliente, h, ct["id"])
    assert r.status_code == 201 and r.json()["sha256"] == hashlib.sha256(b"%PDF-1.4 edital").hexdigest()
    assert "caminho" not in r.json()
    baixado = cliente.get(f"/api/documentos/{r.json()['id']}/arquivo", headers=h)
    assert baixado.status_code == 200 and baixado.content == b"%PDF-1.4 edital"
    assert cliente.get(f"/api/documentos?contrato_id={ct['id']}", headers=h).json()[0]["tipo"] == "EDITAL"


def test_recusa_formato_tamanho_e_tipo(cliente, base):
    h, ct = base["h"], base["contrato"]
    assert _enviar(cliente, h, ct["id"], nome="virus.exe").status_code == 422
    assert _enviar(cliente, h, ct["id"], conteudo=b"x" * (1024 * 1024 + 10)).status_code == 413
    assert _enviar(cliente, h, ct["id"], tipo="QUALQUER").status_code == 422


def test_arquivo_alterado_no_disco_e_recusado(cliente, base):
    h, ct = base["h"], base["contrato"]
    doc = _enviar(cliente, h, ct["id"]).json()
    pasta = Path(os.environ["GERENCIADOR_ARQUIVOS"])
    arquivo = max(pasta.iterdir(), key=lambda p: p.stat().st_mtime)
    arquivo.write_bytes(b"adulterado")
    assert cliente.get(f"/api/documentos/{doc['id']}/arquivo", headers=h).status_code == 409
