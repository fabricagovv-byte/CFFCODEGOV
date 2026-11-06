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
  "code": 3,
  "name": "Suporte técnico de 3º nível",
  "description": "Diagnóstico local de sinais de infraestrutura e priorização",
  "sample": {
    "probes": [
      {
        "name": "cpu",
        "value": 94,
        "max": 80
      },
      {
        "name": "memoria",
        "value": 70,
        "max": 85
      }
    ]
  }
}

def calculate(d):
    probes=d.get('probes')
    if not isinstance(probes,list) or not 1<=len(probes)<=50:raise ValueError('probes deve conter 1 a 50 sinais')
    alerts=[]
    for p in probes:
        if not isinstance(p,dict):raise ValueError('Cada sinal precisa ser objeto')
        name=string(p,'name',1,80); value=number(p,'value',0,1000000); threshold=number(p,'max',0,1000000)
        if value>threshold:alerts.append({'name':name,'value':value,'max':threshold,'recommendation':'Inspecionar manualmente e confirmar a origem do alerta'})
    return {'probes_checked':len(probes),'alerts':alerts,'risk':'CRITICO' if len(alerts)>=3 else 'ATENCAO' if alerts else 'NORMAL','note':'Não conecta com infraestrutura real.'}

