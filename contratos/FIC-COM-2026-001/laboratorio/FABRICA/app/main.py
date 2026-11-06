from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from .db import init,connect
from . import core
BASE=Path(__file__).resolve().parents[1]
@asynccontextmanager
async def lifespan(app):init();yield
app=FastAPI(title='Digitalgov Factory Control Center',version='1.0.0-lab',lifespan=lifespan)
app.mount('/static',StaticFiles(directory=str(BASE/'static')),name='static')
@app.get('/')
def index():return FileResponse(BASE/'static'/'index.html')
@app.get('/health')
def health():return {'status':'ok','deployment':'laboratory','codex_agents_running':0}
@app.get('/api/overview')
def overview():
    with connect() as c:return core.overview(c)
@app.get('/api/contracts')
def contracts():
    with connect() as c:return [dict(r) for r in c.execute('SELECT * FROM contracts ORDER BY created_at DESC')]
@app.get('/api/tasks')
def tasks():
    with connect() as c:return [dict(r) for r in c.execute('SELECT * FROM tasks ORDER BY id')]
@app.get('/api/team')
def team():
    with connect() as c:return [dict(r) for r in c.execute('SELECT id,name,seniority,role,active,cpf_masked FROM people ORDER BY id')]
@app.get('/api/hours')
def hours():
    with connect() as c:
        rows=c.execute('SELECT person_id,started_at,ended_at,break_minutes,activity,evidence_path FROM time_logs ORDER BY id DESC').fetchall()
        from datetime import datetime
        return [{**dict(r),'hours':round((datetime.fromisoformat(r['ended_at'])-datetime.fromisoformat(r['started_at'])).total_seconds()/3600-r['break_minutes']/60,2)} for r in rows]
class Approval(BaseModel):phrase:str;actor:str='Administrador'
@app.post('/api/contracts/{cid}/approve')
def approve(cid:str,p:Approval):
    try:core.approve_contract(cid,p.actor,p.phrase);return {'status':'PLANO_APROVADO'}
    except ValueError as e:raise HTTPException(409,str(e))
class Start(BaseModel):actor:str='Administrador'
@app.post('/api/contracts/{cid}/start')
def start(cid:str,p:Start):
    try:return core.prepare_start(cid,p.actor)
    except ValueError as e:raise HTTPException(409,str(e))
