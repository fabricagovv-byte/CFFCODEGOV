import unittest, tempfile, pathlib, sys, json, os, threading, urllib.request, urllib.error, sqlite3
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import service, app
class DomainTest(unittest.TestCase):
    def test_unique_service_logic(self):
        out=service.calculate(service.META['sample'])
        self.assertEqual(out['platform'],'python')
    def test_api_and_persistence(self):
        with tempfile.TemporaryDirectory() as td:
            old=app.DB;app.DB=pathlib.Path(td)/'isolated.sqlite3'
            server=app.ThreadingHTTPServer(('127.0.0.1',0),app.API)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                base='http://127.0.0.1:'+str(server.server_port)
                response=json.load(urllib.request.urlopen(base+'/api/service/metadata'))
                self.assertEqual(response['code'],8)
                self.assertEqual(urllib.request.urlopen(base+'/service').status,200)
                self.assertEqual(urllib.request.urlopen(base+'/service.js').status,200)
                self.assertEqual(urllib.request.urlopen(base+'/service').status,200)
                self.assertEqual(urllib.request.urlopen(base+'/service.js').status,200)
                data=json.dumps(response['sample']).encode('utf8')
                req=urllib.request.Request(base+'/api/service/run',method='POST',data=data,headers={'Content-Type':'application/json'})
                with urllib.request.urlopen(req) as h:result=json.load(h)
                self.assertTrue(result['run_id']>=1)
                self.assertEqual(result['result']['platform'],'python')
                bad=urllib.request.Request(base+'/api/service/run',method='POST',data=b'{"invalid":true}',headers={'Content-Type':'application/json'})
                with self.assertRaises(urllib.error.HTTPError) as err:urllib.request.urlopen(bad)
                self.assertEqual(err.exception.code,400)
                bad=urllib.request.Request(base+'/api/service/run',method='POST',data=b'{"invalid":true}',headers={'Content-Type':'application/json'})
                with self.assertRaises(urllib.error.HTTPError) as err:urllib.request.urlopen(bad)
                self.assertEqual(err.exception.code,400)
                history=json.load(urllib.request.urlopen(base+'/api/service/history'))['items']
                self.assertEqual(len(history),1)
                with sqlite3.connect(app.DB) as c:self.assertEqual(c.execute('select count(*) from service_runs').fetchone()[0],1)
            finally:
                server.shutdown();server.server_close();thread.join(timeout=3);app.DB=old
if __name__=='__main__':unittest.main()
