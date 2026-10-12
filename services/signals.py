import os,json,hashlib,hmac,urllib.request,urllib.error,datetime
from http.server import ThreadingHTTPServer
from .common import Handler,db
PORT=int(os.environ.get('SIGNALS_PORT','8102'))
IDENTITY_PORT=int(os.environ.get('IDENTITY_PORT','8101'))
def call_auth(token,action,chip,consultation,purpose):
    body=json.dumps({'token':token,'action':action,'chip':chip,'consultation':consultation,'purpose':purpose}).encode()
    req=urllib.request.Request(f'http://127.0.0.1:{IDENTITY_PORT}/authorize',data=body,headers={'Content-Type':'application/json','X-Internal-Secret':os.environ['DIERSIGNAAL_INTERNAL_SECRET']})
    try:
        with urllib.request.urlopen(req,timeout=4) as response:return json.load(response)
    except urllib.error.HTTPError:return {'allow':False}
def init():
    with db('signals.sqlite3') as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS animals(chip TEXT PRIMARY KEY,name TEXT NOT NULL,species TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS signals(id INTEGER PRIMARY KEY AUTOINCREMENT,chip TEXT NOT NULL REFERENCES animals(chip),practice_id TEXT NOT NULL,observed TEXT NOT NULL,method TEXT NOT NULL,caretaker_statement TEXT NOT NULL,interpretation TEXT NOT NULL,followup TEXT NOT NULL,created_by TEXT NOT NULL,created_at TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'draft');
        CREATE TABLE IF NOT EXISTS access_audit(id INTEGER PRIMARY KEY AUTOINCREMENT,at TEXT NOT NULL,actor TEXT NOT NULL,action TEXT NOT NULL,chip_suffix TEXT NOT NULL,consultation TEXT NOT NULL,allowed INTEGER NOT NULL,prev_hash TEXT NOT NULL,entry_hash TEXT NOT NULL);''')
        if not c.execute('SELECT 1 FROM animals').fetchone():
            c.executemany('INSERT INTO animals VALUES(?,?,?)',[('999000000000001','Bowie','Labrador'),('999000000000002','Mila','Beagle')])
            entries=[('999000000000001','west','Fractuur linkervoorpoot aangetoond op radiografie.','Röntgenonderzoek','Volgens verzorger gevallen tijdens spelen.','Toedracht niet onafhankelijk vastgesteld.','Collegiaal overleg','arts.west','published'),('999000000000001','noord','Eerder letsel rechterachterpoot geobserveerd.','Lichamelijk onderzoek','Volgens verzorger tijdens wandeling ontstaan.','Geen conclusie over oorzaak.','Vervolgonderzoek','arts.noord','published'),('999000000000002','west','Otitis externa bij regulier consult.','Ooronderzoek','Niet van toepassing.','Geen specifiek welzijnssignaal.','Reguliere behandeling','arts.west','published')]
            c.executemany('INSERT INTO signals(chip,practice_id,observed,method,caretaker_statement,interpretation,followup,created_by,created_at,status) VALUES(?,?,?,?,?,?,?,?,?,?)',[(a,b,d,e,f,g,h,i,datetime.datetime.now(datetime.timezone.utc).isoformat(),j) for a,b,d,e,f,g,h,i,j in entries])
def audit(actor,action,chip,consultation,allowed):
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with db('signals.sqlite3') as c:
        prev=c.execute('SELECT entry_hash FROM access_audit ORDER BY id DESC LIMIT 1').fetchone()
        previous=prev['entry_hash'] if prev else 'GENESIS'
        msg=json.dumps([previous,now,actor,action,chip[-4:],consultation,bool(allowed)])
        signature=hashlib.sha256(msg.encode()).hexdigest()
        c.execute('INSERT INTO access_audit(at,actor,action,chip_suffix,consultation,allowed,prev_hash,entry_hash) VALUES(?,?,?,?,?,?,?,?)',(now,actor,action,chip[-4:],consultation,int(allowed),previous,signature))
class Api(Handler):
    def do_POST(self):
        if not self.internal():return self.error(403,'Interne service vereist')
        p=self.route()
        try:d=self.body()
        except Exception:return self.error(400,'Ongeldige JSON')
        if p not in ('/lookup','/create'):return self.error(404,'Niet gevonden')
        chip=str(d.get('chip',''));ref=str(d.get('consultation',''));purpose=str(d.get('purpose',''))
        action='read_signals' if p=='/lookup' else 'create_signal'
        permission=call_auth(str(d.get('token','')),action,chip,ref,purpose)
        actor=str(permission.get('subject','anonymous'))
        audit(actor,action,chip,ref,permission.get('allow',False))
        if not permission.get('allow'):return self.error(403,'Toegang geweigerd: behandelrelatie, rol of doel onvoldoende')
        with db('signals.sqlite3') as c:
            animal=c.execute('SELECT * FROM animals WHERE chip=?',(chip,)).fetchone()
            if not animal:return self.error(404,'Geen fictief dossier gevonden')
            if p=='/lookup':
                rows=c.execute('SELECT id,practice_id,observed,method,caretaker_statement,interpretation,followup,created_at FROM signals WHERE chip=? AND status=? ORDER BY id DESC',(chip,'published')).fetchall()
                return self.send_json(200,{'animal':dict(animal),'signals':[dict(x) for x in rows],'policy':permission['policy']})
            fields=['observed','method','caretaker_statement','interpretation','followup']
            vals=[str(d.get(x,'')).strip() for x in fields]
            if any(len(x)>1200 for x in vals) or any(not vals[i] for i in (0,1,3,4)):
                return self.error(400,'Verplichte velden ontbreken of zijn te lang')
            now=datetime.datetime.now(datetime.timezone.utc).isoformat()
            cursor=c.execute('INSERT INTO signals(chip,practice_id,observed,method,caretaker_statement,interpretation,followup,created_by,created_at,status) VALUES(?,?,?,?,?,?,?,?,?,?)',(chip,permission['practice_id'],*vals,actor,now,'draft'))
            return self.send_json(201,{'id':cursor.lastrowid,'status':'draft','message':'Concept opgeslagen, niet gedeeld'})
    def do_GET(self):
        if not self.internal():return self.error(403,'Interne service vereist')
        if self.route()=='/health':return self.send_json(200,{'ok':True})
        return self.error(404,'Niet gevonden')
def main():
    init();ThreadingHTTPServer(('127.0.0.1',PORT),Api).serve_forever()
if __name__=='__main__':main()
