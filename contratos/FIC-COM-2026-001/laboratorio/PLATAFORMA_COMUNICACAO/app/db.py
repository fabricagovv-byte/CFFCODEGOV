import os, sqlite3, pathlib
from . import migrations

DB_PATH = pathlib.Path(os.getenv('DG_COMM_DB', str(pathlib.Path(__file__).resolve().parents[1] / 'data' / 'comunicacao.db')))


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB_PATH), timeout=10, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c


def init():
    """Cria ou atualiza o banco pelas migrações versionadas (migrations/)."""
    migrations.upgrade(DB_PATH)
