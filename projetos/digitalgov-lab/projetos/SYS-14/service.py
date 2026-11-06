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
  "code": 14,
  "name": "Serviços de Gestão de Segurança da Informação",
  "description": "Varredura estática de padrões de código de exemplo",
  "sample": {
    "source_code": "x = eval(user_input)\nprint(x)"
  }
}

def calculate(d):
    code=string(d,'source_code',1,20000)
    patterns=[('S001','CRITICO',r'(?i)\beval\s*\(', 'Avaliação dinâmica de expressão'),('S002','ALTO',r'(?i)\bpickle\.loads\s*\(', 'Desserialização insegura potencial'),('S003','ALTO',r'(?i)\bshell\s*=\s*True\b','Execução via shell habilitada'),('S004','ALTO',r'(?i)(password|secret|api_key)\s*=\s*[\"\'][^\"\']{5,}[\"\']','Possível segredo hardcoded')]
    findings=[]
    for i,line in enumerate(code.splitlines(),1):
        for rule,severity,pattern,msg in patterns:
            if re.search(pattern,line): findings.append({'line':i,'rule':rule,'severity':severity,'message':msg})
    return {'lines_scanned':len(code.splitlines()),'findings':findings,'finding_count':len(findings),'note':'Varredura parcial; não é certificação de segurança ou pentest.'}

