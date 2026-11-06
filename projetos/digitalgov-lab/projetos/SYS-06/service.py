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
  "code": 6,
  "name": "Testes de sistemas",
  "description": "Executor determinístico de cenários e diagnóstico de falhas",
  "sample": {
    "cases": [
      {
        "name": "login",
        "actual": 200,
        "expected": 200
      },
      {
        "name": "permissao",
        "actual": 403,
        "expected": 401
      }
    ]
  }
}

def calculate(d):
    cases=d.get('cases')
    if not isinstance(cases,list) or not 1<=len(cases)<=100:raise ValueError('cases: 1 a 100 casos')
    outcomes=[]
    for i,case in enumerate(cases,1):
        if not isinstance(case,dict) or 'expected' not in case or 'actual' not in case:raise ValueError('Caso sem expected/actual')
        ok=case['expected']==case['actual']
        outcomes.append({'case':i,'name':str(case.get('name',f'Caso {i}'))[:80],'passed':ok,'actual':case['actual'],'expected':case['expected']})
    success=sum(x['passed'] for x in outcomes)
    return {'total':len(outcomes),'passed':success,'failed':len(outcomes)-success,'all_passed':success==len(outcomes),'results':outcomes,'note':'Compara resultados fornecidos; não executa testes externos automaticamente.'}

