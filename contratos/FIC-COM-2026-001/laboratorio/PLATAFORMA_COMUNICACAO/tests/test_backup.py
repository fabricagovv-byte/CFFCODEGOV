"""Backup e restauração dos bancos (infra/scripts/backup.sh e restore.sh)."""
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "infra" / "scripts"


def _rodar(script, *args, env):
    return subprocess.run(["bash", str(SCRIPTS / script), *map(str, args)], capture_output=True, text=True, env=env)


def _banco(caminho, linhas):
    with sqlite3.connect(caminho) as c:
        c.execute("CREATE TABLE IF NOT EXISTS t (v TEXT)")
        c.execute("DELETE FROM t")
        c.executemany("INSERT INTO t VALUES (?)", [(x,) for x in linhas])


def _ler(caminho):
    with sqlite3.connect(caminho) as c:
        return [r[0] for r in c.execute("SELECT v FROM t ORDER BY v")]


def test_backup_e_restauracao_devolvem_os_dados(tmp_path):
    com, fab, destino = tmp_path / "com.db", tmp_path / "fab.db", tmp_path / "backups"
    _banco(com, ["a", "b"]); _banco(fab, ["x"])
    env = {**os.environ, "DG_COMM_DB": str(com), "DG_FACTORY_DB": str(fab), "PYTHON": sys.executable}
    r = _rodar("backup.sh", destino, env=env)
    assert r.returncode == 0, r.stderr
    copias = sorted(destino.glob("comunicacao-*.db"))
    assert len(copias) == 1 and sorted(destino.glob("backup-*.sha256"))

    _banco(com, ["perdido"])                                   # simula perda de dados
    r = _rodar("restore.sh", copias[0], com, env=env)
    assert r.returncode == 0, r.stderr
    assert _ler(com) == ["a", "b"]


def test_restauracao_recusa_arquivo_alterado(tmp_path):
    com, fab, destino = tmp_path / "com.db", tmp_path / "fab.db", tmp_path / "backups"
    _banco(com, ["a"]); _banco(fab, ["x"])
    env = {**os.environ, "DG_COMM_DB": str(com), "DG_FACTORY_DB": str(fab), "PYTHON": sys.executable}
    assert _rodar("backup.sh", destino, env=env).returncode == 0
    copia = sorted(destino.glob("comunicacao-*.db"))[0]
    with open(copia, "ab") as f:
        f.write(b"alterado")
    r = _rodar("restore.sh", copia, com, env=env)
    assert r.returncode != 0 and "SHA-256" in (r.stdout + r.stderr)
    assert _ler(com) == ["a"]
