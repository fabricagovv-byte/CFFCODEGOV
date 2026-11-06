import argparse
from .db import init,connect
from .core import seed,approve_contract,prepare_start

def main():
    p=argparse.ArgumentParser(description='Digitalgov Factory — controle contratual auditável')
    p.add_argument('command',choices=['init','seed-fiction','overview','approve-plan','start','report'])
    p.add_argument('--output',default='reports/RELATORIO_REAL_ATUAL.docx');p.add_argument('--contract',default='FIC-COM-2026-001');p.add_argument('--actor',default='Administrador');p.add_argument('--confirmation')
    a=p.parse_args();init()
    if a.command=='init':print('Banco inicializado sem produção fictícia')
    elif a.command=='seed-fiction':print('Contrato fictício cadastrado' if seed(a.contract) else 'Contrato já existe')
    elif a.command=='overview':
        from .core import overview
        with connect() as c:print(overview(c))
    elif a.command=='approve-plan':approve_contract(a.contract,a.actor,a.confirmation or '');print('PLANO_APROVADO')
    elif a.command=='start':print(prepare_start(a.contract,a.actor))
    elif a.command=='report':
        from .reporting import make_report
        print('Relatório gerado:',make_report(a.output,a.contract))
if __name__=='__main__':main()
