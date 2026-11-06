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
  "code": 13,
  "name": "Serviços de Governança de TI",
  "description": "Matriz de riscos e controle de prioridade",
  "sample": {
    "risks": [
      {
        "name": "Exposição de dados",
        "impact": 5,
        "probability": 4
      }
    ]
  }
}

def calculate(d):
    risks=d.get('risks')
    if not isinstance(risks,list) or not 1<=len(risks)<=100:raise ValueError('risks: 1 a 100 riscos')
    out=[]
    for r in risks:
        if not isinstance(r,dict):raise ValueError('Risco inválido')
        name=string(r,'name',1,140);impact=integer(r,'impact',1,5);prob=integer(r,'probability',1,5);score=impact*prob
        out.append({'risk':name,'impact':impact,'probability':prob,'score':score,'level':'ALTO' if score>=15 else 'MEDIO' if score>=6 else 'BAIXO'})
    out.sort(key=lambda r:r['score'],reverse=True)
    return {'risk_register':out,'high_count':sum(r['level']=='ALTO' for r in out),'method':'matriz interna 5x5, não padrão formal de auditoria'}

