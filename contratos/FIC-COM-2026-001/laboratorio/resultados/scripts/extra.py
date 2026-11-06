import json,urllib.request,urllib.error
B='http://127.0.0.1:8765'
def call(path,method='GET',body=None,tok=None):
    h={'Content-Type':'application/json'}
    if tok:h['Authorization']='Bearer '+tok
    r=urllib.request.Request(B+path,method=method,headers=h,data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(r) as x:return x.status,x.read().decode()[:200]
    except urllib.error.HTTPError as e:return e.code,e.read().decode()[:200]
t=json.loads(call('/api/login','POST',{'username':'editor','password':'demo-editor-senha-forte-2026'})[1])['token']
lv=json.loads(call('/api/login','POST',{'username':'leitor','password':'demo-leitor-senha-forte-2026'})[1])['token']
out={}
out['chamado_com_contato_inexistente']=call('/api/tickets','POST',{'subject':'Teste FK','description':'contato inexistente','contact_id':9999},t)
out['campanha_com_canal_inexistente']=call('/api/campaigns','POST',{'name':'Camp X','objective':'canal 9999','channel_id':9999},t)
out['contato_email_invalido']=call('/api/contacts','POST',{'name':'Fulano','email':'isto-nao-e-email'},t)
out['csv_formula']=call('/api/tickets','POST',{'subject':'=HYPERLINK("http://x")','description':'teste de injeção em CSV'},t)
out['leitor_ve_chamados']=call('/api/tickets',tok=lv)[0]
fails=0
for i in range(12): fails+= call('/api/login','POST',{'username':'editor','password':'tentativa-errada-%d'%i})[0]==401
out['login_12_erros_sem_bloqueio']=fails
r=urllib.request.urlopen(B+'/'); out['cabecalhos_seguranca']={k:v for k,v in r.headers.items() if k.lower() in ('content-security-policy','x-frame-options','strict-transport-security','x-content-type-options')}
print(json.dumps(out,ensure_ascii=False,indent=1))
