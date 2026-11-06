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
  "code": 10,
  "name": "Desenvolvimento de IA",
  "description": "Classificador local explicável de demandas, sem modelo externo",
  "sample": {
    "text": "Falha na API do sistema e bug no cadastro"
  }
}

def calculate(d):
    title=string(d,'text',1,1000).lower()
    keywords={'seguranca':['vazamento','senha','acesso indevido','ataque','phishing'], 'infraestrutura':['servidor','rede','roteador','latencia','nuvem'], 'desenvolvimento':['api','codigo','software','sistema','bug'], 'atendimento':['cidadao','solicitacao','usuario','atendimento']}
    scores={k:sum(1 for kw in words if kw in title) for k,words in keywords.items()}
    best=max(scores,key=scores.get)
    if scores[best]==0: best='nao_classificado'
    return {'label':best,'scores':scores,'matched_keywords':([kw for kw in keywords[best] if kw in title] if best!='nao_classificado' else []),'model':'regras_explicitas_v1','uses_external_ai':False,'note':'Este módulo NÃO é um modelo treinado nem previsão de IA generativa.'}

