"""Envio de e-mail. Em dev/test guarda em memória e registra em log; em produção, integrar SMTP do órgão."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from .config import config

log = logging.getLogger("gd.mail")


@dataclass
class Mensagem:
    para: str
    assunto: str
    corpo: str


CAIXA_SAIDA: list[Mensagem] = []


def enviar(para: str, assunto: str, corpo: str) -> None:
    CAIXA_SAIDA.append(Mensagem(para, assunto, corpo))
    del CAIXA_SAIDA[:-100]  # mantém só as 100 últimas
    if config.env in ("dev", "test"):
        log.info("[e-mail simulado] para=%s assunto=%s\n%s", para, assunto, corpo)
    else:
        # Integração SMTP depende de credenciais do órgão: bloqueio registrado no GEC.
        log.warning("Envio de e-mail não configurado para o ambiente %s (para=%s)", config.env, para)
