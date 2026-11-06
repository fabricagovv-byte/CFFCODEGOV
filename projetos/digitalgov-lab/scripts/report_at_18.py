"""Executa relatório diariamente às 18h, se o usuário configurar agendamento externo.
Uma execução gera um documento e sai; cron/systemd fazem a periodicidade.
Não inicia atividades de engenharia nem altera unidades de medição.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fabrica.db import connect,init
from fabrica.report import build_report
with connect() as conn:
    init(conn)
    print(build_report(conn))
