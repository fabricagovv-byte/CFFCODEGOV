"""Banco relacional persistente, controles de integridade e trilha de auditoria SHA-256."""
import sqlite3, json, hashlib
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'runtime'
DB = DATA / 'fabrica.sqlite3'

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def connect(db_path=None):
    path = Path(db_path) if db_path else DB
    path.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(path, timeout=30, isolation_level=None)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    c.execute('PRAGMA busy_timeout=30000')
    c.execute('PRAGMA journal_mode=WAL')
    return c

SCHEMA = '''
CREATE TABLE IF NOT EXISTS projects (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, macroservice TEXT NOT NULL,
 slug TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'PLANEJADO',
 CHECK(status IN ('PLANEJADO','EM_EXECUCAO','REVISAO','BLOQUEADO','CONCLUIDO'))
);
CREATE TABLE IF NOT EXISTS people (
 id TEXT PRIMARY KEY, name TEXT, role TEXT NOT NULL, seniority TEXT NOT NULL,
 shift_start TEXT, shift_end TEXT, break_minutes INTEGER NOT NULL DEFAULT 60,
 CHECK(break_minutes BETWEEN 0 AND 240)
);
CREATE TABLE IF NOT EXISTS orders (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
 description TEXT NOT NULL, macroservice TEXT NOT NULL, base_target INTEGER NOT NULL,
 factor INTEGER NOT NULL, oversight_person_id TEXT REFERENCES people(id),
 document_ref TEXT NOT NULL, official_order_ref TEXT, catalog_version TEXT,
 status TEXT NOT NULL DEFAULT 'SIMULADA', created_at TEXT NOT NULL,
 CHECK(base_target >= 0), CHECK(factor IN (1,2,3)),
 CHECK(status IN ('SIMULADA','AGUARDANDO_OS','AUTORIZADA','ENCERRADA'))
);
CREATE TABLE IF NOT EXISTS tasks (
 id INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT NOT NULL REFERENCES projects(id),
 order_id TEXT NOT NULL REFERENCES orders(id), description TEXT NOT NULL,
 assignee_kind TEXT NOT NULL CHECK(assignee_kind IN ('AGENTE','HUMANO')),
 assignee TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'ABERTA',
 base_proposed INTEGER NOT NULL DEFAULT 0, evidence_path TEXT, evidence_sha256 TEXT,
 git_commit TEXT, test_result TEXT, created_at TEXT NOT NULL, started_at TEXT, finished_at TEXT,
 reviewed_at TEXT, reviewer TEXT, base_verified INTEGER NOT NULL DEFAULT 0,
 CHECK(base_proposed >= 0), CHECK(base_verified >= 0),
 CHECK(state IN ('ABERTA','EM_EXECUCAO','FINALIZADA','VERIFICADA','REPROVADA'))
);
CREATE TABLE IF NOT EXISTS sessions (
 id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER NOT NULL REFERENCES tasks(id),
 actor_kind TEXT NOT NULL CHECK(actor_kind IN ('AGENTE','HUMANO')),
 actor TEXT NOT NULL, started_at TEXT NOT NULL, ended_at TEXT,
 break_minutes INTEGER NOT NULL DEFAULT 0,
 evidence_path TEXT, CHECK(break_minutes >= 0)
);
CREATE TABLE IF NOT EXISTS acceptances (
 id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL REFERENCES orders(id),
 base_approved INTEGER NOT NULL CHECK(base_approved >= 0),
 authority_name TEXT NOT NULL, document_path TEXT NOT NULL, document_sha256 TEXT NOT NULL,
 approval_at TEXT NOT NULL, UNIQUE(order_id,document_sha256)
);
CREATE TABLE IF NOT EXISTS audit (
 id INTEGER PRIMARY KEY AUTOINCREMENT, recorded_at TEXT NOT NULL, actor TEXT NOT NULL,
 kind TEXT NOT NULL, payload TEXT NOT NULL, previous_hash TEXT NOT NULL,
 chain_hash TEXT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_tasks_order ON tasks(order_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_sessions_task ON sessions(task_id);
CREATE INDEX IF NOT EXISTS idx_audit_kind ON audit(kind);
'''

TEAM = [
 ('H01','Jerlian','Arquitetura e desenvolvimento sênior'),
 ('H02','Ruan','Backend e sustentação sênior'),
 ('H03','Arthur Miguel','Gestão e governança sênior'),
 ('H04','Warley','Frontend e integrações sênior'),
 ('H05','Werverton','DevOps e integrações sênior'),
 ('H06','João Miguel','Dados e IA sênior'),
 ('H07','Warley C.','QA, análise e segurança sênior'),
 ('H08',None,'A definir'), ('H09',None,'A definir'), ('H10',None,'A definir')
]
OS = [
 ('OS-T01',1,'Desenvolvimento de Sistemas',2000,3,'H01'),
 ('OS-T02',2,'Desenvolvimento de Sistemas',2000,3,'H01'),
 ('OS-T03',3,'Sustentação de Sistemas',1500,2,'H02'),
 ('OS-T04',4,'Sustentação de Sistemas',4000,2,'H02'),
 ('OS-T05',5,'Serviços de Integração de Sistemas',2000,3,'H04'),
 ('OS-T06',6,'Testes de Sistemas',1000,2,'H07'),
 ('OS-T07',7,'Análise de Negócios e Processos',1500,2,'H07'),
 ('OS-T08',8,'Implementação DevOps',1000,3,'H05'),
 ('OS-T09',9,'BI e Ciência de Dados',1500,3,'H06'),
 ('OS-T10',10,'Desenvolvimento de IA',1500,3,'H06'),
 ('OS-T11',11,'Gerenciamento de Projetos',1000,3,'H03'),
 ('OS-T12',12,'Serviços para Jornada do Cidadão',1000,2,'H04'),
 ('OS-T13',13,'Governança de TI',1000,3,'H03'),
 ('OS-T14',14,'Gestão de Segurança da Informação',1000,3,'H07'),
 ('OS-T15',15,'Serviços de Integração de Sistemas',1000,3,'H05')
]

def append_audit(c, actor, kind, payload):
    previous = c.execute('SELECT chain_hash FROM audit ORDER BY id DESC LIMIT 1').fetchone()
    ph = previous['chain_hash'] if previous else 'GENESIS'
    ts = now()
    p = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',',':'))
    digest = hashlib.sha256((ph+'|'+ts+'|'+actor+'|'+kind+'|'+p).encode()).hexdigest()
    c.execute('INSERT INTO audit(recorded_at,actor,kind,payload,previous_hash,chain_hash) VALUES (?,?,?,?,?,?)', (ts,actor,kind,p,ph,digest))
    return digest

def init(c):
    c.executescript(SCHEMA)
    existing = c.execute('SELECT count(*) x FROM projects').fetchone()['x']
    if existing:
        return False
    c.execute('BEGIN IMMEDIATE')
    try:
        for pid,name,role in TEAM:
            c.execute('INSERT INTO people(id,name,role,seniority,shift_start,shift_end) VALUES(?,?,?,?,?,?)', (pid,name,role,'SÊNIOR - A CONFIRMAR','09:00','18:00'))
        for osid,num,macro,base,factor,person in OS:
            proj=f'SYS-{num:02d}'
            c.execute('INSERT INTO projects(id,name,macroservice,slug,created_at) VALUES(?,?,?,?,?)',(proj,f'Laboratório {macro} {num:02d}',macro,proj,now()))
            c.execute('INSERT INTO orders(id,project_id,description,macroservice,base_target,factor,oversight_person_id,document_ref,created_at) VALUES(?,?,?,?,?,?,?,?,?)',(osid,proj,'OS SIMULADA — sem autorização externa ou medição oficial',macro,base,factor,person,'PE223/2026, TR 1.3, 1.3.1, 1.3.2, 7, 10',now()))
        append_audit(c,'SISTEMA','LABORATORIO_INICIALIZADO',{'projetos':15,'meta_ust':60000,'medida_ust':0,'nota':'15 OS hipotéticas, não oficiais'})
        c.execute('COMMIT')
    except Exception:
        c.execute('ROLLBACK')
        raise
    return True

def integrity_check(c):
    rows = c.execute('SELECT * FROM audit ORDER BY id').fetchall()
    previous='GENESIS'
    for r in rows:
        if r['previous_hash']!=previous: return False
        digest=hashlib.sha256((previous+'|'+r['recorded_at']+'|'+r['actor']+'|'+r['kind']+'|'+r['payload']).encode()).hexdigest()
        if digest!=r['chain_hash']: return False
        previous=digest
    return True
