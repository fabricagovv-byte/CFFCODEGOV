"""Rastreabilidade de requisitos, tarefas, horas humanas e medição. Jamais homologa sozinho."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,sqlite3
from .db import connect

def now():return datetime.now(timezone.utc).isoformat()
def audit(c,actor,action,details):c.execute('INSERT INTO audit(at,actor,action,details) VALUES(?,?,?,?)',(now(),actor,action,json.dumps(details,ensure_ascii=False)))

def seed(contract_id='FIC-COM-2026-001'):
    with connect() as c:
        if c.execute('SELECT 1 FROM contracts WHERE id=?',(contract_id,)).fetchone():return False
        c.execute('INSERT INTO contracts(id,title,contract_type,scope,ust_target,created_at) VALUES(?,?,?,?,?,?)',(contract_id,'Plataforma Integrada de Comunicação Institucional e Atendimento Digital','FICTICIO','18 módulos planejados, implementação incremental em seis meses',12000,now()))
        c.execute('INSERT INTO projects(id,contract_id,name,folder) VALUES(?,?,?,?)',('COM-001',contract_id,'Plataforma de Comunicação','PLATAFORMA_COMUNICACAO'))
        c.execute('INSERT INTO orders(id,contract_id,name,ust_target,complexity_catalog) VALUES(?,?,?,?,?)',('OS-FIC-001',contract_id,'Construção da Plataforma Integrada',12000,'CATALOGO-PROPOSTO-V1-NÃO-HOMOLOGADO'))
        names=['Jerlian','Ruan','Arthur Miguel','Warley','Werverton','João Miguel','Warley C.']
        for name in names:c.execute('INSERT INTO people(name,role,created_at) VALUES(?,?,?)',(name,'Revisão e contingência — atribuição a confirmar',now()))
        for _ in range(3):c.execute('INSERT INTO people(name,role,active,created_at) VALUES(?,?,0,?)',('[A CADASTRAR]','Pendente de indicação',now()))
        services=[('Identidade e RBAC', 'Autenticação, identidade, perfis, MFA/SSO conforme ambiente', 'DESENVOLVIMENTO', 270, 3), ('Canais e comunidades', 'Controle de canais internos e grupos', 'DESENVOLVIMENTO', 270, 3), ('Mural e comunicados', 'Feed, conteúdo, versão e publicação', 'DESENVOLVIMENTO', 150, 2), ('Fluxo editorial', 'Revisão independente, aprovação, trilha de publicação', 'DESENVOLVIMENTO', 270, 3), ('Campanhas e agenda editorial', 'Calendário, briefing, peças e indicadores', 'DESENVOLVIMENTO', 390, 3), ('Segmentação de públicos', 'Audiencias e segmentação com regras LGPD', 'DESENVOLVIMENTO', 160, 3), ('Contatos e consentimento', 'Cadastro protegido e consentimentos', 'DESENVOLVIMENTO', 200, 3), ('Atendimento e chamados', 'Protocolos, filas, prioridades e SLA', 'DESENVOLVIMENTO', 380, 3), ('Chat em tempo real', 'WebSockets, mensagens, histórico e privacidade', 'DESENVOLVIMENTO', 200, 2), ('Envio multicanal', 'Adaptadores e-mail, SMS e push, confirmação e opt-out', 'INTEGRACAO', 200, 2), ('Portal público', 'Portal do cidadão acessível', 'DESENVOLVIMENTO', 200, 3), ('Acervo digital', 'Uploads, segurança e retenção documental', 'DESENVOLVIMENTO', 240, 2), ('Agenda e eventos', 'Inscrições, agenda e lembretes', 'DESENVOLVIMENTO', 220, 3), ('Pesquisas e feedback', 'Questionários, respostas e exportações', 'DESENVOLVIMENTO', 180, 3), ('BI e indicadores', 'Dashboards conciliáveis com o banco', 'BI', 240, 2), ('APIs e integrações', 'Conectores, webhooks, APIs versionadas', 'INTEGRACAO', 200, 3), ('Segurança e LGPD', 'Acesso, auditoria, retenção e riscos', 'SEGURANCA', 200, 2), ('DevOps, manuais e homologação', 'CI/CD, backups, monitoramento, testes, releases', 'DEVOPS', 440, 3)]
        for title,desc,service,base,factor in services:
            c.execute('INSERT INTO tasks(project_id,order_id,title,description,service,base_planned,factor) VALUES(?,?,?,?,?,?,?)',('COM-001','OS-FIC-001',title,desc,service,base,factor))
        audit(c,'sistema','SEED_FICTICIO',{'contract_id':contract_id,'note':'Metas ilustrativas; nenhuma UST executada ou homologada'})
    return True

def overview(c):
    counts=c.execute('SELECT COUNT(*) projects FROM projects').fetchone()['projects']
    planned=c.execute('SELECT COALESCE(SUM(base_planned*factor),0) v FROM tasks').fetchone()['v']
    checked=c.execute("SELECT COALESCE(SUM(adjusted),0) v FROM measurements WHERE status IN ('VERIFICADA','HOMOLOGADA')").fetchone()['v']
    approved=c.execute("SELECT COALESCE(SUM(adjusted),0) v FROM measurements WHERE status='HOMOLOGADA'").fetchone()['v']
    bystatus={r['status']:r['total'] for r in c.execute('SELECT status,COUNT(*) total FROM tasks GROUP BY status')}
    return {'projects':counts,'ust_target':c.execute('SELECT COALESCE(SUM(ust_target),0) FROM contracts').fetchone()[0], 'ust_planned':planned,'ust_verified':checked,'ust_homologated':approved,'tasks_by_status':bystatus,'agents_configured':100,'agents_running':0,'note':'Sem agente Codex conectado; alocações não são execuções reais'}

def approve_contract(cid,actor,phrase):
    if phrase!=f'APROVO PLANO {cid}':raise ValueError('Confirmação expressa incorreta')
    with connect() as c:
        x=c.execute('SELECT status FROM contracts WHERE id=?',(cid,)).fetchone()
        if not x or x['status']!='RASCUNHO':raise ValueError('Contrato inexistente ou já aprovado')
        c.execute("UPDATE contracts SET status='PLANO_APROVADO',approved_at=? WHERE id=?",(now(),cid))
        c.execute('UPDATE orders SET authorized=1 WHERE contract_id=?',(cid,))
        audit(c,actor,'PLANO_APROVADO',{'contract_id':cid})

def prepare_start(cid,actor):
    """Cria instruções por tarefa. Não finge execução de código nem inicia agentes."""
    from .db import DB
    with connect() as c:
        contract=c.execute('SELECT * FROM contracts WHERE id=?',(cid,)).fetchone()
        if not contract or contract['status'] not in ('PLANO_APROVADO','EM_EXECUCAO'):raise ValueError('Planejamento não aprovado')
        tasks=c.execute("SELECT t.* FROM tasks t JOIN projects p ON p.id=t.project_id WHERE p.contract_id=? AND t.status='PLANEJADA'",(cid,)).fetchall()
        inbox=DB.parent/'codex_inbox';inbox.mkdir(parents=True,exist_ok=True)
        for t in tasks:
            out=inbox/f'TAREFA_{t["id"]:04d}.md'
            out.write_text(f'# INSTRUÇÃO CODEX — Tarefa {t["id"]}\nContrato: {cid}\nProjeto: {t["project_id"]}\nAtividade: {t["title"]}\nDescrição: {t["description"]}\n\nImplemente e teste somente o escopo autorizado. Não declare UST executada; anexar arquivos e testes reais para revisão.\n',encoding='utf-8')
            c.execute("UPDATE tasks SET status='PRONTA_CODEX' WHERE id=?",(t['id'],))
        c.execute("UPDATE contracts SET status='EM_EXECUCAO' WHERE id=?",(cid,))
        audit(c,actor,'START_PREPARADO',{'contract_id':cid,'prompts_gerados':len(tasks),'executor':'manual/external connector pending'})
        return {'prepared':len(tasks),'path':str(inbox),'started_agents':0,'message':'Instruções geradas. A execução do Codex depende de conexão e autorização externa.'}

def register_evidence(task_id,path,tests_result,actor):
    if tests_result not in ('PASS','FAIL','NOT_APPLICABLE'):raise ValueError('Resultado de teste inválido')
    p=Path(path).expanduser().resolve()
    if not p.is_file():raise ValueError('Evidência não encontrada')
    sha=hashlib.sha256(p.read_bytes()).hexdigest()
    with connect() as c:
        task=c.execute('SELECT * FROM tasks WHERE id=?',(task_id,)).fetchone()
        if not task:raise ValueError('Tarefa não encontrada')
        if task['status'] not in ('PRONTA_CODEX','EM_EXECUCAO','ENTREGUE'):raise ValueError('Tarefa não está apta a entregar')
        c.execute("UPDATE tasks SET status='ENTREGUE',evidence_path=?,evidence_sha256=?,tests_result=?,ended_at=? WHERE id=?",(str(p),sha,tests_result,now(),task_id))
        audit(c,actor,'EVIDENCIA_ANEXADA',{'task_id':task_id,'hash':sha,'tests':tests_result})
    return sha

def verify_task(task_id,reviewer,ust_base):
    with connect() as c:
        task=c.execute('SELECT * FROM tasks WHERE id=?',(task_id,)).fetchone()
        if not task or task['status']!='ENTREGUE' or task['tests_result']!='PASS':raise ValueError('Tarefa não entregue com testes aprovados')
        path=Path(task['evidence_path'])
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=task['evidence_sha256']:raise ValueError('Evidência ausente ou alterada')
        if ust_base<0 or ust_base>task['base_planned']:raise ValueError('UST base fora da meta planejada: revisão de OS necessária')
        val=float(ust_base)*task['factor']
        c.execute("UPDATE tasks SET status='VERIFICADA',verified_by=?,verified_at=? WHERE id=?",(reviewer,now(),task_id))
        c.execute("INSERT INTO measurements(task_id,ust_base,factor,adjusted,status,reviewer,reviewed_at) VALUES(?,?,?,?,?,?,?)",(task_id,ust_base,task['factor'],val,'VERIFICADA',reviewer,now()))
        audit(c,reviewer,'MEDICAO_VERIFICADA',{'task_id':task_id,'ust_base':ust_base,'factor':task['factor'],'adjusted':val})
    return val

def register_acceptance(task_id,ref,actor):
    p=Path(ref).expanduser().resolve()
    if not p.is_file():raise ValueError('Arquivo de termo de aceite obrigatório; referência textual isolada não basta')
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    with connect() as c:
        row=c.execute('SELECT * FROM measurements WHERE task_id=?',(task_id,)).fetchone()
        if not row or row['status']!='VERIFICADA':raise ValueError('Medição ainda não verificada')
        c.execute("UPDATE measurements SET status='HOMOLOGADA',external_acceptance_ref=? WHERE task_id=?",(str(p)+'#sha256='+digest,task_id))
        audit(c,actor,'ACEITE_DOCUMENTAL_REGISTRADO',{'task_id':task_id,'path':str(p),'sha256':digest,'authenticity_verified_externally':False})

def record_human_hours(person_id,project_id,started_at,ended_at,break_minutes,activity,evidence):
    start=datetime.fromisoformat(started_at);end=datetime.fromisoformat(ended_at)
    if not start.tzinfo or not end.tzinfo:raise ValueError('Horários devem ter fuso')
    if end<=start or not 0<=break_minutes<((end-start).total_seconds()/60):raise ValueError('Jornada ou intervalo inválido')
    if (end-start).total_seconds()>16*3600:raise ValueError('Jornada superior a 16h requer análise, não registrada automaticamente')
    ep=Path(evidence).expanduser().resolve()
    if not ep.is_file():raise ValueError('Evidência humana obrigatória')
    start_u=start.astimezone(timezone.utc).isoformat();end_u=end.astimezone(timezone.utc).isoformat()
    with connect() as c:
        for r in c.execute('SELECT started_at,ended_at FROM time_logs WHERE person_id=?',(person_id,)).fetchall():
            if start_u<r['ended_at'] and end_u>r['started_at']:raise ValueError('Períodos humanos sobrepostos')
        c.execute('INSERT INTO time_logs(person_id,project_id,started_at,ended_at,break_minutes,activity,evidence_path,created_at) VALUES(?,?,?,?,?,?,?,?)',(person_id,project_id,start_u,end_u,break_minutes,activity,str(ep),now()))
        audit(c,'humano','JORNADA_REGISTRADA',{'person_id':person_id,'minutes':(end-start).total_seconds()/60-break_minutes,'evidence':str(ep)})
    return round((end-start).total_seconds()/3600-break_minutes/60,2)
