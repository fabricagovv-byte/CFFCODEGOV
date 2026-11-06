"""Gera os dados do painel de produção a partir dos registros da fábrica (medição, OS, evidências).

Uso: python3 contratos/FIC-COM-2026-001/relatorios/painel/gerar_dados_painel.py
Nenhum número é digitado: tudo vem de contrato.yaml, TABELA_UST.csv, medicoes/*.json e evidencias/.
"""
import csv, hashlib, json, re, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

C = Path(__file__).resolve().parents[2]
RAIZ = C.parents[1]
OUT = Path(__file__).resolve().parent
TZ = ZoneInfo('America/Sao_Paulo')


def num(v):
    m = re.search(r'-?\d+(?:[.,]\d+)?', str(v or ''))
    return float(m.group(0).replace(',', '.')) if m else None


def fm(p):
    if not p.exists():
        return {}
    m = re.match(r'^---\n(.*?)\n---\n', p.read_text(encoding='utf-8'), re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


ct = yaml.safe_load((C / 'contrato.yaml').read_text(encoding='utf-8'))
med = ct.get('medicao') or {}
contratado, vu = num(med.get('quantidade_contratada')), num(med.get('valor_unitario'))
tab = {r['codigo']: r for r in csv.DictReader(open(C / 'TABELA_UST.csv', encoding='utf-8')) if r['codigo'] and not r['codigo'].startswith('#')}
modulos, provas = [], []
for po in sorted((C / 'os').glob('*.yaml')):
    o = yaml.safe_load(po.read_text(encoding='utf-8'))
    oid = o['os']
    m_json = C / 'medicoes' / f'{oid}.json'
    if not m_json.exists():
        continue
    medicao = json.loads(m_json.read_text(encoding='utf-8'))
    for it in medicao['itens']:
        ev = C / 'evidencias' / oid / it['modulo']
        t = json.loads((ev / 'TESTES.json').read_text(encoding='utf-8')) if (ev / 'TESTES.json').exists() else {}
        rs = t.get('resumo') or {}
        comp = float(it.get('comprovado') or 0)
        modulos.append({'modulo': it['modulo'], 'os': oid, 'nome': it.get('nome', ''), 'item': it.get('item', ''),
                        'ust_comprovada': comp, 'valor': round(comp * vu, 2) if vu is not None else None,
                        'testes': rs.get('testes', 0), 'falhas': rs.get('falhas', 0) + rs.get('erros', 0),
                        'auditoria': it.get('tecnico', ''), 'revisao_humana': 'registrada' if fm(ev / 'REVISOES.md').get('revisao_humana') else 'pendente',
                        'aceite': fm(ev / 'ACEITE.md').get('status', 'PENDENTE'), 'comprovado_em': (it.get('comprovado_em') or '')[:16].replace('T', ' ')})
        if comp > 0:
            arqs = [ev / 'TESTES.json', ev / 'COMMITS.json'] + [RAIZ / e[k] for e in t.get('execucoes', []) for k in ('junit', 'log')]
            arqs += sorted((ev / 'SCREENSHOTS').glob('*.png'))
            for a in dict.fromkeys(arqs):
                if a.is_file():
                    provas.append({'arquivo': str(a.relative_to(C / 'evidencias')), 'modulo': it['modulo'],
                                   'sha256': hashlib.sha256(a.read_bytes()).hexdigest()})
comp_total = sum(m['ust_comprovada'] for m in modulos)
aceito = sum(float(i.get('aceito') or 0) for po in (C / 'medicoes').glob('*.json') for i in json.loads(po.read_text())['itens'])
pagos = [r for r in csv.DictReader(open(C / 'PAGAMENTOS.csv', encoding='utf-8')) if r.get('documento')] if (C / 'PAGAMENTOS.csv').exists() else []
pago = sum(num(r.get('ust')) or 0 for r in pagos)
agora = datetime.now(TZ).isoformat(timespec='seconds')
resumo = [{'contratado': contratado, 'comprovado': comp_total, 'aceito': aceito, 'pago': pago,
           'saldo': (contratado - comp_total) if contratado is not None else None, 'valor_unitario': vu,
           'valor_comprovado': round(comp_total * vu, 2) if vu is not None else None,
           'valor_aceito': round(aceito * vu, 2) if vu is not None else None, 'atualizado_em': agora}]
# catálogo: os 18 módulos do contrato e o que já foi comprovado em cada um (itens parciais somam no módulo)
catalogo = []
for cod, r in tab.items():
    if not re.fullmatch(r'CAT-M\d\d', cod):
        continue
    feito = sum(m['ust_comprovada'] for m in modulos if m['item'] == cod or m['item'].startswith(cod + '-'))
    catalogo.append({'codigo': cod.replace('CAT-', ''), 'modulo': re.sub(r'^M\d\d ', '', r['descricao']).split(' (')[0],
                     'ust_planejada': num(r['ust_por_unidade']), 'ust_comprovada': feito})
for nome, dados in (('resumo', resumo), ('modulos', modulos), ('catalogo', catalogo), ('provas', provas)):
    (OUT / f'{nome}.json').write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps({'resumo': resumo[0], 'modulos': len(modulos), 'catalogo': len(catalogo), 'provas': len(provas)}, ensure_ascii=False))
