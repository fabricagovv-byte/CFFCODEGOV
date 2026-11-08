import json, subprocess, sys, tempfile, unittest
from pathlib import Path
SCRIPT=Path(__file__).with_name('dg_control.py')
class DailyControlTest(unittest.TestCase):
    def setUp(self):self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name)/'workspace'
    def tearDown(self):self.t.cleanup()
    def run_cli(self,*args,code=0):
        p=subprocess.run([sys.executable,str(SCRIPT),'--root',str(self.root),*args],capture_output=True,text=True)
        self.assertEqual(p.returncode,code, (p.stdout,p.stderr));return p
    def test_project_daily_and_handoff(self):
        self.run_cli('init');self.run_cli('novo-projeto','--id','PRJ001','--nome','Teste de continuidade','--tipo','CONSULTORIA')
        self.run_cli('abrir-dia','--id','PRJ001')
        self.run_cli('registrar','--id','PRJ001','--descricao','Inspeção de requisito (registro do teste)','--proximo','Validar escopo')
        self.run_cli('fechar-dia','--id','TODOS'); self.run_cli('kit-handoff','--id','PRJ001')
        self.assertTrue(list((self.root/'CONTROL_CENTER'/'RELATORIOS_CONSOLIDADOS').glob('*.md')))
        p=self.root/'PROJETOS'/'PRJ001';self.assertTrue((p/'HANDOFF_ULTIMO_CHAT.md').exists());self.assertTrue(list((p/'DIARIO').glob('*.md')))
        s=json.loads((p/'ESTADO_PROJETO.json').read_text());self.assertEqual(s['horas_humanas_registradas'],0);self.assertEqual(s['ust_executadas_verificadas'],0)
        self.assertTrue((self.root/'KIT_HANDOFF_PRJ001.zip').exists())
    def test_no_fake_completion_or_overwrite(self):
        self.run_cli('init');self.run_cli('novo-projeto','--id','PRJ002','--nome','Segurança')
        self.run_cli('registrar','--id','PRJ002','--tipo','ENTREGA','--descricao','Sem evidencia',code=2)
        self.run_cli('novo-projeto','--id','PRJ002','--nome','Sobrescrita',code=2)
        self.run_cli('registrar','--id','PRJ002','--tipo','ENTREGA','--descricao','Arquivo inexistente','--evidencia','nao_existe.txt',code=2)
if __name__=='__main__':unittest.main()
