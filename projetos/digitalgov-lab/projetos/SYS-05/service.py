"""Serviço demonstrativo isolado. Não confundir com entrega ou UST contratual."""
from datetime import datetime,timedelta
from xml.etree import ElementTree as ET
import math,re

def string(d,k,minimum=1,maximum=1000):
    v=d.get(k)
    if not isinstance(v,str) or not minimum<=len(v.strip())<=maximum:raise ValueError(f'{k}: texto entre {minimum} e {maximum} caracteres')
    return v.strip()
def integer(d,k,lo,hi):
    v=d.get(k)
    if not isinstance(v,int) or isinstance(v,bool) or not lo<=v<=hi:raise ValueError(f'{k}: inteiro entre {lo} e {hi}')
    return v
def number(d,k,lo,hi):
    v=d.get(k)
    if not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) or not lo<=v<=hi:raise ValueError(f'{k}: número entre {lo} e {hi}')
    return v
def timestamp(d,k):
    v=string(d,k,10,40)
    try:return datetime.fromisoformat(v)
    except ValueError:raise ValueError(f'{k}: ISO-8601 inválido')
def identifier(d,k):
    v=string(d,k,1,40)
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',v):raise ValueError(f'{k}: apenas letras latinas, números e _')
    return v

META={
  "code": 5,
  "name": "Desenvolvimento de sistemas",
  "description": "Geração segura de migração SQL e catálogo de endpoints",
  "sample": {
    "table": "pedidos",
    "fields": [
      {
        "name": "numero",
        "type": "text"
      },
      {
        "name": "quantidade",
        "type": "integer"
      }
    ]
  }
}

def calculate(d):
    table=identifier(d,'table'); fields=d.get('fields')
    if not isinstance(fields,list) or not 1<=len(fields)<=20:raise ValueError('fields: lista de 1 a 20 campos')
    valid={'text':'TEXT','integer':'INTEGER','real':'REAL','boolean':'INTEGER'}
    cols=[]; normalized=[]
    for f in fields:
        if not isinstance(f,dict):raise ValueError('Campo inválido')
        name=identifier(f,'name');typ=string(f,'type',1,20)
        if typ not in valid:raise ValueError('Tipo SQL não permitido')
        if name in ('id','created_at') or name in [x['name'] for x in normalized]:raise ValueError('Campo duplicado ou reservado')
        cols.append(f'"{name}" {valid[typ]}');normalized.append({'name':name,'type':typ})
    sql=f'CREATE TABLE IF NOT EXISTS "{table}" (id INTEGER PRIMARY KEY AUTOINCREMENT, '+', '.join(cols)+', created_at TEXT DEFAULT CURRENT_TIMESTAMP);'
    return {'table':table,'fields':normalized,'migration_sql':sql,'api_routes':[f'GET /api/{table}',f'POST /api/{table}',f'GET /api/{table}/:id',f'PATCH /api/{table}/:id',f'DELETE /api/{table}/:id'],'note':'Gerador de artefatos de projeto; rotas propostas não são automaticamente implementadas por este comando.'}

