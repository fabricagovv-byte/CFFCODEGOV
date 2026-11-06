"""Inicia os 15 serviços isolados em localhost; Ctrl+C encerra todos."""
from pathlib import Path
import subprocess,sys,time,signal
root=Path(__file__).resolve().parents[1]
processes=[]
try:
    for n in range(1,16):
        app=root/'projetos'/f'SYS-{n:02d}'/'app.py'
        p=subprocess.Popen([sys.executable,str(app),'--port',str(8000+n)],cwd=app.parent)
        processes.append(p)
    print('15 operações: http://127.0.0.1:8001/service ... até :8015/service',flush=True)
    while all(p.poll() is None for p in processes):time.sleep(.5)
finally:
    for p in processes:
        if p.poll() is None:p.terminate()
    for p in processes:
        try:p.wait(timeout=3)
        except subprocess.TimeoutExpired:p.kill()
