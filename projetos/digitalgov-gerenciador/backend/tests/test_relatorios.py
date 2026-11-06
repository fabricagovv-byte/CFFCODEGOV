import io

from docx import Document
from openpyxl import load_workbook


def _dados(cliente, base):
    h, ct = base["h"], base["contrato"]
    p = cliente.post("/api/profissionais", headers=h, json={"nome": "Jerlian", "cargo": "Programador"}).json()["id"]
    cliente.post("/api/horas", headers=h, json={"tipo": "HUMANA", "profissional_id": p, "data": "2026-11-04", "inicio": "09:00",
                                               "fim": "18:00", "intervalo_min": 60, "atividade": "Revisão do módulo de sessão"})
    cliente.post("/api/medicoes", headers=h, json={"contrato_id": ct["id"], "item": "CAT-M01-02", "descricao": "Controle de sessão",
                                                  "quantidade": 202.5, "data_execucao": "2026-11-06"})


def test_relatorio_de_horas_em_word_pdf_e_excel(cliente, base):
    _dados(cliente, base)
    h = base["h"]
    docx = cliente.get("/api/relatorios/horas.docx?mes=2026-11", headers=h)
    texto = "\n".join(p.text for p in Document(io.BytesIO(docx.content)).paragraphs)
    tabelas = " ".join(c.text for t in Document(io.BytesIO(docx.content)).tables for r in t.rows for c in r.cells)
    assert "Relatório de horas" in texto and "Jerlian" in tabelas and "8" in tabelas
    pdf = cliente.get("/api/relatorios/horas.pdf?mes=2026-11", headers=h)
    assert pdf.headers["content-type"] == "application/pdf" and pdf.content.startswith(b"%PDF")
    xlsx = load_workbook(io.BytesIO(cliente.get("/api/relatorios/horas.xlsx?mes=2026-11", headers=h).content))
    assert "Totais do mês" in xlsx.sheetnames and xlsx["Totais do mês"]["A2"].value == 8


def test_relatorio_de_medicao(cliente, base):
    _dados(cliente, base)
    h, ct = base["h"], base["contrato"]
    docx = cliente.get(f"/api/relatorios/medicao/{ct['id']}.docx", headers=h)
    celulas = " ".join(c.text for t in Document(io.BytesIO(docx.content)).tables for r in t.rows for c in r.cells)
    assert "202.5 UST" in celulas and "R$ 6.075,00" in celulas and "797.5 UST" in celulas
    assert cliente.get(f"/api/relatorios/medicao/{ct['id']}.pdf", headers=h).content.startswith(b"%PDF")
    assert cliente.get(f"/api/relatorios/medicao/{ct['id']}.txt", headers=h).status_code == 422


def test_exportar_cadastros_para_excel(cliente, base):
    _dados(cliente, base)
    h = base["h"]
    for cadastro in ("contratos", "profissionais", "medicoes", "horas"):
        wb = load_workbook(io.BytesIO(cliente.get(f"/api/relatorios/exportar/{cadastro}.xlsx", headers=h).content))
        assert wb.active.max_row >= 2, cadastro
    assert cliente.get("/api/relatorios/exportar/senhas.xlsx", headers=h).status_code == 404


def test_painel(cliente, base):
    _dados(cliente, base)
    r = cliente.get("/api/painel", headers=base["h"]).json()
    assert r["contratos"] == 1 and r["contratos_resumo"][0]["executado"] == 202.5
