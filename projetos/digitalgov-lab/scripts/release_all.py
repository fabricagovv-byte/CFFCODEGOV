from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
for n in range(1,16):
    p=f'SYS-{n:02d}'
    completed=subprocess.run([sys.executable,str(root/'manage.py'),'release','--project',p],cwd=root)
    if completed.returncode:raise SystemExit(f'Falha ao empacotar {p}')
print('15 pacotes independentes produzidos em entregas/')
