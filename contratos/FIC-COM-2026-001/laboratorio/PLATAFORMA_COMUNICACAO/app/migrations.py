"""Migrações versionadas do banco (SQL em migrations/NNNN_nome.up.sql e .down.sql).

Cada migração roda numa transação; se sobrar chave estrangeira quebrada, nada é gravado.
Banco criado pela versão original do pacote (sem controle de versão) é reconhecido como versão 1.
"""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1] / 'migrations'
_NOME = re.compile(r'^(\d{4})_(.+)\.up\.sql$')


class ErroMigracao(RuntimeError):
    pass


def disponiveis() -> list[tuple[int, str]]:
    itens = []
    for arq in PASTA.glob('*.up.sql'):
        m = _NOME.match(arq.name)
        if m:
            itens.append((int(m.group(1)), m.group(2)))
    return sorted(itens)


def _arquivo(versao: int, sentido: str) -> Path:
    achados = list(PASTA.glob(f'{versao:04d}_*.{sentido}.sql'))
    if len(achados) != 1:
        raise ErroMigracao(f'migração {versao:04d} sem arquivo .{sentido}.sql único')
    return achados[0]


def _comandos(sql: str) -> list[str]:
    comandos, buf = [], ''
    for linha in sql.splitlines(keepends=True):
        if not buf and linha.strip().startswith('--'):
            continue
        buf += linha
        if sqlite3.complete_statement(buf):
            comandos.append(buf.strip())
            buf = ''
    if buf.strip():
        raise ErroMigracao('SQL incompleto no fim do arquivo')
    return comandos


def _conectar(caminho: Path) -> sqlite3.Connection:
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(caminho), isolation_level=None, timeout=10)
    c.execute('PRAGMA foreign_keys=OFF')
    c.execute('CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL)')
    aplicadas = c.execute('SELECT COUNT(*) FROM schema_migrations').fetchone()[0]
    tem_users = c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
    if not aplicadas and tem_users:  # banco da versão original do pacote
        c.execute("INSERT INTO schema_migrations VALUES (1, 'inicial (reconhecida)', ?)", (_agora(),))
    return c


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _aplicadas(c: sqlite3.Connection) -> list[int]:
    return [r[0] for r in c.execute('SELECT version FROM schema_migrations ORDER BY version')]


def _executar(c: sqlite3.Connection, arquivo: Path, registrar) -> None:
    c.execute('BEGIN')
    try:
        for cmd in _comandos(arquivo.read_text(encoding='utf-8')):
            c.execute(cmd)
        quebradas = c.execute('PRAGMA foreign_key_check').fetchall()
        if quebradas:
            raise ErroMigracao(f'{arquivo.name}: {len(quebradas)} referência(s) quebrada(s); nada foi alterado')
        registrar()
        c.execute('COMMIT')
    except Exception:
        c.execute('ROLLBACK')
        raise


def upgrade(caminho) -> list[int]:
    """Aplica as migrações pendentes; devolve as versões aplicadas agora."""
    c = _conectar(caminho)
    try:
        feitas = set(_aplicadas(c))
        novas = []
        for versao, nome in disponiveis():
            if versao in feitas:
                continue
            _executar(c, _arquivo(versao, 'up'),
                      lambda v=versao, n=nome: c.execute('INSERT INTO schema_migrations VALUES (?,?,?)', (v, n, _agora())))
            novas.append(versao)
        return novas
    finally:
        c.close()


def rollback(caminho, ate: int) -> list[int]:
    """Desfaz, da mais nova para a mais antiga, as migrações acima da versão `ate`."""
    c = _conectar(caminho)
    try:
        desfeitas = []
        for versao in reversed(_aplicadas(c)):
            if versao <= ate:
                break
            _executar(c, _arquivo(versao, 'down'),
                      lambda v=versao: c.execute('DELETE FROM schema_migrations WHERE version=?', (v,)))
            desfeitas.append(versao)
        return desfeitas
    finally:
        c.close()


def status(caminho) -> dict:
    c = _conectar(caminho)
    try:
        feitas = _aplicadas(c)
        return {'atual': max(feitas, default=0), 'aplicadas': feitas,
                'pendentes': [v for v, _ in disponiveis() if v not in feitas]}
    finally:
        c.close()
