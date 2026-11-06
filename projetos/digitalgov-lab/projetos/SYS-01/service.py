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
  "code": 1,
  "name": "Suporte técnico de 1º nível",
  "description": "Triagem de chamados, severidade e prazo interno",
  "sample": {
    "title": "Usuário sem acesso",
    "impact": 3,
    "urgency": 2
  }
}

def calculate(d):
    impact=integer(d,'impact',1,3); urgency=integer(d,'urgency',1,3)
    title=string(d,'title',1,140)
    score=impact*urgency
    priority='P1' if score>=6 else 'P2' if score>=3 else 'P3'
    duration={'P1':4,'P2':8,'P3':24}[priority]
    return {'ticket':title,'priority':priority,'impact':impact,'urgency':urgency,'score':score,'internal_target_hours':duration,'route':'escalonar' if priority=='P1' else 'fila_n1','note':'Meta de laboratório; não representa SLA do edital.'}

