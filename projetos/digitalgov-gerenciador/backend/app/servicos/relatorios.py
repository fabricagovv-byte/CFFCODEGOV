"""Relatórios em Word, PDF e Excel montados a partir do banco central."""
from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from docx import Document as DocxDocument
from docx.shared import Pt
from fpdf import FPDF
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


class Relatorio:
    """Conteúdo neutro: título, linhas de identificação, seções com texto e tabelas."""

    def __init__(self, titulo: str, subtitulo: str = "") -> None:
        self.titulo, self.subtitulo = titulo, subtitulo
        self.partes: list[tuple[str, Any]] = []

    def secao(self, nome: str) -> "Relatorio":
        self.partes.append(("secao", nome)); return self

    def texto(self, txt: str) -> "Relatorio":
        self.partes.append(("texto", txt)); return self

    def tabela(self, cabecalho: list[str], linhas: list[list[Any]]) -> "Relatorio":
        self.partes.append(("tabela", (cabecalho, [[_txt(c) for c in l] for l in linhas]))); return self

    # ---------------- Word
    def word(self) -> bytes:
        doc = DocxDocument()
        doc.styles["Normal"].font.name = "Calibri"
        doc.styles["Normal"].font.size = Pt(10)
        doc.add_heading(self.titulo, 0)
        if self.subtitulo:
            doc.add_paragraph(self.subtitulo)
        for tipo, valor in self.partes:
            if tipo == "secao":
                doc.add_heading(valor, 1)
            elif tipo == "texto":
                doc.add_paragraph(valor)
            else:
                cab, linhas = valor
                t = doc.add_table(rows=1, cols=len(cab))
                t.style = "Light Grid Accent 1"
                for cel, txt in zip(t.rows[0].cells, cab):
                    cel.text = txt
                for linha in linhas:
                    for cel, txt in zip(t.add_row().cells, linha):
                        cel.text = txt
        doc.add_paragraph(f"Gerado em {datetime.now():%d/%m/%Y %H:%M} pelo Gerenciador Central DigitalGov.")
        saida = io.BytesIO()
        doc.save(saida)
        return saida.getvalue()

    # ---------------- PDF
    def pdf(self) -> bytes:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 15)
        pdf.multi_cell(0, 8, _latin(self.titulo), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        if self.subtitulo:
            pdf.multi_cell(0, 6, _latin(self.subtitulo), new_x="LMARGIN", new_y="NEXT")
        for tipo, valor in self.partes:
            if tipo == "secao":
                pdf.ln(3); pdf.set_font("Helvetica", "B", 12)
                pdf.multi_cell(0, 7, _latin(valor), new_x="LMARGIN", new_y="NEXT"); pdf.set_font("Helvetica", "", 10)
            elif tipo == "texto":
                pdf.multi_cell(0, 5, _latin(valor), new_x="LMARGIN", new_y="NEXT")
            else:
                cab, linhas = valor
                pdf.set_font("Helvetica", "", 8)
                with pdf.table(text_align="LEFT", line_height=4.5) as tabela:
                    for i, linha in enumerate([cab] + linhas):
                        r = tabela.row()
                        for cel in linha:
                            r.cell(_latin(cel))
                pdf.set_font("Helvetica", "", 10)
                pdf.ln(2)
        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 8)
        pdf.multi_cell(0, 4, _latin(f"Gerado em {datetime.now():%d/%m/%Y %H:%M} pelo Gerenciador Central DigitalGov."))
        return bytes(pdf.output())

    # ---------------- Excel
    def excel(self) -> bytes:
        wb = Workbook()
        wb.remove(wb.active)
        n = 0
        for tipo, valor in self.partes:
            if tipo != "tabela":
                continue
            n += 1
            titulo = next((v for t, v in reversed(self.partes[: self.partes.index((tipo, valor))]) if t == "secao"), f"Tabela {n}")
            ws = wb.create_sheet(_aba(titulo, n))
            cab, linhas = valor
            ws.append(cab)
            for linha in linhas:
                ws.append([_numero(c) for c in linha])
            for cel in ws[1]:
                cel.font = Font(bold=True, color="FFFFFF")
                cel.fill = PatternFill("solid", fgColor="1F4E79")
            for i, _ in enumerate(cab, 1):
                ws.column_dimensions[get_column_letter(i)].width = max(12, min(60, max(len(str(c.value or "")) for c in ws[get_column_letter(i)]) + 2))
            ws.freeze_panes = "A2"
        if not wb.sheetnames:
            wb.create_sheet("Vazio").append(["Sem dados"])
        saida = io.BytesIO()
        wb.save(saida)
        return saida.getvalue()


def _txt(v: Any) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(v)


def _latin(txt: str) -> str:
    """As fontes padrão do PDF usam Latin-1 (acentos do português incluídos)."""
    return str(txt).replace("—", "-").replace("–", "-").replace("·", "-").replace("→", "->").encode("latin-1", "replace").decode("latin-1")


def _numero(txt: str) -> Any:
    try:
        return float(txt.replace(".", "").replace(",", ".")) if any(ch.isdigit() for ch in txt) and txt.replace(".", "").replace(",", "").replace("-", "").isdigit() else txt
    except ValueError:
        return txt


def _aba(nome: str, n: int) -> str:
    limpo = "".join(ch for ch in nome if ch not in "[]:*?/\\")[:28]
    return limpo or f"Tabela {n}"


def brl(v: float | None) -> str:
    return "—" if v is None else "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
