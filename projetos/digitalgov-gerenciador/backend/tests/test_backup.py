"""Backup e restauração reais do banco central (pg_dump / pg_restore)."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "infra" / "scripts"


@pytest.mark.skipif(not shutil.which("pg_dump"), reason="pg_dump não instalado")
def test_backup_e_restauracao_do_banco_central(tmp_path, cliente, entrar):
    h = entrar()
    cliente.post("/api/orgaos", headers=h, json={"nome": "Órgão antes do backup"})
    env = {**os.environ, "GERENCIADOR_ARQUIVOS": str(tmp_path / "arquivos")}
    (tmp_path / "arquivos").mkdir()
    (tmp_path / "arquivos" / "edital.pdf").write_bytes(b"%PDF edital")
    r = subprocess.run(["bash", str(SCRIPTS / "backup.sh"), str(tmp_path / "bk")], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    carimbo = next((tmp_path / "bk").glob("backup-*.sha256")).stem.removeprefix("backup-")

    cliente.post("/api/orgaos", headers=h, json={"nome": "Órgão depois do backup"})
    (tmp_path / "arquivos" / "edital.pdf").unlink()
    r = subprocess.run(["bash", str(SCRIPTS / "restore.sh"), str(tmp_path / "bk"), carimbo], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    nomes = [o["nome"] for o in cliente.get("/api/orgaos", headers=entrar("admin2", "ADMIN")).json()]
    assert nomes == ["Órgão antes do backup"]
    assert (tmp_path / "arquivos" / "edital.pdf").read_bytes() == b"%PDF edital"

    (tmp_path / "bk" / f"gerenciador-{carimbo}.dump").write_bytes(b"alterado")
    r = subprocess.run(["bash", str(SCRIPTS / "restore.sh"), str(tmp_path / "bk"), carimbo], capture_output=True, text=True, env=env)
    assert r.returncode != 0 and "SHA-256" in r.stderr
