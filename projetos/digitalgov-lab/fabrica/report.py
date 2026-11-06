"""Relatório Word editável com valores persistidos do SQLite, sem dados humanos presumidos."""
from pathlib import Path
from datetime import datetime
import csv, json
from .db import ROOT, now
from .core import snapshot

def build_report(c, path=None):
    try:
        from docx import Document
        from docx.shared import Cm,Pt,RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError as e:
        raise RuntimeError('Instale python-docx: python -m pip install -r requirements.txt') from e
    data=snapshot(c)
    target=Path(path) if path else ROOT/'relatorios'/f'RELATORIO_TECNICO_{datetime.now().strftime("%Y%m%d_%H%M")}.docx'
    target.parent.mkdir(parents=True,exist_ok=True)
    doc=Document();sec=doc.sections[0]
    sec.top_margin=Cm(2.1);sec.bottom_margin=Cm(1.8);sec.left_margin=Cm(2.3);sec.right_margin=Cm(2.0)
    styles=doc.styles
    styles['Normal'].font.name='Aptos';styles['Normal'].font.size=Pt(10)
    styles['Normal'].paragraph_format.space_after=Pt(6)
    for sty,color in [('Title',(17,40,72)),('Heading 1',(17,40,72)),('Heading 2',(33,73,117))]:
        styles[sty].font.color.rgb=RGBColor(*color)
    h=sec.header.paragraphs[0];h.text='DIGITALGOV  /  RELATÓRIO DE EXECUÇÃO TÉCNICA  /  LABORATÓRIO'
    h.style='Caption'
    footer=sec.footer.paragraphs[0];footer.text='Documento gerado a partir de dados registrados. NÃO substitui aceite oficial nem comprova vínculo trabalhista.';footer.style='Caption'
    def p(t='',style=None):return doc.add_paragraph(t,style=style)
    def title(t):doc.add_heading(t,level=1)
    def tbl(headers,rows):
        t=doc.add_table(rows=1, cols=len(headers));t.style='Light Shading Accent 1'
        for j,x in enumerate(headers):t.rows[0].cells[j].text=str(x)
        for row in rows:
            cells=t.add_row().cells
            for j,x in enumerate(row):cells[j].text=str(x)
        return t
    def chapter(t):doc.add_page_break();title(t)
    def note(t):p('OBSERVAÇÃO TÉCNICA — '+t)
    doc.add_heading('RELATÓRIO TÉCNICO DE PRODUÇÃO E MEDIÇÃO',0)
    p('Laboratório Fábrica Codex Digitalgov · PE 223/2026 / Paraná')
    p(f'Emitido em: {now()} · Fuso de apresentação: America/Sao_Paulo')
    p('TIPO: TESTE INTERNO / SEM CONTRATO CELEBRADO / SEM OS FORMAL DO ÓRGÃO')
    tbl(['Indicador','Resultado verificado'],[
       ('Meta hipotética',f'{data["target_ust"]:,} UST ajustadas'),
       ('UST técnicamente verificadas (internas)',str(data['internal_verified_ust'])),
       ('UST homologadas oficialmente',str(data['official_accepted_ust'])),
       ('UST faturáveis reconhecidas','NÃO APURADAS: laboratório'),
       ('Projetos de laboratório',str(data['project_count'])),
       ('Cadeia de auditoria', 'ÍNTEGRA' if data['audit_chain_valid'] else 'FALHA')])
    p('Fontes-base: edital do Pregão 223/2026 e seus anexos; registros locais de projetos, sessões, evidências e decisões.')
    note('Nenhuma meta planejada representa entrega, participação humana, aceite ou faturamento.')
    chapter('1. Identificação e fundamento contratual')
    tbl(['Campo','Registro'], [('Identificador interno','LAB-PE223-2026'),('Documento de referência','Pregão Eletrônico 223/2026 — Paraná'),('Objeto','Desenvolvimento, sustentação, manutenção e evolução de sistemas'),('Natureza deste documento','Relatório técnico de laboratório, não medição oficial')])
    p('O TR apresenta estimativa inicial de 325.000 UST ajustadas por complexidade e execução sob demanda por Ordem de Serviço. A meta de 60.000 UST neste teste não é OS do órgão.')
    p('O catálogo analítico previsto no TR 1.3.2 deverá ser pactuado para efetiva medição contratual. Ausente o catálogo formal, qualquer conta no laboratório é apenas uma referência aritmética de planejamento.')
    chapter('2. Regime de medição: UST, fatores e limites')
    p('Fórmula de referência: UST ajustadas = quantidade de UST base elegível × fator de complexidade autorizado, com fatores 1, 2 ou 3 previstos no TR 1.3.1.')
    p('Não se computam UST por commit, linha de código, CRUD, teste, registro de agente ou duração de processo sem correspondência à OS e ao catálogo válido. Não se converte tempo de agentes em HST humano.')
    tbl(['Parcela','UST'],[('Meta das 15 OS hipotéticas',data['target_ust']),('Verificação técnica interna com evidência',data['internal_verified_ust']),('Aceite externo documentado',data['official_accepted_ust']),('Cobrança autorizada','NÃO CALCULADA')])
    note('Para faturamento é necessária OS formal, catálogo, execução comprovada, validação pelo fiscal e critérios de pagamento, conforme TR 7 e 10.')
    chapter('3. Quadro analítico por OS e projeto')
    tbl(['OS','Projeto','Serviço','Base meta','Fator','Meta ajust.','Base verif.','Aceita'],[(o['id'],o['project_id'],o['macroservice'],o['base_target'],o['factor'],o['ust_target'],o['base_verified'],o['base_accepted']) for o in data['orders']])
    p('Nota: todos os totais em “meta” são planejamento hipotético. “Base verificada” só avança mediante tarefa finalizada, teste documentado, arquivo de evidência e conferência explícita.')
    chapter('4. Planejamento, execução e evidências do código')
    if data['tasks']:
        for t in data['tasks'][:40]:
            p(f'Tarefa {t["id"]} — {t["project_id"]} / {t["order_id"]}: {t["description"]}')
            p(f'Situação: {t["state"]}; executor: {t["assignee_kind"]} {t["assignee"]}; base verificada: {t["base_verified"]}; commit: {t["git_commit"] or "não fornecido"}; SHA256: {t["evidence_sha256"] or "não fornecido"}.')
    else:
        p('Até esta emissão não há tarefas com execução registrada nesta base. Produção demonstrada = 0. A existência dos módulos de exemplo distribuídos no ZIP não constitui, por si só, UST do contrato.')
    chapter('5. Jornadas, horários e tempo automatizado')
    p('A jornada proposta dos profissionais é editável, mas não produz horas comprovadas. Apenas sessões humanas iniciadas e encerradas com registro são contabilizadas como tempo observado; pausas, validações e autorizações devem seguir a legislação e o contrato.')
    tbl(['Pessoa','Função','Jornada proposta','Segundos humanos registrados'],[(x['name'] or '(vaga)',x['role'],f'{x["shift_start"]}–{x["shift_end"]}',x['human_seconds_recorded']) for x in data['team']])
    p(f'Sessões registradas no banco: {len(data["sessions"])} (humanas e automatizadas separadas). Agentes não possuem CPF nem jornada humana.')
    chapter('6. Qualidade, testes, revisão e conformidade')
    p('O relatório deve associar artefatos testados a evidências reais e ao identificador da tarefa. O resultado “PASS” somente é aceito pelo motor após registro de evidência em arquivo e revisão humana identificada.')
    for t in data['tasks'][:25]:p(f'Tarefa {t["id"]}: {t["test_result"] or "teste não apresentado"}; revisor: {t["reviewer"] or "pendente"}.')
    if not data['tasks']:note('Nenhum teste de atividade contratual foi registrado. Os testes automatizados do pacote são testes do aplicativo de laboratório, não de serviços solicitados pelo Estado.')
    chapter('7. Indicadores de fluxo inspirados em empresas de tecnologia')
    p('Indicadores selecionados com base em documentação técnica DORA, GitLab Value Stream Analytics e Azure DevOps: quantidade de itens em curso, tempo entre início e conclusão, tempo entre solicitação e conclusão, frequência de entregas e taxa de falhas após implantação.')
    p('Neste laboratório, sem implantação em produção nem histórico de incidentes, os indicadores DORA de implantação são N/A, não zero. O relógio de execução mede duração cronológica, não esforço humano presumido.')
    tbl(['Métrica','Valor verificado'], [('Itens em execução',sum(1 for t in data['tasks'] if t['state']=='EM_EXECUCAO')),('Itens tecnicamente verificados',sum(1 for t in data['tasks'] if t['state']=='VERIFICADA')),('Frequência de deploy em produção','N/A'),('Lead time de commit até produção','N/A'),('Taxa de falha de deploy','N/A')])
    chapter('8. Auditoria, pendências, aceite e encaminhamentos')
    p('A cadeia SHA-256 liga cada registro ao anterior. Alteração manual dos registros pode invalidar sua verificação; proteção contra adulteração sofisticada requer armazenamento imutável externo e controle de acesso.')
    p('A medição oficial permanece bloqueada enquanto não forem disponibilizadas e confirmadas as Ordens de Serviço autorizadas, o catálogo pactuado, a evidência de homologação e as obrigações técnicas específicas.')
    tbl(['Status','Descrição'], [('Integridade da cadeia','ÍNTEGRA' if data['audit_chain_valid'] else 'FALHA'), ('Ordens de serviço','15 hipotéticas'),('Aceite externo','não registrado' if not data['official_accepted_ust'] else 'documentado em banco'),('Elegibilidade financeira','não apurada')])
    chapter('9. Anexo: distribuição e fichas individuais')
    p('As fichas seguintes servem à supervisão e à contingência técnica, não à atribuição automática de produção aos nomes cadastrados.')
    for person in data['team']:
        doc.add_page_break()
        doc.add_heading(f'Ficha técnica — {person["name"] or person["id"]+" / VAGA PENDENTE"}',level=2)
        tbl(['Campo','Informação confirmada'], [('Identificador',person['id']),('Nome',person['name'] or 'não informado'),('Especialidade planejada',person['role']),('Senioridade','declaração do teste, pendente de comprovação'),('Horário proposto',f'{person["shift_start"]}–{person["shift_end"]}'),('OS sob supervisão',person['os_count']),('Meta acompanhada (UST)',person['ust_meta_supervisionadas']),('Trabalho humano observado (segundos)',person['human_seconds_recorded'])])
        p('Lançamentos atribuídos apenas a esta pessoa precisam de tarefas, horários, evidências e validações correspondentes. Metas supervisionadas não equivalem a execução individual.')
    doc.save(target)
    return target
