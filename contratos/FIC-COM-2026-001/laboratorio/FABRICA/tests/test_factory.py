import os,tempfile,pathlib
path=pathlib.Path(tempfile.mkdtemp())
os.environ['DG_FACTORY_DB']=str(path/'f.db')
os.environ['DG_FACTORY_TOKEN']='K'*40
CHAVE={'Authorization':'Bearer '+'K'*40}
from fastapi.testclient import TestClient
from app.main import app
from app import core
from app.db import connect

def test_workflow():
    with TestClient(app,headers=CHAVE) as client:
        assert core.seed()
        dash=client.get('/api/overview').json()
        assert dash['ust_target']==12000 and dash['ust_verified']==0 and dash['agents_running']==0
        assert client.post('/api/contracts/FIC-COM-2026-001/start',json={}).status_code==409
        assert client.post('/api/contracts/FIC-COM-2026-001/approve',json={'phrase':'nao'}).status_code==409
        assert client.post('/api/contracts/FIC-COM-2026-001/approve',json={'phrase':'APROVO PLANO FIC-COM-2026-001'}).status_code==200
        result=client.post('/api/contracts/FIC-COM-2026-001/start',json={}).json()
        assert result['prepared']==18 and result['started_agents']==0
        evidence=path/'output.txt';evidence.write_text('arquivo de teste com resultados verificados')
        sha=core.register_evidence(1,str(evidence),'PASS','agente-integrado')
        assert sha
        evidence.write_text('corrompido')
        try:core.verify_task(1,'revisor',20);assert False
        except ValueError:pass
        evidence.write_text('arquivo de teste com resultados verificados')
        assert core.verify_task(1,'revisor',20)==60
        assert client.get('/api/overview').json()['ust_verified']==60
        assert client.get('/api/overview').json()['ust_homologated']==0
        acceptance=path/'termo_ficticio.txt';acceptance.write_text('DEMO: termo não oficial, somente teste automatizado');core.register_acceptance(1,str(acceptance),'revisor')
        assert client.get('/api/overview').json()['ust_homologated']==60

def test_human_hours():
    evidence=path/'human.txt';evidence.write_text('ata assinada por humano no cenário de laboratório')
    hours=core.record_human_hours(1,'COM-001','2026-11-06T09:00:00-03:00','2026-11-06T18:00:00-03:00',60,'Revisão real - registro de demonstração',str(evidence))
    assert hours==8.0
    try:core.record_human_hours(1,'COM-001','2026-11-06T10:00:00-03:00','2026-11-06T11:00:00-03:00',0,'Duplicata',str(evidence));assert False
    except ValueError:pass
