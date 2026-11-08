#!/usr/bin/env python3
"""Digitalgov -- utilitário local e verificável de estado/handoff/relatório.

Não executa agentes, não lê PDF automaticamente, não cria bancos PostgreSQL,
não valida horas, nem registra aceite externo. Apenas organiza evidências informadas.
"""
import argparse, hashlib, json, re, sys, zipfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ=ZoneInfo('America/Sao_Paulo')

def now(): return datetime.now(TZ).isoformat(timespec='seconds')
def today(): return datetime.now(TZ).date().isoformat()
def valid_id(v):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{1,55}',v): raise ValueError('ID deve ter 2 a 56 caracteres: letras, números, - ou _.')
    return v

def read_json(p, default=None):
    if not p.exists(): return default
    return json.loads(p.read_text(encoding='utf-8'))

def atomic_json(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(p)

def append_event(p,event):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a',encoding='utf-8') as f: f.write(json.dumps(event,ensure_ascii=False,sort_keys=True)+'\n')

def events(p):
    if not p.exists(): return []
    out=[]
    for line in p.read_text(encoding='utf-8').splitlines():
        if line.strip(): out.append(json.loads(line))
    return out

def root_dir(args): return Path(args.root).expanduser().resolve()
def project_path(root,id): return root/'PROJETOS'/valid_id(id)
def require_project(root,id):
    p=project_path(root,id)
    if not (p/'ESTADO_PROJETO.json').exists(): raise ValueError(f'Projeto {id} não cadastrado. Use novo-projeto.')
    return p

def event(root,id,tipo,descricao,executor='usuario',evidencia='',status='REGISTRADO'):
    p=require_project(root,id)
    obj={'quando':now(),'tipo':tipo,'descricao':descricao,'executor':executor,'evidencia':evidencia,'status':status,'projeto_id':id}
    append_event(p/'EVENTOS.jsonl',obj)
    return obj

def setup(args):
    root=root_dir(args)
    (root/'CONTROL_CENTER').mkdir(parents=True,exist_ok=True)
    (root/'CONTRATOS').mkdir(exist_ok=True)
    (root/'PROJETOS').mkdir(exist_ok=True)
    f=root/'CONTROL_CENTER'/'ESTADO_GERAL.json'
    if not f.exists(): atomic_json(f,{'versao':'1.0','criado_em':now(),'projetos':[],'observacao':'Sem trabalhos executados ou horas apontadas.'})
    print('Central inicializada em:',root)

def new_project(args):
    root=root_dir(args)
    if not (root/'CONTROL_CENTER'/'ESTADO_GERAL.json').exists(): raise ValueError('Execute init primeiro.')
    id=valid_id(args.id); p=project_path(root,id)
    if (p/'ESTADO_PROJETO.json').exists(): raise ValueError('ID já cadastrado; nada foi sobrescrito.')
    folders=['REQUISITOS','PLANEJAMENTO','DIAGRAMAS','CODIGO/frontend','CODIGO/backend','CODIGO/database','CODIGO/tests','PRODUTOS_TECNICOS','EVIDENCIAS','MEDICOES','RELATORIOS','ENTREGAS','DIARIO']
    for d in folders:(p/d).mkdir(parents=True,exist_ok=True)
    s={'id':id,'nome':args.nome,'contrato_id':args.contrato or None,'tipo_servico':args.tipo,'fase':'ESCOPAR','gate':'PENDENTE','autorizacao_os':'NAO_COMPROVADA','ultima_atualizacao':now(),'ultimo_dia_fechado':None,'ultimo_passo':'Ler contrato/OS e montar escopo','pendencias':['Anexar fonte contratual e identificar autorização da OS.'],'horas_humanas_registradas':0,'ust_executadas_verificadas':0,'observacao':'Projeto criado; nenhum serviço executado automaticamente.'}
    atomic_json(p/'ESTADO_PROJETO.json',s)
    atomic_json(p/'CONTRATO_FONTE.json',{'contrato_id':args.contrato or None,'fonte':'NAO_ANEXADA','status':'DOCUMENTO_NAO_VERIFICADO'})
    (p/'EVENTOS.jsonl').touch()
    (p/'CLAUDE.md').write_text(f'# Projeto {id} | {args.nome}\n\nLeia ESTADO_PROJETO.json, HANDOFF_ULTIMO_CHAT.md, EVENTOS.jsonl e documentos aprovados. **Não presuma horas ou UST.** Não saia deste projeto sem autorização.\n',encoding='utf-8')
    (p/'PROMPT_PARA_NOVO_CHAT.md').write_text(f'# CHAT DO PROJETO {id}\n\nVocê está no projeto **{args.nome}** (ID `{id}`), contrato `{args.contrato or 'pendente'}`. Leia `CLAUDE.md`, `ESTADO_PROJETO.json`, `HANDOFF_ULTIMO_CHAT.md` (se houver), `EVENTOS.jsonl` e os documentos anexados. Compare com código real, resuma o que foi feito e o próximo passo; não invente execução anterior. Inicie em ESCOPAR até aprovação da OS.\n',encoding='utf-8')
    g=root/'CONTROL_CENTER'/'ESTADO_GERAL.json'; idx=read_json(g);idx['projetos'].append({'id':id,'nome':args.nome,'contrato_id':args.contrato or None});atomic_json(g,idx)
    event(root,id,'PROJETO_CRIADO','Estrutura de arquivos inicial criada; nenhum trabalho contratual executado.',status='PREPARACAO')
    print('Projeto criado:',p)

def last_summary(p):
    hand=p/'HANDOFF_ULTIMO_CHAT.md'
    return hand.read_text(encoding='utf-8')[:3500] if hand.exists() else 'Não há handoff anterior registrado.'

def day_open(args):
    root=root_dir(args);p=require_project(root,args.id);s=read_json(p/'ESTADO_PROJETO.json');log=events(p/'EVENTOS.jsonl')
    print(f'ABERTURA DE DIA {today()} | {args.id} | {s["nome"]}\nEstado: {s["fase"]}/{s["gate"]}; OS: {s["autorizacao_os"]}')
    print('Último passo:',s['ultimo_passo']);print('Pendências:', '; '.join(s['pendencias']) or 'nenhuma registrada')
    print('Últimos eventos:')
    for v in log[-7:]:print('-',v['quando'],v['tipo'],v['descricao'][:200])
    print('Último handoff:\n',last_summary(p))
    event(root,args.id,'ABERTURA_DIA','Resumo consultado; nenhuma execução ou hora acrescentada.',status='CONSULTA')

def log_task(args):
    root=root_dir(args);p=require_project(root,args.id)
    if args.tipo=='ENTREGA' and not args.evidencia:raise ValueError('Para ENTREGA informe --evidencia com arquivo existente.')
    evidence=''
    if args.evidencia:
        path=Path(args.evidencia).expanduser().resolve()
        if not path.is_file():raise ValueError('Evidência não encontrada: '+str(path))
        h=hashlib.sha256(path.read_bytes()).hexdigest()
        evidence=f'{path} SHA256:{h}'
    ev=event(root,args.id,args.tipo,args.descricao,executor=args.executor,evidencia=evidence,status='REGISTRADO_NAO_HOMOLOGADO')
    statefile=p/'ESTADO_PROJETO.json';s=read_json(statefile);s['ultima_atualizacao']=now();s['ultimo_passo']=args.proximo or s['ultimo_passo'];atomic_json(statefile,s)
    print('Evento registrado (sem aceite e sem medição):',ev['quando'],ev['tipo'])

def day_close(args):
    root=root_dir(args)
    if args.id.upper() == 'TODOS':
        idx=read_json(root/'CONTROL_CENTER'/'ESTADO_GERAL.json',{'projetos':[]})
        day=args.data or today()
        summaries=[f'# RELATÓRIO CONSOLIDADO INTERNO — {day}',f'**Gerado em:** {now()}','', 'Este consolidado refere-se exclusivamente a registros persistidos no workspace. Não equivale a aceite, medição ou homologação.','']
        if not idx['projetos']:summaries.append('Nenhum projeto cadastrado; nenhuma execução demonstrada.')
        for project in idx['projetos']:
            id=project['id']
            day_close(argparse.Namespace(root=args.root,id=id,data=day))
            p=project_path(root,id)
            state=read_json(p/'ESTADO_PROJETO.json')
            recent=[x for x in events(p/'EVENTOS.jsonl') if x['quando'].startswith(day) and x['tipo'] not in ('ABERTURA_DIA','FECHAMENTO_DIA')]
            summaries += [f'## {id} — {state["nome"]}',f'- Gate: {state["fase"]} / {state["gate"]}',f'- Eventos documentados: {len(recent)}',f'- Próximo passo: {state["ultimo_passo"]}',f'- Horas humanas verificadas: não apuradas por este utilitário',f'- UST homologadas: não apuradas por este utilitário','']
        folder=root/'CONTROL_CENTER'/'RELATORIOS_CONSOLIDADOS';folder.mkdir(parents=True,exist_ok=True)
        target=folder/f'RELATORIO_CONSOLIDADO_{day}.md';target.write_text('\n'.join(summaries)+'\n',encoding='utf-8')
        print('Consolidado:',target)
        return
    p=require_project(root,args.id);s=read_json(p/'ESTADO_PROJETO.json')
    day=args.data or today()
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',day):raise ValueError('Data deve ser AAAA-MM-DD')
    rows=[x for x in events(p/'EVENTOS.jsonl') if x['quando'].startswith(day)]
    meaningful=[x for x in rows if x['tipo'] not in ('ABERTURA_DIA','FECHAMENTO_DIA')]
    md=[f'# RELATÓRIO DIÁRIO INTERNO — {s["nome"]}',f'**Projeto:** {args.id} | **Data:** {day} | **Gerado em:** {now()}',f'**Fase/Gate:** {s["fase"]} / {s["gate"]}',f'**Autorização de OS:** {s["autorizacao_os"]}', '', '## Eventos documentados']
    if not meaningful: md.append('Não há atividades executadas documentadas neste período. Não presumir execução.')
    for v in meaningful:md.append(f'- {v["quando"]} | {v["tipo"]} | {v["descricao"]} | executor informado: {v["executor"]} | evidência: {v["evidencia"] or "não anexada"}')
    md.extend(['','## Medição e jornada','**Horas humanas:** não calculadas neste utilitário; dependem de lançamentos reais e validação em módulo contratual.','**UST verificadas:** nenhuma UST nova foi computada automaticamente.','**Aceite do órgão:** não presumido.','','## Pendências'])
    md.extend('- '+x for x in s['pendencias'])
    md.extend(['','## Próximo passo',s['ultimo_passo'],'','## Preparação do próximo chat',f'Leia `ESTADO_PROJETO.json`, `EVENTOS.jsonl`, este relatório e `HANDOFF_ULTIMO_CHAT.md` antes de continuar.'])
    (p/'DIARIO'/f'{day}.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    hand=[f'# HANDOFF — {args.id}',f'**Atualizado em:** {now()}',f'**Relatório fechado:** {day}',f'**Fase:** {s["fase"]} | **Gate:** {s["gate"]}',f'**OS:** {s["autorizacao_os"]}',f'**Último passo:** {s["ultimo_passo"]}', '', '## Eventos mais recentes']
    hand.extend(f'- {x["quando"]} [{x["tipo"]}] {x["descricao"]}' for x in events(p/'EVENTOS.jsonl')[-12:]);hand.append('## Pendências');hand.extend('- '+x for x in s['pendencias'])
    (p/'HANDOFF_ULTIMO_CHAT.md').write_text('\n'.join(hand)+'\n',encoding='utf-8')
    s['ultimo_dia_fechado']=day;s['ultima_atualizacao']=now();atomic_json(p/'ESTADO_PROJETO.json',s)
    event(root,args.id,'FECHAMENTO_DIA',f'Relatório diário e handoff gravados para {day}',status='DOCUMENTOS_GERADOS')
    print('Relatório diário:',p/'DIARIO'/f'{day}.md');print('Handoff:',p/'HANDOFF_ULTIMO_CHAT.md')

def status(args):
    root=root_dir(args); idx=read_json(root/'CONTROL_CENTER'/'ESTADO_GERAL.json',{'projetos':[]})
    for p in idx['projetos']:
        s=read_json(project_path(root,p['id'])/'ESTADO_PROJETO.json',{})
        print(f'{p["id"]} | {p["nome"]} | {s.get("fase","?")} | OS {s.get("autorizacao_os","?")} | fechamento {s.get("ultimo_dia_fechado","-")}')
    if not idx['projetos']:print('Nenhum projeto cadastrado.')

def kit(args):
    root=root_dir(args);p=require_project(root,args.id)
    out=Path(args.saida).expanduser().resolve() if args.saida else root/f'KIT_HANDOFF_{args.id}.zip'
    names=['ESTADO_PROJETO.json','CONTRATO_FONTE.json','CLAUDE.md','PROMPT_PARA_NOVO_CHAT.md','HANDOFF_ULTIMO_CHAT.md','EVENTOS.jsonl']
    names+=sorted(str(x.relative_to(p)) for x in (p/'DIARIO').glob('*.md'))[-5:]
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in names:
            f=p/name
            if f.exists():z.write(f,arcname=f'{args.id}/{name}')
    print('Kit criado:',out,'- Verifique confidencialidade antes de compartilhar.')

def main():
    a=argparse.ArgumentParser(description='Digitalgov — estado e continuidade entre chats sem dados inventados');a.add_argument('--root',default='./DIGITALGOV_WORKSPACE',help='Pasta persistente')
    sub=a.add_subparsers(dest='cmd',required=True)
    sub.add_parser('init')
    n=sub.add_parser('novo-projeto');n.add_argument('--id',required=True);n.add_argument('--nome',required=True);n.add_argument('--contrato',default='');n.add_argument('--tipo',default='NAO_CLASSIFICADO')
    for cmd in ['abrir-dia','status','fechar-dia','kit-handoff','registrar']:sub.add_parser(cmd)
    for cmd in ['abrir-dia','fechar-dia','kit-handoff','registrar']:sub.choices[cmd].add_argument('--id',required=True)
    l=sub.choices['registrar'];l.add_argument('--tipo',default='NOTA');l.add_argument('--descricao',required=True);l.add_argument('--executor',default='usuario');l.add_argument('--evidencia',default='');l.add_argument('--proximo',default='')
    sub.choices['fechar-dia'].add_argument('--data',default='')
    sub.choices['kit-handoff'].add_argument('--saida',default='')
    args=a.parse_args()
    try:
        {'init':setup,'novo-projeto':new_project,'abrir-dia':day_open,'registrar':log_task,'fechar-dia':day_close,'status':status,'kit-handoff':kit}[args.cmd](args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:print('ERRO:',exc,file=sys.stderr);sys.exit(2)
if __name__=='__main__':main()
