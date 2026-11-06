import os, tempfile, pathlib
p=pathlib.Path(tempfile.mkdtemp())/'comm.db'
os.environ['DG_COMM_DB']=str(p)
os.environ['DG_COMM_SECRET']='A'*48
from fastapi.testclient import TestClient
from app.main import app
from app.db import connect
from app.security import hash_password
from app.main import now


def test_full_flow():
    with TestClient(app) as client:
        with connect() as c:
            c.execute('INSERT INTO users(name,username,password_hash,role,created_at) VALUES(?,?,?,?,?)',('Editor','editor',hash_password('senha-forte-de-teste-A'),'EDITOR',now()))
            c.execute('INSERT INTO users(name,username,password_hash,role,created_at) VALUES(?,?,?,?,?)',('Revisor','review',hash_password('senha-forte-de-teste-B'),'APPROVER',now()))
        def login(name,password):
            r=client.post('/api/login',json={'username':name,'password':password});assert r.status_code==200,r.text
            return {'Authorization':'Bearer '+r.json()['token']}
        ed=login('editor','senha-forte-de-teste-A');rv=login('review','senha-forte-de-teste-B')
        assert client.post('/api/login',json={'username':'editor','password':'invalida'}).status_code==401
        c=client.post('/api/channels',headers=ed,json={'name':'Boletim oficial','description':'Comunicação interna'});assert c.status_code==201
        ch=c.json()['id']
        r=client.post('/api/posts',headers=ed,json={'channel_id':ch,'title':'Nova circular','body':'Conteúdo institucional com justificativa'});assert r.status_code==201
        pid=r.json()['id']
        assert client.post(f'/api/posts/{pid}/publish',headers=rv).status_code==409
        assert client.post(f'/api/posts/{pid}/submit',headers=ed).status_code==200
        assert client.post(f'/api/posts/{pid}/approve',headers=ed).status_code==403
        assert client.post(f'/api/posts/{pid}/approve',headers=rv).status_code==200
        assert client.post(f'/api/posts/{pid}/publish',headers=rv).json()['external_delivery']=='NAO_EXECUTADA'
        cam=client.post('/api/campaigns',headers=ed,json={'name':'Campanha Escola','objective':'Informar matrículas'});assert cam.status_code==201
        contact=client.post('/api/contacts',headers=ed,json={'name':'Pessoa de Teste','email':'teste@example.invalid','consent':False});assert contact.status_code==201
        ticket=client.post('/api/tickets',headers=ed,json={'subject':'Dúvida sobre circular','description':'Preciso confirmar os horários'});assert ticket.status_code==201
        assert client.patch('/api/tickets/1/status',headers=ed,json={'status':'RESOLVIDO'}).status_code==200
        dash=client.get('/api/overview',headers=ed).json()['kpis']
        assert dash['posts_published']==1 and dash['tickets_open']==0 and dash['campaigns']==1
        assert client.get('/api/export/tickets.csv',headers=rv).status_code==200
        assert client.get('/api/audit',headers=rv).json()
