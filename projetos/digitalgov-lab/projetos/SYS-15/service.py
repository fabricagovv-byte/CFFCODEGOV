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
  "code": 15,
  "name": "Serviços de Integração de Sistemas",
  "description": "Transformação de registros com mapeamento de campos e erros por linha",
  "sample": {
    "records": [
      {
        "nome_origem": "Ana",
        "idade": 23
      },
      {
        "idade": 40
      }
    ],
    "mapping": {
      "nome": "nome_origem",
      "idade": "idade"
    },
    "required": [
      "nome"
    ]
  }
}

def calculate(d):
    source=d.get('records');mapping=d.get('mapping');required=d.get('required',[])
    if not isinstance(source,list) or not 1<=len(source)<=1000:raise ValueError('records: 1 a 1000 linhas')
    if not isinstance(mapping,dict) or not 1<=len(mapping)<=30:raise ValueError('mapping deve ser objeto com 1 a 30 campos')
    if not isinstance(required,list) or not all(isinstance(x,str) for x in required):raise ValueError('required inválido')
    for target,src in mapping.items():
        if not isinstance(target,str) or not isinstance(src,str) or len(target)>80 or len(src)>80:raise ValueError('Nome de campo inválido')
    results=[];errors=[]
    for i,r in enumerate(source,1):
        if not isinstance(r,dict):errors.append({'row':i,'message':'Linha não é objeto'});continue
        mapped={dst:r.get(src) for dst,src in mapping.items()}
        missing=[f for f in required if mapped.get(f) is None or mapped.get(f)=='']
        if missing:errors.append({'row':i,'missing':missing})
        else:results.append(mapped)
    return {'transformed':results,'success_count':len(results),'error_count':len(errors),'errors':errors,'external_send':False,'note':'Transformação local; não encaminha dados a sistemas externos.'}

