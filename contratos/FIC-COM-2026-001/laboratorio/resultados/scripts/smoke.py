import json, sys, urllib.request, urllib.error
B='http://127.0.0.1:8765'; F='http://127.0.0.1:8777'
res=[]
def call(base,path,method='GET',body=None,tok=None):
    h={'Content-Type':'application/json'}
    if tok:h['Authorization']='Bearer '+tok
    r=urllib.request.Request(base+path,method=method,headers=h,data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(r) as x:return x.status,x.read().decode()
    except urllib.error.HTTPError as e:return e.code,e.read().decode()
def chk(name,got,exp):
    ok=got==exp;res.append((name,exp,got,'PASSOU' if ok else 'FALHOU'));
def login(u):
    s,b=call(B,'/api/login','POST',{'username':u,'password':f'demo-{u}-senha-forte-2026'});return json.loads(b)['token']
ad,ed,rv,lv=[login(u) for u in ('admin','editor','revisor','leitor')]
chk('Login com senha errada',call(B,'/api/login','POST',{'username':'editor','password':'errada-123456'})[0],401)
chk('API sem token',call(B,'/api/channels')[0],401)
chk('Token adulterado',call(B,'/api/channels',tok=ed[:-2]+'xx')[0],401)
s,b=call(B,'/api/channels','POST',{'name':'Boletim interno DEMO','description':'Canal de teste'},ed);chk('Editor cria canal',s,201);ch=json.loads(b)['id']
chk('Leitor tenta criar canal',call(B,'/api/channels','POST',{'name':'X canal'},lv)[0],403)
s,b=call(B,'/api/posts','POST',{'channel_id':ch,'title':'Circular DEMO','body':'Conteúdo de teste institucional'},ed);chk('Editor cria publicação',s,201);pid=json.loads(b)['id']
chk('Publicar sem aprovação',call(B,f'/api/posts/{pid}/publish','POST',None,rv)[0],409)
chk('Enviar para revisão',call(B,f'/api/posts/{pid}/submit','POST',None,ed)[0],200)
chk('Editor tenta aprovar',call(B,f'/api/posts/{pid}/approve','POST',None,ed)[0],403)
chk('Revisor aprova (pessoa distinta)',call(B,f'/api/posts/{pid}/approve','POST',None,rv)[0],200)
s,b=call(B,f'/api/posts/{pid}/publish','POST',None,rv);chk('Revisor publica',s,200);chk('Envio externo não simulado',json.loads(b)['external_delivery'],'NAO_EXECUTADA')
# autoaprovação pelo ADMIN autor
s,b=call(B,'/api/posts','POST',{'channel_id':ch,'title':'Post do admin','body':'Conteúdo criado pelo admin'},ad);p2=json.loads(b)['id']
call(B,f'/api/posts/{p2}/submit','POST',None,ad)
chk('ADMIN autor tenta autoaprovar',call(B,f'/api/posts/{p2}/approve','POST',None,ad)[0],409)
chk('Campanha',call(B,'/api/campaigns','POST',{'name':'Campanha DEMO','objective':'Teste de campanha'},ed)[0],201)
chk('Contato com consentimento',call(B,'/api/contacts','POST',{'name':'Pessoa DEMO','email':'demo@example.invalid','consent':True},ed)[0],201)
chk('Leitor lista contatos (dados pessoais)',call(B,'/api/contacts',tok=lv)[0],403)
s,b=call(B,'/api/tickets','POST',{'subject':'Dúvida DEMO','description':'Descrição do chamado de teste','priority':'ALTA'},ed);chk('Abrir chamado',s,201);tid=json.loads(b)['id']
chk('Prioridade inválida',call(B,'/api/tickets','POST',{'subject':'Dúvida DEMO','description':'Descrição do chamado','priority':'URGENTE'},ed)[0],422)
chk('Resolver chamado',call(B,f'/api/tickets/{tid}/status','PATCH',{'status':'RESOLVIDO'},ed)[0],200)
chk('Exportar CSV (revisor)',call(B,'/api/export/tickets.csv',tok=rv)[0],200)
chk('Exportar CSV (leitor)',call(B,'/api/export/tickets.csv',tok=lv)[0],403)
s,b=call(B,'/api/audit',tok=rv);chk('Trilha de auditoria',s,200);naud=len(json.loads(b))
s,b=call(B,'/api/overview',tok=lv);kp=json.loads(b)['kpis']
chk('Painel: publicadas=1',kp['posts_published'],1)
chk('Validação: senha curta em usuário',call(B,'/api/users','POST',{'name':'Novo','username':'novo','password':'curta','role':'EDITOR'},ad)[0],422)
# Fábrica
chk('Fábrica: aprovação sem frase correta',call(F,'/api/contracts/FIC-COM-2026-001/approve','POST',{'phrase':'ok'})[0],409)
chk('Fábrica: START sem plano aprovado',call(F,'/api/contracts/FIC-COM-2026-001/start','POST',{})[0],409)
s,b=call(F,'/api/tasks');t=json.loads(b);chk('Fábrica: 18 tarefas planejadas',len(t),18)
chk('Fábrica: soma planejada 12.000',sum(x['base_planned']*x['factor'] for x in t),12000)
s,b=call(F,'/api/team');chk('Fábrica: 10 posições de equipe',len(json.loads(b)),10)
chk('Fábrica: painel acessível SEM login (lacuna)',call(F,'/api/team')[0],200)
print(json.dumps({'checks':res,'eventos_auditoria':naud,'kpis':kp},ensure_ascii=False,indent=0))
sys.exit(0 if all(r[3]=='PASSOU' for r in res) else 1)
