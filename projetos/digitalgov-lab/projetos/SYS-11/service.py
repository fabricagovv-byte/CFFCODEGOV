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
  "code": 11,
  "name": "Gerenciamento de projetos",
  "description": "Cálculo de caminho crítico em projeto com dependências",
  "sample": {
    "tasks": [
      {
        "id": "a",
        "days": 2
      },
      {
        "id": "b",
        "days": 3,
        "depends_on": [
          "a"
        ]
      },
      {
        "id": "c",
        "days": 1,
        "depends_on": [
          "a"
        ]
      }
    ]
  }
}

def calculate(d):
    tasks=d.get('tasks')
    if not isinstance(tasks,list) or not 1<=len(tasks)<=60:raise ValueError('tasks: 1 a 60 tarefas')
    parsed={}
    for t in tasks:
        if not isinstance(t,dict):raise ValueError('Tarefa inválida')
        key=identifier(t,'id');duration=integer(t,'days',1,365)
        deps=t.get('depends_on',[])
        if not isinstance(deps,list) or any(not isinstance(x,str) for x in deps) or key in parsed:raise ValueError('Dependências ou ID inválidos')
        parsed[key]={'days':duration,'depends_on':deps}
    ordered=[]; visiting=set();visited=set()
    def visit(k):
        if k not in parsed:raise ValueError('Dependência inexistente: '+k)
        if k in visiting:raise ValueError('Ciclo de dependências')
        if k in visited:return
        visiting.add(k)
        for dep in parsed[k]['depends_on']:visit(dep)
        visiting.remove(k);visited.add(k);ordered.append(k)
    for k in parsed:visit(k)
    finish={};origin={}
    for key in ordered:
        deps=parsed[key]['depends_on'];prev=max(deps,key=lambda x:finish[x]) if deps else None
        origin[key]=prev;finish[key]=parsed[key]['days']+(finish[prev] if prev else 0)
    last=max(finish,key=finish.get);critical=[]
    while last:critical.insert(0,last);last=origin[last]
    return {'total_days':finish[critical[-1]],'critical_path':critical,'earliest_finish':finish,'task_count':len(parsed),'note':'Tempos de calendário teórico, sem alocação de recursos ou feriados.'}

