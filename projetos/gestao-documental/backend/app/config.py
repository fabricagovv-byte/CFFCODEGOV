"""Configuração por variáveis de ambiente (12-factor). Nenhum segredo no código."""
from __future__ import annotations

import logging
import os
import secrets
from dataclasses import dataclass, field

log = logging.getLogger("gd.config")


def _lista(valor: str) -> list[str]:
    return [v.strip() for v in valor.split(",") if v.strip()]


@dataclass(frozen=True)
class Config:
    env: str = field(default_factory=lambda: os.getenv("APP_ENV", "dev"))
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./dev.db"))
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", ""))
    jwt_expira_min: int = field(default_factory=lambda: int(os.getenv("JWT_EXPIRA_MIN", "60")))
    upload_dir: str = field(default_factory=lambda: os.getenv("UPLOAD_DIR", "./uploads"))
    max_upload_mb: int = field(default_factory=lambda: int(os.getenv("MAX_UPLOAD_MB", "20")))
    cors_origins: list[str] = field(default_factory=lambda: _lista(os.getenv("CORS_ORIGINS", "http://localhost:5173")))
    url_publica: str = field(default_factory=lambda: os.getenv("URL_PUBLICA", "http://localhost:5173"))
    login_max_tentativas: int = field(default_factory=lambda: int(os.getenv("LOGIN_MAX_TENTATIVAS", "5")))
    login_bloqueio_min: int = field(default_factory=lambda: int(os.getenv("LOGIN_BLOQUEIO_MIN", "15")))

    def validar(self) -> "Config":
        if self.env in ("prod", "homologacao") and len(self.jwt_secret) < 32:
            raise RuntimeError("JWT_SECRET obrigatório (>= 32 caracteres) em homologação/produção")
        return self


def carregar() -> Config:
    cfg = Config().validar()
    if not cfg.jwt_secret:
        # Somente dev/test: segredo efêmero (tokens perdem validade ao reiniciar).
        object.__setattr__(cfg, "jwt_secret", secrets.token_urlsafe(48))
        log.warning("JWT_SECRET não definido: usando segredo efêmero (apenas dev/test)")
    return cfg


config = carregar()
