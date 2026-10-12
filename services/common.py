import json, os, sqlite3, hashlib, hmac, secrets, time
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('DIERSIGNAAL_DATA', str(BASE/'data')))
DATA.mkdir(parents=True, exist_ok=True)
def db(name):
    con=sqlite3.connect(DATA/name, timeout=8)
    con.row_factory=sqlite3.Row
    con.execute('PRAGMA journal_mode=WAL')
    con.execute('PRAGMA foreign_keys=ON')
    return con
def pw_hash(password, salt=None):
    salt=salt or secrets.token_bytes(16)
    derived=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,310000)
    return salt.hex()+':'+derived.hex()
def pw_verify(password,stored):
    try:
        salt,digest=stored.split(':')
        return hmac.compare_digest(pw_hash(password,bytes.fromhex(salt)).split(':')[1],digest)
    except (ValueError,AttributeError): return False
class Handler(BaseHTTPRequestHandler):
    server_version='DierSignaalPilot/0.2'
    def log_message(self, fmt, *args): pass
    def send_json(self, status, obj):
        payload=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'none'")
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers();self.wfile.write(payload)
    def body(self):
        if int(self.headers.get('Content-Length','0'))>16000: raise ValueError('Payload te groot')
        return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
    def error(self,status,msg): self.send_json(status,{'error':msg})
    def route(self): return urlparse(self.path).path
    def header_token(self):
        auth=self.headers.get('Authorization','')
        return auth[7:] if auth.startswith('Bearer ') else ''
    def internal(self):
        return bool(os.environ.get('DIERSIGNAAL_INTERNAL_SECRET')) and hmac.compare_digest(self.headers.get('X-Internal-Secret',''),os.environ['DIERSIGNAAL_INTERNAL_SECRET'])
