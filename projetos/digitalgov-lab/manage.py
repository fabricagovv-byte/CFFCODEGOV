#!/usr/bin/env python3
"""CLI de gerenciamento real do laboratório Codex.  python manage.py --help"""
import argparse, json, sys, zipfile, hashlib
from pathlib import Path
from fabrica.db import connect,init,ROOT,integrity_check
from fabrica.core import create_task,start_task,finish_task,verify_task,snapshot,DomainError,add_external_acceptance
from fabrica.api import serve
from fabrica.report import build_report

def main(argv=None):
    p=argparse.ArgumentParser(prog='python manage.py',description='Fábrica Codex Digitalgov — execução local verificável')
    s=p.add_subparsers(dest='cmd',required=True)
    s.add_parser('init');s.add_parser('status');s.add_parser('audit')
    v=s.add_parser('serve');v.add_argument('--port',type=int,default=8765)
    v=s.add_parser('task-create');v.add_argument('--os',required=True);v.add_argument('--title',required=True);v.add_argument('--kind',choices=['AGENTE','HUMANO'],required=True);v.add_argument('--actor',required=True);v.add_argument('--base',type=int,default=0)
    v=s.add_parser('task-start');v.add_argument('id',type=int)
    v=s.add_parser('task-finish');v.add_argument('id',type=int);v.add_argument('--evidence',required=True);v.add_argument('--test-result',choices=['PASS','FAIL','NOT_APPLICABLE'],required=True);v.add_argument('--commit',default=None)
    v=s.add_parser('task-verify');v.add_argument('id',type=int);v.add_argument('--reviewer',required=True);v.add_argument('--base',type=int,required=True)
    v=s.add_parser('report');v.add_argument('--out',default=None)
    v=s.add_parser('release');v.add_argument('--project',required=True);v.add_argument('--out',default=None)
    a=p.parse_args(argv)
    if a.cmd=='serve':serve(a.port);return
    with connect() as c:
        init(c)
        if a.cmd=='init':print('Banco criado/verificado; 15 projetos e 15 OS SIMULADAS. UST verificadas: 0 na inicialização.');return
        if a.cmd=='status':
            d=snapshot(c)
            print(json.dumps({k:d[k] for k in ('contract','target_ust','internal_verified_ust','official_accepted_ust','project_count','audit_chain_valid')},ensure_ascii=False,indent=2));return
        if a.cmd=='audit':print('CADEIA ÍNTEGRA' if integrity_check(c) else 'ALERTA: CADEIA INVÁLIDA');return
        if a.cmd=='task-create': print('TAREFA CRIADA',create_task(c,a.os,a.title,a.kind,a.actor,a.base));return
        if a.cmd=='task-start':start_task(c,a.id);print('INICIADA',a.id);return
        if a.cmd=='task-finish':finish_task(c,a.id,a.evidence,a.commit,a.test_result);print('FINALIZADA',a.id);return
        if a.cmd=='task-verify':print('UST AJUSTADAS VERIFICADAS INTERNAMENTE NO LABORATÓRIO',verify_task(c,a.id,a.reviewer,a.base));return
        if a.cmd=='report':print(build_report(c,a.out));return
        if a.cmd=='release':
            base=ROOT/'projetos'/a.project
            if not base.is_dir() or a.project not in [f'SYS-{x:02d}' for x in range(1,16)]: raise DomainError('Projeto inexistente')
            out=Path(a.out) if a.out else ROOT/'entregas'/f'{a.project}_LAB.zip';out.parent.mkdir(exist_ok=True,parents=True)
            sha={}
            with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
                for f in sorted(base.rglob('*')):
                    if f.is_file() and '__pycache__' not in f.parts and f.suffix not in ('.db','.db-shm','.db-wal'):
                        arc=f.relative_to(ROOT).as_posix();z.write(f,arc);sha[arc]=hashlib.sha256(f.read_bytes()).hexdigest()
                z.writestr('MANIFEST_SHA256.json',json.dumps({'project':a.project,'kind':'LABORATORIO_NAO_PRODUCAO','hashes':sha},indent=2,ensure_ascii=False))
            print(out, 'arquivos',len(sha));return
if __name__=='__main__':
    try:main()
    except (DomainError,ValueError) as ex:
        print('ERRO:',ex,file=sys.stderr);sys.exit(2)
