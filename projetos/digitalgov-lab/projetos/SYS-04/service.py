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
  "code": 4,
  "name": "Sustentação de sistemas",
  "description": "Cálculo de tempo de indisponibilidade e conformidade com meta interna",
  "sample": {
    "incident_started_at": "2026-11-04T10:00:00",
    "service_restored_at": "2026-11-04T11:15:00",
    "target_minutes": 90
  }
}

def calculate(d):
    start=timestamp(d,'incident_started_at'); end=timestamp(d,'service_restored_at'); target=integer(d,'target_minutes',1,100000)
    if end<start:raise ValueError('Data de recuperação anterior ao incidente')
    minutes=round((end-start).total_seconds()/60,2)
    return {'downtime_minutes':minutes,'target_minutes':target,'meets_target':minutes<=target,'mttr_sample_minutes':minutes,'note':'Apenas um evento; MTTR agregado depende de múltiplos incidentes.'}

