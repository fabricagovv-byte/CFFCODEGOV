import unittest,tempfile
from pathlib import Path
from fabrica.db import connect,init,integrity_check
from fabrica.core import create_task,start_task,finish_task,verify_task,snapshot,DomainError
class TestFactory(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.c=connect(Path(self.tmp.name)/'test.sqlite3');init(self.c)
    def tearDown(self):self.c.close();self.tmp.cleanup()
    def test_plan_is_not_verified(self):
        d=snapshot(self.c)
        self.assertEqual(d['target_ust'],60000);self.assertEqual(d['official_accepted_ust'],0);self.assertEqual(d['internal_verified_ust'],0)
        self.assertEqual(len(d['orders']),15);self.assertTrue(d['audit_chain_valid'])
    def test_evidence_and_review(self):
        src=Path(self.tmp.name)/'evidence.txt';src.write_text('teste executado')
        t=create_task(self.c,'OS-T01','Criar rotas e testes','AGENTE','agent-001',10)
        start_task(self.c,t);finish_task(self.c,t,src,None,'PASS')
        self.assertEqual(verify_task(self.c,t,'revisor-humano',7),21)
        self.assertEqual(snapshot(self.c)['internal_verified_ust'],21)
        self.assertEqual(snapshot(self.c)['official_accepted_ust'],0)
        self.assertTrue(integrity_check(self.c))
    def test_mutated_evidence_fails(self):
        src=Path(self.tmp.name)/'evidence.txt';src.write_text('versao um')
        t=create_task(self.c,'OS-T01','verificar hash','AGENTE','agent-001',10)
        start_task(self.c,t);finish_task(self.c,t,src,None,'PASS')
        src.write_text('mudado')
        with self.assertRaises(DomainError):verify_task(self.c,t,'revisor',10)
    def test_external_acceptance_blocked(self):
        from fabrica.core import add_external_acceptance
        src=Path(self.tmp.name)/'aceite-falso.txt';src.write_text('não é aceite')
        with self.assertRaises(DomainError):add_external_acceptance(self.c,'OS-T01',10,'Fiscal fictício',src)
if __name__=='__main__':unittest.main()
