import os,sqlite3,pathlib
DB=pathlib.Path(os.getenv('DG_FACTORY_DB',str(pathlib.Path(__file__).resolve().parents[1]/'data'/'factory.db')))
SCHEMA='''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS contracts(id TEXT PRIMARY KEY,title TEXT NOT NULL,contract_type TEXT NOT NULL,scope TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'RASCUNHO',ust_target INTEGER DEFAULT 0,approved_at TEXT,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,contract_id TEXT NOT NULL,name TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'PLANEJADO',folder TEXT NOT NULL,FOREIGN KEY(contract_id) REFERENCES contracts(id));
CREATE TABLE IF NOT EXISTS people(id INTEGER PRIMARY KEY, name TEXT NOT NULL,seniority TEXT DEFAULT 'SÊNIOR',role TEXT NOT NULL,active INTEGER DEFAULT 1,cpf_masked TEXT DEFAULT '',created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY,contract_id TEXT NOT NULL,name TEXT NOT NULL,ust_target INTEGER NOT NULL,complexity_catalog TEXT NOT NULL,authorized INTEGER NOT NULL DEFAULT 0,FOREIGN KEY(contract_id) REFERENCES contracts(id));
CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY,project_id TEXT NOT NULL,order_id TEXT NOT NULL,title TEXT NOT NULL,description TEXT NOT NULL,service TEXT NOT NULL,base_planned REAL NOT NULL DEFAULT 0,factor INTEGER NOT NULL DEFAULT 1 CHECK(factor IN (1,2,3)),status TEXT NOT NULL DEFAULT 'PLANEJADA',started_at TEXT,ended_at TEXT,evidence_path TEXT,evidence_sha256 TEXT,tests_result TEXT,verified_by TEXT,verified_at TEXT,FOREIGN KEY(project_id) REFERENCES projects(id),FOREIGN KEY(order_id) REFERENCES orders(id));
CREATE TABLE IF NOT EXISTS time_logs(id INTEGER PRIMARY KEY,person_id INTEGER NOT NULL,project_id TEXT NOT NULL,task_id INTEGER,started_at TEXT NOT NULL,ended_at TEXT NOT NULL,break_minutes INTEGER NOT NULL DEFAULT 0,activity TEXT NOT NULL,evidence_path TEXT,created_at TEXT NOT NULL,FOREIGN KEY(person_id) REFERENCES people(id),FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE IF NOT EXISTS measurements(id INTEGER PRIMARY KEY,task_id INTEGER NOT NULL UNIQUE,ust_base REAL NOT NULL,factor INTEGER NOT NULL,adjusted REAL NOT NULL,status TEXT NOT NULL,reviewer TEXT,reviewed_at TEXT,external_acceptance_ref TEXT,FOREIGN KEY(task_id) REFERENCES tasks(id));
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,at TEXT NOT NULL,actor TEXT NOT NULL,action TEXT NOT NULL,details TEXT NOT NULL);
'''
def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(str(DB),timeout=12,check_same_thread=False)
    c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');return c

def init():
    with connect() as c:c.executescript(SCHEMA)
