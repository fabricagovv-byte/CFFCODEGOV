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
  "code": 9,
  "name": "Business Intelligence e Ciência de Dados",
  "description": "Agregação de indicadores e estatísticas por categoria",
  "sample": {
    "group_by": "setor",
    "measure": "valor",
    "rows": [
      {
        "setor": "A",
        "valor": 10
      },
      {
        "setor": "A",
        "valor": 20
      },
      {
        "setor": "B",
        "valor": 5
      }
    ]
  }
}

def calculate(d):
    rows=d.get('rows'); key=string(d,'group_by',1,80); measure=string(d,'measure',1,80)
    if not isinstance(rows,list) or not 1<=len(rows)<=5000:raise ValueError('rows: 1 a 5000 linhas')
    groups={}
    for row in rows:
        if not isinstance(row,dict) or key not in row or measure not in row:raise ValueError('Linha sem coluna de dimensão ou medida')
        g=str(row[key]);v=row[measure]
        if len(g)>100:raise ValueError('Dimensão muito longa')
        if not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v):raise ValueError('Medida deve ser número finito')
        groups.setdefault(g,[]).append(float(v))
    out=[{'group':k,'count':len(vals),'total':round(sum(vals),4),'average':round(sum(vals)/len(vals),4),'minimum':min(vals),'maximum':max(vals)} for k,vals in sorted(groups.items())]
    return {'dimension':key,'measure':measure,'groups':out,'row_count':len(rows)}

