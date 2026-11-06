"""Servidor local somente leitura — não expor publicamente sem SSO, TLS, autorização e hardening."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
import json, mimetypes
from .db import connect,init,ROOT
from .core import snapshot
WEB=ROOT/'web'
class Handler(BaseHTTPRequestHandler):
    def respond(self,status,body,mime):
        self.send_response(status)
        self.send_header('Content-Type',mime)
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; object-src 'none'")
        self.send_header('Content-Length',str(len(body)))
        self.end_headers();self.wfile.write(body)
    def do_GET(self):
        route=urlparse(self.path).path
        if route=='/api/state':
            with connect() as c: data=snapshot(c)
            return self.respond(200,json.dumps(data,ensure_ascii=False).encode(),'application/json; charset=utf-8')
        if route=='/api/catalog':
            from importlib.util import spec_from_file_location, module_from_spec
            catalog=[]
            for n in range(1,16):
                f=ROOT/'projetos'/f'SYS-{n:02d}'/'service.py'
                spec=spec_from_file_location(f'svc_{n}',f);mod=module_from_spec(spec);spec.loader.exec_module(mod)
                catalog.append({'id':f'SYS-{n:02d}','port':8000+n,**mod.META})
            return self.respond(200,json.dumps({'services':catalog},ensure_ascii=False).encode(),'application/json; charset=utf-8')
        if route=='/health':return self.respond(200,b'{"ok":true}', 'application/json')
        mapping={'/':WEB/'index.html','/app.js':WEB/'app.js','/style.css':WEB/'style.css'}
        f=mapping.get(route)
        if f and f.is_file():return self.respond(200,f.read_bytes(),mimetypes.guess_type(f)[0] or 'text/plain')
        return self.respond(404,b'Not found','text/plain')
    def do_POST(self):return self.respond(405,b'Read only','text/plain')

def serve(port=8765):
    with connect() as c:init(c)
    print(f'Fábrica Overview em http://127.0.0.1:{port} (LOCAL / SOMENTE LEITURA)')
    ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
