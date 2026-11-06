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
  "code": 2,
  "name": "Suporte técnico de 2º nível",
  "description": "Planejamento de visita técnica, janela e atendimento",
  "sample": {
    "requested_at": "2026-11-05T09:00:00",
    "duration_minutes": 90,
    "technician": "Técnico laboratório",
    "location": "Unidade A"
  }
}

def calculate(d):
    start=timestamp(d,'requested_at'); duration=integer(d,'duration_minutes',15,480)
    technician=string(d,'technician',1,80); location=string(d,'location',1,140)
    end=start+timedelta(minutes=duration)
    return {'assigned_to':technician,'location':location,'start':start.isoformat(),'end':end.isoformat(),'duration_minutes':duration,'onsite_required':True,'note':'Agenda simulada; nenhum técnico foi realmente enviado.'}

