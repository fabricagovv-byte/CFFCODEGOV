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
  "code": 12,
  "name": "Serviços para Jornada do Cidadão",
  "description": "Motor de estados para atendimento digital do cidadão",
  "sample": {
    "current_state": "PROTOCOLADO",
    "action": "analisar"
  }
}

def calculate(d):
    state=string(d,'current_state',1,30);action=string(d,'action',1,30)
    transitions={'RASCUNHO':{'enviar':'PROTOCOLADO'},'PROTOCOLADO':{'analisar':'EM_ANALISE','cancelar':'CANCELADO'},'EM_ANALISE':{'solicitar_complemento':'PENDENTE_CIDADAO','deferir':'DEFERIDO','indeferir':'INDEFERIDO'},'PENDENTE_CIDADAO':{'complementar':'EM_ANALISE'},'DEFERIDO':{},'INDEFERIDO':{},'CANCELADO':{}}
    if state not in transitions or action not in transitions[state]:raise ValueError('Transição não permitida para o estado atual')
    return {'previous_state':state,'action':action,'new_state':transitions[state][action],'accessible_message':'Solicitação atualizada para '+transitions[state][action].replace('_',' ').lower(),'note':'Não registra protocolo real em órgão público.'}

