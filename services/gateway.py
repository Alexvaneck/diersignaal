import os,json,urllib.request,urllib.error,mimetypes
from pathlib import Path
from http.server import ThreadingHTTPServer
from .common import Handler
PORT=int(os.environ.get('GATEWAY_PORT','8100'))
IP=int(os.environ.get('IDENTITY_PORT','8101'))
SP=int(os.environ.get('SIGNALS_PORT','8102'))
WEB=Path(__file__).resolve().parents[1]/'web'
class Gateway(Handler):
    def do_GET(self):
        p=self.route()
        if p=='/api/me': return self.proxy('GET',f'http://127.0.0.1:{IP}/me')
        if p not in ('/','/index.html','/about','/about.html','/app.js','/style.css'):return self.error(404,'Niet gevonden')
        name='index.html' if p in ('/','/index.html') else 'about.html' if p in ('/about','/about.html') else p.lstrip('/')
        payload=(WEB/name).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type',{'index.html':'text/html; charset=utf-8','about.html':'text/html; charset=utf-8','app.js':'text/javascript; charset=utf-8','style.css':'text/css; charset=utf-8'}[name])
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers();self.wfile.write(payload)
    def do_POST(self):
        p=self.route()
        paths={'/api/login':(IP,'/login',False),'/api/login/mfa':(IP,'/login/mfa',False),'/api/register':(IP,'/register',False),'/api/email/verify':(IP,'/email/verify',False),'/api/password-reset':(IP,'/password-reset',False),'/api/logout':(IP,'/logout',False),'/api/admin/users/list':(IP,'/admin/users/list',True),'/api/admin/users/status':(IP,'/admin/users/status',True),'/api/admin/users/update':(IP,'/admin/users/update',True),'/api/admin/users/email-code':(IP,'/admin/users/email-code',True),'/api/admin/users/reset-code':(IP,'/admin/users/reset-code',True),'/api/admin/animals/list':(SP,'/admin/animals/list',True),'/api/admin/animals/create':(SP,'/admin/animals/create',True),'/api/admin/animals/update':(SP,'/admin/animals/update',True),'/api/lookup':(SP,'/lookup',True),'/api/signals':(SP,'/create',True)}
        if p not in paths:return self.error(404,'Niet gevonden')
        port,target,internal=paths[p]
        return self.proxy('POST',f'http://127.0.0.1:{port}{target}',internal)
    def proxy(self,method,url,internal=False):
        if int(self.headers.get('Content-Length','0'))>16000:return self.error(413,'Verzoek te groot')
        data=self.rfile.read(int(self.headers.get('Content-Length','0'))) if method=='POST' else None
        headers={'Content-Type':'application/json','Authorization':self.headers.get('Authorization','')}
        if internal:
            headers['X-Internal-Secret']=os.environ['DIERSIGNAAL_INTERNAL_SECRET']
            try:
                payload=json.loads(data)
                auth=self.headers.get('Authorization','')
                payload['token']=auth[7:] if auth.startswith('Bearer ') else ''
                data=json.dumps(payload).encode()
            except (ValueError,TypeError):return self.error(400,'Ongeldige JSON')
        try:
            req=urllib.request.Request(url,data=data,headers=headers,method=method)
            with urllib.request.urlopen(req,timeout=8) as response:
                return self.raw(response.status,response.read())
        except urllib.error.HTTPError as e:return self.raw(e.code,e.read())
        except Exception:return self.error(503,'Interne service niet bereikbaar')
    def raw(self,status,payload):
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers();self.wfile.write(payload)
def main():ThreadingHTTPServer(('127.0.0.1',PORT),Gateway).serve_forever()
if __name__=='__main__':main()
