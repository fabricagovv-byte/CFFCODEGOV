"""MOD-003 (base técnica): migrações versionadas com reversão e cabeçalhos de segurança."""
import sqlite3


def _tabelas(caminho):
    with sqlite3.connect(caminho) as c:
        return {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def test_migracoes_em_banco_vazio_e_reversao(tmp_path):
    from app import migrations
    db = tmp_path / 'vazio.db'
    aplicadas = migrations.upgrade(db)
    assert aplicadas == [v for v, _ in migrations.disponiveis()] and len(aplicadas) >= 3
    assert {'users', 'sessions', 'login_attempts', 'schema_migrations'} <= _tabelas(db)
    assert migrations.status(db)['pendentes'] == []
    migrations.rollback(db, ate=1)
    assert 'sessions' not in _tabelas(db) and 'users' in _tabelas(db)
    assert migrations.status(db)['atual'] == 1
    migrations.upgrade(db)
    assert migrations.status(db)['pendentes'] == []


def test_upgrade_e_idempotente(tmp_path):
    from app import migrations
    db = tmp_path / 'x.db'
    migrations.upgrade(db)
    assert migrations.upgrade(db) == []


def test_banco_antigo_do_pacote_e_reconhecido_sem_perder_dados(tmp_path):
    from app import migrations
    db = tmp_path / 'antigo.db'
    sql_original = (migrations.PASTA / '0001_inicial.up.sql').read_text(encoding='utf-8')
    with sqlite3.connect(db) as c:
        c.executescript(sql_original)
        c.execute("INSERT INTO users(name,username,password_hash,role,created_at) VALUES('A','a','x','ADMIN','2026-01-01')")
        c.execute("INSERT INTO channels(name,created_by,created_at) VALUES('Canal',1,'2026-01-01')")
        c.execute("INSERT INTO campaigns(name,objective,channel_id,owner_id,created_at) VALUES('C','O',1,1,'2026-01-01')")
    migrations.upgrade(db)
    with sqlite3.connect(db) as c:
        assert c.execute('SELECT COUNT(*) FROM campaigns').fetchone()[0] == 1
        assert c.execute('SELECT MIN(version) FROM schema_migrations').fetchone()[0] == 1


def test_campanha_tem_chave_estrangeira_para_canal(tmp_path):
    from app import migrations
    db = tmp_path / 'fk.db'
    migrations.upgrade(db)
    with sqlite3.connect(db) as c:
        fks = {(r[2], r[3]) for r in c.execute('PRAGMA foreign_key_list(campaigns)')}
    assert ('channels', 'channel_id') in fks


def test_cabecalhos_de_seguranca(client):
    for caminho in ('/', '/health', '/static/app.js'):
        h = client.get(caminho).headers
        assert "default-src 'self'" in h['content-security-policy'], caminho
        assert "frame-ancestors 'none'" in h['content-security-policy']
        assert h['x-content-type-options'] == 'nosniff' and h['x-frame-options'] == 'DENY'
        assert h['referrer-policy'] == 'no-referrer'


def test_api_nao_fica_em_cache(client):
    assert client.get('/health').headers['cache-control'] == 'no-store'


def test_tela_nao_usa_estilo_inline_bloqueado_pela_csp():
    import pathlib
    js = (pathlib.Path(__file__).resolve().parents[1] / 'static' / 'app.js').read_text(encoding='utf-8')
    assert 'style="' not in js


def test_dependencias_com_versao_fixa():
    import pathlib
    linhas = [l.strip() for l in (pathlib.Path(__file__).resolve().parents[1] / 'requirements.txt').read_text().splitlines() if l.strip() and not l.startswith('#')]
    assert linhas and all('==' in l for l in linhas), linhas
