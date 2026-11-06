"""Totais de horas e inconsistências. Só lê os lançamentos: nunca os altera."""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Iterable

from ..modelos import LancamentoHoras


def horas_liquidas(l: LancamentoHoras) -> float:
    minutos = (l.fim.hour * 60 + l.fim.minute) - (l.inicio.hour * 60 + l.inicio.minute) - l.intervalo_min
    return round(minutos / 60, 2)


def resumo(lancamentos: Iterable[LancamentoHoras], aceitos: set[int]) -> dict[str, Any]:
    """Totais separados: horas humanas registradas, horas humanas aceitas e horas de IA."""
    por_dia: dict[tuple, dict[str, float]] = defaultdict(lambda: {"humanas": 0.0, "aceitas": 0.0, "ia": 0.0})
    por_mes: dict[tuple, dict[str, float]] = defaultdict(lambda: {"humanas": 0.0, "aceitas": 0.0, "ia": 0.0})
    total = {"humanas": 0.0, "aceitas": 0.0, "ia": 0.0}
    for l in lancamentos:
        h = horas_liquidas(l)
        quem = ("profissional", l.profissional_id) if l.tipo == "HUMANA" else ("agente", l.agente_id)
        chaves = [("ia",)] if l.tipo == "IA" else [("humanas",)] + ([("aceitas",)] if l.id in aceitos else [])
        for (campo,) in chaves:
            por_dia[(*quem, l.data.isoformat())][campo] += h
            por_mes[(*quem, l.data.strftime("%Y-%m"))][campo] += h
            total[campo] += h
    arredonda = lambda d: {k: round(v, 2) for k, v in d.items()}  # noqa: E731
    return {
        "total": arredonda(total),
        "por_dia": [{"tipo": k[0], "id": k[1], "data": k[2], **arredonda(v)} for k, v in sorted(por_dia.items(), key=lambda i: (i[0][2], str(i[0][1])))],
        "por_mes": [{"tipo": k[0], "id": k[1], "mes": k[2], **arredonda(v)} for k, v in sorted(por_mes.items(), key=lambda i: (i[0][2], str(i[0][1])))],
    }


def inconsistencias(lancamentos: list[LancamentoHoras], jornada: float, inativos: set[int],
                    hoje: date | None = None) -> list[dict[str, Any]]:
    """Aponta problemas para o responsável conferir. Não corrige nada."""
    hoje = hoje or date.today()
    achados: list[dict[str, Any]] = []
    humanas = [l for l in lancamentos if l.tipo == "HUMANA"]
    por_pessoa_dia: dict[tuple, list[LancamentoHoras]] = defaultdict(list)
    for l in humanas:
        por_pessoa_dia[(l.profissional_id, l.data)].append(l)
        if l.data > hoje:
            achados.append({"tipo": "DATA_FUTURA", "lancamentos": [l.id], "mensagem": f"Lançamento em data futura ({l.data:%d/%m/%Y})"})
        if l.data.weekday() >= 5:
            achados.append({"tipo": "FIM_DE_SEMANA", "lancamentos": [l.id], "mensagem": f"Trabalho em fim de semana ({l.data:%d/%m/%Y})"})
        if l.profissional_id in inativos:
            achados.append({"tipo": "PROFISSIONAL_INATIVO", "lancamentos": [l.id], "mensagem": "Lançamento para profissional inativo"})
    for (pessoa, dia), itens in por_pessoa_dia.items():
        itens.sort(key=lambda x: x.inicio)
        for a, b in zip(itens, itens[1:]):
            if b.inicio < a.fim:
                achados.append({"tipo": "SOBREPOSICAO", "lancamentos": [a.id, b.id], "profissional_id": pessoa,
                                "mensagem": f"Horários sobrepostos em {dia:%d/%m/%Y} ({a.inicio:%H:%M}-{a.fim:%H:%M} e {b.inicio:%H:%M}-{b.fim:%H:%M})"})
        soma = round(sum(horas_liquidas(x) for x in itens), 2)
        if soma > 12:
            achados.append({"tipo": "JORNADA_EXCESSIVA", "lancamentos": [x.id for x in itens], "profissional_id": pessoa,
                            "mensagem": f"{soma} h em {dia:%d/%m/%Y} (acima de 12 h)"})
        elif soma > jornada:
            achados.append({"tipo": "ACIMA_DA_JORNADA", "lancamentos": [x.id for x in itens], "profissional_id": pessoa,
                            "mensagem": f"{soma} h em {dia:%d/%m/%Y} (jornada de {jornada:g} h)"})
    return achados
