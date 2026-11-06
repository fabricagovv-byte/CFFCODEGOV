"""API CRUD REAL de laboratório. Somente 127.0.0.1; não publicar sem autenticação/TLS.
Banco SQLite exclusivo do subprojeto; não usa credenciais ou dados reais do governo.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from pathlib import Path
import json,os,sqlite3,re
import service
HERE=Path(__file__).resolve().parent
DB=Path(os.environ.get('LAB_DB_PATH',str(HERE/'data'/'records.sqlite3')))
PROJECT_ID='SYS-14'
PROJECT_TITLE='Registro de riscos'
STATUS=('ABERTO','EM_ANALISE','EM_EXECUCAO','CONCLUIDO')

def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DB, timeout=10)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    db.execute("""CREATE TABLE IF NOT EXISTS records(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT NOT NULL,status TEXT NOT NULL CHECK(status IN ('ABERTO','EM_ANALISE','EM_EXECUCAO','CONCLUIDO')),created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    db.execute("CREATE TABLE IF NOT EXISTS service_runs (id INTEGER PRIMARY KEY AUTOINCREMENT,input_json TEXT NOT NULL,result_json TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    db.commit();return db

class API(BaseHTTPRequestHandler):
    def send_json(self,code,body):
        data=json.dumps(body,ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        self.end_headers();self.wfile.write(data)
    def body(self):
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=16384:raise ValueError('Tamanho inválido: limite de 16 KB')
            body=json.loads(self.rfile.read(size))
            if not isinstance(body,dict):raise ValueError('Corpo deve ser objeto JSON')
            return body
        except (ValueError,TypeError,json.JSONDecodeError) as ex:raise ValueError(str(ex))
    def validate(self,body,required=False):
        allowed={'title','description','status'}
        if not body or any(k not in allowed for k in body):raise ValueError('Campos não permitidos ou corpo vazio')
        if required and not isinstance(body.get('title'),str):raise ValueError('Título é obrigatório')
        out={}
        for k,v in body.items():
            if not isinstance(v,str):raise ValueError(k+' deve ser texto')
            if len(v)>2000:raise ValueError('Tamanho de campo excedido')
            if k=='title' and (not v.strip() or len(v)>140):raise ValueError('Título deve ter entre 1 e 140 caracteres')
            if k=='status' and v not in STATUS:raise ValueError('Status inválido')
            out[k]=v.strip()
        return out
    def route(self):
        path=urlparse(self.path).path
        match=re.fullmatch('/api/records/([0-9]+)',path)
        return path,int(match.group(1)) if match else None
    def do_GET(self):
        path,record_id=self.route()
        if path=='/':
            data=(HERE/'index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        if path=='/service':
            data=(HERE/'service.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        if path=='/service.js':
            data=(HERE/'service.js').read_bytes();self.send_response(200);self.send_header('Content-Type','application/javascript; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        if path=='/api/service/metadata':return self.send_json(200,service.META)
        if path=='/api/service/history':
            with connect() as db:return self.send_json(200,{'items':[dict(r) for r in db.execute('SELECT id,created_at,input_json,result_json FROM service_runs ORDER BY id DESC LIMIT 50')]})
        if path=='/app.js':
            data=(HERE/'app.js').read_bytes();self.send_response(200);self.send_header('Content-Type','application/javascript; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        if path=='/health':return self.send_json(200,{'ok':True,'project':PROJECT_ID,'database':DB.name})
        with connect() as db:
            if path=='/api/records':return self.send_json(200,{'items':[dict(r) for r in db.execute('SELECT * FROM records ORDER BY id DESC LIMIT 500')]})
            if record_id is not None:
                rec=db.execute('SELECT * FROM records WHERE id=?',(record_id,)).fetchone()
                return self.send_json(200,dict(rec)) if rec else self.send_json(404,{'error':'Registro não localizado'})
        return self.send_json(404,{'error':'Rota não localizada'})
    def do_POST(self):
        path,_=self.route()
        if path=='/api/service/run':
            try:
                data=self.body(); result=service.calculate(data)
                body=json.dumps(data,ensure_ascii=False); out=json.dumps(result,ensure_ascii=False)
                with connect() as db:
                    cur=db.execute('INSERT INTO service_runs (input_json,result_json) VALUES (?,?)',(body,out));db.commit()
                return self.send_json(201,{'run_id':cur.lastrowid,'service':service.META['name'],'result':result,'laboratory_only':True})
            except (ValueError,TypeError) as ex:return self.send_json(400,{'error':str(ex)})
        if path!='/api/records':return self.send_json(404,{'error':'Rota não localizada'})
        try:obj=self.validate(self.body(),True)
        except ValueError as e:return self.send_json(400,{'error':str(e)})
        with connect() as db:
            cur=db.execute('INSERT INTO records(title,description,status) VALUES(?,?,?)',(obj['title'],obj.get('description',''),obj.get('status','ABERTO')))
            db.commit();rec=db.execute('SELECT * FROM records WHERE id=?',(cur.lastrowid,)).fetchone()
        self.send_json(201,dict(rec))
    def do_PATCH(self):
        path,id=self.route()
        if id is None:return self.send_json(404,{'error':'Rota não localizada'})
        try:obj=self.validate(self.body())
        except ValueError as e:return self.send_json(400,{'error':str(e)})
        with connect() as db:
            old=db.execute('SELECT * FROM records WHERE id=?',(id,)).fetchone()
            if old is None:return self.send_json(404,{'error':'Registro não localizado'})
            new={k:obj.get(k,old[k]) for k in ('title','description','status')}
            db.execute('UPDATE records SET title=?,description=?,status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',(new['title'],new['description'],new['status'],id));db.commit()
            rec=db.execute('SELECT * FROM records WHERE id=?',(id,)).fetchone()
        self.send_json(200,dict(rec))
    def do_DELETE(self):
        path,id=self.route()
        if id is None:return self.send_json(404,{'error':'Rota não localizada'})
        with connect() as db:
            cur=db.execute('DELETE FROM records WHERE id=?',(id,));db.commit()
        return self.send_json(200,{'deleted':True,'id':id}) if cur.rowcount else self.send_json(404,{'error':'Registro não localizado'})
    def log_message(self,*args):pass

def serve(port=0):
    with connect():pass
    with ThreadingHTTPServer(('127.0.0.1',port),API) as srv:
        print(f'Laboratório {PROJECT_ID} em http://127.0.0.1:{srv.server_port}')
        srv.serve_forever()
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8001);a=p.parse_args();serve(a.port)
