"""Executa testes reais das 15 aplicações e da fábrica. Logs não representam UST."""
from pathlib import Path
import subprocess,sys,time,json
ROOT=Path(__file__).resolve().parents[1]; logs=ROOT/'test-results';logs.mkdir(exist_ok=True)
results=[]
for n in range(1,16):
    path=ROOT/'projetos'/f'SYS-{n:02d}'
    start=time.monotonic()
    p=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=path,capture_output=True,text=True,timeout=25)
    results.append({'project':path.name,'exit':p.returncode,'elapsed_seconds':round(time.monotonic()-start,2)})
    (logs/f'{path.name}.txt').write_text(p.stdout+p.stderr)
start=time.monotonic();p=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,timeout=30)
results.append({'project':'CENTRAL','exit':p.returncode,'elapsed_seconds':round(time.monotonic()-start,2)});(logs/'CENTRAL.txt').write_text(p.stdout+p.stderr)
(logs/'summary.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
for row in results:print(row['project'], 'PASS' if row['exit']==0 else 'FAIL',row['elapsed_seconds'])
sys.exit(0 if all(r['exit']==0 for r in results) else 1)
