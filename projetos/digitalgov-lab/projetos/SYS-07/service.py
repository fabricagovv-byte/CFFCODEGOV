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
  "code": 7,
  "name": "Análise de negócios e processos",
  "description": "Validador e gerador BPMN XML para fluxo sequencial",
  "sample": {
    "tasks": [
      "Solicitar",
      "Analisar",
      "Responder"
    ]
  }
}

def calculate(d):
    items=d.get('tasks')
    if not isinstance(items,list) or not 1<=len(items)<=30:raise ValueError('tasks: lista de 1 a 30 etapas')
    names=[str(t).strip() for t in items]
    if any(not x or len(x)>100 for x in names):raise ValueError('Etapa inválida')
    ns='http://www.omg.org/spec/BPMN/20100524/MODEL'
    root=ET.Element('definitions',{'xmlns':ns,'id':'Definitions_1','targetNamespace':'https://example.invalid/bpmn/lab'})
    proc=ET.SubElement(root,'process',{'id':'Process_Lab','isExecutable':'false'})
    ET.SubElement(proc,'startEvent',{'id':'Start'})
    for i,name in enumerate(names,1): ET.SubElement(proc,'task',{'id':f'Task_{i}','name':name})
    ET.SubElement(proc,'endEvent',{'id':'End'})
    chain=['Start']+[f'Task_{i}' for i in range(1,len(names)+1)]+['End']
    for i,(a,b) in enumerate(zip(chain,chain[1:]),1):ET.SubElement(proc,'sequenceFlow',{'id':f'Flow_{i}','sourceRef':a,'targetRef':b})
    xml=ET.tostring(root,encoding='unicode')
    return {'steps':names,'flows':len(names)+1,'bpmn_xml':xml,'note':'BPMN de sequência linear, sem decisões ou raias; edição avançada não implementada.'}

