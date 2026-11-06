import unittest,threading,urllib.request,json
from http.server import ThreadingHTTPServer
from fabrica.api import Handler
class TestCatalog(unittest.TestCase):
 def test_catalog_has_fifteen_distinct_items(self):
  srv=ThreadingHTTPServer(('127.0.0.1',0),Handler)
  t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
  try:
   with urllib.request.urlopen('http://127.0.0.1:'+str(srv.server_port)+'/api/catalog') as h:data=json.load(h)
   self.assertEqual(len(data['services']),15)
   self.assertEqual(len({x['name'] for x in data['services']}),15)
   self.assertEqual(data['services'][9]['name'],'Desenvolvimento de IA')
  finally:srv.shutdown();srv.server_close();t.join(timeout=3)
