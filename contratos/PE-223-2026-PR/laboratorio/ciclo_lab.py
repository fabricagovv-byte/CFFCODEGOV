"""Ciclo de teste do laboratório: tarefa -> execução real dos testes -> evidência -> revisão independente.
UST base proposta = 0: catálogo não pactuado; nenhum valor é inventado."""
import subprocess, sys, json, re
from pathlib import Path
LAB = Path(sys.argv[1]).resolve()
COMMIT = sys.argv[2]
EXEC = 'E17-automacao-testes (agente IA)'
REV = 'G13-revisor-codigo (agente IA, revisão automatizada)'
ev_dir = LAB / 'test-results' / 'ciclo'; ev_dir.mkdir(parents=True, exist_ok=True)
def m(*a):
    p = subprocess.run([sys.executable, 'manage.py', *a], cwd=LAB, capture_output=True, text=True)
    if p.returncode: raise SystemExit(f'falhou {a}: {p.stderr}')
    return p.stdout.strip()
out = []
for n in range(1, 16):
    sys_id, os_id = f'SYS-{n:02d}', f'OS-T{n:02d}'
    tid = int(m('task-create', '--os', os_id, '--title', f'Executar testes automatizados do {sys_id} e registrar evidência', '--kind', 'AGENTE', '--actor', EXEC, '--base', '0').split()[-1])
    m('task-start', str(tid))
    p = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=LAB / 'projetos' / sys_id, capture_output=True, text=True, timeout=60)
    log = ev_dir / f'{sys_id}_tarefa{tid}.txt'
    log.write_text(f'commit {COMMIT}\nexit {p.returncode}\n' + p.stdout + p.stderr)
    res = 'PASS' if p.returncode == 0 else 'FAIL'
    m('task-finish', str(tid), '--evidence', str(log), '--test-result', res, '--commit', COMMIT)
    ver = m('task-verify', str(tid), '--reviewer', REV, '--base', '0') if res == 'PASS' else 'não verificada (FAIL)'
    ntests = len(re.findall(r' \.\.\. ok', p.stderr))
    out.append({'sistema': sys_id, 'os': os_id, 'tarefa': tid, 'testes_ok': ntests, 'resultado': res, 'verificacao': ver})
    print(sys_id, os_id, 'tarefa', tid, res, ntests, 'testes')
(ev_dir / 'RESUMO_CICLO.json').write_text(json.dumps(out, indent=2, ensure_ascii=False))
