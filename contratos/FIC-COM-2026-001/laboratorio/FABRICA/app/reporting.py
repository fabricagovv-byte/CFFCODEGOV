"""Relatório de EXECUÇÃO real do banco local. Não homologa nem preenche horas artificiais."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from .db import connect,init
from .core import overview

def make_report(output: str, contract_id: str = 'FIC-COM-2026-001') -> Path:
    init()
    with connect() as c:
        contract=c.execute('SELECT * FROM contracts WHERE id=?',(contract_id,)).fetchone()
        if contract is None:raise ValueError(f'Contrato não encontrado: {contract_id}')
        info=dict(contract)
        projects=[dict(x) for x in c.execute('SELECT * FROM projects WHERE contract_id=? ORDER BY id',(contract_id,))]
        tasks=[dict(x) for x in c.execute('SELECT t.* FROM tasks t JOIN projects p ON t.project_id=p.id WHERE p.contract_id=? ORDER BY t.id',(contract_id,))]
        measurements=[dict(x) for x in c.execute('SELECT m.*,t.title,t.project_id FROM measurements m JOIN tasks t ON t.id=m.task_id JOIN projects p ON p.id=t.project_id WHERE p.contract_id=? ORDER BY m.id',(contract_id,))]
        people=[dict(x) for x in c.execute('SELECT id,name,seniority,role,active FROM people ORDER BY id')]
        hours=[dict(x) for x in c.execute('SELECT l.*,p.name FROM time_logs l JOIN people p ON p.id=l.person_id JOIN projects j ON j.id=l.project_id WHERE j.contract_id=? ORDER BY l.started_at',(contract_id,))]
        logs=[dict(x) for x in c.execute('SELECT at,actor,action,details FROM audit ORDER BY id DESC LIMIT 25')]
        kpi=overview(c)
    d=Document();s=d.sections[0];s.top_margin=Inches(.8);s.bottom_margin=Inches(.8)
    st=d.styles['Normal'];st.font.name='Aptos';st.font.size=Pt(9)
    def head(x):d.add_heading(x,1)
    def tab(header,rows):
        t=d.add_table(rows=1,cols=len(header));t.style='Light Shading Accent 1'
        for a,b in zip(t.rows[0].cells,header):a.text=str(b)
        for rr in rows:
            for a,b in zip(t.add_row().cells,rr):a.text=str(b)
        d.add_paragraph('')
    d.add_heading('RELATÓRIO TÉCNICO DE EXECUÇÃO — DIGITALGOV',0)
    d.add_paragraph(f'Gerado: {datetime.now(timezone.utc).isoformat()} | Fonte: SQLite local | Sem homologação automática.')
    d.add_paragraph('AVISO: documento gerado a partir de registros presentes na base. Não comprova por si só a atuação humana, a autenticidade de aceite externo ou o cumprimento integral do contrato.')
    head('1. Contrato e estágio')
    tab(['Campo','Valor'],[['Contrato',info['id']],['Objeto',info['title']],['Natureza',info['contract_type']],['Status interno',info['status']],['Meta UST proposta',info['ust_target']],['Projetos cadastrados',len(projects)]])
    head('2. Progresso real do banco')
    tab(['Indicador','Quantidade'],[['UST detalhadas em tarefas propostas',kpi['ust_planned']],['UST tecnicamente verificadas (internas)',kpi['ust_verified']],['UST com referência de aceite externo registrada',kpi['ust_homologated']],['Agentes reais de IA conectados',kpi['agents_running']],['Distribuição das tarefas',str(kpi['tasks_by_status'])]])
    head('3. Projetos')
    tab(['Identificador','Nome','Estado'],[[x['id'],x['name'],x['status']] for x in projects] or [['SEM PROJETOS','—','—']])
    head('4. Tarefas e escopo detalhado')
    tab(['ID','Tarefa','Serviço','Planejado (UST ajuste)','Estado','Teste'],[[x['id'],x['title'],x['service'],float(x['base_planned'])*x['factor'],x['status'],x['tests_result'] or 'NÃO INFORMADO'] for x in tasks] or [['SEM TAREFAS','—','—','—','—','—']])
    head('5. Medição, evidências e revisores')
    tab(['Tarefa','Base','Fator','Ajustada','Estado','Revisor'],[[x['task_id'],x['ust_base'],x['factor'],x['adjusted'],x['status'],x['reviewer'] or 'NÃO INFORMADO'] for x in measurements] or [['NENHUMA MEDIÇÃO REGISTRADA',0,'—',0,'—','—']])
    head('6. Profissionais reais e participação')
    tab(['ID','Profissional','Senioridade','Papel'],[[x['id'],x['name'],x['seniority'],x['role']] for x in people] or [['SEM CADASTRO','—','—','—']])
    head('7. Jornada humana comprovada')
    def calc_hours(x):
        a=datetime.fromisoformat(x['started_at']);b=datetime.fromisoformat(x['ended_at']);return round((b-a).total_seconds()/3600-x['break_minutes']/60,2)
    tab(['Profissional','Início UTC','Término UTC','Pausa min','Horas líquidas','Atividade'],[[x['name'],x['started_at'],x['ended_at'],x['break_minutes'],calc_hours(x),x['activity']] for x in hours] or [['NENHUM LANÇAMENTO HUMANO', '—','—',0,0,'Não inventar horários']])
    head('8. Eventos de auditoria')
    tab(['Data UTC','Ator','Evento'],[[x['at'],x['actor'],x['action']] for x in logs] or [['NENHUM EVENTO','—','—']])
    head('9. Pendências e aceite')
    d.add_paragraph('A relação entre trabalho planejado e serviço remunerável exige: OS e catálogo aprovados, execução verificável, validação dos requisitos, critérios contratuais de aceite e documento legítimo do cliente. O sistema não substitui o fiscal.')
    d.add_paragraph('As quantidades registradas não devem ser enviadas para faturamento sem revisão especializada. Nenhum dado em branco foi preenchido artificialmente.')
    target=Path(output).expanduser();target.parent.mkdir(parents=True,exist_ok=True);d.save(target)
    return target
