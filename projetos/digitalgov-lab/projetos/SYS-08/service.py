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
  "code": 8,
  "name": "Implementação DevOps",
  "description": "Gerador de pipeline de validação para projetos Python e Node",
  "sample": {
    "platform": "python"
  }
}

def calculate(d):
    platform=string(d,'platform',1,20)
    if platform not in ('python','node'):raise ValueError('platform deve ser python ou node')
    cmd='python -m unittest discover -s tests -v' if platform=='python' else 'npm test -- --runInBand'
    setup='actions/setup-python@v5' if platform=='python' else 'actions/setup-node@v4'
    setup_block='python-version: "3.11"' if platform=='python' else 'node-version: "22"'
    install='python -m pip install -r requirements.txt' if platform=='python' else 'npm ci'
    yaml='name: Testes de laboratório\non: [push, pull_request]\njobs:\n  validar:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: '+setup+'\n        with:\n          '+setup_block+'\n      - run: '+install+'\n      - run: '+cmd+'\n'
    yaml=yaml.replace('\\n','\n')
    return {'platform':platform,'workflow_filename':'.github/workflows/validate.yml','workflow_yaml':yaml,'actual_execution':False,'note':'Gera arquivo de pipeline, não publica nem executa GitHub Actions.'}

