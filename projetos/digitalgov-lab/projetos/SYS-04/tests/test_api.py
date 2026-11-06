import unittest, tempfile, os, threading, urllib.request, urllib.error, json, importlib
from http.server import ThreadingHTTPServer
from pathlib import Path
class TestCRUD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();os.environ['LAB_DB_PATH']=str(Path(cls.tmp.name)/'records.sqlite3')
        cls.app=importlib.import_module('app');cls.server=ThreadingHTTPServer(('127.0.0.1',0),cls.app.API)
        cls.url='http://127.0.0.1:'+str(cls.server.server_port);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=3);cls.tmp.cleanup();os.environ.pop('LAB_DB_PATH',None)
    def req(self,method,path,body=None):
        data=json.dumps(body).encode() if body is not None else None
        req=urllib.request.Request(self.url+path,data=data,method=method,headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=3) as r:return r.status,json.loads(r.read().decode())
        except urllib.error.HTTPError as e:return e.code,json.loads(e.read().decode())
    def test_crud_and_validation(self):
        status,a=self.req('POST','/api/records',{'title':'Teste integridade','description':'Real','status':'ABERTO'})
        self.assertEqual(status,201);pk=a['id']
        self.assertEqual(self.req('GET','/api/records/'+str(pk))[1]['title'],'Teste integridade')
        self.assertTrue(any(x['id']==pk for x in self.req('GET','/api/records')[1]['items']))
        st,b=self.req('PATCH','/api/records/'+str(pk),{'status':'CONCLUIDO'})
        self.assertEqual(st,200);self.assertEqual(b['status'],'CONCLUIDO')
        self.assertEqual(self.req('POST','/api/records',{'title':'','status':'ABERTO'})[0],400)
        self.assertEqual(self.req('PATCH','/api/records/'+str(pk),{'status':'X'})[0],400)
        self.assertEqual(self.req('DELETE','/api/records/'+str(pk))[0],200)
        self.assertEqual(self.req('GET','/api/records/'+str(pk))[0],404)
    def test_health(self):
        st,x=self.req('GET','/health');self.assertEqual(st,200);self.assertEqual(x['project'],self.app.PROJECT_ID)
if __name__=='__main__':unittest.main()
