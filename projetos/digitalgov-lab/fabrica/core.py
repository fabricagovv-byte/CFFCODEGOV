"""Operações reais de tarefas, horários, evidências e UST laboratoriais.
Nunca atribui horas de IA a pessoas ou aceita OS simulada como oficial.
"""
import hashlib, json, re
from pathlib import Path
from datetime import datetime, timezone
from .db import now, append_audit, integrity_check, ROOT

class DomainError(ValueError): pass

def evidence_hash(path):
    f = Path(path).expanduser().resolve()
    if not f.is_file(): raise DomainError(f'Evidência não existe: {f}')
    h=hashlib.sha256()
    with f.open('rb') as source:
        for chunk in iter(lambda:source.read(128*1024),b''):h.update(chunk)
    return str(f),h.hexdigest()

def create_task(c, order_id, description, actor_kind, actor, base_proposed=0):
    order=c.execute('SELECT * FROM orders WHERE id=?',(order_id,)).fetchone()
    if order is None: raise DomainError('OS não encontrada')
    if actor_kind not in ('HUMANO','AGENTE'): raise DomainError('executor deve ser HUMANO ou AGENTE')
    if not actor.strip() or not description.strip(): raise DomainError('executor/descrição obrigatórios')
    if base_proposed < 0: raise DomainError('UST base negativa')
    c.execute('BEGIN IMMEDIATE')
    try:
        cur=c.execute('INSERT INTO tasks(project_id,order_id,description,assignee_kind,assignee,base_proposed,created_at) VALUES (?,?,?,?,?,?,?)',(order['project_id'],order_id,description.strip(),actor_kind,actor.strip(),int(base_proposed),now()))
        append_audit(c,actor,'TAREFA_CRIADA',{'task_id':cur.lastrowid,'order_id':order_id,'base_proposed':base_proposed})
        c.execute('COMMIT')
        return cur.lastrowid
    except Exception:
        c.execute('ROLLBACK'); raise

def start_task(c,task_id):
    t=c.execute('SELECT * FROM tasks WHERE id=?',(task_id,)).fetchone()
    if t is None or t['state']!='ABERTA': raise DomainError('Tarefa inexistente ou não está ABERTA')
    c.execute('BEGIN IMMEDIATE')
    try:
        at=now();c.execute("UPDATE tasks SET state='EM_EXECUCAO',started_at=? WHERE id=?",(at,task_id))
        c.execute('INSERT INTO sessions(task_id,actor_kind,actor,started_at) VALUES (?,?,?,?)',(task_id,t['assignee_kind'],t['assignee'],at))
        c.execute("UPDATE projects SET status='EM_EXECUCAO' WHERE id=?",(t['project_id'],))
        append_audit(c,t['assignee'],'TAREFA_INICIADA',{'task_id':task_id,'inicio_real':at})
        c.execute('COMMIT')
    except Exception:
        c.execute('ROLLBACK'); raise

def finish_task(c,task_id,evidence,commit,test_result):
    t=c.execute('SELECT * FROM tasks WHERE id=?',(task_id,)).fetchone()
    if t is None or t['state']!='EM_EXECUCAO': raise DomainError('A tarefa não está em execução')
    path,sha=evidence_hash(evidence)
    if test_result not in ('PASS','FAIL','NOT_APPLICABLE'): raise DomainError('Resultado do teste inválido')
    if commit and not re.fullmatch('[0-9a-fA-F]{7,40}',commit): raise DomainError('Commit deve ter hash Git de 7 a 40 caracteres; não invente hashes')
    c.execute('BEGIN IMMEDIATE')
    try:
        at=now();c.execute("UPDATE tasks SET state='FINALIZADA',evidence_path=?,evidence_sha256=?,git_commit=?,test_result=?,finished_at=? WHERE id=?",(path,sha,commit, test_result,at,task_id))
        c.execute('UPDATE sessions SET ended_at=?,evidence_path=? WHERE task_id=? AND ended_at IS NULL',(at,path,task_id))
        append_audit(c,t['assignee'],'TAREFA_FINALIZADA',{'task_id':task_id,'evidence_sha256':sha,'test_result':test_result,'fim_real':at})
        c.execute('COMMIT')
    except Exception:
        c.execute('ROLLBACK'); raise

def verify_task(c, task_id, reviewer, base_verified):
    t=c.execute('SELECT * FROM tasks WHERE id=?',(task_id,)).fetchone()
    if not t or t['state']!='FINALIZADA': raise DomainError('Tarefa precisa estar FINALIZADA')
    if not reviewer.strip(): raise DomainError('Revisor identificado obrigatório')
    if reviewer.strip().casefold()==t['assignee'].strip().casefold(): raise DomainError('Revisão independente obrigatória: executor não pode conferir a própria tarefa')
    if t['test_result']!='PASS': raise DomainError('Medição interna exige evidência de teste PASS')
    path,sha=evidence_hash(t['evidence_path'])
    if sha!=t['evidence_sha256']: raise DomainError('Evidência alterada após conclusão da tarefa')
    base_verified=int(base_verified)
    if base_verified<0 or base_verified>t['base_proposed']: raise DomainError('UST verificadas devem estar entre 0 e UST propostas para a tarefa')
    # Limite matemático da OS, sem inventar quantidade, duplica nem ultrapassa meta.
    order=c.execute('SELECT * FROM orders WHERE id=?',(t['order_id'],)).fetchone()
    previous=c.execute('SELECT coalesce(sum(base_verified),0) total FROM tasks WHERE order_id=?',(t['order_id'],)).fetchone()['total']
    if previous+base_verified>order['base_target']: raise DomainError('Medição acima da meta base da OS simulada; requer nova análise')
    c.execute('BEGIN IMMEDIATE')
    try:
        at=now();c.execute("UPDATE tasks SET state='VERIFICADA',reviewer=?,reviewed_at=?,base_verified=? WHERE id=?",(reviewer,at,base_verified,task_id))
        append_audit(c,reviewer,'VERIFICACAO_TECNICA_INTERNA',{'task_id':task_id,'base':base_verified,'factor':order['factor'],'adjusted':base_verified*order['factor'],'nota':'APENAS LABORATÓRIO; NÃO HOMOLOGADO PELO ÓRGÃO'})
        c.execute('COMMIT')
    except Exception:
        c.execute('ROLLBACK');raise
    return base_verified*order['factor']

def add_external_acceptance(c,order_id,base,authority_name,document):
    """Só funciona com OS oficial autorizada e documento de aceite existente."""
    order=c.execute('SELECT * FROM orders WHERE id=?',(order_id,)).fetchone()
    if order is None or order['status']!='AUTORIZADA' or not order['official_order_ref'] or not order['catalog_version']:
        raise DomainError('Aceite oficial BLOQUEADO: exige OS oficial autorizada e catálogo pactuado')
    path,sha=evidence_hash(document)
    verified=c.execute("SELECT coalesce(sum(base_verified),0) x FROM tasks WHERE order_id=? AND state='VERIFICADA'",(order_id,)).fetchone()['x']
    prior=c.execute('SELECT coalesce(sum(base_approved),0) x FROM acceptances WHERE order_id=?',(order_id,)).fetchone()['x']
    if base<=0 or base+prior>verified:raise DomainError('Aceite não pode exceder a produção verificada')
    if not authority_name.strip():raise DomainError('Autoridade competente obrigatória')
    c.execute('BEGIN IMMEDIATE')
    try:
        c.execute('INSERT INTO acceptances(order_id,base_approved,authority_name,document_path,document_sha256,approval_at) VALUES (?,?,?,?,?,?)',(order_id,base,authority_name,path,sha,now()))
        append_audit(c,authority_name,'ACEITE_EXTERNO_DOCUMENTADO',{'order_id':order_id,'base':base,'sha256':sha})
        c.execute('COMMIT')
    except Exception:
        c.execute('ROLLBACK');raise

def snapshot(c):
    p=[dict(r) for r in c.execute('SELECT * FROM projects ORDER BY id')]
    os=[dict(r) for r in c.execute('''SELECT o.*,p.name project_name, pe.name overseer,
       (SELECT COALESCE(SUM(base_verified),0) FROM tasks t WHERE t.order_id=o.id AND t.state='VERIFICADA') AS base_verified,
       (SELECT COALESCE(SUM(base_approved),0) FROM acceptances a WHERE a.order_id=o.id) AS base_accepted
       FROM orders o JOIN projects p ON p.id=o.project_id LEFT JOIN people pe ON pe.id=o.oversight_person_id ORDER BY o.id''')]
    tasks=[dict(r) for r in c.execute('SELECT * FROM tasks ORDER BY id DESC LIMIT 250')]
    sessions=[dict(r) for r in c.execute('SELECT * FROM sessions ORDER BY id DESC LIMIT 300')]
    team=[dict(r) for r in c.execute('''SELECT pe.*, (SELECT COUNT(*) FROM orders o WHERE o.oversight_person_id=pe.id) os_count,
       (SELECT COALESCE(SUM(o.base_target*o.factor),0) FROM orders o WHERE o.oversight_person_id=pe.id) ust_meta_supervisionadas
       FROM people pe ORDER BY pe.id''')]
    audit=[dict(r) for r in c.execute('SELECT id,recorded_at,actor,kind,payload,chain_hash FROM audit ORDER BY id DESC LIMIT 100')]
    for o in os:
        o['ust_target']=o['base_target']*o['factor']
        o['ust_verified_lab']=o['base_verified']*o['factor']
        o['ust_official_accepted']=o['base_accepted']*o['factor']
    for person in team:
        # Tempo humano computado somente de sessões humanas encerradas, sem deduzir horas fictícias.
        rows=c.execute("SELECT s.started_at,s.ended_at,s.break_minutes FROM sessions s JOIN tasks t ON s.task_id=t.id WHERE s.actor_kind='HUMANO' AND s.actor=? AND s.ended_at IS NOT NULL",(person['name'] or '',)).fetchall()
        total=0
        for a in rows:
            total+=max(0,(datetime.fromisoformat(a['ended_at'])-datetime.fromisoformat(a['started_at'])).total_seconds()-a['break_minutes']*60)
        person['human_seconds_recorded']=int(total)
    return {'identity':'DIGITALGOV — laboratório não contratual','fetched_at':now(),'contract':'LAB-PE223-2026',
       'target_ust':sum(x['ust_target'] for x in os),'internal_verified_ust':sum(x['ust_verified_lab'] for x in os),
       'official_accepted_ust':sum(x['ust_official_accepted'] for x in os),
       'billable_ust':0, # Não emitir valor faturável automaticamente
       'project_count':len(p),'configured_agent_roles':100,'active_agent_processes':0,
       'catalog_status':'NÃO PACTUADO / SOMENTE LABORATÓRIO','previous_test_deadline':'2026-11-03T23:59:00-03:00',
       'projects':p,'orders':os,'tasks':tasks,'sessions':sessions,'team':team,'events':audit,
       'audit_chain_valid':integrity_check(c)}
