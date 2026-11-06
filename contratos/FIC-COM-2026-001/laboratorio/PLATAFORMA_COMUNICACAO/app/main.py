"""Plataforma de Comunicação Digitalgov: MVP operacional, não produto homologado."""
import json, csv, io
from datetime import datetime, timezone
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from .db import connect, init
from .security import verify_password, token_for, decode, hash_password

BASE=Path(__file__).resolve().parents[1]
def now():return datetime.now(timezone.utc).isoformat()
def row(r):return dict(r) if r else None

def audit(c, uid, action, entity, eid, detail=None):
    c.execute('INSERT INTO audit(user_id,action,entity,entity_id,at,detail) VALUES(?,?,?,?,?,?)',(uid,action,entity,eid,now(),json.dumps(detail or {},ensure_ascii=False)))

@asynccontextmanager
async def lifespan(app):
    init()
    yield

app=FastAPI(title='Digitalgov | Comunicação Institucional',version='1.0.0-mvp',lifespan=lifespan)
app.mount('/static',StaticFiles(directory=str(BASE/'static')),name='static')

@app.get('/')
def homepage():return FileResponse(BASE/'static'/'index.html')
@app.get('/health')
def health():return {'status':'ok','system':'comunicacao','production_ready':False}

def current(authorization: str|None=Header(default=None)):
    if not authorization or not authorization.startswith('Bearer '):raise HTTPException(401,'Autenticação obrigatória')
    uid=decode(authorization[7:])
    if not uid:raise HTTPException(401,'Token inválido ou expirado')
    with connect() as c:
        u=c.execute('SELECT id,name,username,role FROM users WHERE id=? AND active=1',(uid,)).fetchone()
    if not u:raise HTTPException(401,'Usuário não encontrado')
    return row(u)

def need(*roles):
    def check(u=Depends(current)):
        if u['role'] not in roles:raise HTTPException(403,'Acesso não permitido')
        return u
    return check

class Login(BaseModel):username:str;password:str
class UserIn(BaseModel):name:str=Field(min_length=2);username:str=Field(min_length=3);password:str=Field(min_length=12);role:str
class ChannelIn(BaseModel):name:str=Field(min_length=2);description:str='';is_public:bool=False
class PostIn(BaseModel):channel_id:int;title:str=Field(min_length=4);body:str=Field(min_length=8)
class CampaignIn(BaseModel):name:str=Field(min_length=3);objective:str=Field(min_length=4);channel_id:Optional[int]=None;starts_on:Optional[str]=None;ends_on:Optional[str]=None
class ContactIn(BaseModel):name:str=Field(min_length=2);email:Optional[str]=None;category:str='PUBLICO';consent:bool=False
class TicketIn(BaseModel):subject:str=Field(min_length=5);description:str=Field(min_length=8);priority:str='NORMAL';contact_id:Optional[int]=None
class TicketStatus(BaseModel):status:str

@app.post('/api/login')
def login(p:Login):
    with connect() as c:
        u=c.execute('SELECT * FROM users WHERE username=? AND active=1',(p.username,)).fetchone()
        if not u or not verify_password(p.password,u['password_hash']):raise HTTPException(401,'Credenciais inválidas')
        return {'token':token_for(u['id']),'role':u['role'],'name':u['name']}

@app.get('/api/me')
def me(u=Depends(current)):return u

@app.post('/api/users',status_code=201)
def add_user(p:UserIn,u=Depends(need('ADMIN'))):
    if p.role not in {'ADMIN','EDITOR','APPROVER','VIEWER'}:raise HTTPException(422,'Papel inválido')
    try:
        with connect() as c:
            cur=c.execute('INSERT INTO users(name,username,password_hash,role,created_at) VALUES(?,?,?,?,?)',(p.name,p.username,hash_password(p.password),p.role,now()))
            audit(c,u['id'],'CREATE','user',cur.lastrowid)
            return {'id':cur.lastrowid,'username':p.username,'role':p.role}
    except __import__('sqlite3').IntegrityError:raise HTTPException(409,'Usuário duplicado')

@app.get('/api/overview')
def overview(u=Depends(current)):
    with connect() as c:
        counts={t:c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('channels','posts','campaigns','contacts','tickets','deliveries')}
        counts.update({'posts_published':c.execute("SELECT COUNT(*) FROM posts WHERE status='PUBLICADO'").fetchone()[0],'tickets_open':c.execute("SELECT COUNT(*) FROM tickets WHERE status!='RESOLVIDO'").fetchone()[0]})
    return {'kpis':counts,'note':'Indicadores provenientes do banco de dados; nenhuma entrega externa é simulada'}

@app.get('/api/channels')
def channels(u=Depends(current)):
    with connect() as c:return [row(x) for x in c.execute('SELECT * FROM channels ORDER BY id DESC').fetchall()]

@app.post('/api/channels',status_code=201)
def channel_create(p:ChannelIn,u=Depends(need('ADMIN','EDITOR'))):
    with connect() as c:
        cur=c.execute('INSERT INTO channels(name,description,is_public,created_by,created_at) VALUES(?,?,?,?,?)',(p.name,p.description,int(p.is_public),u['id'],now()))
        audit(c,u['id'],'CREATE','channel',cur.lastrowid)
        return {'id':cur.lastrowid,'name':p.name}

@app.get('/api/posts')
def posts(u=Depends(current)):
    with connect() as c:return [row(x) for x in c.execute('SELECT p.*, ch.name AS channel, us.name AS author FROM posts p JOIN channels ch ON ch.id=p.channel_id JOIN users us ON us.id=p.author_id ORDER BY p.id DESC').fetchall()]

@app.post('/api/posts',status_code=201)
def post_create(p:PostIn,u=Depends(need('ADMIN','EDITOR'))):
    with connect() as c:
        if not c.execute('SELECT 1 FROM channels WHERE id=?',(p.channel_id,)).fetchone():raise HTTPException(404,'Canal não encontrado')
        at=now();cur=c.execute('INSERT INTO posts(channel_id,title,body,status,author_id,created_at,updated_at) VALUES(?,?,?,?,?,?,?)',(p.channel_id,p.title,p.body,'RASCUNHO',u['id'],at,at))
        audit(c,u['id'],'CREATE','post',cur.lastrowid)
        return {'id':cur.lastrowid,'status':'RASCUNHO'}

@app.post('/api/posts/{pid}/submit')
def post_submit(pid:int,u=Depends(need('ADMIN','EDITOR'))):
    with connect() as c:
        p=c.execute('SELECT * FROM posts WHERE id=?',(pid,)).fetchone()
        if not p:raise HTTPException(404,'Publicação não encontrada')
        if p['author_id']!=u['id'] and u['role']!='ADMIN':raise HTTPException(403,'Somente autor ou gestor')
        if p['status']!='RASCUNHO':raise HTTPException(409,'Estado inválido')
        c.execute("UPDATE posts SET status='EM_REVISAO',updated_at=? WHERE id=?",(now(),pid));audit(c,u['id'],'SUBMIT','post',pid)
    return {'status':'EM_REVISAO'}

@app.post('/api/posts/{pid}/approve')
def post_approve(pid:int,u=Depends(need('ADMIN','APPROVER'))):
    with connect() as c:
        p=c.execute('SELECT * FROM posts WHERE id=?',(pid,)).fetchone()
        if not p:raise HTTPException(404,'Publicação não encontrada')
        if p['status']!='EM_REVISAO':raise HTTPException(409,'A publicação não está em revisão')
        if p['author_id']==u['id']:raise HTTPException(409,'Aprovação deve ser feita por outra pessoa')
        c.execute("UPDATE posts SET status='APROVADO',approver_id=?,updated_at=? WHERE id=?",(u['id'],now(),pid));audit(c,u['id'],'APPROVE','post',pid)
    return {'status':'APROVADO'}

@app.post('/api/posts/{pid}/publish')
def post_publish(pid:int,u=Depends(need('ADMIN','APPROVER'))):
    with connect() as c:
        p=c.execute('SELECT * FROM posts WHERE id=?',(pid,)).fetchone()
        if not p:raise HTTPException(404,'Publicação não encontrada')
        if p['status']!='APROVADO':raise HTTPException(409,'Aprovação obrigatória')
        at=now();c.execute("UPDATE posts SET status='PUBLICADO',published_at=?,updated_at=? WHERE id=?",(at,at,pid));audit(c,u['id'],'PUBLISH','post',pid)
    return {'status':'PUBLICADO','published_at':at,'external_delivery':'NAO_EXECUTADA'}

@app.get('/api/campaigns')
def campaigns(u=Depends(current)):
    with connect() as c:return [row(x) for x in c.execute('SELECT * FROM campaigns ORDER BY id DESC').fetchall()]

@app.post('/api/campaigns',status_code=201)
def campaign_create(p:CampaignIn,u=Depends(need('ADMIN','EDITOR'))):
    with connect() as c:
        cur=c.execute('INSERT INTO campaigns(name,objective,channel_id,starts_on,ends_on,owner_id,created_at) VALUES(?,?,?,?,?,?,?)',(p.name,p.objective,p.channel_id,p.starts_on,p.ends_on,u['id'],now()))
        audit(c,u['id'],'CREATE','campaign',cur.lastrowid);return {'id':cur.lastrowid,'status':'PLANEJADA'}

@app.get('/api/contacts')
def contacts(u=Depends(need('ADMIN','EDITOR','APPROVER'))):
    with connect() as c:return [row(x) for x in c.execute('SELECT id,name,email,category,consent,created_at FROM contacts ORDER BY id DESC').fetchall()]

@app.post('/api/contacts',status_code=201)
def contact_create(p:ContactIn,u=Depends(need('ADMIN','EDITOR'))):
    with connect() as c:
        cur=c.execute('INSERT INTO contacts(name,email,category,consent,created_at) VALUES(?,?,?,?,?)',(p.name,p.email,p.category,int(p.consent),now()))
        audit(c,u['id'],'CREATE','contact',cur.lastrowid)
        return {'id':cur.lastrowid,'consent':p.consent}

@app.get('/api/tickets')
def tickets(u=Depends(current)):
    with connect() as c:return [row(x) for x in c.execute('SELECT * FROM tickets ORDER BY id DESC').fetchall()]

@app.post('/api/tickets',status_code=201)
def ticket_create(p:TicketIn,u=Depends(need('ADMIN','EDITOR'))):
    if p.priority not in {'BAIXA','NORMAL','ALTA'}:raise HTTPException(422,'Prioridade inválida')
    with connect() as c:
        at=now();cur=c.execute('INSERT INTO tickets(contact_id,subject,description,priority,created_at,updated_at) VALUES(?,?,?,?,?,?)',(p.contact_id,p.subject,p.description,p.priority,at,at))
        audit(c,u['id'],'CREATE','ticket',cur.lastrowid)
        return {'id':cur.lastrowid,'status':'ABERTO'}

@app.patch('/api/tickets/{tid}/status')
def ticket_status(tid:int,p:TicketStatus,u=Depends(need('ADMIN','EDITOR'))):
    if p.status not in {'ABERTO','EM_ATENDIMENTO','RESOLVIDO'}:raise HTTPException(422,'Estado inválido')
    with connect() as c:
        if not c.execute('SELECT 1 FROM tickets WHERE id=?',(tid,)).fetchone():raise HTTPException(404,'Chamado não encontrado')
        c.execute('UPDATE tickets SET status=?,updated_at=? WHERE id=?',(p.status,now(),tid));audit(c,u['id'],'UPDATE_STATUS','ticket',tid,{'status':p.status})
    return {'status':p.status}

@app.get('/api/audit')
def audits(u=Depends(need('ADMIN','APPROVER'))):
    with connect() as c:return [row(x) for x in c.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 200').fetchall()]

@app.get('/api/export/tickets.csv')
def export_tickets(u=Depends(need('ADMIN','APPROVER'))):
    with connect() as c:data=c.execute('SELECT id,subject,priority,status,created_at,updated_at FROM tickets ORDER BY id').fetchall()
    out=io.StringIO();out.write('\ufeff');w=csv.writer(out);w.writerow(['ID','Assunto','Prioridade','Estado','Criado em','Atualizado em']);w.writerows([tuple(x) for x in data]);out.seek(0)
    return StreamingResponse(iter([out.getvalue()]),media_type='text/csv; charset=utf-8',headers={'Content-Disposition':'attachment; filename=chamados.csv'})
